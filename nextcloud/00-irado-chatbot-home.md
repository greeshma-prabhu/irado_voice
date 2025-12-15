## 🤖 Irado Grofvuil Chatbot

Welkom bij de Irado Grofvuil Chatbot!  
Deze pagina is de hoofdingang voor iedereen die wil begrijpen **wat** de chatbot doet, **waarom** hij er is en **hoe** je hem gebruikt.

---

## 🌍 Wat is de grofvuil chatbot?

De grofvuil chatbot is een digitale hulpverlener die inwoners helpt bij:

- vragen over grofvuil en andere afvalstromen;
- het plannen of aanvragen van een grofvuilafspraak;
- duidelijkheid geven over wat wel en niet mag worden aangeboden;
- het verminderen van wachttijden aan de telefoon en in de mailbox.

De chatbot draait in Azure en maakt gebruik van AI (Azure OpenAI), maar is zó ingericht dat hij binnen de Irado-regels en ‑afspraken blijft.

---

## 🎯 Waarom doen we dit?

- **Betere service voor inwoners**  
  24/7 beschikbaar, direct antwoord, geen wachtrij.

- **Minder werkdruk voor medewerkers**  
  Minder herhaalvragen via telefoon en e‑mail; aanvragen zijn vollediger en beter gestructureerd.

- **Meer grip op informatie**  
  Gesprekken en aanvragen worden gelogd, zodat we kunnen analyseren, verbeteren en bijsturen.

---

## 🧑‍🤝‍🧑 Voor wie is deze documentatie?

Deze Collectives-ruimte is bedoeld voor:

- **Irado-medewerkers (klantenservice / planning)**  
  Om te begrijpen wat de chatbot doet, welke informatie hij verzamelt en wat er in de e‑mails staat.

- **Beheerders / super users**  
  Voor dagelijks beheer, monitoring en eenvoudige probleemoplossing.

- **Management / beleidsmakers**  
  Voor inzicht in de werking, kosten en mogelijkheden van de oplossing.

- **Developers / technisch beheer**  
  Als startpunt om door te klikken naar de technische documentatie en bronbestanden.

---

## 💬 Hoe gebruiken inwoners de chatbot?

Inwoners:

- gaan naar de Irado-website waar de chatwidget zichtbaar is;
- stellen hun vraag in gewone taal (bijvoorbeeld: *“Ik wil een oude bank laten ophalen”*);
- worden stap voor stap door de chatbot begeleid:
  - wat voor object(en),
  - hoeveel,
  - bijzondere omstandigheden (trap, lift, bereikbaarheid),
  - contactgegevens.

De chatbot:

- geeft direct uitleg en spelregels;
- maakt, waar nodig, een of meerdere routes/aanvragen aan;
- zorgt dat het team en de klant per e‑mail een duidelijke samenvatting krijgen.

Zie voor details: `02-gebruik-door-irado.md`.

---

## 🧱 Hoe zit het technisch in elkaar? (heel kort)

Op hoofdlijnen:

- Een **chatbot backend** in Python (Flask) die:
  - gesprekken afhandelt,
  - AI (Azure OpenAI) aanroept,
  - toolcalls uitvoert (routes bepalen, e‑mails maken),
  - data opslaat in een PostgreSQL-database.

- Een **dashboard** waarmee we:
  - logs en foutmeldingen kunnen zien,
  - KOAD-data (bedrijfsklanten) kunnen uploaden via CSV.

- De chatbot en het dashboard draaien als **Azure App Services**, met Docker images vanuit een **Azure Container Registry**.

Voor een uitgebreider technisch overzicht: `03-technisch-overzicht-en-architectuur.md`.

---

## 📚 Waar kan ik wat vinden?

Gebruik in deze Collectives-ruimte vooral de volgende pagina’s:

- `01-projectoverzicht.md` – samenvatting van het hele project.  
- `02-gebruik-door-irado.md` – praktisch gebruik voor medewerkers.  
- `03-technisch-overzicht-en-architectuur.md` – technische samenvatting.  
- `04-beheer-en-operations.md` – dagelijks beheer en troubleshooting.  
- `05-deployment-en-omgevingen.md` – hoe en waar alles draait in Azure.  
- `06-links-en-brondocumenten.md` – alle belangrijke links en bron-`.md`’s.

De onderliggende, meer technische documentatie staat in de repository (`/opt/irado-azure`) en is daar als `.md`-bestand te lezen.

---

## 📞 Vragen of verbeteringen?

- Heb je inhoudelijke vragen over grofvuil of de teksten richting inwoners?  
  → Neem contact op met het inhoudelijk verantwoordelijke team binnen Irado.

- Heb je vragen over techniek, storingen of uitbreidingen?  
  → Neem contact op met de technische beheerder / developer van dit project.

Gebruik deze hoofdpagina als startpunt; vanuit hier kun je doorlinken naar de pagina’s die voor jouw rol het meest relevant zijn.


