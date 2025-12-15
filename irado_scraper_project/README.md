# Irado.nl Web Scraper

Ein intelligenter Web Scraper für die irado.nl Website, der strukturierte Inhalte extrahiert und in eine Knowledge Base für einen Chatbot organisiert.

## Features

- **Intelligente Content-Extraktion**: Extrahiert strukturierte Inhalte von irado.nl Seiten
- **Automatische Kategorisierung**: Organisiert Inhalte in logische Kategorien
- **Duplikat-Erkennung**: Vermeidet doppelte Inhalte
- **Saubere Daten**: Filtert unerwünschte Elemente und Social Media Links
- **Respektvolle Scraping-Praktiken**: Verzögerungen zwischen Requests

## Kategorien

Der Scraper organisiert Inhalte in folgende Kategorien:

- **afvalsoorten**: Informationen über verschiedene Abfallarten
- **diensten**: Dienstleistungen wie Termine, Bestellungen, Abholungen
- **informatie**: Allgemeine Informationen und Anleitungen
- **contact**: Kontaktinformationen und Kundenservice
- **regels**: Regeln, Bedingungen und Richtlinien
- **gemeenten**: Spezifische Informationen für verschiedene Gemeinden
- **algemeen**: Allgemeine Inhalte

## Installation

1. Virtuelles Environment aktivieren:
```bash
source venv/bin/activate
```

2. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

## Verwendung

### Test-Scraping
```bash
python test_scraper.py
```

### Vollständiges Scraping
```bash
python irado_scraper_improved.py
```

### Konfiguration
- Ändern Sie `max_pages` in der `main()` Funktion für mehr/ weniger Seiten
- Passen Sie die Kategorien in `categorize_content()` an

## Ausgabe

Die Ergebnisse werden in `knowledge_vector/irado_knowledge_base_clean.json` gespeichert.

### Struktur der Ausgabe:
```json
{
  "kategorie": [
    {
      "url": "https://www.irado.nl/...",
      "title": "Seitentitel",
      "sections": [
        {
          "heading": "Abschnittsüberschrift",
          "content": "Inhalt des Abschnitts"
        }
      ],
      "faqs": [
        {
          "question": "Frage?",
          "answer": "Antwort"
        }
      ],
      "contact_info": {},
      "category": "kategorie"
    }
  ]
}
```

## Dateien

- `irado_scraper_improved.py`: Haupt-Scraper (verbesserte Version)
- `irado_scraper.py`: Ursprünglicher Scraper
- `test_scraper.py`: Test-Script für einzelne Seiten
- `requirements.txt`: Python-Abhängigkeiten
- `knowledge_vector/`: Ordner für die generierten Knowledge Base Dateien

## Technische Details

- **Python 3.x** mit BeautifulSoup4 und Requests
- **Intelligente URL-Filterung**: Nur irado.nl URLs
- **Content-Hashing**: Erkennung von Duplikaten
- **Strukturierte Extraktion**: Headings und Content werden getrennt erfasst
- **FAQ-Erkennung**: Automatische Identifikation von Frage-Antwort-Paaren

## Hinweise

- Der Scraper respektiert die Website durch 1-Sekunden-Verzögerungen
- Social Media Links und externe URLs werden automatisch gefiltert
- Nur relevante Inhalte werden extrahiert (Navigation, Footer etc. werden ignoriert)

## Lizenz

Für interne Verwendung bei Irado entwickelt.



