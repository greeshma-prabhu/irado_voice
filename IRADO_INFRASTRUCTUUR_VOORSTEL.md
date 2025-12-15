# 🏢 IRADO - AZURE INFRASTRUCTUUR VOORSTEL

**AI-Powered Grofvuil Chatbot & Management Platform**  
**Datum:** 4 oktober 2025  
**Versie:** 1.0

---

## 📋 EXECUTIVE SUMMARY

### Oplossing:
Complete Azure cloud infrastructuur voor de Irado AI Chatbot met geïntegreerd management dashboard voor grofvuil aanvragen in Schiedam, Vlaardingen en Capelle aan den IJssel.

### Maandelijkse Kosten:
- **Vaste infrastructuur:** €38.31/maand
- **Variabel (AI):** €0.041 per chatgesprek (10 berichten)
- **Totaal bij 500 gesprekken/maand:** €58.81/maand

### ROI:
- Automatisering van klantcontacten
- 24/7 beschikbaarheid
- Directe integratie met QML routing systeem
- Real-time KOAD (bedrijfsklanten) validatie

---

## 🏗️ INFRASTRUCTUUR COMPONENTEN

### 1. **APPLICATION HOSTING**

#### App Service Plan - Basic B1
**Specificaties:**
- **vCPU:** 1 core
- **RAM:** 1.75 GB
- **Storage:** 10 GB
- **Apps:** 2 (Chatbot + Dashboard op 1 plan)
- **Auto-scaling:** Tot 3 instances
- **SLA:** 99.95% uptime guarantee

**Gebruikers toegang:**
- Chatbot: https://irado-chatbot-app.azurewebsites.net
- Dashboard: https://irado-dashboard-app.azurewebsites.net

**Kosten:** €11.84/maand

---

### 2. **DATABASE - POSTGRESQL FLEXIBLE SERVER**

#### Database: irado-production
**Specificaties:**
- **SKU:** Standard_B1ms (Burstable)
- **vCPU:** 1 core (burstable tot 100%)
- **RAM:** 2 GB
- **Storage:** 32 GB SSD
- **Backup:** 7 dagen retentie
- **High Availability:** Disabled (single zone)
- **Location:** North Europe

**Databases:**
- `bedrijfsklanten` - KOAD data (bedrijfsadressen)
- `irado_chat` - Chat history & sessies

**Features:**
- Automatische backups (7 dagen)
- Point-in-time restore
- SSL/TLS versleuteling
- Firewall regels

**Kosten:** €16.62/maand
- Compute: €12.41
- Storage 32 GB: €3.46
- Backup (7 dagen): €0.75

---

### 3. **CONTAINER REGISTRY**

#### Azure Container Registry - Basic
**Specificaties:**
- **Storage:** 10 GB inclusief
- **Webhooks:** 2 inclusief
- **Geo-replication:** Nee

**Gebruik:**
- Docker images voor chatbot
- Docker images voor dashboard
- Versie beheer (tags)

**Kosten:** €4.55/maand

---

### 4. **STORAGE ACCOUNT**

#### Storage Account - Standard LRS
**Specificaties:**
- **Type:** General Purpose v2
- **Replication:** Locally Redundant Storage (LRS)
- **Access Tier:** Hot
- **Gebruik:** Logging, tijdelijke bestanden

**Features:**
- 99.9% availability
- Blob storage
- File shares
- Encryption at rest

**Kosten:** €2.00/maand (bij laag gebruik)

---

### 5. **KEY VAULT**

#### Azure Key Vault - Standard
**Specificaties:**
- **Secrets:** API keys, wachtwoorden
- **Certificates:** SSL certificaten
- **Access Policies:** RBAC gebaseerd

**Opgeslagen secrets:**
- Azure OpenAI API keys
- Database wachtwoorden
- SMTP credentials
- API tokens

**Kosten:** €0.75/maand (bij laag gebruik)

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
- Input: ~10,000 tokens
- Output: ~2,000 tokens
- **Kosten:** €0.041 per gesprek

**Kosten:** Variabel (pay-per-use)

---

## 💰 KOSTEN OVERZICHT

### VASTE KOSTEN (per maand):

