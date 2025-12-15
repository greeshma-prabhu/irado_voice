#!/usr/bin/env python3
import psycopg2
import subprocess
import sys

# Get password
result = subprocess.run([
    'az', 'webapp', 'config', 'appsettings', 'list',
    '--name', 'irado-chatbot-app',
    '--resource-group', 'irado-rg',
    '--query', "[?name=='POSTGRES_PASSWORD'].value",
    '-o', 'tsv'
], capture_output=True, text=True, timeout=10)
password = result.stdout.strip()

print('Connecting...')
conn = psycopg2.connect(
    host='irado-chat-db.postgres.database.azure.com',
    port=5432,
    database='irado_chat',
    user='irado_admin',
    password=password,
    sslmode='require',
    connect_timeout=5
)

cur = conn.cursor()
cur.execute('SET statement_timeout = 5000')  # 5 second timeout

print('Creating table...')
cur.execute('''
    CREATE TABLE IF NOT EXISTS bedrijfsklanten (
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

print('Creating index...')
cur.execute('CREATE INDEX IF NOT EXISTS idx_bedrijfsklanten_lookup ON bedrijfsklanten ("KOAD-pc", "KOAD-huisnr")')
conn.commit()
print('✅ Index created')

cur.execute('SELECT COUNT(*) FROM bedrijfsklanten')
count = cur.fetchone()[0]
print(f'✅ Current records: {count}')

conn.close()
print('🎉 Done! Now upload CSV via dashboard')

