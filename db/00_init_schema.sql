-- 00_init_schema.sql
-- Base de datos para TaskU (INACAP) - MySQL 8.0+
-- Crea esquema completo con roles, índices, FKs, triggers, vista y SP.

-- Ajusta el nombre si prefieres otro
CREATE DATABASE IF NOT EXISTS tasku
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE tasku;

SET NAMES utf8mb4;
SET @OLD_SQL_MODE := @@SQL_MODE;
SET SQL_MODE = 'STRICT_ALL_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- =======================
-- Tablas principales
-- =======================

CREATE TABLE IF NOT EXISTS usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255),
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso DATETIME,
    tema_preferido ENUM('claro','oscuro') NOT NULL DEFAULT 'claro',
    activo TINYINT(1) NOT NULL DEFAULT 1,
    rol ENUM('alumno','profesor','admin') NOT NULL DEFAULT 'alumno',
    token_recuperacion VARCHAR(255),
    fecha_expiracion_token DATETIME,
    email_lc VARCHAR(100) GENERATED ALWAYS AS (LOWER(email)) STORED,
    UNIQUE KEY ux_usuario_email_lc (email_lc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS asignatura (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    color VARCHAR(7),
    icono VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS usuario_has_asignatura (
    usuario_id INT NOT NULL,
    asignatura_id INT NOT NULL,
    PRIMARY KEY (usuario_id, asignatura_id),
    KEY idx_uha_usuario (usuario_id),
    KEY idx_uha_asignatura (asignatura_id),
    CONSTRAINT fk_uha_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuario(id) ON DELETE CASCADE ON UPDATE RESTRICT,
    CONSTRAINT fk_uha_asignatura FOREIGN KEY (asignatura_id)
        REFERENCES asignatura(id) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS evento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_limite DATETIME,
    prioridad ENUM('baja','media','alta') NOT NULL DEFAULT 'media',
    estado ENUM('pendiente','completada') NOT NULL DEFAULT 'pendiente',
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    asignatura_id INT NULL,
    usuario_id INT NOT NULL,
    tipo ENUM('tarea','evaluacion','evento') NOT NULL,
    profesor VARCHAR(100),
    KEY idx_evento_usuario (usuario_id),
    KEY idx_evento_asignatura (asignatura_id),
    KEY idx_evento_fecha (fecha_limite),
    CONSTRAINT fk_evento_asignatura FOREIGN KEY (asignatura_id)
        REFERENCES asignatura(id) ON DELETE SET NULL ON UPDATE RESTRICT,
    CONSTRAINT fk_evento_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuario(id) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS notificacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo ENUM('recordatorio','aviso','otro') NOT NULL,
    mensaje TEXT,
    fecha_programada DATETIME,
    fecha_enviada DATETIME,
    leida TINYINT(1) NOT NULL DEFAULT 0,
    evento_id INT,
    KEY idx_notif_evento (evento_id),
    CONSTRAINT fk_notif_evento FOREIGN KEY (evento_id)
        REFERENCES evento(id) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS configuracion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tema ENUM('claro','oscuro') NOT NULL DEFAULT 'claro',
    idioma ENUM('es','en') NOT NULL DEFAULT 'es',
    notificaciones_activas TINYINT(1) NOT NULL DEFAULT 1,
    horario_silencioso_inicio TIME,
    horario_silencioso_fin TIME,
    id_usuario INT UNIQUE,
    CONSTRAINT fk_config_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario(id) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =======================
-- Triggers
-- =======================

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

-- =======================
-- Views y SPs
-- =======================

DROP VIEW IF EXISTS vw_eventos_proximos;
CREATE VIEW vw_eventos_proximos AS
SELECT
  e.id,
  e.titulo,
  e.descripcion,
  e.fecha_limite,
  e.prioridad,
  e.estado,
  e.tipo,
  e.profesor,
  e.usuario_id,
  e.asignatura_id
FROM evento e
WHERE e.estado = 'pendiente'
  AND e.fecha_limite IS NOT NULL
  AND e.fecha_limite >= NOW()
ORDER BY e.fecha_limite ASC;

DROP PROCEDURE IF EXISTS sp_crear_evento;
DELIMITER //
CREATE PROCEDURE sp_crear_evento(
  IN p_usuario_id INT,
  IN p_asignatura_id INT,
  IN p_titulo VARCHAR(255),
  IN p_descripcion TEXT,
  IN p_fecha_limite DATETIME,
  IN p_prioridad ENUM('baja','media','alta'),
  IN p_tipo ENUM('tarea','evaluacion','evento'),
  IN p_profesor VARCHAR(100)
)
BEGIN
  INSERT INTO evento
    (titulo, descripcion, fecha_limite, prioridad, estado, asignatura_id, usuario_id, tipo, profesor)
  VALUES
    (p_titulo, p_descripcion, p_fecha_limite, COALESCE(p_prioridad,'media'), 'pendiente',
     p_asignatura_id, p_usuario_id, p_tipo, p_profesor);
  SELECT LAST_INSERT_ID() AS nuevo_evento_id;
END//
DELIMITER ;

SET SQL_MODE := @OLD_SQL_MODE;
