# Incendios en el Perú: clima y riesgo

**Pregunta:** ¿qué zonas con detecciones recientes de fuego presentan condiciones meteorológicas favorables a su propagación durante los próximos siete días, y en qué departamentos se concentran?

Proyecto del reto **F · Clima y riesgo**, de Ciencia de Datos con Python. El trabajo combina detecciones satelitales, pronósticos meteorológicos y análisis raster. El Niño se incorpora como contexto climático documentado, sin atribuirle automáticamente cada incendio o anomalía de temperatura.

## Estado

Planificación inicial, 21 de octubre de 2026. Todavía no hay resultados ni código de análisis. Los números de ejemplo del profesor no son resultados de este proyecto.

- [Hoja de ruta y decisiones metodológicas](docs/HOJA_DE_RUTA.md)
- [Fuentes y requisitos de los datos](docs/FUENTES.md)
- [Consigna del profesor](https://claude.ai/artifact/7PDjxhAxnnJV2K24rVKWT6)
- [Material de la sesión 07: raster](https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/07-raster)

## Producto previsto

1. Panorama de detecciones recientes y condiciones meteorológicas en sus ubicaciones, resumido por departamento.
2. Un caso con Sentinel-2: imágenes antes y después, NBR, dNBR y superficie con señal compatible con quema; se reportarán fechas, nubes, umbral y cobertura observable.
3. Contexto de El Niño y una comparación histórica de temperatura para el caso de estudio, si la calidad y disponibilidad permiten una comparación homogénea.
4. Informe web público con mapa interactivo, filtros, tres hallazgos cuantificados, fuentes y limitaciones.

La extensión sobre condiciones favorables para nuevos incendios se incorporará después de completar el núcleo. No se presentarán probabilidades de ignición ni predicciones de hectáreas futuras sin un modelo validado.

## Qué demostrará el análisis raster

Inspección de bandas, resolución y coordenadas; tratamiento de NoData y nubes; recorte de imágenes; alineación de grillas; cálculo de índices; estadísticas zonales y áreas en un sistema adecuado. Las operaciones se explicarán en un notebook que pueda usarse en la presentación.

## Alcance de las conclusiones

Un foco de calor es una detección, no un incendio individual ni una medida de superficie quemada. Las agrupaciones serán aproximaciones explícitas. La prioridad meteorológica será exploratoria y no una alerta oficial. Una captura de datos con fecha de corte no se describirá como un monitor permanentemente actualizado.

Antes de publicar resultados, este README se completará con las fechas efectivas de cada fuente, el método ejecutado, al menos un mapa y tres hallazgos con números, conforme a la rúbrica.
