# Fuentes e inventario inicial

Consultado durante la planificación del 21 de octubre de 2026. Este catálogo identifica fuentes candidatas; todavía no acredita que los datos hayan sido descargados ni procesados.

| Fuente | Uso previsto | Precaución |
|---|---|---|
| [Consigna del profesor](https://claude.ai/artifact/7PDjxhAxnnJV2K24rVKWT6) | Reto F y rúbrica; diapositivas 3 a 9 | Las cifras del ejemplo pertenecen al trabajo del profesor |
| [Sesión 07](https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/07-raster) | Fundamentos y flujo de análisis | Adaptar el método a la variable y escala del proyecto |
| [raster_aplicado.ipynb](https://github.com/d2cml-ai/Data-Science-Python/blob/main/sessions/07-raster/lecture/raster_aplicado.ipynb) | NoData, estadísticas zonales, suma/media, áreas y validación | No trasladar indicadores económicos a este análisis |
| [RASTER_LAB.ipynb](https://github.com/d2cml-ai/Data-Science-Python/blob/main/sessions/07-raster/lab/RASTER_LAB.ipynb) | Bandas climáticas, recorte y comparación de resoluciones | Sus cinco períodos deben identificarse antes de reutilizar los datos |
| [NASA FIRMS: descargas de fuego activo](https://firms.modaps.eosdis.nasa.gov/active_fire) | CSV VIIRS de Sudamérica, últimos siete días, filtrado a Perú | Nominalmente 375 m; detección no equivale a incendio ni área quemada. Verificar sensor, confianza y cobertura |
| [NASA: preguntas y respuestas FIRMS, 2025](https://appliedsciences.nasa.gov/sites/default/files/2025-05/Part%203%20FIRMS%202025%20Q%26A%20Session.docx.pdf) | Límites de interpretación de focos y superficie quemada | No estimar área como número de focos multiplicado por área nominal de píxel |
| [Open-Meteo: pronóstico](https://open-meteo.com/en/docs) | Humedad, viento, lluvia y temperatura horarias de próximos siete días | Datos de modelos, no mediciones de estaciones en cada incendio. Registrar modelo, resolución, unidades, coordenadas y hora de descarga |
| [Open-Meteo: histórico](https://open-meteo.com/en/docs/historical-weather-api) | Comparación de temperatura con referencia 1991–2020 | Fijar ERA5 o ERA5-Land para consistencia; considerar retraso de disponibilidad |
| [Sentinel-2 L2A en Planetary Computer](https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a) | Reflectancia NIR/SWIR, RGB y clasificación SCL para dNBR | La viabilidad de escenas y acceso se comprobará en la etapa 1; diferentes bandas tienen diferentes resoluciones |
| [ESA WorldCover en Planetary Computer](https://planetarycomputer.microsoft.com/dataset/esa-worldcover) | Cobertura del suelo 2021, 10 m, contexto vegetal | Mapa histórico de clases, no inventario actual de combustible ni humedad |
| [Límites: peru-geojson](https://github.com/juaneladio/peru-geojson) | Departamentos/distritos y UBIGEO según propuesta del profesor | Verificar versión, procedencia, geometrías, claves y licencia antes de usar |
| [ENFEN: comunicados](https://enfen.imarpe.gob.pe/comunicados/) | Estado de El Niño y perspectivas regionales | Comprobar vigencia al corte; distinguir Niño 1+2 y Niño 3.4 |
| [ENFEN N.º 18, 16/10/2026](https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-18-2026/?wpdmdl=2165) | Contexto oficial encontrado durante planificación | Describe anomalías del mar y perspectivas regionales; no atribuye los incendios individuales |

## Registro requerido para cada descarga

- Proveedor, URL o identificador STAC y licencia/atribución.
- Fecha y hora de consulta, fecha del dato, período cubierto y zona horaria.
- Sensor, producto, versión y modelo, según corresponda.
- CRS, resolución, bandas, unidades, escala, offset y NoData para rasters.
- Área solicitada, cobertura efectiva y proporción válida.
- Filtros y exclusiones; ubicación del original y huella de integridad cuando sea posible.

No incluir claves ni credenciales en archivos públicos. Los datos grandes se conservarán localmente o mediante referencias reproducibles, según sus condiciones de uso.
