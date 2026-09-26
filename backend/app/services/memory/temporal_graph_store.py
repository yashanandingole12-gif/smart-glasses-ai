"""
Long-Term Temporal Knowledge Graph & Vector Store.
Stores evolving episodic and semantic memory over days to years with valid time intervals
(Zep/Graphiti-style temporal relations: e.g. "User liked cafe X before dietary transition Y").
Backed by SQLite persistent storage with in-memory caching.
"""
import sqlite3
import json
import time
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.app.config import settings

logger = logging.getLogger("SmartGlasses.TemporalGraphStore")


class TemporalEdge(BaseModel):
    """A semantic relationship between entities with temporal bounds."""
    id: Optional[int] = None
    subject: str
    predicate: str
    object: str
    valid_from: float = Field(default_factory=time.time)
    valid_to: Optional[float] = None  # None indicates currently active
    confidence: float = 1.0
    source_context: str = ""
    tags: List[str] = Field(default_factory=list)


class TemporalGraphStore:
    """
    Temporal Graph Memory Store.
    Tracks facts across time, maintaining history of transitions, past preferences, and long-term habits.
    Persisted persistently to SQLite.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path(settings.DATABASE_URL.replace("sqlite:///", "").lstrip("./")).parent / "eva_memory.db")
        self.db_path = Path(db_path).resolve()
        self.edges: List[TemporalEdge] = []
        self.entity_index: Dict[str, List[int]] = {}
        self._init_db()
        self._load_from_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS temporal_graph_edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject TEXT NOT NULL,
                    predicate TEXT NOT NULL,
                    object TEXT NOT NULL,
                    valid_from REAL NOT NULL,
                    valid_to REAL,
                    confidence REAL NOT NULL DEFAULT 1.0,
                    source_context TEXT DEFAULT '',
                    tags TEXT DEFAULT '[]'
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_temporal_sub_obj ON temporal_graph_edges (subject, object)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_temporal_valid ON temporal_graph_edges (valid_to)
            """)
            conn.commit()

    def _load_from_db(self):
        """Loads all temporal edges from SQLite into the fast lookup index."""
        self.edges.clear()
        self.entity_index.clear()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM temporal_graph_edges ORDER BY valid_from ASC")
                for row in cursor.fetchall():
                    tags_parsed = []
                    if row["tags"]:
                        try:
                            tags_parsed = json.loads(row["tags"])
                        except Exception:
                            tags_parsed = [row["tags"]]
                    edge = TemporalEdge(
                        id=row["id"],
                        subject=row["subject"],
                        predicate=row["predicate"],
                        object=row["object"],
                        valid_from=row["valid_from"],
                        valid_to=row["valid_to"],
                        confidence=row["confidence"],
                        source_context=row["source_context"] or "",
                        tags=tags_parsed
                    )
                    idx = len(self.edges)
                    self.edges.append(edge)
                    for ent in [edge.subject.lower(), edge.object.lower()]:
                        if ent not in self.entity_index:
                            self.entity_index[ent] = []
                        self.entity_index[ent].append(idx)
        except Exception as e:
            logger.error(f"Error loading temporal edges from SQLite: {e}")

    def insert_fact(
        self,
        subject: str,
        predicate: str,
        object: str,
        valid_from: Optional[float] = None,
        valid_to: Optional[float] = None,
        source_context: str = "",
        tags: Optional[List[str]] = None
    ) -> TemporalEdge:
        """Inserts a temporal fact edge into SQLite and updates fast in-memory indices."""
        vf = valid_from if valid_from is not None else time.time()
        tags_list = tags or []
        
        # Persist to SQLite
        edge_id = None
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO temporal_graph_edges (
                        subject, predicate, object, valid_from, valid_to, confidence, source_context, tags
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (subject, predicate, object, vf, valid_to, 1.0, source_context, json.dumps(tags_list)))
                edge_id = cursor.lastrowid
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to persist temporal edge to DB: {e}")

        edge = TemporalEdge(
            id=edge_id,
            subject=subject,
            predicate=predicate,
            object=object,
            valid_from=vf,
            valid_to=valid_to,
            source_context=source_context,
            tags=tags_list
        )
        idx = len(self.edges)
        self.edges.append(edge)

        for ent in [subject.lower(), object.lower()]:
            if ent not in self.entity_index:
                self.entity_index[ent] = []
            self.entity_index[ent].append(idx)

        return edge

    def supersede_fact(
        self,
        subject: str,
        predicate: str,
        new_object: str,
        transition_context: str = ""
    ) -> TemporalEdge:
        """
        Marks previous active facts with matching subject and predicate as expired,
        and creates a new active temporal fact in SQLite and in-memory cache.
        Example: "user -> dietary_preference -> omnivore" -> superseded by "vegan".
        """
        now = time.time()
        
        # Update in SQLite
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE temporal_graph_edges
                    SET valid_to = ?
                    WHERE LOWER(subject) = LOWER(?) AND LOWER(predicate) = LOWER(?) AND valid_to IS NULL
                """, (now, subject, predicate))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to supersede temporal edge in DB: {e}")

        # Update in memory
        for edge in self.edges:
            if edge.subject.lower() == subject.lower() and edge.predicate.lower() == predicate.lower() and edge.valid_to is None:
                edge.valid_to = now

        return self.insert_fact(
            subject=subject,
            predicate=predicate,
            object=new_object,
            valid_from=now,
            source_context=transition_context,
            tags=["superseded_update"]
        )

    def query_entity_history(self, entity: str) -> List[Dict[str, Any]]:
        """Returns the full chronological history of an entity."""
        ent_lower = entity.lower()
        indices = self.entity_index.get(ent_lower, [])
        history = []
        for idx in indices:
            edge = self.edges[idx]
            history.append({
                "subject": edge.subject,
                "predicate": edge.predicate,
                "object": edge.object,
                "valid_from": edge.valid_from,
                "valid_to": edge.valid_to,
                "is_current": edge.valid_to is None,
                "source": edge.source_context
            })
        return sorted(history, key=lambda x: x["valid_from"])

    def query_relevant_facts(self, query: str, active_only: bool = True) -> List[str]:
        """Keyword and token matching search over temporal knowledge base."""
        q_words = set(query.lower().split())
        matched_facts = []

        for edge in self.edges:
            if active_only and edge.valid_to is not None:
                continue

            text_repr = f"{edge.subject} {edge.predicate} {edge.object} {' '.join(edge.tags)}".lower()
            if any(w in text_repr for w in q_words if len(w) > 2):
                status = "currently" if edge.valid_to is None else f"previously (until {time.ctime(edge.valid_to)})"
                matched_facts.append(f"{edge.subject} {edge.predicate} {edge.object} ({status})")

        return matched_facts
