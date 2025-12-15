# 🏢 IRADO - AZURE INFRASTRUCTUUR VOORSTEL (PREMIUM)

**AI-Powered Grofvuil Chatbot & Management Platform - Enterprise Grade**  
**Datum:** 4 oktober 2025  
**Versie:** Premium 1.0

---

## 📋 EXECUTIVE SUMMARY

### Oplossing:
Enterprise-grade Azure cloud infrastructuur met **High Availability**, **Auto-scaling** en **Premium Performance** voor de Irado AI Chatbot met geïntegreerd management dashboard.

### Maandelijkse Kosten:
- **Vaste infrastructuur:** €118.84/maand
- **Variabel (AI):** €0.041 per chatgesprek (10 berichten)
- **Totaal bij 500 gesprekken/maand:** €139.34/maand

### Extra Features vs Basic:
- ✅ **High Availability** database (99.99% uptime)
- ✅ **Premium App Service** (auto-scaling, staging slots)
- ✅ **Geo-redundant backups** (14 dagen retentie)
- ✅ **Enhanced monitoring** & alerting
- ✅ **2× snellere performance**
- ✅ **Deployment slots** voor zero-downtime updates

---

## 🏗️ INFRASTRUCTUUR COMPONENTEN (PREMIUM)

### 1. **APPLICATION HOSTING - PREMIUM**

#### App Service Plan - Standard S1
**Specificaties:**
- **vCPU:** 1 core (dedicated, niet shared)
- **RAM:** 1.75 GB
- **Storage:** 50 GB
- **Apps:** 2 (Chatbot + Dashboard)
- **Auto-scaling:** 1-10 instances (automatic)
- **Deployment slots:** 5 (staging, testing, production)
- **SLA:** 99.95% uptime guarantee
- **Custom domains:** Unlimited
- **Backups:** Automated daily

**Features vs Basic:**
```
Basic B1                    → Standard S1
────────────────────────────────────────────
Shared compute             → Dedicated compute
Manual scaling (max 3)     → Auto-scaling (1-10)
No staging slots           → 5 deployment slots
10 GB storage              → 50 GB storage
No automated backups       → Daily backups
€11.84/maand              → €62.92/maand
```

**Kosten:** €62.92/maand

---

### 2. **DATABASE - POSTGRESQL FLEXIBLE SERVER (HIGH AVAILABILITY)**

#### Database: irado-production-ha
**Specificaties:**
- **SKU:** Standard_D2s_v3 (General Purpose)
- **vCPU:** 2 cores (dedicated)
- **RAM:** 8 GB
- **Storage:** 128 GB Premium SSD
- **IOPS:** 500 provisioned
- **Backup:** 14 dagen retentie + geo-redundant
- **High Availability:** Zone-redundant (99.99% SLA!)
- **Location:** North Europe + backup in West Europe

**Databases:**
- `bedrijfsklanten` - KOAD data (bedrijfsadressen)
- `irado_chat` - Chat history & sessies

**High Availability Features:**
- ✅ **Automatische failover** binnen 60-120 seconden
- ✅ **Synchrone replicatie** naar standby server
- ✅ **Geen data verlies** bij failover
- ✅ **Geo-redundante backups** (bescherming tegen datacenter uitval)
- ✅ **Point-in-time restore** tot 14 dagen terug
- ✅ **Automatische patches** zonder downtime

**Performance vs Basic:**
```
Basic B1ms                  → Standard D2s_v3
────────────────────────────────────────────
1 vCPU burstable           → 2 vCPU dedicated
2 GB RAM                   → 8 GB RAM
32 GB storage              → 128 GB storage
Best-effort IOPS           → 500 guaranteed IOPS
7 dagen backup             → 14 dagen backup
Local backup only          → Geo-redundant backup
99.9% SLA                  → 99.99% SLA (HA enabled)
€16.62/maand              → €85.24/maand
```

**Kosten:** €85.24/maand
- Compute D2s_v3: €44.23
- Storage 128 GB: €13.83
- Backup 14 dagen (128 GB): €18.18
- High Availability: €9.00

---

### 3. **CONTAINER REGISTRY - PREMIUM**

#### Azure Container Registry - Standard
**Specificaties:**
- **Storage:** 100 GB inclusief
- **Webhooks:** 10 inclusief
- **Geo-replication:** Tot 1 extra regio
- **Throughput:** 200 MB/s

**Features vs Basic:**
```
Basic                       → Standard
────────────────────────────────────────────
10 GB storage              → 100 GB storage
2 webhooks                 → 10 webhooks
No geo-replication         → 1 replica mogelijk
20 MB/s throughput         → 200 MB/s throughput
€4.55/maand               → €16.50/maand
```

