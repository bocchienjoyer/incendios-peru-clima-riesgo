# Incendios en el Perú: clima y riesgo

**Pregunta:** ¿qué zonas agrícolas cercanas a detecciones recientes de fuego coinciden con condiciones meteorológicas favorables a su propagación durante los próximos siete días, y en qué departamentos se concentran?

Proyecto del reto **F · Clima y riesgo**, de Ciencia de Datos con Python. El trabajo combina detecciones satelitales, pronósticos meteorológicos y análisis raster. El Niño se incorpora como contexto climático documentado, sin atribuirle automáticamente cada incendio o anomalía de temperatura.

## Estado

Diseño revisado y auditoría de fuentes iniciada el 21 de octubre de 2026. Todavía no hay ranking ni hallazgos finales. Los números del ejemplo del profesor no son resultados de este proyecto.

- [Hoja de ruta y decisiones metodológicas](docs/HOJA_DE_RUTA.md)
- [Fuentes y requisitos de los datos](docs/FUENTES.md)
- [Auditoría de acceso y calidad](docs/AUDITORIA_DATOS.md)
- [Consigna del profesor](https://claude.ai/artifact/7PDjxhAxnnJV2K24rVKWT6)
- [Material de la sesión 07: raster](https://github.com/d2cml-ai/Data-Science-Python/tree/main/sessions/07-raster)

## Producto previsto

1. Panorama de detecciones recientes y condiciones meteorológicas en sus ubicaciones, resumido por departamento.
2. Cruce agrícola con WorldCover 2021: hectáreas y fracción de cultivo cartografiado cerca de las detecciones agrupadas, con las otras coberturas como contexto.
3. Contexto oficial de El Niño; la comparación histórica homogénea de temperatura queda como extensión.
4. Informe web público con mapa interactivo, filtros, tres hallazgos cuantificados, fuentes y limitaciones.

La extensión sobre condiciones favorables para nuevos incendios se incorporará después de completar el núcleo. No se presentarán probabilidades de ignición ni predicciones de hectáreas futuras sin un modelo validado.

## Qué demostrará el análisis raster

Inspección de bandas, clases, resolución y coordenadas; tratamiento de NoData; recorte de WorldCover; conteos por categoría y estadísticas zonales en entornos definidos en metros. Las operaciones se explicarán en un notebook que pueda usarse en la presentación. No se requiere dNBR ni medir superficie quemada para este reto.

## Alcance de las conclusiones

Un foco de calor es una detección, no un incendio individual ni una medida de superficie quemada. Las agrupaciones serán aproximaciones explícitas. La prioridad meteorológica será exploratoria y no una alerta oficial. Una captura de datos con fecha de corte no se describirá como un monitor permanentemente actualizado.

La clase agrícola de WorldCover representa principalmente cultivos anuales y puede omitir cultivos leñosos permanentes. La proximidad del fuego no prueba daño, aumento térmico en las parcelas ni pérdida de producción. Las hectáreas serán superficie cartografiada cercana, no cultivo perdido. Se evaluará el mapa agrícola oficial de MIDAGRI como complemento cuando su acceso y definición estén verificados.

Antes de publicar resultados, este README se completará con las fechas efectivas de cada fuente, el método ejecutado, al menos un mapa y tres hallazgos con números, conforme a la rúbrica.

## Auditoría inicial

El script `scripts/auditar_fuentes.py` comprueba acceso, fechas, campos, geometrías y una muestra de meteorología y raster. Guarda originales en `data/raw/` y un inventario en `docs/AUDITORIA_DATOS.json`. No calcula prioridades ni predicciones. Ejecutarlo dentro de un entorno aislado con las dependencias de `requirements-auditoria.txt`.
