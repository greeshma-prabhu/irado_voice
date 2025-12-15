#!/usr/bin/env python3
"""
Setup System Prompt Schema and insert initial prompt
"""
import psycopg2
import os
import sys

# Add chatbot directory to path
sys.path.append('/opt/irado-azure/chatbot')
from config import Config

def setup_system_prompt_schema():
    """Create system_prompts table and insert initial prompt"""
    
    # Get database connection from chatbot config
    config = Config()
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT,
            database=config.POSTGRES_DB,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD,
            sslmode='require'
        )
        
        cursor = conn.cursor()
        
        print("🔧 Creating system_prompts table...")
        
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_prompts (
                id SERIAL PRIMARY KEY,
                version VARCHAR(50) NOT NULL UNIQUE,
                content TEXT NOT NULL,
                is_active BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR(255) DEFAULT 'admin',
                notes TEXT
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_system_prompts_only_one_active 
            ON system_prompts(is_active) WHERE is_active = TRUE
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_system_prompts_version 
            ON system_prompts(version)
        """)
        
        # Check if table has any data
        cursor.execute("SELECT COUNT(*) FROM system_prompts")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("📝 Inserting initial system prompt...")
            
            # Read the system prompt from file
            prompt_file = '/opt/irado-azure/chatbot/prompts/system_prompt.txt'
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompt_content = f.read().strip()
            except FileNotFoundError:
                print("❌ System prompt file not found, using fallback")
                prompt_content = "Je bent de virtuele assistent van Irado. Help klanten met vragen over afval en recycling."
            
            # Insert initial prompt
            cursor.execute("""
                INSERT INTO system_prompts (version, content, is_active, notes) 
                VALUES (%s, %s, %s, %s)
            """, (
                'v1.0.0',
                prompt_content,
                True,
                'Initial system prompt from chatbot file'
            ))
            
            print("✅ System prompt inserted successfully")
        else:
            print(f"ℹ️  System prompts table already has {count} entries")
        
        # Create trigger for updated_at
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_system_prompt_timestamp()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql
        """)
        
        cursor.execute("""
            DROP TRIGGER IF EXISTS system_prompts_update_timestamp ON system_prompts
        """)
        
        cursor.execute("""
            CREATE TRIGGER system_prompts_update_timestamp
                BEFORE UPDATE ON system_prompts
                FOR EACH ROW
                EXECUTE FUNCTION update_system_prompt_timestamp()
        """)
        
        conn.commit()
        print("✅ System prompt schema setup completed successfully")
        
    except Exception as e:
        print(f"❌ Error setting up system prompt schema: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    print("🚀 Setting up System Prompt Schema...")
    success = setup_system_prompt_schema()
    if success:
        print("🎉 Setup completed successfully!")
    else:
        print("💥 Setup failed!")
        sys.exit(1)













