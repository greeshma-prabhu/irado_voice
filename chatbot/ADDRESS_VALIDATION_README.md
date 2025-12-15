# Address Validation Upgrade für Irado Chatbot

## Übersicht

Der Irado Chatbot wurde um eine umfassende Adressvalidierung erweitert, die vor jeder Anfrage prüft:

1. **Adressvalidierung**: Überprüfung der Gültigkeit niederländischer Adressen via Open Postcode API
2. **Service-Area-Prüfung**: Validierung ob die Adresse im Einzugsgebiet liegt
3. **KOAD-Blacklist**: Prüfung gegen die Liste der gesperrten Firmenkunden

## Neue Komponenten

### 1. AddressValidationService (`address_validation.py`)

**Hauptfunktionen:**
- `validate_address(postcode, huisnummer)`: Validiert eine niederländische Adresse
- `validate_address_from_text(address_text)`: Extrahiert und validiert Adresse aus Text
- `is_address_blocked(postcode, huisnummer)`: Prüft ob Adresse auf KOAD-Liste steht

**Service-Areas:**
- **Capelle aan den IJssel**: 2900-2909
- **Schiedam**: 3100-3125 (inkl. 3111-3119, 3121-3125)
- **Vlaardingen**: 3130-3138

### 2. Erweiterte AI-Service (`ai_service.py`)

**Neue Tools:**
- `validate_address`: Direkte Adressvalidierung mit Postcode und Hausnummer
- `validate_address_from_text`: Adressextraktion aus Text

**Funktionsweise:**
- AI kann automatisch Adressen validieren
- Integriert in den Chat-Flow
- Gibt detaillierte Rückmeldung über Adressstatus

### 3. Konfiguration (`config.py`)

**Neue Konfigurationsoptionen:**
```python
# Address validation configuration
OPEN_POSTCODE_API_BASE_URL = 'https://openpostcode.nl/api'
ADDRESS_VALIDATION_ENABLED = True
SERVICE_AREA_VALIDATION_ENABLED = True

# Service area postcode ranges
SERVICE_AREAS = {
    'Capelle aan den IJssel': ['2900', '2901', ...],
    'Schiedam': ['3100', '3101', ...],
    'Vlaardingen': ['3130', '3131', ...]
}
```

## API-Integration

### Open Postcode API

**Endpoint:** `https://openpostcode.nl/api/address`

**Beispiel-Request:**
```
GET https://openpostcode.nl/api/address?postcode=1017XN&huisnummer=42
```

**Response:**
```json
{
  "postcode": "1017XN",
  "huisnummer": "42",
  "straat": "Frederiksplein",
  "buurt": "Frederikspleinbuurt",
  "wijk": "De Weteringschans",
  "woonplaats": "Amsterdam",
  "gemeente": "Amsterdam",
  "provincie": "Noord-Holland",
  "latitude": 52.35999,
  "longitude": 4.898108
}
```

## KOAD-Integration

Die `koad.csv` Datei enthält die Liste der gesperrten Firmenkunden:
- Format: `KOAD-nummer,KOAD-str,KOAD-pc,KOAD-huisaand,KOAD-huisnr,KOAD-etage,KOAD-naam,KOAD-actief,KOAD-inwoner`
- Wird automatisch geladen beim Start
- Adressen auf dieser Liste werden automatisch abgelehnt

## Validierungsflow

1. **Adresseingabe**: Benutzer gibt Adresse ein
2. **Format-Validierung**: Postcode-Format prüfen (4 Ziffern + 2 Buchstaben)
3. **API-Aufruf**: Open Postcode API für Adressvalidierung
4. **Service-Area-Check**: Prüfung gegen erlaubte Postleitzahlbereiche
5. **KOAD-Check**: Prüfung gegen Blacklist
6. **Ergebnis**: Detaillierte Rückmeldung an Benutzer

## Test-Script

```bash
python test_address_validation.py
```

**Test-Fälle:**
- Gültige Adressen in Service-Area
- Ungültige Postcode-Formate
- Adressen außerhalb Service-Area
- Adressextraktion aus Text

## System-Prompt Updates

Der AI-System-Prompt wurde erweitert um:

```
Adres-validatie

Gebruik de validate_address functie om te controleren of:
1. Het adres geldig is (via Open Postcode API)
2. Het adres in het verzorgingsgebied ligt
3. Het adres niet op de KOAD-lijst staat (geblokkeerde adressen)

Voer ALTIJD adresvalidatie uit voordat je een aanvraag verwerkt.
```

## Fehlerbehandlung

- **API-Fehler**: Graceful Fallback mit Fehlermeldung
- **Ungültige Adressen**: Klare Rückmeldung an Benutzer
- **Service-Area**: Freundliche Ablehnung mit Erklärung
- **KOAD-Blacklist**: Automatische Ablehnung ohne Begründung

## Sicherheit

- Rate-Limiting für API-Aufrufe
- Input-Validierung und Sanitization
- Fehlerbehandlung ohne Datenpreisgabe
- Logging für Debugging

## Wartung

**Konfiguration anpassen:**
- Service-Areas in `config.py` erweitern
- API-Endpoints bei Änderungen anpassen
- KOAD-Liste regelmäßig aktualisieren

**Monitoring:**
- API-Response-Zeiten überwachen
- Fehlerrate bei Adressvalidierung
- Service-Area-Coverage prüfen

