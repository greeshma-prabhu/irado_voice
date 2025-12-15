# Azure Container Architecture - Irado Chatbot

## 🏗️ Overzicht

Azure container architectuur voor het Irado chatbot systeem met microservices en managed databases.

## 📊 Huidige Architectuur Analyse

### Services:
1. **Chatbot Service** (Flask) - Port 5000
2. **Dashboard Service** (Flask) - Port 5001  
3. **Express.js Proxy** - Port 3254 (website)
4. **Express.js Dashboard** - Port 3256 (dashboard)
5. **PostgreSQL Database** - Chat history
6. **PostgreSQL Database** - Bedrijfsklanten (KOAD)

### Dependencies:
- **OpenAI API** - AI responses
- **Open Postcode API** - Address validation
- **Email Service** - Notifications
- **File System** - Static files, backups

## 🐳 Azure Container Architectuur

### Container Services:

#### 1. **Chatbot Container**
- **Service**: Main chatbot Flask app
- **Port**: 5000 (internal)
- **Dependencies**: PostgreSQL (chat), PostgreSQL (bedrijfsklanten)
- **External APIs**: OpenAI, Open Postcode

#### 2. **Dashboard Container** 
- **Service**: Dashboard Flask app
- **Port**: 5001 (internal)
- **Dependencies**: PostgreSQL (bedrijfsklanten), PostgreSQL (chat)
- **Features**: CSV upload, bedrijfsklanten management

#### 3. **Website Container**
- **Service**: Express.js website proxy
- **Port**: 80/443 (external)
- **Dependencies**: Chatbot container
- **Features**: Static website, chatbot proxy

#### 4. **Dashboard Frontend Container**
- **Service**: Express.js dashboard proxy  
- **Port**: 80/443 (external)
- **Dependencies**: Dashboard container
- **Features**: Dashboard proxy, static files

### Azure Managed Services:

#### 1. **Azure Database for PostgreSQL - Flexible Server**
- **Database 1**: Chat history
- **Database 2**: Bedrijfsklanten (KOAD)
- **Benefits**: Managed, scalable, backup

#### 2. **Azure Container Instances (ACI)**
- **Alternative**: Azure Container Apps
- **Benefits**: Serverless, auto-scaling

#### 3. **Azure Application Gateway**
- **Load Balancer**: Route traffic to containers
- **SSL Termination**: HTTPS support
- **Health Checks**: Container monitoring

#### 4. **Azure Key Vault**
- **Secrets**: API keys, database passwords
- **Configuration**: Environment variables

#### 5. **Azure Storage Account**
- **File Storage**: Static files, backups
- **Blob Storage**: CSV uploads, logs

## 🔄 Container Communication

```
Internet → Application Gateway → Website Container → Chatbot Container
                                ↓
                            Dashboard Container ← Dashboard Frontend Container
                                ↓
                            PostgreSQL (Chat) + PostgreSQL (Bedrijfsklanten)
```

## 📦 Container Specifications

### Chatbot Container:
- **Base**: Python 3.11 Alpine
- **Size**: ~500MB
- **Memory**: 512MB
- **CPU**: 0.5 cores
- **Environment**: Production

### Dashboard Container:
- **Base**: Python 3.11 Alpine  
- **Size**: ~400MB
- **Memory**: 256MB
- **CPU**: 0.25 cores
- **Environment**: Production

### Website Container:
- **Base**: Node.js 18 Alpine
- **Size**: ~200MB
- **Memory**: 128MB
- **CPU**: 0.25 cores
- **Environment**: Production

### Dashboard Frontend Container:
- **Base**: Node.js 18 Alpine
- **Size**: ~200MB  
- **Memory**: 128MB
- **CPU**: 0.25 cores
- **Environment**: Production

## 🌐 Networking

### Internal Communication:
- **Chatbot ↔ Dashboard**: Direct container communication
- **Website ↔ Chatbot**: HTTP calls
- **Dashboard Frontend ↔ Dashboard**: HTTP calls

### External Communication:
- **OpenAI API**: HTTPS outbound
- **Open Postcode API**: HTTPS outbound
- **Email Service**: SMTP outbound

## 🔒 Security

### Container Security:
- **Non-root users**: All containers run as non-root
- **Read-only filesystems**: Immutable containers
- **Secrets management**: Azure Key Vault integration
- **Network policies**: Container-to-container communication

### Database Security:
- **Encryption**: TLS for all connections
- **Authentication**: Managed identity
- **Firewall**: IP restrictions
- **Backup**: Automated backups

## 📊 Monitoring & Logging

### Azure Monitor:
- **Container Insights**: Performance monitoring
- **Application Insights**: Application telemetry
- **Log Analytics**: Centralized logging

### Health Checks:
- **Liveness**: Container health
- **Readiness**: Service readiness
- **Startup**: Initialization checks

## 💰 Cost Optimization

### Container Sizing:
- **Right-sizing**: Minimal resource allocation
- **Auto-scaling**: Scale based on demand
- **Spot instances**: Cost-effective compute

### Database Optimization:
- **Serverless**: Pay-per-use database
- **Reserved capacity**: Long-term discounts
- **Storage optimization**: Efficient data storage

## 🚀 Deployment Strategy

### Blue-Green Deployment:
- **Zero downtime**: Seamless updates
- **Rollback capability**: Quick recovery
- **Testing**: Staging environment

### CI/CD Pipeline:
- **GitHub Actions**: Automated builds
- **Container Registry**: Azure Container Registry
- **Deployment**: Azure Container Instances

## 📈 Scalability

### Horizontal Scaling:
- **Container Instances**: Multiple replicas
- **Load Balancing**: Traffic distribution
- **Database Scaling**: Read replicas

### Vertical Scaling:
- **Resource allocation**: CPU/Memory scaling
- **Database performance**: Tier upgrades
- **Storage scaling**: Capacity increases

## 🔧 Configuration Management

### Environment Variables:
- **Development**: Local development
- **Staging**: Pre-production testing
- **Production**: Live environment

### Secrets Management:
- **API Keys**: OpenAI, external services
- **Database Credentials**: Connection strings
- **SSL Certificates**: TLS configuration

## 📋 Migration Strategy

### Phase 1: Container Preparation
- Dockerize all services
- Create Azure configurations
- Set up CI/CD pipeline

### Phase 2: Database Migration
- Migrate to Azure PostgreSQL
- Data synchronization
- Performance testing

### Phase 3: Container Deployment
- Deploy to Azure Container Instances
- Configure networking
- Set up monitoring

### Phase 4: Production Cutover
- DNS updates
- Traffic migration
- Monitoring and optimization
