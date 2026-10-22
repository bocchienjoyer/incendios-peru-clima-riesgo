"""Prepara detecciones y agrupaciones aproximadas; no confirma incendios."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Geod

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/processed'
GEOD = Geod(ellps='WGS84')


def agrupar(frame, distancia_m=1000, horas=48):
    """Componentes conexos de parejas a <= distancia y <= tiempo; puede haber cadenas."""
    lat, lon = frame.latitude.to_numpy(), frame.longitude.to_numpy()
    seconds = np.array([t.timestamp() for t in frame.fecha_utc])
    lat_margin = distancia_m / 110000
    lon_margin = lat_margin / np.cos(np.deg2rad(np.max(np.abs(lat))))
    parent = np.arange(len(frame))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    edges = 0
    for i in range(len(frame)):
        # Ventana amplia de candidatos; la decisión final usa distancia geodésica.
        candidates = np.flatnonzero((np.arange(len(frame)) > i) &
            (np.abs(lat - lat[i]) <= lat_margin) & (np.abs(lon - lon[i]) <= lon_margin) &
            (np.abs(seconds - seconds[i]) <= horas * 3600))
        if not len(candidates):
            continue
        _, _, distances = GEOD.inv(np.full(len(candidates), lon[i]), np.full(len(candidates), lat[i]),
                                  lon[candidates], lat[candidates])
        for j in candidates[np.asarray(distances) <= distancia_m]:
            a, b = find(i), find(j)
            parent[max(a, b)] = min(a, b)
            edges += 1
    roots = [find(i) for i in range(len(frame))]
    mapping = {r: f'G{k:04d}' for k, r in enumerate(sorted(set(roots)), 1)}
    return [mapping[r] for r in roots], edges


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    audit = json.loads((ROOT / 'docs/AUDITORIA_DATOS.json').read_text(encoding='utf-8'))
    cutoff = pd.Timestamp(audit['consulta_utc'])
    paths = {x['nombre']: ROOT / x['original_local'] for x in audit['fuentes']}
    departments = gpd.read_file(paths['departamentos.geojson']).sort_values('FIRST_IDDP')
    raw = pd.read_csv(paths['firms_snpp_7d.csv'], dtype={'acq_time': str})
    raw['fecha_utc'] = pd.to_datetime(raw.acq_date + ' ' + raw.acq_time.str.zfill(4), format='%Y-%m-%d %H%M', utc=True)
    period = raw[(raw.fecha_utc >= cutoff - pd.Timedelta(hours=168)) & (raw.fecha_utc <= cutoff)]
    valid = period[period.confidence.isin(['n', 'h', 'nominal', 'high'])].drop_duplicates().copy()
    points = gpd.GeoDataFrame(valid, geometry=gpd.points_from_xy(valid.longitude, valid.latitude), crs=4326)
    joined = gpd.sjoin(points, departments[['FIRST_IDDP', 'NOMBDEP', 'geometry']], how='inner', predicate='intersects')
    border_matches = int(joined.index.duplicated().sum())
    joined = joined.sort_values('FIRST_IDDP').loc[lambda f: ~f.index.duplicated()].copy()
    joined = joined.sort_values(['fecha_utc', 'latitude', 'longitude']).reset_index(drop=True)
    joined['grupo_id'], edges = agrupar(joined)
    joined['reciente_48h'] = joined.fecha_utc >= cutoff - pd.Timedelta(hours=48)
    groups = []
    for group_id, subset in joined.groupby('grupo_id', sort=True):
        recent = subset[subset.reciente_48h]
        reference = recent if len(recent) else subset
        # Representante siempre situado sobre una detección, no en un centro sin fuego.
        center_lon, center_lat = reference.longitude.mean(), reference.latitude.mean()
        representative = reference.iloc[np.argmin((reference.longitude-center_lon)**2 + (reference.latitude-center_lat)**2)]
        counts = reference.groupby(['FIRST_IDDP', 'NOMBDEP']).size().reset_index(name='n')
        assigned = counts.sort_values(['n', 'FIRST_IDDP'], ascending=[False, True]).iloc[0]
        _, _, diagonal = GEOD.inv(subset.longitude.min(), subset.latitude.min(), subset.longitude.max(), subset.latitude.max())
        duration = (subset.fecha_utc.max() - subset.fecha_utc.min()).total_seconds() / 3600
        groups.append({'grupo_id': group_id, 'codigo_departamento': assigned.FIRST_IDDP,
            'departamento': assigned.NOMBDEP, 'detecciones_168h': len(subset), 'detecciones_48h': len(recent),
            'reciente_48h': bool(len(recent)), 'primera_utc': subset.fecha_utc.min().isoformat(),
            'ultima_utc': subset.fecha_utc.max().isoformat(), 'latitud': representative.latitude,
            'longitud': representative.longitude, 'duracion_h': round(duration, 2),
            'diagonal_envolvente_km': round(diagonal/1000, 3),
            'cruza_departamentos': subset.FIRST_IDDP.nunique() > 1,
            'revisar_encadenamiento': duration > 48 or diagonal > 3000})
    group_table = pd.DataFrame(groups)
    group_table.to_csv(OUT / 'agrupaciones_preliminares.csv', index=False, encoding='utf-8')
    export = joined[['grupo_id','FIRST_IDDP','NOMBDEP','latitude','longitude','fecha_utc','confidence','frp','reciente_48h']].copy()
    export['fecha_utc'] = export.fecha_utc.map(lambda t: t.isoformat())
    export.to_csv(OUT / 'detecciones_preparadas.csv', index=False, encoding='utf-8')
    summary = []
    for _, department in departments.iterrows():
        rows = joined[joined.FIRST_IDDP == department.FIRST_IDDP]
        gs = group_table[group_table.codigo_departamento == department.FIRST_IDDP]
        recent_gs = gs[gs.reciente_48h]
        summary.append({'codigo_departamento': department.FIRST_IDDP, 'departamento': department.NOMBDEP,
            'detecciones_168h': len(rows), 'detecciones_48h': int(rows.reciente_48h.sum()),
            'agrupaciones_168h': len(gs), 'agrupaciones_recientes_48h': len(recent_gs),
            'agrupaciones_a_revisar': int(recent_gs.revisar_encadenamiento.sum())})
    summary = pd.DataFrame(summary).sort_values(['agrupaciones_recientes_48h','departamento'], ascending=[False,True])
    summary.to_csv(OUT / 'resumen_departamental_preliminar.csv', index=False, encoding='utf-8')
    geo = gpd.GeoDataFrame(group_table, geometry=gpd.points_from_xy(group_table.longitud, group_table.latitud), crs=4326)
    geo[geo.reciente_48h].to_file(OUT / 'agrupaciones_recientes.geojson', driver='GeoJSON')
    report = {'fecha_corte_utc': cutoff.isoformat(), 'ventana_h': 168, 'reciente_h': 48,
        'distancia_pareja_m': 1000, 'tiempo_pareja_h': 48, 'detecciones_validas_peru': len(joined),
        'detecciones_recientes_48h': int(joined.reciente_48h.sum()), 'agrupaciones_total': len(group_table),
        'agrupaciones_recientes': int(group_table.reciente_48h.sum()), 'parejas_enlazadas': edges,
        'coincidencias_limite_resueltas_por_codigo': border_matches,
        'recientes_a_revisar': int(group_table[group_table.reciente_48h].revisar_encadenamiento.sum()),
        'asignacion_departamento': 'Mayor número de detecciones de últimas 48 h; si no hay, de 168 h. Empate por código.',
        'advertencia': 'Agrupaciones aproximadas; no incendios confirmados ni prioridad agrícola. Encadenamientos pendientes de revisión.',
        'top_conteo_agrupaciones': summary.head(8).to_dict(orient='records')}
    (ROOT / 'docs/PASO_2_DETECCIONES.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    assert len(joined) == audit['comprobaciones']['firms']['nominal_alta_ultimas_168h']
    assert group_table.detecciones_168h.sum() == len(joined)
    assert summary.detecciones_168h.sum() == len(joined)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
