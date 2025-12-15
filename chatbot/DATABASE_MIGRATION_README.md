# KOAD naar Database Migratie

## Overzicht

De KOAD blacklist is gemigreerd van CSV naar PostgreSQL database. Dit biedt betere prestaties, schaalbaarheid en beheerbaarheid.

## Belangrijke Veranderingen

### 🗄️ Database Schema
- **Tabel**: `bedrijfsklanten` (voormalig KOAD blacklist)
- **Database**: PostgreSQL `irado`
- **Functies**: `is_bedrijfsklant()`, `get_bedrijfsklant_info()`
- **Views**: `bedrijfsklanten_stats` voor statistieken

### 🔄 Migratie Details
- **Van**: CSV bestand (`koad.csv`)
- **Naar**: PostgreSQL database
- **Overschrijving**: Nieuwe CSV uploads overschrijven alle bestaande data
- **Backup**: Automatische backup bij uploads

### 🏗️ Nieuwe Componenten

#### Database Service (`database_service.py`)
```python
from database_service import BedrijfsklantenDatabaseService

db = BedrijfsklantenDatabaseService()
is_blocked = db.is_bedrijfsklant('3136HN', '464')
info = db.get_bedrijfsklant_info('3136HN', '464')
```

#### Address Validation (Updated)
```python
from address_validation import AddressValidationService

validator = AddressValidationService()
result = validator.validate_address('3136HN', '464')
is_blocked = validator.is_address_blocked('3136HN', '464')
```

### 📊 Dashboard Updates
- **Terminologie**: "KOAD Blacklist" → "Bedrijfsklanten"
- **Database**: Alle operaties via PostgreSQL
- **CSV Upload**: Overschrijft bestaande data
- **Performance**: Snellere zoekopdrachten

## Installatie

### 1. Database Setup
```bash
# Run installatie script
sudo /opt/irado/chatbot/install_database_migration.sh
```

### 2. Handmatige Installatie
```bash
# Install dependencies
pip3 install psycopg2-binary pandas requests

# Create database
sudo -u postgres psql -c "CREATE DATABASE irado;"
sudo -u postgres psql -c "CREATE USER irado WITH PASSWORD 'irado123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE irado TO irado;"

# Create schema
sudo -u postgres psql -d irado -f /opt/irado/chatbot/database_schema.sql

# Run migration
cd /opt/irado/chatbot
python3 migrate_koad_to_database.py
```

### 3. Test Integratie
```bash
# Test alle functionaliteit
python3 /opt/irado/chatbot/test_database_integration.py
```

## Database Schema

### Tabel: `bedrijfsklanten`
```sql
CREATE TABLE bedrijfsklanten (
    id SERIAL PRIMARY KEY,
    koad_nummer VARCHAR(20) UNIQUE,
    straat VARCHAR(255),
    postcode VARCHAR(10),
    huisnummer VARCHAR(20),
    huisnummer_toevoeging VARCHAR(10),
    etage VARCHAR(50),
    naam VARCHAR(255),
    actief BOOLEAN DEFAULT true,
    inwoner BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Functies
```sql
-- Check if address is bedrijfsklant
SELECT is_bedrijfsklant('3136HN', '464');

-- Get bedrijfsklant info
SELECT * FROM get_bedrijfsklant_info('3136HN', '464');

-- Get statistics
SELECT * FROM bedrijfsklanten_stats;
```

## API Endpoints

### Dashboard API (Port 3256)
- `GET /api/koad` - Alle bedrijfsklanten
- `GET /api/koad/search?q=query` - Zoek bedrijfsklanten
- `POST /api/koad/upload` - Upload CSV (overschrijft data)
- `DELETE /api/koad/{id}` - Verwijder bedrijfsklant
- `PUT /api/koad/{id}` - Update bedrijfsklant

### Chatbot Integration
- Address validation gebruikt database
- Geen CSV bestand meer nodig
- Betere performance

## Beheer

### Database Connectie
```bash
# Connect to database
psql -h localhost -U irado -d irado

# View records
SELECT COUNT(*) FROM bedrijfsklanten;
SELECT * FROM bedrijfsklanten LIMIT 10;

