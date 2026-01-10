#!/bin/bash
# Deploy Dashboard to Azure as 3rd Web App

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════════"
echo "  IRADO DASHBOARD DEPLOYMENT TO AZURE"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Environment selection (prod/dev)
ENVIRONMENT="${ENVIRONMENT:-prod}"
if [[ "${1:-}" == "--env" ]]; then
  ENVIRONMENT="${2:-}"
  shift 2
fi

if [[ "$ENVIRONMENT" != "prod" && "$ENVIRONMENT" != "dev" ]]; then
  echo "❌ Error: --env must be 'prod' or 'dev'"
  exit 1
fi

# Configuration
LOCATION="westeurope"
ACR_NAME="irado"
DASHBOARD_IMAGE_NAME="irado-dashboard-$(date +%Y%m%d-%H%M%S)"

if [[ "$ENVIRONMENT" == "dev" ]]; then
  RESOURCE_GROUP="irado-dev-rg"
  DASHBOARD_APP_NAME="irado-dev-dashboard-app"
  APP_SERVICE_PLAN="irado-dev-app-service-plan"
  DB_HOST_DEFAULT="irado-dev-chat-db.postgres.database.azure.com"
  DB_NAME_DEFAULT="irado_dev_chat"
  CHATBOT_URL_DEFAULT="https://irado-dev-chatbot-app.azurewebsites.net"
else
  RESOURCE_GROUP="irado-rg"
  DASHBOARD_APP_NAME="irado-dashboard-app"
  APP_SERVICE_PLAN="irado-app-service-plan"
  DB_HOST_DEFAULT="irado-chat-db.postgres.database.azure.com"
  DB_NAME_DEFAULT="irado_chat"
  CHATBOT_URL_DEFAULT="https://irado-chatbot-app.azurewebsites.net"
fi

echo "📦 Configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   ACR: $ACR_NAME"
echo "   Dashboard App: $DASHBOARD_APP_NAME"
echo ""

# Step 1: Build Docker Image for Dashboard
echo "🔨 Step 1: Building Dashboard Docker Image..."
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT_DIR}/chatbot"

cat > Dockerfile.dashboard << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy application files
COPY . .

# Set Python path and working directory
ENV PYTHONPATH=/app
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

# Step 2: Tag and Push to ACR
echo "🚀 Step 2: Pushing to Azure Container Registry..."

# Login to ACR
az acr login --name $ACR_NAME

# Tag with timestamp for version tracking
TIMESTAMP=$(date +%s)
docker tag ${DASHBOARD_IMAGE_NAME}:latest ${ACR_NAME}.azurecr.io/${DASHBOARD_IMAGE_NAME}:v${TIMESTAMP}
docker tag ${DASHBOARD_IMAGE_NAME}:latest ${ACR_NAME}.azurecr.io/${DASHBOARD_IMAGE_NAME}:latest

# Push both tags
echo "   Pushing versioned image (v${TIMESTAMP})..."
docker push ${ACR_NAME}.azurecr.io/${DASHBOARD_IMAGE_NAME}:v${TIMESTAMP}

echo "   Pushing latest tag..."
docker push ${ACR_NAME}.azurecr.io/${DASHBOARD_IMAGE_NAME}:latest

echo "✅ Images pushed to ACR"
echo ""

# Step 3: Create App Service Plan for Dashboard (if not exists)
echo "📋 Step 3: Creating App Service Plan..."

PLAN_EXISTS=$(az appservice plan show --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP 2>/dev/null || echo "")

if [ -z "$PLAN_EXISTS" ]; then
    echo "   Creating new App Service Plan..."
    az appservice plan create \
        --name $APP_SERVICE_PLAN \
        --resource-group $RESOURCE_GROUP \
        --is-linux \
        --sku B1 \
        --location $LOCATION
    
    echo "✅ App Service Plan created"
else
    echo "✅ App Service Plan already exists"
fi
echo ""

# Step 4: Create or Update Web App
echo "🌐 Step 4: Creating/Updating Dashboard Web App..."

APP_EXISTS=$(az webapp show --name $DASHBOARD_APP_NAME --resource-group $RESOURCE_GROUP 2>/dev/null || echo "")

if [ -z "$APP_EXISTS" ]; then
    echo "   Creating new Web App..."
    az webapp create \
        --resource-group $RESOURCE_GROUP \
        --plan $APP_SERVICE_PLAN \
        --name $DASHBOARD_APP_NAME \
        --deployment-container-image-name ${ACR_NAME}.azurecr.io/${DASHBOARD_IMAGE_NAME}:latest
    
    echo "✅ Web App created"
else
    echo "   Updating existing Web App..."
    az webapp config container set \
        --name $DASHBOARD_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --container-image-name ${ACR_NAME}.azurecr.io/${DASHBOARD_IMAGE_NAME}:v${TIMESTAMP}
    
    echo "✅ Web App updated"
fi
echo ""

# Step 5: Configure ACR Authentication
echo "🔐 Step 5: Configuring ACR Authentication..."

ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

