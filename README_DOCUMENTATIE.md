# 📚 IRADO CHATBOT PROJECT - COMPLETE DOCUMENTATIE

**Overzicht van alle documentatie voor Irado Grofvuil Chatbot Project**

---

## 🚀 QUICK START GUIDES

### Voor Nieuwe Setup:
1. **[AZURE_QUICKSTART.md](AZURE_QUICKSTART.md)** - ⚡ 5 minuten Azure account setup
2. **[AZURE_DEPLOYMENT_GUIDE.md](AZURE_DEPLOYMENT_GUIDE.md)** - Complete deployment instructies

### Voor Bestaande Setup:
1. **[DEPLOYMENT_README.md](DEPLOYMENT_README.md)** - Snelle deploy/update instructies
2. **[DASHBOARD_QUICKSTART.md](DASHBOARD_QUICKSTART.md)** - Dashboard deployment

---

## 🔧 SETUP & CONFIGURATIE

### Azure Account
- **[AZURE_ACCOUNT_SETUP.md](AZURE_ACCOUNT_SETUP.md)** - Complete Azure account setup guide
  - Account aanmaken
  - Service Principal configuratie
  - Permissies en roles
  - Security best practices
  - ⏱️ Leestijd: 15 min

- **[AZURE_QUICKSTART.md](AZURE_QUICKSTART.md)** - Korte versie voor snelle setup
  - 5 minuten stappen
  - Minimale configuratie
  - ⏱️ Leestijd: 2 min

### Database
- **[DATABASE_MIGRATION_COMPLETE.md](DATABASE_MIGRATION_COMPLETE.md)** - Database consolidatie
  - Van 2 → 1 database
  - Kostenbesparing (€16.90/maand)
  - Migratie stappenplan
  - Troubleshooting
  - ⏱️ Leestijd: 10 min

### Database Backups (aanbevolen)
- **Backup script**: `mainfact-azure-backup.sh`
  - Maakt **PostgreSQL dumps** (`.sql` + `.dump`) en een **tar.gz archive** met:
    - DB dumps
    - `VERSION.txt`
    - `chatbot/koad.csv`
    - `chatbot/prompts/system_prompt.txt`
    - `data/`
  - Slaat alles **lokaal** op in: `./backups/`
  - Vereist: `az login`, `pg_dump`, `psql`, `tar`, `curl`

**Gebruik (lokaal op deze server):**
```bash
cd /opt/irado-azure
az login
./mainfact-azure-backup.sh
```

**Output (voorbeeld):**
```bash
/opt/irado-azure/backups/irado_chat-YYYYMMDD-HHMMSS.sql
/opt/irado-azure/backups/irado_chat-YYYYMMDD-HHMMSS.dump
/opt/irado-azure/backups/irado-backup-YYYYMMDD-HHMMSS.tar.gz
```

### Dashboard
- **[DASHBOARD_LOGGING_COMPLETE.md](DASHBOARD_LOGGING_COMPLETE.md)** - Dashboard logging infrastructuur
  - Complete logging service
  - Activity logs UI
  - CSV upload debugging
  - API endpoints
  - ⏱️ Leestijd: 8 min

- **[DASHBOARD_AZURE_DEPLOYMENT.md](DASHBOARD_AZURE_DEPLOYMENT.md)** - Dashboard deployment details
- **[DASHBOARD_AZURE_PLAN.md](DASHBOARD_AZURE_PLAN.md)** - Architectuur planning

---

## 💰 KOSTEN & INFRASTRUCTUUR

### Kostenoverzicht
- **[IRADO_INFRASTRUCTUUR_VOORSTEL.md](IRADO_INFRASTRUCTUUR_VOORSTEL.md)** - Standaard infrastructuur
  - **Totaal:** €58.53/maand (bij 500 gesprekken)
  - 1× Database (€18.89)
  - 2× App Services (€11.84 each)
  - Container Registry, Storage, Key Vault
  - Per-chat kosten: €0.041
  - ⏱️ Leestijd: 5 min

