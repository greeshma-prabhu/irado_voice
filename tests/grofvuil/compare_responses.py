#!/usr/bin/env python3
# Compare chatbot responses to ground truth via keyword/phrase checks (simple heuristic)
import json, sys, re, pathlib

GROUND = pathlib.Path('/opt/irado/tests/grofvuil/ground_truth.txt').read_text(encoding='utf-8', errors='ignore').lower()

KEYS = {
  # Tijden & aanbieden
  'tijden_algemeen': [
    '7.30 – 16.00', '7.30-16.00', 'tussen 7.30 – 16.00', 'tussen 7.30-16.00',
  ],
  'buitenzetten_tijd': [
    'tussen 5.00 uur', '5.00 uur tot 7.30 uur', '5.00 tot 7.30', '5.00-7.30',
  ],
  'locatie': [
    'aan de weg', 'doorgaande weg', 'vrije parkeerplaats', 'niet op de stoep', 'niet op je eigen erf', 'vrij aan de weg',
  ],

  # Omvang/gewicht/hoeveelheid
  'omvang_gewicht': [
    '1,80 meter', '1.80 meter', '30 kg', 'gebundeld', 'open dozen', 'open zakken',
  ],
  'hoeveelheid_gemeente': [
    'maximale hoeveelheid', 'raadpleeg de aanvullende aanbiedregels voor jouw gemeente',
  ],

  # Specifieke categorieën/voorbeelden
  'glasplaten': [
    'glasplaten: aftapen', 'glasplaten: aftapen of verpakken met karton', 'aftapen of verpakken met karton',
  ],
  'meubels_matrassen_bijzonder': [
    'meubels en matrassen', 'in één stuk meegenomen', 'mogen afwijken van de maximale lengte',
  ],
  'mattroute': [
    'matrassen', 'alleen droge matrassen', 'schiedam', 'vlaardingen', 'aparte route', 'geen boxspring', 'boxspring onderstellen',
  ],
  'ijzer_voorbeelden': [
    'fiets (niet op slot!)', 'strijkplank', 'bedspiraal', 'bureaustoel', 'barbecue', 'ijzeren wasrekken',
  ],
  'zonwering_radiatoren': [
    'zonwering', 'markies', 'uitvalscherm', 'max. 2 meter', 'radiatoren (max. 2 meter)', 'radiatoren mogen maximaal 2 meter',
  ],
  'elektra_voorbeelden': [
    'koelkasten', 'diepvriezers', 'zonder levensmiddelen', '(af)wasmachine', 'droogtrommel', 'oven', 'televisie', 'radio', 'stofzuigers', 'videorecorders', 'magnetrons', 'stereo-apparatuur', 'koffiezetters', 'dvd-spelers', 'dvd-recorders', 'strijkijzers', 'waterkokers', 'elektrisch gereedschap', 'pc-apparatuur', 'scanners', 'schrijfmachines', 'rekenmachines', 'printers', 'telefoons', 'babyfoons', 'opladers',
  ],

  # Snoeiafval/tuin
  'tuinafval': [
    'snoeiafval', 'gebundeld', '1,80 meter lang', '1.80 meter lang', 'niet in dozen of zakken', 'boomstronken', '50 cm lang', '25 cm dik', 'versnipperen',
  ],

  # Niet meenemen / uitsluitingen (uitgebreider)
  'uitsluitingen': [
    'huisvuil', 'restafval', 'verbouwing', 'renovatie', 'sloop', 'sanitair', 'keukenblok', 'tegels', 'gipsplaten', 'puin', 'steen', 'klein chemisch afval', 'kca', 'verf', 'tl-buizen', 'latex', 'accu', 'batterijen', 'asbest', 'autobanden', 'brommers', 'scooters', 'scoot(brom)mobiel', 'aanhangwagentjes', 'bloembakken van beton', 'parasolvoet van beton', 'dakpannen', 'dak-shingles', 'golfplaten', 'regenpijpen', 'dakgoten', 'graszoden', 'zand', 'aarde', 'grond', 'satellietschotels', 'bedrijfsafval',
  ],

  # Afspraak per soort (aparte route)
  'aparte_route_per_soort': [
    'aparte routes', 'per afvalsoort een aparte grofvuilafspraak', 'aparte grofvuilafspraak',
  ],
}

WEIGHTS = {k:1 for k in KEYS}


def score(text: str):
  t = text.lower()
  result = {}
  total = 0
  hit = 0
  for k, phrases in KEYS.items():
    total += WEIGHTS[k]
    found = any(p in t for p in phrases)
    result[k] = bool(found)
    if found:
      hit += WEIGHTS[k]
  return hit/total if total else 0.0, result


def _gather_strings(obj):
  """Recursively collect string leaves from JSON-like structures."""
  if isinstance(obj, str):
    return [obj]
  if isinstance(obj, dict):
    out = []
    for v in obj.values():
      out.extend(_gather_strings(v))
    return out
  if isinstance(obj, list):
    out = []
    for it in obj:
      out.extend(_gather_strings(it))
    return out
  return []


def main(paths):
  rows = []
  for p in paths:
    try:
      data = json.loads(pathlib.Path(p).read_text(encoding='utf-8', errors='ignore'))
    except Exception:
      # fallback: treat as plain text
      text = pathlib.Path(p).read_text(encoding='utf-8', errors='ignore')
      s, details = score(text)
      rows.append((p, s, details, text[:500]))
      continue
    # Extract answer text: prefer top-level 'output' if present, else concatenate all string leaves
    if isinstance(data, dict) and isinstance(data.get('output'), str):
      text = data['output']
    else:
      text = '\n'.join(_gather_strings(data)) or json.dumps(data, ensure_ascii=False)
    s, details = score(text)
    rows.append((p, s, details, text[:500]))

  # Write markdown report
  rpt_path = '/opt/irado/tests/grofvuil/reports/compare_report.md'
  with open(rpt_path, 'w', encoding='utf-8') as f:
    f.write('## Vergelijkingsrapport: Chatbot vs Aanbiedregels grofvuil\n\n')
    for p, s, det, preview in rows:
      f.write(f'- Bestand: `{p}`\n')
      f.write(f'  - Score: {s:.2f}\n')
      f.write(f'  - Checks: {det}\n')
      f.write('  - Voorbeeld (eerste 500 tekens):\n')
      f.write('```\n')
      f.write(preview)
      f.write('\n```\n\n')
  print(rpt_path)

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print('Usage: compare_responses.py <response.json> [more...]')
    sys.exit(1)
  main(sys.argv[1:])
