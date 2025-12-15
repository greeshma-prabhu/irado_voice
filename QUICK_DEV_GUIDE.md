# 🚀 Quick Development Guide - Irado Project

## Probleem: Deployment duurt te lang (~30 min per wijziging)

### ✅ SNELLE DEVELOPMENT OPTIES:

---

## Optie 1: Local Development met Azure DB (AANBEVOLEN) ⚡

**Snelheid:** Direct testen (< 5 seconden)  
**Gebruik:** Voor kleine fixes, testing, debugging

### Setup:

```bash
cd /opt/irado/chatbot

# 1. Activeer venv (als je die hebt)
source venv/bin/activate  # of: python3 -m venv venv && source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables voor Azure DB
export POSTGRES_HOST="irado-chat-db.postgres.database.azure.com"
export POSTGRES_PORT="5432"
export POSTGRES_DB="irado_chat"
export POSTGRES_USER="irado_admin"
export POSTGRES_PASSWORD="lqBp6OF31+wCNXzyTMvasFrspdtL+IWPGVtooy2zjS4="

export BEDRIJFSKLANTEN_DB_HOST="irado-bedrijfsklanten-db.postgres.database.azure.com"
export BEDRIJFSKLANTEN_DB_PORT="5432"
export BEDRIJFSKLANTEN_DB_NAME="irado_bedrijfsklanten"
export BEDRIJFSKLANTEN_DB_USER="irado_admin"
export BEDRIJFSKLANTEN_DB_PASSWORD="lqBp6OF31+wCNXzyTMvasFrspdtL+IWPGVtooy2zjS4="

# Azure OpenAI credentials
export AZURE_OPENAI_ENDPOINT="https://info-mgal213r-swedencentral.cognitiveservices.azure.com"
export AZURE_OPENAI_KEY="BXFgQF9udVZRqyhvapyyKmaO5MxXH5CUZb2Xf992rD99al4C4zyKJQQJ99BJACfhMk5XJ3w3AAAAACOGL8rA"
export AZURE_OPENAI_DEPLOYMENT="o4-mini"

# SMTP (use fake for testing or real)
export SMTP_HOST="localhost"  # of: mail.mainfact.ai
export SMTP_PORT="1025"       # of: 587

# 4. Run chatbot locally
python app.py
# → Runs on http://localhost:8080

# 5. Test met curl
curl -X POST http://localhost:8080/api/chat \
  -u irado:20Irado25! \
  -H "Content-Type: application/json" \
  -d '{"message": "hallo", "session_id": "test123"}'
```

### Voor Dashboard:

```bash
cd /opt/irado/chatbot/dashboard

# Run dashboard locally
python dashboard.py
# → Runs on http://localhost:3255

# Open in browser: http://localhost:3255
```

**Voordeel:** Direct testen, logs realtime zien, breakpoints zetten!

---

## Optie 2: Azure Console SSH/Exec (MEDIUM) 🔧

**Snelheid:** ~5 minuten  
**Gebruik:** Kleine file edits direct in container

### Via Azure Portal:

1. Ga naar: https://portal.azure.com
2. Open: `irado-chatbot-app` (of `irado-dashboard-app`)
3. Ga naar: **Development Tools** → **SSH** (or **Console**)
4. Je hebt nu shell access in de container!

```bash
# In Azure SSH console:
cd /app
ls -la

# Edit files direct (vi/nano usually not available, maar je kunt cat/echo gebruiken)
cat ai_service.py  # bekijk file

# Restart de app (van buiten via Azure CLI):
az webapp restart --name irado-chatbot-app --resource-group irado-rg
```

**Nadeel:** Geen vi/nano usually, changes niet persistent

---

## Optie 3: Hot-Reload Docker Container (LOCAL) 🔥

**Snelheid:** ~30 seconden per wijziging  
**Gebruik:** Test Docker setup lokaal

