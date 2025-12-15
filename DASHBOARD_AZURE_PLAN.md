# Dashboard Deployment naar Azure - Plan & Architectuur

**Status:** 🟡 In Planning  
**Datum:** 3 Oktober 2025

---

## 🎯 Doel

Het Irado Dashboard als 3de Web App deployen naar Azure met:
1. KOAD/Bedrijfsklanten management (al werkend)
2. Chat History viewer (al werkend)
3. **NIEUW:** System Prompt Editor (live aanpasbaar)

---

## 🏗️ Huidige Architectuur

```
┌─────────────────────────────────────────────────────────────┐
│                        Azure Cloud                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐ │
│  │   Web App 1     │  │   Web App 2     │  │  Web App 3 │ │
│  │   (Chatbot)     │  │   (Website)     │  │ (Dashboard)│ │
│  │   Port 80       │  │   Port 80       │  │  Port 80   │ │
│  │                 │  │                 │  │            │ │
│  │ /api/chat       │  │ index.html      │  │ KOAD mgmt  │ │
│  │ /health         │  │ script.js       │  │ Chat hist  │ │
│  └────────┬────────┘  └────────┬────────┘  │ Prompt ed  │ │
│           │                    │           └─────┬──────┘ │
│           │                    │                 │        │
│           └────────────┬───────┴─────────────────┘        │
│                        │                                   │
│  ┌─────────────────────▼──────────────────────────┐      │
│  │          Azure PostgreSQL (Flexible)           │      │
│  ├────────────────────────────────────────────────┤      │
│  │  Database 1: irado_chat                       │      │
│  │  ├─ chat_sessions                             │      │
│  │  ├─ chat_messages                             │      │
│  │  └─ system_prompts (NEW!)                     │      │
│  │                                                │      │
│  │  Database 2: irado_bedrijfsklanten            │      │
│  │  └─ bedrijfsklanten                           │      │
│  └────────────────────────────────────────────────┘      │
│                                                             │
│  ┌────────────────────────────────────────────────┐       │
│  │     Azure Container Registry (ACR)             │       │
│  │  ├─ irado.azurecr.io/chatbot:final-complete-v1│       │
│  │  ├─ irado.azurecr.io/website:v1 (toekomstig)  │       │
│  │  └─ irado.azurecr.io/dashboard:v1 (toekomstig)│       │
│  └────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Wat al werkt (Chatbot)

- ✅ Azure OpenAI integratie
- ✅ PostgreSQL chat_sessions & chat_messages
- ✅ Adres validatie
- ✅ Email functionaliteit (XML naar team, HTML naar klant)
- ✅ Tool calls
- ✅ Health & readiness checks

---

## 🔄 Wat nu moet gebeuren

### 1. Database Updates

**Nieuwe table in `irado_chat` database:**

```sql
CREATE TABLE system_prompts (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) DEFAULT 'admin',
    notes TEXT
);
```

**Status:** 📝 Schema klaar in `system_prompt_schema.sql`

### 2. Dashboard Features

#### A. KOAD Management (✅ Al werkend)
- Upload CSV → Azure PostgreSQL `irado_bedrijfsklanten`
- Search, add, edit, delete entries
- **Verificatie nodig:** Werkt dit met Azure DB?

#### B. Chat History (✅ Al werkend)
- View alle sessions
- Bekijk messages per session
- **Verificatie nodig:** Leest dit van Azure DB?

#### C. System Prompt Editor (🟡 Nieuw)
- **Versioning**: Meerdere prompt versies bewaren
- **Live Edit**: WYSIWYG editor met preview
- **Activate**: Activeer een specifieke versie
- **History**: Bekijk alle versies en rollback
- **No Restart**: Changes zijn direct actief (chatbot checkt DB)

---

## 🎨 Dashboard UI Ontwerp

### Nieuwe Tab: "System Prompt"

```
┌─────────────────────────────────────────────────────────────┐
│  IRADO Dashboard                                            │
├─────────────────────────────────────────────────────────────┤
│  [Bedrijfsklanten] [Chat History] [System Prompt] [Stats]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Active Prompt: v1.0.0 (Last updated: 2025-10-03 19:00)    │
│  [Create New Version] [View History]                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  System Prompt Editor                               │   │
│  │  ─────────────────────────────────────────────────  │   │
│  │                                                       │   │
│  │  # Introductie                                       │   │
│  │                                                       │   │
│  │  👋 Hallo, ik ben de virtuele assistent van Irado.  │   │
│  │  Fijn dat je er bent! Waarmee kan ik je vandaag     │   │
│  │  helpen? Ik beantwoord vragen over afval...         │   │
│  │                                                       │   │
│  │  ...                                                 │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Version: [v1.1.0____] Notes: [Minor improvements_____]    │
│  [Save as Draft] [Save & Activate] [Test Prompt]           │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Prompt Versions History                            │   │
│  │  ─────────────────────────────────────────────────  │   │
│  │  ● v1.0.0 (Active) - 2025-10-03 12:00             │   │
│  │    v0.9.0 - 2025-10-01 10:00  [Activate] [View]   │   │
│  │    v0.8.5 - 2025-09-28 14:30  [Activate] [View]   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Plan

