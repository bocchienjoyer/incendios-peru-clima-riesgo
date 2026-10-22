# Hoja de ruta: clima y riesgo de incendios en el Perú

Versión de trabajo: 21 de octubre de 2026. Documento previo al código; las propuestas pendientes de verificación se identifican expresamente.

## 1. Objetivo y alcance

Responder una pregunta acotada: **¿qué zonas con detecciones recientes de fuego coinciden con condiciones meteorológicas favorables a su propagación durante los próximos siete días, y cómo se distribuyen por departamento?**

La unidad de análisis será la agrupación aproximada de detecciones, con su ubicación y ventana temporal. El departamento será la unidad de presentación. No se asignará el clima de una capital a todos los incendios de su departamento.

El resultado será una priorización exploratoria para vigilancia, acompañada de un caso de área quemada con Sentinel-2. No se estimará velocidad de propagación, perímetro futuro, daños ni probabilidad de incendio. La exposición de personas y bienes queda fuera del núcleo; por ello se hablará con precisión de peligro meteorológico y condiciones favorables al fuego, aunque el reto se titule «Clima y riesgo».

## 2. Lo que exige la consigna

La diapositiva 7 define el reto F mediante humedad, viento y lluvia de Open-Meteo y pregunta qué incendios pueden crecer esta semana. La diapositiva 9 establece una rúbrica general:

- Mínimo: un incendio, dNBR, mapa y hectáreas quemadas, con fechas y porcentaje de nubes.
- Bueno: lo anterior más un cruce, incluido el clima.
- Excelente: lo anterior más un dashboard que explique el hallazgo.
- README: pregunta, datos y fechas, método, tres hallazgos con números, mapa y limitaciones.

Para cubrir ambas indicaciones, se incluirá un caso dNBR además del análisis meteorológico. No hace falta replicar todo el monitor del profesor, usar IA, procesar Sentinel-2 para todo el país ni hacer un estudio histórico nacional desde 2012.

## 3. Decisiones propuestas antes del procesamiento

| Decisión | Propuesta | Motivo y límite |
|---|---|---|
| Fecha de corte | Fijar una hora de descarga T y conservar las respuestas originales | Las fuentes cambian; una ejecución debe poder auditarse |
| Detecciones | Descargar siete días; destacar las últimas 48 horas respecto de T | «Reciente» no equivale a incendio confirmado que continúa activo |
| Sensor inicial | VIIRS S-NPP, confianza nominal y alta | Mantener una fuente consistente; comprobar disponibilidad antes de fijarla |
| Agrupación | Usar como punto de partida proximidad de 1 km y 48 h | Referencia del profesor; revisar encadenamientos y sensibilidad |
| Horizonte | Siete días desde T, separando primeras 72 h y resto | Mostrar que la incertidumbre aumenta con el horizonte |
| Clima | Pronóstico horario en ubicaciones de las agrupaciones | Conservar coincidencia temporal de humedad, viento y lluvia |
| Raster obligatorio | Sentinel-2 L2A en un caso acotado | Demostrar bandas, máscaras, índices, área y estadísticas zonales |
| Cobertura | WorldCover 2021 alrededor del caso y agrupaciones seleccionadas | Contexto de vegetación; no representa exactamente el combustible actual |
| Niño | ENFEN y comparación histórica local homogénea | Contexto y asociación, sin afirmación causal |
| Web | Informe estático interactivo con datos procesados | Acceso público y rápido; sin depender de recalcular imágenes al abrirlo |

Si S-NPP no tiene cobertura suficiente, se documentará el cambio de sensor o la combinación. No se sumarán sensores, sobrevuelos ni INPE y FIRMS como si cada fila fuera un incendio diferente.

## 4. Etapas y criterios para avanzar

### Etapa 1 — Auditoría de fuentes y cierre del diseño

