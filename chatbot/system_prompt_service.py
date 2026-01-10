"""
System Prompt Management Service
Handles loading, saving, and versioning of chatbot system prompts
"""
import psycopg2
import psycopg2.extras
from typing import Dict, List, Optional
import logging
from config import Config

logger = logging.getLogger(__name__)


class SystemPromptService:
    """Service for managing chatbot system prompts"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.connection = None
        self._state_ready = False
        self._session_configured = False

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #
    def _get_connection(self):
        """Get database connection to chat database"""
        if not self.connection or self.connection.closed:
            host = self.config.POSTGRES_HOST
            port = int(self.config.POSTGRES_PORT or 5432)
            database = self.config.POSTGRES_DB
            user = self.config.POSTGRES_USER
            password = self.config.POSTGRES_PASSWORD

            if not password:
                raise ValueError("POSTGRES_PASSWORD is not configured. Set it via environment variable or connection string.")

            logger.info("🔍 SystemPromptService database connection attempt:")
            logger.info(f"   Host: {host}")
            logger.info(f"   Port: {port}")
            logger.info(f"   Database: {database}")
            logger.info(f"   User: {user}")
            logger.info(f"   Password: {'*' * len(password) if password else 'None'}")

            try:
                self.connection = psycopg2.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password,
                    sslmode=self.config.POSTGRES_SSL_MODE or 'require'
                )
                self.connection.autocommit = False
                self._configure_session()
                self._ensure_prompts_table()
                self._ensure_state_table()
                logger.info("✅ SystemPromptService database connection successful!")
            except Exception as e:
                logger.error(f"❌ SystemPromptService database connection failed: {e}")
                raise
        return self.connection

    def _configure_session(self):
        if not self.connection or self._session_configured:
            return
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SET TIME ZONE %s", (self.config.APP_TIMEZONE,))
            self.connection.commit()
        except Exception as e:
            logger.warning(f"Failed to apply timezone setting: {e}")
            self.connection.rollback()
        finally:
            self._session_configured = True

    def _ensure_state_table(self):
        """Ensure helper table for tracking active prompt exists"""
        if self._state_ready or not self.connection:
            return

        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_prompt_state (
                    key TEXT PRIMARY KEY,
                    prompt_id INTEGER REFERENCES system_prompts(id) ON DELETE SET NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                INSERT INTO system_prompt_state (key, prompt_id)
                VALUES ('active_prompt_id', NULL)
                ON CONFLICT (key) DO NOTHING
            """)
            self.connection.commit()
            self._state_ready = True
        except Exception as e:
            self.connection.rollback()
            logger.warning(f"Failed to ensure system_prompt_state table: {e}")
        finally:
            cursor.close()

    def _ensure_prompts_table(self):
        """Ensure system_prompts table exists (needed for empty dev databases)."""
        if not self.connection:
            return
        cursor = self.connection.cursor()
        try:
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
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_system_prompts_active
                ON system_prompts(is_active) WHERE is_active = TRUE
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_system_prompts_version
                ON system_prompts(version)
            """)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            logger.warning(f"Failed to ensure system_prompts table: {e}")
        finally:
            cursor.close()

    def _get_active_prompt_id(self, cursor) -> Optional[int]:
        self._ensure_state_table()
        cursor.execute("""
            SELECT prompt_id
            FROM system_prompt_state
            WHERE key = 'active_prompt_id'
            LIMIT 1
        """)
        row = cursor.fetchone()
        if row is None:
            return None
        if isinstance(row, dict):
            return row.get('prompt_id')
        return row[0] if row[0] is not None else None

    def _set_active_prompt(self, cursor, prompt_id: int):
        self._ensure_state_table()
        current_id = self._get_active_prompt_id(cursor)

        if current_id and current_id != prompt_id:
            cursor.execute("UPDATE system_prompts SET is_active = FALSE WHERE id = %s", (current_id,))

        cursor.execute("UPDATE system_prompts SET is_active = TRUE WHERE id = %s", (prompt_id,))
        cursor.execute("""
            INSERT INTO system_prompt_state (key, prompt_id, updated_at)
            VALUES ('active_prompt_id', %s, NOW())
            ON CONFLICT (key) DO UPDATE
                SET prompt_id = EXCLUDED.prompt_id,
                    updated_at = EXCLUDED.updated_at
        """, (prompt_id,))

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def get_active_prompt(self) -> Optional[str]:
        """
        Get the currently active system prompt content from database
        Returns just the content string, or None if no active prompt found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            active_id = self._get_active_prompt_id(cursor)
            result = None

            if active_id:
                cursor.execute("""
                    SELECT content, version
                    FROM system_prompts
                    WHERE id = %s
                    LIMIT 1
                """, (active_id,))
                result = cursor.fetchone()

            if not result:
                cursor.execute("""
                    SELECT id, content, version
                    FROM system_prompts
                    WHERE is_active = TRUE
                    LIMIT 1
                """)
                result = cursor.fetchone()
                if result:
                    self._set_active_prompt(cursor, result['id'])
                    conn.commit()

            cursor.close()

            if result:
                logger.info(f"Loaded active system prompt version: {result['version']}")
                return result['content']
            else:
                logger.warning("No active system prompt found in database")
                return None

        except Exception as e:
            logger.error(f"Error loading active prompt: {e}")
            return None

    def get_active_prompt_full(self) -> Optional[Dict]:
        """
        Get the currently active system prompt with all metadata
        Returns full prompt object, or None if no active prompt found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            active_id = self._get_active_prompt_id(cursor)
            result = None

            if active_id:
                cursor.execute("""
                    SELECT id, version, content, is_active,
                           created_at, updated_at, created_by, notes
                    FROM system_prompts
                    WHERE id = %s
                    LIMIT 1
                """, (active_id,))
                result = cursor.fetchone()

            if not result:
                cursor.execute("""
                    SELECT id, version, content, is_active,
                           created_at, updated_at, created_by, notes
                    FROM system_prompts
                    WHERE is_active = TRUE
                    LIMIT 1
                """)
                result = cursor.fetchone()
                if result:
                    self._set_active_prompt(cursor, result['id'])
                    conn.commit()

            cursor.close()

            if result:
                logger.info(f"Loaded active system prompt (full) version: {result['version']}")
                return dict(result)
            else:
                logger.warning("No active system prompt found in database")
                return None

        except Exception as e:
            logger.error(f"Error loading active prompt (full): {e} ({type(e).__name__})")
            return None

    def get_all_prompts(self) -> List[Dict]:
        """Get all system prompts with their metadata"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            cursor.execute("""
                SELECT id, version, content, is_active,
                       created_at, updated_at, created_by, notes
                FROM system_prompts
                ORDER BY created_at DESC
            """)

            results = cursor.fetchall()
            cursor.close()

            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Error loading all prompts: {e}")
            return []

    def get_prompt_by_id(self, prompt_id: int) -> Optional[Dict]:
        """Get a specific prompt by ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            cursor.execute("""
                SELECT id, version, content, is_active,
                       created_at, updated_at, created_by, notes
                FROM system_prompts
                WHERE id = %s
            """, (prompt_id,))

            result = cursor.fetchone()
            cursor.close()

            return dict(result) if result else None

        except Exception as e:
            logger.error(f"Error loading prompt {prompt_id}: {e}")
            return None

    def create_prompt(self, version: str, content: str, notes: str = "",
                      created_by: str = "admin", activate: bool = False) -> Optional[int]:
        """
        Create a new system prompt
        Returns the ID of the created prompt, or None on failure
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if activate:
                active_id = self._get_active_prompt_id(cursor)
                if active_id:
                    cursor.execute("UPDATE system_prompts SET is_active = FALSE WHERE id = %s", (active_id,))

            cursor.execute("""
                INSERT INTO system_prompts
                (version, content, is_active, notes, created_by)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (version, content, activate, notes, created_by))

            prompt_id = cursor.fetchone()[0]

            if activate:
                self._set_active_prompt(cursor, prompt_id)

            conn.commit()
            cursor.close()

            logger.info(f"Created new prompt version {version} (ID: {prompt_id}, Active: {activate})")
            return prompt_id

        except Exception as e:
            logger.error(f"Error creating prompt: {e}")
            if conn:
                conn.rollback()
            return None

    def update_prompt(self, prompt_id: int, content: str,
                      version: str = None, notes: str = None) -> bool:
        """Update an existing prompt's content"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            update_fields = ["content = %s"]
            params = [content]

            if version is not None:
                update_fields.append("version = %s")
                params.append(version)

            if notes is not None:
                update_fields.append("notes = %s")
                params.append(notes)

            params.append(prompt_id)

            query = f"""
                UPDATE system_prompts
                SET {', '.join(update_fields)}
                WHERE id = %s
            """

            cursor.execute(query, params)
            conn.commit()
            cursor.close()

            logger.info(f"Updated prompt ID {prompt_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating prompt: {e}")
            if conn:
                conn.rollback()
            return False

    def activate_prompt(self, prompt_id: int) -> bool:
        """Activate a specific prompt (deactivates previous active prompt)"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id
                FROM system_prompts
                WHERE id = %s
            """, (prompt_id,))

            if cursor.fetchone() is None:
                raise Exception(f"Prompt ID {prompt_id} not found")

            self._set_active_prompt(cursor, prompt_id)

            conn.commit()
            cursor.close()

            logger.info(f"Activated prompt ID {prompt_id}")
            return True

        except Exception as e:
            logger.error(f"Error activating prompt: {e}")
            if conn:
                conn.rollback()
            return False

    def delete_prompt(self, prompt_id: int) -> bool:
        """Delete a prompt (cannot delete active prompt)"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT is_active FROM system_prompts WHERE id = %s
            """, (prompt_id,))

            result = cursor.fetchone()
            if not result:
                raise Exception(f"Prompt ID {prompt_id} not found")

            if result[0]:
                raise Exception("Cannot delete active prompt")

            cursor.execute("""
                DELETE FROM system_prompts WHERE id = %s
            """, (prompt_id,))

            conn.commit()
            cursor.close()

            logger.info(f"Deleted prompt ID {prompt_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting prompt: {e}")
            if conn:
                conn.rollback()
            return False

    def get_prompt_with_fallback(self) -> str:
        """
        Get active prompt from database with fallback to file
        This is the main method used by the chatbot
        """
        db_prompt = self.get_active_prompt()
        if db_prompt:
            return db_prompt

        try:
            prompt_file = "prompts/system_prompt.txt"
            with open(prompt_file, 'r', encoding='utf-8') as f:
                file_prompt = f.read().strip()
                logger.info("Loaded system prompt from file (database fallback)")
                return file_prompt
        except Exception as e:
            logger.error(f"Error loading prompt from file: {e}")

        logger.warning("Using hardcoded fallback prompt")
        return "Je bent de virtuele assistent van Irado. Help klanten met vragen over afval en recycling."

    def close(self):
        """Close database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()
