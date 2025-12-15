#!/usr/bin/env python3
"""
Import KOAD CSV data into chat database
"""
import pandas as pd
import psycopg2
import subprocess
import sys

def get_password():
    """Get chat database password from Azure"""
    try:
        result = subprocess.run([
            'az', 'webapp', 'config', 'appsettings', 'list',
            '--name', 'irado-chatbot-app',
            '--resource-group', 'irado-rg',
            '--query', "[?name=='POSTGRES_PASSWORD'].value",
            '-o', 'tsv'
        ], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Failed to get password: {e}")
        sys.exit(1)

def main():
    print('📊 KOAD CSV Import to Chat Database')
    print('=' * 50)
    
    # Get password
    print('\n📋 Step 1: Getting database credentials...')
    password = get_password()
    print('✅ Credentials obtained')
    
    # Load CSV
    print('\n📋 Step 2: Loading KOAD CSV...')
    try:
        df = pd.read_csv('/opt/irado/chatbot/koad.csv')
        print(f'✅ Loaded {len(df)} records')
        print(f'   Columns: {list(df.columns)}')
    except Exception as e:
        print(f'❌ Failed to load CSV: {e}')
        sys.exit(1)
    
    # Connect to database
    print('\n📋 Step 3: Connecting to chat database...')
    try:
        conn = psycopg2.connect(
            host='irado-chat-db.postgres.database.azure.com',
            port=5432,
            database='irado_chat',
            user='irado_admin',
            password=password,
            sslmode='require'
        )
        cur = conn.cursor()
        print('✅ Connected to irado_chat database')
    except Exception as e:
        print(f'❌ Failed to connect: {e}')
        sys.exit(1)
    
    # Create table
    print('\n📋 Step 4: Creating bedrijfsklanten table...')
    try:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS bedrijfsklanten (
                id SERIAL PRIMARY KEY,
                bedrijf_id VARCHAR(255),
                postcode VARCHAR(10),
                huisnummer VARCHAR(20),
                straat VARCHAR(255),
                naam VARCHAR(255),
                actief BOOLEAN DEFAULT true,
                inwoner BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print('✅ Table created/verified')
    except Exception as e:
        print(f'❌ Failed to create table: {e}')
        conn.close()
        sys.exit(1)
    
    # Clear existing data
    print('\n📋 Step 5: Clearing existing data...')
    try:
        cur.execute('TRUNCATE TABLE bedrijfsklanten RESTART IDENTITY')
        conn.commit()
        print('✅ Existing data cleared')
    except Exception as e:
        print(f'❌ Failed to truncate: {e}')
        conn.close()
        sys.exit(1)
    
    # Insert data in batches
    print(f'\n📋 Step 6: Inserting {len(df)} records...')
    try:
        batch_size = 1000
        total = len(df)
        
        for start_idx in range(0, total, batch_size):
            end_idx = min(start_idx + batch_size, total)
            batch = df.iloc[start_idx:end_idx]
            
            for _, row in batch.iterrows():
                cur.execute('''
                    INSERT INTO bedrijfsklanten 
                    (bedrijf_id, postcode, huisnummer, straat, naam, actief, inwoner)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (
                    str(row.get('KOAD-nummer', '')),
                    str(row.get('KOAD-pc', '')),
                    str(row.get('KOAD-huisnr', '')),
                    str(row.get('KOAD-str', '')),
                    str(row.get('KOAD-naam', '')),
                    str(row.get('KOAD-actief', '1')) == '1',
                    str(row.get('KOAD-inwoner', '1')) == '1'
                ))
            
            conn.commit()
            print(f'   ✅ Inserted {end_idx}/{total} records ({int(end_idx/total*100)}%)')
        
        print(f'✅ All {total} records inserted')
    except Exception as e:
        print(f'❌ Failed to insert data: {e}')
        conn.rollback()
        conn.close()
        sys.exit(1)
    
    # Verify
    print('\n📋 Step 7: Verifying import...')
    try:
        cur.execute('SELECT COUNT(*) FROM bedrijfsklanten')
        count = cur.fetchone()[0]
        
        if count == len(df):
            print(f'✅ Verification successful: {count} records in database')
        else:
            print(f'⚠️  Warning: CSV has {len(df)} but database has {count}')
        
        # Show sample
        cur.execute('SELECT postcode, huisnummer, naam FROM bedrijfsklanten LIMIT 3')
        samples = cur.fetchall()
        print('\n   Sample records:')
        for postcode, huisnr, naam in samples:
            print(f'   - {postcode} {huisnr}: {naam}')
    except Exception as e:
        print(f'❌ Verification failed: {e}')
    
    # Close
    conn.close()
    
    print('\n' + '=' * 50)
    print('🎉 KOAD data imported successfully!')
    print('\nThe bedrijfsklanten table is now in irado_chat database')
    print('Next: Update app configuration to use single database')

if __name__ == '__main__':
    main()