1. Comprobar acceso a FIRMS, Open-Meteo, límites con UBIGEO y catálogo Sentinel-2.
2. Crear inventario de URL, proveedor, licencia, fecha del dato, fecha de descarga, unidades, cobertura, sensor, modelo y resolución.
3. Descargar una muestra pequeña para comprobar columnas, horas, calidad y valores faltantes.
4. Revisar los rasters del laboratorio si se desean reutilizar: no tratarlos como clima actual hasta identificar sus fechas, unidades y significado de bandas.
5. Mostrar al estudiante las decisiones y una muestra legible antes del cálculo principal.

**Salida:** fuentes verificadas, fecha de corte y parámetros documentados. No fabricar conclusiones si una fuente falla.

### Etapa 2 — Ubicar las detecciones recientes

1. Filtrar Perú mediante polígonos, revisar confianza y eliminar duplicados exactos.
2. Mantener fecha, hora, satélite y FRP; transformar UTC a hora de Lima para presentación.
3. Revisar fuentes térmicas persistentes y volcanes usando las banderas disponibles y contexto verificable; registrar exclusiones.
4. Formar agrupaciones espaciotemporales aproximadas. Revisar grupos muy extensos por encadenamiento y los truncados por la ventana de siete días.
5. Identificar cuáles contienen detecciones de las últimas 48 h y mostrar última fecha detectada.
6. Asignar departamentos sin duplicar agrupaciones que cruzan límites; conservar esa condición como atributo.

**Salida:** mapa de detecciones y tabla de agrupaciones. Las cantidades de detecciones y agrupaciones se reportarán por separado. Ausencia de detección no significa ausencia de fuego.

### Etapa 3 — Prioridad meteorológica

Variables: temperatura del aire a 2 m, humedad relativa a 2 m, velocidad del viento a 10 m y precipitación horaria. Guardar coordenadas solicitadas y devueltas, elevación, unidades, zona horaria, modelo y hora de descarga. Procurar un único modelo global para comparabilidad; verificar que cubra el horizonte y todas las variables.

Para una agrupación pequeña se usará una ubicación representativa cercana a sus detecciones. En agrupaciones extensas se comprobarán varios puntos y se reportará el rango; puntos que comparten la misma celda meteorológica no se interpretarán como información independiente.

**Indicador propuesto:** número y porcentaje de horas pronosticadas en que coinciden aire seco, viento y escasa precipitación reciente. Ejemplo inicial para discutir antes de calcular: humedad < 30 %, viento ≥ 20 km/h y precipitación acumulada en las 24 h anteriores < 2 mm. La ventana de lluvia incluirá historia previa a T y el pronóstico posterior, distinguiendo ambas procedencias.

Estos cortes son hipótesis exploratorias, no umbrales oficiales validados para el Perú. Se revisará su fundamento y se fijará la regla antes de ver el ranking. Se mostrará sensibilidad, por ejemplo humedad de 30/40 %, viento de 15/20 km/h y lluvia de 1/2 mm. Si no hay fundamento suficiente para clases «alto/medio/bajo», se mostrarán las variables y horas directamente, sin inventar esas clases.

No se combinará la humedad mínima de una hora con el viento máximo de otra para afirmar que ocurrieron simultáneamente. La temperatura y la lluvia de los siete días previos se mostrarán como contexto adicional; no se asignarán pesos arbitrarios a un índice compuesto. Poca lluvia durante una semana no demuestra por sí sola sequía.

**Resumen por departamento:** detecciones, agrupaciones recientes, proporción de agrupaciones evaluables con horas favorables y mayor número de esas horas entre sus agrupaciones. Mostrar denominadores y datos faltantes. No llamar a esa proporción «porcentaje del territorio en riesgo».

**Salida:** tabla justificable de prioridades y series horarias para explorar casos. No es una probabilidad de crecimiento ni un índice FWI validado.

### Etapa 4 — Caso raster con Sentinel-2

