# AMA Bot - Sistema de Envíos Automatizados

## Descripción del Proyecto
Sistema automatizado para envío de sesiones de terapia a través de Botpress, con control granular por ubicaciones (colegios/salones) y monitoreo detallado de interacciones.

## Estructura del Sistema

### 📁 Estructura del Proyecto

#### Scripts Principales (Directorio Raíz)
1. **csvNumbersGenerator.py** - Generador de CSV de control desde XLSX
2. **ama_bot_controller.py** - Controlador principal de envíos con lógica de negocio
3. **monitor_ubicaciones.py** - Sistema de monitoreo y reportes por ubicación
4. **agregar_numeros_nuevos.py** - Actualizar CSV manteniendo progreso existente
5. **botNumbers_test.xlsx** - Archivo fuente con usuarios y ubicaciones

#### Carpetas Organizadas
- **`scripts_legacy/`** - Versiones anteriores (botpressSender.py, etc.)
- **`utilities/`** - Herramientas de soporte (get_table_rows.py, sync, GitHub runner)
- **`testing/`** - Scripts de prueba (test_webhook.py, botPressCURL.py) 
- **`scripts_especificos/`** - Scripts para casos puntuales (resets específicos)

> 💡 **Nota**: El flujo normal solo requiere los scripts del directorio principal

### 📊 Estructura de Datos

#### Archivo XLSX de entrada (`botNumbers_test.xlsx`):
```
numero          | location | location_name | salon
573168124099    | Colegio  | Maynas        | 5H
573156617659    | Colegio  | Maynas        | 5H  
573159267303    | Colegio  | Maynas        | 5H
```

#### CSV de Control Generado (`control_envios.csv`):
- **numero**: Número de teléfono
- **location**: Tipo de ubicación (ej: Colegio)
- **location_name**: Nombre específico (ej: Maynas)
- **salon**: Salón o aula específica
- **sesion**: Sesión (1-6)
- **day**: Día de la sesión (1-5)
- **enviado**: 0/1 si fue enviado
- **fecha_envio**: Timestamp del envío
- **resultado**: Resultado del envío
- **completado**: 0/1 si fue completado por el usuario
- **intentos_envio**: Contador de intentos (máx 2)
- **fecha_completado**: Timestamp de completación
- **ultimo_estado_botpress**: Estado actual en Botpress
- **reenvios_consecutivos_fallidos**: Contador de fallos
- **usuario_excluido**: 0/1 si fue excluido del sistema

## Lógica de Envíos Automatizada

### 🕒 Programación Diaria (5:00 PM)
1. **Envío inicial**: Todas las sesiones se envían a las 17:00 horas
2. **Validación al día siguiente**: Sistema verifica completación automáticamente
3. **Lógica de reenvío**:
   - ✅ **Completó sesión**: Envía siguiente sesión
   - ❌ **No completó**: Reenvía misma sesión (segunda oportunidad)
   - 🚫 **No completa segunda vez**: Usuario se marca inactivo

### 📝 Reglas de Negocio
- **Máximo 2 intentos** por sesión por usuario
- **Usuarios excluidos** después de 2 fallos consecutivos
- **Prerrequisito**: Día anterior debe estar completado para continuar
- **Sesión 1, Día 1**: Siempre permitido (inicio de campaña)

## Comandos de Uso

### Generar CSV desde XLSX
```bash
python3 csvNumbersGenerator.py
```

### Ejecutar Sistema de Envíos
```bash
python3 ama_bot_controller.py
```
**Opciones del menú**:
1. Ver estadísticas actualizadas
2. Procesar TODOS los pendientes  
3. Procesar sesión/día específico
4. Procesar cantidad limitada
5. Actualizar datos desde Botpress

### Generar Reportes de Monitoreo
```bash
# Reporte en consola
python3 monitor_ubicaciones.py --no-excel

# Reporte con exportación a Excel
python3 monitor_ubicaciones.py
```

### Agregar Números Nuevos (Mantener Progreso)
```bash
# Actualizar CSV con números nuevos del XLSX
python3 agregar_numeros_nuevos.py

# Usar archivos específicos
python3 agregar_numeros_nuevos.py --csv otro_control.csv --xlsx otros_numeros.xlsx
```

**Comportamiento**:
- ✅ **Números nuevos**: Empiezan en sesión 1, día 1
- ♻️ **Números existentes**: Mantienen su progreso actual  
- 🔄 **Datos de ubicación**: Se actualizan desde el XLSX
- 💾 **Backup automático**: Se crea backup antes de modificar

## Configuración de APIs

### Webhook Botpress
- **URL**: `https://webhook.botpress.cloud/2d63c736-0910-47a8-b06a-c82c12372106`
- **Secret**: `73c380fc550ad6b061d4d8ec3547731eprod`

### Tables API Botpress  
- **Token**: `bp_pat_t3Qzk5mKulbKTudzrZHEJ2Rjqkb6z9f6qrw9`
- **Bot ID**: `f70c360d-ed8d-402f-9cd2-488d9f1d358c`
- **Tabla**: `DataJsonProgressTable`

## Monitoreo por Ubicaciones

### 📊 Reportes Disponibles
1. **Reporte General**: Estadísticas por location/location_name
2. **Reporte por Salón**: Detalle granular por salon
3. **Progreso por Sesión**: Avance por sesión y ubicación  
4. **Usuarios Problemáticos**: Excluidos y con reenvíos fallidos
5. **Exportación Excel**: Reporte completo en múltiples hojas

### 📈 Métricas Clave
- **Tasa de envío**: % de registros enviados vs total
- **Tasa de completado**: % de sesiones completadas vs enviadas
- **Tasa de exclusión**: % de usuarios excluidos por ubicación
- **Progreso por sesión**: Avance específico por sesión y ubicación

