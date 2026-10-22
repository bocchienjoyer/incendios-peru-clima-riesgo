# Fuentes e inventario inicial

Actualizado el 21 de octubre de 2026. La evidencia de las descargas de prueba está en [AUDITORIA_DATOS.md](AUDITORIA_DATOS.md) y el inventario [JSON](AUDITORIA_DATOS.json). Una muestra de acceso no es un análisis nacional completo.

| Fuente | Uso previsto | Precaución |
|---|---|---|
| [Consigna del profesor](https://claude.ai/artifact/7PDjxhAxnnJV2K24rVKWT6) | Reto F y referencias de entrega | La rúbrica se adapta al reto: dNBR no es requisito para nuestro caso. Las cifras del ejemplo pertenecen al profesor |
| [Sesión 07](https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/07-raster) | Fundamentos y flujo de análisis | Adaptar el método a la variable y escala del proyecto |
| [raster_aplicado.ipynb](https://github.com/d2cml-ai/Data-Science-Python/blob/main/sessions/07-raster/lecture/raster_aplicado.ipynb) | NoData, estadísticas zonales, suma/media, áreas y validación | No trasladar indicadores económicos a este análisis |
| [RASTER_LAB.ipynb](https://github.com/d2cml-ai/Data-Science-Python/blob/main/sessions/07-raster/lab/RASTER_LAB.ipynb) | Bandas climáticas, recorte y comparación de resoluciones | Sus cinco períodos deben identificarse antes de reutilizar los datos |
| [NASA FIRMS: descargas de fuego activo](https://firms.modaps.eosdis.nasa.gov/active_fire) | CSV VIIRS de Sudamérica, últimos siete días, filtrado a Perú | Nominalmente 375 m; detección no equivale a incendio ni área quemada. Verificar sensor, confianza y cobertura |
| [NASA: preguntas y respuestas FIRMS, 2025](https://appliedsciences.nasa.gov/sites/default/files/2025-05/Part%203%20FIRMS%202025%20Q%26A%20Session.docx.pdf) | Límites de interpretación de focos y superficie quemada | No estimar área como número de focos multiplicado por área nominal de píxel |
| [Open-Meteo: pronóstico](https://open-meteo.com/en/docs) | Humedad, viento, lluvia y temperatura horarias de próximos siete días | Datos de modelos, no mediciones de estaciones en cada incendio. Registrar modelo, resolución, unidades, coordenadas y hora de descarga |
| [Open-Meteo: histórico](https://open-meteo.com/en/docs/historical-weather-api) | Comparación de temperatura con referencia 1991–2020 | Fijar ERA5 o ERA5-Land para consistencia; considerar retraso de disponibilidad |
| [ESA WorldCover en Planetary Computer](https://planetarycomputer.microsoft.com/dataset/esa-worldcover) | Raster central: cobertura del suelo 2021, 10 m, contexto vegetal | CC BY 4.0; 11 clases; NoData = 0. Mapa histórico, no combustible actual. La clase arbórea no distingue bosque natural de plantaciones |
| [Metadatos WorldCover](https://planetarycomputer.microsoft.com/api/stac/v1/collections/esa-worldcover) | Catálogo, clases, productos 2020/2021 y licencias | Usar 2021 v200; no interpretar diferencias 2020/2021 como cambio puro porque cambió el algoritmo |
| [Manual WorldCover v2](https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/docs/WorldCover_PUM_V2.0.pdf) | Definición agrícola, tabla 4, página 15 | Clase 40: principalmente cultivo anual herbáceo; cultivos leñosos permanentes pueden clasificarse como árboles/matorrales y los invernaderos como urbano |
| [Mapa agrícola actualizado: MIDAGRI, RM 0026-2025](https://busquedas.elperuano.pe/dispositivo/NL/2367371-1) | Referencia de superficie agrícola, cartografía actualizada hasta 2024 | Descarga e integración en tres recortes verificadas. Incluye superficie agrícola, no prueba cultivo activo en 2026; sin licencia abierta explícita encontrada en el paquete |
| [SIEA: descarga oficial superficie agrícola](https://siea.midagri.gob.pe/herramientas/superficie-agricola) | Enlace a MNSA_2024.rar alojado en Drive | 401.542.766 bytes, SHA-256 en MIDAGRI_ACCESO.json. 1.827 registros de categoría AGRICOLA, CRS EPSG:4326 y fuente 2024. Nacional guardado fuera de Git |
| [SENAMHI: pronóstico agroclimático agosto–octubre 2026](https://www.gob.pe/institucion/senamhi/informes-publicaciones/8454797-pronostico-de-riesgo-agroclimatico-agosto-octubre-2026) | Contexto por cultivo y contraste con fuentes peruanas | Se localizó la publicación; no se procesó su PDF ni se incorporaron diagnósticos a los resultados. Un pronóstico no confirma daño observado |
| [Open-Meteo: modelo ECMWF](https://open-meteo.com/en/docs/ecmwf-api) | Modelo fijo para comparar ubicaciones | El piloto usa IFS 0,25°, aproximadamente 25 km; la salida horaria interpola pasos nativos más espaciados. Evaluar IFS 9 km antes del procesamiento definitivo |
| [Límites: peru-geojson](https://github.com/juaneladio/peru-geojson) | Departamentos y códigos de dos dígitos | README indica INEI 2007 y archivo LICENSE MPL 2.0; geometrías simplificadas. Se usarán con atribución y sin adjudicar precisión catastral |
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