Elegir un caso conectado con el panorama actual usando criterios publicados: detecciones claras, AOI manejable, imágenes con cobertura válida antes y después de la ventana analizada y cambio visible compatible con quema. No elegirlo por obtener la cifra más grande. Si ningún caso reciente es observable, documentar la limitación y separar explícitamente un caso retrospectivo cercano en fecha.

1. Definir el área de interés con las detecciones y un margen justificado. Ese margen no será el perímetro del incendio.
2. Mostrar escenas candidatas, fechas, identificadores y nubosidad de catálogo. Calcular además el porcentaje inválido dentro del AOI, que es el relevante.
3. Usar reflectancia Sentinel-2 L2A, aplicando correctamente escala y offset del producto. Revisar que las escenas sean comparables.
4. Alinear ambas fechas y bandas a una grilla común de 20 m. Para NBR con B08 y B12, reducir B08 de 10 a 20 m con agregación adecuada; no crear detalle nuevo ampliando B12. Remuestrear clases SCL con vecino más cercano.
5. Enmascarar NoData, píxeles defectuosos, sombras, nubes, cirros, nieve y otras clases no interpretables; revisar agua. Usar la intersección válida de ambas fechas, con el mismo denominador espacial.
6. Calcular NBR = (NIR − SWIR) / (NIR + SWIR) y dNBR = NBR_antes − NBR_después. Revisar denominadores nulos.
7. Comparar RGB antes/después, detecciones y mapa dNBR. Distinguir cambio por quema de cosecha, agua, sombra u otros cambios.
8. Evaluar dNBR ≥ 0,27 como referencia utilizada por el profesor, comparando alternativas como 0,10 y 0,44. Estos cortes no prueban severidad ecológica local y no deben universalizarse.
9. Calcular superficie con señal compatible con quema en una proyección métrica adecuada al caso; publicar hectáreas, área observable, área sin observación y porcentaje válido. Si el fuego sigue activo, llamar al resultado estimación parcial hasta la fecha de imagen.
10. Resumir por distrito mediante estadísticas zonales e intersección de píxeles; comprobar que las áreas no se dupliquen en límites. Recortar WorldCover y resumir categorías como contexto, si está disponible.

**Salida:** mapa de caso, tabla de áreas y ficha metodológica. NoData no se transforma en «no quemado», los focos no se multiplican por 375 × 375 m para obtener área, y el buffer no se presenta como superficie quemada.

### Etapa 5 — Temperatura y contexto de El Niño

Leer el comunicado ENFEN vigente al corte y distinguir Niño Costero (Niño 1+2) de la señal del Pacífico central (Niño 3.4). El comunicado N.º 18, del 16 de octubre de 2026, es la referencia encontrada durante la planificación; habrá que comprobar si sigue siendo el vigente al ejecutar.

Para comprobar «más caliente de lo habitual» en el caso, propuesta: temperatura máxima media de una ventana histórica reciente de 30 días completos frente a las mismas fechas de 1991–2020, usando un solo producto ERA5 o ERA5-Land y la misma ubicación. Terminar la ventana en la última fecha común disponible, considerando el retraso del reanálisis. Reportar diferencia en °C, años válidos y sensibilidad al período de referencia. No mezclar sin aviso un pronóstico actual con una climatología de otro producto.

Una anomalía local y un contexto ENSO compatible no demuestran cuánto calentamiento o fuego causó El Niño. Si no podemos construir la comparación homogénea, conservaremos el contexto oficial y no afirmaremos haber medido una anomalía propia.

**Salida:** gráfico breve y texto con alcance regional y temporal explícito.

### Etapa 6 — Revisión y explicación para la presentación

