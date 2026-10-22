"""Piloto acotado de MIDAGRI, WorldCover y meteorología en tres agrupaciones."""
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import hashlib
import json
import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio
from pyproj import Geod
import rasterio
from rasterio.features import geometry_mask
from rasterio.merge import merge
from shapely.geometry import mapping

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/piloto_agricola'
OUT = ROOT / 'data/processed'
GEOD = Geod(ellps='WGS84')


def json_publico(url, path):
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    with urlopen(Request(url, headers={'User-Agent': 'curso-python/0.1'}), timeout=35) as response:
        data = json.load(response)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    return data


def cobertura(group, points):
    subset = points[(points.grupo_id == group.grupo_id) & points.reciente_48h]
    geo = gpd.GeoDataFrame(subset, geometry=gpd.points_from_xy(subset.longitude, subset.latitude), crs=4326)
    # UTM local para distancias; EPSG:6933 para áreas.
    epsg = 32700 + int((group.longitud + 180) // 6 + 1)
    neighborhood = geo.to_crs(epsg).buffer(1000).union_all()
    aoi = gpd.GeoSeries([neighborhood], crs=epsg).to_crs(4326).iloc[0]
    area = gpd.GeoSeries([aoi], crs=4326).to_crs(6933).area.iloc[0] / 10000
    crop_file = ROOT / 'data/raw/midagri/SuperficieAgricolaNacional.shp'
    crops = gpd.read_file(crop_file, bbox=aoi.bounds)
    bad = int((~crops.is_valid).sum())
    crops.geometry = crops.geometry.make_valid().intersection(aoi)
    crops = crops[~crops.is_empty].copy()
    agricultural = crops.geometry.union_all()
    agricultural_ha = gpd.GeoSeries([agricultural], crs=4326).to_crs(6933).area.iloc[0] / 10000
    crops[['CATEGORIA','FUENTE','geometry']].to_file(RAW / f'{group.grupo_id}_midagri_recorte.geojson', driver='GeoJSON')
    stac_url = 'https://planetarycomputer.microsoft.com/api/stac/v1/search?' + urlencode({
        'collections':'esa-worldcover', 'bbox':','.join(map(str,aoi.bounds)),
        'datetime':'2021-01-01T00:00:00Z/2021-12-31T23:59:59Z', 'limit':10})
    items = json_publico(stac_url, RAW / f'{group.grupo_id}_worldcover_items.json')['features']
    if not items:
        raise RuntimeError('No hay teselas WorldCover para el área del piloto.')
    urls = ['https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/' +
            item['assets']['map']['href'].rsplit('/',1)[-1] for item in items]
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', GDAL_HTTP_TIMEOUT='35', CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif'):
        with ExitStack() as stack:
            datasets = [stack.enter_context(rasterio.open(url)) for url in urls]
            values, transform = merge(datasets, bounds=aoi.bounds, nodata=0)
    values = values[0]
    inside = geometry_mask([mapping(aoi)], out_shape=values.shape, transform=transform, invert=True)
    valid = inside & (values != 0)
    midpoint_area = []
    for row in range(values.shape[0]):
        x0, y0 = transform * (0,row)
        x1, y1 = transform * (1,row+1)
        sq, _ = GEOD.polygon_area_perimeter([x0,x1,x1,x0],[y0,y0,y1,y1])
        midpoint_area.append(abs(sq)/10000)
    weights = np.broadcast_to(np.array(midpoint_area)[:,None], values.shape)
    mid_mask = (geometry_mask([mapping(agricultural)], out_shape=values.shape, transform=transform, invert=True)
                if not agricultural.is_empty else np.zeros(values.shape,dtype=bool))
    wc_crop = valid & (values == 40)
    inverse = ~transform
    detection_codes = []
    for point in subset.itertuples():
        col, row = inverse * (point.longitude, point.latitude)
        detection_codes.append(int(values[int(np.floor(row)),int(np.floor(col))]))
    both = wc_crop & mid_mask
    # Comparaciones limitadas al dominio observado en WorldCover.
    mid_only = valid & mid_mask & ~wc_crop
    wc_only = wc_crop & ~mid_mask
    profile = dict(driver='GTiff',height=values.shape[0],width=values.shape[1],count=1,
                   dtype='uint8',crs='EPSG:4326',transform=transform,nodata=0,compress='deflate')
    tif = RAW / f'{group.grupo_id}_worldcover_recorte.tif'
    with rasterio.open(tif,'w',**profile) as dst:
        dst.write(np.where(valid,values,0).astype('uint8'),1)
    valid_ha = float(weights[valid].sum())
    wc_ha = float(weights[wc_crop].sum())
    intersection_ha = float(weights[both].sum())
    assert intersection_ha <= wc_ha + 1e-6
    assert agricultural_ha <= area + 0.01
    return {'grupo_id':group.grupo_id, 'departamento':group.departamento,
        'latitud':group.latitud,'longitud':group.longitud,'detecciones_48h':int(group.detecciones_48h),
        'entorno_ha':round(area,2),'midagri_agricola_ha':round(agricultural_ha,2),
        'worldcover_cultivo_ha':round(wc_ha,2),'coinciden_ha_aprox':round(intersection_ha,2),
        'midagri_sin_clase40_ha_aprox':round(float(weights[mid_only].sum()),2),
        'clase40_fuera_midagri_ha_aprox':round(float(weights[wc_only].sum()),2),
        'worldcover_valido_pct_pixeles':round(100*valid.sum()/inside.sum(),3),
        'midagri_geometrias_reparadas':bad, 'worldcover_teselas':[item['id'] for item in items],
        'worldcover_clases_en_midagri_ha':{str(int(value)):round(float(weights[valid & mid_mask & (values==value)].sum()),2)
                                        for value in np.unique(values[valid & mid_mask])},
        'clase_wc_en_detecciones_48h':{str(value):detection_codes.count(value) for value in sorted(set(detection_codes))},
        'recorte_sha256':hashlib.sha256(tif.read_bytes()).hexdigest()}


