# Hoja de ruta: cultivos, fuego reciente y condiciones meteorológicas

Revisión del 21 de octubre de 2026. Alcance ajustado a la aclaración del estudiante: la rúbrica se adapta al reto F. No se requiere calcular dNBR ni superficie quemada.

## 1. Pregunta y producto

**¿Qué zonas agrícolas cercanas a detecciones recientes de fuego coinciden con condiciones meteorológicas favorables a su propagación durante los próximos siete días, y en qué departamentos se concentran?**

El foco es agrícola: identificar proximidad entre cultivos cartografiados y fuego reciente, e interpretar esa proximidad junto a las condiciones meteorológicas. El resultado será un insumo exploratorio para priorizar vigilancia agrícola. No se medirá pérdida de producción ni daño confirmado.

| Nivel del trabajo | Entrega para nuestro reto |
|---|---|
| Mínimo | Detecciones recientes, condiciones meteorológicas y tabla de prioridades por departamento |
| Bueno | Lo anterior cruzado con cultivos cartografiados: superficie y fracción de cultivo cerca de las detecciones |
| Excelente | Dashboard público que explique los hallazgos, permita explorar el mapa y muestre método y límites |

No se calcularán NBR, dNBR, hectáreas quemadas, perímetros futuros ni probabilidades de ignición. Sentinel-2 queda fuera del plan de ejecución. El Niño permanece como contexto oficial; una comparación histórica local de temperatura es opcional y posterior al núcleo.

## 2. Por qué cruzar con cultivos

Dos agrupaciones con condiciones meteorológicas similares pueden tener distinta superficie agrícola alrededor. El cruce permitirá localizar dónde coinciden detecciones recientes, condiciones favorables a la propagación y cultivos cercanos. La composición de las otras coberturas se conservará como contexto.

La hipótesis del estudiante es que temperaturas elevadas y lluvia escasa pueden agravar la vulnerabilidad agrícola y que un fuego cercano podría añadir presión. El estudio medirá solo las señales disponibles: meteorología, proximidad y superficie cartografiada. La temperatura regional de Open-Meteo no permite atribuir al incendio un aumento local de temperatura en las parcelas. Tampoco mide temperatura foliar, humedad del combustible ni estrés fisiológico. No se inferirán cultivos secos, pérdidas de rendimiento, humo o daño térmico con estas fuentes.

| Cruce evaluado | Pregunta adicional | Decisión |
|---|---|---|
| WorldCover, clase 40 | ¿Cuánta superficie clasificada como cultivo hay cerca de detecciones con condiciones favorables? | Elegido como base raster disponible |
| WorldPop | ¿Cuánta población vive cerca? | Útil para exposición humana; añade antigüedad y supuestos de distribución poblacional |
| Áreas protegidas | ¿Qué prioridades coinciden con espacios protegidos? | Útil para conservación, pero principalmente vectorial; extensión posible |

WorldCover 2021 tiene clases a 10 m; se usará como contexto histórico de cobertura, no como mapa de combustible o vegetación actual. «Tree cover» se traducirá como cobertura arbórea: no identifica por sí sola bosque natural, plantación ni estado de conservación. No se asumirán órdenes de peligrosidad entre clases sin evidencia.

**Límite agrícola fundamental:** el manual define la clase 40 principalmente como cultivo anual herbáceo; los cultivos leñosos permanentes pueden quedar en árboles/matorrales y los invernaderos en urbano. No presentarla como el universo de cultivos peruanos ni afirmar ausencia de agricultura donde la clase 40 sea cero. No identifica especie cultivada, riego, campaña o si la parcela sigue en producción en 2026.

Se encontró una actualización del Mapa Nacional de Superficie Agrícola, oficializada por MIDAGRI en 2025 con trabajo cartográfico concluido en 2024. Su acceso geográfico, licencia y compatibilidad con el objetivo aún deben verificarse; la fecha de oficialización no equivale a fecha de cultivo activo. Es el complemento candidato si queremos ampliar cobertura a agricultura leñosa y otros terrenos agrícolas. No reemplazarlo por cifras departamentales repartidas artificialmente entre píxeles.

## 3. Diseño espacial y temporal

