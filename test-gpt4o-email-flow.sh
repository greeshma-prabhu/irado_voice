#!/bin/bash
# Complete end-to-end test met GPT-4o (sneller dan mini!)
# Kortere timeouts dankzij hogere quota

set -e

API_URL="https://irado-chatbot-app.azurewebsites.net/api/chat"
AUTH="Basic aXJhZG86MjBJcmFkbzI1IQ=="
SESSION_ID="test-gpt4o-email-$(date +%s)"
WAIT_TIME=90  # 90 seconden tussen requests (was 180 met mini)

echo "=========================================="
echo "GPT-4O EMAIL FLOW TEST (SNELLER!)"
echo "Session ID: $SESSION_ID"
echo "Wait time: ${WAIT_TIME}s (was 180s met mini)"
echo "=========================================="
echo ""

send_message() {
    local message="$1"
    local step="$2"
    
    echo "[$step] Verzenden: $message"
    echo "Wachten ${WAIT_TIME} seconden..."
    sleep $WAIT_TIME
    
    START_TIME=$(date +%s)
    RESPONSE=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -H "Authorization: $AUTH" \
        -d "{\"sessionId\": \"$SESSION_ID\", \"action\": \"sendMessage\", \"chatInput\": \"$message\"}")
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo "Response (${DURATION}s):"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""
    echo "=========================================="
    echo ""
}

# Complete flow tot email
send_message "hoi" "STAP 1/10"
send_message "Schiedam" "STAP 2/10"
send_message "ophalen" "STAP 3/10"
send_message "ja" "STAP 4/10"
send_message "Armin Jonker, armin@fam-jonker.de, Hoofdstraat 14, 3114 GG, Schiedam" "STAP 5/10"
send_message "1 takkenbundel (1,80 m, 5 kg)" "STAP 6/10"
send_message "ja dat klopt" "STAP 7/10"
send_message "nee verder niets" "STAP 8/10"
send_message "bevestig" "STAP 9/10"
send_message "dank je" "STAP 10/10"

echo "=========================================="
echo "TEST COMPLEET MET GPT-4O!"
echo "=========================================="
echo ""
echo "Nu logs checken:"
echo "  sleep 30"
echo "  az webapp log download --name irado-chatbot-app --resource-group irado-rg --log-file /tmp/gpt4o-email-logs.zip"
echo "  unzip -p /tmp/gpt4o-email-logs.zip 'LogFiles/*default_docker.log' | grep -i 'email\\|smtp\\|tool_call' | tail -50"

