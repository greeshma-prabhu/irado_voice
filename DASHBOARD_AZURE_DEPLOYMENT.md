# 📊 Irado Dashboard - Azure Deployment Guide

Complete guide voor het deployen en gebruiken van het Irado Dashboard op Azure.

## 📋 Overzicht

Het Irado Dashboard is een webapplicatie voor het beheren van:
- **Bedrijfsklanten (KOAD)**: CSV upload, zoeken, toevoegen, bewerken
- **Chat History**: Bekijk alle chat sessies en berichten
- **System Prompts**: Live aanpassen van de chatbot system prompt met versioning

### Architectuur

```
┌─────────────────────────────────────────────────────────────┐
│                        Azure Cloud                          │
│                                                             │
│  ┌──────────────────┐      ┌──────────────────┐           │
│  │  Chatbot WebApp  │      │ Dashboard WebApp │           │
│  │  (Flask)         │      │  (Flask)         │           │
│  │  Port 8000       │      │  Port 8000       │           │
│  └────────┬─────────┘      └────────┬─────────┘           │
│           │                         │                      │
│           │                         │                      │
│  ┌────────▼─────────────────────────▼─────────┐           │
│  │        Azure PostgreSQL Databases           │           │
│  │  ┌──────────────┐    ┌──────────────────┐  │           │
│  │  │  irado_chat  │    │ irado_bedrijfs-  │  │           │
│  │  │              │    │   klanten        │  │           │
│  │  │ • sessions   │    │ • bedrijfsklanten│  │           │
│  │  │ • messages   │    │                  │  │           │
│  │  │ • system_    │    │                  │  │           │
│  │  │   prompts    │    │                  │  │           │
│  │  └──────────────┘    └──────────────────┘  │           │
│  └──────────────────────────────────────────────┘           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Deployment Stappen

### Optie A: Volledige Nieuwe Deployment

Als je het dashboard nog **NIET** hebt gedeployed:

```bash
cd /opt/irado-azure

# 1. Pas eerst het database schema toe
./apply-system-prompt-schema-azure.sh

# 2. Deploy het dashboard
./deploy-dashboard-to-azure.sh
```

### Optie B: Update Bestaand Dashboard

Als het dashboard al op Azure staat:

```bash
cd /opt/irado-azure

