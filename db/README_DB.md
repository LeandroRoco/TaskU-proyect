# TaskU - Base de Datos (MySQL 8.0+)

Este paquete crea la base de datos **tasku** con todas las tablas, claves foráneas,
índices, triggers para normalizar correos, una vista de eventos próximos y un procedimiento para crear eventos.

## Archivos

- `00_init_schema.sql` → Crea la BD y el esquema completo.
- `02_demo_seeds.sql` → Inserta datos de ejemplo (asignaturas y usuarios demo).

> Nota: No hay `01_migration.sql` porque el esquema ya integra las mejoras.
> Si ya tenías tablas, respalda y usa ALTERs equivalentes.

## Requisitos
- MySQL **8.0+** (probado con 8.0.x)
- Charset `utf8mb4`

## Cómo ejecutar (CLI)
```bash
mysql -u root -p < 00_init_schema.sql
mysql -u root -p < 02_demo_seeds.sql
```

## Cómo ejecutar (Docker)
```yaml
# docker-compose.yml (ejemplo)
services:
  mysql:
    image: mysql:8.0
    container_name: tasku-mysql
    environment:
      - MYSQL_ROOT_PASSWORD=secret
      - MYSQL_DATABASE=tasku
    ports:
      - "3306:3306"
    volumes:
      - ./mysql-data:/var/lib/mysql
    command: ["--character-set-server=utf8mb4", "--collation-server=utf8mb4_unicode_ci"]
```
Luego:
```bash
docker compose up -d
mysql -h 127.0.0.1 -P 3306 -u root -p < 00_init_schema.sql
mysql -h 127.0.0.1 -P 3306 -u root -p < 02_demo_seeds.sql
```

## Contraseñas (bcrypt)
En `02_demo_seeds.sql` reemplaza `REEMPLAZAR_CON_BCRYPT` por un hash **bcrypt** real.
Ejemplos de cómo generarlo:

**Node.js**
```js
import bcrypt from 'bcrypt';
console.log(await bcrypt.hash('Demo1234!', 12));
```

**Python**
```py
import bcrypt
bcrypt.hashpw(b'Demo1234!', bcrypt.gensalt(rounds=12)).decode()
```

## Tablas y relaciones
- `usuario` (con `rol` y `email_lc` generado + índice único)
- `asignatura`
- `usuario_has_asignatura` (N:M)
- `evento` (FK a `usuario` CASCADE, a `asignatura` SET NULL)
- `notificacion` (FK a `evento` CASCADE)
- `configuracion` (1:1 con `usuario` CASCADE)

## Extras
- **Triggers**: normalizan `email` a minúsculas en INSERT/UPDATE.
- **Vista**: `vw_eventos_proximos` (tareas pendientes por vencer).
- **SP**: `sp_crear_evento` (inserción consistente de eventos).

---

Cualquier ajuste que quieras (multi-rol con tabla `rol`, políticas de borrado, etc.), me dices y genero un script incremental.
