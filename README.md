# 🤖 AMA Bot Automation

Sistema automatizado de mensajería WhatsApp integrado con Botpress para campañas de 6 sesiones.

## 🚀 Características

- ✅ **Envíos automáticos** programados diariamente
- ✅ **Validación de prerrequisitos** (día anterior completado)
- ✅ **Control de reenvíos** (máximo 2 intentos)
- ✅ **Sincronización con Botpress** en tiempo real
- ✅ **GitHub Actions** para ejecución en la nube

## ⏰ Programación

**Horario:** 3:00 PM Colombia (GMT-5) todos los días

## 📊 Estructura de Campaña

- **6 sesiones** de **5 días** cada una
- **Prerrequisitos:** Día anterior debe estar completado
- **Control automático** de progreso individual

## 🔧 Configuración

Las credenciales se manejan mediante **GitHub Secrets**:

- `WEBHOOK_URL`
- `WEBHOOK_SECRET` 
- `BOTPRESS_TOKEN`
- `BOT_ID`
- `PROGRESS_TABLE_NAME`

## 📁 Archivos Principales

- `.github/workflows/ama-bot-scheduler.yml` - Workflow de GitHub Actions
- `ama_bot_github_runner.py` - Script principal
- `control_envios.csv` - Base de datos de control
- `requirements.txt` - Dependencias Python

## 🎯 Uso

El sistema se ejecuta automáticamente. Para ejecutar manualmente:
1. Ve a **Actions** en GitHub
2. Selecciona **AMA Bot Daily Scheduler**  
3. Haz clic en **Run workflow**

---
🚀 **Automatizado con GitHub Actions**