# Dashboard heeft aparte Web App, gebruik dashboard deployment script
./deploy-dashboard-to-azure.sh
```

**Voor chatbot updates:**
```bash
cd /opt/irado-azure
./deploy-to-azure.sh
```

## ⚙️ Configuratie

### Environment Variables

Het dashboard heeft de volgende environment variables nodig in Azure:

#### Chat Database (voor chat history & system prompts)
```bash
POSTGRES_HOST=irado-chat-db.postgres.database.azure.com
POSTGRES_PORT=5432
POSTGRES_DB=irado_chat
POSTGRES_USER=irado_admin
POSTGRES_PASSWORD=<your-password>
```

#### Bedrijfsklanten Database (voor KOAD data)
```bash
BEDRIJFSKLANTEN_DB_HOST=irado-bedrijfsklanten-db.postgres.database.azure.com
BEDRIJFSKLANTEN_DB_PORT=5432
BEDRIJFSKLANTEN_DB_NAME=irado_bedrijfsklanten
BEDRIJFSKLANTEN_DB_USER=irado_admin
BEDRIJFSKLANTEN_DB_PASSWORD=<your-password>
```

#### Web App Settings
```bash
WEBSITES_PORT=8000
SCM_DO_BUILD_DURING_DEPLOYMENT=false
```

### Database Schema Setup

De `system_prompts` tabel moet worden aangemaakt in de `irado_chat` database:

```sql
CREATE TABLE IF NOT EXISTS system_prompts (
    id SERIAL PRIMARY KEY,
    prompt_content TEXT NOT NULL,
    version VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_prompts_active ON system_prompts(is_active);
CREATE INDEX idx_system_prompts_version ON system_prompts(version);
```

Dit wordt automatisch uitgevoerd door `apply-system-prompt-schema-azure.sh`.

## 🏗️ Huidige Architectuur

Het Irado systeem gebruikt een **apart Web App** architectuur:

- **Chatbot Web App**: `irado-chatbot-app.azurewebsites.net` (Port 80)
- **Dashboard Web App**: `irado-dashboard-app.azurewebsites.net` (Port 8000)
- **Gedeelde Databases**: Beide apps gebruiken dezelfde PostgreSQL databases

## 📱 Dashboard Gebruik

### Toegang

- **URL**: https://irado-dashboard-app.azurewebsites.net (of je gekozen naam)
- **Geen authenticatie** (voeg toe indien gewenst)

### Features

#### 1. Bedrijfsklanten Tab

**CSV Upload:**
- Klik op "Upload CSV"
- Selecteer CSV bestand met kolommen: `KOAD-str`, `KOAD-pc`, `KOAD-huisnr`
- Upload overschrijft oude data in database

**Zoeken:**
- Typ in zoekbalk (straat, postcode, huisnummer, naam)
- Real-time search in database
- Geen data wordt standaard geladen (performance)

**Toevoegen/Bewerken:**
- Klik "Nieuwe Entry" om handmatig toe te voegen
- Klik ✏️ icoon om te bewerken
- Klik 🗑️ icoon om te verwijderen

#### 2. Chat History Tab

**Sessies bekijken:**
- Lijst van alle chat sessies
- Sorteer op datum/tijd
- Klik 👁️ icoon om volledige conversatie te zien

**Zoeken:**
- Zoek in berichten content
- Filter op datum/tijd
- Bekijk metadata per bericht

#### 3. System Prompt Tab ⭐ **NIEUW**

**Actieve Prompt:**
- Bovenaan zie je de huidige actieve system prompt
- Klik "Bewerk" om deze direct aan te passen
- Wijzigingen zijn **DIRECT** actief in de chatbot

**Prompt Versies:**
- Overzicht van alle system prompt versies
- Bekijk historie van wijzigingen
- Activeer oudere versies indien nodig

**Nieuwe Prompt Maken:**
1. Klik "Nieuwe Prompt"
2. Voer versienummer in (bijv. "2.0", "2.1")
3. Schrijf de volledige system prompt
4. ☑️ Vink "Direct activeren" aan om deze direct actief te maken
5. Klik "Opslaan"

**Prompt Bewerken:**
1. Klik ✏️ icoon bij een prompt versie
2. Pas inhoud aan
3. Update versienummer indien gewenst
4. Klik "Bijwerken"
5. ⚠️ Als dit de actieve prompt is, zijn wijzigingen direct zichtbaar!

**Prompt Activeren:**
1. Klik ✅ icoon bij een inactieve prompt
2. Bevestig activatie
3. De oude actieve prompt wordt automatisch gedeactiveerd

## 🔄 Hoe System Prompt Werkt

### Chatbot Lookup Volgorde

De chatbot zoekt de system prompt in deze volgorde:

1. **Database** (Azure PostgreSQL `irado_chat.system_prompts`)
   - Haalt actieve prompt op (`is_active = TRUE`)
   - Versie + timestamp info beschikbaar
   
2. **File Fallback** (`/app/system_prompt.txt`)
   - Als database niet beschikbaar
   - Hardcoded backup prompt
   
3. **Hardcoded Default**
   - Als alles faalt
   - Minimale functionaliteit

### Live Updates

**BELANGRIJK:** System prompt wijzigingen zijn **NIET** per direct actief omdat:
- Chatbot gebruikt caching (30 seconden)
- Bestaande chat sessies behouden hun prompt

**Om wijzigingen door te voeren:**
- **Nieuw chat sessie** zal direct nieuwe prompt gebruiken
- **Bestaande sessies** krijgen nieuwe prompt na herstart/refresh
- **Force Update**: Restart chatbot Web App in Azure Portal

```bash
# Force restart via CLI
az webapp restart --name irado-chatbot-app --resource-group irado-rg
```

## 🛠️ Troubleshooting

### Dashboard laadt niet

**Symptomen:**
- 502/503 errors
- Witte pagina
- Timeout

**Oplossingen:**
1. Check logs:
   ```bash
   az webapp log tail --name irado-dashboard-app --resource-group irado-rg
   ```

2. Verify database connectivity:
   - Check firewall rules in Azure Portal
   - Test credentials met `psql` lokaal

3. Restart Web App:
   ```bash
   az webapp restart --name irado-dashboard-app --resource-group irado-rg
   ```

### System Prompt niet zichtbaar in chatbot

**Symptomen:**
- Dashboard toont actieve prompt
- Chatbot gebruikt nog oude prompt

**Oplossingen:**
1. **Wacht 30 seconden** (cache expiry)
2. **Start nieuwe chat sessie** (open in incognito/private window)
3. **Force restart chatbot**:
   ```bash
   az webapp restart --name irado-chatbot-app --resource-group irado-rg
   ```
4. Check chatbot logs:
   ```bash
   az webapp log tail --name irado-chatbot-app --resource-group irado-rg | grep "system_prompt"
   ```

### Database verbinding fout

**Symptomen:**
- "Database connection failed"
- 500 errors bij laden van data

**Oplossingen:**
1. Verify environment variables in Azure:
   ```bash
   az webapp config appsettings list --name irado-dashboard-app --resource-group irado-rg
   ```

2. Check database firewall:
   ```bash
   # Add your IP (or Azure services)
   az postgres flexible-server firewall-rule create \
     --resource-group irado-rg \
     --name irado-chat-db \
     --rule-name AllowAzureServices \
     --start-ip-address 0.0.0.0 \
     --end-ip-address 0.0.0.0
   ```

3. Test database connection:
   ```bash
   psql -h irado-chat-db.postgres.database.azure.com \
        -U irado_admin \
        -d irado_chat \
        -c "SELECT version FROM system_prompts WHERE is_active = true;"
   ```

### CSV upload faalt

**Symptomen:**
- Upload lijkt te werken maar data verschijnt niet
- Error melding

**Oplossingen:**
1. Check CSV formaat:
   - UTF-8 encoding
   - Kolommen: `KOAD-str`, `KOAD-pc`, `KOAD-huisnr` (verplicht)
   - Geen extra spaties in kolomnamen

2. Check file size:
   - Azure heeft upload limits (standaard 10MB)
   - Split grote files indien nodig

3. Check logs voor details:
   ```bash
   az webapp log tail --name irado-dashboard-app --resource-group irado-rg
   ```

## 📈 Best Practices

### System Prompt Management

1. **Versioning:**
   - Gebruik semantic versioning (1.0, 1.1, 2.0)
   - Incrementeer major version bij grote wijzigingen
   - Incrementeer minor version bij kleine aanpassingen

2. **Testing:**
   - Maak eerst een nieuwe versie (niet direct activeren)
   - Test in een test chat sessie
   - Activeer pas na verificatie

3. **Backup:**
   - Database bevat automatisch alle versies
   - Oude prompts zijn altijd beschikbaar
   - Geen handmatige backups nodig

4. **Documentation:**
   - Noteer in versie field wat er is veranderd
   - Bijvoorbeeld: "2.1 - Added email templates"

### CSV Upload

1. **Regular Updates:**
   - Upload wekelijks of maandelijks verse data
   - Check voor duplicaten voor upload

2. **Validation:**
   - Verify data in dashboard na upload
   - Use search functie om random entries te checken

3. **Backup:**
   - Dashboard maakt automatisch backups in `/opt/irado-azure/chatbot/backups/`
   - Azure database heeft ook automatic backups

## 🔗 Resources

- **Main README**: `/opt/irado-azure/chatbot/README.md`
- **Azure Deployment Guide**: `/opt/irado-azure/AZURE_DEPLOYMENT_GUIDE.md`
- **Architecture Plan**: `/opt/irado-azure/DASHBOARD_AZURE_PLAN.md`

## 📞 Support

Bij problemen:
1. Check deze troubleshooting guide
2. Bekijk Azure Portal logs
3. Review deployment scripts voor configuratie details
4. Check database connectivity en credentials

---

**Laatste update:** 2025-10-03  
**Versie:** 1.0

