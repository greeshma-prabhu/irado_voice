#!/bin/bash
# Quick deployment script voor Irado Chatbot naar Azure
# Usage: ./deploy-to-azure.sh [optional-tag-name]

set -e  # Stop bij errors

# Colors voor output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="irado-rg"
WEBAPP_NAME="irado-chatbot-app"
ACR_NAME="irado"
IMAGE_NAME="chatbot-$(date +%Y%m%d-%H%M%S)"
VERSION=$(cat VERSION.txt)

echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Irado Chatbot - Azure Deployment    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "Dockerfile.chatbot" ]; then
    echo -e "${RED}❌ Error: Dockerfile.chatbot niet gevonden. Run dit script vanuit /opt/irado-azure${NC}"
    exit 1
fi

# Generate unique tag
if [ -z "$1" ]; then
    TAG="v$(date +%s)"
    echo -e "${YELLOW}⚠️  Geen tag opgegeven, gebruik timestamp: $TAG${NC}"
else
    TAG="$1"
    echo -e "${GREEN}✅ Gebruik custom tag: $TAG${NC}"
fi

IMAGE_FULL="$ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG"

# Show current deployment
echo ""
echo -e "${BLUE}📋 Huidige deployment:${NC}"
CURRENT_IMAGE=$(az webapp config show --resource-group $RESOURCE_GROUP --name $WEBAPP_NAME --query linuxFxVersion -o tsv | cut -d'|' -f2)
echo -e "   $CURRENT_IMAGE"

echo -e "${BLUE}📦 Container versie:${NC}"
echo -e "   Chatbot: v$VERSION"

# Confirmation
echo ""
echo -e "${YELLOW}🚀 Nieuwe deployment:${NC}"
echo -e "   $IMAGE_FULL"
echo ""
read -p "Doorgaan? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Deployment geannuleerd${NC}"
    exit 1
fi

# Step 1: Build Docker image
echo ""
echo -e "${BLUE}🔨 Step 1/5: Building Docker image...${NC}"
echo -e "${BLUE}📦 Container versie:${NC}"
echo -e "   Chatbot: v$VERSION"
docker build --no-cache -f Dockerfile.chatbot -t $IMAGE_FULL . 2>&1 | tail -n 10
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build successful${NC}"
else
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi

# Step 2: Login to ACR
echo ""
echo -e "${BLUE}🔐 Step 2/5: Login to Azure Container Registry...${NC}"
az acr login --name $ACR_NAME > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ ACR login successful${NC}"
else
    echo -e "${RED}❌ ACR login failed${NC}"
    exit 1
fi

# Step 3: Push to ACR
echo ""
echo -e "${BLUE}📤 Step 3/5: Pushing to Azure Container Registry...${NC}"
docker push $IMAGE_FULL 2>&1 | grep -E "Pushed|digest:" | tail -n 2
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Push successful${NC}"
else
    echo -e "${RED}❌ Push failed${NC}"
    exit 1
fi

# Step 4: Update Web App
echo ""
echo -e "${BLUE}🔄 Step 4/5: Updating Web App configuration...${NC}"
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $WEBAPP_NAME \
    --linux-fx-version "DOCKER|$IMAGE_FULL" \
    --output none

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Web App updated${NC}"
else
    echo -e "${RED}❌ Web App update failed${NC}"
    exit 1
fi

# Step 4.5: Set database environment variables
echo ""
echo -e "${BLUE}🗄️  Setting database environment variables...${NC}"
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $WEBAPP_NAME \
    --settings \
        CHAT_DB_HOST="irado-chat-db.postgres.database.azure.com" \
        CHAT_DB_NAME="irado_chat" \
        CHAT_DB_USER="irado_admin" \
        CHAT_DB_PASSWORD="lqBp6OF31+wCNXzyTMvasFrspdtL+IWPGVtooy2zjS4=" \
        POSTGRES_HOST="irado-chat-db.postgres.database.azure.com" \
        POSTGRES_DB="irado_chat" \
        POSTGRES_USER="irado_admin" \
        POSTGRES_PASSWORD="lqBp6OF31+wCNXzyTMvasFrspdtL+IWPGVtooy2zjS4=" \
        POSTGRES_PORT="5432" \
        POSTGRES_SSLMODE="require" \
        APP_TIMEZONE="Europe/Amsterdam" \
        TZ="Europe/Amsterdam" \
        AZURE_OPENAI_API_KEY="BXFgQF9udVZRqyhvapyyKmaO5MxXH5CUZb2Xf992rD99al4C4zyKJQQJ99BJACfhMk5XJ3w3AAAAACOGL8rA" \
        AZURE_OPENAI_ENDPOINT="https://info-mgal213r-swedencentral.cognitiveservices.azure.com" \
        AZURE_OPENAI_DEPLOYMENT="gpt-4o" \
        AZURE_OPENAI_API_VERSION="2025-01-01-preview" \
        CHAT_BASIC_AUTH_USER="irado" \
        CHAT_BASIC_AUTH_PASSWORD="20Irado25!" \
    --output none

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database environment variables set${NC}"
else
    echo -e "${RED}❌ Failed to set database environment variables${NC}"
    exit 1