def meteorologia(group, cutoff):
    params = {'latitude':group.latitud,'longitude':group.longitud,
        'hourly':'temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation',
        'models':'ecmwf_ifs','forecast_days':8,'past_days':1,'timezone':'America/Lima','wind_speed_unit':'kmh'}
    url = 'https://api.open-meteo.com/v1/forecast?' + urlencode(params)
    path = RAW / f'{group.grupo_id}_meteorologia_ifs9.json'
    existed = path.exists()
    data = json_publico(url,path)
    frame = pd.DataFrame(data['hourly'])
    frame['time'] = pd.to_datetime(frame.time).dt.tz_localize('America/Lima').dt.tz_convert('UTC')
    frame['lluvia_24h'] = frame.precipitation.rolling(24,min_periods=24).sum()
    frame = frame[(frame.time > cutoff) & (frame.time <= cutoff+pd.Timedelta(hours=168))].copy()
    usable = frame[['temperature_2m','relative_humidity_2m','wind_speed_10m','lluvia_24h']].notna().all(axis=1)
    base = usable & (frame.relative_humidity_2m < 30) & (frame.wind_speed_10m >= 20) & (frame.lluvia_24h < 2)
    alternative = usable & (frame.relative_humidity_2m < 40) & (frame.wind_speed_10m >= 15) & (frame.lluvia_24h < 2)
    frame.to_csv(OUT / f'piloto_{group.grupo_id}_meteorologia.csv',index=False)
    return {'meteorologia_modelo':'ecmwf_ifs','meteorologia_url':url,
        'meteorologia_descarga_utc':datetime.now(timezone.utc).isoformat() if not existed else 'respuesta local reutilizada',
        'celda_latitud':data['latitude'],'celda_longitud':data['longitude'],
        'horas_horizonte':len(frame),'horas_evaluables':int(usable.sum()),
        'horas_escenario_30_20_2':int(base.sum()),'horas_escenario_40_15_2':int(alternative.sum()),
        'tmax_pronostico_c':float(frame.temperature_2m.max()),'lluvia_pronostico_168h_mm':round(float(frame.precipitation.sum()),2),
        'humedad_min_pct':float(frame.relative_humidity_2m.min()),'viento_max_kmh':float(frame.wind_speed_10m.max())}


def main():
    RAW.mkdir(parents=True,exist_ok=True)
    groups = pd.read_csv(OUT/'agrupaciones_preliminares.csv')
    points = pd.read_csv(OUT/'detecciones_preparadas.csv')
    depts = pd.read_csv(OUT/'resumen_departamental_preliminar.csv').head(3).departamento.tolist()
    audit = json.loads((ROOT/'docs/AUDITORIA_DATOS.json').read_text(encoding='utf-8'))
    cutoff = pd.Timestamp(audit['consulta_utc'])
    cache_cutoff = RAW/'corte.txt'
    if cache_cutoff.exists() and cache_cutoff.read_text().strip() != cutoff.isoformat():
        raise RuntimeError('El piloto contiene otro corte temporal; usar una carpeta de muestras nueva.')
    cache_cutoff.write_text(cutoff.isoformat(),encoding='utf-8')
    chosen = []
    for department in depts:
        options = groups[(groups.departamento == department) & groups.reciente_48h & ~groups.revisar_encadenamiento]
        chosen.append(options.sort_values(['detecciones_48h','grupo_id'],ascending=[False,True]).iloc[0])
    results = []
    for group in chosen:
        print(f'Piloto: {group.grupo_id} / {group.departamento}',flush=True)
        result = cobertura(group,points)
        result.update(meteorologia(group,cutoff))
        results.append(result)
        print(json.dumps(result,ensure_ascii=False),flush=True)
    report = {'fecha_corte_detecciones_utc':cutoff.isoformat(),'buffer_m':1000,
        'seleccion':'Una agrupación con más detecciones recientes en cada uno de los tres departamentos con más agrupaciones recientes; excluye grupos marcados para revisión.',
        'advertencia':'Muestra de factibilidad, no ranking nacional. MIDAGRI es superficie agrícola cartografiada; WorldCover clase 40 no cubre todos los cultivos. Los escenarios meteorológicos no están calibrados.',
        'resultados':results}
    (ROOT/'docs/PILOTO_AGRICOLA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    flat = [{k:v for k,v in result.items() if not isinstance(v,(dict,list))} for result in results]
    pd.DataFrame(flat).to_csv(OUT/'piloto_agricola.csv',index=False)


if __name__ == '__main__':
    main()
