import sqlite3
import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from backend.app.config import settings

class MemoryRepository:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Parse from settings or default to root db
            db_path = settings.DATABASE_URL.replace("sqlite:///", "").lstrip("./")
        self.db_path = Path(db_path).resolve()
        self._init_db()

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Session messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    metadata TEXT
                )
            """)
            # Persistent memories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS long_term_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    value TEXT NOT NULL,
                    category TEXT,
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()

    def save_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO session_messages (session_id, role, content, timestamp, metadata) VALUES (?, ?, ?, ?, ?)",
                (session_id, role, content, time.time(), json.dumps(metadata or {}))
            )
            conn.commit()

    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM session_messages WHERE session_id = ? ORDER BY id ASC LIMIT ?",
                (session_id, limit)
            )
            rows = cursor.fetchall()
            return [{"role": r[0], "content": r[1]} for r in rows]

    def store_memory(self, key: str, value: str, category: str = "general"):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO long_term_memories (key, value, category, timestamp) VALUES (?, ?, ?, ?)",
                (key, value, category, time.time())
            )
            conn.commit()

    def search_memory(self, query: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT key, value, category FROM long_term_memories WHERE key LIKE ? OR value LIKE ?",
                (f"%{query}%", f"%{query}%")
            )
            rows = cursor.fetchall()
            return [{"key": r[0], "value": r[1], "category": r[2]} for r in rows]

    def get_relevant_memories(self, query: str, limit: int = 5) -> List[str]:
        results = self.search_memory(query)
        return [f"{r['key']}: {r['value']}" for r in results[:limit]]

memory_repository = MemoryRepository()