**Kosten:** €16.50/maand

---

### 4. **STORAGE ACCOUNT - PREMIUM**

#### Storage Account - Standard GRS
**Specificaties:**
- **Type:** General Purpose v2
- **Replication:** Geo-Redundant Storage (GRS)
- **Access Tier:** Hot
- **Redundancy:** 6 kopieën (3 primair, 3 secundair)

**Features vs Basic LRS:**
```
LRS (Local)                 → GRS (Geo-redundant)
────────────────────────────────────────────
3 kopieën (1 datacenter)   → 6 kopieën (2 regio's)
99.9% durability           → 99.99999999999999% durability
Geen disaster recovery     → Automatische geo-failover
€2.00/maand               → €5.00/maand
```

**Kosten:** €5.00/maand

---

### 5. **KEY VAULT - PREMIUM**

#### Azure Key Vault - Premium (HSM)
**Specificaties:**
- **Hardware Security Module:** Ja
- **Secrets:** Onbeperkt
- **Certificates:** Onbeperkt
- **Key protection:** FIPS 140-2 Level 2

**Features vs Standard:**
```
Standard                    → Premium (HSM)
────────────────────────────────────────────
Software encryption        → Hardware Security Module
FIPS 140-2 Level 1        → FIPS 140-2 Level 2
€0.75/maand               → €4.17/maand
```

**Kosten:** €4.17/maand

---

### 6. **AZURE OPENAI SERVICE**

#### AI Services - GPT-4o
**Specificaties:**
- **Model:** GPT-4o (nieuwste generatie)
- **Location:** Sweden Central
- **SKU:** S0 (Standard)

**Pricing:**
- **Input tokens:** $2.50 per 1 miljoen tokens
- **Output tokens:** $10.00 per 1 miljoen tokens

**Per chatgesprek (10 berichten):**
- **Kosten:** €0.041 per gesprek

**Kosten:** Variabel (pay-per-use)

---

### 7. **APPLICATION INSIGHTS - PREMIUM**

#### Monitoring & Analytics
**Specificaties:**
- **Data retention:** 90 dagen (vs 30 dagen basic)
- **Log analytics:** Geavanceerd
- **Alerting:** Unlimited
- **Custom metrics:** Ja
- **Live metrics:** Ja
- **Application map:** Ja

**Kosten:** €5.00/maand (bij laag-gemiddeld gebruik)

---

## 💰 KOSTEN OVERZICHT (PREMIUM)

### VASTE KOSTEN (per maand):

| Component | Basic Spec | Premium Spec | Basic € | Premium € | Verschil |
|-----------|------------|--------------|---------|-----------|----------|
| **App Service** | B1 | S1 Standard | €11.84 | €62.92 | +€51.08 |
| **Database** | B1ms (single) | D2s_v3 (HA) | €16.62 | €85.24 | +€68.62 |
| **Container Registry** | Basic | Standard | €4.55 | €16.50 | +€11.95 |
| **Storage** | LRS | GRS | €2.00 | €5.00 | +€3.00 |
| **Key Vault** | Standard | Premium HSM | €0.75 | €4.17 | +€3.42 |
| **Monitoring** | Basic | Premium | €0.00 | €5.00 | +€5.00 |
| | **SUBTOTAAL** | | **€38.31** | **€118.84** | **+€80.53** |

### VERGELIJKING:

```
BASIC:    €38.31/maand  → 99.9% uptime, geen HA
PREMIUM:  €118.84/maand → 99.99% uptime, volledige HA
VERSCHIL: +€80.53/maand (3.1× duurder)
```

### TOTALE KOSTEN (met AI):

| Gesprekken | Basic Totaal | Premium Totaal | Verschil |
|------------|--------------|----------------|----------|
| **100** | €42.41 | €123.94 | +€81.53 |
| **500** | €58.81 | €139.34 | +€80.53 |
| **1,000** | €79.31 | €159.84 | +€80.53 |
| **2,500** | €140.81 | €221.34 | +€80.53 |
| **5,000** | €243.31 | €323.84 | +€80.53 |

---

## 📊 FEATURE VERGELIJKING

### Performance:

| Metric | Basic | Premium | Verbetering |
|--------|-------|---------|-------------|
| **CPU Power** | 1 core shared | 1 core dedicated + auto-scale | 2-5× |
| **RAM** | 1.75 GB + 2 GB DB | 1.75 GB + 8 GB DB | 4× voor DB |
| **Storage IOPS** | Best-effort | 500 guaranteed | 2-3× |
| **Response Time** | 1-3 sec | 0.5-1.5 sec | 2× sneller |
| **Concurrent Users** | 50-100 | 200-500 | 4× meer |
| **Database Queries/sec** | 100-200 | 500-1000 | 5× meer |

