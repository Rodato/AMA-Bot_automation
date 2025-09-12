# 🏗️ AMA Bot Automation - Arquitectura del Sistema

## 📐 Diagrama de Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  GitHub Actions │    │  Botpress API   │    │ WhatsApp Users  │
│                 │    │                 │    │                 │
│ • Cron: 9AM COL │────│ • Tables API    │────│ • Template Msgs │
│ • Python Script │    │ • Webhook       │    │ • User Response │
│ • CSV Updates   │    │ • Progress Data │    │ • Completions   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ CSV Database    │    │ Business Logic  │    │ Campaign Flow   │
│                 │    │                 │    │                 │
│ • User Progress │    │ • Prerequisites │    │ • 6 Sessions    │
│ • Retry Logic   │    │ • Retry Rules   │    │ • 5 Days Each   │
│ • Exclusions    │    │ • Exclusions    │    │ • Sequential    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🔄 Flujo de Datos

### **1. Inicialización (9:00 AM Colombia)**
```python
GitHub Actions Trigger
├── Load CSV Database
├── Initialize Botpress Connection
└── Setup Environment Variables
```

### **2. Data Synchronization**
```python
Botpress API Query
├── GET /tables/DataJsonProgressTable/rows/find
├── Parse User Progress (session1: {1: "2", 2: "1", ...})
├── Sync with Local CSV
└── Update Completion Status
```

### **3. Candidate Selection**
```python
Filter Pending Records
├── enviado = 0 (Never sent)
└── OR
    ├── enviado = 1 (Sent but...)
    ├── completado = 0 (Not completed)
    ├── intentos_envio < 2 (Less than 2 attempts)
    └── usuario_excluido = 0 (Not excluded)
```

### **4. Validation Logic**
```python
For Each Candidate:
├── Check if user_excluded = 1 → Skip
├── Check if attempts_day >= 2 → Skip  
├── Check if completed = 1 → Skip
├── If session=1, day=1 → Always Allow
└── Else:
    ├── Check prerequisite (previous day completed)
    ├── OR retry same day (sent but not completed)
    └── Allow/Deny based on conditions
```

### **5. Message Sending**
```python
Webhook POST Request
├── URL: webhook.botpress.cloud/[webhook-id]
├── Headers: x-bp-secret, Content-Type
├── Payload: {clientNumber, session, day}
├── Response: 200 = Success, Other = Failure
└── Update CSV: attempts++, sent status, timestamp
```

### **6. Consecutive Failures Logic**
```python
Post-Send Analysis
├── For each user:
│   ├── If day completed → reset consecutive_failures = 0
│   └── If retry failed → consecutive_failures++
├── If consecutive_failures >= 2:
│   ├── Set usuario_excluido = 1
│   └── Log exclusion
└── Save changes to CSV
```

---

## 📊 Data Models

### **CSV Schema**
```csv
Column                        | Type | Description
------------------------------|------|----------------------------------
numero                        | str  | Phone number (+57 format)
sesion                        | int  | Session number (1-6)
day                          | int  | Day within session (1-5)
enviado                      | int  | 0=not sent, 1=sent
fecha_envio                  | str  | Timestamp of send attempt
resultado                    | str  | Result message/error
completado                   | int  | 0=not completed, 1=completed
intentos_envio               | int  | Number of attempts for this day
fecha_completado             | str  | Completion timestamp
ultimo_estado_botpress       | int  | Last status from Botpress (0,1,2)
reenvios_consecutivos_fallidos| int  | Consecutive failed retries
usuario_excluido             | int  | 0=active, 1=permanently excluded
```

### **Botpress Progress Structure**
```json
{
  "clientNumber": "573156617659",
  "session1": {
    "1": "2",  // Day 1: Completed
    "2": "1",  // Day 2: Sent but not completed
    "3": "0",  // Day 3: Not sent
    "4": "0",  // Day 4: Not sent
    "5": "0"   // Day 5: Not sent
  }
}
```

### **Status Codes**
- **0:** Not sent
- **1:** Sent but not completed by user
- **2:** Completed by user

---

## 🔐 Security Architecture

### **Environment Variables**
```yaml
GitHub Secrets:
├── WEBHOOK_URL      # Botpress webhook endpoint
├── WEBHOOK_SECRET   # Authentication secret
├── BOTPRESS_TOKEN   # API bearer token
├── BOT_ID          # Botpress bot identifier
└── PROGRESS_TABLE_NAME # Table name in Botpress
```

