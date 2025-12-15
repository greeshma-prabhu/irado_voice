# 💰 AZURE KOSTEN ANALYSE - IRADO PROJECT

**Datum:** 4 oktober 2025  
**Resource Group:** irado-rg  
**Region:** West Europe / North Europe / Sweden Central

---

## 📊 ACTUELE CONFIGURATIE

### 1. **WEB APPS (App Service)**

**App Service Plan:** `irado-app-service-plan`
- **SKU:** B1 (Basic)
- **Tier:** Basic
- **vCPU:** 1 core
- **RAM:** 1.75 GB
- **Storage:** 10 GB
- **Apps:** 2 (chatbot + dashboard)
- **SLA:** 99.95%

**Kosten B1 (West Europe):**
- **€11.84/maand** (~$13/maand)
- Beide apps draaien op dezelfde plan = **geen extra kosten**

---

### 2. **DATABASES (PostgreSQL Flexible Server)**

#### Database 1: `irado-chat-db`
- **SKU:** Standard_B1ms (Burstable)
- **Location:** North Europe
- **vCPU:** 1 core (burstable)
- **RAM:** 2 GB
- **Storage:** 32 GB
- **Backup:** 31 dagen retentie
- **High Availability:** Nee

**Kosten:**
- **Compute (B1ms):** ~€12.41/maand
- **Storage (32 GB):** ~€3.46/maand (€0.108/GB)
- **Backup (32 GB × 31 dagen):** ~€3.30/maand
- **Subtotaal:** ~€19.17/maand

#### Database 2: `irado-bedrijfsklanten-db`
- **SKU:** Standard_B1ms (Burstable)
- **Location:** North Europe
- **vCPU:** 1 core (burstable)
- **RAM:** 2 GB
- **Storage:** 32 GB
- **Backup:** 7 dagen retentie
- **High Availability:** Nee

**Kosten:**
- **Compute (B1ms):** ~€12.41/maand
- **Storage (32 GB):** ~€3.46/maand
- **Backup (32 GB × 7 dagen):** ~€0.75/maand
- **Subtotaal:** ~€16.62/maand

---

### 3. **CONTAINER REGISTRY**

**Registry:** `irado` (ACR)
- **SKU:** Basic
- **Location:** West Europe
- **Storage:** Inclusief 10 GB
- **Webhooks:** 2 inclusief

**Kosten:**
- **€4.55/maand** (~$5/maand)
- Extra storage (per GB boven 10 GB): €0.091/GB/maand

---

### 4. **STORAGE ACCOUNT**

**Account:** `iradostorage`
- **SKU:** Standard_LRS (Locally Redundant Storage)
- **Kind:** StorageV2 (General Purpose v2)
- **Access Tier:** Hot
- **Location:** West Europe

**Kosten (schatting bij laag gebruik):**
- **Storage (eerste 50 TB):** €0.0188/GB/maand
- **Transactions:** Zeer laag (€0.004 per 10,000 transacties)
- **Geschatte kosten:** ~€1-3/maand (afhankelijk van gebruik)

---

### 5. **KEY VAULT**

**Vault:** `irado-keyvault`
- **SKU:** Standard
- **Location:** West Europe

**Kosten:**
- **Operations:** €0.028 per 10,000 transacties
- **Secrets:** Eerste 25,000 transacties gratis
- **Geschatte kosten:** ~€0.50-1/maand (bij laag gebruik)

---

### 6. **AZURE OPENAI (AI SERVICES)**

**Service:** `info-mgal213r-swedencentral`
- **SKU:** S0 (Standard)
- **Location:** Sweden Central
- **Model:** GPT-4o

**Kosten GPT-4o:**
- **Input:** $2.50 per 1M tokens
- **Output:** $10.00 per 1M tokens

**Per chat gesprek (10 berichten):**
- **Gemiddeld per bericht:**
  - User input: ~50 tokens
  - System prompt: ~3500 tokens (1× per gesprek)
  - Chat history: ~200 tokens (groeit per bericht)
  - AI output: ~150 tokens
  