```bash
cd /opt/irado/chatbot

# Run met volume mount (changes meteen zichtbaar)
docker run -it --rm \
  -p 8080:8080 \
  -v $(pwd):/app \
  -e POSTGRES_HOST="irado-chat-db.postgres.database.azure.com" \
  -e POSTGRES_PASSWORD="lqBp6OF31+wCNXzyTMvasFrspdtL+IWPGVtooy2zjS4=" \
  -e AZURE_OPENAI_KEY="BXFgQF9udVZRqyhvapyyKmaO5MxXH5CUZb2Xf992rD99al4C4zyKJQQJ99BJACfhMk5XJ3w3AAAAACOGL8rA" \
  -e AZURE_OPENAI_ENDPOINT="https://info-mgal213r-swedencentral.cognitiveservices.azure.com" \
  irado-dashboard:latest
```

**Voordeel:** Test Docker setup, maar met live code reload

---

## Optie 4: Azure Web App Deploy (SLOW - only for production) 🐌

**Snelheid:** 30+ minuten  
**Gebruik:** Alleen voor final deployments

```bash
cd /opt/irado
./deploy-to-azure.sh
```

---

## 🛠️ RECOMMENDED WORKFLOW:

### Voor kleine fixes/testing:
1. **LOCAL DEVELOPMENT** (Optie 1) - test lokaal met Azure DB
2. Verify het werkt
3. Commit code
4. Deploy naar Azure (Optie 4) alleen als het lokaal werkt

### Voor debugging in production:
1. **Azure Console SSH** (Optie 2) - bekijk logs, check files
2. Download logs: `az webapp log download`
3. Fix lokaal, test, dan deploy

---

## 📋 DEBUGGING TIPS:

### Chatbot Logs (realtime):
```bash
# Tail logs
az webapp log tail --name irado-chatbot-app --resource-group irado-rg

# Download all logs
az webapp log download --name irado-chatbot-app --resource-group irado-rg --log-file logs.zip
```

### Dashboard Logs:
```bash
az webapp log tail --name irado-dashboard-app --resource-group irado-rg
```

### Database Check:
```bash
PGPASSWORD="lqBp6OF31+wCNXzyTMvasFrspdtL+IWPGVtooy2zjS4=" psql \
  -h irado-chat-db.postgres.database.azure.com \
  -p 5432 \
  -U irado_admin \
  -d irado_chat \
  -c "SELECT * FROM system_prompts WHERE is_active = true;"
```

---

## 🔥 INSTANT TEST SETUP:

Maak een test script:

```bash
cat > /opt/irado/quick-test.sh << 'EOF'
#!/bin/bash
cd /opt/irado/chatbot

# Export all env vars
export POSTGRES_HOST="irado-chat-db.postgres.database.azure.com"
export POSTGRES_PASSWORD="lqBp6OF31+wCNXzyTMvasFrspdtL+IWPGVtooy2zjS4="
export AZURE_OPENAI_KEY="BXFgQF9udVZRqyhvapyyKmaO5MxXH5CUZb2Xf992rD99al4C4zyKJQQJ99BJACfhMk5XJ3w3AAAAACOGL8rA"
export AZURE_OPENAI_ENDPOINT="https://info-mgal213r-swedencentral.cognitiveservices.azure.com"
export AZURE_OPENAI_DEPLOYMENT="o4-mini"
export SMTP_HOST="localhost"
export SMTP_PORT="1025"

echo "🚀 Starting chatbot locally..."
echo "📍 Access at: http://localhost:8080"
echo ""

python app.py
EOF

chmod +x /opt/irado/quick-test.sh
```

Dan gebruik je gewoon:
```bash
/opt/irado/quick-test.sh
```

---

## 📊 PERFORMANCE COMPARISON:

| Method | Time | Best For |
|--------|------|----------|
| Local Dev | 5 sec | Daily development, testing fixes |
| Docker Local | 30 sec | Docker testing |
| Azure SSH | 5 min | Quick production checks |
| Azure Deploy | 30 min | Production deployments only |

---

**TIP:** Gebruik local development voor 95% van je werk, deploy alleen naar Azure als alles lokaal werkt! 🎯