| Component | Specificatie | Kosten |
|-----------|--------------|--------|
| **App Service B1** | 1 vCPU, 1.75 GB RAM, 10 GB | €11.84 |
| **PostgreSQL B1ms** | 1 vCPU, 2 GB RAM, 32 GB, 7d backup | €16.62 |
| **Container Registry** | Basic, 10 GB | €4.55 |
| **Storage Account** | LRS, Hot, laag gebruik | €2.00 |
| **Key Vault** | Standard, laag gebruik | €0.75 |
| **Monitoring** | Inclusief in services | €0.00 |
| | **TOTAAL VAST** | **€38.31** |

### VARIABELE KOSTEN (AI/OpenAI):

| Volume | Kosten/gesprek | Totaal AI kosten | **Totaal/maand** |
|--------|----------------|------------------|------------------|
| **100 gesprekken** | €0.041 | €4.10 | **€42.41** |
| **250 gesprekken** | €0.041 | €10.25 | **€48.56** |
| **500 gesprekken** | €0.041 | €20.50 | **€58.81** |
| **1,000 gesprekken** | €0.041 | €41.00 | **€79.31** |
| **2,500 gesprekken** | €0.041 | €102.50 | **€140.81** |
| **5,000 gesprekken** | €0.041 | €205.00 | **€243.31** |

**Per gesprek definitie:** 10 berichten uitwisseling tussen gebruiker en AI

---

## 📊 SCENARIO ANALYSE

### Scenario 1: **Lancering / Laag Volume**
```
Maandelijkse gesprekken:  100 (≈ 3 per dag)
Vaste kosten:            €38.31
AI kosten:               €4.10
────────────────────────────────────
TOTAAL:                  €42.41/maand
Per gesprek:             €0.42
```

### Scenario 2: **Groei / Gemiddeld Volume** ⭐
```
Maandelijkse gesprekken:  500 (≈ 17 per dag)
Vaste kosten:            €38.31
AI kosten:               €20.50
────────────────────────────────────
TOTAAL:                  €58.81/maand
Per gesprek:             €0.12
```

### Scenario 3: **Stabiel / Hoog Volume**
```
Maandelijkse gesprekken:  1,000 (≈ 33 per dag)
Vaste kosten:            €38.31
AI kosten:               €41.00
────────────────────────────────────
TOTAAL:                  €79.31/maand
Per gesprek:             €0.08
```

### Scenario 4: **Druk / Zeer Hoog Volume**
```
Maandelijkse gesprekken:  2,500 (≈ 83 per dag)
Vaste kosten:            €38.31
AI kosten:               €102.50
────────────────────────────────────
TOTAAL:                  €140.81/maand
Per gesprek:             €0.06
```

**Conclusie:** Hoe meer volume, hoe lager de kosten per gesprek!

---

## 🎯 FEATURES & FUNCTIONALITEIT

### Chatbot Features:
✅ 24/7 beschikbaarheid  
✅ Meertalig (Nederlands primair)  
✅ Automatische adres validatie  
✅ KOAD bedrijfsklanten detectie  
✅ Routering per afvaltype (Huisraad, IJzer/EA, Tuin, Matrassen)  
✅ Gemeente-specifieke regels (Schiedam, Vlaardingen, Capelle)  
✅ QML XML generatie voor intern systeem  
✅ Automatische bevestigingsemails  
✅ Privacy compliance (GDPR)  
✅ Chat history tracking  

### Dashboard Features:
✅ KOAD database beheer (CSV upload/download)  
✅ Real-time chat logs viewer  
✅ System prompt editor (live AI aanpassingen)  
✅ Chat history inzage  
✅ Statistieken & analytics  
✅ Export functionaliteit  
✅ Gebruikersbeheer  

### Technische Features:
✅ SSL/TLS versleuteling  
✅ Automatische backups (7 dagen)  
✅ 99.95% uptime SLA  
✅ Auto-scaling capabilities  
✅ Monitoring & alerting  
✅ Container-based deployment  
✅ CI/CD ready  

---

## 🔒 BEVEILIGING & COMPLIANCE

