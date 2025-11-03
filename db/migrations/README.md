# Database Migrations

Este directorio contiene los scripts SQL para crear y modificar la estructura de la base de datos.

## Orden de Ejecución

### 1. `01_create_schema.sql`
- Crea la estructura inicial de la base de datos
- Tabla `users` con información básica
- Tablas `session_1` a `session_6` para progreso
- Funciones, triggers y vistas

### 2. `02_add_sessions_7_8_9.sql` 
- Agrega sesiones adicionales para colegios
- Tablas `session_7`, `session_8`, `session_9`
- Triggers correspondientes

## Cómo Ejecutar

1. Ve a Supabase Dashboard → SQL Editor
2. Copia y pega el contenido de cada archivo en orden
3. Ejecuta con el botón "RUN"

## Estructura Final

### Tablas Principales
- `users` - Datos básicos de usuarios
- `session_1` a `session_9` - Progreso por sesión y día

### Vistas
- `city_stats` - Estadísticas por ciudad
- `location_progress` - Progreso por ubicación

### Funciones
- `update_updated_at_column()` - Actualiza timestamps automáticamente