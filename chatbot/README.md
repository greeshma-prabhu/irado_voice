# Irado Chatbot System

Ein vollständiges Chatbot-System für Irado mit Adressvalidierung und Service Area Management.

**🚀 Live op Azure:** https://irado-chatbot-app.azurewebsites.net  
**📊 Dashboard:** https://irado-dashboard-app.azurewebsites.net  
**📚 Deployment Guides:**
- [Azure Chatbot Deployment](../AZURE_DEPLOYMENT_GUIDE.md)
- [Dashboard Deployment](../DASHBOARD_AZURE_DEPLOYMENT.md) 🆕
- [Dashboard Quick Start](../DASHBOARD_QUICKSTART.md) 🚀

## 🚀 Features

### Core Chatbot
- **AI-Powered Conversations**: OpenAI GPT Integration
- **Session Management**: Benutzer-spezifische Gespräche
- **Email Integration**: Automatische Email-Versendung
- **Database Integration**: PostgreSQL für Datenpersistierung

### Dashboard Management 📊
- **Bedrijfsklanten Management**: Web-based interface voor bedrijfsklanten beheer (was: KOAD blacklist)
- **Chat History Viewer**: Bekijk alle chat conversaties en statistieken
- **System Prompt Editor**: Live aanpassen van chatbot system prompts met versioning
- **Real-time Statistics**: Live overzicht van systeem performance
- **Database Integration**: Alles opgeslagen in Azure PostgreSQL
- **Systemd Service**: Automatische startup en monitoring (lokaal) of Azure Web App (cloud)


### Address Validation 🏠
- **Open Postcode API**: Niederländische Adressvalidierung
- **Service Area Check**: Capelle, Schiedam, Vlaardingen
- **KOAD Blacklist**: Geschäftsadressen werden blockiert
- **Real-time Validation**: Sofortige Adressprüfung

### Security & Performance 🔒
- **Rate Limiting**: API-Schutz vor Missbrauch
- **Authentication**: Basic Auth für alle Endpoints
- **HTTPS Support**: Sichere Datenübertragung
- **Systemd Integration**: Automatischer Service-Start

## 📋 System Requirements

- Python 3.8+
- PostgreSQL
- OpenAI API Key
- Moderner Browser

## 🛠 Installation

### 1. Repository Setup
```bash
cd /opt/irado/chatbot
git clone <repository-url>
cd chatbot
```

### 2. Python Environment
```bash
# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# OpenAI API Key
export OPENAI_API_KEY="your-openai-api-key"

# Database Configuration
export DATABASE_URL="postgresql://user:password@localhost/chatbot"

# Address Validation
export OPEN_POSTCODE_API_BASE_URL="https://api.openpostcode.nl"
export ADDRESS_VALIDATION_ENABLED="true"
export SERVICE_AREA_VALIDATION_ENABLED="true"
```

### 4. Service Installation
```bash
# Systemd Service installieren
sudo cp irado-chatbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable irado-chatbot
sudo systemctl start irado-chatbot
```

## 🚀 Quick Start

### 1. Service starten
```bash
sudo systemctl start irado-voice-chatbot
sudo systemctl status irado-voice-chatbot | cat
```

### 2. Health Check
```bash
curl http://localhost:5000/health
```

### 3. Voice Chat öffnen
Öffne: `http://localhost:5000/voice-chat`

### 4. API Test
```bash
# Voice API Test
curl -X GET "http://localhost:5000/api/voice/test" \
  -H "Authorization: Basic $(echo -n 'irado:20Irado25!' | base64)"
```

## 📚 API Documentation

### Core Endpoints
- `GET /health` - Service Health Check
- `POST /api/chat` - Chatbot Conversation (structured UI payload for website widget)
- `GET /api/sessions` - Session Management

#### /api/chat – Response format for the website widget

```json
{
  "output": {
    "text": "bot response for the user (markdown supported)",
    "language": "nl",
    "buttons": [
      {
        "id": "yes_option",
        "label": "Ja",
        "value": "Ja",
        "variant": "primary"
      },
      {
        "id": "no_option",
        "label": "Nee",
        "value": "Nee",
        "variant": "secondary"
      }
    ],
    "showAfvalplaatsImage": false
  }
}
```

