# Paso 1: auditoría de fuentes

Consulta principal: **21 de octubre de 2026, 20:25 h de Lima** (22/10/2026, 01:25 UTC). Se probaron descargas públicas y una lectura raster. No se ha calculado un ranking, una superficie agrícola cercana al fuego ni daño a cultivos.

## Resultado de acceso y calidad

| Componente | Comprobación realizada | Resultado |
|---|---|---|
| NASA FIRMS, VIIRS S-NPP | Descargar CSV de Sudamérica y revisar campos/fechas | HTTP 200; 59.694 filas regionales; 3.553 dentro de los límites usados de Perú |
| Filtro de confianza y fecha | Confianza nominal/alta y 168 h previas a la consulta | 2.727 detecciones preliminares; no son incendios individuales |
| Límites departamentales | Geometrías, CRS y claves | 25 polígonos, EPSG:4326; cero geometrías inválidas/vacías y cero códigos duplicados |
| Open-Meteo | Consultar un punto con temperatura, humedad, viento y precipitación | HTTP 200; 216 horas de salida, sin valores nulos en las cuatro variables |
| Catálogo WorldCover | Consultar versión 2021 y una tesela para el punto de prueba | HTTP 200; producto v2.0.0, 11 clases, licencia CC BY 4.0 |
| Lectura WorldCover | Abrir COG remoto y guardar ventana de 128 × 128 | 16.384 píxeles válidos; una banda uint8, NoData = 0, EPSG:4326 |

Los originales y la muestra raster están en `data/raw/auditoria/20261022T012532Z/`, fuera de Git. Sus URL y huellas SHA-256, junto con metadatos y comprobaciones, están en [AUDITORIA_DATOS.json](AUDITORIA_DATOS.json). El entorno de auditoría y sus versiones se conservan en los archivos de dependencias del repositorio.

## Hallazgos de calidad que modifican el diseño

**El nombre «7d» no basta para definir la ventana.** El CSV recibido cubre desde 14/10/2026 03:28 UTC hasta 21/10/2026 19:04 UTC en toda Sudamérica. Hay que filtrar explícitamente las 168 h anteriores a T. No se detectaron fechas futuras ni duplicados exactos entre las filas dentro de Perú.

**La confianza viene como palabras.** En Perú aparecen `high` (244), `nominal` (2.928) y `low` (381), antes de filtrar la ventana exacta. La preparación admitirá también códigos cortos `n/h` si otro producto los usa. No convertir cada fila en un incendio ni multiplicarla por el área nominal del píxel.

**El punto de prueba está en Áncash y solo comprueba acceso.** Se eligió la detección nominal/alta más reciente, no una ubicación agrícola ni una prioridad. La ventana raster contiene varias clases y no contiene píxeles de clase 40. Esto no demuestra ausencia de agricultura en Áncash y no invalida el cruce: todavía falta seleccionar y recortar los entornos de todas las agrupaciones.

**La meteorología es más gruesa que el raster.** La muestra solicita IFS 0,25° (aproximadamente 25 km), con coordenadas de entrada −9,05636 / −78,60162 y celda devuelta −9,0 / −78,5. Antes del análisis definitivo se evaluará IFS 9 km. La salida horaria contiene interpolación de pasos nativos más espaciados. No mide el calentamiento local causado por un fuego en una parcela.

**Los límites son simplificados y antiguos.** El repositorio indica INEI 2007 y tiene archivo de licencia MPL 2.0. Son utilizables para la auditoría departamental con atribución; habrá que revisar puntos cerca de bordes y no asumir exactitud catastral.

**WorldCover no es agricultura actual completa.** Es de 2021 y su clase 40 representa principalmente cultivos anuales herbáceos; los leñosos permanentes pueden quedar en árboles/matorrales. Tiene que publicarse esa definición. La actualización del mapa agrícola de MIDAGRI, oficializada en 2025 y concluida cartográficamente en 2024, se identificó como complemento candidato; su descarga geográfica y licencia aún no están verificadas.

## Decisión al cerrar este paso

El cruce base es viable: detecciones recientes + meteorología + cultivo cartografiado (WorldCover, clase 40). El objetivo es priorización exploratoria de vigilancia agrícola, no medir cultivos secos, calor añadido por incendios o pérdida de producción. Las otras clases se conservarán como contexto.

Antes del cálculo del ranking deben fijarse el modelo meteorológico definitivo, los cortes de condiciones favorables, la agrupación de detecciones, el buffer agrícola y el tratamiento de solapamientos. Propuesta para revisar: entorno de 1 km, sensibilidad a 0,5/2 km y dos criterios visibles —horas favorables y hectáreas agrícolas cercanas— sin índice de pérdidas inventado.

## Próximo paso

Preparar las detecciones y las agrupaciones, mostrar su mapa y comprobar un pequeño piloto agrícola antes de ampliar el procesamiento. El informe final distinguirá superficie agrícola cartografiada próxima al fuego, datos meteorológicos y daño observado. Por ahora se ha completado la auditoría de acceso y muestras; no se ha investigado ni confirmado daño en parcelas.
