"""Exporta datos locales y una escena 3D real; no modifica el análisis nacional."""
from pathlib import Path
from io import BytesIO
from urllib.request import Request, urlopen
import argparse, json, math, shutil
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False), encoding='utf-8')

def download(url, path):
    if path.exists(): return path.read_bytes()
    with urlopen(Request(url, headers={'User-Agent': 'PeruFuegoAgricultura/1.0'}), timeout=35) as r: data=r.read()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('site'); args=parser.parse_args()
    dest=Path(args.site)/'dist'; assets=dest/'assets'; vendor=dest/'vendor'
    assets.mkdir(parents=True,exist_ok=True); vendor.mkdir(exist_ok=True)
    for name in ['dashboard_datos.json','tabla_departamental_nacional.csv','tabla_agrupaciones_nacional.csv','meteorologia_diaria_nacional.csv']:
        shutil.copy2(ROOT/'data/processed'/name, assets/name)
    shutil.copy2(ROOT/'outputs/puno_contexto.jpg',assets/'puno_contexto.jpg')
    data=json.loads((assets/'dashboard_datos.json').read_text(encoding='utf-8'))
    groups=data['agrupaciones']; ids={g['grupo_id'] for g in groups}
    pts=pd.read_csv(ROOT/'data/processed/detecciones_preparadas.csv')
    pts=pts[pts.grupo_id.isin(ids)&pts.reciente_48h]
    write(assets/'detecciones.json',pts[['grupo_id','latitude','longitude','fecha_utc','frp']].to_dict('records'))
    departments=gpd.read_file(ROOT/'data/raw/auditoria/20261022T012532Z/departamentos.geojson')
    departments.geometry=departments.geometry.simplify(.003,preserve_topology=True)
    write(assets/'departamentos.geojson',json.loads(departments.to_json(drop_id=True)))
    features=[]
    for group in groups:
        p=ROOT/'data/raw/nacional'/f"{group['grupo_id']}_midagri_recorte.geojson"
        for f in json.loads(p.read_text(encoding='utf-8'))['features']:
            from shapely.geometry import shape, mapping
            f['geometry']=mapping(shape(f['geometry']).simplify(.00002,preserve_topology=True))
            f['properties']={'grupo_id':group['grupo_id']}
            features.append(f)
    write(assets/'agricultura.geojson',{'type':'FeatureCollection','features':features})
    meta=json.loads((ROOT/'docs/IMAGEN_CONTEXTO.json').read_text(encoding='utf-8'))
    bbox=meta['bbox_wgs84']; w,s,e,n=bbox
    target=from_bounds(*bbox,768,768)
    with rasterio.open(ROOT/'data/raw/revision_contexto/puno_visual.tif') as src:
        rgb=np.zeros((3,768,768),dtype='uint8')
        for band in range(3):
            reproject(src.read(band+1),rgb[band],src_transform=src.transform,src_crs=src.crs,dst_transform=target,dst_crs='EPSG:4326',resampling=Resampling.bilinear)
    Image.fromarray(np.moveaxis(rgb,0,-1)).save(assets/'puno_satelite.jpg',quality=90)
    colors={10:[41,110,70],20:[157,162,76],30:[196,187,120],40:[246,201,70],50:[206,92,103],60:[149,143,133],70:[239,245,255],80:[57,132,197],90:[82,163,174],95:[33,123,110],100:[170,150,95]}
    with rasterio.open(ROOT/'data/raw/nacional/G1184_worldcover_recorte.tif') as src:
        wc=np.zeros((768,768),dtype='uint8')
        reproject(src.read(1),wc,src_transform=src.transform,src_crs=src.crs,dst_transform=target,dst_crs='EPSG:4326',resampling=Resampling.nearest)
    rgba=np.zeros((768,768,4),dtype='uint8')
    for code,color in colors.items(): rgba[wc==code]=color+[255]
    Image.fromarray(rgba).save(assets/'puno_worldcover.png')
    # 96x96 muestreo de Terrain Tiles Terrarium z13 (~19 m en esta latitud).
    zoom=13; size=96; cache=ROOT/'data/raw/dashboard_terreno'; cache.mkdir(parents=True,exist_ok=True)
    def tilexy(lon,lat):
        return (lon+180)/360*2**zoom,(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*2**zoom
    tiles={}; urls=[]
    x0,y0=tilexy(w,n); x1,y1=tilexy(e,s)
    for tx in range(int(x0),int(x1)+1):
        for ty in range(int(y0),int(y1)+1):
            url=f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{zoom}/{tx}/{ty}.png'
            im=np.array(Image.open(BytesIO(download(url,cache/f'{zoom}_{tx}_{ty}.png'))).convert('RGB'),dtype=float)
            tiles[tx,ty]=im[:,:,0]*256+im[:,:,1]+im[:,:,2]/256-32768; urls.append(url)
    heights=[]
    for lat in np.linspace(n,s,size):
        for lon in np.linspace(w,e,size):
            x,y=tilexy(lon,lat); arr=tiles[int(x),int(y)]
            px=min(255,max(0,int((x%1)*256))); py=min(255,max(0,int((y%1)*256)))
            heights.append(round(float(arr[py,px]),1))
    terrain={**meta,'size':size,'heights_m':heights,'min_m':min(heights),'max_m':max(heights),
             'terrain_source':'Terrain Tiles / Mapzen vía AWS; SRTM y GMTED2010, USGS',
             'terrain_urls':urls,'terrain_zoom':zoom,'exageracion_vertical':1.3,
             'nota':'Muestreo para visualización; no se utilizó pendiente ni altitud en el escenario meteorológico.'}
    write(assets/'puno_terreno.json',terrain)
    write(ROOT/'docs/TERRENO_DASHBOARD.json',{k:v for k,v in terrain.items() if k!='heights_m'})
    vendor_urls={
        'leaflet.js':'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
        'leaflet.css':'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
        'three.module.js':'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js',
        'three.core.js':'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.core.js',
        'OrbitControls.js':'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/controls/OrbitControls.js',
        'THREE-LICENSE.txt':'https://cdn.jsdelivr.net/npm/three@0.180.0/LICENSE',
        'LEAFLET-LICENSE.txt':'https://unpkg.com/leaflet@1.9.4/LICENSE'}
    for name,url in vendor_urls.items(): download(url,vendor/name)
    print(json.dumps({'agrupaciones':len(groups),'detecciones':len(pts),'agricultura_features':len(features),'altura_min':min(heights),'altura_max':max(heights),'teselas':len(urls),'destino':str(dest)},ensure_ascii=False))

if __name__=='__main__': main()
