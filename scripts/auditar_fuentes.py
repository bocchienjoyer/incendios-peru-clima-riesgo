"""Auditoría de acceso y muestras; no calcula prioridades ni predice incendios."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import csv
import hashlib
import io
import json

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime.now(timezone.utc)
STAMP = NOW.strftime('%Y%m%dT%H%M%SZ')
RAW = ROOT / 'data' / 'raw' / 'auditoria' / STAMP
RAW.mkdir(parents=True, exist_ok=True)
RECORDS = []


def descargar(nombre, url):
    started = datetime.now(timezone.utc).isoformat()
    record = {'nombre': nombre, 'url': url, 'consulta_utc': started}
    try:
        with urlopen(Request(url, headers={'User-Agent': 'curso-python-incendios-auditoria/0.1'}), timeout=45) as response:
            data = response.read()
            record.update(estado='descargado', http=response.status,
                          content_type=response.headers.get('Content-Type'), bytes=len(data),
                          sha256=hashlib.sha256(data).hexdigest())
        (RAW / nombre).write_bytes(data)
        record['original_local'] = str((RAW / nombre).relative_to(ROOT)).replace('\\', '/')
        return record, data
    except Exception as exc:
        record.update(estado='error', error=str(exc))
        return record, None


def main():
    sources = [
        ('firms_snpp_7d.csv', 'https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_South_America_7d.csv'),
        ('departamentos.geojson', 'https://raw.githubusercontent.com/juaneladio/peru-geojson/master/peru_departamental_simple.geojson'),
        ('limites_licencia.txt', 'https://raw.githubusercontent.com/juaneladio/peru-geojson/master/LICENSE'),
        ('worldcover_coleccion.json', 'https://planetarycomputer.microsoft.com/api/stac/v1/collections/esa-worldcover'),
    ]
    with ThreadPoolExecutor(max_workers=4) as pool:
        responses = list(pool.map(lambda args: descargar(*args), sources))
    contents = {}
    for record, data in responses:
        RECORDS.append(record)
        if data is not None:
            contents[record['nombre']] = data
    report = {'consulta_utc': NOW.isoformat(), 'alcance': 'Auditoría y muestra de un punto; sin ranking',
              'fuentes': RECORDS, 'comprobaciones': {}}
    checks = report['comprobaciones']
    selected = None

    if 'departamentos.geojson' in contents:
        import geopandas as gpd
        from shapely.geometry import Point
        departments = gpd.read_file(RAW / 'departamentos.geojson')
        checks['limites'] = {'filas': len(departments), 'crs': str(departments.crs),
                            'geometrias_invalidas': int((~departments.is_valid).sum()),
                            'geometrias_vacias': int(departments.is_empty.sum()),
                            'columnas': list(departments.columns),
                            'codigos_duplicados': int(departments['FIRST_IDDP'].duplicated().sum()),
                            'procedencia': 'Repositorio peru-geojson; README indica INEI 2007',
                            'licencia_archivo': contents.get('limites_licencia.txt', b'').decode('utf-8')[:150]}
        if 'firms_snpp_7d.csv' in contents:
            rows = list(csv.DictReader(io.StringIO(contents['firms_snpp_7d.csv'].decode('utf-8-sig'))))
            geometry = departments.geometry.union_all()
            peru = [r for r in rows if geometry.covers(Point(float(r['longitude']), float(r['latitude'])))]
            confidence = {key: sum(r['confidence'] == key for r in peru) for key in sorted({r['confidence'] for r in peru})}
            def timestamp(row):
                return datetime.strptime(row['acq_date'] + ' ' + row['acq_time'].zfill(4), '%Y-%m-%d %H%M').replace(tzinfo=timezone.utc)
            dates = [timestamp(r) for r in rows]
            eligible = [r for r in peru if r['confidence'] in ('n', 'h', 'nominal', 'high') and 0 <= (NOW - timestamp(r)).total_seconds() <= 7 * 86400]
            selected = max(eligible, key=timestamp) if eligible else None
            checks['firms'] = {'filas_sudamerica': len(rows), 'columnas': list(rows[0]) if rows else [],
                               'primera_deteccion_utc': min(dates).isoformat() if dates else None,
                               'ultima_deteccion_utc': max(dates).isoformat() if dates else None,
                               'filas_futuras': sum(d > NOW for d in dates), 'filas_en_limites_peru': len(peru),
                               'confianza_en_peru': confidence, 'satellites': sorted({r['satellite'] for r in peru}),
                               'duplicados_exactos_peru': len(peru) - len({tuple(sorted(r.items())) for r in peru}),
                               'nominal_alta_ultimas_168h': len(eligible),
                               'nota': 'Conteo preliminar para comprobar fuente; no son incendios ni agrupaciones'}

    if 'worldcover_coleccion.json' in contents:
        collection = json.loads(contents['worldcover_coleccion.json'])
        asset = collection['item_assets']['map']
        checks['worldcover'] = {'licencia': collection['license'], 'periodo': collection['extent']['temporal'],
                                'banda': asset['raster:bands'], 'clases': asset['classification:classes']}

    if selected:
        latitude, longitude = float(selected['latitude']), float(selected['longitude'])
        names = departments.loc[departments.geometry.covers(Point(longitude, latitude)), 'NOMBDEP'].tolist()
        checks['punto_muestra'] = {'latitud': latitude, 'longitud': longitude, 'departamentos': names,
                                   'criterio': 'Detección nominal/alta más reciente en Perú; solo prueba de acceso',
                                   'fecha_deteccion_utc': selected['acq_date'] + 'T' + selected['acq_time'].zfill(4)}
        weather_url = 'https://api.open-meteo.com/v1/forecast?' + urlencode({
            'latitude': latitude, 'longitude': longitude,
            'hourly': 'temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation',
            'models': 'ecmwf_ifs025', 'past_days': 1, 'forecast_days': 8,
            'timezone': 'America/Lima', 'wind_speed_unit': 'kmh', 'temperature_unit': 'celsius'})
        stac_url = 'https://planetarycomputer.microsoft.com/api/stac/v1/search?' + urlencode({
            'collections': 'esa-worldcover',
            'bbox': f'{longitude-0.001},{latitude-0.001},{longitude+0.001},{latitude+0.001}',
            'datetime': '2021-01-01T00:00:00Z/2021-12-31T23:59:59Z', 'limit': 4})
        with ThreadPoolExecutor(max_workers=2) as pool:
            samples = list(pool.map(lambda args: descargar(*args), [('meteorologia_muestra.json', weather_url), ('worldcover_items_muestra.json', stac_url)]))
        for record, data in samples:
            RECORDS.append(record)
            if data is None:
                continue
            parsed = json.loads(data)
            if record['nombre'].startswith('meteorologia'):
                hourly = parsed['hourly']
                checks['meteorologia'] = {'coordenadas_devueltas': [parsed['latitude'], parsed['longitude']],
                    'elevacion_m': parsed.get('elevation'), 'zona_horaria': parsed['timezone'],
                    'modelo_solicitado': 'ecmwf_ifs025', 'unidades': parsed['hourly_units'],
                    'horas': len(hourly['time']), 'inicio_local': hourly['time'][0], 'fin_local': hourly['time'][-1],
                    'nulos': {key: sum(v is None for v in values) for key, values in hourly.items()},
                    'rangos': {key: [min(v for v in values if v is not None), max(v for v in values if v is not None)]
                               for key, values in hourly.items() if key != 'time' and any(v is not None for v in values)}}
            else:
                checks['worldcover_items'] = [{'id': item['id'], 'fecha': item['properties'].get('datetime'),
                    'inicio_periodo': item['properties'].get('start_datetime'),
                    'fin_periodo': item['properties'].get('end_datetime'),
                    'epsg': item['properties'].get('proj:epsg'), 'asset_map': item['assets']['map']['href'],
                    'version': item['properties'].get('esa_worldcover:product_version')}
                    for item in parsed['features']]
                if parsed['features']:
                    import numpy as np
                    import rasterio
                    from rasterio.windows import Window
                    # El origen S3 público evita conservar tokens de acceso temporales.
                    item = parsed['features'][0]
                    filename = item['assets']['map']['href'].rsplit('/', 1)[-1]
                    cog_url = 'https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/' + filename
                    try:
                        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', GDAL_HTTP_TIMEOUT='30',
                                          CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif'):
                            with rasterio.open(cog_url) as src:
                                row, col = src.index(longitude, latitude)
                                window = Window(max(0, min(src.width - 128, col - 64)),
                                                max(0, min(src.height - 128, row - 64)), 128, 128)
                                pixels = src.read(1, window=window, masked=True)
                                values, counts = np.unique(pixels.compressed(), return_counts=True)
                                checks['worldcover_lectura'] = {'estado': 'verificado', 'url': cog_url,
                                    'crs': str(src.crs), 'resolucion_grados': list(src.res),
                                    'tamano_original': [src.height, src.width], 'nodata': src.nodata,
                                    'dtype': src.dtypes[0], 'bandas': src.count, 'muestra_pixeles': list(pixels.shape),
                                    'pixeles_validos': int(pixels.count()),
                                    'clases_en_muestra': {str(int(v)): int(n) for v, n in zip(values, counts)},
                                    'nota': 'Ventana rectangular para comprobar lectura; no es área quemada ni buffer analítico'}
                                profile = src.profile.copy()
                                profile.update(height=128, width=128, transform=src.window_transform(window),
                                               driver='GTiff', count=1)
                                with rasterio.open(RAW / 'worldcover_muestra.tif', 'w', **profile) as dst:
                                    dst.write(pixels.filled(src.nodata), 1)
                    except Exception as exc:
                        checks['worldcover_lectura'] = {'estado': 'error', 'url': cog_url, 'error': str(exc)}

    output = ROOT / 'docs' / 'AUDITORIA_DATOS.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
