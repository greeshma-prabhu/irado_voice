#!/bin/bash
# Complete end-to-end test van chatbot met email functionaliteit
# Met langere timeouts vanwege Azure OpenAI quota

set -e

API_URL="https://irado-chatbot-app.azurewebsites.net/api/chat"
AUTH="Basic aXJhZG86MjBJcmFkbzI1IQ=="
SESSION_ID="test-email-flow-$(date +%s)"
WAIT_TIME=180  # 3 minuten tussen requests

echo "=========================================="
echo "COMPLETE CHATBOT EMAIL FLOW TEST"
echo "Session ID: $SESSION_ID"
echo "Wait time between requests: ${WAIT_TIME}s"
echo "=========================================="
echo ""

send_message() {
    local message="$1"
    local step="$2"
    
    echo "[$step] Verzenden: $message"
    echo "Wachten ${WAIT_TIME} seconden voor quota..."
    sleep $WAIT_TIME
    
    RESPONSE=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -H "Authorization: $AUTH" \
        -d "{\"sessionId\": \"$SESSION_ID\", \"action\": \"sendMessage\", \"chatInput\": \"$message\"}")
    
    echo "Response:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""
    echo "=========================================="
    echo ""
}

# Stap 1: Groet
send_message "hoi" "STAP 1/12"

# Stap 2: Gemeente
send_message "Schiedam" "STAP 2/12"

# Stap 3: Ophalen grofvuil
send_message "ophalen" "STAP 3/12"

# Stap 4: Privacy akkoord
send_message "ja" "STAP 4/12"

# Stap 5: Naam en adres
send_message "Armin Jonker, armin@fam-jonker.de, Hoofdstraat 14, 3114 GG, Schiedam" "STAP 5/12"

# Stap 6: Items opgeven
send_message "1 takkenbundel (1,80 m, 5 kg)" "STAP 6/12"

# Stap 7: Bevestiging categorie
send_message "ja dat klopt" "STAP 7/12"

# Stap 8: Extra notities
send_message "graag na 14:00 uur" "STAP 8/12"

# Stap 9: Finale bevestiging
send_message "ja bevestig" "STAP 9/12"

echo "=========================================="
echo "TEST COMPLEET!"
echo "=========================================="
echo ""
echo "Check nu de logs voor email verzending:"
echo "  az webapp log download --name irado-chatbot-app --resource-group irado-rg --log-file /tmp/email-test-logs.zip"
echo ""
echo "Zoek naar:"
echo "  - 'send_email_to_team'"
echo "  - 'send_email_to_customer'"
echo "  - 'Email sent' of 'SMTP'"
echo "  - Eventuele errors"

