# Irado Project Migration Package v2.2.0

## 📦 Package Contents

Dit package bevat het volledige Irado project met alle benodigde bestanden voor deployment op een nieuwe server.

### ✅ Inbegrepen:
- **Alle source code** (chatbot, dashboard, website)
- **Deployment scripts** met hardcoded credentials
- **Database schemas** en migration scripts
- **Docker configuratie**
- **Azure configuratie bestanden**
- **Documentatie** en quickstart guides

### 🚫 Uitgesloten:
- `venv/` (Python virtual environment)
- `__pycache__/` (Python cache bestanden)
- `.git/` (Git repository)
- `*.log` (Log bestanden)
- `tmp/` en `temp/` (Tijdelijke bestanden)

## 🚀 Quick Start

### 1. Extract Package
```bash
tar -xzf irado-project-v2.1.1.tar.gz
cd irado/
```

### 2. Run Migration Script
```bash
chmod +x MigrationStart.sh
./MigrationStart.sh
```

### 3. Azure Setup
```bash
# Login to Azure
az login

# Set subscription (if needed)
az account set --subscription <your-subscription-id>

# Login to ACR
az acr login --name irado
```

### 4. Deploy
```bash
# Deploy chatbot
./deploy-to-azure.sh

# Deploy dashboard
./deploy-dashboard-to-azure.sh

# Apply database schema
./apply-system-prompt-schema-azure.sh
```

## 🔧 Hardcoded Values

De deployment scripts bevatten de volgende hardcoded waarden:

### Database Credentials:
- **Host**: `irado-chat-db.postgres.database.azure.com`
- **Database**: `irado_chat`
- **User**: `irado_admin`
- **Password**: `lqBp6OF31+wCNXzyTMvasFrspdtL+IWPGVtooy2zjS4=`

### Azure OpenAI:
- **API Key**: `BXFgQF9udVZRqyhvapyyKmaO5MxXH5CUZb2Xf992rD99al4C4zyKJQQJ99BJACfhMk5XJ3w3AAAAACOGL8rA`
- **Endpoint**: `https://info-mgal213r-swedencentral.cognitiveservices.azure.com`
- **Deployment**: `gpt-4o`

### Authentication:
- **Username**: `irado`
- **Password**: `20Irado25!`

### Runtime Settings:
- **APP_TIMEZONE**: `Europe/Amsterdam`
- **TZ**: `Europe/Amsterdam`

## 📋 Project Status

- **Version**: 2.2.0
- **Status**: Fully operational on Azure
- **Componenten**: 
  - ✅ Chatbot (https://irado-chatbot-app.azurewebsites.net)
  - ✅ Dashboard (https://irado-dashboard-app.azurewebsites.net)
  - ✅ Database (PostgreSQL met alle tabellen incl. `bedrijfsklanten`, `system_prompts`, `dashboard_logs`)
  - ✅ System prompt v2.0 (mix-detectie & tool-schema's) actief

## 🔍 Verification

Na deployment, test de endpoints:

```bash
# Health check
curl https://irado-chatbot-app.azurewebsites.net/health

# Chat API test
curl -X POST https://irado-chatbot-app.azurewebsites.net/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'irado:20Irado25!' | base64)" \
  -d '{"chatInput": "Test", "sessionId": "test-123", "action": "sendMessage", "source": "website"}'
```

## 📚 Documentation

- **Quick Start**: `START_HIER.txt`
- **Azure Setup**: `AZURE_QUICKSTART.md`
- **Dashboard**: `DASHBOARD_QUICKSTART.md`
- **Deployment Guide**: `AZURE_DEPLOYMENT_GUIDE.md`

## 🆘 Troubleshooting

### Common Issues:

1. **Docker build fails**: Check if Docker is running
2. **Azure login fails**: Run `az login` first
3. **Database connection fails**: Check firewall rules
4. **API returns 500**: Check logs with `az webapp log tail`

### Log Commands:
```bash
# Chatbot logs
az webapp log tail --name irado-chatbot-app --resource-group irado-rg

# Dashboard logs  
az webapp log tail --name irado-dashboard-app --resource-group irado-rg
```

## 📞 Support

- **Version**: 2.2.0
- **Last Updated**: $(date)
- **Status**: Production Ready

---

### 🔄 Release highlights v2.2.0

- Per-route QML e-mails via `send_email_to_team` en één klantmail via `send_email_to_customer`
- Alle containers draaien met `APP_TIMEZONE=Europe/Amsterdam` (Amsterdam-tijd in logs)
- Dashboard logviewer toont volledige JSON voor toolcalls/e-mails
- Nieuwe system prompt (`chatbot/prompts/system_prompt.txt`) beschrijft volledige workflow

**Ready to deploy! 🚀**
