
-- create_tasku_schema.sql
-- Esquema base (limpio) para TaskU - MySQL 8.0+ (XAMPP compatible)
-- Ejecuta este archivo en phpMyAdmin (Importar) o por CLI.

-- 1) Crear BD
CREATE DATABASE IF NOT EXISTS tasku
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE tasku;

SET NAMES utf8mb4;
SET @OLD_SQL_MODE := @@SQL_MODE;
SET SQL_MODE = 'STRICT_ALL_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- 2) Tablas

CREATE TABLE IF NOT EXISTS usuario (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  email VARCHAR(100) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  rol ENUM('alumno','profesor','admin') NOT NULL DEFAULT 'alumno',
  activo TINYINT(1) NOT NULL DEFAULT 1,
  fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ultimo_acceso DATETIME NULL,
  email_lc VARCHAR(100) GENERATED ALWAYS AS (LOWER(email)) STORED,
  UNIQUE KEY ux_usuario_email_lc (email_lc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS asignatura (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  color VARCHAR(7) NULL,
  icono VARCHAR(50) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS usuario_asignatura (
  usuario_id INT NOT NULL,
  asignatura_id INT NOT NULL,
  PRIMARY KEY (usuario_id, asignatura_id),
  KEY idx_u_a_u (usuario_id),
  KEY idx_u_a_a (asignatura_id),
  CONSTRAINT fk_u_a_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(id)
    ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_u_a_asignatura FOREIGN KEY (asignatura_id) REFERENCES asignatura(id)
    ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS evento (
  id INT AUTO_INCREMENT PRIMARY KEY,
  titulo VARCHAR(255) NOT NULL,
  descripcion TEXT NULL,
  fecha_limite DATETIME NULL,
  prioridad ENUM('baja','media','alta') NOT NULL DEFAULT 'media',
  estado ENUM('pendiente','completada') NOT NULL DEFAULT 'pendiente',
  tipo ENUM('tarea','evaluacion','evento') NOT NULL,
  profesor VARCHAR(100) NULL,
  fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  usuario_id INT NOT NULL,
  asignatura_id INT NULL,
  KEY idx_evento_usuario (usuario_id),
  KEY idx_evento_asignatura (asignatura_id),
  KEY idx_evento_fecha (fecha_limite),
  CONSTRAINT fk_evento_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(id)
    ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_evento_asignatura FOREIGN KEY (asignatura_id) REFERENCES asignatura(id)
    ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS notificacion (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tipo ENUM('recordatorio','aviso','otro') NOT NULL,
  mensaje TEXT NULL,
  fecha_programada DATETIME NULL,
  fecha_enviada DATETIME NULL,
  leida TINYINT(1) NOT NULL DEFAULT 0,
  evento_id INT NOT NULL,
  KEY idx_notif_evento (evento_id),
  CONSTRAINT fk_notif_evento FOREIGN KEY (evento_id) REFERENCES evento(id)
    ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS configuracion (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tema ENUM('claro','oscuro') NOT NULL DEFAULT 'claro',
  idioma ENUM('es','en') NOT NULL DEFAULT 'es',
  notificaciones_activas TINYINT(1) NOT NULL DEFAULT 1,
  horario_silencioso_inicio TIME NULL,
  horario_silencioso_fin TIME NULL,
  usuario_id INT NOT NULL UNIQUE,
  CONSTRAINT fk_conf_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(id)
    ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3) Triggers (normalizar email a minúsculas)
DROP TRIGGER IF EXISTS trg_usuario_bi_email_lower;
DELIMITER //
CREATE TRIGGER trg_usuario_bi_email_lower
BEFORE INSERT ON usuario
FOR EACH ROW
BEGIN
  SET NEW.email = LOWER(NEW.email);
END//
DELIMITER ;

DROP TRIGGER IF EXISTS trg_usuario_bu_email_lower;
DELIMITER //
CREATE TRIGGER trg_usuario_bu_email_lower
BEFORE UPDATE ON usuario
FOR EACH ROW
BEGIN
  IF NEW.email IS NOT NULL THEN
    SET NEW.email = LOWER(NEW.email);
  END IF;
END//
DELIMITER ;

-- 4) Vista útil
DROP VIEW IF EXISTS vw_eventos_proximos;
CREATE VIEW vw_eventos_proximos AS
SELECT e.*
FROM evento e
WHERE e.estado = 'pendiente'
  AND e.fecha_limite IS NOT NULL
  AND e.fecha_limite >= NOW()
ORDER BY e.fecha_limite ASC;

-- 5) Datos de ejemplo mínimos (opcional)
-- Genera primero un hash con bcrypt (PHP/Node/Python) y reemplaza el texto:
-- UPDATE usuario SET password_hash='REEMPLAZAR_CON_BCRYPT' WHERE email='alumno@demo.cl';

INSERT INTO usuario (nombre, email, password_hash, rol, activo)
VALUES ('Admin', 'admin@demo.cl', '$2y$12$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'admin', 1)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

INSERT INTO usuario (nombre, email, password_hash, rol, activo)
VALUES ('Alumno Demo', 'alumno@demo.cl', '$2y$12$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'alumno', 1)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

INSERT INTO asignatura (nombre, color, icono) VALUES
('Cálculo', '#0ea5e9', 'calculator'),
('Oceanografía', '#22c55e', 'waves')
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);