- **[IRADO_INFRASTRUCTUUR_PREMIUM.md](IRADO_INFRASTRUCTUUR_PREMIUM.md)** - Premium infrastructuur
  - **Totaal:** €119.13/maand
  - High Availability database
  - Geo-redundant backups (28 dagen)
  - Premium App Service Plan
  - ⏱️ Leestijd: 5 min

- **[AZURE_KOSTEN_ANALYSE.md](AZURE_KOSTEN_ANALYSE.md)** - Gedetailleerde cost breakdown
  - Per-resource kosten
  - Schaalbaarheid analyse
  - Optimalisatie tips
  - ⏱️ Leestijd: 10 min

---

## 🏗️ PROJECT STRUCTUUR

```
/opt/irado/
├── chatbot/                          # Hoofdapplicatie
│   ├── app.py                        # Flask API server
│   ├── ai_service.py                 # OpenAI integratie
│   ├── database_service.py           # PostgreSQL service
│   ├── email_service_xml.py          # Email functionaliteit
│   ├── config.py                     # Configuratie
│   ├── prompts/system_prompt.txt     # AI instructies
│   └── dashboard/                    # Management dashboard
│       ├── dashboard.py              # Dashboard Flask app
│       ├── logging_service.py        # Dashboard logging
│       ├── templates/                # HTML templates
│       └── static/                   # JS, CSS
│
├── website/                          # Chatbot frontend widget
│   ├── index.html                    # Chat interface
│   └── website/                      # Assets
│
├── deploy-to-azure.sh                # 🚀 Chatbot deployment
├── deploy-dashboard-to-azure.sh      # 🚀 Dashboard deployment
├── quick-deploy.sh                   # ⚡ Snelle deploy (beide)
│
└── *.md                              # 📚 Documentatie
```

---

## 📘 Nextcloud Collectives – samenvattende documentatie

Voor gebruik in Nextcloud Collectives is er een aparte, leesbare samenvatting aangemaakt in de map `nextcloud/`:

- `nextcloud/README.md` – startpagina + navigatie.
- `nextcloud/01-projectoverzicht.md` – functioneel overzicht van het project.
- `nextcloud/02-gebruik-door-irado.md` – hoe medewerkers en inwoners de chatbot gebruiken.
- `nextcloud/03-technisch-overzicht-en-architectuur.md` – technisch overzicht op hoog niveau.
- `nextcloud/04-beheer-en-operations.md` – dagelijks beheer, monitoring en support.
- `nextcloud/05-deployment-en-omgevingen.md` – samenvatting van deployment en Azure-omgevingen.
- `nextcloud/06-links-en-brondocumenten.md` – overzicht van alle belangrijke URLs en .md-bestanden.

Gebruik deze `nextcloud/`-map als basis voor de Collectives-pagina’s; de hierboven gelinkte .md-bestanden zijn geschreven in het Nederlands en verwijzen waar nodig naar de diepere documentatie in deze repository.

---

## 🆕 Release 2.2.0 (13 oktober 2025)

| Onderdeel | Update |
|-----------|--------|
| **Multi-route verwerking** | Chatbot detecteert itemmixen en verstuurt voor elke route exact één `send_email_to_team`-toolcall plus één gecombineerde `send_email_to_customer`-toolcall. Zie `chatbot/ai_service.py` voor de JSON-schema’s. |
| **Nieuwe system prompt** | `chatbot/prompts/system_prompt.txt` (versie 2.0) beschrijft mix-detectie, routingregels en verplichte toolpayloads. De prompt is actief in de tabel `system_prompts`. |
| **Lokale tijdzone** | Alle services draaien met `APP_TIMEZONE=Europe/Amsterdam` (inclusief automatische zomertijd). Logs en emails tonen Amsterdam-tijd. |
| **Gedetailleerde logging** | Elke toolcall en e-mail wordt als gestructureerde JSON vastgelegd. Bekijk de Dashboard Logs-tab of `/api/dashboard/logs` voor debugging. |
| **Per-route QML** | `chatbot/email_service_xml.py` genereert één XML-bestand per route (met volume/constraints) en een klantmail met routesecties + eventuele planningnotes. |
| **Versies & deployment** | Chatbot en dashboard health endpoints rapporteren `2.2.0`. Deployment scripts lezen `VERSION.txt` en publiceren `TZ`/`APP_TIMEZONE` naar Azure. |