### Availability:

| Feature | Basic | Premium |
|---------|-------|---------|
| **App Service SLA** | 99.95% | 99.95% |
| **Database SLA** | 99.9% | **99.99%** ✅ |
| **Combined Uptime** | 99.85% | **99.94%** ✅ |
| **Downtime/jaar** | ~13 uur | **~5 uur** |
| **Downtime/maand** | ~1 uur | **~26 minuten** |
| **Auto-failover** | ❌ | ✅ |
| **Geo-redundancy** | ❌ | ✅ |

### Disaster Recovery:

| Feature | Basic | Premium |
|---------|-------|---------|
| **Database Backup** | 7 dagen, local | **14 dagen, geo-redundant** ✅ |
| **Point-in-time Restore** | 7 dagen | **14 dagen** ✅ |
| **Geo-restore** | ❌ | ✅ |
| **App Backups** | Manual | **Automated daily** ✅ |
| **Recovery Time (DB)** | 5-30 min | **60-120 sec** ✅ |
| **Data Loss (DB)** | Tot laatste backup | **0 data loss** ✅ |

### Deployment & Scaling:

| Feature | Basic | Premium |
|---------|-------|---------|
| **Scaling** | Manual (max 3) | **Auto (1-10 instances)** ✅ |
| **Deployment Slots** | ❌ | **5 slots** ✅ |
| **Zero-downtime Deploy** | ❌ | ✅ |
| **A/B Testing** | ❌ | ✅ |
| **Rollback** | Manual | **Instant** ✅ |
| **Traffic Routing** | ❌ | **Weighted %** ✅ |

### Monitoring:

| Feature | Basic | Premium |
|---------|-------|---------|
| **Log Retention** | 30 dagen | **90 dagen** ✅ |
| **Custom Metrics** | Limited | **Unlimited** ✅ |
| **Application Map** | Basic | **Advanced** ✅ |
| **Live Metrics** | ❌ | ✅ |
| **Smart Detection** | ❌ | ✅ |
| **Alert Rules** | 10 | **Unlimited** ✅ |

---

## 🎯 WANNEER PREMIUM KIEZEN?

### ✅ Premium is NODIG wanneer:

1. **Business Critical:**
   - Downtime kost geld/reputatie
   - 24/7 beschikbaarheid essentieel
   - Klanten verwachten instant response

2. **Hoog Volume:**
   - >2,000 gesprekken/maand
   - >100 gelijktijdige gebruikers
   - Piekbelasting verwacht

3. **Compliance/Audit:**
   - Hardware Security Module vereist (HSM)
   - Geo-redundancy verplicht
   - Langere log retention nodig (90 dagen)

4. **Zero Downtime:**
   - Deployment slots voor testing
   - Instant rollback capability
   - A/B testing van nieuwe features

5. **Disaster Recovery:**
   - Geo-redundante backups
   - Cross-region failover
   - 0 data loss garantie

### ⚠️ Premium is OVERKILL wanneer:

1. **Lage Kritikaliteit:**
   - 1-2 uur downtime per maand acceptabel
   - Geen piekbelasting verwacht
   - Klein gebruikersaantal (<100 gesprekken/dag)

2. **Budget Constraint:**
   - 3× hogere kosten te veel
   - ROI niet duidelijk
   - Basic functionaliteit voldoet

3. **Testfase:**
   - Nog in pilot/MVP fase
   - Volume onbekend
   - Kan later upgraden

---

## 💡 HYBRIDE OPTIE: "PREMIUM LITE"

### Beste van Beide Werelden:

**Configuratie:**
```
App Service:        Standard S1        €62.92
Database:           B2ms (no HA)       €24.82
Container Registry: Basic              €4.55
Storage:            GRS                €5.00
Key Vault:         Standard            €0.75
Monitoring:        Basic               €0.00
──────────────────────────────────────────────
TOTAAL:                               €97.99/maand
```

**Features:**
- ✅ Auto-scaling & deployment slots
- ✅ Geo-redundant storage
- ✅ 2× betere database (B2ms)
- ✅ 14 dagen backups
- ❌ Geen database HA (maar wel beter dan Basic)
- ❌ Geen HSM Key Vault

**Bij 500 gesprekken:** €118.49/maand (vs €139.34 Premium)

---

## 📈 ROI ANALYSE PREMIUM vs BASIC

### Kosten Verschil:
```
Premium - Basic = €80.53/maand = €966/jaar
```

### Wat Krijg Je Ervoor:

