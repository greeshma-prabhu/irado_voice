## n8n Chatbot Test Rapport - Grofvuil

- **Datum**: $(date)
- **Webhook**: `https://n8n.mainfact.ai/webhook/ac0c1794-2908-4204-acf9-06ad03419634/chat`

### Testvraag
```
{{QUESTION}}
```

### Antwoord (raw JSON)
```
{{RAW_JSON_PATH}}
```

### Beoordeling
- **Taal**: NL / niet-NL
- **Relevant**: ja / nee
- **Correcte kernpunten gedekt**:
  - Tijdvenster (5:00-7:30 buiten zetten; ophaal 7:30-16:00)
  - Locatie (aan de weg; niet op stoep/eigen erf; bereikbaar)
  - Omvang/gewicht (≤ 1,80 m; ≤ 30 kg; bundelen)
  - Uitsluitingen (puin/steen/gips; kca; asbest; bedrijfsafval etc.)
  - Speciale routes (matrassen Schiedam/Vlaardingen)
- **Opmerkingen**: 

