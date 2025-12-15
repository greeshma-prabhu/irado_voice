## 🛠️ Technisch overzicht & architectuur

Dit document geeft een technisch overzicht van de Irado Grofvuil Chatbot: componenten, dataflows en gebruikte diensten.

---

## 1. Hoofdcomponenten

De belangrijkste onderdelen (op hoog niveau):

- **Chatbot backend (Flask / Python)**  
  - API-endpoint voor chatverkeer (`/api/chat`).  
  - Verwerkt inkomende berichten, bewaart sessies en roept Azure OpenAI aan.  
  - Gebruikt toolcalls voor:
    - Routering en volume-berekening.
    - E‑mails genereren naar team en klant.

- **Dashboard backend (Flask / Python)**  
  - Beheerinterface voor:
    - Logs (toolcalls, e‑mails, errors).
    - CSV-upload (KOAD-data).  
  - Draait in een eigen Azure App Service.

- **Website widget (HTML/JS)**  
  - Embedded chatvenster op de Irado website.  
  - Maakt HTTP(S)-requests naar de chatbot backend.

- **PostgreSQL database**  
  - Tabelgroepen:
    - `sessions`, `messages`: gesprekken.  
    - `system_prompts`: actieve AI-system prompt.  
    - `dashboard_logs`: logging vanuit dashboard en chatbot.  
    - KOAD-gerelateerde tabellen (bedrijfsklanten).

- **Azure OpenAI**  
  - Model: `gpt-4o` / `o4-mini` (zie configuratie).  
  - Verwerkt prompts en toolcalls met strikte JSON-schema’s voor routes en e‑mails.

Een ASCII-overzicht staat ook in `README_DOCUMENTATIE.md` onder *System Overview*.

---

## 2. Architectuur in Azure

Belangrijkste Azure-resources:

- **App Services**
  - `irado-chatbot-app` – draait de chatbot backend container.
  - `irado-dashboard-app` – draait de dashboard backend container.

- **Azure Container Registry**
  - Bevat Docker images:
    - `irado-chatbot:latest`
    - `irado-dashboard:latest`
  - Deployment-scripts bouwen en pushen nieuwe images hierheen.

- **Azure Database for PostgreSQL**
  - Eén hoofd-database (`irado_chat`) na de migratie (zie `DATABASE_MIGRATION_COMPLETE.md`).
  - Eventuele KOAD / bedrijfsklanten-database is geconsolideerd of gekoppeld volgens de migratie-documentatie.

- **Azure OpenAI resource**
  - Endpoint en key worden via environment variables geconfigureerd.
  - Wordt door de chatbot backend gebruikt.

- **Storage & Key Vault (optioneel / aanbevolen)**
  - Voor back-ups, bestanden en secrets.

---

## 3. Belangrijke scripts en configuratie

- **Deployment scripts (root van de repo)**
  - `deploy-to-azure.sh` – deployt de chatbot.  
  - `deploy-dashboard-to-azure.sh` – deployt het dashboard.  
  - `quick-deploy.sh` – snelle gecombineerde deployment.

- **Configuratiebestanden**
  - `.azure-credentials` – lokaal bestand met Azure-credentials (niet in git).  
  - `.env` in `chatbot/` – applicatie secrets (niet in git).  
  - Applicatie-instellingen in Azure App Service → *Configuration*.

- **Prompts & AI-config**
  - `chatbot/prompts/system_prompt.txt` – centrale system prompt (versie 2.0, multi-route logica).  
  - De actieve promptversie staat in de tabel `system_prompts`.

Zie `README_DOCUMENTATIE.md` en `AZURE_DEPLOYMENT_GUIDE.md` voor meer technische details.

---

## 4. Dataflow van een gesprek (vereenvoudigd)

1. **Gebruiker stuurt bericht via de widget**  
   - Request naar `irado-chatbot-app` (`/api/chat`).
2. **Chatbot backend**
   - Slaat het bericht op in de database.
   - Roept Azure OpenAI aan met system prompt + gesprekshistorie.
3. **AI-model**
   - Bepaalt of er toolcalls nodig zijn (bijv. route-berekening, e‑mail).
   - Stuurt gestructureerde JSON terug (tool payloads).
4. **Backend voert tools uit**
   - Past routeringslogica toe.
   - Stelt e‑mails op (team en klant).
   - Schrijft logs in `dashboard_logs`.
5. **Antwoord naar gebruiker**
   - Gebruiker krijgt een tekstueel antwoord in de chat.
   - (Later) worden e‑mails verstuurd naar team en klant.

---

## 5. Verdere technische documentatie

Voor meer diepgang:

- `README_DOCUMENTATIE.md` – compleet technisch overzicht, incl. kosten, monitoring en troubleshooting.  
- `AZURE_DEPLOYMENT_GUIDE.md` – volledige uitleg deployment naar Azure.  
- `AZURE_ACCOUNT_SETUP.md` en `AZURE_QUICKSTART.md` – inrichting Azure-account + snelle start.  
- `QUICK_DEV_GUIDE.md` – handleiding voor lokale ontwikkeling en debugging.  

Gebruik deze Nextcloud-pagina als “kaart” en klik vervolgens door naar de specifieke bestanden in de repository als je meer detail nodig hebt.


