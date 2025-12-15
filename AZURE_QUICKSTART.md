# ⚡ AZURE ACCOUNT SETUP - QUICK START

**5 minuten setup voor Irado Azure deployment**

---

## 🚀 SNELLE STAPPEN

### 1. Azure Account (5 min)
```
1. Ga naar: https://azure.microsoft.com/nl-nl/
2. Klik: "Start gratis"
3. Vul in: Email, telefoon, creditcard
4. Kies: Pay-As-You-Go subscription
```

### 2. Login via CLI (1 min)
```bash
# Installeer Azure CLI (als nodig)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Check subscription
az account list --output table
```

### 3. Service Principal (2 min)
```bash
# Haal subscription ID op
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Maak deployment bot
az ad sp create-for-rbac \
  --name "irado-deployment-bot" \
  --role Contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID

# BEWAAR DE OUTPUT! (appId, password, tenant)
```

### 4. Resource Group (1 min)
```bash
az group create \
  --name irado-rg \
  --location northeurope
```

### 5. Credentials File (2 min)
```bash
# Maak credentials file
cat > /opt/irado-azure/.azure-credentials << 'EOF'
export AZURE_SUBSCRIPTION_ID="VULL_HIER_IN"
export AZURE_TENANT_ID="VULL_HIER_IN"
export AZURE_CLIENT_ID="VULL_HIER_IN"
export AZURE_CLIENT_SECRET="VULL_HIER_IN"
export AZURE_RESOURCE_GROUP="irado-rg"
export AZURE_LOCATION="northeurope"
EOF

# Vul de waardes in van stap 3!
nano /opt/irado-azure/.azure-credentials

# Source it
source /opt/irado-azure/.azure-credentials
```

### 6. Deploy! (15 min)
```bash
cd /opt/irado-azure

# Deploy alles
./deploy-to-azure.sh
./deploy-dashboard-to-azure.sh

# Check
curl https://irado-chatbot-app.azurewebsites.net/health
curl https://irado-dashboard-app.azurewebsites.net/
```

---

## ✅ KLAAR!

**Total tijd:** ~25 minuten (waarvan 15 min deployment)

**Kosten:** 
- Eerste maand: €0 (free trial)
- Daarna: ~€58/maand

**Volledige docs:** Zie `AZURE_ACCOUNT_SETUP.md`

---

## 🔑 CREDENTIALS TEMPLATE

```bash
# Vul deze in na stap 3:
export AZURE_SUBSCRIPTION_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export AZURE_TENANT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export AZURE_CLIENT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # appId
export AZURE_CLIENT_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxx"         # password
export AZURE_RESOURCE_GROUP="irado-rg"
export AZURE_LOCATION="northeurope"
```

---

## 🚨 TROUBLESHOOTING

**"az: command not found"**
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

**"Insufficient permissions"**
```bash
az role assignment create \
  --assignee YOUR_CLIENT_ID \
  --role "Contributor" \
  --scope /subscriptions/YOUR_SUBSCRIPTION_ID
```

**"Resource provider not registered"**
```bash
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.DBforPostgreSQL
az provider register --namespace Microsoft.Web
```

---

**Support:** Zie volledige docs in `AZURE_ACCOUNT_SETUP.md` 📖