### Security Measures:
- **Versleuteling:** TLS 1.2+ voor alle verbindingen
- **Authentication:** Basic Auth + API keys
- **Secrets Management:** Azure Key Vault
- **Database:** SSL/TLS versleuteld, firewall protected
- **Network:** IP whitelisting mogelijk
- **Logging:** Audit trails in Application Insights

### Compliance:
- **GDPR:** Privacy beleid geïmplementeerd
- **Data residency:** EU (North/West Europe)
- **Backups:** 7 dagen retentie
- **Access control:** Role-based access

### SLA:
- **App Service:** 99.95% uptime
- **Database:** 99.9% uptime
- **Azure OpenAI:** 99.9% uptime
- **Overall systeem:** 99.85%+ uptime

---

## 📈 SCHAALBAARHEID

### Huidige Capaciteit (Basic B1 + B1ms):
```
Gelijktijdige chats:     50-100
Berichten per uur:       200-500
Database queries/sec:    100-200
Response tijd:           < 2 seconden
```

### Opschalen Opties:

#### Bij 1,000+ gesprekken/maand:
**App Service:** B1 → B2
- Kosten: +€11.84/maand
- 2× CPU, 2× RAM
- Capaciteit: 2× hogere throughput

#### Bij 5,000+ gesprekken/maand:
**Database:** B1ms → B2s
- Kosten: +€12.41/maand
- 2× vCPU, 2× RAM
- Capaciteit: 4× hogere query performance

#### Bij 10,000+ gesprekken/maand:
**App Service:** B2 → S1 Standard
- Kosten: +€23.68/maand
- 1 vCPU maar betere baseline
- Auto-scaling tot 10 instances
- Staging slots

**Totale kosten bij 10,000 gesprekken:**
```
Infrastructuur:    ~€85/maand
AI kosten:         ~€410/maand
────────────────────────────────
TOTAAL:           ~€495/maand
Per gesprek:      €0.049
```

---

## 💡 OPTIMALISATIE MOGELIJKHEDEN

### AI Kosten Reductie (Toekomst):

#### Optie 1: **GPT-4o-mini** (94% goedkoper)
```
Per gesprek:  €0.041 → €0.0025
Besparing:    94%
```
**Bij 500 gesprekken:**
- Was: €58.81/maand
- Wordt: €39.56/maand
- **Besparing: €19.25/maand**

**Trade-off:** 
- ✅ Veel goedkoper
- ⚠️ Iets minder geavanceerd
- ✅ Nog steeds zeer capabel voor deze use case

#### Optie 2: **Hybrid Approach**
```
Simpele vragen:   GPT-4o-mini (80% van gesprekken)
Complexe vragen:  GPT-4o (20% van gesprekken)
```
**Besparing:** ~75% op AI kosten

#### Optie 3: **Response Caching**
```
Veelvoorkomende vragen cachen
Besparing: 20-30% op AI calls
```

### Database Optimalisatie:
- **Backup retentie:** 7 dagen is voldoende voor productie
- **Storage:** 32 GB ruim voldoende voor 2+ jaar

### Geen upgrade nodig:
- App Service B1 voldoende tot 2,000+ gesprekken/maand
- Database B1ms voldoende tot 5,000+ gesprekken/maand

---

## 🚀 DEPLOYMENT & ONDERHOUD

### Deployment Proces:
1. **Code wijzigingen:** Push naar Git repository
2. **Docker build:** Automatisch in Azure Container Registry
3. **Deploy:** Automated deployment naar Azure App Service
4. **Health check:** Automatische validatie
5. **Rollback:** Mogelijk binnen 5 minuten

**Deployment tijd:** 3-5 minuten per update

### Monitoring:
- **Application Insights:** Real-time metrics
- **Log Analytics:** Gestructureerde logs
- **Alerts:** Email/SMS bij problemen
- **Dashboard:** Live logs viewer beschikbaar

### Onderhoud:
- **Database backups:** Automatisch dagelijks
- **Security patches:** Automatisch via Azure
- **SSL certificaten:** Automatisch vernieuwd
- **Monitoring:** 24/7 beschikbaar

### Support:
- **Deployment script:** Geautomatiseerd (`deploy-to-azure.sh`)
- **Documentatie:** Complete guides aanwezig
- **Logging:** Uitgebreid voor debugging

---

## 📅 IMPLEMENTATIE ROADMAP

