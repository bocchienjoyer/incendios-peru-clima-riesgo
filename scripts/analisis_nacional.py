"""Cruce nacional de una captura fija; escenarios exploratorios, no alerta oficial."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import json
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import make_valid
from shapely.geometry import mapping
import piloto_agricola as piloto

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw/nacional'
OUT=ROOT/'data/processed'
METADATA=ROOT/'docs/ANALISIS_NACIONAL.json'


def guardar(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def consultar(url,path):
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    with urlopen(Request(url,headers={'User-Agent':'curso-python/0.1'}),timeout=45) as response:
        data=json.load(response)
    guardar(path,data)
    return data


def construir_entornos(groups,points):
    rows=[]
    for group in groups.itertuples():
        p=points[(points.grupo_id==group.grupo_id)&points.reciente_48h]
        geo=gpd.GeoSeries(gpd.points_from_xy(p.longitude,p.latitude),crs=4326)
        epsg=(32700 if group.latitud<0 else 32600)+int((group.longitud+180)//6+1)
        metric=geo.to_crs(epsg)
        record={'grupo_id':group.grupo_id}
        for radius in [500,1000,2000]:
            union=metric.buffer(radius).union_all()
            record[f'g{radius}']=gpd.GeoSeries([union],crs=epsg).to_crs(4326).iloc[0]
        rows.append(record)
    return rows


def preparar_midagri(entornos):
    path=RAW/'midagri_recorte_2km.gpkg'
    if path.exists():
        return gpd.read_file(path),path
    mask=gpd.GeoSeries([r['g2000'] for r in entornos],crs=4326).union_all()
    data=gpd.read_file(ROOT/'data/raw/midagri/SuperficieAgricolaNacional.shp',mask=mask,
                       columns=['IDDPTO','CATEGORIA','FUENTE'])
    invalid=int((~data.is_valid).sum())
    data.geometry=data.geometry.make_valid().intersection(mask)
    data=data[~data.is_empty].copy()
    data.to_file(path,driver='GPKG')
    guardar(RAW/'midagri_recorte_metadatos.json',{'registros_leidos':len(data),'geometrias_invalidas_reparadas':invalid,
        'criterio':'Intersección con unión de entornos de 2 km de las 131 agrupaciones recientes; original local MIDAGRI 2024.'})
    return data,path


def meteorologia_lote(groups,start):
    records={}
    for offset in range(0,len(groups),25):
        batch=groups.iloc[offset:offset+25]
        params={'latitude':','.join(map(str,batch.latitud)), 'longitude':','.join(map(str,batch.longitud)),
            'hourly':'temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation',
            'models':'ecmwf_ifs','past_days':1,'forecast_days':8,'timezone':'America/Lima',
            'elevation':','.join(['nan']*len(batch)),'wind_speed_unit':'kmh'}
        url='https://api.open-meteo.com/v1/forecast?'+urlencode(params)
        file=RAW/f'meteorologia_lote_{offset:03d}.json'
        existed=file.exists()
        data=consultar(url,file)
        if not isinstance(data,list):data=[data]
        if len(data)!=len(batch):raise RuntimeError('Respuesta incompleta de meteorología.')
        for group,response in zip(batch.itertuples(),data):
            frame=pd.DataFrame(response['hourly'])
            frame['time']=pd.to_datetime(frame.time).dt.tz_localize('America/Lima').dt.tz_convert('UTC')
            frame['lluvia_24h']=frame.precipitation.rolling(24,min_periods=24).sum()
            frame=frame[(frame.time>=start)&(frame.time<start+pd.Timedelta(hours=168))].copy()
            valid=frame[['temperature_2m','relative_humidity_2m','wind_speed_10m','precipitation','lluvia_24h']].notna().all(axis=1)
            base=valid&(frame.relative_humidity_2m<30)&(frame.wind_speed_10m>=20)&(frame.lluvia_24h<2)
            alt=valid&(frame.relative_humidity_2m<40)&(frame.wind_speed_10m>=15)&(frame.lluvia_24h<2)
            frame['escenario_base']=base
            frame['escenario_sensibilidad']=alt
            frame.to_csv(OUT/f'nacional_meteo_{group.grupo_id}.csv',index=False)
            records[group.grupo_id]={'horas_pronostico':len(frame),'horas_evaluables':int(valid.sum()),
                'horas_base':int(base.sum()),'horas_sensibilidad':int(alt.sum()),
                'horas_base_72h':int(base[frame.time<start+pd.Timedelta(hours=72)].sum()),
                'tmax_c':round(float(frame.temperature_2m.max()),1),'lluvia_7d_mm':round(float(frame.precipitation.sum()),1),
                'humedad_min_pct':float(frame.relative_humidity_2m.min()),'viento_max_kmh':float(frame.wind_speed_10m.max()),
                'celda_latitud':response['latitude'],'celda_longitud':response['longitude']}
        if not existed:
            guardar(RAW/f'meteorologia_lote_{offset:03d}_procedencia.json',{'url':url,'consulta_utc':datetime.now(timezone.utc).isoformat(),
                'modelo':'ecmwf_ifs','elevacion':'nan: sin ajuste artificial a elevación puntual','grupos':batch.grupo_id.tolist()})
        print(f'Meteorología: {min(offset+25,len(groups))}/{len(groups)}',flush=True)
    return records


def main():
    RAW.mkdir(parents=True,exist_ok=True)
    groups=pd.read_csv(OUT/'agrupaciones_preliminares.csv')
    groups=groups[groups.reciente_48h].copy()
    points=pd.read_csv(OUT/'detecciones_preparadas.csv')
    audit=json.loads((ROOT/'docs/AUDITORIA_DATOS.json').read_text(encoding='utf-8'))
    cutoff=pd.Timestamp(audit['consulta_utc'])
    start=(cutoff.tz_convert('America/Lima').normalize()+pd.Timedelta(days=1)).tz_convert('UTC')
    config={'corte_detecciones':cutoff.isoformat(),'inicio_pronostico':start.isoformat(),'buffer_m':1000,
        'escenario_base':[30,20,2],'escenario_sensibilidad':[40,15,2],'modelo':'ecmwf_ifs','elevacion':'nan'}
    config_file=RAW/'configuracion.json'
    if config_file.exists() and json.loads(config_file.read_text(encoding='utf-8'))!=config:
        raise RuntimeError('La carpeta nacional corresponde a otra configuración. No se reutilizan silenciosamente sus datos.')
    guardar(config_file,config)
    print('Preparando recorte MIDAGRI único para las zonas de interés...',flush=True)
    entornos=construir_entornos(groups,points)
    crops,crop_path=preparar_midagri(entornos)
    agricultural=crops.geometry.union_all()
    env_by_id={row['grupo_id']:row for row in entornos}
    piloto.RAW=RAW

    def one(group):
        path=RAW/f'{group.grupo_id}_cobertura_resultado.json'
        if path.exists():return json.loads(path.read_text(encoding='utf-8'))
        try:
            result=piloto.cobertura(group,points,crop_file=crop_path)
            for radius in [500,2000]:
                clip=agricultural.intersection(env_by_id[group.grupo_id][f'g{radius}'])
                result[f'midagri_agricola_{radius}m_ha']=round(float(gpd.GeoSeries([clip],crs=4326).to_crs(6933).area.iloc[0]/10000),2)
            result['cobertura_estado']='ok'
        except Exception as exc:
            result={'grupo_id':group.grupo_id,'departamento':group.departamento,'cobertura_estado':'error','error_cobertura':str(exc)}
        guardar(path,result)
        return result

    results=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(one,group) for group in groups.itertuples()]
        for future in as_completed(futures):
            results.append(future.result())
            if len(results)%10==0 or len(results)==len(groups):
                print(f'Cobertura: {len(results)}/{len(groups)}',flush=True)
    weather=meteorologia_lote(groups,start)
    table=groups.merge(pd.DataFrame(results),on=['grupo_id','departamento'],how='left',suffixes=('','_cobertura'))
    table=table.merge(pd.DataFrame([dict(grupo_id=k,**v) for k,v in weather.items()]),on='grupo_id',how='left')
    reasons=[]
    for row in table.itertuples():
        reason=[]
        if row.revisar_encadenamiento:reason.append('actividad repetida/encadenamiento')
        codes=getattr(row,'clase_wc_en_detecciones_48h',{})
        if isinstance(codes,dict):
            water=codes.get('80',0)
            urban=codes.get('50',0)
            if water>0:reason.append('detección sobre agua cartografiada en 2021')
            if urban>0:reason.append('detección sobre urbano cartografiado en 2021')
        if row.cobertura_estado!='ok':reason.append('cobertura no disponible')
        if row.horas_evaluables!=168:reason.append('pronóstico incompleto')
        reasons.append('; '.join(reason))
    table['revision']=reasons
    table['apta_comparacion']=table.revision.eq('')
    table['coincidencia_base']=table.apta_comparacion&(table.midagri_agricola_ha>0)&(table.horas_base>0)
    table['coincidencia_sensibilidad']=table.apta_comparacion&(table.midagri_agricola_ha>0)&(table.horas_sensibilidad>0)
    table=table.sort_values(['coincidencia_base','horas_base','midagri_agricola_ha','grupo_id'],ascending=[False,False,False,True])
    # La unión evita contar dos veces agricultura situada cerca de grupos distintos.
    def union_ids(ids):
        geoms=[env_by_id[g]['g1000'] for g in ids]
        return agricultural.intersection(gpd.GeoSeries(geoms,crs=4326).union_all()) if geoms else agricultural.difference(agricultural)
    all_ag=union_ids(table.grupo_id.tolist())
    base_ag=union_ids(table.loc[table.coincidencia_base,'grupo_id'].tolist())
    alt_ag=union_ids(table.loc[table.coincidencia_sensibilidad,'grupo_id'].tolist())
    bounds_path=next(ROOT/x['original_local'] for x in audit['fuentes'] if x['nombre']=='departamentos.geojson')
    depts=gpd.read_file(bounds_path)
    dept_rows=[]
    for dept in depts.itertuples():
        subset=table[table.departamento==dept.NOMBDEP]
        areas=[]
        for geom in [all_ag,base_ag,alt_ag]:
            clipped=geom.intersection(dept.geometry)
            areas.append(round(float(gpd.GeoSeries([clipped],crs=4326).to_crs(6933).area.iloc[0]/10000),2))
        dept_rows.append({'codigo_departamento':dept.FIRST_IDDP,'departamento':dept.NOMBDEP,
            'agrupaciones_recientes':len(subset),'agrupaciones_revision':int((~subset.apta_comparacion).sum()),
            'agrupaciones_con_agricultura':int((subset.midagri_agricola_ha>0).sum()),
            'grupos_coincidencia_base':int(subset.coincidencia_base.sum()),
            'grupos_coincidencia_sensibilidad':int(subset.coincidencia_sensibilidad.sum()),
            'agricola_cercana_ha_unicas':areas[0],'agricola_escenario_base_ha_unicas':areas[1],
            'agricola_escenario_sensibilidad_ha_unicas':areas[2]})
    dept_table=pd.DataFrame(dept_rows).sort_values(['agricola_escenario_base_ha_unicas','agricola_cercana_ha_unicas'],ascending=False)
    dept_table.to_csv(OUT/'tabla_departamental_nacional.csv',index=False)
    # Las estructuras anidadas se conservan en JSON; CSV incluye las columnas comparables.
    nested=['worldcover_teselas','worldcover_clases_en_midagri_ha','clase_wc_en_detecciones_48h']
    table.drop(columns=[c for c in nested if c in table]).to_csv(OUT/'tabla_agrupaciones_nacional.csv',index=False)
    guardar(OUT/'agrupaciones_nacional.json',json.loads(table.to_json(orient='records',force_ascii=False)))
    report={**config,'fin_pronostico_exclusivo':(start+pd.Timedelta(hours=168)).isoformat(),
        'agrupaciones_recientes':len(table),'coberturas_ok':int(table.cobertura_estado.eq('ok').sum()),
        'agrupaciones_revision':int((~table.apta_comparacion).sum()),
        'agrupaciones_con_agricultura':int((table.midagri_agricola_ha>0).sum()),
        'coincidencias_base':int(table.coincidencia_base.sum()),'coincidencias_sensibilidad':int(table.coincidencia_sensibilidad.sum()),
        'meteorologia_horas_completas':int(table.horas_evaluables.eq(168).sum()),
        'celdas_meteorologicas_unicas':len(table[['celda_latitud','celda_longitud']].drop_duplicates()),
        'top_departamentos':dept_table.head(10).to_dict(orient='records'),
        'advertencia':'Escenarios exploratorios no calibrados. Agricultura cartografiada cercana, no cultivo dañado. Grupos con revisión pendientes fuera de la comparación principal.'}
    guardar(METADATA,report)
    assert table.grupo_id.is_unique
    assert len(table)==131
    assert ((table.horas_base<=table.horas_sensibilidad)&(table.horas_sensibilidad<=168)).all()
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    main()
