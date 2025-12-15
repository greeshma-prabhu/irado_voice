#!/bin/bash
# Batch: stuur elke vraag met eigen UUID; sla response per vraag op en maak CSV.
WEBHOOK_URL="https://n8n.mainfact.ai/webhook/ac0c1794-2908-4204-acf9-06ad03419634/chat"
QUESTIONS_FILE="/opt/irado/tests/grofvuil/questions_nl.txt"
OUT_DIR="/opt/irado/tests/grofvuil/reports"
CSV_FILE="$OUT_DIR/summary.csv"
LIMIT=""

# Optioneel: --limit N om de eerste N vragen te sturen
while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit)
      LIMIT="$2"; shift 2;;
    *) shift;;
  esac
done

mkdir -p "$OUT_DIR"
echo "test_num,session_id,timestamp,question,response_path" > "$CSV_FILE"

num=0
while IFS= read -r line; do
  # Strip leading numbering like '1. ' if present
  question="${line#*. }"
  if [[ -z "$question" ]]; then
    continue
  fi
  num=$((num+1))
  if [[ -n "$LIMIT" && $num -gt $LIMIT ]]; then
    break
  fi
  session_id=$(python3 -c 'import uuid; print(uuid.uuid4())')
  ts=$(date +%Y%m%d_%H%M%S)
  out_file="$OUT_DIR/response_${num}_${ts}.json"

  payload_file="$OUT_DIR/payload_${num}_${ts}.json"
  echo "{\"sessionId\":\"$session_id\",\"action\":\"sendMessage\",\"chatInput\":\"$question\"}" > "$payload_file"

  echo "[$num] Sending: $question"
  echo "Session: $session_id"
  hdr_file="$OUT_DIR/headers_${num}_${ts}.txt"
  http_code=$(curl -sS -m 120 --connect-timeout 10 -D "$hdr_file" -o "$out_file" -w "%{http_code}" -X POST "$WEBHOOK_URL" \
    -H 'Content-Type: application/json' \
    --data @"$payload_file")

  size=$(stat -c '%s' "$out_file" 2>/dev/null || echo 0)
  echo "HTTP: $http_code | Size: $size bytes | Headers: $hdr_file"
  if [ "$size" -eq 0 ] || [ -z "$http_code" ]; then
    echo "❌ Lege response of geen status voor test $num"
    echo "Payload:"; head -c 300 "$payload_file" | tr -d '\n' | cat; echo
  else
    echo "🔎 Preview:"; head -c 200 "$out_file" | tr -d '\n' | cat; echo
  fi

  echo "$num,$session_id,$ts,\"$question\",$out_file" >> "$CSV_FILE"
  sleep 0.5

done < "$QUESTIONS_FILE"

echo "Done. CSV: $CSV_FILE"