# View statistics
SELECT * FROM bedrijfsklanten_stats;
```

### CSV Upload via Dashboard
1. Ga naar http://localhost:3256/dashboard
2. Klik op "Upload CSV"
3. Selecteer CSV bestand
4. Upload overschrijft alle bestaande data

### Backup & Restore
```bash
# Backup database
pg_dump -h localhost -U irado irado > backup.sql

# Restore database
psql -h localhost -U irado irado < backup.sql
```

## Monitoring

### Service Status
```bash
# Check dashboard service
systemctl status dashboard-express

# Check logs
journalctl -u dashboard-express -f
```

### Database Monitoring
```sql
-- Check table size
SELECT pg_size_pretty(pg_total_relation_size('bedrijfsklanten'));

-- Check recent uploads
SELECT * FROM csv_uploads ORDER BY upload_date DESC LIMIT 10;

-- Check performance
EXPLAIN ANALYZE SELECT * FROM bedrijfsklanten WHERE postcode = '3136HN';
```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL status
systemctl status postgresql

# Check database exists
sudo -u postgres psql -l | grep irado

# Check user permissions
sudo -u postgres psql -d irado -c "\du"
```

### Dashboard Issues
```bash
# Restart dashboard
systemctl restart dashboard-express

# Check logs
journalctl -u dashboard-express -f

# Test API
curl http://localhost:3256/health
```

### Migration Issues
```bash
# Re-run migration
cd /opt/irado/chatbot
python3 migrate_koad_to_database.py

# Check migration logs
tail -f /opt/irado/chatbot/migration.log
```

## Performance

### Voordelen
- **Snellere zoekopdrachten**: Database indexes
- **Betere schaalbaarheid**: PostgreSQL vs CSV
- **Concurrent access**: Meerdere gebruikers tegelijk
- **Data integriteit**: Constraints en validatie

### Indexes
```sql
-- Performance indexes
CREATE INDEX idx_bedrijfsklanten_postcode_huisnummer ON bedrijfsklanten(postcode, huisnummer);
CREATE INDEX idx_bedrijfsklanten_naam ON bedrijfsklanten(naam);
CREATE INDEX idx_bedrijfsklanten_actief ON bedrijfsklanten(actief) WHERE actief = true;
```

## Security

### Database Security
- Gebruiker `irado` met beperkte rechten
- Wachtwoord beveiliging
- Database-level constraints

### API Security
- Input validatie
- SQL injection bescherming
- Error handling zonder data lekken

## Backup Strategy

### Automatische Backups
- Bij elke CSV upload wordt backup gemaakt
- Backups opgeslagen in `/opt/irado/chatbot/backups/`
- Retentie: 30 dagen

### Handmatige Backups
```bash
# Full database backup
pg_dump -h localhost -U irado irado > backup_$(date +%Y%m%d).sql

# Table-specific backup
pg_dump -h localhost -U irado -t bedrijfsklanten irado > bedrijfsklanten_backup.sql
```

## Rollback Plan

### Terug naar CSV
1. Export database naar CSV:
```sql
COPY bedrijfsklanten TO '/tmp/bedrijfsklanten.csv' WITH CSV HEADER;
```

2. Herstel oude CSV:
```bash
cp /opt/irado/chatbot/backups/koad_backup_*.csv /opt/irado/chatbot/koad.csv
```

3. Herstart chatbot services

### Database Rollback
```bash
# Restore from backup
psql -h localhost -U irado irado < backup.sql

# Restart services
systemctl restart dashboard-express
```

## Support

### Logs
- **Migration**: `/opt/irado/chatbot/migration.log`
- **Dashboard**: `journalctl -u dashboard-express`
- **Database**: PostgreSQL logs

### Debugging
```bash
# Test database connection
python3 -c "from database_service import BedrijfsklantenDatabaseService; db = BedrijfsklantenDatabaseService(); print('OK'); db.close()"

# Test address validation
python3 -c "from address_validation import AddressValidationService; v = AddressValidationService(); print(v.is_address_blocked('3136HN', '464'))"
```

## Changelog

### v1.0.0 - Database Migration
- ✅ CSV naar PostgreSQL migratie
- ✅ Dashboard updates (bedrijfsklanten terminologie)
- ✅ Address validation database integratie
- ✅ CSV upload functionaliteit
- ✅ Performance verbeteringen
- ✅ Backup & restore functionaliteit





