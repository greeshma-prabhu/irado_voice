#!/usr/bin/env python3
"""
Setup KOAD table in chat database and import CSV
Quick and simple - matches CSV structure exactly
"""
import psycopg2
import subprocess
import sys
import csv

print('🔧 KOAD Database Setup (Simple)')
print('=' * 50)

# Get password
print('\n1️⃣ Getting credentials...')
try:
    result = subprocess.run([
        'az', 'webapp', 'config', 'appsettings', 'list',
        '--name', 'irado-chatbot-app',
        '--resource-group', 'irado-rg',
        '--query', "[?name=='POSTGRES_PASSWORD'].value",
        '-o', 'tsv'
    ], capture_output=True, text=True, check=True, timeout=10)
    password = result.stdout.strip()
    print('✅ Got password')
except Exception as e:
    print(f'❌ Failed: {e}')
    sys.exit(1)

# Connect
print('\n2️⃣ Connecting to chat database...')
try:
    conn = psycopg2.connect(
        host='irado-chat-db.postgres.database.azure.com',
        port=5432,
        database='irado_chat',
        user='irado_admin',
        password=password,
        sslmode='require',
        connect_timeout=10
    )
    conn.autocommit = False
    cur = conn.cursor()
    print('✅ Connected')
except Exception as e:
    print(f'❌ Failed: {e}')
    sys.exit(1)

# Drop old table
print('\n3️⃣ Dropping old table if exists...')
try:
    cur.execute('DROP TABLE IF EXISTS bedrijfsklanten CASCADE')
    conn.commit()
    print('✅ Old table dropped')
except Exception as e:
    print(f'⚠️  Warning: {e}')
    conn.rollback()

# Create new table (exact CSV structure)
print('\n4️⃣ Creating table (matching CSV)...')
try:
    cur.execute('''
        CREATE TABLE bedrijfsklanten (
            "KOAD-nummer" VARCHAR(255),
            "KOAD-str" VARCHAR(255),
            "KOAD-pc" VARCHAR(10),
            "KOAD-huisaand" VARCHAR(50),
            "KOAD-huisnr" VARCHAR(20),
            "KOAD-etage" VARCHAR(50),
            "KOAD-naam" VARCHAR(255),
            "KOAD-actief" VARCHAR(1) DEFAULT '1',
            "KOAD-inwoner" VARCHAR(1) DEFAULT '1'
        )
    ''')
    conn.commit()
    print('✅ Table created')
except Exception as e:
    print(f'❌ Failed: {e}')
    conn.rollback()
    conn.close()
    sys.exit(1)

# Create index
print('\n5️⃣ Creating index...')
try:
    cur.execute('''
        CREATE INDEX idx_bedrijfsklanten_lookup 
        ON bedrijfsklanten ("KOAD-pc", "KOAD-huisnr")
    ''')
    conn.commit()
    print('✅ Index created')
except Exception as e:
    print(f'⚠️  Warning: {e}')
    conn.rollback()

# Import CSV using COPY (fastest way)
print('\n6️⃣ Importing CSV data...')
try:
    print('   Reading CSV file...')
    with open('/opt/irado/chatbot/koad.csv', 'r', encoding='utf-8') as f:
        # Skip header
        next(f)
        
        print('   Copying data to database...')
        cur.copy_expert(
            """
            COPY bedrijfsklanten (
                "KOAD-nummer", "KOAD-str", "KOAD-pc", "KOAD-huisaand",
                "KOAD-huisnr", "KOAD-etage", "KOAD-naam", "KOAD-actief", "KOAD-inwoner"
            ) FROM STDIN WITH CSV
            """,
            f
        )
    
    conn.commit()
    print('✅ CSV data imported')
except Exception as e:
    print(f'❌ Failed: {e}')
    conn.rollback()
    conn.close()
    sys.exit(1)

# Verify
print('\n7️⃣ Verifying...')
try:
    cur.execute('SELECT COUNT(*) FROM bedrijfsklanten')
    count = cur.fetchone()[0]
    print(f'✅ Total records: {count:,}')
    
    cur.execute('SELECT "KOAD-pc", "KOAD-huisnr", "KOAD-naam" FROM bedrijfsklanten LIMIT 3')
    print('\n   Sample records:')
    for pc, hn, naam in cur.fetchall():
        print(f'   - {pc} {hn}: {naam}')
except Exception as e:
    print(f'⚠️  Verification warning: {e}')

conn.close()

print('\n' + '=' * 50)
print('🎉 SUCCESS!')
print('\n✅ bedrijfsklanten table is now in irado_chat database')
print('✅ Table structure matches CSV exactly')
print('✅ Ready for dashboard CSV uploads')
print('\nNext: Update app config to use single database')