### Phase 1: Database Setup (15 min)

```bash
# 1. Login to Azure PostgreSQL
psql "host=irado-chat-db.postgres.database.azure.com \
     port=5432 \
     dbname=irado_chat \
     user=irado_admin \
     password=xxx \
     sslmode=require"

# 2. Run schema script
\i /opt/irado/chatbot/system_prompt_schema.sql

# 3. Verify
SELECT * FROM system_prompts;
```

### Phase 2: Chatbot Update (10 min)

```bash
# Already done:
# - system_prompt_service.py created
# - ai_service.py updated to use database

# Test locally:
cd /opt/irado/chatbot
python3 -c "from system_prompt_service import SystemPromptService; \
            svc = SystemPromptService(); \
            print(svc.get_active_prompt()[:100])"
```

### Phase 3: Dashboard Updates (30 min)

**Bestanden om aan te passen:**

1. `chatbot/dashboard/dashboard.py`
   - Voeg routes toe:
     - `GET /api/prompts` - List all prompts
     - `GET /api/prompts/active` - Get active prompt
     - `POST /api/prompts` - Create new prompt
     - `PUT /api/prompts/<id>` - Update prompt
     - `POST /api/prompts/<id>/activate` - Activate prompt
     - `DELETE /api/prompts/<id>` - Delete prompt

2. `chatbot/dashboard/templates/dashboard.html`
   - Voeg nieuwe tab toe: "System Prompt"
   - Voeg prompt editor UI toe
   - Voeg version history table toe

3. `chatbot/dashboard/static/js/dashboard.js`
   - Voeg JavaScript functies toe:
     - `loadPrompts()`
     - `savePrompt()`
     - `activatePrompt()`
     - `deletePrompt()`

### Phase 4: Azure Deployment (20 min)

**Option A: Zelfde container als chatbot**
```bash
# Pros: 
# - Simpel, geen extra Web App nodig
# - Dashboard en chatbot delen dezelfde database connections
# - Kosten besparing

# Cons:
# - Dashboard en chatbot in 1 container (minder scheiding)
# - Als chatbot restart, gaat dashboard ook down

# Implementation:
# - Dashboard routes toevoegen aan chatbot/app.py
# - Dashboard static files in chatbot/dashboard/
# - Rebuild chatbot image met dashboard included
```

**Option B: Aparte Web App (Aanbevolen)**
```bash
# Pros:
# - Scheiding van concerns
# - Dashboard kan independent schalen
# - Makkelijker om te maintainen
# - Security: Dashboard kan aparte auth hebben

# Cons:
# - Extra Web App kosten (~€10/maand)
# - Aparte deployment pipeline

# Implementation:
# 1. Create Dockerfile voor dashboard
# 2. Build en push naar ACR
# 3. Create nieuwe Web App in Azure
# 4. Configure environment variables
# 5. Deploy
```

---

## 💰 Kosten Schatting