> ✅ Na wijzigingen altijd `./deploy-dashboard-fresh.sh` en `./deploy-to-azure.sh` draaien zodat de 2.2.0-containers live staan.

---

## 🔍 WELKE DOCUMENTATIE HEB IK NODIG?

### Scenario: "Ik wil een nieuw Irado Azure account opzetten"
→ **[AZURE_QUICKSTART.md](AZURE_QUICKSTART.md)** (5 min)  
→ **[AZURE_ACCOUNT_SETUP.md](AZURE_ACCOUNT_SETUP.md)** (volledige details)

### Scenario: "Ik wil het project deployen"
→ **[AZURE_DEPLOYMENT_GUIDE.md](AZURE_DEPLOYMENT_GUIDE.md)**  
→ **[DEPLOYMENT_README.md](DEPLOYMENT_README.md)** (updates)

### Scenario: "Hoeveel gaat dit kosten?"
→ **[IRADO_INFRASTRUCTUUR_VOORSTEL.md](IRADO_INFRASTRUCTUUR_VOORSTEL.md)** (standaard)  
→ **[IRADO_INFRASTRUCTUUR_PREMIUM.md](IRADO_INFRASTRUCTUUR_PREMIUM.md)** (premium)  
→ **[AZURE_KOSTEN_ANALYSE.md](AZURE_KOSTEN_ANALYSE.md)** (details)

### Scenario: "CSV upload werkt niet"
→ **[DASHBOARD_LOGGING_COMPLETE.md](DASHBOARD_LOGGING_COMPLETE.md)**  
→ Dashboard → Logs tab → Dashboard Activity Logs

### Scenario: "Database problemen"
→ **[DATABASE_MIGRATION_COMPLETE.md](DATABASE_MIGRATION_COMPLETE.md)**  
→ Check: Is `bedrijfsklanten` tabel in `irado_chat` database?

### Scenario: "Ik wil iets aanpassen en opnieuw deployen"
→ **[DEPLOYMENT_README.md](DEPLOYMENT_README.md)**  
→ Run: `./quick-deploy.sh` (of `./deploy-to-azure.sh`)

### Scenario: "Wat zijn de actuele prompt-/toolregels?"
→ `chatbot/prompts/system_prompt.txt` (versie 2.0)  
→ Controleer actieve prompt: `SELECT version FROM system_prompts WHERE is_active = TRUE;`

### Scenario: "Toolcalls of e-mails debuggen"
→ Dashboard → Logs tab → filter op `TOOL_CALL`, `EMAIL_TO_TEAM`, `EMAIL_TO_CUSTOMER`  
→ Elke entry bevat volledige JSON (items, route, session_id, timing).

---

## 📊 SYSTEM OVERVIEW

### Huidige Architectuur (October 2025)

