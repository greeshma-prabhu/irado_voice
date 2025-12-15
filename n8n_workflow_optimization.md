# n8n Workflow Optimierung für Irado Vector Store

## Aktueller Workflow Status
✅ **Workflow funktioniert** - Daten werden erfolgreich in die Datenbank geladen
✅ **Korrekte Tabelle** - `langchain_pg_embedding` wird verwendet
✅ **OpenAI Embeddings** - Text-embedding-3-small (1536 Dimensionen)

## Identifizierte Probleme aus den Tests

### 1. **Chunk Size zu groß?**
- **Aktuell:** 2000 Zeichen
- **Problem:** Große Chunks können spezifische Informationen "verwässern"
- **Empfehlung:** 500-1000 Zeichen testen

### 2. **Text Splitter Strategie**
- **Aktuell:** Recursive Character Text Splitter
- **Problem:** Könnte wichtige FAQ-Strukturen zerstören
- **Empfehlung:** Semantic Chunking oder FAQ-spezifische Aufteilung

### 3. **Collection Name fehlt**
- **Problem:** Keine Collection Name definiert
- **Empfehlung:** `collection_name: "irado_knowledge"` setzen

## Optimierungsvorschläge

### Option 1: Chunk Size reduzieren
```json
{
  "parameters": {
    "chunkSize": 500,
    "chunkOverlap": 50,
    "options": {}
  }
}
```

### Option 2: FAQ-spezifische Aufteilung
- Separate Chunks für jede FAQ
- Separate Chunks für jeden Abschnitt
- Metadata für bessere Kategorisierung

### Option 3: Collection Name hinzufügen
```json
{
  "parameters": {
    "mode": "insert",
    "tableName": "langchain_pg_embedding",
    "collectionName": "irado_knowledge",
    "options": {}
  }
}
```

## Test-Strategie

### 1. **Verschiedene Chunk Sizes testen:**
- 500 Zeichen
- 1000 Zeichen  
- 1500 Zeichen
- 2000 Zeichen (aktuell)

### 2. **FAQ-spezifische Tests:**
- Jede FAQ als separater Chunk
- Metadata für Kategorien hinzufügen

### 3. **Performance-Messung:**
- Antwortqualität bei verschiedenen Chunk Sizes
- Retrieval-Geschwindigkeit
- Relevanz der gefundenen Chunks

## Empfohlene nächste Schritte

1. **Chunk Size auf 500 reduzieren** und neu laden
2. **Collection Name hinzufügen**
3. **Neue Tests durchführen** mit den optimierten Einstellungen
4. **FAQ-spezifische Aufteilung** implementieren falls nötig

## Erwartete Verbesserungen

- **Bessere Trefferquote** bei spezifischen Fragen
- **Präzisere Antworten** durch kleinere Chunks
- **Bessere Kategorisierung** durch Metadata
- **Schnellere Retrieval** durch optimierte Chunks


