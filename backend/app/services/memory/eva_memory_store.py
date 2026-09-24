"""
EVA Memory Store: Offline-First Persistent Knowledge Engine with SQLite + FTS5.
Implements the Book of Yash personal database, 15 memory categories, epistemic confidence,
sensitivity gating (S0-S4), temporal evolution, and graph relationships.
"""
import sqlite3
import json
import time
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from backend.app.config import settings

# 15 Memory Categories
MEMORY_CATEGORIES = {
    "CORE_IDENTITY",
    "PERSONAL_FACT",
    "PREFERENCE",
    "PERSONALITY_PATTERN",
    "LIFE_EVENT",
    "RELATIONSHIP",
    "EMOTIONAL_CONTEXT",
    "ASPIRATION",
    "ACHIEVEMENT",
    "FAILURE",
    "PROJECT",
    "TECHNICAL_KNOWLEDGE",
    "CONVERSATION_SUMMARY",
    "USER_INSTRUCTION",
    "TEMPORARY_CONTEXT",
    # Aliases
    "identity",
    "education",
    "career",
    "interests",
    "personality",
    "emotional",
    "habits",
    "health",
    "communication",
    "eva_relationship",
    "technical",
    "project",
    "achievement",
    "requirement",
    "strategy",
    "learning",
    "physiology_policy",
    "meta"
}

# Sensitivity Mapping
SENSITIVITY_LEVELS = {
    "S0": 0, "PUBLIC": 0,
    "S1": 1, "PERSONAL": 1,
    "S2": 2, "PRIVATE": 2,
    "S3": 3, "HIGHLY_PRIVATE": 3,
    "S4": 4, "CRITICAL": 4
}

CORE_IDENTITY_CARD_FALLBACK = """Yash Anand Ingole ("Yash"), India. Mechanical-engineering diploma -> IIoT -> robotics/AI/embedded.
Builds EVA, an offline-first smart-glasses assistant (ESP32-S3 -> Android -> local LLM + memory).
Wants R&D in robotics/AI. Highly ambitious; hates losing; self-critical; wants to be understood.
Mixes Hindi/English. Technical questions: be precise. Emotional moments: calm and human.
Strategy: think critically, don't just agree. If he's wrong, say so kindly.
Wants EVA as a long-term companion that remembers continuity; no manipulation, no dependency.
Private topics (relationships, habits, health) are never spoken aloud unless he asks and it's private."""


class MemoryItem(BaseModel):
    memory_id: str
    category: str
    content: str
    importance: int = Field(default=3, ge=0, le=5)
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    sensitivity: str = "S1"
    status: str = "current"  # current, historical, evolved, uncertain
    kind: str = "said"       # said, did, pref, infer, event, system
    source: str = "conversation"
    date_created: str = Field(default_factory=lambda: time.strftime("%Y-%m-%d"))
    last_confirmed: Optional[str] = None
    last_used: Optional[str] = None
    temporary: bool = False
    expires: Optional[str] = None
    triggers: List[str] = Field(default_factory=list)