fi

# Step 5: Wait and verify
echo ""
echo -e "${BLUE}⏳ Step 5/6: Waiting for container to start (4 minutes)...${NC}"
for i in {1..48}; do
    echo -n "."
    sleep 5
done
echo ""

# Health check
echo ""
echo -e "${BLUE}🏥 Step 6/6: Health check...${NC}"
HEALTH_RESPONSE=$(curl -sS https://$WEBAPP_NAME.azurewebsites.net/health --max-time 10 2>&1)

if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎉 Chatbot is live op:${NC}"
    echo -e "${GREEN}   https://$WEBAPP_NAME.azurewebsites.net${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BLUE}📝 Deployment log:${NC}"
    echo "   Tag: $TAG"
    echo "   Previous: $(echo $CURRENT_IMAGE | awk -F: '{print $2}')"
    echo "   Time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo -e "${YELLOW}💡 Test de chat:${NC}"
    echo '   curl -X POST https://'$WEBAPP_NAME'.azurewebsites.net/api/chat \'
    echo '     -H "Content-Type: application/json" \'
    echo '     -H "Authorization: Basic aXJhZG86MjBJcmFkbzI1IQ==" \'
    echo '     -d '"'"'{"sessionId": "test", "action": "sendMessage", "chatInput": "hoi"}'"'"
    echo ""
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo -e "${YELLOW}Response: $HEALTH_RESPONSE${NC}"
    echo ""
    echo -e "${YELLOW}🔍 Checking logs...${NC}"
    az webapp log tail --resource-group $RESOURCE_GROUP --name $WEBAPP_NAME 2>&1 | head -n 20
    echo ""
    echo -e "${YELLOW}💡 Probeer:${NC}"
    echo "   - Wacht nog 30 seconden en test opnieuw"
    echo "   - Check logs: az webapp log tail --resource-group $RESOURCE_GROUP --name $WEBAPP_NAME"
    echo "   - Rollback: ./deploy-to-azure.sh $(echo $CURRENT_IMAGE | awk -F: '{print $2}')"
    exit 1
fi

# Cleanup: Remove old local Docker images to save disk space
echo ""
echo -e "${BLUE}🧹 Cleaning up Docker images and containers...${NC}"
echo -e "${BLUE}   Removing local build image...${NC}"
docker rmi $IMAGE_FULL 2>/dev/null || true

echo -e "${BLUE}   Removing dangling images...${NC}"
docker image prune -f > /dev/null 2>&1

echo -e "${BLUE}   Removing old chatbot images (keeping last 3)...${NC}"
OLD_CHATBOT_IMAGES=$(docker images irado.azurecr.io/chatbot-* --format "{{.ID}} {{.Repository}}:{{.Tag}}" | grep -v "$IMAGE_NAME" | tail -n +4 | awk '{print $1}')
if [ ! -z "$OLD_CHATBOT_IMAGES" ]; then
    echo "$OLD_CHATBOT_IMAGES" | xargs -r docker rmi -f > /dev/null 2>&1
    echo -e "${GREEN}   ✅ Removed old chatbot images${NC}"
else
    echo -e "${GREEN}   ✅ No old chatbot images to clean${NC}"
fi

echo -e "${BLUE}   Removing unused containers...${NC}"
docker container prune -f > /dev/null 2>&1

echo -e "${BLUE}   Removing unused networks...${NC}"
docker network prune -f > /dev/null 2>&1

echo -e "${GREEN}✅ Comprehensive cleanup completed${NC}"
