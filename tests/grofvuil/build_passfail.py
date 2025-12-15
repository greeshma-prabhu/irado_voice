import re, json, pathlib

rep_path = pathlib.Path('/opt/irado/tests/grofvuil/reports/compare_report.md')
out_path = pathlib.Path('/opt/irado/tests/grofvuil/reports/qa_passfail.md')

rep = rep_path.read_text(encoding='utf-8', errors='ignore')
rows, cur = [], {}

for line in rep.splitlines():
    m = re.match(r"- Bestand: `(.+?)`", line)
    if m:
        if cur:
            rows.append(cur)
        cur = {'path': m.group(1)}
        continue
    m = re.match(r"\s*- Score: ([0-9.]+)", line)
    if m:
        cur['score'] = float(m.group(1))
        continue
    m = re.match(r"\s*- Checks: (\{.*\})", line)
    if m:
        d = m.group(1).replace("False","false").replace("True","true").replace("'","\"")
        try:
            cur['checks'] = json.loads(d)
        except Exception:
            cur['checks'] = {}
        continue
if cur:
    rows.append(cur)

def mark(checks, key):
    return '✅' if checks.get(key) else '—'

lines = [
    "| test | score | tijden | locatie | omvang_gewicht | uitsluitingen | matrassen_route | tuinafval |",
    "|---:|---:|:---:|:---:|:---:|:---:|:---:|:---:|",
]
for r in rows:
    name = pathlib.Path(r.get('path','')).name
    m = re.match(r"response_(\d+)_", name)
    test = m.group(1) if m else name
    s = r.get('score', 0.0)
    c = r.get('checks', {})
    lines.append(f"| {test} | {s:.2f} | {mark(c,'tijden')} | {mark(c,'locatie')} | {mark(c,'omvang_gewicht')} | {mark(c,'uitsluitingen')} | {mark(c,'matrassen_route')} | {mark(c,'tuinafval')} |")

out_path.write_text("\n".join(lines), encoding='utf-8')
print(out_path)
