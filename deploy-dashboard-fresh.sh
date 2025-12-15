#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="irado-rg"
LOCATION="westeurope"
ACR_NAME="irado"
TIMESTAMP=$(date +%s)
DASHBOARD_IMAGE_NAME="irado-dashboard-$(date +%Y%m%d-%H%M%S)"
DASHBOARD_APP_NAME="irado-dashboard-app"
APP_SERVICE_PLAN="irado-app-service-plan"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  IRADO DASHBOARD FRESH DEPLOYMENT TO AZURE                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "📦 Configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   ACR: $ACR_NAME"
echo "   Dashboard App: $DASHBOARD_APP_NAME"
echo "   Image: $DASHBOARD_IMAGE_NAME"
echo ""

# Step 1: Build Docker Image for Dashboard
echo "🔨 Step 1: Building Dashboard Docker Image..."
cd /opt/irado-azure/chatbot

cat > Dockerfile.dashboard << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app

# Set working directory to dashboard
WORKDIR /app/dashboard

# Expose port
EXPOSE 8000

# Run dashboard with gunicorn from dashboard directory
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "1200", "--chdir", "/app/dashboard", "dashboard:app"]
EOF

echo "   Building dashboard image (no cache)..."
docker build --no-cache -f Dockerfile.dashboard -t ${DASHBOARD_IMAGE_NAME}:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "✅ Dashboard image built successfully"
echo ""

# Step 2: Push to ACR
echo "🚀 Step 2: Pushing to Azure Container Registry..."
az acr login --name $ACR_NAME > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "❌ ACR login failed!"
    exit 1
fi

echo "   Pushing versioned image (v${TIMESTAMP})..."
docker tag ${DASHBOARD_IMAGE_NAME}:latest ${ACR_NAME}.azurecr.io/${DASHBOARD_IMAGE_NAME}:v${TIMESTAMP}
docker push ${ACR_NAME}.azurecr.io/${DASHBOARD_IMAGE_NAME}:v${TIMESTAMP}

echo "   Pushing latest tag..."
docker tag ${DASHBOARD_IMAGE_NAME}:latest ${ACR_NAME}.azurecr.io/${DASHBOARD_IMAGE_NAME}:latest
docker push ${ACR_NAME}.azurecr.io/${DASHBOARD_IMAGE_NAME}:latest

echo "✅ Images pushed to ACR"
echo ""

# Step 3: Create App Service Plan
echo "📋 Step 3: Creating App Service Plan..."
if az appservice plan show --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP >/dev/null 2>&1; then
    echo "✅ App Service Plan already exists"
else
    az appservice plan create \
        --name $APP_SERVICE_PLAN \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --is-linux \
        --sku B1
    echo "✅ App Service Plan created"
fi
echo ""

# Step 4: Delete existing Web App if it exists
echo "🗑️ Step 4: Removing existing Web App (if exists)..."
if az webapp show --name $DASHBOARD_APP_NAME --resource-group $RESOURCE_GROUP >/dev/null 2>&1; then
    az webapp delete --name $DASHBOARD_APP_NAME --resource-group $RESOURCE_GROUP
    echo "✅ Existing Web App deleted"
    sleep 10  # Wait for deletion to complete
else
    echo "✅ No existing Web App found"
fi

# Step 5: Create Web App
echo "🌐 Step 5: Creating Dashboard Web App..."
az webapp create \
    --name $DASHBOARD_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --container-image-name ${ACR_NAME}.azurecr.io/${DASHBOARD_IMAGE_NAME}:v${TIMESTAMP} \
     
echo "✅ Web App created"
echo ""

# Step 6: Configure ACR Authentication
echo "🔐 Step 6: Configuring ACR Authentication..."
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

az webapp config container set \
    --name $DASHBOARD_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --container-registry-url https://${ACR_NAME}.azurecr.io \
    --container-registry-user $ACR_USERNAME \
    --container-registry-password $ACR_PASSWORD

echo "✅ ACR authentication configured"
echo ""

# Step 7: Configure Environment Variables
echo "⚙️  Step 7: Configuring Environment Variables..."

# Database configurations (same as chatbot)
CHAT_DB_HOST="irado-chat-db.postgres.database.azure.com"
CHAT_DB_PORT="5432"
CHAT_DB_NAME="irado_chat"
CHAT_DB_USER="irado_admin"
CHAT_DB_PASSWORD="lqBp6OF31+wCNXzyTMvasFrspdtL+IWPGVtooy2zjS4="

