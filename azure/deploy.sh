#!/bin/bash

# Azure Deployment Script for Irado Chatbot System
# Deploys the complete containerized system to Azure

set -e

# Configuration
RESOURCE_GROUP="irado-rg"
LOCATION="westeurope"
ACR_NAME="irado"
KEY_VAULT_NAME="irado-keyvault"
STORAGE_ACCOUNT="iradostorage"
CONTAINER_GROUP="irado-chatbot-system"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Azure CLI is installed
check_azure_cli() {
    log "Checking Azure CLI installation..."
    if ! command -v az &> /dev/null; then
        error "Azure CLI is not installed. Please install it first."
    fi
    success "Azure CLI is installed"
}

# Check if logged in to Azure
check_azure_login() {
    log "Checking Azure login status..."
    if ! az account show &> /dev/null; then
        error "Not logged in to Azure. Please run 'az login' first."
    fi
    success "Logged in to Azure"
}

# Create resource group
create_resource_group() {
    log "Creating resource group: $RESOURCE_GROUP"
    if az group show --name $RESOURCE_GROUP &> /dev/null; then
        warning "Resource group $RESOURCE_GROUP already exists"
    else
        az group create --name $RESOURCE_GROUP --location $LOCATION
        success "Resource group created"
    fi
}

# Create Azure Container Registry
create_acr() {
    log "Creating Azure Container Registry: $ACR_NAME"
    if az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
        warning "Container Registry $ACR_NAME already exists"
    else
        az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true
        success "Container Registry created"
    fi
}

# Create Key Vault
create_key_vault() {
    log "Creating Key Vault: $KEY_VAULT_NAME"
    if az keyvault show --name $KEY_VAULT_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
        warning "Key Vault $KEY_VAULT_NAME already exists"
    else
        az keyvault create --resource-group $RESOURCE_GROUP --name $KEY_VAULT_NAME --location $LOCATION --sku standard
        success "Key Vault created"
    fi
}

# Create Storage Account
create_storage_account() {
    log "Creating Storage Account: $STORAGE_ACCOUNT"
    if az storage account show --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP &> /dev/null; then
        warning "Storage Account $STORAGE_ACCOUNT already exists"
    else
        az storage account create --resource-group $RESOURCE_GROUP --name $STORAGE_ACCOUNT --location $LOCATION --sku Standard_LRS
        success "Storage Account created"
    fi
}

# Create PostgreSQL databases
create_postgresql_databases() {
    log "Creating PostgreSQL databases..."
    
    # Chat database
    log "Creating chat database..."
    az postgres flexible-server create \
        --resource-group $RESOURCE_GROUP \
        --name irado-chat-db \
        --location $LOCATION \
        --admin-user irado_admin \
        --admin-password $(openssl rand -base64 32) \
        --sku-name Standard_B1ms \
        --tier Burstable \
        --public-access 0.0.0.0 \
        --storage-size 32 \
        --version 14
    
    # Bedrijfsklanten database
    log "Creating bedrijfsklanten database..."
    az postgres flexible-server create \
        --resource-group $RESOURCE_GROUP \
        --name irado-bedrijfsklanten-db \
        --location $LOCATION \
        --admin-user irado_admin \
        --admin-password $(openssl rand -base64 32) \
        --sku-name Standard_B1ms \
        --tier Burstable \
        --public-access 0.0.0.0 \
        --storage-size 32 \
        --version 14
    
    success "PostgreSQL databases created"
}

# Build and push Docker images
build_and_push_images() {
    log "Building and pushing Docker images..."
    
    # Login to ACR
    az acr login --name $ACR_NAME
    
    # Build and push chatbot image
    log "Building chatbot image..."
    docker build -t $ACR_NAME.azurecr.io/chatbot:latest ./containers/chatbot/
    docker push $ACR_NAME.azurecr.io/chatbot:latest
    
    # Build and push dashboard image
    log "Building dashboard image..."
    docker build -t $ACR_NAME.azurecr.io/dashboard:latest ./containers/dashboard/
    docker push $ACR_NAME.azurecr.io/dashboard:latest
    
    # Build and push website image
    log "Building website image..."
    docker build -t $ACR_NAME.azurecr.io/website:latest ./containers/website/
    docker push $ACR_NAME.azurecr.io/website:latest
    
    # Build and push dashboard-frontend image
    log "Building dashboard-frontend image..."
    docker build -t $ACR_NAME.azurecr.io/dashboard-frontend:latest ./containers/dashboard-frontend/
    docker push $ACR_NAME.azurecr.io/dashboard-frontend:latest
    
    success "All images built and pushed"
}

