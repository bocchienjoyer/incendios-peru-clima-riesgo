"""Revisión visual de alineación y desacuerdos cartográficos del piloto."""
from pathlib import Path
import json
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.colors import to_rgba

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/'data/raw/piloto_agricola'
COLORS = {10:'#12683b',20:'#d6ab32',30:'#efe25e',40:'#e899ba',50:'#dc6b63',60:'#bdb8ae',
          70:'#e5f1f5',80:'#4b9ed5',90:'#62babc',95:'#00aa75',100:'#ddd8ad'}


def main():
    report = json.loads((ROOT/'docs/PILOTO_AGRICOLA.json').read_text(encoding='utf-8'))
    points = pd.read_csv(ROOT/'data/processed/detecciones_preparadas.csv')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
    fig, axes = plt.subplots(1,3,figsize=(15,7.3))
    fig.subplots_adjust(top=0.82,bottom=0.30,left=0.055,right=0.985,wspace=0.26)
    for ax, row in zip(axes,report['resultados']):
        group_id = row['grupo_id']
        with rasterio.open(RAW/f'{group_id}_worldcover_recorte.tif') as src:
            values = src.read(1)
            bounds = src.bounds
        rgba = np.zeros((*values.shape,4))
        for code,color in COLORS.items():
            rgba[values==code] = to_rgba(color)
        ax.imshow(rgba,extent=(bounds.left,bounds.right,bounds.bottom,bounds.top),origin='upper',interpolation='nearest')
        crops = gpd.read_file(RAW/f'{group_id}_midagri_recorte.geojson')
        crops.boundary.plot(ax=ax,color='#165bce',linewidth=1.5)
        selected = points[(points.grupo_id==group_id)&points.reciente_48h]
        ax.scatter(selected.longitude,selected.latitude,s=32,c='#c52336',edgecolor='white',linewidth=0.7,zorder=5)
        ax.set_xlim(bounds.left,bounds.right)
        ax.set_ylim(bounds.bottom,bounds.top)
        ax.set_aspect(1/np.cos(np.deg2rad(row['latitud'])))
        ax.ticklabel_format(useOffset=False,style='plain')
        ax.tick_params(axis='x',rotation=30)
        ax.set_xlabel('Longitud')
        ax.set_ylabel('Latitud')
        ax.set_title(f"{row['departamento'].title()} · {group_id}\nMIDAGRI: {row['midagri_agricola_ha']:.2f} ha | WC cultivo: {row['worldcover_cultivo_ha']:.2f} ha",fontsize=11,pad=12)
    fig.suptitle('Superficie agrícola cerca de detecciones recientes: tres pruebas del cruce',fontsize=16,fontweight='bold')
    handles=[Line2D([0],[0],color='#165bce',lw=2,label='Superficie agrícola MIDAGRI 2024'),
             Line2D([0],[0],marker='o',color='w',markerfacecolor='#c52336',markersize=7,label='Detección en últimas 48 h')]
    handles += [Patch(facecolor=COLORS[c],label=name) for c,name in [(10,'Árboles'),(20,'Matorral'),(30,'Pastizal'),(40,'Cultivo anual'),(50,'Urbano'),(60,'Suelo desnudo'),(80,'Agua')]]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(0.5,0.005),ncol=4,frameon=False,fontsize=10)
    fig.text(0.5,0.165,'Fondo: WorldCover 2021 · Entorno de 1 km alrededor de detecciones recientes · Corte: 21/10/2026, 20:25 h de Lima\nMuestra de factibilidad: no es daño agrícola confirmado ni ranking nacional.',ha='center',va='center',fontsize=10)
    output=ROOT/'outputs'
    output.mkdir(exist_ok=True)
    fig.savefig(output/'piloto_agricola.png',dpi=140,facecolor='white')
    plt.close(fig)
    print(output/'piloto_agricola.png')


if __name__=='__main__':
    main()
