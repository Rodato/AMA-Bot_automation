# 📋 AMA Bot Automation - Registro de Desarrollo

## 🎯 Objetivo del Proyecto
Sistema automatizado de mensajería WhatsApp integrado con Botpress para campañas de 6 sesiones (5 días cada una) con control de reenvíos y validación de prerrequisitos.

---

## 📅 Registro de Desarrollo - Septiembre 12, 2025

### ✅ **Fase 1: Análisis del código existente**
- **Archivos analizados:**
  - `botPressCURL.py` - Script básico de envíos
  - `botpressSender.py` - Controlador con menú
  - `sender_&_controltables.py` - Sistema avanzado con validaciones
  - `get_table_rows.py` - Consulta correcta a API de Botpress
  - `control_envios.csv` - Base de datos de control

### ✅ **Fase 2: Corrección de API de Botpress**
- **Problema identificado:** Método incorrecto para consultar tabla de progreso
- **Solución implementada:** 
  - URL correcta: `https://api.botpress.cloud/v1/tables/{TABLE_NAME}/rows/find`
  - Método: POST con payload `{"limit": 1000}`
  - Integrado desde `get_table_rows.py` al sistema principal

### ✅ **Fase 3: Sincronización de datos**
- **Problema:** CSV desactualizado con datos de Botpress
- **Solución:** Script `sync_control_with_botpress.py`
- **Resultado:** 1 usuario marcado como completado, datos sincronizados

### ✅ **Fase 4: GitHub Actions - Automatización**
- **Configuración realizada:**
  ```yaml
  # Workflow: .github/workflows/ama-bot-scheduler.yml
  # Ejecución: Diaria automática
  # Horario: 9:00 AM Colombia (14:00 UTC)
  ```
- **Script optimizado:** `ama_bot_github_runner.py`
- **GitHub Secrets configurados:**
  - `WEBHOOK_URL`
  - `WEBHOOK_SECRET` 
  - `BOTPRESS_TOKEN`
  - `BOT_ID`
  - `PROGRESS_TABLE_NAME`

### ✅ **Fase 5: Lógica de Reenvíos Consecutivos**
- **Requisito:** Máximo 2 reenvíos consecutivos fallidos por usuario
- **Implementación:**
  - Nueva columna: `reenvios_consecutivos_fallidos`
  - Nueva columna: `usuario_excluido`
  - Función: `manejar_reenvios_fallidos()`
  
- **Lógica de exclusión:**
  ```
  Usuario falla día X (intento 1) → Reenvío día X
  Si falla reenvío → Contador +1
  Si completa cualquier día → Reset contador a 0
  Si contador = 2 → Usuario excluido permanentemente
  ```

---

## 🔧 Problemas Identificados y Solucionados

### 1. **Error 403 en GitHub Actions**
- **Problema:** Permisos denegados para push
- **Solución:** Configurar "Read and write permissions" en Settings → Actions

### 2. **Mensajes no llegan a WhatsApp**
- **Problema:** Webhook responde 200 pero templates no llegan
- **Estado:** Problema de Botpress/WhatsApp (no del código)
- **Workaround:** Solo 1 de 3 números recibe mensajes correctamente

### 3. **Reenvíos no funcionaban**
- **Problema:** Solo consideraba registros con `enviado=0`
- **Solución:** Incluir registros con `enviado=1 AND completado=0 AND intentos_envio<2`

---

## 📊 Arquitectura Actual

### **Flujo de Ejecución:**
```
1. GitHub Actions (9 AM Colombia)
   ↓
2. Cargar CSV de control
   ↓
3. Consultar progreso en Botpress
   ↓
4. Sincronizar estados locales
   ↓
5. Filtrar registros pendientes/reenvíos
   ↓
6. Validar prerrequisitos por usuario
   ↓
7. Enviar mensajes via webhook
   ↓
8. Actualizar CSV con resultados
   ↓
9. Verificar reenvíos consecutivos fallidos
   ↓
10. Excluir usuarios si corresponde
   ↓
11. Commit cambios al repositorio
```

### **Validaciones Implementadas:**
- ✅ Usuario no excluido permanentemente
- ✅ Máximo 2 intentos por día
- ✅ No reenviar si ya completado
- ✅ Día anterior completado (excepto día 1)
- ✅ Solo sesión 1 implementada

### **Estructura del CSV:**
```csv
numero,sesion,day,enviado,fecha_envio,resultado,completado,intentos_envio,fecha_completado,ultimo_estado_botpress,reenvios_consecutivos_fallidos,usuario_excluido
```

---

## 🧪 Estado de Pruebas

### **Números de Prueba (Colombia +57):**
- `573156617659` ✅ Recibe mensajes
- `573159267303` ❌ No recibe (problema Botpress)
- `573155503266` ❌ No recibe (problema Botpress)  
- `573168124099` ✅ Usuario avanzado (días 1,2,3 enviados)

### **Pruebas Realizadas:**
- ✅ Envío manual exitoso
- ✅ GitHub Actions funcional
- ✅ Sincronización con Botpress
- ✅ Validación de prerrequisitos
- ⏳ Lógica de reenvíos (pendiente prueba)

---

## 📋 Próximos Pasos

### **Fin de Semana (Pruebas):**
- **Sábado 9 AM:** Prueba automática de reenvíos
- **Domingo 9 AM:** Segunda prueba de validación

### **Lunes (Producción):**
- [ ] Cargar ~300 números reales de Perú (+51)
- [ ] Cambiar configuración de Colombia a Perú
- [ ] Iniciar campaña real de 6 semanas
- [ ] Implementar sesiones 2-6 si es necesario

---

## 🔐 Configuración de Seguridad

### **Variables de Entorno (GitHub Secrets):**
- Todas las credenciales protegidas
- No hay keys hardcodeados en el código
- Archivo `.env.example` como plantilla

### **Archivos Sensibles:**
- ✅ `.gitignore` configurado
- ✅ `.env` excluido del repositorio
- ✅ Credenciales en GitHub Secrets únicamente

---

## 📈 Métricas y Monitoreo

### **GitHub Actions:**
- Logs detallados de cada ejecución
- Reporte de envíos exitosos/fallidos/omitidos
- Historial completo en repositorio

### **CSV de Control:**
- Estado en tiempo real de cada usuario
- Tracking de intentos y completados
- Contador de reenvíos fallidos

---

## 🛠️ Stack Tecnológico

- **Lenguaje:** Python 3.9
- **Dependencias:** pandas, requests
- **Automatización:** GitHub Actions
- **Base de datos:** CSV (control local)
- **API:** Botpress Cloud
- **Webhook:** Botpress WhatsApp Integration
- **Monitoreo:** GitHub Actions Logs

---

**Documentación creada:** Septiembre 12, 2025  
**Versión:** 1.0  
**Estado:** Sistema en pruebas, listo para producción