#!/bin/bash

# Irado Project Migration Script
# Version: 2.1.1
# Date: $(date)

set -e

echo "🚀 Irado Project Migration Script v2.1.1"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Running as root. Consider using a regular user for development.${NC}"
fi

# Check system requirements
echo -e "${BLUE}🔍 Checking system requirements...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI is not installed. Please install Azure CLI first.${NC}"
    echo "   Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if Python 3.11+ is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.11+ first.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠️  PostgreSQL client not found. Installing...${NC}"
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y postgresql-client
    elif command -v yum &> /dev/null; then
        sudo yum install -y postgresql
    else
        echo -e "${YELLOW}⚠️  Please install postgresql-client manually${NC}"
    fi
fi

echo -e "${GREEN}✅ System requirements check completed${NC}"
echo ""

# Create project directory
PROJECT_DIR="/opt/irado-azure"
echo -e "${BLUE}📁 Setting up project directory: $PROJECT_DIR${NC}"

if [ ! -d "$PROJECT_DIR" ]; then
    sudo mkdir -p "$PROJECT_DIR"
    echo -e "${GREEN}✅ Created project directory${NC}"
else
    echo -e "${YELLOW}⚠️  Project directory already exists${NC}"
fi

# Set permissions
sudo chown -R $USER:$USER "$PROJECT_DIR" 2>/dev/null || true

# Extract project files (assuming this script is run from the extracted archive)
echo -e "${BLUE}📦 Extracting project files...${NC}"
if [ -f "irado-project-v2.1.1.tar.gz" ]; then
    tar -xzf irado-project-v2.1.1.tar.gz -C "$PROJECT_DIR"
    echo -e "${GREEN}✅ Project files extracted${NC}"
else
    echo -e "${YELLOW}⚠️  Archive not found. Please ensure irado-project-v2.1.1.tar.gz is in the current directory${NC}"
fi

# Set up Python virtual environment
echo -e "${BLUE}🐍 Setting up Python virtual environment...${NC}"
cd "$PROJECT_DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Activate virtual environment and install dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
source venv/bin/activate

# Install chatbot dependencies
if [ -f "chatbot/requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r chatbot/requirements.txt
    echo -e "${GREEN}✅ Chatbot dependencies installed${NC}"
fi

# Install dashboard dependencies
if [ -f "dashboard/requirements.txt" ]; then
    pip install -r dashboard/requirements.txt
    echo -e "${GREEN}✅ Dashboard dependencies installed${NC}"
fi

# Set up Azure CLI
echo -e "${BLUE}☁️  Azure CLI setup...${NC}"
echo "Please log in to Azure CLI:"
echo "Run: az login"
echo "Then run: az account set --subscription <your-subscription-id>"
echo ""

# Set up Docker
echo -e "${BLUE}🐳 Docker setup...${NC}"
echo "Please log in to Azure Container Registry:"
echo "Run: az acr login --name <your-acr-name>"
echo ""

# Check for existing configuration files
echo -e "${BLUE}🔧 Checking configuration files...${NC}"

# Check if .env exists
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file found${NC}"
else
    echo -e "${YELLOW}⚠️  .env file not found. You may need to create one.${NC}"
fi

# Check if azure-credentials exists
if [ -f "azure-credentials" ]; then
    echo -e "${GREEN}✅ azure-credentials found${NC}"
else
    echo -e "${YELLOW}⚠️  azure-credentials not found. You may need to create one.${NC}"
fi

# Check if deployment scripts have hardcoded values
echo -e "${BLUE}🔍 Checking deployment scripts for hardcoded values...${NC}"
if grep -q "lqBp6OF31+wCNXzyTMvasFrspdtL+IWPGVtooy2zjS4=" deploy-to-azure.sh 2>/dev/null; then
    echo -e "${GREEN}✅ Database password found in deployment script${NC}"
fi

if grep -q "BXFgQF9udVZRqyhvapyyKmaO5MxXH5CUZb2Xf992rD99al4C4zyKJQQJ99BJACfhMk5XJ3w3AAAAACOGL8rA" deploy-to-azure.sh 2>/dev/null; then
    echo -e "${GREEN}✅ Azure OpenAI API key found in deployment script${NC}"
fi

if grep -q "https://info-mgal213r-swedencentral.cognitiveservices.azure.com" deploy-to-azure.sh 2>/dev/null; then
    echo -e "${GREEN}✅ Azure OpenAI endpoint found in deployment script${NC}"
fi

# Make scripts executable
echo -e "${BLUE}🔧 Making scripts executable...${NC}"
chmod +x *.sh
chmod +x azure/*.sh 2>/dev/null || true
echo -e "${GREEN}✅ Scripts made executable${NC}"

# Create quick start guide
cat > QUICK_START_MIGRATION.md << EOF
# Irado Project - Quick Start Guide

## Project Status
- **Version**: 2.1.1
- **Status**: Fully operational on Azure
- **Components**: Chatbot, Dashboard, Database

## Quick Start

### 1. Azure Setup
\`\`\`bash
# Login to Azure
az login

# Set subscription
az account set --subscription <your-subscription-id>

# Login to ACR
az acr login --name <your-acr-name>
\`\`\`

### 2. Environment Configuration
\`\`\bash
# Update .env file with your values
nano .env
\`\`\`

### 3. Deploy Chatbot
\`\`\`bash
./deploy-to-azure.sh
\`\`\`

### 4. Deploy Dashboard
\`\`\`bash
./deploy-dashboard-to-azure.sh
\`\`\`

### 5. Apply Database Schema
\`\`\`bash
./apply-system-prompt-schema-azure.sh
\`\`\`

## URLs
- **Chatbot**: https://irado-chatbot-app.azurewebsites.net
- **Dashboard**: https://irado-dashboard-app.azurewebsites.net

## Troubleshooting
- Check logs: \`az webapp log tail --name <webapp-name> --resource-group irado-rg\`
- Health check: \`curl https://irado-chatbot-app.azurewebsites.net/health\`

## Support
- Documentation: See README files in project
- Version: 2.1.1
- Last updated: $(date)
EOF

echo -e "${GREEN}✅ Quick start guide created${NC}"

# Final status
echo ""
echo -e "${GREEN}🎉 Migration completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Update .env file with your Azure credentials"
echo "2. Run: az login"
echo "3. Run: az acr login --name <your-acr-name>"
echo "4. Deploy: ./deploy-to-azure.sh"
echo "5. Deploy dashboard: ./deploy-dashboard-to-azure.sh"
echo ""
echo -e "${BLUE}📖 Documentation:${NC}"
echo "- Quick start: QUICK_START_MIGRATION.md"
echo "- Azure setup: AZURE_QUICKSTART.md"
echo "- Dashboard: DASHBOARD_QUICKSTART.md"
echo ""
echo -e "${GREEN}✅ Ready for development!${NC}"
