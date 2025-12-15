#!/bin/bash
# Watch dashboard logs live during CSV upload

echo "📊 Live Dashboard Logs"
echo "====================="
echo "Probeer nu de CSV te uploaden in het dashboard..."
echo ""

az webapp log tail \
  --name irado-dashboard-app \
  --resource-group irado-rg \
  2>&1 | grep -v "GET /static" | grep -v "GET /api/stats" | grep --line-buffered -E "(📤|✅|❌|CSV|upload|ERROR|Exception|Traceback|bedrijfsklanten)"