**Berekening voor 1 gesprek (10 berichten):**
- **Input tokens:**
  - System prompt: 3,500 (1×)
  - User messages: 500 (10 × 50)
  - History context: 5,000 (gemiddeld over 10 berichten)
  - Tool responses: 1,000
  - **Totaal input:** ~10,000 tokens
- **Output tokens:**
  - AI responses: 1,500 (10 × 150)
  - Tool calls: 500
  - **Totaal output:** ~2,000 tokens

**Kosten per gesprek:**
- Input: (10,000 / 1,000,000) × $2.50 = **$0.025** (€0.023)
- Output: (2,000 / 1,000,000) × $10.00 = **$0.020** (€0.018)
- **Totaal per gesprek:** **~$0.045** (~€0.041)

---

## 💵 TOTALE MAANDELIJKSE KOSTEN

### VASTE KOSTEN (per maand):

| Resource | Specificatie | Kosten/maand |
|----------|--------------|--------------|
| **App Service Plan B1** | 1 vCPU, 1.75 GB RAM | €11.84 |
| **PostgreSQL Chat DB** | B1ms, 32 GB, 31d backup | €19.17 |
| **PostgreSQL KOAD DB** | B1ms, 32 GB, 7d backup | €16.62 |
| **Container Registry** | Basic, 10 GB | €4.55 |
| **Storage Account** | LRS, Hot, laag gebruik | €2.00 |
| **Key Vault** | Standard, laag gebruik | €0.75 |
| **Azure OpenAI** | S0 basis (geen gebruik) | €0.00 |
| | **SUBTOTAAL VAST** | **€54.93** |

### VARIABELE KOSTEN (per gebruik):

| Item | Berekening | Kosten |
|------|------------|--------|
| **Per chat gesprek** | 10 berichten, GPT-4o | **€0.041** |
| **Per 100 gesprekken** | 100 × €0.041 | **€4.10** |
| **Per 1000 gesprekken** | 1000 × €0.041 | **€41.00** |

---

## 📈 SCENARIO'S

### Scenario 1: Laag Verkeer (100 gesprekken/maand)
```
Vaste kosten:     €54.93
AI kosten:        €4.10   (100 gesprekken)
TOTAAL:          €59.03/maand
```

### Scenario 2: Gemiddeld Verkeer (500 gesprekken/maand)
```
Vaste kosten:     €54.93
AI kosten:        €20.50  (500 gesprekken)
TOTAAL:          €75.43/maand
```

### Scenario 3: Hoog Verkeer (1000 gesprekken/maand)
```
Vaste kosten:     €54.93
AI kosten:        €41.00  (1000 gesprekken)
TOTAAL:          €95.93/maand
```

### Scenario 4: Zeer Hoog Verkeer (2500 gesprekken/maand)
```
Vaste kosten:     €54.93
AI kosten:        €102.50 (2500 gesprekken)
TOTAAL:          €157.43/maand
```

---

## 🔍 KOSTEN BREAKDOWN PER COMPONENT

### Percentage van Vaste Kosten:
```
PostgreSQL Databases:  65.2%  (€35.79)
App Service Plan:      21.6%  (€11.84)
Container Registry:     8.3%  (€4.55)
Storage Account:        3.6%  (€2.00)
Key Vault:              1.4%  (€0.75)
```

### Bij 500 gesprekken/maand:
```
Vaste infrastructuur:  72.8%  (€54.93)
AI/OpenAI kosten:      27.2%  (€20.50)
```

---

## 💡 OPTIMALISATIE MOGELIJKHEDEN

### 1. **Database Optimalisatie**
**Huidig:** 2× B1ms = €35.79/maand

**Opties:**
- **Backup retentie verlagen:** 
  - Chat DB: 31 dagen → 7 dagen = **-€2.55/maand**
- **Storage verkleinen (indien mogelijk):**
  - 32 GB → 20 GB = **-€1.30/maand per DB**
- **Burstable blijven:** B1ms is al de goedkoopste optie

**Potentiële besparing:** €2.55 - €5.15/maand

### 2. **App Service Plan**
**Huidig:** B1 = €11.84/maand

