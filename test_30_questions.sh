#!/bin/bash

# Test script for n8n chatbot with 30 random questions
# Generated from the large JSON dataset

WEBHOOK_URL="https://n8n.mainfact.ai/webhook/ac0c1794-2908-4204-acf9-06ad03419634/chat"

echo "=== n8n Chatbot Test - 30 Random Questions ==="
echo ""

# Function to generate session ID
generate_session_id() {
    python3 -c "import uuid; print(uuid.uuid4())"
}

# Function to send question
send_question() {
    local question="$1"
    local session_id=$(generate_session_id)
    
    echo "Frage: $question"
    echo "Session ID: $session_id"
    echo ""
    
    JSON_PAYLOAD=$(cat <<EOF
{
  "sessionId": "$session_id",
  "action": "sendMessage",
  "chatInput": "$question"
}
EOF
)
    
    echo "Sending request..."
    curl -X POST "$WEBHOOK_URL" \
      -H "Content-Type: application/json" \
      -d "$JSON_PAYLOAD"
    
    echo ""
    echo "---"
    echo ""
}


# Test 1: informatie
send_question "Kan ik ook stagelopen of afstuderen bij Irado?"

# Test 2: afvalsoorten
send_question "Wat doe ik met mijn (afgedankte) textiel?"

# Test 3: afvalsoorten
send_question "Waarom scheiden?"

# Test 4: informatie
send_question "Dus wat doe je met asbest?"

# Test 5: afvalsoorten
send_question "Hoe zit het met plastic verpakkingen, metalen verpakkingen en drankenkartons in Schiedam?"

# Test 6: afvalsoorten
send_question "Waarom scheiden?"

# Test 7: afvalsoorten
send_question "Zal ik wasbare- of wegwerpluiers gebruiken?"

# Test 8: afvalsoorten
send_question "Wat doe ik met mijn groente-, fruit- tuinafval en etensresten?"

# Test 9: informatie
send_question "Hoe ga je verder na de veilige verwijdering van asbest?"

# Test 10: afvalsoorten
send_question "Wat doe ik met mijn plastic- en metalen/blik verpakkingen en drankenkartons (pmd)?"

# Test 11: informatie
send_question "Wil Irado mij sponsoren?"

# Test 12: gemeenten
send_question "Ongedierte? Neem contact met ons op"

# Test 13: diensten
send_question "Hoe huur ik een container?"

# Test 14: afvalsoorten
send_question "Een defecte afvalpas ontvangen?"

# Test 15: diensten
send_question "Last van kakkerlakken? Neem contact met ons op"

# Test 16: afvalsoorten
send_question "Wat doe ik met mijn puin, bouw- en sloopafval?"

# Test 17: afvalsoorten
send_question "Wat mag er bij het oud papier?"

# Test 18: afvalsoorten
send_question "Waar kan ik oud papier en karton kwijt?"

# Test 19: afvalsoorten
send_question "Vragen?"

# Test 20: afvalsoorten
send_question "Waarom scheiden?"

# Test 21: afvalsoorten
send_question "Waarom zou ik wasbare luiers gebruiken?"

# Test 22: afvalsoorten
send_question "Wat zijn de voordelen van deze afvalbakken?"

# Test 23: diensten
send_question "Big Bag laten ophalen?"

# Test 24: gemeenten
send_question "Wat kan ik doen om ongedierte te voorkomen?"

# Test 25: diensten
send_question "Wespen bestrijden in en om de woning?"

# Test 26: afvalsoorten
send_question "Waar laat ik mijn restafval aan?"

# Test 27: informatie
send_question "Wanneer kun je terecht bij het inzamelpunt?"

# Test 28: informatie
send_question "Welke tuin past bij mij?"

# Test 29: informatie
send_question "Wat zoeken we?"

# Test 30: vacatures
send_question "Solliciteren?"

echo "=== Test completed ==="
