# Dashboard público

**https://peru-fuego-agricultura.fancyperch2.chatgpt.site**

La pregunta se conserva: ¿Qué zonas agrícolas cercanas a detecciones recientes de fuego coinciden con condiciones meteorológicas favorables para su propagación durante los próximos siete días, y en qué departamentos se concentran?

## Implementación entregada

La revisión de claridad presenta primero la pregunta, después el caso localizado en Tiquillaca (provincia de Puno) y su significado, luego el comparador nacional y el visor 3D. Se conserva al final una metodología ampliada con fechas por fuente, operaciones raster, criterios, cinco registros horarios y procedencia de la ubicación. No se recalculó el análisis nacional.

El caso se comunica como dos detecciones a unos 610 m de agricultura cartografiada, con 5,08 ha dentro de la unión de entornos de 1 km. Las cinco horas del escenario principal se explican con fechas y valores; no representan duración del incendio. Ver [detalle trazable del caso](TIQUILLACA_CASO.json).

El visor distingue imagen óptica, cobertura del suelo 2021 y altitud en metros, con texto y leyendas que cambian según la selección. La zona gris de cobertura queda fuera del recorte; los colores no representan calor ni riesgo. Se eliminó el bloque raster repetido y se trasladó su contenido a la metodología.

- Narrativa nacional: 131 grupos recientes, 106 con agricultura cercana y 12.910,68 ha únicas; una coincidencia comparable en Puno.
- Mapa con filtro de departamento, selección de grupo, contornos agrícolas y anillos de 1 km por detección. Los puntos nacionales representan agrupaciones; al acercarse se ven las detecciones del grupo seleccionado.
- Pronóstico diario: horas base o alternativas, temperatura, humedad, viento y lluvia diaria. La clasificación usa lluvia acumulada previa de 24 h, distinta de la lluvia diaria de contexto.
- Tabla de 25 departamentos ordenable, selección que filtra el mapa y descargas CSV.
- Escena 3D real de Puno G1184: elevación Terrain Tiles, imagen Sentinel-2 del 17/10/2026, WorldCover 2021 con vecino más cercano, contornos MIDAGRI y dos detecciones. Giro, zoom, texturas, capas, restablecer y vista desde arriba.
- Método, fuentes, decisiones raster y límites. Sin cuentas ni claves privadas para visitar.

El 3D se limita a Puno. No incluye animación de propagación, dNBR, infrarrojo ni superficie continua de temperatura. La imagen óptica es anterior a las detecciones. El relieve se exagera ×1,3 y no interviene en el escenario meteorológico.

## Código y reproducción

Fuentes en web/dist/: index.html, style.css y app.js. Con el entorno de requirements-analisis.txt y los originales preparados por los scripts del análisis:

```powershell
python scripts/preparar_dashboard.py web
python -m http.server 8080 --directory web/dist
```

El exportador conserva los resultados nacionales y no vuelve a consultar pronósticos. Descarga cuatro teselas de elevación y las versiones fijadas Leaflet 1.9.4 y Three.js 0.180.0, con sus licencias. Los activos generados se excluyen de este Git; la versión completa publicada está guardada en el repositorio fuente de Sites.

Los datos, recortes e imágenes se sirven desde el mismo sitio. Solo el fondo OpenStreetMap usa un servicio externo, con atribución visible. Sin WebGL se ofrece una imagen estática de contexto.

## Publicación y comprobaciones

Sites, audiencia pública. Proyecto appgprj_6ad974541e988191aec7dcc405017c32; versión 1, commit de fuente 0da4054e3b1789e18d436f7ad1602836afc3329e. Publicación confirmada como succeeded y URL abierta en navegador.

Comprobado: sintaxis JavaScript; carga de datos y 25 filas; selección de Puno; escenario alternativo de 5 a 15 horas; estado vacío de Callao; escena 3D real y cambio a WorldCover. Diseño con reglas para pantallas pequeñas; sin prueba visual específica en teléfono físico.

Captura fija: corte 21/10/2026, 20:25 Lima; pronóstico 22–28/10. Cuatro observaciones pendientes quedan fuera de las coincidencias principales. Los contornos se simplificaron solo para dibujar; las áreas conservan los cálculos originales.