- Fijar fecha y hora de descarga T y guardar los originales.
- Descargar CSV VIIRS S-NPP de siete días, comprobar fechas efectivas y filtrar la ventana exacta de 168 h. El nombre del archivo no garantiza el corte deseado.
- Usar confianza nominal y alta. Reconocer ambas codificaciones posibles: `nominal/high` y `n/h`.
- Destacar agrupaciones con detecciones en las últimas 48 h. «Reciente» no equivale a incendio confirmado que sigue activo.
- Proponer agrupación por proximidad de 1 km y 48 h, como referencia de clase. Revisar encadenamientos, grupos extensos y sensibilidad antes de fijar la regla.
- Consultar meteorología en las agrupaciones, conservando coordenadas solicitadas y devueltas. No usar una capital como representante de todo su departamento.
- Evaluar siete días posteriores a T; separar primeras 72 h y resto. Conservar historia de lluvia suficiente para las primeras ventanas de 24 h.
- Usar un modelo meteorológico global fijo y documentar resolución nativa e interpolación temporal. Una salida horaria no implica observaciones independientes cada hora.
- Aplicar buffers métricos de 1 km alrededor de las detecciones agrupadas, disueltos por agrupación, como entorno de consulta de cobertura. Comprobar sensibilidad a 0,5 y 2 km. Son vecindades analíticas, no perímetros ni distancias predichas de propagación.

La unidad de análisis será la agrupación aproximada de detecciones; el departamento será la unidad de presentación. Los grupos que crucen fronteras administrativas se marcarán y tendrán una regla de asignación única para el ranking. No sumar áreas de buffers superpuestos para declarar una superficie nacional expuesta.

## 4. Indicador meteorológico

Variables base: humedad relativa a 2 m, viento a 10 m, precipitación horaria y temperatura del aire a 2 m. Guardar unidades, elevación, modelo, coordenadas, horas y fecha de consulta.

Propuesta inicial: contar las horas de coincidencia entre humedad baja, viento y poca lluvia acumulada en las 24 h previas. Ejemplo de cortes para evaluar antes de calcular prioridades: humedad < 30 %, viento ≥ 20 km/h y lluvia previa < 2 mm. Son hipótesis exploratorias; falta justificar y fijar los cortes. Mostrar sensibilidad con humedad de 30/40 %, viento de 15/20 km/h y lluvia de 1/2 mm. Si no hay fundamento para clases de peligro, mostrar variables y horas directamente.

No mezclar la humedad mínima de una hora con el viento máximo de otra. No añadir pesos arbitrarios a una suma de temperatura, viento, lluvia y cobertura. No llamar sequía a una semana seca. La cobertura describirá el entorno y permitirá comparar estratos; no será un multiplicador inventado de probabilidad.

La temperatura se mostrará como contexto. Para afirmar «por encima de lo habitual» hace falta una referencia histórica homogénea. El estado de El Niño no demuestra por sí solo una anomalía térmica en cada departamento ni atribuye causalmente los incendios.

Como contexto agrícola, resumir precipitación de los 14 días anteriores y días con lluvia escasa, conservando su procedencia como modelo/reanálisis. Estos datos no demostrarán estrés hídrico del cultivo. Una anomalía de lluvia o diagnóstico de sequía exige referencia histórica o boletín oficial aplicable; se añadirá solo cuando la fuente y el período estén claros.

## 5. Qué hará el análisis raster

WorldCover será el raster central del trabajo:

1. Inspeccionar banda, CRS, transformación, resolución, tipo de dato, clases y NoData.
2. Leer únicamente ventanas necesarias de los GeoTIFF optimizados para acceso remoto; evitar descargar el país completo a 10 m.
3. Crear buffers en una proyección métrica adecuada y transformar sus polígonos al CRS del raster antes del recorte.
4. Recortar, enmascarar NoData y contar píxeles válidos por categoría. Para superficies, ponderar área de píxel/intersección o emplear una proyección adecuada; no convertir grados cuadrados en hectáreas.
5. Obtener una fila por agrupación con superficie clasificada como cultivo, fracción de cultivo y fracciones de otras clases. El denominador será el entorno con observación válida; reportar también la fracción no observable. Las hectáreas se etiquetarán como cultivo cartografiado cercano, nunca cultivo quemado o perdido.
6. Comparar inclusión por centro de píxel frente a `all_touched` en bordes. No promediar los códigos de clase: una media de 10 y 40 no representa una cobertura real.
7. Usar vecino más cercano si es necesario remuestrear categorías. No ampliar la meteorología a 10 m para fingir detalle climático local.

Se conservarán clases separadas. Cobertura arbórea, matorral, pastizal y cultivo serán los contrastes principales; humedales, manglares y otras categorías se reportarán explícitamente, sin declararlas automáticamente incombustibles. Agua, nieve, urbano y suelo desnudo no se interpretarán como combustible vegetal por defecto.

## 6. Etapas

### Paso 1 — Auditoría de datos y cierre del diseño

