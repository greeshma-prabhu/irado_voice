## 🧑‍💻 Gebruik door Irado-medewerkers

Dit document beschrijft hoe Irado-medewerkers de Grofvuil Chatbot en het dashboard in de praktijk gebruiken.

---

## 1. Hoe inwoners de chatbot gebruiken

- Inwoners openen de chat via de Irado website (widget).
- De chatbot stelt gerichte vragen:
  - Wat wil de inwoner aanbieden? (bijvoorbeeld bank, kast, matras)
  - Hoeveel stuks / volume?
  - Zijn er bijzonderheden (bijv. trap, lift, slechte bereikbaarheid)?
- Op basis van de antwoorden:
  - Bepaalt de chatbot de juiste route(s).
  - Bereidt de benodigde informatie voor de planning/uitvoering voor.

Resultaat:
- De inwoner krijgt direct duidelijkheid (wat mag wel/niet, hoe werkt ophalen).
- De medewerker krijgt later een goed gevulde melding per e‑mail.

---

## 2. Dashboard – waar gebruik je het voor?

Dashboard-URL:  
`https://irado-dashboard-app.azurewebsites.net`

Belangrijkste functies:

- **Logs bekijken**
  - Tab *Logs*:
    - Chatbot Live Logs (lopend verkeer).
    - Dashboard Activity Logs (o.a. CSV-upload, systeemacties).
  - Handig voor:
    - Controleren of e‑mails zijn verstuurd.
    - Inzien welke routes en items aan een aanvraag zijn gekoppeld.

- **KOAD CSV-upload**
  - Tab *Bedrijfsklanten* (of vergelijkbare naam in de UI).
  - Upload van `koad.csv` om KOAD-data in de database te verversen.
  - Zie voor details: `CSV_UPLOAD_IMPROVEMENTS.md` en dashboard-documentatie.

---

## 3. Hoe komen meldingen bij het team terecht?

De chatbot gebruikt toolcalls om e‑mails te versturen:

- **E‑mail naar team**  
  - Per route wordt één e‑mail verstuurd met:
    - Gegevens van de inwoner.
    - Geselecteerde items en volumes.
    - Bijzonderheden / opmerkingen.

- **E‑mail naar klant**  
  - De klant krijgt een samenvatting:
    - Welke routes zijn aangemaakt.
    - Welke stukken grofvuil zijn opgegeven.
    - Eventuele afspraken of aanvullende instructies.

In de dashboard-logs zijn deze e‑mails als gestructureerde JSON terug te vinden (handig voor debugging).

---

## 4. Standaard werkstroom voor medewerkers

1. **Inwoner gebruikt de chatbot**  
   - De chatbot begeleidt de inwoner door de vragen.
2. **Medewerker ontvangt e‑mail(s)**  
   - Controleer of de gegevens compleet zijn.
3. **Eventueel vervolgactie**  
   - Aanmaak opdracht in interne systemen.
   - Contact opnemen met klant bij onduidelijkheden.
4. **Optioneel: dashboard checken**  
   - Bij twijfel: open de logs in het dashboard om precies te zien wat de chatbot heeft geregistreerd.

---

## 5. Wat te doen bij problemen (korte versie)

Voor een snelle eerste check door medewerkers:

- **Chatbot reageert niet / foutmelding in de widget**
  - Probeer de chatbot-URL direct in de browser:
    - `https://irado-chatbot-app.azurewebsites.net/health`
  - Werkt dit niet? Schakel een beheerder / developer in.

- **Je mist e‑mails van de chatbot**
  - Controleer eerst je SPAM / ongewenste mail.
  - Check in het dashboard onder *Logs* of de toolcalls en e‑mails zijn gelogd.
  - Zo niet: vraag een beheerder om de technische status te controleren.

Voor diepere troubleshooting (database, Azure, OpenAI) zie het document  
`04-beheer-en-operations.md`.


