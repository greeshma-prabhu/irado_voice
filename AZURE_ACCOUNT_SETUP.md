# 🔐 AZURE ACCOUNT SETUP VOOR IRADO

**Complete guide voor het aanmaken van een Azure account met alle benodigde permissies**

---

## 📋 STAP 1: AZURE ACCOUNT AANMAKEN

### A. Nieuw Azure Account
1. **Ga naar:** https://azure.microsoft.com/nl-nl/
2. **Klik:** "Gratis account maken" of "Start gratis"
3. **Vul in:**
   - Email adres (bijvoorbeeld: `tech@irado.nl`)
   - Telefoonnummer
   - Creditcard (voor verificatie, €0 kosten eerste maand)
   - Bedrijfsnaam: **Irado**
   - Land: Nederland

4. **Kies subscription type:**
   - **Free Trial** (eerste 30 dagen €170 gratis credits)
   - Of direct **Pay-As-You-Go** subscription

---

## 💰 SUBSCRIPTION & BILLING

### B. Azure Subscription Aanmaken

Na account aanmaak heb je automatisch een subscription. Check:

```bash
az account list --output table
```

**Belangrijk:** Noteer de **Subscription ID** - deze heb je nodig!

### C. Betaling Instellen

1. **Azure Portal:** https://portal.azure.com
2. **Navigeer naar:** "Cost Management + Billing"
3. **Billing profile:** Vul bedrijfsgegevens in
4. **Payment method:** Creditcard of factuur (vanaf €100/maand)
5. **Budget alerts instellen:**
   - Ga naar "Cost Management" → "Budgets"
   - Maak budget alert: €100/maand
   - Alert bij 80%, 90%, 100%

---

## 👤 STAP 2: SERVICE PRINCIPAL AANMAKEN (voor deployment automation)

### Optie A: Via Azure Portal (Makkelijk)

1. **Open Azure Portal:** https://portal.azure.com
2. **Zoek:** "Azure Active Directory" (of "Microsoft Entra ID")
3. **Ga naar:** "App registrations"
4. **Klik:** "+ New registration"
5. **Vul in:**
   - Name: `irado-deployment-bot`
   - Supported account types: "Single tenant"
   - Redirect URI: (leeg laten)
6. **Klik:** "Register"

7. **Noteer deze waarden:**
   - **Application (client) ID**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
   - **Directory (tenant) ID**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

8. **Maak client secret:**
   - Ga naar "Certificates & secrets"
   - Klik "+ New client secret"
   - Description: `deployment-secret`
   - Expires: 24 months
   - Klik "Add"
   - **Kopieer de "Value"** (kan je maar 1× zien!)

### Optie B: Via Azure CLI (Snel)

```bash
# Login
az login

# Maak service principal met Contributor role
az ad sp create-for-rbac \
  --name "irado-deployment-bot" \
  --role Contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID

# Output (BEWAAR DIT GOED!):
# {
#   "appId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",        <- CLIENT_ID
#   "displayName": "irado-deployment-bot",
#   "password": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",          <- CLIENT_SECRET
#   "tenant": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"         <- TENANT_ID
# }
```

---

## 🔑 STAP 3: PERMISSIES TOEKENNEN

### A. Contributor Role (minimum vereist)

```bash
# Check huidige subscription
az account show --query id -o tsv

# Assign Contributor role aan service principal
az role assignment create \
  --assignee YOUR_APP_ID \
  --role "Contributor" \
  --scope /subscriptions/YOUR_SUBSCRIPTION_ID
```

### B. Extra Rollen (optioneel maar aangeraden)

```bash
# Voor Key Vault operaties
az role assignment create \
  --assignee YOUR_APP_ID \
  --role "Key Vault Administrator" \
  --scope /subscriptions/YOUR_SUBSCRIPTION_ID

# Voor Container Registry
az role assignment create \
  --assignee YOUR_APP_ID \
  --role "AcrPush" \
  --scope /subscriptions/YOUR_SUBSCRIPTION_ID
```

### C. Verificatie

```bash
# Check toegewezen rollen
az role assignment list \
  --assignee YOUR_APP_ID \
  --output table
```

**Verwacht:**
```
Principal               Role                Scope
----------------------  ------------------  ---------------------------------
irado-deployment-bot    Contributor         /subscriptions/xxx...
```

---

## 🌍 STAP 4: RESOURCE GROUP AANMAKEN

### Via Portal:
1. **Azure Portal** → "Resource groups"
2. **Klik:** "+ Create"
3. **Vul in:**
   - Subscription: (jouw subscription)
   - Resource group: `irado-rg`
   - Region: `North Europe` (Amsterdam datacenter)
4. **Tags** (optioneel):
   - Environment: `production`
   - Project: `irado-chatbot`
5. **Review + Create**

### Via CLI:

```bash
# Maak resource group
az group create \
  --name irado-rg \
  --location northeurope \
  --tags Environment=production Project=irado-chatbot

# Verificatie
az group show --name irado-rg --output table
```