# Deploy container group
deploy_container_group() {
    log "Deploying container group..."
    
    # Get ACR credentials
    ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
    ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)
    
    # Get database passwords
    CHAT_DB_PASSWORD=$(az postgres flexible-server show --resource-group $RESOURCE_GROUP --name irado-chat-db --query administratorLoginPassword --output tsv)
    BEDRIJFSKLANTEN_DB_PASSWORD=$(az postgres flexible-server show --resource-group $RESOURCE_GROUP --name irado-bedrijfsklanten-db --query administratorLoginPassword --output tsv)
    
    # Get storage account key
    STORAGE_KEY=$(az storage account keys list --resource-group $RESOURCE_GROUP --account-name $STORAGE_ACCOUNT --query [0].value --output tsv)
    
    # Deploy container group
    az container create \
        --resource-group $RESOURCE_GROUP \
        --name $CONTAINER_GROUP \
        --image $ACR_NAME.azurecr.io/chatbot:latest \
        --registry-login-server $ACR_NAME.azurecr.io \
        --registry-username $ACR_USERNAME \
        --registry-password $ACR_PASSWORD \
        --dns-name-label irado-chatbot \
        --ports 80 443 \
        --cpu 2 \
        --memory 4 \
        --environment-variables \
            FLASK_ENV=production \
            DATABASE_HOST=irado-chat-db.postgres.database.azure.com \
            DATABASE_NAME=irado_chat \
            DATABASE_USER=irado_admin \
            DATABASE_PASSWORD=$CHAT_DB_PASSWORD \
            BEDRIJFSKLANTEN_DB_HOST=irado-bedrijfsklanten-db.postgres.database.azure.com \
            BEDRIJFSKLANTEN_DB_NAME=irado_bedrijfsklanten \
            BEDRIJFSKLANTEN_DB_USER=irado_admin \
            BEDRIJFSKLANTEN_DB_PASSWORD=$BEDRIJFSKLANTEN_DB_PASSWORD \
        --secure-environment-variables \
            OPENAI_API_KEY=$OPENAI_API_KEY \
        --restart-policy Always
    
    success "Container group deployed"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Create Log Analytics Workspace
    az monitor log-analytics workspace create \
        --resource-group $RESOURCE_GROUP \
        --workspace-name irado-logs \
        --location $LOCATION
    
    # Create Application Insights
    az monitor app-insights component create \
        --resource-group $RESOURCE_GROUP \
        --app irado-chatbot-insights \
        --location $LOCATION \
        --kind web
    
    success "Monitoring setup completed"
}

# Main deployment function
main() {
    log "Starting Azure deployment for Irado Chatbot System"
    echo "=================================================="
    
    # Pre-deployment checks
    check_azure_cli
    check_azure_login
    
    # Create Azure resources
    create_resource_group
    create_acr
    create_key_vault
    create_storage_account
    create_postgresql_databases
    
    # Build and deploy
    build_and_push_images
    deploy_container_group
    setup_monitoring
    
    # Get deployment information
    log "Getting deployment information..."
    FQDN=$(az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_GROUP --query ipAddress.fqdn --output tsv)
    
    success "Deployment completed successfully!"
    echo ""
    echo "=================================================="
    echo "🌐 Application URL: http://$FQDN"
    echo "📊 Dashboard URL: http://$FQDN/dashboard"
    echo "🔧 Resource Group: $RESOURCE_GROUP"
    echo "📦 Container Registry: $ACR_NAME.azurecr.io"
    echo "🗄️ Key Vault: $KEY_VAULT_NAME"
    echo "💾 Storage Account: $STORAGE_ACCOUNT"
    echo "=================================================="
    echo ""
    echo "Next steps:"
    echo "1. Configure DNS records for your domain"
    echo "2. Set up SSL certificates"
    echo "3. Configure monitoring alerts"
    echo "4. Test the application"
}

# Run main function
main "$@"
