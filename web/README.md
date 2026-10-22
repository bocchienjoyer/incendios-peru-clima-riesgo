# Fuego y agricultura · Perú

Dashboard público estático del análisis académico de detecciones recientes, agricultura y meteorología. Sitio en español con mapa nacional, filtros, tabla departamental, pronóstico diario y escena 3D real de Tiquillaca (provincia de Puno).

El análisis reproducible y las decisiones metodológicas están en https://github.com/bocchienjoyer/incendios-peru-clima-riesgo.

## Ejecutar localmente

Servir `dist/` con cualquier servidor HTTP estático; por ejemplo `python -m http.server 8080 --directory dist`. Abrir http://localhost:8080. No se requiere compilación ni claves.

Las dependencias Leaflet 1.9.4 y Three.js 0.180.0 se distribuyen en `dist/vendor/` junto a sus licencias. Solo el fondo OpenStreetMap consulta un servicio externo; los datos, imagen y relieve del caso son archivos locales. OSM requiere conexión y está sujeto a su política de uso.

## Datos

Captura de detecciones del 21/10/2026, 20:25 Lima; pronóstico del 22 al 28/10/2026. No se actualiza automáticamente. Los escenarios son exploratorios y no equivalen a alertas oficiales. La escena muestra relieve real con exageración vertical 1,3, imagen Sentinel-2 del 17/10/2026 y contornos agrícolas MIDAGRI 2024, no daños.

Los activos se generan con `scripts/preparar_dashboard.py` en el repositorio del análisis. Las tablas originales no se recalculan en el navegador.
