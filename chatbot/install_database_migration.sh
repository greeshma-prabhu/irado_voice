#!/bin/bash

# Installatie script voor KOAD naar Database migratie
# Van CSV blacklist naar PostgreSQL bedrijfsklanten database

set -e

echo "🚀 Installing KOAD Database Migration..."
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Check if PostgreSQL is running
echo "📊 Checking PostgreSQL status..."
if ! systemctl is-active --quiet postgresql; then
    echo "❌ PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd /opt/irado/chatbot
pip3 install psycopg2-binary pandas

# Create database if it doesn't exist
echo "🗄️ Setting up database..."
sudo -u postgres psql -c "CREATE DATABASE irado;" 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER irado WITH PASSWORD 'irado123';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE irado TO irado;" 2>/dev/null || echo "Privileges already granted"

# Run database schema creation
echo "🏗️ Creating database schema..."
sudo -u postgres psql -d irado -f /opt/irado/chatbot/database_schema.sql

# Run migration
echo "🔄 Running KOAD migration..."
cd /opt/irado/chatbot
python3 migrate_koad_to_database.py

# Test database connection
echo "🧪 Testing database connection..."
python3 -c "
from database_service import BedrijfsklantenDatabaseService
db = BedrijfsklantenDatabaseService()
print('✅ Database connection successful')
print(f'Total records: {len(db.search_bedrijfsklanten(\"\", limit=10000))}')
db.close()
"

# Restart dashboard services
echo "🔄 Restarting dashboard services..."
systemctl restart dashboard-express

# Check service status
echo "📊 Checking service status..."
systemctl status dashboard-express --no-pager

echo ""
echo "✅ Installation complete!"
echo "🌐 Dashboard available at: http://localhost:3256/dashboard"
echo "📊 Database: PostgreSQL 'irado' database with 'bedrijfsklanten' table"
echo ""
echo "📋 Next steps:"
echo "  1. Test the dashboard at http://localhost:3256/dashboard"
echo "  2. Upload a new CSV to test the upload functionality"
echo "  3. Verify that the chatbot still works with the new database"
echo ""
echo "🔧 Database management:"
echo "  - Connect: psql -h localhost -U irado -d irado"
echo "  - View records: SELECT COUNT(*) FROM bedrijfsklanten;"
echo "  - View stats: SELECT * FROM bedrijfsklanten_stats;"