**1. Uptime Verbetering:**
```
Basic:   99.85% uptime = 13 uur downtime/jaar
Premium: 99.94% uptime = 5 uur downtime/jaar
WINST:   8 uur minder downtime/jaar
```

**Waarde per uur downtime:**
- 50 gesprekken/uur gemist × €0.12 AI besparing = €6/uur
- Reputatie schade: Moeilijk te meten
- Klant frustratie: Moeilijk te meten

**2. Performance Verbetering:**
- 2× snellere response times
- 4× meer concurrent capacity
- Betere gebruikerservaring

**3. Disaster Recovery:**
- 0 data loss vs mogelijke uren werk bij restore
- Geo-redundancy beschermt tegen datacenter uitval
- Snellere recovery (2 min vs 30 min)

**4. Operational Efficiency:**
- Zero-downtime deployments
- Instant rollback bij problemen
- A/B testing mogelijk
- Minder stress bij updates

### Break-even Analyse:

**Als downtime je €120/uur kost:**
```
€966/jaar ÷ €120/uur = 8 uur
Premium betaalt zichzelf terug na 8 uur voorkomen downtime
Premium voorkomt ~8 uur downtime/jaar
→ BREAK-EVEN
```

**Als downtime je €250/uur kost:**
```
Premium bespaart: 8 uur × €250 = €2000/jaar
Premium kost: €966/jaar
ROI: €1034/jaar positief (107% return)
```

---

## 🎯 AANBEVELING

### Voor Irado Specifiek:

#### **START MET BASIC** ✅
```
Kosten: €58.81/maand (bij 500 gesprekken)
```

**Waarom:**
- ✅ Pilot/Launch fase
- ✅ Volume nog onbekend
- ✅ Budget vriendelijk
- ✅ 99.85% uptime voldoende voor start
- ✅ Kan later upgraden zonder data verlies

**Monitor deze metrics:**
- Uptime percentage
- Response times
- Database CPU/RAM gebruik
- Gebruikersklachten over snelheid

#### **UPGRADE NAAR PREMIUM WANNEER:**

1. **Volume trigger:** >2,000 gesprekken/maand
2. **Performance issues:** Response times >3 seconden
3. **Reliability issues:** >2 uur downtime/maand
4. **Business requirement:** Zero-downtime deployments nodig
5. **Compliance:** HSM of geo-redundancy vereist

**Upgrade pad:**
```
Maand 1-3:   Basic (€58.81/maand)
Maand 4-6:   Premium Lite (€118.49/maand)
Maand 7+:    Premium (€139.34/maand)
```

---

## 📊 KOSTEN SAMENVATTING

### Drie Opties Vergelijken:

| Feature | BASIC | PREMIUM LITE | PREMIUM FULL |
|---------|-------|--------------|--------------|
| **App Service** | B1 | S1 | S1 |
| **Database** | B1ms (single) | B2ms (single) | D2s_v3 (HA) |
| **Auto-scaling** | ❌ | ✅ | ✅ |
| **Deployment Slots** | ❌ | ✅ | ✅ |
| **Database HA** | ❌ | ❌ | ✅ |
| **Geo-redundancy** | ❌ | Partial | ✅ |
| **HSM Key Vault** | ❌ | ❌ | ✅ |
| | | | |
| **Vaste Kosten** | €38.31 | €97.99 | €118.84 |
| **Bij 500 gesprekken** | **€58.81** | **€118.49** | **€139.34** |
| **Uptime SLA** | 99.85% | 99.90% | 99.94% |
| **Downtime/maand** | ~1 uur | ~40 min | ~26 min |

---

## ✅ CONCLUSIE

### Voor Irado:

**ADVIES: Start met BASIC, upgrade later indien nodig**

**Rationale:**
1. ✅ Basic biedt 99.85% uptime (voldoende voor launch)
2. ✅ €80/maand besparing vs Premium
3. ✅ Volume nog onbekend
4. ✅ Kan zonder data verlies upgraden
5. ✅ Premium features zijn "nice to have" niet "must have"

**Upgrade triggers:**
- Volume >2,000 gesprekken/maand
- Response times >3 seconden
- Downtime wordt business probleem
- Compliance vereist HA/geo-redundancy

**Kosten (bij 500 gesprekken/maand):**
```
Basic:          €58.81   ← START HIER
Premium Lite:   €118.49  ← Upgrade optie 1
Premium:        €139.34  ← Upgrade optie 2
```

**Over 1 jaar review:**
- Wat is actueel volume?
- Hoeveel downtime ervaren?
- Zijn response times OK?
- Is er business case voor Premium?

---

**Document:** Premium Infrastructuur Voorstel  
**Versie:** 1.0  
**Datum:** 4 oktober 2025  
**Status:** Ready for Review