### Fase 1: **Live & Operationeel** ✅ (KLAAR)
- [x] Azure infrastructuur opgezet
- [x] Chatbot gedeployed en werkend
- [x] Dashboard gedeployed en werkend
- [x] Database migratie naar PostgreSQL
- [x] KOAD integratie
- [x] Email functionaliteit (QML XML)
- [x] System prompt editor
- [x] Live logs viewer

### Fase 2: **Optimalisatie** (Aanbevolen)
- [ ] Database consolidatie (2 → 1 server)
- [ ] GPT-4o-mini migratie (94% cost savings)
- [ ] Response caching implementatie
- [ ] Enhanced monitoring & analytics

### Fase 3: **Uitbreiding** (Toekomstig)
- [ ] Email notificaties voor medewerkers
- [ ] SMS confirmaties voor klanten
- [ ] Advanced analytics dashboard
- [ ] API voor externe integraties
- [ ] Mobile app integratie

---

## ✅ AANBEVELING

### Voorgestelde Configuratie:

**Infrastructuur:**
```
App Service:          Basic B1
Database:             1× PostgreSQL B1ms
Container Registry:   Basic
Storage:              Standard LRS
Key Vault:           Standard
AI Model:            GPT-4o (nu) → GPT-4o-mini (later)
```

**Kosten (bij 500 gesprekken/maand):**
```
Vaste kosten:    €38.31/maand
AI kosten:       €20.50/maand
────────────────────────────────
TOTAAL:         €58.81/maand
```

**Met GPT-4o-mini optimalisatie:**
```
Vaste kosten:    €38.31/maand
AI kosten:       €1.25/maand
────────────────────────────────
TOTAAL:         €39.56/maand  (-€19.25 besparing!)
```

---

## 📞 VOLGENDE STAPPEN

### Voor Irado:

1. **Review:** Deze infrastructuur voorstel beoordelen
2. **Beslissing:** Akkoord voor live gang met deze configuratie
3. **Optimalisatie:** Beslissen over GPT-4o-mini migratie
4. **Database:** Goedkeuring voor consolidatie (2 → 1 database)
5. **Monitoring:** Eerste maand volume tracken voor optimalisatie

### Optioneel:
- [ ] Training voor Irado medewerkers (dashboard gebruik)
- [ ] Documentatie voor eindgebruikers
- [ ] Marketing materiaal (chatbot promotie)
- [ ] Integratie met bestaande Irado systemen

---

## 📋 BIJLAGEN

### Documentatie:
- `AZURE_KOSTEN_ANALYSE.md` - Volledige kosten breakdown
- `AZURE_DEPLOYMENT_GUIDE.md` - Deployment instructies
- `DASHBOARD_QUICKSTART.md` - Dashboard handleiding
- `LOGGING_UPGRADE.md` - Logging specificaties

### Scripts:
- `deploy-to-azure.sh` - Automated chatbot deployment
- `deploy-dashboard-to-azure.sh` - Automated dashboard deployment

### Live URLs:
- **Chatbot:** https://irado-chatbot-app.azurewebsites.net
- **Dashboard:** https://irado-dashboard-app.azurewebsites.net

---

## 💬 CONTACT

Voor vragen over deze infrastructuur:
- Technische vragen: Zie documentatie in `/opt/irado/`
- Cost management: Azure Cost Management dashboard
- Support: Azure Portal support tickets

---

**Versie:** 1.0  
**Datum:** 4 oktober 2025  
**Status:** ✅ Productie Ready  
**Approved by:** [Te vullen door Irado]

---

## 🎉 SAMENVATTING

**Complete AI Chatbot Infrastructuur voor €58.81/maand (bij 500 gesprekken)**

- ✅ 24/7 beschikbaarheid
- ✅ 99.95% uptime SLA
- ✅ Volledig geautomatiseerd
- ✅ Schaalbaar naar 10,000+ gesprekken
- ✅ GDPR compliant
- ✅ Volledige monitoring & logging
- ✅ Management dashboard inclusief

**ROI:** Automatisering van klantcontact, 24/7 service, directe QML integratie

**Potentiële optimalisatie:** -€19.25/maand met GPT-4o-mini (totaal €39.56/maand)

