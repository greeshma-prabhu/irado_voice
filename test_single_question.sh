#!/bin/bash

# Test-Script für eine einzelne Chatbot-Frage
# Verwendung: ./test_single_question.sh

echo "=== Chatbot Test - Einzelne Frage ==="
echo ""

# Test-Frage 2: "Wat kosten BigBags?"
echo "Teste Frage: Wat kosten BigBags?"
echo ""

# JSON für den Webhook
cat << 'EOF'
{
  "sessionId": "eb6406c1-6064-421c-b7a4-2f40b5501c4f",
  "action": "sendMessage",
  "chatInput": "Wat kosten BigBags?"
}
EOF

echo ""
echo "=== Erwartete Antwort ==="
echo "BigBags kosten €15 per stuk. Je kunt ze bestellen via de website of telefonisch. BigBags zijn handig voor grote hoeveelheden afval zoals puin, gipsplaten of steen."
echo ""

echo "=== Webhook URL ==="
echo "https://n8n.mainfact.ai/webhook/ac0c1794-2908-4204-acf9-06ad03419634/chat"
echo ""

echo "=== Anweisungen ==="
echo "1. Gehe zur Webhook URL"
echo "2. Kopiere das JSON oben"
echo "3. Sende es als POST Request"
echo "4. Vergleiche die Antwort mit der erwarteten Antwort"
echo ""

echo "=== Prüfungen ==="
echo "✓ Enthält die Antwort '€15'?"
echo "✓ Erwähnt sie 'website of telefonisch'?"
echo "✓ Sagt sie etwas über 'puin, gipsplaten of steen'?"