### **Authentication Flow**
```
GitHub Actions
├── Load secrets from GitHub environment
├── Pass to Python script as env vars
├── Script uses os.getenv() with fallbacks
└── No credentials in code/repository
```

---

## ⚡ Performance Considerations

### **Rate Limiting**
- **2 second pause** between message sends
- **Maximum 1000 records** per Botpress API call
- **Timeout: 15 seconds** for webhook requests
- **Timeout: 30 seconds** for API queries

### **Memory Usage**
- **CSV loaded in pandas DataFrame** (~120 records = minimal memory)
- **Botpress data cached** in dictionary for fast lookups
- **Processing in batches** (all pending records per execution)

### **Execution Time**
- **Estimated: 2-5 minutes** for typical workload
- **Scales linearly** with number of pending sends
- **Network I/O bound** (webhook calls)

---

## 🚨 Error Handling

### **API Failures**
```python
try:
    response = requests.post(api_endpoint, timeout=30)
    if response.status_code != 200:
        log_error(f"API Error: {response.status_code}")
        continue_processing = True
except requests.exceptions.Timeout:
    log_error("API Timeout - continuing with cached data")
    continue_processing = True
except Exception as e:
    log_error(f"Unexpected error: {e}")
    continue_processing = False
```

### **Webhook Failures**
```python
# Individual webhook failures don't stop batch processing
# Failed sends are marked with error status
# Retry logic handles failed sends in next execution
```

### **Git Failures**
```python
# Graceful handling of commit/push failures
# CSV changes preserved locally
# Manual intervention possible if needed
```

---

## 🔄 Retry Logic Flowchart

```
User receives Day N message
├── Completes → Status = 2
│   ├── consecutive_failures = 0
│   └── Advance to Day N+1
└── Does not complete → Status = 1
    ├── attempts_day < 2?
    │   ├── YES → Schedule retry Day N
    │   │   └── Retry fails?
    │   │       ├── YES → consecutive_failures++
    │   │       │   └── consecutive_failures >= 2?
    │   │       │       ├── YES → EXCLUDE USER
    │   │       │       └── NO → Continue
    │   │       └── NO → consecutive_failures = 0
    │   └── NO → Move to next eligible day
    └── User excluded → No more messages
```

---

## 🎯 Campaign Logic

### **Session Structure**
```
Campaign = 6 Sessions × 5 Days = 30 Messages per user
├── Session 1: Days 1-5 (Week 1)
├── Session 2: Days 1-5 (Week 2)  [Not implemented]
├── Session 3: Days 1-5 (Week 3)  [Not implemented]
├── Session 4: Days 1-5 (Week 4)  [Not implemented]
├── Session 5: Days 1-5 (Week 5)  [Not implemented]
└── Session 6: Days 1-5 (Week 6)  [Not implemented]
```

### **Prerequisites**
- **Day 1:** Always allowed (campaign start)
- **Day N+1:** Requires Day N to be completed (status = 2)
- **Session N+1:** Requires Session N Day 5 to be completed
- **Retries:** Same day if sent but not completed (status = 1)

---

## 📈 Monitoring & Logging

### **GitHub Actions Logs**
```
[TIMESTAMP] 🚀 INICIANDO PROCESAMIENTO AUTOMÁTICO
[TIMESTAMP] ✅ CSV cargado: 120 registros
[TIMESTAMP] 🔄 Consultando datos de Botpress...
[TIMESTAMP] ✅ Datos Botpress: 9 usuarios
[TIMESTAMP] 📞 Evaluando: 573156617659 S1D1
[TIMESTAMP]    ✅ Validado: Inicio campaña
[TIMESTAMP]    ✅ Enviado exitosamente
[TIMESTAMP] 📊 RESUMEN DE ENVÍOS:
[TIMESTAMP]    ✅ Exitosos: 3
[TIMESTAMP]    ❌ Fallidos: 0
[TIMESTAMP]    ⏭️ Omitidos: 114
```

### **Metrics Tracked**
- Total records processed
- Successful sends
- Failed sends  
- Omitted records (with reasons)
- Users excluded
- Execution time
- API response times

---

**Documentación actualizada:** Septiembre 12, 2025  
**Versión:** 1.0  
**Mantenedor:** AMA Bot Development Team