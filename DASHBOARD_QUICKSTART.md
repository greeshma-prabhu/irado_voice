# 📊 Dashboard Quick Start

## 🚀 In 3 Stappen Live

### 1️⃣ Database Schema Toepassen (1x nodig)

```bash
cd /opt/irado
./apply-system-prompt-schema-azure.sh
```

**Wat dit doet:**
- Maakt `system_prompts` tabel aan in Azure database
- Voegt indexes toe voor performance
- Trigger voor `updated_at` timestamps

**Input nodig:**
- Azure database password (wordt gevraagd)

---

### 2️⃣ Dashboard Deployen

```bash
cd /opt/irado
./deploy-dashboard-to-azure.sh
```

**Wat dit doet:**
- Bouwt Docker image voor dashboard
- Push naar Azure Container Registry
- Maakt Azure Web App (of update bestaande)
- Configureert environment variables
- Start dashboard

**Input nodig:**
- Chat database password
- Bedrijfsklanten database password

**Duur:** ~5-10 minuten

---

### 3️⃣ Gebruik Dashboard

Open in browser:
```
https://irado-dashboard-app.azurewebsites.net
```

**Tabs:**
- 📁 **Bedrijfsklanten**: Upload CSV, zoek, beheer KOAD data
- 💬 **Chat History**: Bekijk alle chat sessies
- ⚙️ **System Prompt**: 🆕 Beheer chatbot prompts LIVE!

---

## ⚙️ System Prompt Editor Gebruiken

### Nieuwe Prompt Maken

1. Ga naar "System Prompt" tab
2. Klik "Nieuwe Prompt"
3. Vul in:
   - **Versie**: bijv. "2.0"
   - **Content**: volledige system prompt tekst
   - ☑️ **Direct activeren** (optioneel)
4. Klik "Opslaan"

### Bestaande Prompt Bewerken

1. Klik ✏️ icoon bij gewenste prompt
2. Pas content aan
3. Klik "Bijwerken"
4. ⚠️ **Let op**: Als dit de actieve prompt is, is wijziging direct live!

### Prompt Activeren/Wisselen

1. Klik ✅ icoon bij inactieve prompt
2. Bevestig
3. Oude actieve prompt wordt automatisch gedeactiveerd
4. Nieuwe chatbot sessies gebruiken direct nieuwe prompt

---

## 🔄 Updates Deployen

Als je wijzigingen maakt aan dashboard code:

```bash
cd /opt/irado
./deploy-dashboard-to-azure.sh
```

**Of** als dashboard in dezelfde container zit als chatbot:

```bash
cd /opt/irado
./deploy-to-azure.sh
```

---

## 🛠️ Troubleshooting

### Dashboard laadt niet
```bash
# Check logs
az webapp log tail --name irado-dashboard-app --resource-group irado-chatbot-rg

# Restart
az webapp restart --name irado-dashboard-app --resource-group irado-chatbot-rg
```

### System Prompt wijziging niet zichtbaar in chatbot
1. Wacht 30 seconden (cache)
2. Open nieuwe chat sessie (incognito window)
3. Of force restart:
   ```bash
   az webapp restart --name irado-chatbot-app --resource-group irado-chatbot-rg
   ```

### Database connection error
```bash
# Check firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group irado-chatbot-rg \
  --name irado-db-chat

# Add Azure services if missing
az postgres flexible-server firewall-rule create \
  --resource-group irado-chatbot-rg \
  --name irado-db-chat \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

---

## 📚 Meer Info

- **Volledige Guide**: [DASHBOARD_AZURE_DEPLOYMENT.md](DASHBOARD_AZURE_DEPLOYMENT.md)
- **Azure Deployment**: [AZURE_DEPLOYMENT_GUIDE.md](AZURE_DEPLOYMENT_GUIDE.md)
- **Architecture**: [DASHBOARD_AZURE_PLAN.md](DASHBOARD_AZURE_PLAN.md)

---

**Klaar! 🎉 Je dashboard is nu live met System Prompt management!**