### Option A (Dashboard in chatbot container):
- **Extra kosten:** €0/maand
- **Extra complexiteit:** Laag

### Option B (Aparte Web App):
- **Extra kosten:** ~€10-15/maand (Basic tier)
- **Extra complexiteit:** Medium
- **Voordelen:** Betere architectuur, scheiding

---

## 🔒 Security Considerations

1. **Dashboard Auth**: 
   - Basic Auth (zelfde als chatbot)
   - Of: Azure AD integratie (advanced)

2. **Database Access**:
   - Read/Write voor dashboard
   - Read-only voor chatbot op `system_prompts`

3. **Prompt Validation**:
   - Max length check (bijv. 10KB)
   - SQL injection prevention (via prepared statements)
   - XSS prevention in UI

---

## 🚀 Deployment Steps (Aanbeveling: Option B)

```bash
# 1. Database setup
psql -h irado-chat-db.postgres.database.azure.com \
     -U irado_admin \
     -d irado_chat \
     -f /opt/irado/chatbot/system_prompt_schema.sql

# 2. Create dashboard Dockerfile
cd /opt/irado
# (zie voorbeeldcode hieronder)

# 3. Build en push
docker build -f azure/containers/dashboard/Dockerfile \
  -t irado.azurecr.io/dashboard:v1.0.0 .
az acr login --name irado
docker push irado.azurecr.io/dashboard:v1.0.0

# 4. Create Web App
az webapp create \
  --resource-group irado-rg \
  --plan irado-app-service-plan \
  --name irado-dashboard-app \
  --deployment-container-image-name irado.azurecr.io/dashboard:v1.0.0

# 5. Configure environment variables
az webapp config appsettings set \
  --resource-group irado-rg \
  --name irado-dashboard-app \
  --settings \
    POSTGRES_HOST="irado-chat-db.postgres.database.azure.com" \
    POSTGRES_DB="irado_chat" \
    POSTGRES_USER="irado_admin" \
    POSTGRES_PASSWORD="xxx" \
    BEDRIJFSKLANTEN_DB_HOST="irado-bedrijfsklanten-db.postgres.database.azure.com" \
    BEDRIJFSKLANTEN_DB_NAME="irado_bedrijfsklanten" \
    BEDRIJFSKLANTEN_DB_USER="irado_admin" \
    BEDRIJFSKLANTEN_DB_PASSWORD="xxx"

# 6. Test
curl https://irado-dashboard-app.azurewebsites.net/health
```

---

## ✅ Testing Checklist

- [ ] Database schema created successfully
- [ ] System prompt service loads from DB
- [ ] Chatbot uses DB prompt (test via API)
- [ ] Dashboard can list all prompts
- [ ] Dashboard can create new prompt version
- [ ] Dashboard can activate a prompt
- [ ] Dashboard can edit existing prompt
- [ ] Prompt changes zijn DIRECT actief in chatbot (no restart)
- [ ] KOAD upload werkt met Azure DB
- [ ] Chat history viewer werkt met Azure DB
- [ ] All endpoints secured with authentication

---

## 🎯 Success Criteria

1. ✅ Dashboard live op Azure
2. ✅ System Prompt editor werkend
3. ✅ Prompt changes direct actief (no restart)
4. ✅ KOAD management werkt met Azure DB
5. ✅ Chat history viewer werkt met Azure DB
6. ✅ Versioning en rollback mogelijk
7. ✅ < 5 seconden response tijd
8. ✅ Authentication op alle endpoints

---

## 📚 Volgende Stappen

**Optie 1: Ik implementeer alles (aanbevolen)**
- Ik maak alle code
- Ik test lokaal
- Ik deploy naar Azure
- Jij test de UI

**Optie 2: Stapsgewijs samen**
- Eerst database setup
- Dan dashboard UI
- Dan Azure deployment
- Test na elke stap

**Optie 3: Alleen database + API**
- Ik focus op backend (database, API endpoints)
- Jij maakt dashboard UI later
- Of we gebruiken API via curl/Postman

---

**Welke optie wil je? Dan ga ik direct verder! 🚀**




