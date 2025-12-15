# Irado Chatbot Dashboard

Een web-based dashboard voor het beheren van de KOAD blacklist en systeem configuratie.

## 🚀 Features

### KOAD Blacklist Management
- **KOAD Blacklist Management**: Bekijk, zoek, voeg toe, bewerk en verwijder entries
- **CSV Upload**: Upload nieuwe KOAD CSV bestanden
- **Real-time Statistics**: Overzicht van totale entries, actieve entries, unieke postcodes en straten
- **Search & Filter**: Zoek door de blacklist op straat, postcode, huisnummer of naam
- **Backup System**: Automatische backups bij wijzigingen

### Chat History Management
- **Chat Sessions Overview**: Bekijk alle chat sessions met statistieken
- **Message Search**: Zoek door alle chat berichten
- **Session Details**: Bekijk complete chat conversaties
- **Real-time Statistics**: Totaal sessions, berichten, activiteit vandaag/deze week
- **PostgreSQL Integration**: Directe verbinding met de chatbot database

## 📁 Structuur

```
dashboard/
├── dashboard.py          # Flask applicatie
├── start_dashboard.py    # Start script
├── requirements.txt      # Python dependencies
├── templates/
│   └── dashboard.html    # HTML template
├── static/
│   ├── css/
│   │   └── dashboard.css # Styling
│   └── js/
│       └── dashboard.js  # JavaScript functionaliteit
└── README.md            # Deze file
```

## 🛠️ Installatie

### Automatische Installatie (Aanbevolen)
```bash
cd /opt/irado/chatbot/dashboard
sudo ./install.sh
```

### Handmatige Installatie

1. **Installeer dependencies:**
   ```bash
   cd /opt/irado/chatbot/dashboard
   pip3 install -r requirements.txt
   ```

2. **Installeer als systemd service:**
   ```bash
   sudo cp irado-dashboard.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable irado-dashboard
   sudo systemctl start irado-dashboard
   ```

3. **Open in browser:**
   ```
   http://localhost:3255
   ```

### Service Management
```bash
# Start/stop/restart service
sudo systemctl start irado-dashboard
sudo systemctl stop irado-dashboard
sudo systemctl restart irado-dashboard

# Check status
sudo systemctl status irado-dashboard

# View logs
sudo journalctl -u irado-dashboard -f
```

## 📊 Functionaliteiten

### KOAD Blacklist Management

- **Bekijk alle entries** in een overzichtelijke tabel
- **Zoek en filter** op straat, postcode, huisnummer of naam
- **Voeg nieuwe entries toe** via het formulier
- **Bewerk bestaande entries** inline
- **Verwijder entries** met bevestiging
- **Upload CSV bestanden** om bulk updates te doen

### Statistics Dashboard

- **Totaal entries**: Totaal aantal KOAD entries
- **Actieve entries**: Aantal actieve entries
- **Unieke postcodes**: Aantal unieke postcodes
- **Unieke straten**: Aantal unieke straten

### Backup System

- Automatische backups worden gemaakt bij elke wijziging
- Backups worden opgeslagen in `/opt/irado/chatbot/backups/`
- Backup bestanden hebben timestamp: `koad_backup_YYYYMMDD_HHMMSS.csv`

## 🔧 API Endpoints

### KOAD Management
- **GET /api/koad** - Haal alle KOAD entries op
- **GET /api/koad/search?q=query** - Zoek in KOAD entries
- **POST /api/koad/add** - Voeg nieuwe KOAD entry toe
- **POST /api/koad/update** - Bewerk bestaande KOAD entry
- **POST /api/koad/delete** - Verwijder KOAD entry
- **POST /api/koad/upload** - Upload nieuwe CSV file
- **GET /api/stats** - Haal KOAD statistieken op

### Chat History Management
- **GET /api/chat/sessions** - Haal alle chat sessions op
- **GET /api/chat/sessions/<session_id>** - Haal specifieke chat session op
- **GET /api/chat/search?q=query** - Zoek in chat berichten
- **GET /api/chat/stats** - Haal chat statistieken op

## 📝 CSV Format

De KOAD CSV moet de volgende kolommen bevatten:

- `KOAD-nummer`: KOAD nummer
- `KOAD-str`: Straatnaam
- `KOAD-pc`: Postcode
- `KOAD-huisaand`: Huisletter
- `KOAD-huisnr`: Huisnummer
- `KOAD-etage`: Etage
- `KOAD-naam`: Naam
- `KOAD-actief`: Actief (1=ja, 0=nee)
- `KOAD-inwoner`: Inwoner (1=ja, 0=nee)

## 🔒 Beveiliging

- Het dashboard draait op localhost (127.0.0.1)
- Geen authenticatie geïmplementeerd (voor interne gebruik)
- Automatische backups bij wijzigingen
- Input validatie op alle formulieren

## 🐛 Troubleshooting

### Service niet start
```bash
# Check service status
sudo systemctl status irado-dashboard

# View logs
sudo journalctl -u irado-dashboard -f

# Restart service
sudo systemctl restart irado-dashboard
```

### Port 3255 al in gebruik
```bash
# Zoek proces op port 3255
sudo lsof -i :3255

# Stop het proces
sudo kill -9 <PID>
```

### Database verbinding problemen
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database configuratie
cat /opt/irado/chatbot/.env
```

### Dependencies niet geïnstalleerd
```bash
cd /opt/irado/chatbot/dashboard
pip3 install -r requirements.txt
```

### KOAD file niet gevonden
Controleer of `koad.csv` bestaat in `/opt/irado/chatbot/`

### Service logs bekijken
```bash
# Real-time logs
sudo journalctl -u irado-dashboard -f

# Recent logs
sudo journalctl -u irado-dashboard --since "1 hour ago"
```

## 📞 Support

Voor vragen of problemen, contacteer het Irado team.

## 🔄 Updates

Het dashboard wordt automatisch bijgewerkt wanneer de KOAD data verandert. Refresh de pagina om de nieuwste data te zien.
