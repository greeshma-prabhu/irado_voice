#!/bin/bash
# Test script for multiple routes (takken + matras)
# Should send 2 separate emails

SESSION_ID="test-multi-route-$(date +%s)"

echo "🧪 Testing multiple routes (takken + matras in Schiedam)"
echo "Session ID: $SESSION_ID"
echo ""
echo "Step 1: Start conversation..."

curl -s -X POST https://irado-chatbot-app.azurewebsites.net/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic aXJhZG86MjBJcmFkbzI1IQ==" \
  -d "{\"sessionId\": \"$SESSION_ID\", \"chatInput\": \"start bot\"}" | python3 -m json.tool

echo ""
echo "Step 2: Specify municipality..."
sleep 3

curl -s -X POST https://irado-chatbot-app.azurewebsites.net/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic aXJhZG86MjBJcmFkbzI1IQ==" \
  -d "{\"sessionId\": \"$SESSION_ID\", \"chatInput\": \"Schiedam\"}" | python3 -m json.tool

echo ""
echo "Step 3: Request pickup..."
sleep 3

curl -s -X POST https://irado-chatbot-app.azurewebsites.net/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic aXJhZG86MjBJcmFkbzI1IQ==" \
  -d "{\"sessionId\": \"$SESSION_ID\", \"chatInput\": \"ik wil een matras en takken laten ophalen\"}" | python3 -m json.tool

echo ""
echo "Step 4: Accept privacy..."
sleep 3

curl -s -X POST https://irado-chatbot-app.azurewebsites.net/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic aXJhZG86MjBJcmFkbzI1IQ==" \
  -d "{\"sessionId\": \"$SESSION_ID\", \"chatInput\": \"ja\"}" | python3 -m json.tool

echo ""
echo "Step 5: Provide details..."
sleep 3

curl -s -X POST https://irado-chatbot-app.azurewebsites.net/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic aXJhZG86MjBJcmFkbzI1IQ==" \
  -d "{\"sessionId\": \"$SESSION_ID\", \"chatInput\": \"Test Gebruiker, test@example.com, Hoofdstraat 14, 3114GG Schiedam, 1 matras 90x200cm, 1 takkenbundel 1,5m\"}" | python3 -m json.tool

echo ""
echo "Step 6: Confirm..."
sleep 3

curl -s -X POST https://irado-chatbot-app.azurewebsites.net/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic aXJhZG06MjBJcmFkbzI1IQ==" \
  -d "{\"sessionId\": \"$SESSION_ID\", \"chatInput\": \"ja, klopt\"}" | python3 -m json.tool

echo ""
echo "✅ Test completed! Check logs for EMAIL events:"
echo ""
echo "az webapp log download --name irado-chatbot-app --resource-group irado-rg --log-file /tmp/test-multi.zip && unzip -p /tmp/test-multi.zip 'LogFiles/*default_docker.log' | grep '$SESSION_ID' | grep -E '\[EMAIL|\[TOOL_CALL.*email'"


