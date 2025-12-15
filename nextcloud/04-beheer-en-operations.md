## 🧯 Beheer & operations (dagelijks gebruik en support)

Dit document is bedoeld voor beheerders / technisch aanspreekpunt binnen Irado.

---

## 1. Dagelijkse controles (korte checklist)

1. **Werkt de chatbot?**
   - Open de health-URL in de browser:
     - `https://irado-chatbot-app.azurewebsites.net/health`
2. **Werkt het dashboard?**
   - Open:
     - `https://irado-dashboard-app.azurewebsites.net`
3. **Geen opvallende fouten in de logs?**
   - Ga in het dashboard naar de tab *Logs*:
     - Controleer recente `ERROR`- of `EXCEPTION`-meldingen.

Als dit er allemaal goed uitziet, is de basis-werking in orde.

---

## 2. Monitoring & logging

### Via Azure CLI

Zie ook `README_DOCUMENTATIE.md` onder *Monitoring & Logs*.

- **Chatbot logs (live tail)**

```bash
az webapp log tail --name irado-chatbot-app --resource-group irado-rg
```

- **Dashboard logs (live tail)**

```bash
az webapp log tail --name irado-dashboard-app --resource-group irado-rg
```

### Via dashboard UI

- Open: `https://irado-dashboard-app.azurewebsites.net`
- Ga naar tab *Logs*:
  - Filter op `TOOL_CALL`, `EMAIL_TO_TEAM`, `EMAIL_TO_CUSTOMER`, `ERROR`.
  - Gebruik dit om te zien:
    - Welke toolcalls zijn uitgevoerd.
    - Welke e‑mails zijn verstuurd.
    - Of er fouten optreden bij CSV-upload of AI-calls.

---

## 3. Veelvoorkomende problemen (beheer)

### 3.1 Chatbot down / foutmeldingen in widget

Te zien als:
- De widget toont een foutmelding.
- Health-URL (`/health`) geeft geen `200 OK`.

Acties:
1. Check logs (Azure CLI of dashboard).  
2. Herstart de App Service:

```bash
az webapp restart --name irado-chatbot-app --resource-group irado-rg
```

3. Controleer na een paar minuten opnieuw de health-URL.

### 3.2 Databaseproblemen

Symptomen:
- Fouten over database-connecties in de logs.
- Chatbot of dashboard start niet goed op.

Acties:
1. Controleer firewall / netwerkregels bij de Azure PostgreSQL instantie.  
2. Verifieer de credentials in Azure App Service → *Configuration*.  
3. Raadpleeg `DATABASE_MIGRATION_COMPLETE.md` voor details over de database-setup.

### 3.3 OpenAI / AI-problemen

Symptomen:
- Fouten in logs over OpenAI API-key of endpoint.
- Chatbot lijkt geen goede antwoorden meer te geven.

Acties:
1. Check environment variables in Azure App Service:
   - `AZURE_OPENAI_API_KEY` (of gelijkwaardige variabele).
   - `AZURE_OPENAI_ENDPOINT`.
2. Controleer of het gebruikte model/deployment nog bestaat in Azure OpenAI.

---

## 4. CSV-upload (KOAD) beheer

De KOAD-data wordt via het dashboard ingelezen:

1. Ga naar `https://irado-dashboard-app.azurewebsites.net`.
2. Open de tab voor bedrijfsklanten / KOAD (zie UI).
3. Upload de nieuwste `koad.csv`.
4. Controleer in de logs of:
   - De upload succesvol was.
   - Eventuele fouten duidelijk worden weergegeven.

Voor details over kolommen, validatie en verbeteringen:
- Zie `CSV_UPLOAD_IMPROVEMENTS.md`.  
- Zie de dashboard-gerelateerde documentatie (bijv. `DASHBOARD_LOGGING_COMPLETE.md` als aanwezig).

---

## 5. Escalatie / wanneer developer inschakelen

Schakel een developer in als:

- Deployments blijven mislukken, ondanks juiste Azure-credentials.
- De database-corrupt lijkt of structurele fouten geeft.
- AI-antwoorden structureel fout zijn en niet komen door content, maar door logica/toolcalls.
- Er wijzigingen nodig zijn in:
  - System prompt (`chatbot/prompts/system_prompt.txt`).
  - Routeringslogica / tool-implementatie.
  - Dashboardfunctionaliteit.

Voor developers en technisch beheer is het document  
`05-deployment-en-omgevingen.md` de volgende stap.


