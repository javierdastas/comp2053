-- Ejecutar UNA sola variante en una base nueva. No borra bases existentes.
-- MySQL 8.4 o MariaDB 10.11. Datos completamente ficticios.
SET NAMES utf8mb4;
CREATE DATABASE fullstack_tutorias
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE fullstack_tutorias;

CREATE TABLE personas (
  id INT NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(80) NOT NULL,
  email VARCHAR(120) NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_persona_email UNIQUE (email)
) ENGINE=InnoDB;

CREATE TABLE recursos (
  id INT NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(80) NOT NULL,
  categoria VARCHAR(60) NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_recurso_nombre UNIQUE (nombre)
) ENGINE=InnoDB;

CREATE TABLE reservas (
  id INT NOT NULL AUTO_INCREMENT,
  persona_id INT NOT NULL,
  recurso_id INT NOT NULL,
  inicio DATETIME NOT NULL,
  motivo VARCHAR(200) NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT fk_reserva_persona FOREIGN KEY (persona_id) REFERENCES personas(id),
  CONSTRAINT fk_reserva_recurso FOREIGN KEY (recurso_id) REFERENCES recursos(id),
  CONSTRAINT uq_recurso_inicio UNIQUE (recurso_id, inicio),
  CONSTRAINT uq_persona_inicio UNIQUE (persona_id, inicio)
) ENGINE=InnoDB;

INSERT INTO personas (nombre, email) VALUES
  ('Estudiante Uno', 'uno@example.org'),
  ('Estudiante Dos', 'dos@example.org');

INSERT INTO recursos (nombre, categoria) VALUES
  ('Alex Rivera', 'Programación Python'),
  ('Sam Torres', 'Bases de datos'),
  ('Dani Cruz', 'Matemáticas');
