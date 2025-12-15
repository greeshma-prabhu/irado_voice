# 🔐 AZURE PERMISSIONS VOOR IRADO ACCOUNT

**Welke permissies heeft `mainfact@irado.nl` nodig om alles te deployen?**

---

## 📋 TWEE OPTIES

### OPTIE 1: Direct met Irado Account (MAKKELIJKSTE) ✅

**Account:** `mainfact@irado.nl` (of ander Office365 account)

**Geen Service Principal nodig!** Gewoon inloggen met je normale account.

---

## 🎯 OPTIE 1: NORMALE LOGIN (AANBEVOLEN)

### Stap 1: Azure Account Setup
```
1. Ga naar: https://portal.azure.com
2. Login met: mainfact@irado.nl
3. Kies: "Start gratis" of "Pay-As-You-Go"
4. Vul bedrijfsgegevens in
```

**Result:** Je hebt nu een Azure Subscription als **Owner**

### Stap 2: Check je Role

```bash
# Login via browser
az login
# Dit opent browser → login met mainfact@irado.nl

# Check je subscription
az account show

# Check je role
az role assignment list \
  --assignee mainfact@irado.nl \
  --include-inherited \
  --output table
```

**Verwacht resultaat:**
```
Principal                Role        Scope
-----------------------  ----------  ------------------------------------
mainfact@irado.nl        Owner       /subscriptions/xxx-xxx-xxx-xxx
```

### Stap 3: Deploy vanaf Dev Server

```bash
# Op dev server (167.235.62.54)
az login
# Browser opent → login met mainfact@irado.nl

# Nu kun je ALLES doen:
./deploy-to-azure.sh
./deploy-dashboard-to-azure.sh
```

**Klaar!** Geen extra setup nodig.

---

## 🔐 WELKE PERMISSIES ZIJN NODIG?

### Minimale Role: **Contributor** ✅

**Wat kan je met Contributor:**
- ✅ Resource Groups aanmaken/verwijderen
- ✅ App Service Plans aanmaken
- ✅ Web Apps aanmaken/configureren
- ✅ Container Registry aanmaken
- ✅ PostgreSQL databases aanmaken
- ✅ Storage Accounts aanmaken
- ✅ Resources updaten/restarten
- ✅ Logs bekijken
- ✅ Metrics bekijken

**Wat kan je NIET met Contributor:**
- ❌ Users/permissions beheren (daarvoor: Owner role)
- ❌ Subscriptions aanmaken
- ❌ Billing wijzigen

### Ideale Role: **Owner** 🌟

**Als je de Azure subscription zelf aanmaakt, ben je automatisch Owner!**

**Extra wat je kan met Owner:**
- ✅ Alles van Contributor
- ✅ Users toevoegen/verwijderen
- ✅ Permissions geven aan anderen
- ✅ Service Principals aanmaken
- ✅ Billing bekijken/wijzigen

---

## 📝 EXACTE PERMISSIONS DIE GEBRUIKT WORDEN

### Bij Deployment worden deze Azure Resources aangemaakt:

```bash
# 1. Resource Group
az group create --name irado-rg --location northeurope
# Required: Microsoft.Resources/resourceGroups/write

# 2. Container Registry
az acr create --name irado --resource-group irado-rg --sku Basic
# Required: Microsoft.ContainerRegistry/registries/write

# 3. App Service Plan
az appservice plan create --name irado-app-plan --resource-group irado-rg
# Required: Microsoft.Web/serverfarms/write

# 4. Web Apps
az webapp create --name irado-chatbot-app --plan irado-app-plan
# Required: Microsoft.Web/sites/write

# 5. PostgreSQL Database
az postgres flexible-server create --name irado-chat-db
# Required: Microsoft.DBforPostgreSQL/flexibleServers/write

# 6. Storage Account
az storage account create --name iradostorage
# Required: Microsoft.Storage/storageAccounts/write

# 7. Key Vault (optioneel)
az keyvault create --name irado-keyvault
# Required: Microsoft.KeyVault/vaults/write
```

### Alle benodigde Resource Providers:

```bash
Microsoft.Resources         # Resource Groups
Microsoft.ContainerRegistry # Container Registry
Microsoft.Web              # App Services
Microsoft.DBforPostgreSQL  # PostgreSQL
Microsoft.Storage          # Storage Accounts
Microsoft.KeyVault         # Key Vault (optioneel)
Microsoft.Insights         # Monitoring (auto)
```

**Deze worden automatisch geregistreerd bij eerste gebruik!**

---

## 🚀 SETUP OP DEV SERVER (167.235.62.54)

### Scenario: Login met mainfact@irado.nl vanaf dev server

```bash
# 1. Login (opent browser op je lokale machine via SSH forwarding)
az login --use-device-code

# Output:
# To sign in, use a web browser to open the page:
#   https://microsoft.com/devicelogin
# and enter the code XXXXXXXXX to authenticate.

# 2. Open browser op je LOKALE machine
# - Ga naar: https://microsoft.com/devicelogin
# - Vul code in: XXXXXXXXX
# - Login met: mainfact@irado.nl
# - Bevestig permissions

# 3. Terug in terminal:
# ✅ You have logged in. Now let us find all the subscriptions...

# 4. Check subscription
az account show --output table

# 5. Deploy!
cd /opt/irado
./deploy-to-azure.sh
```

### Permanente Login (session blijft actief)

```bash
# Na az login blijf je ingelogd voor ~90 dagen
# Token wordt opgeslagen in: ~/.azure/

# Check of je nog ingelogd bent:
az account show

# Als expired:
az login --use-device-code
```

---

## 🎭 OPTIE 2: SERVICE PRINCIPAL (voor automation)

**Alleen nodig als:**
- ❌ Je GEEN browser toegang hebt
- ❌ Je CI/CD pipelines wil zonder user interaction
- ❌ Je scripts wil die 24/7 runnen zonder user

**Voor normale deployment vanaf dev server: NIET NODIG!**

### Wanneer WEL Service Principal?

**Bijvoorbeeld:**
- GitHub Actions deployment
- Jenkins/GitLab CI
- Automated backups
- Scheduled scripts

**Dan:**
```bash
# Maak service principal (MET je Owner/Contributor account)
az ad sp create-for-rbac \
  --name "irado-automation-bot" \
  --role Contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID

# Output:
{
  "appId": "xxx",      # CLIENT_ID
  "password": "xxx",   # CLIENT_SECRET  
  "tenant": "xxx"      # TENANT_ID
}

# Login met service principal (zonder browser!)
az login --service-principal \
  --username $CLIENT_ID \
  --password $CLIENT_SECRET \
  --tenant $TENANT_ID
```

---

## ✅ CHECKLIST: Permissions Check

### Test of je account genoeg permissions heeft:

```bash
# 1. Check of je ingelogd bent
az account show
# ✅ Moet je subscription tonen

# 2. Check je role
az role assignment list \
  --assignee mainfact@irado.nl \
  --all \
  --output table
# ✅ Moet minimaal "Contributor" of "Owner" tonen

# 3. Test resource group aanmaken
az group create \
  --name test-permissions-rg \
  --location northeurope \
  --dry-run
# ✅ Moet succesvol zijn

# 4. Delete test group
az group delete \
  --name test-permissions-rg \
  --yes \
  --no-wait
# ✅ Moet succesvol zijn

# 5. Check resource providers
az provider list \
  --query "[?registrationState=='Registered'].namespace" \
  --output table
# ✅ Moet Microsoft.Web, Microsoft.DBforPostgreSQL, etc. tonen
```

**Als alle 5 checks ✅ zijn → Je hebt genoeg permissions!**

---

## 🔍 TROUBLESHOOTING

### Error: "Insufficient privileges"

```bash
# Check je role
az role assignment list --assignee mainfact@irado.nl --output table

# Als je GEEN role hebt:
# → Je bent niet de subscription owner
# → Laat de subscription owner je een role geven:

# Subscription owner moet runnen:
az role assignment create \
  --assignee mainfact@irado.nl \
  --role Contributor \
  --scope /subscriptions/YOUR_SUBSCRIPTION_ID
```

