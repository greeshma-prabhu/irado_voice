"""
Dashboard Logging Service
Comprehensive logging for all dashboard operations
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import psycopg2
import psycopg2.extras
import os
import sys
from zoneinfo import ZoneInfo

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class DashboardLoggingService:
    """Service for logging dashboard operations to database"""
    
    def __init__(self):
        self.config = Config()
        self.connection = None
        self._session_configured = False
        self.timezone = ZoneInfo(self.config.APP_TIMEZONE)
    
    def _get_connection(self):
        """Get database connection"""
        if not self.connection or self.connection.closed:
            try:
                self.connection = psycopg2.connect(
                    host=self.config.POSTGRES_HOST,
                    port=int(self.config.POSTGRES_PORT or 5432),
                    database=self.config.POSTGRES_DB,
                    user=self.config.POSTGRES_USER,
                    password=self.config.POSTGRES_PASSWORD,
                    sslmode='require'
                )
                self._configure_session()
            except Exception as e:
                print(f"❌ Dashboard logging DB connection failed: {e}")
                return None
        return self.connection

    def _configure_session(self):
        if not self.connection or self._session_configured:
            return
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SET TIME ZONE %s", (self.config.APP_TIMEZONE,))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(f"⚠️  Failed to set dashboard logging timezone: {e}")
        finally:
            self._session_configured = True
    
    def setup_tables(self):
        """Create dashboard logs table if not exists"""
        try:
            conn = self._get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            # Create dashboard_logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    log_type VARCHAR(50),
                    action VARCHAR(100),
                    message TEXT,
                    details JSONB,
                    level VARCHAR(20) DEFAULT 'info',
                    user_ip VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_dashboard_logs_timestamp 
                ON dashboard_logs(timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_dashboard_logs_type 
                ON dashboard_logs(log_type)
            """)
            
            conn.commit()
            cursor.close()
            print("✅ Dashboard logs tables ready")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up dashboard logs tables: {e}")
            return False
    
    def log(self, log_type: str, action: str, message: str, 
            details: Optional[Dict[str, Any]] = None, 
            level: str = 'info',
            user_ip: Optional[str] = None):
        """
        Log a dashboard event
        
        Args:
            log_type: Type of log (CSV_UPLOAD, API_CALL, ERROR, etc.)
            action: Action being performed
            message: Human-readable message
            details: Additional details as dict
            level: Log level (info, warning, error)
            user_ip: Client IP address
        """
        try:
            conn = self._get_connection()
            if not conn:
                # Fallback to console logging
                print(f"[{level.upper()}] [{log_type}] {action}: {message}")
                if details:
                    print(f"   Details: {json.dumps(details, indent=2)}")
                return
            
            cursor = conn.cursor()
            
            # Convert details to JSON
            details_json = json.dumps(details) if details else None
            
            cursor.execute("""
                INSERT INTO dashboard_logs 
                (log_type, action, message, details, level, user_ip)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (log_type, action, message, details_json, level, user_ip))
            
            conn.commit()
            cursor.close()
            
            # Also print to console
            emoji = {'info': '📋', 'warning': '⚠️', 'error': '❌'}.get(level, '📝')
            print(f"{emoji} [{log_type}] {action}: {message}")
            if details:
                print(f"   {json.dumps(details)}")
                
        except Exception as e:
            print(f"❌ Logging error: {e}")
            # Always print to console as fallback
            print(f"[{level.upper()}] [{log_type}] {action}: {message}")
    
    def get_recent_logs(self, limit: int = 100, log_type: Optional[str] = None) -> List[Dict]:
        """Get recent logs from database"""
        try:
            conn = self._get_connection()
            if not conn:
                return []
            
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            if log_type:
                cursor.execute("""
                    SELECT id, timestamp, log_type, action, message, details, level, user_ip
                    FROM dashboard_logs
                    WHERE log_type = %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (log_type, limit))
            else:
                cursor.execute("""
                    SELECT id, timestamp, log_type, action, message, details, level, user_ip
                    FROM dashboard_logs
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (limit,))
            
            logs = cursor.fetchall()
            cursor.close()
            
            # Convert to list of dicts and format timestamps
            result = []
            for log in logs:
                log_dict = dict(log)
                ts = log_dict.get('timestamp')
                if ts:
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=self.timezone)
                    else:
                        ts = ts.astimezone(self.timezone)
                    log_dict['timestamp'] = ts.isoformat()
                created = log_dict.get('created_at')
                if created:
                    if created.tzinfo is None:
                        created = created.replace(tzinfo=self.timezone)
                    else:
                        created = created.astimezone(self.timezone)
                    log_dict['created_at'] = created.isoformat()
                result.append(log_dict)
            
            return result
            
        except Exception as e:
            print(f"❌ Error getting logs: {e}")
            return []
    
    def clear_old_logs(self, days: int = 30):
        """Clear logs older than specified days"""
        try:
            conn = self._get_connection()
            if not conn:
                return 0
            
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM dashboard_logs
                WHERE timestamp < NOW() - INTERVAL '%s days'
            """, (days,))
            
            deleted = cursor.rowcount
            conn.commit()
            cursor.close()
            
            print(f"🗑️ Cleared {deleted} old dashboard logs")
            return deleted
            
        except Exception as e:
            print(f"❌ Error clearing old logs: {e}")
            return 0

# Global logger instance
_logger = None

def get_logger() -> DashboardLoggingService:
    """Get global logger instance"""
    global _logger
    if _logger is None:
        _logger = DashboardLoggingService()
        _logger.setup_tables()
    return _logger

# Convenience functions
def log_info(log_type: str, action: str, message: str, details: Optional[Dict] = None, user_ip: Optional[str] = None):
    """Log info message"""
    get_logger().log(log_type, action, message, details, 'info', user_ip)

def log_warning(log_type: str, action: str, message: str, details: Optional[Dict] = None, user_ip: Optional[str] = None):
    """Log warning message"""
    get_logger().log(log_type, action, message, details, 'warning', user_ip)

def log_error(log_type: str, action: str, message: str, details: Optional[Dict] = None, user_ip: Optional[str] = None):
    """Log error message"""
    get_logger().log(log_type, action, message, details, 'error', user_ip)
