# 🤖 AMA Bot Automation

Sistema automatizado de mensajería WhatsApp integrado con Botpress para campañas de 6 sesiones con control inteligente de reenvíos.

## 🚀 Características

- ✅ **Envíos automáticos** programados diariamente a las 9 AM Colombia
- ✅ **Validación de prerrequisitos** (día anterior completado)
- ✅ **Control de reenvíos consecutivos** (máximo 2 fallos seguidos)
- ✅ **Exclusión automática** de usuarios no responsivos
- ✅ **Sincronización bidireccional** con Botpress en tiempo real
- ✅ **GitHub Actions** para ejecución en la nube sin servidor

## ⏰ Programación

**Horario:** 9:00 AM Colombia (GMT-5) todos los días  
**Próxima ejecución:** Automática según cronograma

## 📊 Estructura de Campaña

- **6 sesiones** de **5 días** cada una (30 mensajes total por usuario)
- **Prerrequisitos secuenciales:** Día anterior debe estar completado
- **Lógica de reenvíos:** Máximo 2 intentos por día
- **Exclusión inteligente:** Usuario eliminado tras 2 reenvíos consecutivos fallidos

## 🔄 Lógica de Reenvíos

```
Usuario falla Día 1 → Reenvío Día 1 → ✅ Completa → Avanza Día 2
Usuario falla Día 1 → Reenvío Día 1 → ❌ Falla → Contador = 1
Usuario falla Día 2 → Reenvío Día 2 → ❌ Falla → Contador = 2 → EXCLUIDO
```

## 🔧 Configuración

### GitHub Secrets Requeridos:
- `WEBHOOK_URL` - Endpoint del webhook de Botpress
- `WEBHOOK_SECRET` - Clave de autenticación del webhook  
- `BOTPRESS_TOKEN` - Token de API de Botpress
- `BOT_ID` - Identificador del bot en Botpress
- `PROGRESS_TABLE_NAME` - Nombre de la tabla de progreso

### Variables de entorno locales:
Copia `.env.example` a `.env` y completa los valores para desarrollo local.

## 📁 Estructura del Proyecto

```
├── .github/workflows/
│   └── ama-bot-scheduler.yml    # Automatización GitHub Actions
├── ama_bot_github_runner.py     # Script principal optimizado
├── control_envios.csv           # Base de datos de control local
├── requirements.txt             # Dependencias Python
├── DEVELOPMENT_LOG.md           # Registro completo de desarrollo
├── ARCHITECTURE.md              # Documentación técnica detallada
└── README.md                    # Esta documentación
```

## 🎯 Uso

### Ejecución Automática
El sistema se ejecuta automáticamente todos los días a las 9 AM Colombia.

### Ejecución Manual
1. Ve a **Actions** en GitHub
2. Selecciona **AMA Bot Daily Scheduler**  
3. Haz clic en **Run workflow** → **Run workflow**

### Monitoreo
- **Logs detallados** en GitHub Actions
- **Historial de ejecuciones** en pestaña Actions
- **CSV actualizado** automáticamente con cada ejecución

## 📈 Métricas y Reportes

Cada ejecución genera reportes detallados:
- ✅ Envíos exitosos con detalles
- ❌ Envíos fallidos con razones
- ⏭️ Mensajes omitidos con causas
- 🚫 Usuarios excluidos permanentemente
- 📊 Estadísticas de progreso general

## 🧪 Estado Actual

**Fase:** Pruebas con números de Colombia (+57)  
**Números de prueba:** 4 usuarios  
**Próximo paso:** Migración a números de Perú (+51) con ~300 usuarios

## 🔐 Seguridad

- ✅ **Credenciales encriptadas** en GitHub Secrets
- ✅ **Sin datos sensibles** en el código
- ✅ **Variables de entorno** para desarrollo local
- ✅ **Autenticación segura** con Botpress

## 📋 Logs de Ejemplo

```
[2025-09-12 16:58:57] 🚀 INICIANDO PROCESAMIENTO AUTOMÁTICO
[2025-09-12 16:58:57] ✅ CSV cargado: 120 registros
[2025-09-12 16:58:57] 🔄 Consultando datos de Botpress...
[2025-09-12 16:58:57] ✅ Datos Botpress: 9 usuarios
[2025-09-12 16:58:57] 📞 Evaluando: 573156617659 S1D1
[2025-09-12 16:58:57]    ✅ Validado: Inicio campaña
[2025-09-12 16:58:57]    ✅ Enviado exitosamente
[2025-09-12 16:59:04] 📊 RESUMEN DE ENVÍOS:
[2025-09-12 16:59:04]    ✅ Exitosos: 3
[2025-09-12 16:59:04]    ❌ Fallidos: 0
[2025-09-12 16:59:04]    ⏭️ Omitidos: 114
```

## 🛠️ Tecnologías

- **Python 3.9** - Lenguaje principal
- **pandas** - Manipulación de datos CSV
- **requests** - Comunicación HTTP con APIs
- **GitHub Actions** - Automatización en la nube
- **Botpress Cloud** - Plataforma de chatbot
- **WhatsApp Business API** - Canal de mensajería

## 📚 Documentación Adicional

- [**DEVELOPMENT_LOG.md**](./DEVELOPMENT_LOG.md) - Registro detallado del desarrollo
- [**ARCHITECTURE.md**](./ARCHITECTURE.md) - Documentación técnica completa

---

**Estado:** ✅ Sistema funcional en fase de pruebas  
**Próxima milestone:** Migración a producción con números reales  
**Mantenimiento:** Automatizado via GitHub Actions  

🚀 **Desarrollado con GitHub Actions + Botpress + Python**