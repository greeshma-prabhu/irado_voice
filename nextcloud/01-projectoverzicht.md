## 🧩 Projectoverzicht – Irado Grofvuil Chatbot

Dit document geeft een functioneel en inhoudelijk overzicht van de Irado Grofvuil Chatbot zoals die in Azure draait.

---

## 🎯 Doel van de chatbot

- **Onderwerp**: grofvuil, afvalstromen en bijbehorende afspraken.
- **Doelgroep**: inwoners en medewerkers van Irado.
- **Hoofddoelen**:
  - Inwoners snel en correct antwoord geven op grofvuil-vragen.
  - Bel- en e‑mailvolume bij medewerkers verminderen.
  - Aanvragen en meldingen zo volledig mogelijk voorbereiden voor de backoffice.

De chatbot combineert:
- AI (Azure OpenAI) voor taalbegrip en dialoog,
- vaste regels en tools voor routes, afspraken en e‑mails,
- logging en dashboarding voor beheer en inzicht.

---

## 🧑‍🤝‍🧑 Belangrijke rollen

- **Inwoner**  
  Stelt vragen via de chat (web-widget op de Irado site).

- **Irado-medewerker (klantenservice / planning)**  
  - Bekijkt aanvragen en meldingen.
  - Krijgt e‑mails met de resultaten van de chatbot (routes, volumes, opmerkingen).
  - Gebruikt het dashboard voor logging en CSV-upload (KOAD-data).

- **Beheerder / super user**  
  - Houdt de omgeving in de gaten (logging, foutmeldingen).
  - Monitort kosten en performance.

- **Developer / technisch beheer**  
  - Past code aan.
  - Beheert deployments naar Azure.
  - Houdt de database en integraties (OpenAI, e‑mail, KOAD) in orde.

---

## 🏗️ Hoofdcomponenten

Op hoofdlijnen bestaat het systeem uit:

- **Chatbot backend (`chatbot/`)**
  - Flask API voor chatverkeer.
  - AI-integratie (Azure OpenAI).
  - Toolcalls voor o.a.:
    - routebepaling,
    - e‑mail naar team,
    - e‑mail naar klant.
  - Opslag van sessies, berichten en logs in PostgreSQL.

- **Dashboard (beheer-UI)**  
  - Flask webapp voor:
    - bekijken van logs (toolcalls, e‑mails, fouten),
    - uploaden van KOAD CSV-data,
    - health checks en debug-informatie.

- **Website widget (`website/`)**  
  - Frontend (HTML/JS) die de chat integreert in de Irado website.
  - Praat via HTTP(S) met de chatbot backend.

- **Azure infrastructuur**
  - App Services voor chatbot en dashboard.
  - PostgreSQL database.
  - Azure Container Registry voor Docker images.
  - Azure OpenAI voor de taalmodellen.

Een visueel plaatje hiervan staat in `README_DOCUMENTATIE.md` onder *System Overview*.

---

## 🌐 Belangrijke URLs (productie)

- **Chatbot**  
  `https://irado-chatbot-app.azurewebsites.net`

- **Dashboard**  
  `https://irado-dashboard-app.azurewebsites.net`

- **Chat widget (ingebed)**  
  Via de Irado website, gebruikt de chatbot-URL hierboven als backend.

---

## 📦 Belangrijkste bronbestanden

In deze repository (`/opt/irado-azure`) zijn vooral de volgende documenten relevant:

- `README_DOCUMENTATIE.md` – centrale index van alle technische documentatie.  
- `START_HIER.txt` – korte “start hier”-uitleg voor nieuwe gebruikers.  
- `AZURE_QUICKSTART.md` – snelle Azure-setup en eerste deployment.  
- `AZURE_DEPLOYMENT_GUIDE.md` – uitgebreide deployment handleiding.  
- `IRADO_INFRASTRUCTUUR_VOORSTEL.md` en `IRADO_INFRASTRUCTUUR_PREMIUM.md` – kosten en infra-opties.  
- `DASHBOARD_QUICKSTART.md` en `DASHBOARD_AZURE_DEPLOYMENT.md` – dashboard-specifieke info.  

In de overige Nextcloud-pagina’s linken we naar deze bestanden waar nodig.