```
┌─────────────────────────────────────────────────────┐
│                   AZURE CLOUD                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │  Chatbot App     │      │  Dashboard App   │   │
│  │  (B1 Plan)       │      │  (B1 Plan)       │   │
│  │  Port: 443       │      │  Port: 443       │   │
│  └────────┬─────────┘      └────────┬─────────┘   │
│           │                          │              │
│           │   ┌──────────────────────┘              │
│           │   │                                     │
│           ▼   ▼                                     │
│  ┌────────────────────────────────┐                │
│  │  PostgreSQL Database           │                │
│  │  irado_chat (B1ms, 32GB)      │                │
│  │  ├── sessions                  │                │
│  │  ├── messages                  │                │
│  │  ├── system_prompts            │                │
│  │  ├── bedrijfsklanten (KOAD)   │                │
│  │  └── dashboard_logs            │                │
│  └────────────────────────────────┘                │
│                                                      │
│  ┌────────────────────────────────┐                │
│  │  Azure Container Registry      │                │
│  │  irado.azurecr.io              │                │
│  │  ├── irado-chatbot:latest      │                │
│  │  └── irado-dashboard:latest    │                │
│  └────────────────────────────────┘                │
│                                                      │
│  ┌────────────────────────────────┐                │
│  │  Azure OpenAI                  │                │
│  │  Model: gpt-4o                 │                │
│  │  Endpoint: ...openai.azure.com │                │
│  └────────────────────────────────┘                │
│                                                      │
│  ┌────────────────────────────────┐                │
│  │  Storage & Key Vault           │                │
│  │  (voor backups & secrets)      │                │
│  └────────────────────────────────┘                │
│                                                      │
└─────────────────────────────────────────────────────┘

         ▲                      ▲
         │                      │
    ┌────┴──────┐         ┌────┴──────┐
    │  End User │         │  Irado    │
    │  (Chat)   │         │  Admin    │
    └───────────┘         └───────────┘
```

### URLs:
- **Chatbot:** https://irado-chatbot-app.azurewebsites.net
- **Dashboard:** https://irado-dashboard-app.azurewebsites.net
- **Chat Widget:** https://irado-chatbot-app.azurewebsites.net/ (embedded)

---

## 🔐 CREDENTIALS & SECURITY

### Waar staan credentials?

**Lokaal (development):**
```bash
/opt/irado/.azure-credentials      # Azure credentials (NIET in git!)
/opt/irado/chatbot/.env            # App secrets (NIET in git!)
```

**Azure (production):**
```
Azure App Service → Configuration → Application Settings
- POSTGRES_HOST
- POSTGRES_PASSWORD
- AZURE_OPENAI_API_KEY
- SMTP credentials
- etc.
```

**⚠️ BELANGRIJK:**
- `.azure-credentials` is in `.gitignore`
- `.env` is in `.gitignore`
- Credentials worden automatisch via Azure App Settings gezet bij deployment
- NOOIT credentials committen naar Git!

---

## 🛠️ DEPLOYMENT SCRIPTS

### Hoofdscripts:
```bash
./deploy-to-azure.sh              # Chatbot deployment (prod/dev)
./deploy-dashboard-fresh.sh       # Dashboard fresh deploy (prod/dev)
# (legacy) ./deploy-dashboard-to-azure.sh
# (legacy) ./quick-deploy.sh
```

### Omgevingen (prod/dev)
Er zijn twee volledig gescheiden omgevingen in dezelfde Azure subscription:

- **prod** (bestaande live omgeving)
  - RG: `irado-rg`
  - Apps: `irado-chatbot-app`, `irado-dashboard-app`
  - DB: `irado-chat-db` / `irado_chat`
- **dev** (oefen-/test omgeving)
  - RG: `irado-dev-rg`
  - Apps: `irado-dev-chatbot-app`, `irado-dev-dashboard-app`
  - DB: `irado-dev-chat-db` / `irado_dev_chat`

Deploy naar dev of prod met `--env`:
```bash
./deploy-to-azure.sh --env dev
./deploy-dashboard-fresh.sh --env dev

./deploy-to-azure.sh --env prod
./deploy-dashboard-fresh.sh --env prod
```

### Dev secrets (server-only)
Op deze server gebruiken we een lokaal bestand (niet in git) om dev DB secrets niet te vergeten:

- `/opt/irado-azure/.env.dev.local` (staat in `.gitignore`)

De deploy scripts laden dit bestand **automatisch** bij `--env dev` als het aanwezig is.

### Wat doen ze?
1. **Build** Docker images
2. **Push** naar Azure Container Registry
3. **Deploy** naar App Services
4. **Configure** environment variables
5. **Restart** apps
6. **Health check**
7. **Cleanup** oude images

