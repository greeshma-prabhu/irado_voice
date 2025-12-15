## 🚀 Deployment & omgevingen

Dit document vat samen hoe de Irado Grofvuil Chatbot in Azure is ingericht en hoe deployments werken.

---

## 1. Overzicht omgevingen

In de basis wordt er gedeployed naar één Azure resource group (bijvoorbeeld `irado-rg`) met daarin:

- **Chatbot App Service**
  - Naam: `irado-chatbot-app`
  - URL: `https://irado-chatbot-app.azurewebsites.net`

- **Dashboard App Service**
  - Naam: `irado-dashboard-app`
  - URL: `https://irado-dashboard-app.azurewebsites.net`

- **PostgreSQL database**
  - Database: `irado_chat`

- **Azure Container Registry**
  - Bevat de Docker images voor chatbot en dashboard.

De deployment-scripts in deze repository zorgen ervoor dat alle benodigde resources worden aangemaakt/geüpdatet.

---

## 2. Eerste keer opzetten (nieuwe Azure-omgeving)

Stap-voor-stap uitgewerkt in:

- `AZURE_QUICKSTART.md` – 5-minuten quickstart.  
- `AZURE_ACCOUNT_SETUP.md` – volledige uitleg voor account, service principal en credentials.  

Samengevat:

1. Maak een Azure-account en subscription aan.  
2. Installeer Azure CLI en log in (`az login`).  
3. Maak een service principal aan voor deployments.  
4. Vul `/opt/irado-azure/.azure-credentials` met de juiste waardes.  
5. Maak een resource group aan (bijv. `irado-rg`).  

Daarna kun je de deployment-scripts draaien.

---

## 3. Standaard deployment scripts

In de root van de repository (`/opt/irado-azure`):

```bash
./deploy-to-azure.sh              # Chatbot deployment (10–15 min)
./deploy-dashboard-to-azure.sh    # Dashboard deployment (±5 min)
./quick-deploy.sh                 # Beide tegelijk (voor updates)
```

Wat deze scripts doen (samengevat, zie ook `README_DOCUMENTATIE.md`):

1. Build Docker images.  
2. Push images naar Azure Container Registry.  
3. Update de App Services om de nieuwe images te gebruiken.  
4. Zet/controleert environment variables.  
5. Voert health checks uit.  

---

## 4. Workflow voor wijzigingen (bestaande omgeving)

Aanbevolen werkwijze (zie ook `QUICK_DEV_GUIDE.md`):

1. **Lokaal ontwikkelen en testen**
   - Gebruik lokale development setup met verbinding naar Azure DB.
   - Run `app.py` en/of `dashboard.py` lokaal.
   - Test je wijziging met Postman/curl of via de lokale UI.

2. **Code review / testen**
   - Check dat de belangrijkste scenario’s werken (chat, routing, e‑mail, dashboard).

3. **Deploy naar Azure**
   - In `/opt/irado-azure`:

   ```bash
   ./quick-deploy.sh
   ```

   - Of afzonderlijk:

   ```bash
   ./deploy-to-azure.sh
   ./deploy-dashboard-to-azure.sh
   ```

4. **Na deployment**
   - Controleer health endpoints:

   ```bash
   curl https://irado-chatbot-app.azurewebsites.net/health
   curl https://irado-dashboard-app.azurewebsites.net/
   ```

   - Bekijk (kort) de Azure logs voor eventuele errors.

---

## 5. Kosten & infra-opties

De kosten en varianten zijn uitgewerkt in:

- `IRADO_INFRASTRUCTUUR_VOORSTEL.md` – standaard infrastructuur (~€58,53/maand bij 500 gesprekken).  
- `IRADO_INFRASTRUCTUUR_PREMIUM.md` – premium setup (~€119,13/maand met extra redundantie).  
- `AZURE_KOSTEN_ANALYSE.md` – gedetailleerde cost breakdown en optimalisaties.  

Gebruik deze documenten bij:
- budgetbesprekingen,
- schaalbeslissingen,
- keuzes voor premium / standaard setup.

---

## 6. Meer details

Voor uitgebreide technische details, foutafhandeling en monitoring:

- `README_DOCUMENTATIE.md` – centrale technische documentatie, inclusief monitoring, troubleshooting en changelog.  
- `DASHBOARD_AZURE_DEPLOYMENT.md` – details rond dashboard-deploy.  
- `DASHBOARD_QUICKSTART.md` – snelle start speciaal voor het dashboard.  
- `QUICK_DEV_GUIDE.md` – versnellen van de ontwikkelcyclus (lokaal testen i.p.v. steeds naar Azure).  

Deze Nextcloud-pagina is bedoeld als samenvatting; gebruik de genoemde bestanden voor verdieping.


