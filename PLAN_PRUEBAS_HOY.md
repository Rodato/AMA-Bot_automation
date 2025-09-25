# 📋 Plan de Pruebas GitHub Actions - Hoy

## 🎯 Objetivo
Probar el sistema de envíos automatizados en GitHub Actions hoy y preparar para agregar números nuevos mañana.

## ✅ Estado Actual del Sistema

### 📊 Datos Disponibles
- **60 registros** en `control_envios.csv` 
- **2 usuarios únicos** (Colegio Maynas)
- **60 registros pendientes** (todos sin enviar aún)
- **Estructura con ubicaciones** implementada y funcionando

### 🤖 GitHub Actions Configurado

#### Workflow Principal: `ama-bot-scheduler.yml`
- **Horario**: Diario a las 5:00 PM Colombia (10:00 PM UTC)
- **Trigger manual**: Con opción de modo prueba
- **Funcionalidades**:
  - ✅ Ejecuta envíos con `utilities/ama_bot_github_runner.py`
  - ✅ Genera reporte de monitoreo
  - ✅ Commitea cambios automáticamente
  - ✅ Variables de entorno para APIs

#### Workflow Semanal: `weekly-monitoring.yml`
- **Horario**: Lunes 8:00 AM Colombia 
- **Función**: Reportes semanales detallados por ubicación

## 🧪 Plan de Pruebas para Hoy

### Paso 1: Ejecutar Prueba Manual
```bash
# En el repositorio, ir a Actions > AMA Bot Daily Scheduler
# Click "Run workflow" > Seleccionar "test_mode: true" > Run
```

### Paso 2: Verificar Ejecución
- ✅ Logs del workflow muestran progreso 
- ✅ Se actualizan registros en `control_envios.csv`
- ✅ Se genera reporte Excel `reporte_ubicaciones_*.xlsx`
- ✅ Commit automático con cambios

### Paso 3: Analizar Resultados
- Revisar cuántos mensajes se enviaron exitosamente
- Verificar estados de usuarios en CSV actualizado
- Revisar reporte Excel para monitoreo por ubicación

## 📋 Preparación para Mañana

### Plan para Agregar Números Nuevos
1. **Actualizar XLSX**: Agregar nuevos usuarios a `botNumbers_test.xlsx`
2. **Ejecutar actualización**: `python3 agregar_numeros_nuevos.py`
3. **Verificar**: Los nuevos usuarios empezarán en sesión 1, día 1
4. **GitHub Actions**: Continuará enviando automáticamente a las 5 PM

## 🔧 Variables de Entorno Requeridas en GitHub

Asegúrate de que estos secrets estén configurados:
- `WEBHOOK_URL` - URL del webhook Botpress
- `WEBHOOK_SECRET` - Secret del webhook
- `BOTPRESS_TOKEN` - Token de API Botpress
- `BOT_ID` - ID del bot
- `PROGRESS_TABLE_NAME` - Nombre de tabla de progreso

## 📊 Monitoreo Esperado

### Métricas Clave
- **Tasa de envío**: % de mensajes enviados exitosamente
- **Respuesta de usuarios**: Completados vs enviados
- **Por ubicación**: Colegio Maynas performance

### Reportes Generados
- **CSV actualizado**: Con nuevos estados y timestamps
- **Excel de monitoreo**: Análisis por ubicación y sesión
- **Logs detallados**: En output de GitHub Actions

## 🚀 Próximos Pasos

### Si las Pruebas de Hoy Son Exitosas:
1. ✅ Confirmar que los envíos funcionan
2. ➕ Agregar números nuevos mañana  
3. 📊 Monitorear resultados semanalmente
4. 🔄 Ajustar horarios si es necesario

### Si Hay Problemas:
1. 🔍 Revisar logs de GitHub Actions
2. 🧪 Probar localmente con `test_github_runner.py`
3. 🔧 Ajustar configuración según errores
4. 🔁 Re-ejecutar workflow manualmente

---
**Fecha**: 2025-09-25  
**Estado**: ✅ Listo para pruebas  
**Próxima revisión**: Después de ejecución de hoy