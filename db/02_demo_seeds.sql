-- 02_demo_seeds.sql
-- Datos de ejemplo (usuario admin y alumno, y asignaturas).
-- IMPORTANTE: Reemplaza REEMPLAZAR_CON_BCRYPT por un hash real (bcrypt cost >= 12).

USE tasku;

-- Asignaturas base (ejemplo)
INSERT INTO asignatura (nombre, color, icono) VALUES
('Cálculo Diferencial', '#0ea5e9', 'calculator'),
('Oceanografía', '#22c55e', 'waves'),
('Seguridad de la Información', '#ef4444', 'shield')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

-- Usuarios demo
INSERT INTO usuario (nombre, email, password_hash, tema_preferido, activo, rol)
VALUES
('Admin', 'admin@demo.cl', 'REEMPLAZAR_CON_BCRYPT', 'oscuro', 1, 'admin'),
('Alumno Demo', 'alumno@demo.cl', 'REEMPLAZAR_CON_BCRYPT', 'claro', 1, 'alumno')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre), rol = VALUES(rol);

-- Relación usuario-asignatura (Alumno Demo con todas)
INSERT IGNORE INTO usuario_has_asignatura (usuario_id, asignatura_id)
SELECT u.id, a.id
FROM usuario u CROSS JOIN asignatura a
WHERE u.email_lc = 'alumno@demo.cl';
