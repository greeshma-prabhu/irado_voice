## 🔗 Belangrijke links & brondocumenten

Deze pagina geeft een overzicht van de belangrijkste URLs en .md-bestanden die bij het Irado Grofvuil Chatbot project horen.

---

## 1. Productie-URLs

- **Chatbot (backend / health)**  
  - `https://irado-chatbot-app.azurewebsites.net`  
  - `https://irado-chatbot-app.azurewebsites.net/health`

- **Dashboard**  
  - `https://irado-dashboard-app.azurewebsites.net`

---

## 2. Centrale documentatiebestanden

In de root van de repository (`/opt/irado-azure`):

- `START_HIER.txt`  
  - Ultra-korte “start hier”-uitleg voor nieuwe gebruikers.

- `README_DOCUMENTATIE.md`  
  - Hoofdindex van alle technische documentatie.
  - Verwijst naar quickstarts, kostenoverzichten, infra-plannen, troubleshooting, enz.

- `AZURE_QUICKSTART.md`  
  - 5-minuten quickstart voor nieuwe Azure-omgevingen.

- `AZURE_ACCOUNT_SETUP.md`  
  - Volledige beschrijving van Azure-account, service principal en credentials.

- `AZURE_DEPLOYMENT_GUIDE.md`  
  - Uitgebreide handleiding voor deployment naar Azure.

- `DASHBOARD_QUICKSTART.md`  
  - Korte gids om het dashboard te deployen en gebruiken.

- `DASHBOARD_AZURE_DEPLOYMENT.md`  
  - Specifieke details over de dashboard-deployment.

- `IRADO_INFRASTRUCTUUR_VOORSTEL.md`  
- `IRADO_INFRASTRUCTUUR_PREMIUM.md`  
- `AZURE_KOSTEN_ANALYSE.md`  
  - Kosten, varianten en analyses van de Azure-infrastructuur.

- `DATABASE_MIGRATION_COMPLETE.md`  
  - Uitleg over database-migratie en huidige stand van de database.

---

## 3. Ontwikkeling & debugging

- `QUICK_DEV_GUIDE.md`  
  - Snel lokaal ontwikkelen (met Azure DB) in plaats van steeds naar Azure te deployen.
  - Uitleg over verschillende ontwikkelmodi (local, Docker, Azure).

- `STATUS_REPORT_GPT4O.md`  
  - Statusrapport over de AI-configuratie / GPT-4o (indien aanwezig en actueel).

- `n8n_optimization_summary.md`, `n8n_workflow_optimization.md`  
  - Documenten rondom optimalisatie van n8n-workflows.

---

## 4. Data & analyses

In de map `data/`:

- `belangrijkste_verschillen_samenvatting.md`  
- `grofvuil_vergelijking_analyse.md`  
- `finale_kritieke_verschillen.md`  

Deze bestanden bevatten analyses en samenvattingen over verschillen tussen oude en nieuwe flows / datasets rond grofvuil.

---

## 5. Testen

- `test_questions.md`  
  - Verzameling testvragen voor de chatbot.

- Shell-scripts voor testflows in de root, bijvoorbeeld:
  - `test_30_questions.sh`
  - `test_30_questions_comprehensive.sh`
  - `test-complete-email-flow.sh`

Deze scripts kunnen gebruikt worden om regressietests of uitgebreide scenario’s te draaien.

---

## 6. Waar deze Nextcloud-pagina’s voor zijn

De Nextcloud-Collectives map `nextcloud/` is bedoeld als **leesbare samenvatting** voor:

- management en niet-technische stakeholders,
- beheerders / super users,
- developers die snel context willen.

Voor diepere technische details gebruik je altijd de brondocumenten hierboven (in de repository zelf).  
Zie ook:

- `01-projectoverzicht.md` – functioneel overzicht.  
- `03-technisch-overzicht-en-architectuur.md` – technische samenvatting.  
- `05-deployment-en-omgevingen.md` – hoe en waar er wordt gedeployed.  


