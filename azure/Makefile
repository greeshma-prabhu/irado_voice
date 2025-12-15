# Makefile for Irado Chatbot Azure Deployment
# Simplifies common development and deployment tasks

.PHONY: help build push deploy start stop restart logs clean test

# Default target
help:
	@echo "Irado Chatbot Azure Deployment"
	@echo "=============================="
	@echo ""
	@echo "Available targets:"
	@echo "  build       - Build all Docker images"
	@echo "  push        - Push images to Azure Container Registry"
	@echo "  deploy      - Deploy to Azure Container Instances"
	@echo "  start       - Start local development environment"
	@echo "  stop        - Stop local development environment"
	@echo "  restart     - Restart local development environment"
	@echo "  logs        - View container logs"
	@echo "  clean       - Clean up containers and volumes"
	@echo "  test        - Run tests"
	@echo "  status      - Check container status"
	@echo "  shell       - Open shell in chatbot container"
	@echo "  db-shell    - Open database shell"
	@echo "  backup      - Backup databases"
	@echo "  restore     - Restore databases"
	@echo ""

# Build all Docker images
build:
	@echo "Building Docker images..."
	docker build -t irado-chatbot:latest ./containers/chatbot/
	docker build -t irado-dashboard:latest ./containers/dashboard/
	docker build -t irado-website:latest ./containers/website/
	docker build -t irado-dashboard-frontend:latest ./containers/dashboard-frontend/
	@echo "✅ All images built successfully"

# Push images to Azure Container Registry
push:
	@echo "Pushing images to Azure Container Registry..."
	az acr login --name irado
	docker tag irado-chatbot:latest irado.azurecr.io/chatbot:latest
	docker tag irado-dashboard:latest irado.azurecr.io/dashboard:latest
	docker tag irado-website:latest irado.azurecr.io/website:latest
	docker tag irado-dashboard-frontend:latest irado.azurecr.io/dashboard-frontend:latest
	docker push irado.azurecr.io/chatbot:latest
	docker push irado.azurecr.io/dashboard:latest
	docker push irado.azurecr.io/website:latest
	docker push irado.azurecr.io/dashboard-frontend:latest
	@echo "✅ All images pushed successfully"

# Deploy to Azure Container Instances
deploy:
	@echo "Deploying to Azure Container Instances..."
	./deploy.sh
	@echo "✅ Deployment completed"

# Start local development environment
start:
	@echo "Starting local development environment..."
	docker-compose up -d
	@echo "✅ Local environment started"
	@echo "🌐 Website: http://localhost:3254"
	@echo "📊 Dashboard: http://localhost:3256"
	@echo "🤖 Chatbot API: http://localhost:5000"

# Stop local development environment
stop:
	@echo "Stopping local development environment..."
	docker-compose down
	@echo "✅ Local environment stopped"

# Restart local development environment
restart: stop start

# View container logs
logs:
	@echo "Viewing container logs..."
	docker-compose logs -f

# View specific service logs
logs-chatbot:
	docker-compose logs -f chatbot

logs-dashboard:
	docker-compose logs -f dashboard

logs-website:
	docker-compose logs -f website

logs-dashboard-frontend:
	docker-compose logs -f dashboard-frontend

# Clean up containers and volumes
clean:
	@echo "Cleaning up containers and volumes..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ Cleanup completed"

# Run tests
test:
	@echo "Running tests..."
	docker-compose exec chatbot python -m pytest tests/
	docker-compose exec dashboard python -m pytest tests/
	@echo "✅ Tests completed"

# Check container status
status:
	@echo "Container Status:"
	@echo "=================="
	docker-compose ps

# Open shell in chatbot container
shell:
	@echo "Opening shell in chatbot container..."
	docker-compose exec chatbot /bin/sh

# Open database shell
db-shell:
	@echo "Opening database shell..."
	docker-compose exec postgres-chat psql -U irado -d irado_chat

db-shell-bedrijfsklanten:
	@echo "Opening bedrijfsklanten database shell..."
	docker-compose exec postgres-bedrijfsklanten psql -U irado -d irado_bedrijfsklanten

# Backup databases
backup:
	@echo "Backing up databases..."
	mkdir -p backups
	docker-compose exec postgres-chat pg_dump -U irado irado_chat > backups/chat_backup_$(shell date +%Y%m%d_%H%M%S).sql
	docker-compose exec postgres-bedrijfsklanten pg_dump -U irado irado_bedrijfsklanten > backups/bedrijfsklanten_backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backups completed"

# Restore databases
restore:
	@echo "Restoring databases..."
	@echo "Available backups:"
	@ls -la backups/
	@echo "Please specify backup file: make restore FILE=backup_file.sql"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r containers/chatbot/requirements.txt
	pip install -r containers/dashboard/requirements.txt
	npm install --prefix containers/website
	npm install --prefix containers/dashboard-frontend
	@echo "✅ Dependencies installed"

# Setup development environment
setup: install
	@echo "Setting up development environment..."
	cp .env.example .env
	@echo "✅ Development environment setup completed"
	@echo "📝 Please edit .env file with your configuration"

# Health check
health:
	@echo "Checking service health..."
	@curl -f http://localhost:3254/health && echo "✅ Website healthy" || echo "❌ Website unhealthy"
	@curl -f http://localhost:3256/health && echo "✅ Dashboard healthy" || echo "❌ Dashboard unhealthy"
	@curl -f http://localhost:5000/health && echo "✅ Chatbot healthy" || echo "❌ Chatbot unhealthy"
	@curl -f http://localhost:5001/health && echo "✅ Dashboard service healthy" || echo "❌ Dashboard service unhealthy"

# Database migration
migrate:
	@echo "Running database migrations..."
	docker-compose exec chatbot python migrate_koad_to_database.py
	@echo "✅ Migrations completed"

# Load test data
load-test-data:
	@echo "Loading test data..."
	docker-compose exec chatbot python load_test_data.py
	@echo "✅ Test data loaded"

# Performance test
perf-test:
	@echo "Running performance tests..."
	docker-compose exec chatbot python perf_test.py
	@echo "✅ Performance tests completed"

# Security scan
security-scan:
	@echo "Running security scan..."
	docker run --rm -v $(PWD):/app securecodewarrior/docker-security-scan /app
	@echo "✅ Security scan completed"

# Update dependencies
update-deps:
	@echo "Updating dependencies..."
	docker-compose exec chatbot pip install --upgrade -r requirements.txt
	docker-compose exec dashboard pip install --upgrade -r requirements.txt
	docker-compose exec website npm update
	docker-compose exec dashboard-frontend npm update
	@echo "✅ Dependencies updated"

# Generate documentation
docs:
	@echo "Generating documentation..."
	docker-compose exec chatbot python -m pydoc -w .
	docker-compose exec dashboard python -m pydoc -w .
	@echo "✅ Documentation generated"

# Format code
format:
	@echo "Formatting code..."
	docker-compose exec chatbot black .
	docker-compose exec chatbot isort .
	docker-compose exec dashboard black .
	docker-compose exec dashboard isort .
	@echo "✅ Code formatted"

# Lint code
lint:
	@echo "Linting code..."
	docker-compose exec chatbot flake8 .
	docker-compose exec dashboard flake8 .
	@echo "✅ Linting completed"
