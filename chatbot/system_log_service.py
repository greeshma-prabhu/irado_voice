"""
System Log Service (DB-first)
Stores structured system events in PostgreSQL so the dashboard can query them
without calling the chatbot.
"""

from __future__ import annotations

import json
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

import psycopg2
import psycopg2.extras

from config import Config


class SystemLogService:
    """DB-backed structured logging + querying for system-level events."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.connection = None
        self._session_configured = False
        self._tables_ready = False
        self.timezone = ZoneInfo(self.config.APP_TIMEZONE)

    def _get_connection(self):
        if not self.connection or self.connection.closed:
            self.connection = psycopg2.connect(
                host=self.config.POSTGRES_HOST,
                port=int(self.config.POSTGRES_PORT or 5432),
                database=self.config.POSTGRES_DB,
                user=self.config.POSTGRES_USER,
                password=self.config.POSTGRES_PASSWORD,
                sslmode=self.config.POSTGRES_SSL_MODE or "require",
            )
            self.connection.autocommit = False
            self._configure_session()
        return self.connection

    def _configure_session(self):
        if not self.connection or self._session_configured:
            return
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SET TIME ZONE %s", (self.config.APP_TIMEZONE,))
            self.connection.commit()
        except Exception:
            self.connection.rollback()
        finally:
            self._session_configured = True

    def ensure_tables(self) -> bool:
        """Create system log tables and indexes if they don't exist."""
        if self._tables_ready:
            return True
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS system_log_events (
                    id BIGSERIAL PRIMARY KEY,
                    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    severity VARCHAR(10) NOT NULL,
                    event_name TEXT NOT NULL,
                    component TEXT NOT NULL,
                    message TEXT,
                    error_type TEXT,
                    http_status INTEGER,
                    request_id TEXT,
                    session_id TEXT,
                    conversation_id TEXT,
                    stacktrace TEXT,
                    meta JSONB,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )

            # Indexes for filtering and time-range queries
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_system_log_events_ts ON system_log_events(ts DESC)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_system_log_events_severity ON system_log_events(severity)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_system_log_events_component ON system_log_events(component)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_system_log_events_event_name ON system_log_events(event_name)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_system_log_events_request_id ON system_log_events(request_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_system_log_events_session_id ON system_log_events(session_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_system_log_events_error_type ON system_log_events(error_type)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_system_log_events_meta_gin ON system_log_events USING GIN (meta)"
            )

            conn.commit()
            cursor.close()
            self._tables_ready = True
            return True
        except Exception:
            try:
                if self.connection:
                    self.connection.rollback()
            except Exception:
                pass
            return False

    def log_event(
        self,
        *,
        severity: str,
        event_name: str,
        component: str,
        message: str,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        error_type: Optional[str] = None,
        http_status: Optional[int] = None,
        stacktrace_text: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Write a structured system event to DB.
        This must never crash the app; failures are swallowed.
        """
        try:
            if not self.ensure_tables():
                return
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO system_log_events
                  (severity, event_name, component, message, error_type, http_status,
                   request_id, session_id, conversation_id, stacktrace, meta)
                VALUES
                  (%s, %s, %s, %s, %s, %s,
                   %s, %s, %s, %s, %s)
                """,
                (
                    (severity or "info").lower(),
                    event_name,
                    component,
                    message,
                    error_type,
                    http_status,
                    request_id,
                    session_id,
                    conversation_id,
                    stacktrace_text,
                    json.dumps(meta) if meta is not None else None,
                ),
            )
            conn.commit()
            cursor.close()
        except Exception:
            try:
                if self.connection:
                    self.connection.rollback()
            except Exception:
                pass

    def log_exception(
        self,
        *,
        event_name: str,
        component: str,
        message: str,
        exc: Exception,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        error_type: Optional[str] = None,
        http_status: Optional[int] = None,
        meta: Optional[Dict[str, Any]] = None,
        severity: str = "error",
    ) -> None:
        self.log_event(
            severity=severity,
            event_name=event_name,
            component=component,
            message=message,
            request_id=request_id,
            session_id=session_id,
            conversation_id=conversation_id,
            error_type=error_type or type(exc).__name__,
            http_status=http_status,
            stacktrace_text="".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
            meta=meta,
        )

    def query_events(
        self,
        *,
        ts_from: Optional[datetime] = None,
        ts_to: Optional[datetime] = None,
        q: Optional[str] = None,
        severity: Optional[str] = None,
        component: Optional[str] = None,
        event_name: Optional[str] = None,
        error_type: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 200,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Query system events with basic search and filters. Returns (rows, total_count)."""
        if limit > 500:
            limit = 500
        if limit < 1:
            limit = 1
        if offset < 0:
            offset = 0

        if not self.ensure_tables():
            return [], 0

        clauses = ["1=1"]
        params: List[Any] = []

        if ts_from:
            clauses.append("ts >= %s")
            params.append(ts_from)
        if ts_to:
            clauses.append("ts <= %s")
            params.append(ts_to)

        if severity:
            clauses.append("severity = %s")
            params.append(severity.lower())
        if component:
            clauses.append("component = %s")
            params.append(component)
        if event_name:
            clauses.append("event_name = %s")
            params.append(event_name)
        if error_type:
            clauses.append("error_type = %s")
            params.append(error_type)
        if request_id:
            clauses.append("request_id = %s")
            params.append(request_id)
        if session_id:
            clauses.append("session_id = %s")
            params.append(session_id)

        if q:
            # Basic keyword search (works without extensions). Later we can upgrade to FTS.
            clauses.append("(message ILIKE %s OR stacktrace ILIKE %s OR meta::text ILIKE %s)")
            like = f"%{q}%"
            params.extend([like, like, like])

        where_sql = " AND ".join(clauses)

        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(f"SELECT COUNT(*) AS cnt FROM system_log_events WHERE {where_sql}", params)
        total = int(cursor.fetchone()["cnt"])

        cursor.execute(
            f"""
            SELECT id, ts, severity, event_name, component, message, error_type, http_status,
                   request_id, session_id, conversation_id, stacktrace, meta
            FROM system_log_events
            WHERE {where_sql}
            ORDER BY ts DESC
            LIMIT %s OFFSET %s
            """,
            params + [limit, offset],
        )
        rows = cursor.fetchall()
        cursor.close()

        # Normalize timestamps for the UI
        result: List[Dict[str, Any]] = []
        for row in rows:
            r = dict(row)
            ts = r.get("ts")
            if ts:
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=self.timezone)
                else:
                    ts = ts.astimezone(self.timezone)
                r["ts"] = ts.isoformat()
            result.append(r)
        return result, total


