#!/usr/bin/env python3
"""
Migrate KOAD data from bedrijfsklanten-db to chat-db
This script connects to both databases and copies the bedrijfsklanten table
"""
import psycopg2
import os
import sys

# Database credentials from environment
BEDRIJFSKLANTEN_DB = {
    'host': os.getenv('BEDRIJFSKLANTEN_DB_HOST', 'irado-bedrijfsklanten-db.postgres.database.azure.com'),
    'port': os.getenv('BEDRIJFSKLANTEN_DB_PORT', '5432'),
    'database': os.getenv('BEDRIJFSKLANTEN_DB_NAME', 'irado_bedrijfsklanten'),
    'user': os.getenv('BEDRIJFSKLANTEN_DB_USER', 'irado_admin'),
    'password': os.getenv('BEDRIJFSKLANTEN_DB_PASSWORD', 'lqBp6OF31+wCNXzyTMvasFrspdtL+IWPGVtooy2zjS4=')
}

CHAT_DB = {
    'host': os.getenv('POSTGRES_HOST', 'irado-chat-db.postgres.database.azure.com'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'irado_chat'),
    'user': os.getenv('POSTGRES_USER', 'irado_admin'),
    'password': os.getenv('POSTGRES_PASSWORD', '')  # Will get from Azure
}

def get_chat_db_password():
    """Get chat database password from Azure"""
    import subprocess
    try:
        result = subprocess.run([
            'az', 'webapp', 'config', 'appsettings', 'list',
            '--name', 'irado-chatbot-app',
            '--resource-group', 'irado-rg',
            '--query', "[?name=='POSTGRES_PASSWORD'].value",
            '-o', 'tsv'
        ], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except:
        return None

def main():
    print("🔄 KOAD Database Migration")
    print("=" * 50)
    
    # Get chat DB password
    print("\n📋 Step 1: Getting credentials...")
    chat_password = get_chat_db_password()
    if not chat_password:
        print("❌ Could not get chat database password")
        sys.exit(1)
    CHAT_DB['password'] = chat_password
    print("✅ Credentials obtained")
    
    # Connect to source database
    print("\n📋 Step 2: Connecting to source database (bedrijfsklanten-db)...")
    try:
        source_conn = psycopg2.connect(**BEDRIJFSKLANTEN_DB, sslmode='require')
        source_cur = source_conn.cursor()
        print("✅ Connected to source database")
    except Exception as e:
        print(f"❌ Failed to connect to source database: {e}")
        sys.exit(1)
    
    # Connect to target database
    print("\n📋 Step 3: Connecting to target database (chat-db)...")
    try:
        target_conn = psycopg2.connect(**CHAT_DB, sslmode='require')
        target_cur = target_conn.cursor()
        print("✅ Connected to target database")
    except Exception as e:
        print(f"❌ Failed to connect to target database: {e}")
        source_conn.close()
        sys.exit(1)
    
    # Get table structure
    print("\n📋 Step 4: Reading table structure...")
    try:
        source_cur.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'bedrijfsklanten'
            ORDER BY ordinal_position
        """)
        columns = source_cur.fetchall()
        print(f"✅ Found {len(columns)} columns")
        for col in columns:
            print(f"   - {col[0]}: {col[1]}")
    except Exception as e:
        print(f"❌ Failed to read structure: {e}")
        source_conn.close()
        target_conn.close()
        sys.exit(1)
    
    # Count records
    print("\n📋 Step 5: Counting records...")
    try:
        source_cur.execute("SELECT COUNT(*) FROM bedrijfsklanten")
        count = source_cur.fetchone()[0]
        print(f"✅ Found {count} records to migrate")
    except Exception as e:
        print(f"❌ Failed to count records: {e}")
        source_conn.close()
        target_conn.close()
        sys.exit(1)
    
    # Create table in target if not exists
    print("\n📋 Step 6: Creating table in target database...")
    try:
        # Get CREATE TABLE statement from source
        source_cur.execute("""
            SELECT 
                'CREATE TABLE IF NOT EXISTS bedrijfsklanten (' ||
                string_agg(
                    column_name || ' ' || 
                    CASE 
                        WHEN data_type = 'character varying' THEN 'VARCHAR(' || character_maximum_length || ')'
                        ELSE data_type 
                    END,
                    ', '
                ) || ');'
            FROM information_schema.columns
            WHERE table_name = 'bedrijfsklanten'
        """)
        create_stmt = source_cur.fetchone()[0]
        
        # Execute in target
        target_cur.execute(create_stmt)
        target_conn.commit()
        print("✅ Table created/verified in target")
    except Exception as e:
        print(f"❌ Failed to create table: {e}")
        source_conn.close()
        target_conn.close()
        sys.exit(1)
    
    # Copy data
    print("\n📋 Step 7: Copying data...")
    try:
        # Clear existing data
        target_cur.execute("TRUNCATE TABLE bedrijfsklanten")
        print("   - Cleared existing data")
        
        # Get all data
        source_cur.execute("SELECT * FROM bedrijfsklanten")
        rows = source_cur.fetchall()
        
        # Get column names
        col_names = [desc[0] for desc in source_cur.description]
        
        # Insert data
        placeholders = ','.join(['%s'] * len(col_names))
        insert_query = f"INSERT INTO bedrijfsklanten ({','.join(col_names)}) VALUES ({placeholders})"
        
        for i, row in enumerate(rows, 1):
            target_cur.execute(insert_query, row)
            if i % 100 == 0:
                print(f"   - Inserted {i}/{count} records...")
        
        target_conn.commit()
        print(f"✅ Successfully copied {count} records")
    except Exception as e:
        print(f"❌ Failed to copy data: {e}")
        target_conn.rollback()
        source_conn.close()
        target_conn.close()
        sys.exit(1)
    
    # Verify
    print("\n📋 Step 8: Verifying migration...")
    try:
        target_cur.execute("SELECT COUNT(*) FROM bedrijfsklanten")
        target_count = target_cur.fetchone()[0]
        
        if target_count == count:
            print(f"✅ Verification successful: {target_count} records in target")
        else:
            print(f"⚠️  Warning: Source has {count} but target has {target_count}")
    except Exception as e:
        print(f"❌ Verification failed: {e}")
    
    # Close connections
    source_conn.close()
    target_conn.close()
    
    print("\n" + "=" * 50)
    print("🎉 Migration completed successfully!")
    print("\nNext steps:")
    print("1. Update app configuration to use single database")
    print("2. Test chatbot functionality")
    print("3. Delete old bedrijfsklanten-db database")

if __name__ == '__main__':
    main()

