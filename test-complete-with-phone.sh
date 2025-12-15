#!/bin/bash
# COMPLETE email flow test met alle velden (incl. telefoonnummer)

set -e

API_URL="https://irado-chatbot-app.azurewebsites.net/api/chat"
AUTH="Basic aXJhZG86MjBJcmFkbzI1IQ=="
SESSION_ID="test-email-complete-$(date +%s)"
WAIT_TIME=90

echo "=========================================="
echo "COMPLETE EMAIL TEST (MET TELEFOONNUMMER)"
echo "Session: $SESSION_ID"
echo "=========================================="
echo ""

send() {
    echo ">> $1"
    sleep $WAIT_TIME
    curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -H "Authorization: $AUTH" \
        -d "{\"sessionId\": \"$SESSION_ID\", \"action\": \"sendMessage\", \"chatInput\": \"$1\"}" \
        | python3 -m json.tool | grep '"output"' | sed 's/.*"output": "//;s/"$//'
    echo ""
}

send "hoi"
send "Schiedam"
send "grofvuil ophalen"
send "ja, akkoord met privacy"
send "Armin Jonker"
send "armin@fam-jonker.de"
send "Hoofdstraat 14"
send "3114 GG"
send "Schiedam"
send "06-12345678"
send "1 takkenbundel, 1.80 meter, 5 kg"
send "ja dat klopt"
send "graag tussen 14:00 en 16:00"
send "ja bevestig graag"

echo "=========================================="
echo "WACHT 30 SECONDEN EN CHECK LOGS..."
echo "=========================================="
sleep 30

az webapp log download --name irado-chatbot-app --resource-group irado-rg --log-file /tmp/email-complete-logs.zip 2>&1 | grep -v "WARNING"
echo ""
echo "Zoeken naar email verzending..."
unzip -p /tmp/email-complete-logs.zip "LogFiles/*default_docker.log" 2>/dev/null | grep -i -E "(email|smtp|tool_call|send_email)" | tail -30

echo ""
echo "=========================================="
echo "KLAAR! Check of emails verzonden zijn."
echo "=========================================="

