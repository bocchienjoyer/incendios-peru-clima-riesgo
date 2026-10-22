"""Una imagen óptica de contexto para el caso nacional; sin medir área quemada."""
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
import json
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import transform_bounds, transform
from rasterio.windows import from_bounds
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw/revision_contexto'


def get_json(url):
    with urlopen(url,timeout=25) as response:return json.load(response)


def main():
    RAW.mkdir(parents=True,exist_ok=True)
    table=pd.read_csv(ROOT/'data/processed/tabla_agrupaciones_nacional.csv')
    group=table[table.coincidencia_base].iloc[0]
    q={'collections':'sentinel-2-l2a','bbox':f'{group.longitud-.02},{group.latitud-.02},{group.longitud+.02},{group.latitud+.02}',
        'datetime':'2026-10-01T00:00:00Z/2026-10-22T01:25:32Z','limit':10,'sortby':'-datetime'}
    scenes=get_json('https://planetarycomputer.microsoft.com/api/stac/v1/search?'+urlencode(q))
    (RAW/'puno_escenas.json').write_text(json.dumps(scenes),encoding='utf-8')
    # La nubosidad de catálogo solo selecciona candidatos; se mide también SCL local.
    options=[item for item in scenes['features'] if item['properties'].get('eo:cloud_cover',100)<60]
    if not options:raise RuntimeError('No hay escena candidata bajo el corte de nube de catálogo.')
    item=options[0]
    bbox=(group.longitud-.018,group.latitud-.018,group.longitud+.018,group.latitud+.018)
    arrays={}
    profiles={}
    for name in ['visual','SCL']:
        href=item['assets'][name]['href']
        signed=get_json('https://planetarycomputer.microsoft.com/api/sas/v1/sign?'+urlencode({'href':href}))['href']
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',GDAL_HTTP_TIMEOUT='25',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif'):
            with rasterio.open(signed) as src:
                bounds=transform_bounds(4326,src.crs,*bbox)
                window=from_bounds(*bounds,transform=src.transform).round_offsets().round_lengths()
                data=src.read(window=window)
                profile=src.profile.copy()
                profile.update(width=data.shape[2],height=data.shape[1],transform=src.window_transform(window))
                arrays[name],profiles[name]=data,profile
                with rasterio.open(RAW/f'puno_{name}.tif','w',**profile) as dst:dst.write(data)
    scl=arrays['SCL'][0]
    invalid=np.isin(scl,[0,1,3,7,8,9,10,11])
    metadata={'grupo_id':group.grupo_id,'escena_id':item['id'],'fecha_imagen':item['properties']['datetime'],
        'nubes_catalogo_pct':item['properties']['eo:cloud_cover'],'scl_invalido_recorte_pct':round(100*float(invalid.mean()),2),
        'uso':'Contexto óptico; no confirma ignición, daño, cultivo activo o superficie quemada.',
        'fuente':'Copernicus Sentinel-2 L2A vía Microsoft Planetary Computer','bbox_wgs84':bbox,
        'url_asset_sin_firma':item['assets']['visual']['href']}
    (ROOT/'docs/IMAGEN_CONTEXTO.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    points=pd.read_csv(ROOT/'data/processed/detecciones_preparadas.csv')
    selected=points[(points.grupo_id==group.grupo_id)&points.reciente_48h]
    profile=profiles['visual']
    trans=profile['transform']
    x0,y0=trans*(0,0);x1,y1=trans*(profile['width'],profile['height'])
    fig,ax=plt.subplots(figsize=(9,8))
    ax.imshow(np.moveaxis(arrays['visual'],0,-1),extent=(x0,x1,y1,y0),origin='upper')
    crops=gpd.read_file(ROOT/'data/raw/nacional'/f'{group.grupo_id}_midagri_recorte.geojson').to_crs(profile['crs'])
    if not crops.empty:crops.boundary.plot(ax=ax,color='#34f4e9',linewidth=1.7)
    xs,ys=transform(4326,profile['crs'],selected.longitude.to_list(),selected.latitude.to_list())
    ax.scatter(xs,ys,s=90,c='#ff433d',edgecolor='white',linewidth=1.2,label='Detecciones recientes',zorder=5)
    ax.set_xlim(x0,x1);ax.set_ylim(y1,y0);ax.set_axis_off()
    ax.set_title(f"Puno · {group.grupo_id}\nSentinel-2: {metadata['fecha_imagen'][:10]} · contornos: agricultura MIDAGRI 2024",fontsize=12)
    ax.legend(loc='lower right')
    fig.text(.5,.02,'Imagen de contexto: los contornos no indican daño ni cultivo activo. Fuente: Copernicus Sentinel-2 / MIDAGRI.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.03,1,1))
    fig.savefig(ROOT/'outputs/puno_contexto.png',dpi=140,facecolor='white')
    plt.close(fig)
    print(json.dumps(metadata,ensure_ascii=False))


if __name__=='__main__':
    main()
