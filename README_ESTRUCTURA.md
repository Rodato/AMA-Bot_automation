# 📁 Estructura del Proyecto AMA Bot

## 🎯 Archivos Principales (Sistema de Producción)

### Scripts Core
- **`ama_bot_controller.py`** - 🤖 Controlador principal de envíos automatizados
- **`csvNumbersGenerator.py`** - 📊 Generador de CSV de control desde XLSX
- **`agregar_numeros_nuevos.py`** - ➕ Actualizar CSV manteniendo progreso existente
- **`monitor_ubicaciones.py`** - 📈 Sistema de monitoreo y reportes por ubicación

### Datos y Configuración
- **`botNumbers_test.xlsx`** - 📋 Archivo fuente con usuarios y ubicaciones
- **`requirements.txt`** - 📦 Dependencias del proyecto

### Documentación
- **`CLAUDE.md`** - 📚 Documentación principal del sistema
- **`ARCHITECTURE.md`** - 🏗️ Arquitectura técnica
- **`DEVELOPMENT_LOG.md`** - 📝 Log de desarrollo

## 📂 Carpetas Organizadas

### `scripts_legacy/` - Versiones Anteriores
Scripts que fueron reemplazados por versiones mejoradas:
- `botpressSender.py` - Versión anterior del controlador
- `sender_&_controltables.py` - Script legacy combinado

### `utilities/` - Herramientas de Soporte  
Scripts auxiliares para mantenimiento y operaciones especiales:
- `get_table_rows.py` - Consultar filas de tablas Botpress
- `list_botpress_tables.py` - Listar todas las tablas disponibles
- `sync_control_with_botpress.py` - Sincronización manual de datos
- `ama_bot_github_runner.py` - Runner para GitHub Actions

### `testing/` - Scripts de Prueba
Herramientas para testing y debugging:
- `test_webhook.py` - Probar webhook de Botpress
- `botPressCURL.py` - Pruebas con cURL

### `scripts_especificos/` - Scripts Puntuales
Scripts para casos específicos o tareas puntuales:
- `reset_all_except_one.py` - Reset específico excluyendo un usuario
- `reset_and_send.py` - Reset y reenvío para usuarios específicos

## 🚀 Comandos Principales

```bash
# Sistema de producción
python3 csvNumbersGenerator.py              # Generar CSV inicial
python3 agregar_numeros_nuevos.py          # Actualizar con nuevos números
python3 ama_bot_controller.py               # Ejecutar envíos
python3 monitor_ubicaciones.py              # Generar reportes

# Utilidades de soporte
python3 utilities/get_table_rows.py         # Consultar datos Botpress
python3 utilities/sync_control_with_botpress.py  # Sincronización manual

# Testing
python3 testing/test_webhook.py             # Probar conexión webhook
```

## 📋 Flujo de Trabajo Recomendado

1. **Actualizar usuarios**: Editar `botNumbers_test.xlsx`
2. **Actualizar CSV**: `python3 agregar_numeros_nuevos.py`
3. **Ejecutar envíos**: `python3 ama_bot_controller.py`  
4. **Monitorear**: `python3 monitor_ubicaciones.py`

## 🔧 Mantenimiento

- **Archivos esenciales**: Solo los del directorio raíz
- **Backups**: Se generan automáticamente en `control_envios.csv.backup_*`
- **Logs**: Consultar salida de consola de cada script
- **Troubleshooting**: Usar scripts en `utilities/` y `testing/`

---
**Nota**: Los archivos en las subcarpetas son para casos especiales, desarrollo o mantenimiento. El flujo normal solo requiere los scripts del directorio principal.