### Parameters:
- Geen parameters nodig! Scripts detecteren alles automatisch
- Credentials komen van `.azure-credentials` of `az login`
- Prompt voor bevestiging (type 'y')

---

## 📈 MONITORING & LOGS

### Live Logs Bekijken:

**Chatbot logs:**
```bash
az webapp log tail --name irado-chatbot-app --resource-group irado-rg
```

**Dashboard logs:**
```bash
az webapp log tail --name irado-dashboard-app --resource-group irado-rg
```

**Of via Dashboard UI:**
- Open: https://irado-dashboard-app.azurewebsites.net
- Ga naar: **Logs** tab
- Zie: Chatbot Live Logs + Dashboard Activity Logs

### Metrics:
```bash
# CPU usage
az monitor metrics list \
  --resource /subscriptions/.../irado-chatbot-app \
  --metric "CpuPercentage"

# Memory
az monitor metrics list \
  --resource /subscriptions/.../irado-chatbot-app \
  --metric "MemoryPercentage"
```

---

## 🐛 TROUBLESHOOTING

### Common Issues:

**"503 Service Unavailable"**
→ App is nog aan het opstarten (wacht 2-3 minuten)  
→ Check logs: `az webapp log tail ...`

**"CSV upload timeout"**
→ Check Dashboard Logs tab  
→ Zie: [DASHBOARD_LOGGING_COMPLETE.md](DASHBOARD_LOGGING_COMPLETE.md)

**"Database connection failed"**
→ Check firewall rules  
→ Check: [DATABASE_MIGRATION_COMPLETE.md](DATABASE_MIGRATION_COMPLETE.md)

**"OpenAI API key invalid"**
→ Check App Service → Configuration  
→ Verify: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT

**"Deployment failed"**
→ Check Azure CLI login: `az account show`  
→ Check permissions: `az role assignment list`  
→ Zie: [AZURE_ACCOUNT_SETUP.md](AZURE_ACCOUNT_SETUP.md)

---

## 📞 SUPPORT & CONTACT

### Documentation:
- **Alle guides:** `/opt/irado/*.md`
- **Azure Docs:** https://docs.microsoft.com/azure/

### Azure Support:
- **Portal:** https://portal.azure.com → Help + Support
- **Status:** https://status.azure.com/

### Project Info:
- **Version:** October 2025
- **Status:** ✅ Production Ready
- **Deployment:** v17595xxxxx (zie logs voor current version)

---

## 📝 CHANGELOG

### October 2025
- ✅ Database consolidatie (2 → 1 database)
- ✅ Dashboard logging infrastructuur
- ✅ Complete Azure setup documentation
- ✅ Cost optimization (€16.90/maand besparing)
- ✅ CSV upload debugging tools
- ✅ Live logs viewer in dashboard

### September 2025
- ✅ Dashboard deployment naar Azure
- ✅ System prompt live editor
- ✅ Chat history viewer
- ✅ KOAD management

### August 2025
- ✅ Chatbot deployment naar Azure
- ✅ PostgreSQL database integratie
- ✅ Azure OpenAI integratie
- ✅ Email service (XML + HTML)

---

## 🎯 NEXT STEPS

### Voor Nieuwe Gebruikers:
1. ✅ Lees: [AZURE_QUICKSTART.md](AZURE_QUICKSTART.md)
2. ✅ Setup: Azure account + credentials
3. ✅ Deploy: Run deployment scripts
4. ✅ Test: Access chatbot en dashboard
5. ✅ Upload: KOAD CSV via dashboard

### Voor Bestaande Gebruikers:
1. ✅ Update: Pull latest code
2. ✅ Deploy: `./quick-deploy.sh`
3. ✅ Verify: Check health endpoints
4. ✅ Monitor: Dashboard logs tab

---

**🚀 Happy Deploying!**

Voor vragen: Check de relevante `.md` files of Azure documentation.
