# Azure Container Deployment - Irado Chatbot

## 🏗️ Overzicht

Complete Azure container architectuur voor het Irado chatbot systeem met microservices, managed databases en container orchestration.

## 📊 Architectuur

### Container Services:
1. **Chatbot Container** - Flask AI service (Port 5000)
2. **Dashboard Container** - Flask dashboard service (Port 5001)  
3. **Website Container** - Express.js website proxy (Port 80/443)
4. **Dashboard Frontend Container** - Express.js dashboard proxy (Port 80/443)

### Azure Managed Services:
1. **Azure Database for PostgreSQL** - Chat history database
2. **Azure Database for PostgreSQL** - Bedrijfsklanten database
3. **Azure Container Registry** - Container images
4. **Azure Key Vault** - Secrets management
5. **Azure Storage Account** - File storage
6. **Azure Container Instances** - Container orchestration

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Set subscription
az account set --subscription "your-subscription-id"
```

### 2. Deploy to Azure
```bash
# Clone repository
git clone <repository-url>
cd azure

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"

# Run deployment script
./deploy.sh
```

### 3. Local Development
```bash
# Start local development environment
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f chatbot
```

## 📦 Container Details

### Chatbot Container
- **Base**: Python 3.11 Alpine
- **Size**: ~500MB
- **Memory**: 512MB
- **CPU**: 0.5 cores
- **Dependencies**: PostgreSQL (chat), PostgreSQL (bedrijfsklanten)
- **External APIs**: OpenAI, Open Postcode

### Dashboard Container
- **Base**: Python 3.11 Alpine
- **Size**: ~400MB
- **Memory**: 256MB
- **CPU**: 0.25 cores
- **Dependencies**: PostgreSQL (bedrijfsklanten), PostgreSQL (chat)
- **Features**: CSV upload, bedrijfsklanten management

### Website Container
- **Base**: Node.js 18 Alpine
- **Size**: ~200MB
- **Memory**: 128MB
- **CPU**: 0.25 cores
- **Dependencies**: Chatbot container
- **Features**: Static website, chatbot proxy

### Dashboard Frontend Container
- **Base**: Node.js 18 Alpine
- **Size**: ~200MB
- **Memory**: 128MB
- **CPU**: 0.25 cores
- **Dependencies**: Dashboard container
- **Features**: Dashboard proxy, static files

## 🗄️ Database Schema

### Chat Database (PostgreSQL)
```sql
-- Chat sessions table
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat messages table
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    role VARCHAR(50),
    content TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Bedrijfsklanten Database (PostgreSQL)
```sql
-- Bedrijfsklanten table
CREATE TABLE bedrijfsklanten (
    id SERIAL PRIMARY KEY,
    koad_nummer VARCHAR(20) UNIQUE,
    straat VARCHAR(255),
    postcode VARCHAR(10),
    huisnummer VARCHAR(20),
    naam VARCHAR(255),
    actief BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
DATABASE_HOST=postgres-server.postgres.database.azure.com
DATABASE_NAME=irado_chat
DATABASE_USER=irado_admin
DATABASE_PASSWORD=secure-password

# Bedrijfsklanten Database
BEDRIJFSKLANTEN_DB_HOST=bedrijfsklanten-server.postgres.database.azure.com
BEDRIJFSKLANTEN_DB_NAME=irado_bedrijfsklanten
BEDRIJFSKLANTEN_DB_USER=irado_admin
BEDRIJFSKLANTEN_DB_PASSWORD=secure-password

# External APIs
OPENAI_API_KEY=your-openai-api-key
OPEN_POSTCODE_API_BASE_URL=https://openpostcode.nl/api

# Application Configuration
FLASK_ENV=production
NODE_ENV=production
```

### Azure Key Vault Secrets
- `openai-api-key` - OpenAI API key
- `database-chat-password` - Chat database password
- `database-bedrijfsklanten-password` - Bedrijfsklanten database password
- `container-registry-password` - ACR password
- `storage-account-key` - Storage account key
- `email-smtp-password` - Email SMTP password

## 🌐 Networking

### Container Communication
```
Internet → Application Gateway → Website Container → Chatbot Container
                                ↓
                            Dashboard Container ← Dashboard Frontend Container
                                ↓
                            PostgreSQL (Chat) + PostgreSQL (Bedrijfsklanten)
```

### Port Configuration
- **Website**: 80/443 (HTTP/HTTPS)
- **Dashboard**: 80/443 (HTTP/HTTPS)
- **Chatbot**: 5000 (Internal)
- **Dashboard Service**: 5001 (Internal)
- **PostgreSQL Chat**: 5432 (Internal)
- **PostgreSQL Bedrijfsklanten**: 5432 (Internal)

## 🔒 Security

### Container Security
- **Non-root users**: All containers run as non-root
- **Read-only filesystems**: Immutable containers
- **Secrets management**: Azure Key Vault integration
- **Network policies**: Container-to-container communication

### Database Security
- **Encryption**: TLS for all connections
- **Authentication**: Managed identity
- **Firewall**: IP restrictions
- **Backup**: Automated backups

