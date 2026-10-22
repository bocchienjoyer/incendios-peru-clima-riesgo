# Alcance del dashboard público

La pregunta se conserva exactamente: **¿Qué zonas agrícolas cercanas a detecciones recientes de fuego coinciden con condiciones meteorológicas favorables para su propagación durante los próximos siete días, y en qué departamentos se concentran?**

## Versión base

Un solo mapa central con selector de departamento y selección de agrupación. Cambiar la selección actualizará el encuadre, la tabla y el detalle meteorológico. La narrativa y tres hallazgos tendrán más peso que la cantidad de controles.

Capas previstas:

- Imagen satelital óptica de referencia, con fecha/proveedor y atribución visibles; no confundirla con la fecha de las detecciones.
- Detecciones VIIRS, diferenciadas por antigüedad y, si aporta claridad, potencia radiativa FRP. No son una superficie continua de temperatura.
- Superficie agrícola MIDAGRI 2024 recortada en las zonas estudiadas.
- Cobertura WorldCover 2021 como capa alternativa, para entender el paso de raster a tabla y las diferencias con MIDAGRI.

Si se muestra temperatura meteorológica, tendrá su propia escala y resolución de modelo. No crear una capa de temperatura del suelo interpolando focos VIIRS. Una imagen térmica continua requeriría otro producto, con fecha, nubes y resolución propias; queda como mejora opcional y no es necesaria para responder la pregunta.

## Relieve 3D

Probar una vista con terreno e inclinación, limitada a una zona seleccionada, usando capacidades existentes como MapLibre y un modelo de elevación público. El relieve representa altura del terreno, no intensidad ni volumen del fuego. Mantener botón para volver a 2D.

Se incorporará solo si funciona en un navegador corriente y permite compartir el enlace sin cuentas, claves privadas o un servidor de procesamiento. Si añade lentitud o complejidad desproporcionada, entregar el mapa 2D. La integración completa de 3D todavía no se ha implementado ni verificado.

## Límites prácticos

- Procesamiento en Python; navegador recibe tablas y recortes pequeños.
- Una sola descarga nacional de MIDAGRI; no cargar 709 MB de geometrías originales en la web.
- Consultas raster solo en áreas necesarias y datos meteorológicos reutilizados por celda cuando corresponda.
- No prometer actualización automática; la captura tendrá fecha y hora.
- Verificar permisos/atribución de la imagen base y del terreno antes de publicación. Las teselas cartográficas pueden requerir acceso a Internet aunque los resultados estén precalculados.
- No añadir población, pérdida de rendimiento, humedad fisiológica, simulación de propagación ni animación temporal a la primera versión.

## Orden de implementación

Primero el análisis revisado y la tabla nacional; después mapa 2D con capas y selector; luego narrativa y publicación; finalmente prueba del relieve 3D si el costo sigue siendo razonable. No cambiar los criterios de prioridad para obtener un mapa más vistoso.