class EvaMemoryStore:
    """
    Offline-First Persistent Memory Store for EVA.
    Backed by SQLite with FTS5 full-text indexing, relationship edges, and session logs.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path(settings.DATABASE_URL.replace("sqlite:///", "").lstrip("./")).parent / "eva_memory.db")
        self.db_path = Path(db_path).resolve()
        self._init_db()
        self._bootstrap_if_empty()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Main memories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    importance INTEGER NOT NULL DEFAULT 3,
                    confidence REAL NOT NULL DEFAULT 0.85,
                    sensitivity TEXT NOT NULL DEFAULT 'S1',
                    status TEXT NOT NULL DEFAULT 'current',
                    kind TEXT NOT NULL DEFAULT 'said',
                    source TEXT NOT NULL DEFAULT 'conversation',
                    date_created TEXT NOT NULL,
                    last_confirmed TEXT,
                    last_used TEXT,
                    temporary INTEGER NOT NULL DEFAULT 0,
                    expires TEXT,
                    triggers TEXT NOT NULL DEFAULT '[]'
                )
            """)

            # 2. FTS5 Virtual Table for sub-millisecond keyword retrieval
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                    memory_id UNINDEXED,
                    content,
                    category,
                    triggers,
                    tokenize = 'porter unicode61'
                )
            """)

            # 3. Triggers for syncing memories into memory_fts
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS mem_ai AFTER INSERT ON memories BEGIN
                    INSERT INTO memory_fts(memory_id, content, category, triggers)
                    VALUES (new.memory_id, new.content, new.category, new.triggers);
                END;
            """)

            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS mem_ad AFTER DELETE ON memories BEGIN
                    DELETE FROM memory_fts WHERE memory_id = old.memory_id;
                END;
            """)

            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS mem_au AFTER UPDATE ON memories BEGIN
                    DELETE FROM memory_fts WHERE memory_id = old.memory_id;
                    INSERT INTO memory_fts(memory_id, content, category, triggers)
                    VALUES (new.memory_id, new.content, new.category, new.triggers);
                END;
            """)

            # 4. Knowledge Graph Edges Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_edges (
                    src TEXT REFERENCES memories(memory_id) ON DELETE CASCADE,
                    dst TEXT REFERENCES memories(memory_id) ON DELETE CASCADE,
                    relation TEXT NOT NULL,
                    note TEXT,
                    created_at REAL NOT NULL,
                    PRIMARY KEY (src, dst, relation)
                )
            """)

            # 5. Conversation Sessions Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_sessions (
                    session_id TEXT PRIMARY KEY,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    active_topic TEXT,
                    previous_topic TEXT,
                    summary TEXT,
                    important_decisions TEXT DEFAULT '[]',
                    unfinished_topics TEXT DEFAULT '[]',
                    new_memory_ids TEXT DEFAULT '[]'
                )
            """)

            # 6. Conversation Messages Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    metadata TEXT DEFAULT '{}'
                )
            """)

            # 7. Audit & Decision Log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    action TEXT NOT NULL,
                    memory_id TEXT,
                    details TEXT
                )
            """)

            conn.commit()

    def _bootstrap_if_empty(self):
        """Seeds the database from docs/BOOK_OF_YASH.md if empty."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM memories")
            count = cursor.fetchone()[0]
            if count > 0:
                return

        # Attempt to read from docs/BOOK_OF_YASH.md
        boy_path = Path("docs/BOOK_OF_YASH.md")
        if not boy_path.exists():
            # Try alternate paths
            boy_path = Path(__file__).resolve().parents[4] / "docs" / "BOOK_OF_YASH.md"

        seeded = False
        if boy_path.exists():
            try:
                text = boy_path.read_text(encoding="utf-8")
                # Look for JSON seed block in Appendix 2
                json_match = re.search(r'```json seed\s*([\s\S]*?)\s*```', text)
                if json_match:
                    seed_data = json.loads(json_match.group(1))
                    for item in seed_data:
                        self.insert_memory(MemoryItem(**item))
                    seeded = True
            except Exception as e:
                print(f"[EvaMemoryStore] Warning: Could not parse BOOK_OF_YASH.md: {e}")

        if not seeded:
            # Seed foundational core identity
            self.insert_memory(MemoryItem(
                memory_id="ID.001",
                category="identity",
                content="Full name Yash Anand Ingole; goes by Yash; from India; engineering background.",
                source="bootstrap",
                confidence=0.98,
                importance=5,
                sensitivity="S1",
                kind="said",
                status="current",
                triggers=["name", "who am i", "introduction", "yash"]
            ))
            self.insert_memory(MemoryItem(
                memory_id="PR.003",
                category="project",
                content="EVA smart glasses AI assistant: wearable AI with voice, translation, navigation, image understanding, visual search, try-on, music, contextual assistance, project and personal memory. Phone does the heavy compute. Current main focus.",
                source="bootstrap",
                confidence=0.95,
                importance=5,
                sensitivity="S1",
                kind="did",
                status="current",
                triggers=["eva", "lara", "smart glasses", "glasses project"]
            ))
            self.insert_memory(MemoryItem(
                memory_id="CA.001",
                category="career",
                content="Wants a career in robotics/AI/IIoT/embedded R&D; motivated by building new technology, not just holding a job.",
                source="bootstrap",
                confidence=0.92,
                importance=5,
                sensitivity="S1",
                kind="said",
                status="current",
                triggers=["career", "job", "r&d", "future", "goal", "robotics"]
            ))

    def insert_memory(self, item: MemoryItem) -> str:
        """Inserts or replaces a memory item."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO memories (
                    memory_id, category, content, importance, confidence,
                    sensitivity, status, kind, source, date_created,
                    last_confirmed, last_used, temporary, expires, triggers
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.memory_id, item.category, item.content, item.importance,
                item.confidence, item.sensitivity, item.status, item.kind,
                item.source, item.date_created, item.last_confirmed,
                item.last_used, 1 if item.temporary else 0, item.expires,
                json.dumps(item.triggers)
            ))
            cursor.execute("""
                INSERT INTO memory_audit_log (timestamp, action, memory_id, details)
                VALUES (?, ?, ?, ?)
            """, (time.time(), "INSERT", item.memory_id, json.dumps({"category": item.category, "confidence": item.confidence})))
            conn.commit()
        return item.memory_id

    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Updates specific fields of an existing memory."""
        allowed_fields = {
            "content", "importance", "confidence", "sensitivity",
            "status", "last_confirmed", "last_used", "expires", "triggers"
        }
        set_clauses = []
        values = []
        for k, v in updates.items():
            if k in allowed_fields:
                set_clauses.append(f"{k} = ?")
                values.append(json.dumps(v) if k == "triggers" and isinstance(v, list) else v)

        if not set_clauses:
            return False

        values.append(memory_id)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE memories SET {', '.join(set_clauses)} WHERE memory_id = ?", tuple(values))
            cursor.execute("""
                INSERT INTO memory_audit_log (timestamp, action, memory_id, details)
                VALUES (?, ?, ?, ?)
            """, (time.time(), "UPDATE", memory_id, json.dumps(updates)))
            conn.commit()
            return cursor.rowcount > 0

    def evolve_memory(self, old_memory_id: str, new_item: MemoryItem, transition_context: str = "") -> str:
        """
        Marks an old memory as 'evolved' or 'historical' rather than deleting it,
        inserts the new active memory, and establishes a 'supersedes' edge.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE memories SET status = 'evolved', last_used = ? WHERE memory_id = ?",
                           (time.strftime("%Y-%m-%d"), old_memory_id))
            conn.commit()

        new_id = self.insert_memory(new_item)
        self.add_edge(src=new_id, dst=old_memory_id, relation="supersedes", note=transition_context)
        return new_id

    def add_edge(self, src: str, dst: str, relation: str, note: str = ""):
        """Adds a graph relationship between memories (e.g. led_to, part_of, related_to, supersedes)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO memory_edges (src, dst, relation, note, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (src, dst, relation, note, time.time()))
            conn.commit()

    def search_memories(
        self,
        query: str,
        category: Optional[str] = None,
        max_sensitivity: str = "S3",
        min_confidence: float = 0.50,
        active_only: bool = True,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Hybrid retrieval: FTS5 keyword matching + category filter + sensitivity gating + confidence weighting.
        """
        max_sens_val = SENSITIVITY_LEVELS.get(max_sensitivity.upper(), 3)
        clean_query = re.sub(r'[^a-zA-Z0-9\s]', ' ', query).strip()
        tokens = [t for t in clean_query.split() if len(t) > 2]

        results: List[Dict[str, Any]] = []
        with self._get_connection() as conn:
            cursor = conn.cursor()

        # 1. Try FTS5 match first
        fts_tokens = [re.sub(r'[^a-zA-Z0-9]', '', t) for t in tokens if len(t) > 1]
        fts_tokens = [t for t in fts_tokens if t]
        if fts_tokens:
            fts_expr = " OR ".join([f"{t}*" for t in fts_tokens])
            try:
                cursor.execute("""
                    SELECT m.*, rank
                    FROM memory_fts f
                    JOIN memories m ON f.memory_id = m.memory_id
                    WHERE memory_fts MATCH ?
                    ORDER BY rank
                    LIMIT 50
                """, (fts_expr,))
                for row in cursor.fetchall():
                    item_dict = dict(row)
                    item_sens_val = SENSITIVITY_LEVELS.get(item_dict.get("sensitivity", "S1").upper(), 1)
                    if item_sens_val > max_sens_val:
                        continue
                    if item_dict.get("confidence", 0.0) < min_confidence:
                        continue
                    if active_only and item_dict.get("status") not in ("current", "CURRENT", "uncertain", "UNCERTAIN"):
                        continue
                    if category and item_dict.get("category").lower() != category.lower():
                        continue
                    results.append(item_dict)
            except Exception:
                pass

        # 2. Fallback / supplement: Trigger keywords and LIKE matching
        existing_ids = {r["memory_id"] for r in results}
        for t in tokens:
            cursor.execute("""
                SELECT * FROM memories
                WHERE (triggers LIKE ? OR content LIKE ? OR category LIKE ?)
            """, (f'%"{t}"%', f'%{t}%', f'%{t}%'))
            for row in cursor.fetchall():
                item_dict = dict(row)
                if item_dict["memory_id"] in existing_ids:
                    continue
                item_sens_val = SENSITIVITY_LEVELS.get(item_dict.get("sensitivity", "S1").upper(), 1)
                if item_sens_val > max_sens_val:
                    continue
                if item_dict.get("confidence", 0.0) < min_confidence:
                    continue
                if active_only and item_dict.get("status") not in ("current", "CURRENT", "uncertain", "UNCERTAIN"):
                    continue
                if category and item_dict.get("category").lower() != category.lower():
                    continue
                results.append(item_dict)
                existing_ids.add(item_dict["memory_id"])

        # Calculate token overlap relevance and sort by match quality
        for r in results:
            content_lower = (r.get("content", "") + " " + str(r.get("triggers", "")) + " " + r.get("memory_id", "")).lower()
            overlap = sum(1 for t in tokens if t.lower() in content_lower)
            # Boost exact phrase match if multiple tokens
            exact_boost = 5.0 if clean_query.lower() in content_lower else 0.0
            r["_relevance_score"] = (overlap * 10.0) + exact_boost + (r.get("importance", 3) * 0.5) + (r.get("confidence", 0.8) * 0.5)

        results.sort(key=lambda x: x.get("_relevance_score", 0.0), reverse=True)
        return results[:limit]

    def get_core_identity_card(self) -> str:
        """Returns the ≤300 token deterministic Core Identity Card."""
        boy_path = Path("docs/BOOK_OF_YASH.md")
        if boy_path.exists():
            try:
                text = boy_path.read_text(encoding="utf-8")
                match = re.search(r'### A6\. Core Identity Card[^\n]*\n```text\s*([\s\S]*?)\s*```', text)
                if match:
                    return match.group(1).strip()
            except Exception:
                pass
        return CORE_IDENTITY_CARD_FALLBACK.strip()

    def get_memory_graph(self, memory_id: str) -> Dict[str, Any]:
        """Returns linked memories and relationships for a given memory ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.*, m.content, m.category, m.status
                FROM memory_edges e
                JOIN memories m ON e.dst = m.memory_id
                WHERE e.src = ?
            """, (memory_id,))
            outgoing = [dict(r) for r in cursor.fetchall()]

            cursor.execute("""
                SELECT e.*, m.content, m.category, m.status
                FROM memory_edges e
                JOIN memories m ON e.src = m.memory_id
                WHERE e.dst = ?
            """, (memory_id,))
            incoming = [dict(r) for r in cursor.fetchall()]

            return {
                "memory_id": memory_id,
                "outgoing": outgoing,
                "incoming": incoming
            }

    def export_all_memories(self) -> List[Dict[str, Any]]:
        """Exports all memories as structured dictionaries for user inspection."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM memories ORDER BY importance DESC, date_created DESC")
            rows = cursor.fetchall()
            exported = []
            for r in rows:
                d = dict(r)
                if isinstance(d.get("triggers"), str):
                    try:
                        d["triggers"] = json.loads(d["triggers"])
                    except Exception:
                        d["triggers"] = []
                exported.append(d)
            return exported

    def delete_memory(self, memory_id: str) -> bool:
        """Deletes a memory item."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories WHERE memory_id = ?", (memory_id,))
            cursor.execute("""
                INSERT INTO memory_audit_log (timestamp, action, memory_id, details)
                VALUES (?, ?, ?, ?)
            """, (time.time(), "DELETE", memory_id, "User requested memory deletion"))
            conn.commit()
            return cursor.rowcount > 0

    # Session / Dialogue Management
    def save_conversation_turn(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversation_messages (session_id, role, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, role, content, time.time(), json.dumps(metadata or {})))
            conn.commit()

    def get_session_turns(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, content, timestamp, metadata
                FROM conversation_messages
                WHERE session_id = ?
                ORDER BY id ASC
                LIMIT ?
            """, (session_id, limit))
            return [dict(r) for r in cursor.fetchall()]

    def update_session_summary(
        self,
        session_id: str,
        topic: str,
        summary: str,
        decisions: Optional[List[str]] = None,
        unfinished: Optional[List[str]] = None
    ):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO conversation_sessions (
                    session_id, start_time, end_time, active_topic, summary,
                    important_decisions, unfinished_topics
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, time.time(), time.time(), topic, summary,
                json.dumps(decisions or []), json.dumps(unfinished or [])
            ))
            conn.commit()

    def get_latest_session_summary(self, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if session_id:
                cursor.execute("SELECT * FROM conversation_sessions WHERE session_id = ?", (session_id,))
            else:
                cursor.execute("SELECT * FROM conversation_sessions ORDER BY start_time DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d["important_decisions"] = json.loads(d.get("important_decisions") or "[]")
                d["unfinished_topics"] = json.loads(d.get("unfinished_topics") or "[]")
                return d
            return None


# Global Singleton
eva_memory_store = EvaMemoryStore()