### Network Security
- **VNet Integration**: Private networking
- **NSG Rules**: Network security groups
- **SSL/TLS**: End-to-end encryption
- **Rate Limiting**: API protection

## 📊 Monitoring

### Azure Monitor
- **Container Insights**: Performance monitoring
- **Application Insights**: Application telemetry
- **Log Analytics**: Centralized logging
- **Metrics**: Custom metrics and alerts

### Health Checks
- **Liveness**: Container health
- **Readiness**: Service readiness
- **Startup**: Initialization checks

### Logging
- **Application Logs**: Container logs
- **Database Logs**: PostgreSQL logs
- **Access Logs**: Nginx logs
- **Error Logs**: Error tracking

## 💰 Cost Optimization

### Container Sizing
- **Right-sizing**: Minimal resource allocation
- **Auto-scaling**: Scale based on demand
- **Spot instances**: Cost-effective compute

### Database Optimization
- **Serverless**: Pay-per-use database
- **Reserved capacity**: Long-term discounts
- **Storage optimization**: Efficient data storage

### Storage Optimization
- **Lifecycle policies**: Automatic cleanup
- **Compression**: Data compression
- **Tiering**: Hot/Cool/Archive tiers

## 🚀 Deployment Strategies

### Blue-Green Deployment
- **Zero downtime**: Seamless updates
- **Rollback capability**: Quick recovery
- **Testing**: Staging environment

### CI/CD Pipeline
- **GitHub Actions**: Automated builds
- **Container Registry**: Azure Container Registry
- **Deployment**: Azure Container Instances

### Environment Management
- **Development**: Local Docker Compose
- **Staging**: Azure Container Instances
- **Production**: Azure Container Instances

## 📋 Maintenance

### Updates
```bash
# Update container images
az acr build --registry irado --image chatbot:latest ./containers/chatbot/
az acr build --registry irado --image dashboard:latest ./containers/dashboard/

# Deploy updates
az container restart --resource-group irado-rg --name irado-chatbot-system
```

### Backups
```bash
# Database backups
az postgres flexible-server backup create --resource-group irado-rg --name irado-chat-db
az postgres flexible-server backup create --resource-group irado-rg --name irado-bedrijfsklanten-db

# Storage backups
az storage blob copy start --source-uri https://source.blob.core.windows.net/container/blob --destination-uri https://dest.blob.core.windows.net/container/blob
```

### Monitoring
```bash
# Check container status
az container show --resource-group irado-rg --name irado-chatbot-system

# View logs
az container logs --resource-group irado-rg --name irado-chatbot-system --container-name chatbot

# Check metrics
az monitor metrics list --resource /subscriptions/{subscription-id}/resourceGroups/irado-rg/providers/Microsoft.ContainerInstance/containerGroups/irado-chatbot-system
```

## 🔧 Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check container logs
az container logs --resource-group irado-rg --name irado-chatbot-system --container-name chatbot

# Check container status
az container show --resource-group irado-rg --name irado-chatbot-system
```

#### Database Connection Issues
```bash
# Check database status
az postgres flexible-server show --resource-group irado-rg --name irado-chat-db

# Test connection
az postgres flexible-server connect --resource-group irado-rg --name irado-chat-db --admin-user irado_admin
```

#### Performance Issues
```bash
# Check resource usage
az monitor metrics list --resource /subscriptions/{subscription-id}/resourceGroups/irado-rg/providers/Microsoft.ContainerInstance/containerGroups/irado-chatbot-system

# Scale containers
az container update --resource-group irado-rg --name irado-chatbot-system --cpu 2 --memory 4
```

### Debug Commands
```bash
# Container shell access
az container exec --resource-group irado-rg --name irado-chatbot-system --container-name chatbot --exec-command "/bin/sh"

# Database queries
az postgres flexible-server execute --resource-group irado-rg --name irado-chat-db --admin-user irado_admin --admin-password password --database-name irado_chat --querytext "SELECT * FROM chat_sessions LIMIT 10;"
```

## 📚 Additional Resources

### Documentation
- [Azure Container Instances](https://docs.microsoft.com/en-us/azure/container-instances/)
- [Azure Database for PostgreSQL](https://docs.microsoft.com/en-us/azure/postgresql/)
- [Azure Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/)
- [Azure Storage](https://docs.microsoft.com/en-us/azure/storage/)

### Best Practices
- [Container Security](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-security)
- [Database Security](https://docs.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-security)
- [Monitoring](https://docs.microsoft.com/en-us/azure/azure-monitor/containers/container-insights-overview)

### Support
- [Azure Support](https://azure.microsoft.com/en-us/support/)
- [Community Forums](https://docs.microsoft.com/en-us/answers/topics/azure.html)
- [GitHub Issues](https://github.com/your-repo/issues)

## 🏷️ Tags

- **Environment**: Production
- **Application**: Irado-Chatbot
- **Version**: 1.0.0
- **Architecture**: Microservices
- **Platform**: Azure
- **Language**: Python, Node.js
- **Database**: PostgreSQL
- **Container**: Docker
