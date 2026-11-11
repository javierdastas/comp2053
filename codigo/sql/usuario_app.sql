-- Ejecutar con cuenta administradora local después de crear la base.
-- Copiar como usuario_app.local.sql y cambiar la clave solo en la copia. Para equipos/tutorias cambiar fullstack_salas en GRANT.
-- Si esta cuenta ya existe, usa la cuenta asignada por tu docente.
CREATE USER 'fullstack_app'@'localhost' IDENTIFIED BY 'CAMBIAR_ESTA_CLAVE';
GRANT SELECT, INSERT, DELETE ON fullstack_salas.* TO 'fullstack_app'@'localhost';
-- No hacen falta permisos globales ni FLUSH PRIVILEGES.
