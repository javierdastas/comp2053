# Verificación del material de referencia

Preparado el 10 de noviembre de 2026.

- 23 pruebas automáticas del servidor aprobadas en SQLite temporal, con reloj fijo y claves foráneas activadas.
- Sintaxis JavaScript comprobada con `node --check`.
- Los tres scripts SQL se ejecutaron en bases nuevas de una instancia temporal MySQL 5.7.24 disponible en el entorno de autoría. Cada base creó exactamente tres tablas y sus semillas.
- En cada variante se comprobó la página inicial, creación concurrente del mismo bloque (una respuesta 201 y otra 409), persistencia de una sola fila, resumen y cancelación.
- En Chrome se comprobó el alta de una persona y una reserva desde los formularios, el bloqueo de su hora y el cambio del resumen a 1 de 27 bloques. La cancelación se verificó mediante la API.
- La guía propone MySQL 8.4 o MariaDB 10.11 o posterior para el laboratorio. No se ejecutó aquí una instancia de esas versiones; corresponde repetir la matriz de integración en el motor del curso. MySQL 5.7 no se recomienda como instalación nueva.
- Las pruebas del servidor no constituyen una auditoría completa de accesibilidad. La matriz pide comprobar teclado, foco, pantalla estrecha y zoom en el navegador del laboratorio.

Las verificaciones se refieren al código de referencia, no a futuras modificaciones de los equipos.