---

## 🐳 STAP 5: AZURE CLI CONFIGUREREN (lokaal)

### A. Installeer Azure CLI (als nog niet gedaan)

**Linux/WSL:**
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

**macOS:**
```bash
brew update && brew install azure-cli
```

**Windows:**
Download van: https://aka.ms/installazurecliwindows

### B. Login met Service Principal

```bash
# Login met credentials
az login --service-principal \
  --username YOUR_APP_ID \
  --password YOUR_CLIENT_SECRET \
  --tenant YOUR_TENANT_ID

# Set default subscription
az account set --subscription YOUR_SUBSCRIPTION_ID

# Verificatie
az account show
```

### C. Alternatief: Login met Browser (voor developers)

```bash
# Normale login (opent browser)
az login

# Select subscription
az account set --subscription YOUR_SUBSCRIPTION_ID
```

---

## 📝 STAP 6: CREDENTIALS OPSLAAN

### Environment Variables Setup

Maak file: `/opt/irado/.azure-credentials`

```bash
# Azure Subscription
export AZURE_SUBSCRIPTION_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export AZURE_TENANT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Service Principal (deployment bot)
export AZURE_CLIENT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export AZURE_CLIENT_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Resource Group
export AZURE_RESOURCE_GROUP="irado-rg"
export AZURE_LOCATION="northeurope"

# Container Registry
export AZURE_CONTAINER_REGISTRY="irado"
```

**Source deze file:**
```bash
source /opt/irado/.azure-credentials
```

**Of voeg toe aan `.bashrc` / `.zshrc`:**
```bash
echo "source /opt/irado/.azure-credentials" >> ~/.bashrc
```

### ⚠️ SECURITY: Never commit credentials!

```bash
# Voeg toe aan .gitignore
echo ".azure-credentials" >> /opt/irado/.gitignore
echo "*.env" >> /opt/irado/.gitignore
```

---

## 🚀 STAP 7: TEST DEPLOYMENT

### A. Test Azure CLI Access

```bash
# List resource groups
az group list --output table

# List locations
az account list-locations --query "[?displayName=='North Europe']" --output table

# Test creating a resource (test storage account)
az storage account check-name --name iradotest123
```

### B. Test Container Registry Access

```bash
# Check if ACR exists (should fail if not created yet)
az acr show --name irado --resource-group irado-rg 2>/dev/null \
  && echo "✅ ACR exists" \
  || echo "⚠️ ACR not yet created (will be created on first deploy)"
```

### C. Run Full Deployment Test

```bash
cd /opt/irado

# Dit script zal ALLES aanmaken:
# - Container Registry
# - PostgreSQL Database
# - App Service Plans
# - Web Apps
# - Storage Account
# - Key Vault (indien nodig)

./deploy-to-azure.sh
```

**Eerste deployment duurt ~10-15 minuten** en maakt alle resources aan.

---

## 📊 STAP 8: MONITORING & COST MANAGEMENT

### A. Cost Alerts Instellen

1. **Portal:** https://portal.azure.com
2. **Zoek:** "Cost Management + Billing"
3. **Ga naar:** "Cost alerts"
4. **Maak alert:**
   - Name: `irado-monthly-budget`
   - Budget amount: €100
   - Alert thresholds: 50%, 80%, 100%
   - Alert recipients: `tech@irado.nl`

### B. Resource Tags (voor cost tracking)

Alle resources hebben automatisch tags:
- `Project: irado-chatbot`
- `Environment: production`

View costs per tag:
```bash
az consumption usage list \
  --start-date 2025-10-01 \
  --end-date 2025-10-31 \
  --query "[?tags.Project=='irado-chatbot']" \
  --output table
```

### C. Cost Analysis

**Portal:** Cost Management → Cost analysis → Group by: Resource / Service

**CLI:**
```bash
# Current month costs
az consumption usage list \
  --start-date $(date -d "$(date +%Y-%m-01)" +%Y-%m-%d) \
  --end-date $(date +%Y-%m-%d) \
  --query "sum([].pretaxCost)" \
  --output tsv
```

---

## 🔒 STAP 9: SECURITY BEST PRACTICES

### A. Enable Azure Defender (optioneel, €15/maand)

```bash
az security pricing create \
  --name VirtualMachines \
  --tier Standard
```

### B. Enable Activity Logs

Automatisch enabled. View via:
```bash
az monitor activity-log list \
  --resource-group irado-rg \
  --offset 1d
```

### C. Access Reviews

Regelmatig checken:
```bash
# Wie heeft toegang tot resources?
az role assignment list \
  --resource-group irado-rg \
  --output table
```

---

## 👥 STAP 10: TEAM MEMBERS TOEVOEGEN (optioneel)

### A. Uitnodigen als Guest User

1. **Azure Portal** → "Azure Active Directory"
2. **Users** → "+ New guest user"
3. **Email:** `developer@example.com`
4. **Role:** Reader, Contributor, of Owner

