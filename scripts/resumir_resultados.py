"""Genera el resumen nacional, una figura y un paquete ligero para la web."""
from pathlib import Path
import json
import shutil
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/processed'


def main():
    report=json.loads((ROOT/'docs/ANALISIS_NACIONAL.json').read_text(encoding='utf-8'))
    groups=pd.read_csv(OUT/'tabla_agrupaciones_nacional.csv')
    depts=pd.read_csv(OUT/'tabla_departamental_nacional.csv',dtype={'codigo_departamento':str})
    daily=[]
    for group in groups.itertuples():
        f=pd.read_csv(OUT/f'nacional_meteo_{group.grupo_id}.csv')
        f['dia']=pd.to_datetime(f.time,utc=True).dt.tz_convert('America/Lima').dt.strftime('%Y-%m-%d')
        for day,part in f.groupby('dia'):
            daily.append({'grupo_id':group.grupo_id,'dia':day,'tmax_c':round(float(part.temperature_2m.max()),1),
                'humedad_min_pct':float(part.relative_humidity_2m.min()),'viento_max_kmh':round(float(part.wind_speed_10m.max()),1),
                'lluvia_mm':round(float(part.precipitation.sum()),1),'horas_base':int(part.escenario_base.sum()),
                'horas_sensibilidad':int(part.escenario_sensibilidad.sum())})
    daily=pd.DataFrame(daily)
    daily.to_csv(OUT/'meteorologia_diaria_nacional.csv',index=False)
    package={'metadatos':report,'departamentos':json.loads(depts.to_json(orient='records',force_ascii=False)),
        'agrupaciones':json.loads(groups.to_json(orient='records',force_ascii=False)),
        'meteorologia_diaria':json.loads(daily.to_json(orient='records',force_ascii=False))}
    (OUT/'dashboard_datos.json').write_text(json.dumps(package,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    selected=groups[groups.coincidencia_base].iloc[0]
    shutil.copyfile(OUT/f'nacional_meteo_{selected.grupo_id}.csv',OUT/'puno_meteorologia_7dias.csv')
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(12,5.2),gridspec_kw={'width_ratios':[1,1.2]})
    fig.subplots_adjust(top=.80,bottom=.23,wspace=.5,left=.12,right=.98)
    top=depts.nlargest(6,'agricola_cercana_ha_unicas').iloc[::-1]
    bars=ax1.barh(top.departamento.str.title(),top.agricola_cercana_ha_unicas,color='#2a7b69')
    ax1.bar_label(bars,fmt='%.0f',padding=4,fontsize=9)
    ax1.set_xlim(0,2700)
    ax1.set_xlabel('Hectáreas agrícolas cartografiadas cercanas')
    ax1.set_title('Mayor cercanía agrícola\nNo equivale a prioridad meteorológica',fontsize=11)
    for spine in ['top','right']:ax1.spines[spine].set_visible(False)
    p=daily[daily.grupo_id==selected.grupo_id]
    positions=list(range(len(p)))
    ax2.bar([v-.18 for v in positions],p.horas_base,width=.36,color='#294f83',label='Escenario base')
    ax2.bar([v+.18 for v in positions],p.horas_sensibilidad,width=.36,color='#da9a34',label='Sensibilidad')
    ax2.set_xticks(positions,p.dia.str[8:10]+'/10')
    ax2.set_ylabel('Horas de coincidencia')
    ax2.set_title('Puno · G1184: una coincidencia exploratoria\n5,08 ha agrícolas a menos de 1 km',fontsize=11)
    ax2.legend(frameon=False,fontsize=9)
    for spine in ['top','right']:ax2.spines[spine].set_visible(False)
    fig.suptitle('Cercanía agrícola y condiciones meteorológicas responden preguntas distintas',fontsize=13,fontweight='bold')
    fig.text(.5,.075,'Detecciones: corte 21/10/2026, 20:25 h de Lima · Pronóstico: 22–28/10/2026\nEscenarios exploratorios no calibrados; las hectáreas no son cultivo dañado. Fuente: FIRMS, MIDAGRI y Open-Meteo.',ha='center',fontsize=9)
    fig.savefig(ROOT/'outputs/resultado_nacional.png',dpi=140,facecolor='white')
    plt.close(fig)
    sensitivity={str(radius):int((groups.apta_comparacion&(groups[column]>0)&(groups.horas_base>0)).sum())
        for radius,column in [(500,'midagri_agricola_500m_ha'),(1000,'midagri_agricola_ha'),(2000,'midagri_agricola_2000m_ha')]}
    summary={'agricola_cercana_ha_unicas':round(float(depts.agricola_cercana_ha_unicas.sum()),2),
        'agrupaciones_comparables':int(groups.apta_comparacion.sum()),
        'comparables_con_agricultura':int((groups.apta_comparacion&(groups.midagri_agricola_ha>0)).sum()),
        'sensibilidad_grupos_base_por_buffer_m':sensitivity,'grupo_coincidente':selected.grupo_id,
        'paquete_web_bytes':(OUT/'dashboard_datos.json').stat().st_size,
        'primera_hora_base_local':'2026-10-27T14:00:00-05:00',
        'advertencia':'No es una alerta ni una estimación de pérdida agrícola.'}
    (ROOT/'docs/RESUMEN_NACIONAL.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
