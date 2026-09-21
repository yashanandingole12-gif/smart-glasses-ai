"""
EVA Event Repository & Activity Timeline Service
Provides unified persistent operational logging, session tracking,
active work duration intelligence, and real-time broadcasting for Web and Android.
"""

import time
import uuid
import json
import sqlite3
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from backend.app.config import settings, PROJECT_ROOT

logger = logging.getLogger("eva.services.event_repository")

class EventRepository:
    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = db_path
        elif settings.DATABASE_URL.startswith("sqlite:///"):
            self.db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        else:
            self.db_path = "./smart_glasses.db"

        self._mem_conn = sqlite3.connect(":memory:", check_same_thread=False) if self.db_path == ":memory:" else None
        if self._mem_conn:
            self._mem_conn.row_factory = sqlite3.Row

        self._active_session_id: Optional[str] = None
        self._session_start_time: Optional[float] = None
        self._last_active_time: Optional[float] = None

        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if self._mem_conn is not None:
            return self._mem_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS eva_events (
                    id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    timestamp_iso TEXT NOT NULL,
                    session_id TEXT,
                    user_id TEXT DEFAULT 'default_user',
                    type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    entity_type TEXT,
                    entity_id TEXT,
                    status TEXT DEFAULT 'SUCCESS',
                    duration_ms INTEGER DEFAULT 0,
                    metadata_json TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS eva_sessions (
                    session_id TEXT PRIMARY KEY,
                    start_time REAL NOT NULL,
                    start_time_iso TEXT NOT NULL,
                    end_time REAL,
                    end_time_iso TEXT,
                    active_duration_ms INTEGER DEFAULT 0,
                    activity_count INTEGER DEFAULT 0,
                    summary TEXT
                )
            """)
            conn.commit()

    def start_session(self, session_id: Optional[str] = None) -> str:
        s_id = session_id or f"session_{uuid.uuid4().hex[:10]}"
        now = time.time()
        now_iso = datetime.now(timezone.utc).isoformat()
        self._active_session_id = s_id
        self._session_start_time = now
        self._last_active_time = now

        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO eva_sessions (
                    session_id, start_time, start_time_iso, active_duration_ms, activity_count, summary
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (s_id, now, now_iso, 0, 0, "Active EVA Session"))
            conn.commit()

        self.record_event(
            event_type="SESSION_STARTED",
            source="system",
            title="EVA Session Started",
            description="Ambient living environment awakened",
            session_id=s_id
        )
        return s_id

    def get_active_session_id(self) -> Optional[str]:
        return self._active_session_id

    def end_session(self, session_id: Optional[str] = None, summary: Optional[str] = None) -> Dict[str, Any]:
        s_id = session_id or self._active_session_id
        if not s_id:
            return {"status": "NO_ACTIVE_SESSION"}

        now = time.time()
        now_iso = datetime.now(timezone.utc).isoformat()
        session_summary = summary or "Session concluded."

        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM eva_sessions WHERE session_id = ?", (s_id,)).fetchone()
            if row:
                start = row["start_time"]
                total_duration_ms = int((now - start) * 1000)
                conn.execute("""
                    UPDATE eva_sessions
                    SET end_time = ?, end_time_iso = ?, active_duration_ms = ?, summary = ?
                    WHERE session_id = ?
                """, (now, now_iso, total_duration_ms, session_summary, s_id))
                conn.commit()

        self.record_event(
            event_type="SESSION_ENDED",
            source="system",
            title="EVA Session Ended",
            description=session_summary,
            session_id=s_id
        )
        self._active_session_id = None
        return {"status": "SESSION_ENDED", "session_id": s_id, "summary": session_summary}


    def record_event(
        self,
        event_type: str,
        title: Optional[str] = None,
        source: str = "eva",
        description: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        status: str = "SUCCESS",
        session_id: Optional[str] = None,
        duration_ms: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        now = time.time()
        now_iso = datetime.now(timezone.utc).isoformat()
        s_id = session_id or self._active_session_id or "session_default"
        evt_title = title or event_type.replace("_", " ").title()
        meta_dict = metadata or {}
        if kwargs:
            meta_dict.update(kwargs)
        meta_json = json.dumps(meta_dict)

        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO eva_events (
                    id, timestamp, timestamp_iso, session_id, user_id,
                    type, source, title, description, entity_type,
                    entity_id, status, duration_ms, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id, now, now_iso, s_id, "default_user",
                event_type, source, evt_title, description or "", entity_type,
                entity_id, status, duration_ms, meta_json
            ))
            # Update session activity count
            conn.execute("""
                UPDATE eva_sessions
                SET activity_count = activity_count + 1
                WHERE session_id = ?
            """, (s_id,))
            conn.commit()

        event_payload = {
            "id": event_id,
            "timestamp": now_iso,
            "session_id": s_id,
            "type": event_type,
            "source": source,
            "title": evt_title,
            "description": description,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "status": status,
            "duration_ms": duration_ms,
            "metadata": meta_dict
        }
        return event_payload

    def get_timeline(
        self,
        date_filter: str = "all",
        category: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        event_type: Optional[str] = None,
        source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM eva_events WHERE 1=1"
        params: List[Any] = []

        now = time.time()
        if date_filter == "today":
            day_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
            query += " AND timestamp >= ?"
            params.append(day_start)
        elif date_filter == "yesterday":
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
            yesterday_start = today_start - 86400
            query += " AND timestamp >= ? AND timestamp < ?"
            params.extend([yesterday_start, today_start])
        elif date_filter == "week":
            week_start = now - (7 * 86400)
            query += " AND timestamp >= ?"
            params.append(week_start)

        if category and category.lower() != "all":
            query += " AND (type LIKE ? OR source LIKE ?)"
            params.extend([f"%{category}%", f"%{category}%"])

        if event_type:
            query += " AND type = ?"
            params.append(event_type)

        if source:
            query += " AND source = ?"
            params.append(source)

        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._get_conn() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()

        events = []
        for r in rows:
            events.append({
                "id": r["id"],
                "timestamp": r["timestamp_iso"],
                "session_id": r["session_id"],
                "type": r["type"],
                "source": r["source"],
                "title": r["title"],
                "description": r["description"],
                "entity_type": r["entity_type"],
                "entity_id": r["entity_id"],
                "status": r["status"],
                "duration_ms": r["duration_ms"],
                "metadata": json.loads(r["metadata_json"] or "{}")
            })
        return events


    def get_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM eva_sessions ORDER BY start_time DESC LIMIT ?",
                (limit,)
            ).fetchall()

        sessions = []
        for r in rows:
            duration_minutes = round((r["active_duration_ms"] or 0) / 60000, 1)
            sessions.append({
                "session_id": r["session_id"],
                "start_time": r["start_time_iso"],
                "end_time": r["end_time_iso"],
                "duration_minutes": duration_minutes,
                "activity_count": r["activity_count"],
                "summary": r["summary"]
            })
        return sessions

event_repository = EventRepository()
