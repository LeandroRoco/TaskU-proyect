-- TaskU INACAP - Base de datos segura con encriptación

CREATE DATABASE IF NOT EXISTS tasku;
USE tasku;

-- Tabla de usuarios con password_hash encriptado
CREATE TABLE IF NOT EXISTS usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL, -- bcrypt hash
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso DATETIME,
    activo TINYINT(1) DEFAULT 1,
    rol ENUM('estudiante', 'profesor', 'administrador') DEFAULT 'estudiante'
);

-- Tabla de asignaturas INACAP predefinidas
CREATE TABLE IF NOT EXISTS asignatura (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo VARCHAR(20) UNIQUE,
    color VARCHAR(7) DEFAULT '#003366',
    icono VARCHAR(50)
);

-- Tabla intermedia para asignaturas del usuario
CREATE TABLE IF NOT EXISTS usuario_asignatura (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    asignatura_id INT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (asignatura_id) REFERENCES asignatura(id) ON DELETE CASCADE,
    UNIQUE KEY unique_usuario_asignatura (usuario_id, asignatura_id)
);

-- Tabla de eventos/tareas
CREATE TABLE IF NOT EXISTS evento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_limite DATETIME NOT NULL,
    prioridad ENUM('baja','media','alta') DEFAULT 'media',
    estado ENUM('pendiente','completada','atrasada') DEFAULT 'pendiente',
    tipo ENUM('tarea','examen','proyecto','presentacion','laboratorio') NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT NOT NULL,
    asignatura_id INT,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (asignatura_id) REFERENCES asignatura(id) ON DELETE SET NULL
);

-- Tabla de notificaciones
CREATE TABLE IF NOT EXISTS notificacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo ENUM('recordatorio','urgencia','recordatorio_24h') NOT NULL,
    mensaje TEXT NOT NULL,
    fecha_programada DATETIME NOT NULL,
    leida TINYINT(1) DEFAULT 0,
    evento_id INT NOT NULL,
    usuario_id INT NOT NULL,
    FOREIGN KEY (evento_id) REFERENCES evento(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
);

CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('estudiante', 'profesor', 'admin') DEFAULT 'estudiante',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP NULL,
    activo TINYINT DEFAULT 1
);
USE tasku;

-- Agregar columna 'rol' si no existe
ALTER TABLE usuario 
ADD COLUMN IF NOT EXISTS rol ENUM('estudiante', 'profesor', 'admin') DEFAULT 'estudiante' AFTER password_hash;

-- Agregar columna 'ultimo_acceso' si no existe
ALTER TABLE usuario 
ADD COLUMN IF NOT EXISTS ultimo_acceso TIMESTAMP NULL AFTER fecha_registro;

-- Agregar columna 'activo' si no existe
ALTER TABLE usuario 
ADD COLUMN IF NOT EXISTS activo TINYINT DEFAULT 1 AFTER ultimo_acceso;

-- Verificar la estructura final
DESCRIBE usuario;

-- Insertar asignaturas INACAP comunes
INSERT INTO asignatura (nombre, codigo, color) VALUES
('Integración de Proyecto', 'INF-401', '#003366'),
('Base de Datos', 'INF-301', '#28a745'),
('Desarrollo Móvil', 'INF-302', '#FF6600'),
('Seguridad de la Información', 'INF-303', '#dc3545'),
('Redes de Computadores', 'INF-304', '#6f42c1'),
('Algoritmos y Estructuras', 'INF-305', '#ffc107');

-- Índices para mejorar performance
CREATE INDEX idx_evento_usuario ON evento(usuario_id);
CREATE INDEX idx_evento_fecha ON evento(fecha_limite);
CREATE INDEX idx_notificacion_usuario ON notificacion(usuario_id, leida);