az webapp config container set \
    --name $DASHBOARD_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --container-registry-url https://${ACR_NAME}.azurecr.io \
    --container-registry-user $ACR_USERNAME \
    --container-registry-password $ACR_PASSWORD

echo "✅ ACR authentication configured"
echo ""

# Step 6: Configure Environment Variables
echo "⚙️  Step 6: Configuring Environment Variables..."

az webapp config appsettings set \
    --name $DASHBOARD_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        POSTGRES_HOST="${POSTGRES_HOST:-$DB_HOST_DEFAULT}" \
        POSTGRES_PORT="5432" \
        POSTGRES_DB="${POSTGRES_DB:-$DB_NAME_DEFAULT}" \
        POSTGRES_USER="${POSTGRES_USER:-irado_admin}" \
        BEDRIJFSKLANTEN_DB_HOST="${BEDRIJFSKLANTEN_DB_HOST:-$DB_HOST_DEFAULT}" \
        BEDRIJFSKLANTEN_DB_PORT="5432" \
        BEDRIJFSKLANTEN_DB_NAME="${BEDRIJFSKLANTEN_DB_NAME:-$DB_NAME_DEFAULT}" \
        BEDRIJFSKLANTEN_DB_USER="${BEDRIJFSKLANTEN_DB_USER:-irado_admin}" \
        CHATBOT_URL="${CHATBOT_URL:-$CHATBOT_URL_DEFAULT}" \
        WEBSITES_PORT="8000" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="false"

# Set secrets only if provided in environment (avoid committing secrets into this script).
if [[ -n "${POSTGRES_PASSWORD:-}" || -n "${BEDRIJFSKLANTEN_DB_PASSWORD:-}" ]]; then
  secret_settings=()
  [[ -n "${POSTGRES_PASSWORD:-}" ]] && secret_settings+=("POSTGRES_PASSWORD=${POSTGRES_PASSWORD}")
  [[ -n "${BEDRIJFSKLANTEN_DB_PASSWORD:-}" ]] && secret_settings+=("BEDRIJFSKLANTEN_DB_PASSWORD=${BEDRIJFSKLANTEN_DB_PASSWORD}")
  az webapp config appsettings set \
      --name "$DASHBOARD_APP_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --settings "${secret_settings[@]}" \
      --output none
fi

echo "✅ Environment variables configured"
echo ""

# Step 7: Restart Web App
echo "🔄 Step 7: Restarting Dashboard Web App..."
az webapp restart --name $DASHBOARD_APP_NAME --resource-group $RESOURCE_GROUP
echo "✅ Web App restarted"
echo ""

# Wait for startup
echo "⏳ Waiting for dashboard to start (4 minutes)..."
sleep 240

# Step 8: Health Check
echo "🏥 Step 8: Performing Health Check..."
DASHBOARD_URL="https://${DASHBOARD_APP_NAME}.azurewebsites.net"

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L "$DASHBOARD_URL" --connect-timeout 30 || echo "000")

echo ""
echo "════════════════════════════════════════════════════════════════"
if [ "$HTTP_STATUS" -ge 200 ] && [ "$HTTP_STATUS" -lt 400 ]; then
    echo "✅ DEPLOYMENT SUCCESSFUL!"
    echo ""
    echo "🌐 Dashboard URL: $DASHBOARD_URL"
    echo "📊 HTTP Status: $HTTP_STATUS"
    echo ""
    echo "📝 Next Steps:"
    echo "   1. Open dashboard in browser: $DASHBOARD_URL"
    echo "   2. Navigate to 'System Prompt' tab"
    echo "   3. Create or edit system prompts"
    echo "   4. Changes are immediately reflected in the chatbot"
else
    echo "⚠️  DEPLOYMENT COMPLETED WITH WARNINGS"
    echo ""
    echo "🌐 Dashboard URL: $DASHBOARD_URL"
    echo "📊 HTTP Status: $HTTP_STATUS (may still be starting up)"
    echo ""
    echo "🔍 Troubleshooting:"
    echo "   - Check logs: az webapp log tail --name $DASHBOARD_APP_NAME --resource-group $RESOURCE_GROUP"
    echo "   - Wait a few more minutes and try accessing the URL"
    echo "   - Verify database connectivity and credentials"
fi
echo "════════════════════════════════════════════════════════════════"

# Cleanup: Remove old local Docker images to save disk space
echo ""
echo "🧹 Cleaning up old Docker images..."
# Remove dangling images
docker image prune -f > /dev/null 2>&1
# Remove old dashboard images (keep only last 3)
OLD_IMAGES=$(docker images irado.azurecr.io/irado-dashboard --format "{{.ID}} {{.Tag}}" | tail -n +4 | awk '{print $1}')
if [ ! -z "$OLD_IMAGES" ]; then
    echo "$OLD_IMAGES" | xargs -r docker rmi -f > /dev/null 2>&1
    echo "✅ Cleaned up old dashboard images"
else
    echo "✅ No old images to clean"
fi
echo ""