# Business clients database (using same database as chat)
BEDRIJFSKLANTEN_DB_HOST="irado-chat-db.postgres.database.azure.com"
BEDRIJFSKLANTEN_DB_PORT="5432"
BEDRIJFSKLANTEN_DB_NAME="irado_chat"
BEDRIJFSKLANTEN_DB_USER="irado_admin"
BEDRIJFSKLANTEN_DB_PASSWORD="lqBp6OF31+wCNXzyTMvasFrspdtL+IWPGVtooy2zjS4="

az webapp config appsettings set \
    --name $DASHBOARD_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        POSTGRES_HOST="$CHAT_DB_HOST" \
        POSTGRES_PORT="$CHAT_DB_PORT" \
        POSTGRES_DB="$CHAT_DB_NAME" \
        POSTGRES_USER="$CHAT_DB_USER" \
        POSTGRES_PASSWORD="$CHAT_DB_PASSWORD" \
        BEDRIJFSKLANTEN_DB_HOST="$BEDRIJFSKLANTEN_DB_HOST" \
        BEDRIJFSKLANTEN_DB_PORT="$BEDRIJFSKLANTEN_DB_PORT" \
        BEDRIJFSKLANTEN_DB_NAME="$BEDRIJFSKLANTEN_DB_NAME" \
        BEDRIJFSKLANTEN_DB_USER="$BEDRIJFSKLANTEN_DB_USER" \
        BEDRIJFSKLANTEN_DB_PASSWORD="$BEDRIJFSKLANTEN_DB_PASSWORD" \
        APP_TIMEZONE="Europe/Amsterdam" \
        TZ="Europe/Amsterdam" \
        WEBSITES_PORT="8000" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="false" \
        WEBSITES_ENABLE_APP_SERVICE_STORAGE="false"

echo "✅ Environment variables configured"
echo ""

# Step 8: Restart Web App
echo "🔄 Step 8: Restarting Dashboard Web App..."
az webapp restart --name $DASHBOARD_APP_NAME --resource-group $RESOURCE_GROUP
echo "✅ Web App restarted"
echo ""

# Wait for startup
echo "⏳ Waiting for dashboard to start (4 minutes)..."
sleep 240

# Step 9: Health Check
echo "🏥 Step 9: Performing Health Check..."
DASHBOARD_URL="https://${DASHBOARD_APP_NAME}.azurewebsites.net"

# Check if the dashboard is responding
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $DASHBOARD_URL)

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ DEPLOYMENT SUCCESSFUL!${NC}"
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ DEPLOYMENT SUCCESSFUL!${NC}"
    echo ""
    echo -e "${BLUE}🌐 Dashboard URL:${NC} $DASHBOARD_URL"
    echo -e "${BLUE}📊 HTTP Status:${NC} $HTTP_STATUS"
    echo ""
    echo -e "${BLUE}📝 Next Steps:${NC}"
    echo -e "   1. Open dashboard in browser: $DASHBOARD_URL"
    echo -e "   2. Navigate to 'System Prompt' tab"
    echo -e "   3. Create or edit system prompts"
    echo -e "   4. Changes are immediately reflected in the chatbot"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
else
    echo -e "${RED}❌ Health check failed (HTTP $HTTP_STATUS)${NC}"
    echo -e "${YELLOW}💡 Try accessing the dashboard manually: $DASHBOARD_URL${NC}"
fi

echo ""

# Cleanup
echo "🧹 Cleaning up Docker images and containers..."
echo "   Removing local build image..."
docker rmi ${DASHBOARD_IMAGE_NAME}:latest 2>/dev/null || true

echo "   Removing dangling images..."
docker image prune -f > /dev/null 2>&1

echo "   Removing old dashboard images (keeping last 3)..."
OLD_DASHBOARD_IMAGES=$(docker images irado.azurecr.io/irado-dashboard-* --format "{{.ID}} {{.Repository}}:{{.Tag}}" | grep -v "$DASHBOARD_IMAGE_NAME" | tail -n +4 | awk '{print $1}')
if [ ! -z "$OLD_DASHBOARD_IMAGES" ]; then
    echo "$OLD_DASHBOARD_IMAGES" | xargs -r docker rmi -f > /dev/null 2>&1
    echo "   ✅ Removed old dashboard images"
else
    echo "   ✅ No old dashboard images to clean"
fi

echo "   Removing unused containers..."
docker container prune -f > /dev/null 2>&1

echo "   Removing unused networks..."
docker network prune -f > /dev/null 2>&1

echo "✅ Comprehensive cleanup completed"
