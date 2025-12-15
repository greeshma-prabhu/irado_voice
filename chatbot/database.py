"""
Database models and connection handling for the Irado Chatbot
"""
import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import List, Dict, Optional
from config import Config

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.config = Config()
        self.connection = None
        self._session_configured = False
    
    def get_connection(self):
        """Get database connection"""
        try:
            if not self.connection or self.connection.closed:
                print(f"🔗 Connecting to database: {self.config.POSTGRES_HOST}:{self.config.POSTGRES_PORT}/{self.config.POSTGRES_DB}")
                self.connection = psycopg2.connect(
                    host=self.config.POSTGRES_HOST,
                    port=int(self.config.POSTGRES_PORT or 5432),
                    database=self.config.POSTGRES_DB,
                    user=self.config.POSTGRES_USER,
                    password=self.config.POSTGRES_PASSWORD,
                    sslmode=self.config.POSTGRES_SSL_MODE
                )
                self._configure_session()
                print("✅ Database connection successful")
            return self.connection
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Create chat_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create chat_messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    message_type VARCHAR(20) NOT NULL, -- 'user' or 'bot'
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB
                )
            """)
            
            # Create chat_memory table for AI context
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_memory (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    memory_type VARCHAR(50) NOT NULL, -- 'conversation', 'user_info', 'request_data'
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_memory_session_id ON chat_memory(session_id)")
            
            conn.commit()
            print("Database tables initialized successfully")
            
        except Exception as e:
            conn.rollback()
            print(f"Error initializing database: {e}")
            raise
        finally:
            cursor.close()

    def _configure_session(self):
        """Apply per-session settings (timezone, etc.)"""
        if not self.connection or self._session_configured:
            return
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SET TIME ZONE %s", (self.config.APP_TIMEZONE,))
            self.connection.commit()
        except Exception as e:
            print(f"Warning: failed to set database session timezone: {e}")
            self.connection.rollback()
        finally:
            self._session_configured = True
    
    def save_message(self, session_id: str, message_type: str, content: str, metadata: Dict = None):
        """Save a chat message to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO chat_messages (session_id, message_type, content, metadata)
                VALUES (%s, %s, %s, %s)
            """, (session_id, message_type, content, metadata))
            
            # Update session last activity
            cursor.execute("""
                UPDATE chat_sessions 
                SET last_activity = CURRENT_TIMESTAMP 
                WHERE session_id = %s
            """, (session_id,))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"Error saving message: {e}")
            raise
        finally:
            cursor.close()
    
    def get_chat_history(self, session_id: str, limit: int = 20) -> List[Dict]:
        """Get chat history for a session"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT message_type, content, timestamp, metadata
                FROM chat_messages 
                WHERE session_id = %s 
                ORDER BY timestamp DESC 
                LIMIT %s
            """, (session_id, limit))
            
            messages = cursor.fetchall()
            return [dict(msg) for msg in reversed(messages)]  # Reverse to get chronological order
            
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []
        finally:
            cursor.close()
    
    def create_or_update_session(self, session_id: str):
        """Create or update a chat session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO chat_sessions (session_id, created_at, last_activity)
                VALUES (%s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (session_id) 
                DO UPDATE SET last_activity = CURRENT_TIMESTAMP
            """, (session_id,))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"Error creating/updating session: {e}")
            raise
        finally:
            cursor.close()
    
    def save_memory(self, session_id: str, memory_type: str, content: str):
        """Save AI memory/context"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO chat_memory (session_id, memory_type, content, created_at, updated_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (session_id, memory_type) 
                DO UPDATE SET content = %s, updated_at = CURRENT_TIMESTAMP
            """, (session_id, memory_type, content, content))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"Error saving memory: {e}")
            raise
        finally:
            cursor.close()
    
    def get_memory(self, session_id: str, memory_type: str = None) -> List[Dict]:
        """Get AI memory/context for a session"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            if memory_type:
                cursor.execute("""
                    SELECT memory_type, content, created_at, updated_at
                    FROM chat_memory 
                    WHERE session_id = %s AND memory_type = %s
                    ORDER BY updated_at DESC
                """, (session_id, memory_type))
            else:
                cursor.execute("""
                    SELECT memory_type, content, created_at, updated_at
                    FROM chat_memory 
                    WHERE session_id = %s
                    ORDER BY updated_at DESC
                """, (session_id,))
            
            memories = cursor.fetchall()
            return [dict(mem) for mem in memories]
            
        except Exception as e:
            print(f"Error getting memory: {e}")
            return []
        finally:
            cursor.close()

