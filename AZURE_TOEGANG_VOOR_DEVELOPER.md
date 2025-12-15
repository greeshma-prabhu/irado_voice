# 🔐 AZURE TOEGANG VOOR EXTERNE DEVELOPER

**Wat moet Irado doen om jou toegang te geven tot hun Azure omgeving?**

---

## 🎯 SITUATIE

- **Irado heeft:** Azure account (bijvoorbeeld via `mainfact@irado.nl`)
- **Jij werkt op:** Dev server (167.235.62.54)
- **Jij moet kunnen:** Resources aanmaken, deployen, beheren

---

## ✅ OPTIE 1: GUEST USER IN IRADO'S AZURE (AANBEVOLEN)

### Wat moet Irado doen:

#### Stap 1: Jouw email adres uitnodigen

1. **Irado logt in op:** https://portal.azure.com (met hun account)
2. **Navigeer naar:** "Azure Active Directory" (of "Microsoft Entra ID")
3. **Ga naar:** "Users" → "+ New user" → "Invite external user"
4. **Vul in:**
   - Email address: `developer@example.com` (jouw email)
   - Name: `Developer Name`
   - Message: "Toegang voor Azure deployment"
5. **Klik:** "Invite"

**Resultaat:** Jij krijgt een email met invite link

#### Stap 2: Permissions toekennen

```bash
# Irado moet runnen (in hun Azure CLI of via Portal):
az role assignment create \
  --assignee developer@example.com \
  --role "Contributor" \
  --scope /subscriptions/THEIR_SUBSCRIPTION_ID
```

**Of via Portal:**
1. **Ga naar:** "Subscriptions" → [Hun subscription]
2. **Klik:** "Access control (IAM)"
3. **Klik:** "+ Add" → "Add role assignment"
4. **Selecteer:** 
   - Role: **Contributor**
   - Members: `developer@example.com`
5. **Review + Assign**

### Wat moet jij doen:

```bash
# Op dev server (167.235.62.54):

# 1. Accept de invite (klik link in email)
# 2. Login met device code
az login --use-device-code

# Dit geeft een code, bijvoorbeeld: ABC123DEF
# Open browser → https://microsoft.com/devicelogin
# Vul code in → Login met JOUW email
# Kies Irado's tenant (als je meerdere ziet)

# 3. Verify
az account show

# 4. Deploy!
cd /opt/irado
./deploy-to-azure.sh
```

**✅ JE BENT KLAAR!**

---

## 🔑 OPTIE 2: SERVICE PRINCIPAL (voor volledig geautomatiseerd)

### Wat moet Irado doen:

```bash
# Irado logt in
az login

# Check subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Maak service principal voor jou
az ad sp create-for-rbac \
  --name "external-developer-bot" \
  --role Contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID
```

**Output (IRADO MOET DIT AAN JOU STUREN):**
```json
{
  "appId": "12345678-1234-1234-1234-123456789abc",
  "displayName": "external-developer-bot",
  "password": "abcdefgh-1234-5678-90ab-cdefghijklmn",
  "tenant": "87654321-4321-4321-4321-210987654321"
}
```

### Wat moet jij doen:

```bash
# Op dev server, maak credentials file:
cat > /opt/irado/.azure-credentials << 'EOF'
export AZURE_SUBSCRIPTION_ID="xxx"  # Van Irado
export AZURE_TENANT_ID="xxx"        # Van Irado (tenant uit output)
export AZURE_CLIENT_ID="xxx"        # appId uit output
export AZURE_CLIENT_SECRET="xxx"    # password uit output
EOF

# Edit en vul de waardes in
nano /opt/irado/.azure-credentials

# Source it
source /opt/irado/.azure-credentials

# Login met service principal (GEEN browser nodig!)
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --password $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID

# Deploy!
./deploy-to-azure.sh
```

**✅ JE BENT KLAAR!**

---