- `text`: main content for the user (website renders markdown formatting).
- `language`: current conversation language (`nl`, `en`, `tr`, `ar`).
- `buttons`: optional interactive buttons (for example for yes/no questions).
- `showAfvalplaatsImage`: when `true`, the website shows the example image that
  clearly indicates where bulky waste should be placed on the street.

### Voice Endpoints
- `POST /api/voice/tts` - Text-to-Speech
- `POST /api/voice/stt` - Speech-to-Text
- `POST /api/voice/process` - Complete Voice Processing
- `GET /api/voice/voices` - Available Voices
- `GET /api/voice/test` - Voice API Test

### Frontend
- `GET /voice-chat` - Voice Chat Widget
- `GET /` - Main Chatbot Interface

### Authentication
Alle API Endpoints erfordern Basic Authentication:
```
Authorization: Basic <base64(username:password)>
```
Standard: `irado:20Irado25!`

## 🎤 Voice Features

### Verfügbare Stimmen
- **alloy**: Neutrale, ausgewogene Stimme
- **echo**: Klare, professionelle Stimme
- **fable**: Warme, freundliche Stimme
- **onyx**: Tiefe, resonante Stimme
- **nova**: Süße, sanfte Stimme (Standard)
- **shimmer**: Helle, artikulierende Stimme

### Voice Widget Features
- **Audio Recording**: Start/Stop Recording
- **Voice Selection**: Dropdown für Stimmen
- **Audio Playback**: Bot-Antworten abspielen
- **Status Indicators**: Recording/Processing Status
- **Responsive Design**: Mobile und Desktop optimiert

## 🏠 Address Validation

### Service Areas
- Capelle aan den IJssel
- Schiedam
- Vlaardingen

### Features
- **Real-time Validation**: Open Postcode API
- **Business Address Blocking**: KOAD Blacklist
- **Service Area Check**: Automatische Prüfung
- **Address Formatting**: Standardisierte Adressen

## 🧪 Testing

### Automatisierte Tests
```bash
# Voice Integration Test
cd /opt/irado/chatbot
source venv/bin/activate
python3 voice/tests/test_voice_integration.py

# Address Validation Test
python3 test_address_validation.py

# Complete System Test
python3 test_complete_system.py
```

### Manuelle Tests
1. **Voice Chat**: `http://localhost:5000/voice-chat`
2. **API Endpoints**: Mit curl oder Postman
3. **Address Validation**: Test-Adressen eingeben

## 📊 Monitoring

### Service Status
```bash
# Service Status
sudo systemctl status irado-voice-chatbot | cat

# Live Logs
sudo journalctl -u irado-voice-chatbot -f | cat

# Health Check
curl -s http://localhost:5000/health | jq
```

### Performance Monitoring
```bash
# CPU/Memory Usage
ps aux | grep python | grep app.py

# Network Connections
netstat -tlnp | grep :5000

# OpenAI API Usage
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/usage
```

## 🔧 Troubleshooting

### Häufige Probleme

#### 1. OpenAI API Quota Exceeded
**Symptom:** 500 Fehler bei Voice API Calls
**Lösung:** OpenAI API Quota prüfen und erweitern

#### 2. Service startet nicht
**Symptom:** `systemctl status` zeigt "failed"
**Lösung:**
```bash
sudo journalctl -u irado-voice-chatbot -n 50 | cat
sudo systemctl restart irado-voice-chatbot
```

#### 3. Mikrofon-Zugriff verweigert
**Symptom:** "Microphone access denied"
**Lösung:** HTTPS verwenden und Browser-Berechtigungen prüfen

### Debug Commands
```bash
# Service Logs
sudo journalctl -u irado-voice-chatbot -f | cat

# API Test
curl -X GET "http://localhost:5000/api/voice/test" \
  -H "Authorization: Basic $(echo -n 'irado:20Irado25!' | base64)"

# Voice Integration Test
python3 voice/tests/test_voice_integration.py
```

