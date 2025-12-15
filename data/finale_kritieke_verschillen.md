# FINALE KRITIEKE VERSCHILLEN - GROFVUILREGELS

## 🚨 MEEST KRITIEKE VERSCHILLEN

### 1. **MAXIMALE HOEVEELHEID PER AFSPRAAK**
| Gemeente | Limiet | Omschrijving |
|----------|--------|--------------|
| **Schiedam** | 1m³ | Circa een kwart van een parkeerplaats |
| **Vlaardingen** | 2m³ | Circa een halve parkeerplaats |
| **Capelle** | GEEN LIMIET | "Maximale hoeveelheid: geen maximale hoeveelheid" |

### 2. **KLEIN GEVAARLIJK AFVAL (KGA)**
| Gemeente | KGA Regels |
|----------|------------|
| **Schiedam** | Alleen woensdag 8:00-12:00 uur, thuis moeten zijn |
| **Vlaardingen** | Alleen woensdag 8:00-12:00 uur, thuis moeten zijn |
| **Capelle** | KGA wordt NIET geaccepteerd als grofvuil |

### 3. **SNOEIROUTES TIMING**
| Gemeente | Snoeiroutes |
|----------|-------------|
| **Schiedam** | Extra snoeiroutes in voor- en najaar |
| **Vlaardingen** | Extra snoeiroutes in voor- en najaar |
| **Capelle** | Laatste maandag van de maand |

### 4. **FLATBEWONERS (alleen Vlaardingen)**
- **Plaatsing**: Nabij ingang van flat, op stoep naast flat
- **Niet op**: Parkeervak
- **Zorg voor**: Doorgangen niet blokkeren

## 📋 CHATBOT IMPLEMENTATIE STRATEGIE

### Stap 1: Gemeente Detectie
```
"In welke gemeente woont u? (Schiedam, Vlaardingen of Capelle aan den IJssel)"
```

### Stap 2: Algemene Regels (voor alle gemeentes)
- Aanbiedtijden: 05:00-07:30 plaatsen, 07:30-16:00 ophalen
- Afmetingen: max 1,80m x 0,90m, max 30kg per stuk
- Locatie: doorgaande weg, niet op erf of stoep
- Toegestane en verboden afvalsoorten

### Stap 3: Gemeente-specifieke Regels
- **Schiedam**: 1m³ limiet, woensdag KGA, extra snoeiroutes
- **Vlaardingen**: 2m³ limiet, woensdag KGA, extra snoeiroutes, flatregels
- **Capelle**: Geen limiet, KGA niet toegestaan, laatste maandag snoeiroutes

### Stap 4: Kritieke Verschillen Benadrukken
- **Schiedam**: "Belangrijk: maximaal 1m³ per afspraak"
- **Vlaardingen**: "Belangrijk: maximaal 2m³ per afspraak, speciale regels voor flatbewoners"
- **Capelle**: "Belangrijk: geen maximale hoeveelheid, KGA niet toegestaan"

## 🎯 CHATBOT PROMPT STRUCTUUR

### Basis Prompt:
```
1. Vraag gemeente
2. Geef algemene regels
3. Voeg gemeente-specifieke regels toe
4. Benadruk belangrijkste verschillen
5. Verwijs naar officiële website
```

### Technische Implementatie:
```
IF gemeente = "Schiedam":
    - Toon 1m³ limiet
    - Toon woensdag KGA regel
    - Toon extra snoeiroutes

IF gemeente = "Vlaardingen":
    - Toon 2m³ limiet
    - Toon woensdag KGA regel
    - Toon extra snoeiroutes
    - Toon flatregels

IF gemeente = "Capelle":
    - Toon geen limiet
    - Toon KGA niet toegestaan
    - Toon laatste maandag snoeiroutes
```

## 📊 IMPACT ANALYSE

### Hoogste Impact Verschillen:
1. **1m³ vs 2m³ vs geen limiet** (Schiedam vs Vlaardingen vs Capelle)
2. **KGA regels** (woensdag vs niet toegestaan)
3. **Snoeiroutes** (voor/najaar vs laatste maandag)

### Midden Impact Verschillen:
4. **Flatregels** (alleen Vlaardingen)
5. **Matrassen regels** (specifieke uitsluitingen vs algemeen)

### Laagste Impact Verschillen:
6. **Algemene regels** (grotendeels hetzelfde)

## 🔧 IMPLEMENTATIE TIPS

1. **Gemeente detectie**: Altijd eerst vragen naar gemeente
2. **Regel hiërarchie**: Algemene regels eerst, dan gemeente-specifieke verschillen
3. **Belangrijke verschillen**: Benadruk de belangrijkste verschillen tussen gemeentes
4. **Actuele informatie**: Verwijs naar officiële website voor meest recente regels
5. **Gebruiksvriendelijk**: Houd antwoorden overzichtelijk en praktisch
6. **Flatbewoners**: Speciale aandacht voor Vlaardingen flatregels
7. **KGA regels**: Duidelijk onderscheid tussen gemeentes
8. **Snoeiroutes**: Verschillende timings per gemeente

## 📞 CONTACTINFORMATIE

### KGA Ophalen (Schiedam & Vlaardingen)
- **Telefoon**: 010 - 262 1000
- **Dag**: Woensdag
- **Tijd**: 8:00 - 12:00 uur
- **Voorwaarde**: U moet thuis zijn

### Website Verwijzingen
- **Schiedam**: https://www.irado.nl/schiedam/afvalsoorten/grofvuil/aanbiedregels
- **Vlaardingen**: https://www.irado.nl/vlaardingen/afvalsoorten/grofvuil/aanbiedregels
- **Capelle**: https://www.irado.nl/capelle/afvalsoorten/grofvuil/aanbiedregels