- Revisar mapas superpuestos, rangos físicos, unidades, fechas y denominadores.
- Comparar un subconjunto de agrupaciones con reportes oficiales de COEN, INDECI o SERFOR cuando existan, sin equiparar automáticamente los registros.
- Repetir solamente las decisiones que pueden cambiar conclusiones: agrupación, ventanas, umbrales meteorológicos, máscara/umbral dNBR y criterio de inclusión de píxeles en los bordes.
- Comprobar coherencia entre tabla, mapa y texto; registrar discrepancias y casos sin información.
- Preparar tres hallazgos con cifras reales y un ejemplo en que una decisión metodológica cambie el resultado. Ningún hallazgo está decidido de antemano.

**Salida:** notebook explicativo y resultados que el estudiante pueda defender: qué vale cada píxel, por qué se eligieron esas fechas, cómo se excluyeron nubes y cómo se pasó de raster a tabla.

### Etapa 7 — Página pública e informe

El notebook hará el procesamiento; la web leerá productos pequeños ya calculados. Propuesta de publicación: HTML interactivo en GitHub Pages, sujeto a verificar las opciones del repositorio. No se necesita un servidor Python para que el lector explore los resultados.

Contenido previsto:

1. Pregunta, fecha/hora de corte y resumen de tres hallazgos.
2. Mapa nacional con detecciones/agrupaciones, filtro por departamento y antigüedad.
3. Tabla de condiciones meteorológicas con detalles de humedad, viento, lluvia y temperatura; contraste de primeras 72 h frente al resto de la semana.
4. Caso Sentinel-2 con imágenes antes/después, dNBR, hectáreas y cobertura válida.
5. Contexto de El Niño, método, incertidumbre, fuentes y descarga de tablas.

No depender de llamadas a las APIs desde el navegador del lector. La versión inicial será una captura fechada; no se prometerá actualización automática. Las fechas observadas, pronosticadas y de adquisición satelital se mostrarán por separado. Verificar acceso sin iniciar sesión, controles, leyendas, uso en móvil y coherencia de unidades.

**Salida final:** enlace público, README completo, notebook ejecutable e inventario de datos. No publicar raster pesados en Git; conservar productos pequeños y las instrucciones para obtener los originales.

## 5. Extensión: zonas sin detecciones recientes

Se abordará tras cerrar el núcleo. Empezar por una región de interés con una malla de muestreo coherente con la resolución meteorológica, documentando cobertura y costo de consultas. Combinar las mismas condiciones meteorológicas con fracción de cobertura vegetal obtenida de WorldCover; excluir agua, zonas urbanas y suelo desnudo con reglas explícitas.

La conclusión permitida será «condiciones favorables al fuego en áreas con vegetación, sin detecciones recientes en nuestra fuente». Para hablar de probabilidad de nuevos incendios faltan igniciones, prácticas de quema, humedad del combustible y validación histórica. No interpolar unos pocos puntos a un mapa fino del país ni asignar el clima de una capital a todo un departamento. La temperatura elevada de un desierto no basta para concluir peligro de incendio forestal.

## 6. Organización prevista cuando comience el código

- `notebooks/`: explicación y ejecución del análisis.
- `src/`: funciones reutilizables de descarga y procesamiento, si hacen falta.
- `data/raw/`: originales guardados localmente, excluidos de Git.
- `data/processed/`: tablas pequeñas y metadatos reproducibles.
- `outputs/`: mapas y gráficos finales.
- `site/`: informe web público.
- `docs/`: fuentes y decisiones metodológicas.

Estas carpetas se crearán cuando hagan falta. En esta etapa se guardan únicamente los documentos del plan y las exclusiones de Git.

## 7. Orden de prioridades

Primero datos auditados y caso raster viable; después cruce climático; luego tres hallazgos comprobados; finalmente presentación web y extensión sobre posibles nuevos fuegos. Si hay que reducir alcance, conservar un buen caso dNBR y su análisis meteorológico antes que ampliar cobertura territorial o añadir modelos complejos.

La siguiente sesión de trabajo debe comenzar por la auditoría y selección de escenas, sin calcular todavía índices ni rankings definitivos. Las decisiones se explicarán antes de ejecutar cada bloque principal.