## 📧 EMAIL TEMPLATE VOOR IRADO

### Subject: Azure toegang nodig voor deployment

```
Hallo Irado team,

Voor de deployment van de chatbot applicatie heb ik toegang nodig 
tot jullie Azure omgeving.

Kunnen jullie het volgende doen:

OPTIE A (Makkelijk - via mijn email):
1. Ga naar Azure Portal → Azure Active Directory → Users
2. Invite external user: developer@example.com
3. Geef "Contributor" role op de subscription
4. Ik krijg dan een invite email

OF

OPTIE B (Via Service Principal - voor automation):
1. Run dit command (na az login):
   az ad sp create-for-rbac \
     --name "external-developer-bot" \
     --role Contributor \
     --scopes /subscriptions/$(az account show --query id -o tsv)

2. Stuur mij de output (appId, password, tenant)

Ik kan dan vanaf de dev server (167.235.62.54) de volledige 
deployment uitvoeren.

Bedankt!
```

---

## 🔍 WELKE GEGEVENS HEB JE NODIG VAN IRADO?

### Als Guest User (Optie 1):
```
✅ Invite email (komt automatisch)
✅ Dat's het!
```

### Als Service Principal (Optie 2):
```
✅ Subscription ID (bijvoorbeeld: 12345678-1234-1234-1234-123456789abc)
✅ Tenant ID       (bijvoorbeeld: 87654321-4321-4321-4321-210987654321)
✅ Client ID       (appId uit service principal)
✅ Client Secret   (password uit service principal)
```

---

## ⚡ WELKE PERMISSIONS HEB JE NODIG?

### Minimaal: **Contributor** role

**Met Contributor kun je:**
- ✅ Resource Groups aanmaken/verwijderen
- ✅ App Services aanmaken
- ✅ Databases aanmaken  
- ✅ Container Registry beheren
- ✅ Storage Accounts aanmaken
- ✅ Deployen, updaten, logs bekijken
- ✅ **ALLES wat nodig is voor deployment!**

**Je kunt NIET:**
- ❌ Users beheren (niet nodig)
- ❌ Billing wijzigen (niet nodig)
- ❌ Subscription aanmaken (niet nodig)

**→ Contributor is precies genoeg! ✅**

### Als je ook permissies moet geven aan anderen:

Dan vraag **Owner** role (maar meestal niet nodig voor development)

---

## 🚨 SECURITY OVERWEGINGEN

### Voor Irado:

**Optie 1 (Guest User):**
- ✅ Gebonden aan jouw persoonlijke email
- ✅ Multi-factor authentication mogelijk
- ✅ Makkelijk in te trekken
- ✅ Audit logs per user
- ⚠️ Vereist device code flow (browser)

**Optie 2 (Service Principal):**
- ✅ Geen browser nodig
- ✅ Goed voor automation/scripts
- ✅ Credentials kunnen roteren
- ⚠️ Password moet veilig opgeslagen worden
- ⚠️ Als password lekt → toegang voor iedereen

**Aanbeveling:** 
- **Development:** Optie 1 (Guest User) - veiliger
- **CI/CD Pipeline:** Optie 2 (Service Principal) - praktischer

### Credentials opslaan (als Service Principal):

```bash
# ✅ GOED: Lokaal encrypted file
chmod 600 /opt/irado/.azure-credentials
source /opt/irado/.azure-credentials

# ✅ GOED: Azure Key Vault
az keyvault secret set --vault-name irado-kv --name sp-secret --value "$SECRET"

# ❌ SLECHT: In git committen
# ❌ SLECHT: Plain text in shared locations
# ❌ SLECHT: Email/Slack zonder encryption
```

---

## ✅ VERIFICATIE: Heb je genoeg toegang?

### Test na setup:

```bash
# 1. Ben je ingelogd?
az account show
# Moet Irado's subscription tonen

# 2. Heb je Contributor role?
az role assignment list \
  --assignee $(az account show --query user.name -o tsv) \
  --all --output table
# Moet "Contributor" tonen

# 3. Kun je resource group aanmaken?
az group create \
  --name test-permissions-rg \
  --location northeurope
# Moet succesvol zijn

# 4. Opruimen
az group delete --name test-permissions-rg --yes --no-wait

# 5. Kun je deployment runnen?
cd /opt/irado
./deploy-to-azure.sh
# Moet zonder errors runnen
```

**Als alle 5 checks ✅ zijn → Perfect!**

---

## 📋 CHECKLIST VOOR IRADO

**Wat moet Irado doen:**
- [ ] Azure account hebben (bijv. mainfact@irado.nl)
- [ ] Subscription actief hebben
- [ ] Beslissen: Guest User of Service Principal?

**Als Guest User:**
- [ ] Developer email uitnodigen in Azure AD
- [ ] Contributor role toewijzen op subscription
- [ ] Bevestigen dat invite verstuurd is

**Als Service Principal:**
- [ ] Service Principal aanmaken via Azure CLI
- [ ] Output (appId, password, tenant) veilig versturen
- [ ] Subscription ID delen

**Wat moet jij daarna doen:**
- [ ] Accept invite (Guest User) of credentials opslaan (Service Principal)
- [ ] `az login` (met browser of service principal)
- [ ] Test: `az account show`
- [ ] Test: Permissions check (zie hierboven)
- [ ] Deploy: `./deploy-to-azure.sh`

---

## 🎯 RECOMMENDED FLOW

### Voor Irado (via Portal - geen CLI kennis nodig):

1. **Login:** https://portal.azure.com
2. **Zoek:** "Subscriptions" in search bar
3. **Klik:** Op hun subscription naam
4. **Klik:** "Access control (IAM)" in left menu
5. **Klik:** "+ Add" → "Add role assignment"
6. **Tab "Role":** Selecteer **Contributor** → Next
7. **Tab "Members":** 
   - Klik: "+ Select members"
   - Typ: jouw email (developer@example.com)
   - Als je nog niet bestaat: Klik "Invite external user"
8. **Klik:** "Review + assign"

**Klaar! Jij krijgt een email.**

### Voor jou (op dev server):

```bash
# 1. Check email → klik invite link
# 2. Login
az login --use-device-code

# 3. Deploy
cd /opt/irado
./deploy-to-azure.sh
```

**Total tijd: ~5 minuten**

---

## 🆘 TROUBLESHOOTING

### "You do not have permission"
→ Irado heeft je geen Contributor role gegeven  
→ Vraag ze de role assignment te checken

### "Subscription not found"
→ Je bent ingelogd met verkeerde account  
→ Run: `az account list` om te zien welke subscriptions je hebt  
→ Als Irado's subscription er niet bij is → vraag invite opnieuw

### "Invalid credentials" (Service Principal)
→ appId, password of tenant is verkeerd  
→ Vraag Irado om nieuwe service principal

### "Device code expired"
→ Te lang gewacht met invoeren  
→ Run `az login --use-device-code` opnieuw

---

## 📞 SAMENVATTING

### WAT IRADO MOET DOEN:
**Jou uitnodigen als Guest User met Contributor role**

### WAT JIJ NODIG HEBT:
**Email invite link OF service principal credentials**

### WAT JIJ DAN DOET:
```bash
az login --use-device-code
./deploy-to-azure.sh
```

**Klaar! 🎉**

---

## 📧 QUICK REFERENCE

### Irado's actions (Portal):
```
1. portal.azure.com
2. Subscriptions → [subscription]
3. Access control (IAM)
4. Add role assignment
5. Role: Contributor
6. Member: developer@example.com
7. Review + assign
```

### Jouw actions (CLI):
```bash
az login --use-device-code
az account show
./deploy-to-azure.sh
```

**Time to deploy: 15 minuten na toegang! ✅**