**Opties:**
- **Downgrade naar Free F1:** 
  - Limiet: 60 CPU minuten/dag, 1 GB RAM
  - **-€11.84/maand** maar NIET geschikt voor productie
- **Blijven bij B1:** Beste optie voor productie met 99.95% SLA

**Aanbeveling:** Blijven bij B1

### 3. **Container Registry**
**Huidig:** Basic = €4.55/maand

**Opties:**
- Geen goedkoper alternatief
- Basic is al de minimale tier

### 4. **AI Kosten Optimalisatie**

**Opties:**
- **Switch naar GPT-4o-mini:**
  - Input: $0.15 per 1M (was $2.50) = **-94% goedkoper!**
  - Output: $0.60 per 1M (was $10.00) = **-94% goedkoper!**
  - **Per gesprek: €0.041 → €0.0025** (94% besparing!)
  - Bij 500 gesprekken: €20.50 → €1.25 = **-€19.25/maand**
  
- **Context optimalisatie:**
  - Kortere system prompt: -10% tokens
  - Beperkte chat history: -20% tokens
  - **Potentiële besparing:** 25-30% op AI kosten

- **Caching implementeren:**
  - Veelvoorkomende vragen cachen
  - **Potentiële besparing:** 20-40% op AI kosten

---

## 🎯 AANBEVOLEN CONFIGURATIE

### Optimale Setup (Productie-ready, kosten-efficiënt):

**Infrastructuur:**
- App Service: B1 (blijven) - €11.84
- PostgreSQL Chat: B1ms, 32GB, **7 dagen backup** - €16.62
- PostgreSQL KOAD: B1ms, 32GB, 7 dagen backup - €16.62
- Container Registry: Basic - €4.55
- Storage: Standard LRS - €2.00
- Key Vault: Standard - €0.75
- **Vaste kosten:** **€52.38/maand** (-€2.55)

**AI:**
- **Switch naar GPT-4o-mini** voor 94% besparing
- Per gesprek: €0.0025 (was €0.041)

**Totaal bij 500 gesprekken/maand:**
- Vaste kosten: €52.38
- AI kosten: €1.25 (500 × €0.0025)
- **TOTAAL: €53.63/maand** (was €75.43 = **-€21.80 besparing!**)

---

## 📊 VERGELIJKING: HUIDIG vs GEOPTIMALISEERD

| Scenario | Huidig (GPT-4o) | Geoptimaliseerd (GPT-4o-mini) | Besparing |
|----------|-----------------|-------------------------------|-----------|
| **100 gesprekken** | €59.03 | €52.63 | **-€6.40** (11%) |
| **500 gesprekken** | €75.43 | €53.63 | **-€21.80** (29%) |
| **1000 gesprekken** | €95.93 | €55.13 | **-€40.80** (43%) |
| **2500 gesprekken** | €157.43 | €58.63 | **-€98.80** (63%) |

---

## ✅ SAMENVATTING

### Huidige Kosten:
- **Vaste kosten:** €54.93/maand
- **Per gesprek (10 berichten):** €0.041
- **Bij 500 gesprekken/maand:** €75.43

### Alle Resources:
1. ✅ App Service Plan B1 (2 apps)
2. ✅ PostgreSQL Chat DB (B1ms, 32GB)
3. ✅ PostgreSQL KOAD DB (B1ms, 32GB)
4. ✅ Container Registry (Basic)
5. ✅ Storage Account (LRS)
6. ✅ Key Vault (Standard)
7. ✅ Azure OpenAI (GPT-4o)

### Grootste Kostenposten:
1. **Databases:** 65% (€35.79)
2. **App Service:** 22% (€11.84)
3. **AI (bij 500 gesprekken):** 27% van totaal

### Quick Win Optimalisaties:
- ✅ **Switch naar GPT-4o-mini:** -94% AI kosten
- ✅ **Verlaag chat DB backup:** 31d → 7d (-€2.55)
- 💰 **Potentiële besparing bij 500 gesprekken:** €21.80/maand (29%)

---

**Status:** ✅ Complete analyse  
**Datum:** 4 oktober 2025  
**Kosten accuraat voor:** West Europe / North Europe pricing