### Error: "Resource provider not registered"

```bash
# Registreer providers (gebeurt meestal automatisch)
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.Web
az provider register --namespace Microsoft.DBforPostgreSQL
az provider register --namespace Microsoft.Storage

# Check status (duurt 1-2 minuten)
az provider show --namespace Microsoft.Web --query registrationState
```

### Error: "Subscription not found"

```bash
# List alle subscriptions
az account list --output table

# Zijn er subscriptions maar niet de juiste?
az account set --subscription "Subscription Name"
# of
az account set --subscription "subscription-id"
```

---

## 📊 PERMISSION MATRIX

| Action | Contributor | Owner | Reader |
|--------|-------------|-------|--------|
| **Resource aanmaken** | ✅ | ✅ | ❌ |
| **Resource verwijderen** | ✅ | ✅ | ❌ |
| **Resource updaten** | ✅ | ✅ | ❌ |
| **Logs bekijken** | ✅ | ✅ | ✅ |
| **Metrics bekijken** | ✅ | ✅ | ✅ |
| **Users beheren** | ❌ | ✅ | ❌ |
| **Permissions geven** | ❌ | ✅ | ❌ |
| **Billing bekijken** | ❌ | ✅ | ❌ |
| **Service Principal maken** | ❌ | ✅ | ❌ |

**Voor deployment: Contributor is genoeg!**  
**Als je de subscription aanmaakt: Je bent automatisch Owner!**

---

## 🎯 RECOMMENDED SETUP VOOR IRADO

### Scenario 1: Mainfact is de enige developer (SIMPEL)

```bash
# Op dev server:
az login --use-device-code
# Login met mainfact@irado.nl
# → Automatisch Owner van subscription

# Deploy:
./deploy-to-azure.sh
```

**Klaar! Geen extra config nodig.**

### Scenario 2: Meerdere developers

```bash
# Mainfact (owner) voegt anderen toe:
az role assignment create \
  --assignee developer@irado.nl \
  --role Contributor \
  --resource-group irado-rg

# Developer kan nu deployen:
az login --use-device-code
# Login met developer@irado.nl
./deploy-to-azure.sh
```

### Scenario 3: CI/CD Automation

```bash
# Mainfact maakt service principal:
az ad sp create-for-rbac \
  --name "irado-github-actions" \
  --role Contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID

# Zet credentials in GitHub Secrets
# Deploy via GitHub Actions zonder user interaction
```

---

## 📝 SAMENVATTING

### Voor normale deployment vanaf dev server:

**JE HEBT NODIG:**
1. ✅ Azure account (mainfact@irado.nl)
2. ✅ Azure subscription (aangemaakt via portal)
3. ✅ Owner of Contributor role (automatisch bij eigen subscription)
4. ✅ Azure CLI installed (`az`)
5. ✅ Login: `az login --use-device-code`

**JE HEBT NIET NODIG:**
- ❌ Service Principal
- ❌ Client ID / Client Secret
- ❌ Extra permissions aanvragen
- ❌ Complex setup

### Commands die je moet kunnen runnen:

```bash
az group create          # Resource Group
az acr create           # Container Registry
az appservice plan      # App Service Plan
az webapp create        # Web Apps
az postgres server      # PostgreSQL
az storage account      # Storage
```

**Met Owner of Contributor role: Alles werkt! ✅**

---

## 🚀 QUICK START

```bash
# 1. Login
az login --use-device-code
# → Login met mainfact@irado.nl in browser

# 2. Verify
az account show

# 3. Deploy
cd /opt/irado
./deploy-to-azure.sh

# Done! 🎉
```

**Verwachte tijd:** 
- Login: 1 minuut
- Deploy: 10-15 minuten
- Total: ~15 minuten

**Kosten:**
- Eerste maand: €0 (trial credits)
- Daarna: €58/maand

---

**TL;DR:** Login met `mainfact@irado.nl` via `az login` en je hebt ALLE permissions die je nodig hebt! 🔥