## 📁 Projektstruktur

```
chatbot/
├── app.py                          # Haupt-Flask Anwendung
├── voice_chatbot_service.py        # Voice Service
├── ai_service.py                   # AI Service
├── email_service.py               # Email Service
├── database.py                    # Database Manager
├── config.py                      # Konfiguration
├── requirements.txt               # Python Dependencies
├── irado-voice-chatbot.service    # Systemd Service
├── voice/                         # Voice Integration
│   ├── docs/                      # Dokumentation
│   │   ├── COMPREHENSIVE_DOCUMENTATION.md
│   │   ├── API_REFERENCE.md
│   │   └── FRONTEND_INTEGRATION.md
│   ├── tests/                     # Tests
│   │   └── test_voice_integration.py
│   └── README.md                  # Voice-spezifische Docs
├── static/                        # Frontend Assets
│   └── voice-chat-widget.html     # Voice Widget
└── tests/                         # System Tests
    ├── test_complete_system.py
    ├── test_address_validation.py
    └── test_voice_integration.py
```

## 📊 Dashboard Management

### Dashboard Installation
```bash
cd /opt/irado/chatbot/dashboard
sudo ./install.sh
```

### Dashboard Access
- **URL**: http://localhost:3255
- **Features**: KOAD blacklist management, chat history viewer
- **Service**: `irado-dashboard.service`

### Dashboard Commands
```bash
# Service management
sudo systemctl start irado-dashboard
sudo systemctl stop irado-dashboard
sudo systemctl restart irado-dashboard
sudo systemctl status irado-dashboard

# View logs
sudo journalctl -u irado-dashboard -f
```

## 🔒 Sicherheit

### Authentication
- Basic Authentication für alle Endpoints
- Rate Limiting für API-Schutz
- Session-basierte Authentifizierung

### Datenübertragung
- HTTPS für alle Voice-Kommunikation
- Base64-Kodierung für Audio-Daten
- Keine permanente Audio-Speicherung

### API Sicherheit
- Input Validation
- Rate Limiting
- Error Handling
- Secure Headers

## 📈 Performance

### Rate Limits
- TTS/STT: 20 requests/minute
- Voice Processing: 10 requests/minute
- Chat API: 100 requests/minute

### Optimierungen
- Async Processing für Voice Operations
- Audio Streaming für große Dateien
- Caching für häufige Anfragen
- Connection Pooling für Database

## 🤝 Contributing

### Development Setup
```bash
# Repository klonen
git clone <repository-url>
cd chatbot

# Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Tests ausführen
python3 voice/tests/test_voice_integration.py
```

### Code Standards
- Python PEP 8
- Type Hints
- Docstrings
- Error Handling
- Logging

## 📞 Support

### Dokumentation
- **Voice Integration**: `/opt/irado/chatbot/voice/docs/COMPREHENSIVE_DOCUMENTATION.md`
- **API Reference**: `/opt/irado/chatbot/voice/docs/API_REFERENCE.md`
- **Frontend Guide**: `/opt/irado/chatbot/voice/docs/FRONTEND_INTEGRATION.md`

### Logs
```bash
# Service Logs
sudo journalctl -u irado-voice-chatbot -f | cat

# Application Logs
tail -f /opt/irado/chatbot/logs/voice.log
```

## 📄 License

Proprietary - Irado Development Team

---

**Version:** 1.0.0  
**Letzte Aktualisierung:** 30. September 2025  
**Status:** Produktionsbereit ✅

## 🎯 Quick Links

- [Voice Integration Docs](voice/docs/COMPREHENSIVE_DOCUMENTATION.md)
- [API Reference](voice/docs/API_REFERENCE.md)
- [Frontend Integration](voice/docs/FRONTEND_INTEGRATION.md)
- [Address Validation](ADDRESS_VALIDATION_README.md)
- [Cloudflare Integration](CLOUDFLARE-README.md)