### B. Via CLI

```bash
az ad user create \
  --display-name "Irado Developer" \
  --password "TempPassword123!" \
  --user-principal-name developer@YOURDOMAIN.onmicrosoft.com

# Assign role
az role assignment create \
  --assignee developer@YOURDOMAIN.onmicrosoft.com \
  --role "Contributor" \
  --resource-group irado-rg
```

---

## ✅ CHECKLIST: IS ALLES KLAAR?

### Account Setup
- [ ] Azure account aangemaakt
- [ ] Subscription actief (Pay-As-You-Go of Trial)
- [ ] Betaling ingesteld
- [ ] Budget alerts geconfigureerd (€100/maand)

### Service Principal
- [ ] Service Principal aangemaakt (`irado-deployment-bot`)
- [ ] Client ID bewaard
- [ ] Client Secret bewaard
- [ ] Tenant ID bewaard
- [ ] Contributor role toegekend

### Resource Group
- [ ] Resource group `irado-rg` aangemaakt
- [ ] Locatie: North Europe
- [ ] Tags ingesteld

### Azure CLI
- [ ] Azure CLI geïnstalleerd
- [ ] Ingelogd met service principal of browser
- [ ] Default subscription ingesteld
- [ ] Credentials veilig opgeslagen in `.azure-credentials`
- [ ] `.azure-credentials` toegevoegd aan `.gitignore`

### Testing
- [ ] `az group list` werkt
- [ ] Test deployment succesvol
- [ ] Resources zichtbaar in portal

### Monitoring
- [ ] Cost alerts ingesteld
- [ ] Email notificaties geconfigureerd
- [ ] Activity logs enabled

---

## 📞 CREDENTIALS OVERZICHT

**Bewaar deze informatie VEILIG (password manager!):**

```
AZURE ACCOUNT
=============
Email: tech@irado.nl
Subscription ID: [van az account show]
Tenant ID: [van az account show]

SERVICE PRINCIPAL (deployment bot)
==================================
Name: irado-deployment-bot
Application (Client) ID: [van app registration]
Client Secret: [van certificates & secrets]
Role: Contributor
Scope: /subscriptions/[subscription-id]

RESOURCE GROUP
==============
Name: irado-rg
Location: North Europe
Subscription: [subscription name]

CONTAINER REGISTRY
==================
Name: irado.azurecr.io
Login server: irado.azurecr.io
Admin enabled: Yes
```

---

## 🚨 TROUBLESHOOTING

### "Insufficient permissions"
```bash
# Check je role assignments
az role assignment list --assignee YOUR_APP_ID --output table

# Assign missing role
az role assignment create \
  --assignee YOUR_APP_ID \
  --role "Contributor" \
  --scope /subscriptions/YOUR_SUBSCRIPTION_ID
```

### "Subscription not found"
```bash
# List alle subscriptions
az account list --output table

# Set correct subscription
az account set --subscription YOUR_SUBSCRIPTION_ID
```

### "Resource provider not registered"
```bash
# Register required providers
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.DBforPostgreSQL
az provider register --namespace Microsoft.Web
az provider register --namespace Microsoft.Storage
az provider register --namespace Microsoft.KeyVault

# Check status
az provider list --query "[?registrationState=='Registered'].namespace" --output table
```

### "Quota exceeded"
```bash
# Check quotas
az vm list-usage --location northeurope --output table

# Request quota increase via portal:
# Help + Support → New support request → Service and subscription limits (quotas)
```

---

## 📚 NUTTIGE LINKS

- **Azure Portal:** https://portal.azure.com
- **Azure CLI Docs:** https://docs.microsoft.com/cli/azure/
- **Pricing Calculator:** https://azure.microsoft.com/pricing/calculator/
- **Cost Management:** https://portal.azure.com/#blade/Microsoft_Azure_CostManagement/Menu/costanalysis
- **Service Health:** https://status.azure.com/
- **Support:** https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade

---

## 💰 VERWACHTE KOSTEN

**Eerste maand:** €0 (met free trial credits)  
**Daarna:** ~€58/maand (zie `IRADO_INFRASTRUCTUUR_VOORSTEL.md`)

**Budget recommendation:** €100/maand (met buffer)

---

## 🎯 NA SETUP: EERSTE DEPLOYMENT

```bash
# 1. Clone repo (of gebruik bestaande)
cd /opt/irado

# 2. Source credentials
source .azure-credentials

# 3. Deploy chatbot
./deploy-to-azure.sh

# 4. Deploy dashboard
./deploy-dashboard-to-azure.sh

# 5. Check status
curl https://irado-chatbot-app.azurewebsites.net/health
curl https://irado-dashboard-app.azurewebsites.net/
```

**Deployment duurt eerste keer ~15 minuten** (maakt alle resources aan)

---

**Status:** ✅ Ready for Production  
**Support:** Deze documentatie + Azure docs  
**Next:** Run deployment en test! 🚀