## Flujo de Trabajo Semanal

### Método Inicial (CSV nuevo)
1. **Actualizar XLSX**: Agregar/modificar usuarios en `botNumbers_test.xlsx`
2. **Regenerar CSV**: Ejecutar `csvNumbersGenerator.py` (⚠️ Pierde progreso existente)
3. **Procesar envíos**: Usar `ama_bot_controller.py` para envíos diarios
4. **Monitoreo semanal**: Ejecutar `monitor_ubicaciones.py` para reportes

### Método Recomendado (Mantener progreso)
1. **Actualizar XLSX**: Agregar/modificar usuarios en `botNumbers_test.xlsx` 
2. **Actualizar CSV**: Ejecutar `agregar_numeros_nuevos.py` (✅ Mantiene progreso)
3. **Procesar envíos**: Usar `ama_bot_controller.py` para envíos diarios
4. **Monitoreo semanal**: Ejecutar `monitor_ubicaciones.py` para reportes
5. **Análisis**: Revisar Excel exportado para toma de decisiones

### Casos de Uso Típicos
- **🆕 Nuevos estudiantes**: Usar `agregar_numeros_nuevos.py`
- **🔄 Cambio de salón**: Actualizar XLSX y usar `agregar_numeros_nuevos.py` 
- **🗑️ Eliminar usuarios**: Remover del XLSX y usar `agregar_numeros_nuevos.py`
- **📊 Inicio de período**: Usar `csvNumbersGenerator.py` para empezar limpio

## Próximas Implementaciones
- [ ] Integración con GitHub Actions para descarga automática de CSV
- [ ] Scheduler automático para envíos a las 17:00
- [ ] Dashboard web para monitoreo en tiempo real
- [ ] Notificaciones automáticas por Slack/Teams

---
**Última actualización**: 2025-09-25
**Versión**: 2.0 (Con soporte de ubicaciones)

## 🔑 PUNTOS CRÍTICOS PARA RECORDAR SIEMPRE

### 📡 Sistema de Envíos
- **Los envíos se ejecutan SOLO por GitHub Actions** - No por archivos locales
- **Para que cambios estén en producción**: Deben estar subidos al repositorio remoto
- **Horario**: Actions se ejecutan automáticamente a las 5:00 PM Colombia diariamente

### 📊 Monitoreo de Envíos
- **Para monitorear envíos**: Siempre revisar el `control_envios.csv` **REMOTO**, no local
- **El CSV remoto es el que se actualiza** con respuestas y progreso real
- **El CSV local puede estar desactualizado** respecto al progreso real

### ➕ Proceso para Agregar Nuevos Usuarios (SIN PERDER PROGRESO)
1. **Obtener el CSV `control_envios.csv` remoto** (con progreso actual de usuarios existentes)
2. **Actualizar CSV local** añadiendo números nuevos MANTENIENDO el progreso de usuarios anteriores
3. **Subir CSV actualizado al remoto** sin perder información anterior

### 🎯 Objetivo Principal
- **Agregar nuevos usuarios** que empiecen en sesión 1, día 1
- **Mantener progreso** de usuarios existentes
- **Proceso incremental**: Ir sumando usuarios sin resetear el sistema

## Memorias Personales

### 📤 **PROCESO ESTÁNDAR PARA AGREGAR NUEVOS NÚMEROS (ACTUALIZADO 2025-11-03)**

#### 🎯 **Método Único Estandarizado**
Este es el **ÚNICO proceso aprobado** para agregar nuevos números al sistema. Todas las formas anteriores quedan obsoletas.

#### **Paso 1: 📥 Descargar CSV Remoto Actual**
```bash
python3 -c "
import requests
import pandas as pd
import io

github_url = 'https://raw.githubusercontent.com/Rodato/AMA-Bot_automation/main/control_envios.csv'
response = requests.get(github_url, timeout=30)
df = pd.read_csv(io.StringIO(response.text), dtype={'numero': str})
df.to_csv('control_envios.csv', index=False)
print(f'✅ CSV remoto descargado: {len(df)} registros')
"
```

#### **Paso 2: ➕ Procesar Nuevos Números**
```bash
# Archivo fuente: BotNumbers_Production.xlsx (o el nombre que corresponda)
echo "s" | python3 agregar_numeros_nuevos.py --xlsx BotNumbers_Production.xlsx
```

#### **Paso 3: 📤 Subir CSV Actualizado al Repositorio Remoto**
```bash
git add control_envios.csv
git commit -m "➕ Agregar [X] nuevos usuarios al sistema AMA Bot"
git stash           # Si hay cambios pendientes
git pull --rebase origin main
git push origin main
```

#### **✅ Características del Proceso Estándar:**
- **Mantiene progreso existente** de usuarios anteriores
- **Descarga CSV remoto actualizado** automáticamente
- **Procesa sin confirmación manual** (`echo "s"`)
- **Manejo robusto de conflictos** git (stash + rebase)
- **Backup automático** antes de modificar
- **Sincronización completa** con repositorio remoto

#### **🚫 Procesos Obsoletos (NO USAR):**
- ❌ Regenerar CSV completo con `csvNumbersGenerator.py`
- ❌ Procesos manuales sin descarga remota
- ❌ Cualquier método que no mantenga progreso existente
- ❌ Sincronización manual sin git stash/rebase

#### **📊 Flujo Completo:**
```
XLSX actualizado → Descargar CSV remoto → Procesar nuevos números → 
Subir al repositorio → GitHub Actions (5:00 PM) → Envíos automáticos
```

**REGLA**: Este es el único proceso autorizado para mantener consistencia y evitar pérdida de datos.