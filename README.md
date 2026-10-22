# Incendios en el Perú: clima y riesgo

**Pregunta:** ¿Qué zonas agrícolas cercanas a detecciones recientes de fuego coinciden con condiciones meteorológicas favorables para su propagación durante los próximos siete días, y en qué departamentos se concentran?

Proyecto del reto **F · Clima y riesgo**, de Ciencia de Datos con Python. El trabajo combina detecciones satelitales, pronósticos meteorológicos y análisis raster. El Niño se incorpora como contexto climático documentado, sin atribuirle automáticamente cada incendio o anomalía de temperatura.

## Estado

Fuentes auditadas, detecciones preparadas y piloto agrícola de tres zonas completado el 21 de octubre de 2026. Todavía no hay ranking nacional de prioridad ni dashboard publicado. Los números del ejemplo del profesor no son resultados de este proyecto.

- [Hoja de ruta y decisiones metodológicas](docs/HOJA_DE_RUTA.md)
- [Fuentes y requisitos de los datos](docs/FUENTES.md)
- [Auditoría de acceso y calidad](docs/AUDITORIA_DATOS.md)
- [Preparación y resultados del piloto agrícola](docs/AVANCE_PILOTO.md)
- [Alcance previsto del mapa interactivo](docs/DASHBOARD.md)
- [Consigna del profesor](https://claude.ai/artifact/7PDjxhAxnnJV2K24rVKWT6)
- [Material de la sesión 07: raster](https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/07-raster)

## Producto previsto

1. Panorama de detecciones recientes y condiciones meteorológicas en sus ubicaciones, resumido por departamento.
2. Superficie agrícola MIDAGRI 2024 cercana a las detecciones, caracterizada con el raster WorldCover 2021; comparación explícita de ambas cartografías.
3. Contexto oficial de El Niño; la comparación histórica homogénea de temperatura queda como extensión.
4. Informe web público con mapa interactivo, filtros, tres hallazgos cuantificados, fuentes y limitaciones.

La extensión sobre condiciones favorables para nuevos incendios se incorporará después de completar el núcleo. No se presentarán probabilidades de ignición ni predicciones de hectáreas futuras sin un modelo validado.

## Qué demostrará el análisis raster

Inspección de bandas, clases, resolución y coordenadas; tratamiento de NoData; recorte de WorldCover; conteos por categoría y estadísticas zonales en entornos definidos en metros. Las operaciones se explicarán en un notebook que pueda usarse en la presentación. No se requiere dNBR ni medir superficie quemada para este reto.

## Alcance de las conclusiones

Un foco de calor es una detección, no un incendio individual ni una medida de superficie quemada. Las agrupaciones serán aproximaciones explícitas. La prioridad meteorológica será exploratoria y no una alerta oficial. Una captura de datos con fecha de corte no se describirá como un monitor permanentemente actualizado.

La clase agrícola de WorldCover representa principalmente cultivos anuales y puede omitir cultivos leñosos permanentes. La proximidad del fuego no prueba daño, aumento térmico en las parcelas ni pérdida de producción. Las hectáreas serán superficie agrícola cartografiada cercana, no cultivo perdido. MIDAGRI mejora la cobertura del inventario agrícola disponible, pero no acredita cultivo activo en cada parcela ni se asume más exacto en todos los lugares sin validación.

Antes de publicar resultados, este README se completará con las fechas efectivas de cada fuente, el método ejecutado, al menos un mapa y tres hallazgos con números, conforme a la rúbrica.

## Auditoría inicial

El script `scripts/auditar_fuentes.py` comprueba acceso, fechas, campos, geometrías y una muestra de meteorología y raster. Guarda originales en `data/raw/` y un inventario en `docs/AUDITORIA_DATOS.json`. No calcula prioridades ni predicciones. Ejecutarlo dentro de un entorno aislado con las dependencias de `requirements-auditoria.txt`.

## Avance verificable

La captura tiene 2.727 detecciones nominales/altas en las últimas 168 h. De ellas, 234 corresponden a las últimas 48 h y forman 131 agrupaciones aproximadas recientes. Es un conteo, no un ranking agrícola ni un número de incendios confirmados.

En el piloto, la zona de Madre de Dios tiene 91,15 ha de superficie agrícola MIDAGRI dentro del entorno de 1 km y solo 0,16 ha de clase cultivo en WorldCover. Las fechas y definiciones son diferentes; no se interpreta la discrepancia como expansión agrícola medida ni pérdida de cultivo. Ver [detalle y comprobaciones](docs/AVANCE_PILOTO.md).

## Reproducir la preparación y el piloto

Con un entorno aislado y `requirements-analisis.txt`, conservar los originales de la auditoría e iniciar en la raíz del repositorio:

```powershell
python scripts/descargar_midagri.py
tar -xf data/raw/midagri/MNSA_2024.rar -C data/raw/midagri
python scripts/preparar_detecciones.py
python scripts/piloto_agricola.py
python scripts/graficar_piloto.py
```

La extracción se realiza tras comprobar el listado del archivo oficial. MIDAGRI nacional se conserva localmente (aproximadamente 402 MB comprimido); la web utilizará recortes y tablas pequeños. Las respuestas meteorológicas de este piloto quedan guardadas y no se actualizarán en silencio.
