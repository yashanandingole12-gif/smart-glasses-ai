"""
Long-Term Temporal Knowledge Graph & Vector Store.
Stores evolving episodic and semantic memory over days to years with valid time intervals
(Zep/Graphiti-style temporal relations: e.g. "User liked cafe X before dietary transition Y").
"""
from typing import Dict, Any, List, Optional
import time
from pydantic import BaseModel, Field


class TemporalEdge(BaseModel):
    """A semantic relationship between entities with temporal bounds."""
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
    """

    def __init__(self):
        self.edges: List[TemporalEdge] = []
        self.entity_index: Dict[str, List[int]] = {}

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
        """Inserts a temporal fact edge and updates indices."""
        edge = TemporalEdge(
            subject=subject,
            predicate=predicate,
            object=object,
            valid_from=valid_from if valid_from is not None else time.time(),
            valid_to=valid_to,
            source_context=source_context,
            tags=tags or []
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
        and creates a new active temporal fact.
        Example: "user -> dietary_preference -> omnivore" -> superseded by "vegan".
        """
        now = time.time()
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
        """Simple keyword/semantic search over temporal knowledge base."""
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