Comprobar acceso a FIRMS, Open-Meteo, WorldCover y límites; guardar una captura y verificar fechas, campos, calidad, geometrías, unidades y licencias. Consultar meteorología y leer una pequeña ventana raster en una ubicación de prueba. Esta muestra verifica acceso; no es una selección de caso crítico.

**Salida:** inventario, informe de auditoría, originales locales y decisiones pendientes. No calcular un ranking final todavía.

### Paso 2 — Preparación de detecciones

Filtrar Perú, ventana temporal y confianza; eliminar duplicados exactos; revisar fuentes térmicas persistentes cuando sea posible; agrupar y asignar departamentos. Conservar última detección y sensor. No sumar sensores, INPE y FIRMS ni sobrevuelos como si cada fila fuera un incendio.

**Salida:** mapa de detecciones y tabla auditable de agrupaciones recientes.

### Paso 3 — Cruce meteorológico

Consultar ubicaciones y calcular simultaneidad de condiciones con los cortes documentados. Revisar grupos extensos y localizaciones que comparten celda meteorológica. Mostrar datos faltantes y sensibilidad.

**Salida:** horas/porcentaje de horas favorables, perfiles meteorológicos y prioridades preliminares.

### Paso 4 — Cruce raster de cobertura

Recortar WorldCover en los entornos y obtener fracciones por clase. Comparar cobertura alrededor de grupos con más y menos horas favorables. Mantener visibles las fechas 2021/2026 y las diferentes resoluciones.

**Salida:** tabla de prioridades enriquecida y mapa de cobertura para explicar el paso de píxeles a tabla.

**Prioridad agrícola:** presentar dos dimensiones, horas meteorológicas favorables y hectáreas cartografiadas de cultivo cercano, sin multiplicarlas para fingir pérdidas o probabilidad. Mostrar ambos criterios y cómo cambia el orden si se prioriza extensión agrícola o persistencia meteorológica. Para totales departamentales, unir buffers/intersecciones y contar cada píxel agrícola una sola vez; no sumar ciegamente las áreas por agrupación. Mantener también la fracción agrícola para comparar entornos de diferente tamaño.

### Paso 5 — Validación y narrativa

Revisar mapas, denominadores, cortes y sensibilidad al buffer. Contrastar una muestra con reportes oficiales si existen. Establecer tres hallazgos con cifras reales; el análisis puede mostrar diferencias débiles o ninguna prioridad bajo ciertos cortes.

La tabla por departamento incluirá detecciones, agrupaciones recientes, agrupaciones evaluables, horas favorables y hectáreas únicas de cultivo cartografiado en los entornos estudiados. Los resultados se referirán a esas agrupaciones, no a todo el territorio departamental. Mostrar números absolutos y proporciones para evitar premiar únicamente departamentos grandes.

**Salida:** resultados revisados y notebook que explique raster, clases, NoData, recorte y estadísticas zonales.

### Paso 6 — Dashboard público

Página interactiva con datos ya procesados: pregunta, tres hallazgos, fecha de corte, mapa, filtro departamental, tabla de prioridades, curvas meteorológicas, cobertura, contexto de El Niño y método. Propuesta técnica: HTML estático en GitHub Pages, verificando acceso sin cuenta y uso en móvil.

No recalcular raster ni llamar APIs desde el navegador del lector. La primera versión será una captura fechada, sin prometer actualización automática. Las horas anteriores al corte obtenidas con `past_days` son pronósticos archivados, no observaciones de estaciones. Los datos originales pesados quedarán fuera de Git.

## 7. Extensiones y prioridades

Después del núcleo se podrá evaluar una malla de zonas con vegetación y sin detecciones recientes. Esa evaluación necesita muestreo espacial explícito, no solo puntos donde ya se detectó fuego. Permitirá hablar de condiciones favorables; para probabilidades de nuevos incendios faltan igniciones, combustible actual y validación histórica.

La comparación histórica de temperatura, población y áreas protegidas son extensiones. No se incorporarán todas. Orden de trabajo: fuentes verificadas → detecciones y meteorología → cobertura raster → hallazgos revisados → dashboard.

## 8. Organización y reproducción

- `scripts/`: auditoría inicial de fuentes.
- `docs/`: plan, fuentes e informe de auditoría.
- `data/raw/`: originales y muestra raster, excluidos de Git.
- `notebooks/`: se añadirá con el análisis explicado.
- `data/processed/`, `outputs/` y `site/`: se crearán cuando haya productos.

Usar un entorno local aislado para no modificar las dependencias de otros cursos. Publicar las dependencias usadas y conservar huellas de integridad de los originales.
