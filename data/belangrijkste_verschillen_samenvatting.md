# Belangrijkste Verschillen Grofvuilregels - Samenvatting

## 🚨 KRITIEKE VERSCHILLEN TUSSEN GEMEENTES

### 1. **Maximale hoeveelheid per afspraak**
- **Schiedam & Vlaardingen**: 1m³ per huishouden per grofvuilafspraak
- **Capelle**: Geen specifieke limiet vermeld

### 2. **Klein Gevaarlijk Afval (KGA) ophalen**
- **Schiedam & Vlaardingen**: Alleen woensdag 8:00-12:00 uur, thuis moeten zijn
- **Capelle**: Geen specifieke informatie beschikbaar

### 3. **Snoeiroutes timing**
- **Schiedam & Vlaardingen**: Extra snoeiroutes in voor- en najaar
- **Capelle**: Laatste maandag van de maand

### 4. **Takken bundelen**
- **Schiedam & Vlaardingen**: Max 1,80 meter lang per bundel
- **Capelle**: Geen specifieke maximale lengte

### 5. **Matrassen regels**
- **Schiedam & Vlaardingen**: Geen boxspring onderstellen, bed ombouw onderdelen, beddengoed
- **Capelle**: Alleen droge matrassen, geen specifieke uitsluitingen

## 📋 CHATBOT IMPLEMENTATIE STRATEGIE

### Stap 1: Gemeente detectie
```
"In welke gemeente woont u? (Schiedam, Vlaardingen of Capelle aan den IJssel)"
```

### Stap 2: Algemene regels (voor alle gemeentes)
- Aanbiedtijden: 05:00-07:30 plaatsen, 07:30-16:00 ophalen
- Afmetingen: max 1,80m x 0,90m, max 30kg per stuk
- Locatie: doorgaande weg, niet op erf of stoep

### Stap 3: Gemeente-specifieke regels
- **Schiedam/Vlaardingen**: 1m³ limiet, woensdag KGA, extra snoeiroutes
- **Capelle**: Geen 1m³ limiet, laatste maandag snoeiroutes

### Stap 4: Belangrijke verschillen benadrukken
- Voor Schiedam/Vlaardingen: "Belangrijk: maximaal 1m³ per afspraak"
- Voor Capelle: "Belangrijk: snoeiroutes op laatste maandag van de maand"

## 🎯 CHATBOT PROMPT STRUCTUUR

```
1. Vraag gemeente
2. Geef algemene regels
3. Voeg gemeente-specifieke regels toe
4. Benadruk belangrijkste verschillen
5. Verwijs naar officiële website
```

## 📊 IMPACT ANALYSE

### Hoogste impact verschillen:
1. **1m³ limiet** (Schiedam/Vlaardingen vs Capelle)
2. **KGA ophalen** (woensdag vs onbekend)
3. **Snoeiroutes** (voor/najaar vs laatste maandag)

### Midden impact verschillen:
4. **Takken bundelen** (1,80m vs onbekend)
5. **Matrassen regels** (specifieke uitsluitingen vs algemeen)

### Laagste impact verschillen:
6. **Algemene regels** (grotendeels hetzelfde)

## 🔧 TECHNISCHE IMPLEMENTATIE

### Chatbot logica:
```
IF gemeente = "Schiedam" OR "Vlaardingen":
    - Toon 1m³ limiet
    - Toon woensdag KGA regel
    - Toon extra snoeiroutes
    - Toon specifieke matrassen regels

IF gemeente = "Capelle":
    - Toon geen 1m³ limiet
    - Toon laatste maandag snoeiroutes
    - Toon algemene matrassen regels
    - Waarschuw voor beperkte KGA info
```

### Fallback strategie:
```
IF gemeente onbekend:
    - Toon algemene regels
    - Vraag opnieuw naar gemeente
    - Verwijs naar algemene website
```

