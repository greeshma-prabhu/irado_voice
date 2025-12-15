# Irado Chatbot Testfragen

## 5 Testfragen aus der Knowledge Base:

### 1. Grundlegende Abfallentsorgung
**Frage:** "Waar laat ik mijn afval?"
**Erwartete Antwort:** Informationen über Abfalltrennung, Minicontainer/Kliko, Sammelcontainer in der Nachbarschaft, und die Möglichkeit, Abfall zur Milieustraat zu bringen.

### 2. Grofvuil-Regeln
**Frage:** "Wat mag je niet aanbieden als grofvuil?"
**Erwartete Antwort:** Liste der nicht erlaubten Gegenstände wie Hausmüll, Bauschutt, Kleinchemikalien, Asbest, Autoreifen, etc.

### 3. Glasentsorgung
**Frage:** "Waar kan ik glas kwijt?"
**Erwartete Antwort:** Informationen über Glascontainer, separate Behälter für verschiedene Glasfarben, und dass nur Glasverpackungen in die Glascontainer gehören.

### 4. Plastik-Recycling
**Frage:** "Wat mag wel of niet bij plastic afval?"
**Erwartete Antwort:** Spezifische Regeln für Plastik+ Abfall, was erlaubt und was nicht erlaubt ist.

### 5. Grofvuil-Terminbuchung
**Frage:** "Hoe maak ik een grofvuil afspraak?"
**Erwartete Antwort:** Anweisungen zur Online-Terminbuchung, Hinweise auf Aanbiedregels, und spezielle Regeln für Matratzen in Schiedam/Vlaardingen.

## Zusätzliche Testfragen:

### 6. Milieupas Problem
**Frage:** "Wat moet ik doen als mijn milieupas kapot is?"
**Erwartete Antwort:** Informationen über defekte Milieupas und Lösungsmöglichkeiten.

### 7. BigBag Kosten
**Frage:** "Wat kosten BigBags?"
**Erwartete Antwort:** Preisinformationen für BigBags.

## Webhook URL:
https://n8n.mainfact.ai/webhook/ac0c1794-2908-4204-acf9-06ad03419634/chat

## Test Command:
```bash
curl -X POST "https://n8n.mainfact.ai/webhook/ac0c1794-2908-4204-acf9-06ad03419634/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "DEINE_FRAGE_HIER"}'
```


