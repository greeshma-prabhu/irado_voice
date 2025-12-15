#!/bin/bash
# Send a single testvraag naar n8n webhook en sla het antwoord op
WEBHOOK_URL="https://n8n.mainfact.ai/webhook/ac0c1794-2908-4204-acf9-06ad03419634/chat"

# Optioneel: --session <uuid> om een vaste sessie te gebruiken; standaard nieuw UUID per vraag
SESSION_ARG=""
QUESTION=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --session)
      SESSION_ARG="$2"; shift 2 ;;
    *)
      QUESTION="$1"; shift ;;
  esac
done

if [ -z "$QUESTION" ]; then
  echo "Gebruik: $0 [--session <uuid>] 'jouw vraag in het Nederlands'"
  exit 1
fi

if [ -z "$SESSION_ARG" ]; then
  SESSION_ID=$(python3 -c 'import uuid; print(uuid.uuid4())')
else
  SESSION_ID="$SESSION_ARG"
fi

OUT_DIR="/opt/irado/tests/grofvuil/reports"
mkdir -p "$OUT_DIR"
TS=$(date +%Y%m%d_%H%M%S)
OUT_FILE="$OUT_DIR/response_${TS}.json"

PAYLOAD=$(cat <<JSON
{
  "sessionId": "$SESSION_ID",
  "action": "sendMessage",
  "chatInput": "$QUESTION"
}
JSON
)

curl -s -X POST "$WEBHOOK_URL" \
  -H 'Content-Type: application/json' \
  -d "$PAYLOAD" > "$OUT_FILE"

SIZE=$(stat -c '%s' "$OUT_FILE" 2>/dev/null || echo 0)
if [ "$SIZE" -eq 0 ]; then
  echo "❌ Lege response ontvangen (0 bytes). Session: $SESSION_ID"
  echo "Payload: $PAYLOAD"
  exit 2
fi

echo "✅ Vraag verstuurd. Session: $SESSION_ID"
echo "📄 Antwoord opgeslagen: $OUT_FILE"
echo "🔎 Preview:"; head -c 300 "$OUT_FILE" | tr -d '\n' | cat; echo
