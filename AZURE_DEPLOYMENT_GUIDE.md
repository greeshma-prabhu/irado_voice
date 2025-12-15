# Azure Deployment Guide - Irado Chatbot

**Versie:** 1.0  
**Laatst bijgewerkt:** 3 Oktober 2025  
**Huidige deployment:** `irado.azurecr.io/chatbot:v2.1.2`

---

## 📋 Inhoudsopgave

1. [Quick Reference](#quick-reference)
2. [Deployment Proces](#deployment-proces)
3. [Troubleshooting](#troubleshooting)
4. [Best Practices](#best-practices)
5. [Rollback Procedure](#rollback-procedure)
6. [Environment Variables](#environment-variables)

---

## 🚀 Quick Reference

### Snelle Deployment (3 minuten)

```bash
# 1. Navigeer naar project directory
cd /opt/irado-azure

# 2. Build nieuwe Docker image met unique tag
TAG="v$(date +%s)"
docker build -f Dockerfile.chatbot -t irado.azurecr.io/chatbot:$TAG .

# 3. Push naar Azure Container Registry
az acr login --name irado
docker push irado.azurecr.io/chatbot:$TAG

# 4. Update Web App (ZONDER restart - sneller!)
az webapp config set \
  --resource-group irado-rg \
  --name irado-chatbot-app \
  --linux-fx-version "DOCKER|irado.azurecr.io/chatbot:$TAG"

# 5. Wacht 60-90 seconden en test
sleep 60
curl -sS https://irado-chatbot-app.azurewebsites.net/health
```

### Huidige Configuratie

| Component | Waarde |
|-----------|--------|
| Resource Group | `irado-rg` |
| Web App | `irado-chatbot-app` |
| Container Registry | `irado.azurecr.io` |
| Huidige Image | `irado.azurecr.io/chatbot:v2.1.2` |
| Region | West Europe |
| Port | 80 |

---

## 📦 Deployment Proces

### Stap 1: Lokale Voorbereiding

```bash
# Test je changes lokaal (optioneel maar aangeraden)
cd /opt/irado-azure/chatbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py  # Test op http://localhost:80
```

### Stap 2: Docker Image Bouwen

```bash
cd /opt/irado-azure

# Gebruik ALTIJD een unique tag (timestamp of versienummer)
TAG="v$(date +%s)"
# Of gebruik semantic versioning:
# TAG="v1.2.3"

# Build de image
docker build -f Dockerfile.chatbot \
  -t irado.azurecr.io/chatbot:$TAG .

# Controleer of de build succesvol was
docker images | grep irado.azurecr.io/chatbot
```

**⚠️ Belangrijk:** 
- Gebruik NOOIT dezelfde tag twee keer
- Tag met timestamp voorkomt cache problemen
- Voorbeeld goede tags: `v1759517954`, `v1.2.3`, `fix-email-v1`

### Stap 3: Push naar Azure Container Registry

```bash
# Login (blijft 3 uur geldig)
az acr login --name irado

# Push de image
docker push irado.azurecr.io/chatbot:$TAG

# Verificeer dat de image in ACR staat
az acr repository show-tags --name irado --repository chatbot --orderby time_desc --top 5
```

### Stap 4: Update Web App

**Methode 1: Zonder Restart (AANBEVOLEN - 60 sec)**
```bash
# Update alleen de image configuratie
az webapp config set \
  --resource-group irado-rg \
  --name irado-chatbot-app \
  --linux-fx-version "DOCKER|irado.azurecr.io/chatbot:$TAG"

# Azure laadt automatisch de nieuwe container
# Wacht 60-90 seconden
sleep 60
```

**Methode 2: Met Restart (als Methode 1 niet werkt)**
```bash
# Stop, update, start
az webapp stop --resource-group irado-rg --name irado-chatbot-app
az webapp config set \
  --resource-group irado-rg \
  --name irado-chatbot-app \
  --linux-fx-version "DOCKER|irado.azurecr.io/chatbot:$TAG"
az webapp start --resource-group irado-rg --name irado-chatbot-app

# Wacht langer voor restart
sleep 90
```

### Stap 5: Verificatie

```bash
# Check health endpoint
curl -sS https://irado-chatbot-app.azurewebsites.net/health

# Verwachte output:
# {
#   "status": "healthy",
#   "timestamp": "2025-10-03T19:00:00.000000",
#   "version": "1.0.0"
# }

# Test chat API
curl -X POST "https://irado-chatbot-app.azurewebsites.net/api/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic aXJhZG86MjBJcmFkbzI1IQ==" \
  -d '{"sessionId": "test123", "action": "sendMessage", "chatInput": "hoi"}' \
  --max-time 30

# Check logs voor errors
az webapp log tail --resource-group irado-rg --name irado-chatbot-app
```

---

## 🔧 Troubleshooting

### Probleem: Container start niet / Timeout

**Symptomen:**
- Health endpoint reageert niet na 2+ minuten
- `curl: (28) Operation timed out`

**Oplossingen:**

1. **Check de logs EERST:**
```bash
az webapp log download --resource-group irado-rg \
  --name irado-chatbot-app --log-file /tmp/debug.zip
cd /tmp && unzip -o debug.zip
tail -n 100 LogFiles/*_default_docker.log
```

2. **Veelvoorkomende oorzaken:**
- ❌ Python module ontbreekt → Check `requirements.txt`
- ❌ Syntax error in code → Zie traceback in logs
- ❌ Poort conflict → Moet 80 zijn (zie Dockerfile)
- ❌ Missing environment variables → Check app settings

3. **Force nieuwe container:**
```bash
# Stop en verwijder alles
az webapp stop --resource-group irado-rg --name irado-chatbot-app

# Wacht 10 seconden
sleep 10

# Start opnieuw met nieuwe image
az webapp config set --resource-group irado-rg \
  --name irado-chatbot-app \
  --linux-fx-version "DOCKER|irado.azurecr.io/chatbot:$TAG"
az webapp start --resource-group irado-rg --name irado-chatbot-app

# Wacht langer
sleep 120
```

### Probleem: Azure gebruikt oude container

**Symptomen:**
- Nieuwe code changes zijn niet zichtbaar
- Oude errors blijven terugkomen
- Logs tonen oude timestamp

**Oplossing:**

```bash
# 1. Gebruik ALTIJD een nieuwe unique tag
TAG="force-$(date +%s)"

# 2. Tag de image lokaal NIEUW
docker tag irado.azurecr.io/chatbot:final-complete-v1 irado.azurecr.io/chatbot:$TAG

# 3. Push met nieuwe tag
docker push irado.azurecr.io/chatbot:$TAG

# 4. Update config
az webapp config set --resource-group irado-rg \
  --name irado-chatbot-app \
  --linux-fx-version "DOCKER|irado.azurecr.io/chatbot:$TAG"

# 5. Force restart
az webapp restart --resource-group irado-rg --name irado-chatbot-app
```

### Probleem: "max_tokens" Error

**Symptoom:**
```
Error code: 400 - max_tokens or model output limit was reached
```

**Oplossing:**
```python
# In /opt/irado/chatbot/config.py
OPENAI_MAX_TOKENS = 2000  # Verhoog naar 2000 of hoger
```

### Probleem: Database Connection Errors

**Oplossing:**
```bash
# Check of databases bestaan
az postgres flexible-server db list \
  --resource-group irado-rg \
  --server-name irado-chat-db

az postgres flexible-server db list \
  --resource-group irado-rg \
  --server-name irado-bedrijfsklanten-db

# Check firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group irado-rg \
  --server-name irado-chat-db
```

---

## ✅ Best Practices

### 1. Versiebeheer

```bash
# ✅ GOED: Gebruik semantic versioning
TAG="v1.2.3"

# ✅ GOED: Gebruik timestamps
TAG="v$(date +%s)"

# ✅ GOED: Gebruik descriptieve tags
TAG="fix-email-bug-v1"

# ❌ SLECHT: Hergebruik van tags
TAG="latest"  # Cache problemen!
TAG="v1"      # Moeilijk te tracken
```

### 2. Testing Strategy

```bash
# Test ALTIJD lokaal eerst
docker build -f Dockerfile.chatbot -t test-local .
docker run --rm -p 8080:80 \
  -e AZURE_OPENAI_API_KEY="test" \
  -e POSTGRES_HOST="test" \
  test-local

# Test in browser: http://localhost:8080/health
```

### 3. Deployment Timing

```bash
# Check huidige container status VOOR deployment
az webapp show --resource-group irado-rg \
  --name irado-chatbot-app \
  --query "state" -o tsv

# Als "Running" → Gewoon updaten (Methode 1)
# Als "Stopped" → Eerst starten
```

### 4. Log Monitoring

```bash
# Real-time logs (gebruik Ctrl+C om te stoppen)
az webapp log tail --resource-group irado-rg \
  --name irado-chatbot-app

# Download logs voor analyse
az webapp log download --resource-group irado-rg \
  --name irado-chatbot-app \
  --log-file logs-$(date +%Y%m%d-%H%M).zip
```

### 5. Environment Variables Checken

```bash
# List alle app settings
az webapp config appsettings list \
  --resource-group irado-rg \
  --name irado-chatbot-app \
  --query "[].{name:name, value:value}" -o table

# Update een specifieke setting
az webapp config appsettings set \
  --resource-group irado-rg \
  --name irado-chatbot-app \
  --settings OPENAI_MAX_TOKENS=2000
```

---

## 🔄 Rollback Procedure

Als een deployment faalt, rollback naar vorige versie:

```bash
# 1. Check welke images beschikbaar zijn
az acr repository show-tags \
  --name irado \
  --repository chatbot \
  --orderby time_desc \
  --top 10

# 2. Kies een werkende versie (bijv. final-complete-v1)
PREVIOUS_TAG="final-complete-v1"

# 3. Rollback
az webapp stop --resource-group irado-rg --name irado-chatbot-app
az webapp config set \
  --resource-group irado-rg \
  --name irado-chatbot-app \
  --linux-fx-version "DOCKER|irado.azurecr.io/chatbot:$PREVIOUS_TAG"
az webapp start --resource-group irado-rg --name irado-chatbot-app

# 4. Verificatie
sleep 60
curl -sS https://irado-chatbot-app.azurewebsites.net/health
```

---

## 🔐 Environment Variables

### Vereiste Variabelen

| Variable | Beschrijving | Voorbeeld |
|----------|-------------|-----------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | `BXFgQF9udVZRqyhvap...` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | `https://info-mgal213r...` |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment naam | `o4-mini` |
| `AZURE_OPENAI_API_VERSION` | API versie | `2025-01-01-preview` |
| `POSTGRES_HOST` | Chat DB host | `irado-chat-db.postgres.database.azure.com` |
| `POSTGRES_DB` | Chat database naam | `irado_chat` |
| `POSTGRES_USER` | Database user | `irado_admin` |
| `POSTGRES_PASSWORD` | Database password | `****` |
| `BEDRIJFSKLANTEN_DB_HOST` | Bedrijfsklanten DB host | `irado-bedrijfsklanten-db...` |
| `BEDRIJFSKLANTEN_DB_NAME` | Bedrijfsklanten DB naam | `irado_bedrijfsklanten` |
| `BEDRIJFSKLANTEN_DB_USER` | Database user | `irado_admin` |
| `BEDRIJFSKLANTEN_DB_PASSWORD` | Database password | `****` |

### Update Environment Variables

```bash
# Single variable
az webapp config appsettings set \
  --resource-group irado-rg \
  --name irado-chatbot-app \
  --settings OPENAI_MAX_TOKENS=2000

# Multiple variables
az webapp config appsettings set \
  --resource-group irado-rg \
  --name irado-chatbot-app \
  --settings \
    AZURE_OPENAI_API_KEY="new-key" \
    POSTGRES_PASSWORD="new-password"

# Na environment variable changes: RESTART VEREIST
az webapp restart --resource-group irado-rg --name irado-chatbot-app
```

---

## 📊 Monitoring & Metrics

### Health Checks

```bash
# Basic health
curl https://irado-chatbot-app.azurewebsites.net/health

# Readiness check (met config validation)
curl https://irado-chatbot-app.azurewebsites.net/ready

# Homepage
curl https://irado-chatbot-app.azurewebsites.net/
```

### Performance Metrics

```bash
# Check app service metrics
az monitor metrics list \
  --resource /subscriptions/c05f7490-d7a0-4b49-ab02-aeb0fd35b82e/resourceGroups/irado-rg/providers/Microsoft.Web/sites/irado-chatbot-app \
  --metric "Requests" \
  --start-time $(date -u -d '1 hour ago' '+%Y-%m-%dT%H:%M:%S')Z \
  --end-time $(date -u '+%Y-%m-%dT%H:%M:%S')Z \
  --interval PT1M
```

---

## 🎯 Deployment Checklist

Gebruik deze checklist voor elke deployment:

- [ ] Code changes getest lokaal
- [ ] `requirements.txt` up-to-date
- [ ] Unique tag gekozen
- [ ] Docker image gebouwd zonder errors
- [ ] Image gepushed naar ACR
- [ ] Backup van huidige tag gemaakt (voor rollback)
- [ ] Web App config geupdatet
- [ ] 60-90 seconden gewacht
- [ ] Health endpoint getest
- [ ] Chat functionaliteit getest
- [ ] Logs gecheckt voor errors
- [ ] Performance metrics bekeken

---

## 📝 Deployment Log Template

Bewaar deze info voor elke deployment:

```
Deployment: [DATE/TIME]
Tag: [TAG_NAME]
Changes: [BESCHRIJVING]
Previous Tag: [PREVIOUS_TAG]
Status: [SUCCESS/FAILED]
Issues: [EVENTUELE PROBLEMEN]
Rollback: [JA/NEE]
```

Voorbeeld:
```
Deployment: 2025-10-03 19:00
Tag: final-complete-v1
Changes: Fixed email functionality, increased max_tokens to 2000
Previous Tag: fix-postcode-v2
Status: SUCCESS
Issues: Initial timeout, resolved after 90s wait
Rollback: NEE
```

---

## 🆘 Snelle Hulp

### Als NIETS werkt:

```bash
# Nuclear option: Volledig opnieuw starten
az webapp stop --resource-group irado-rg --name irado-chatbot-app
sleep 30
az webapp start --resource-group irado-rg --name irado-chatbot-app
sleep 120
curl https://irado-chatbot-app.azurewebsites.net/health
```

### Contact Info

- Azure Portal: https://portal.azure.com
- Resource Group: `irado-rg`
- Subscription: `c05f7490-d7a0-4b49-ab02-aeb0fd35b82e`

---

**📌 Tip:** Bookmark deze guide en gebruik het bij elke deployment!




