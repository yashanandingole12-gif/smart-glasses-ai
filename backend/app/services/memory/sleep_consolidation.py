"""
Sleep & Idle Memory Consolidation Engine.
Runs on a periodic or idle schedule (analogous to biological sleep consolidation)
to extract long-term semantic habits from working memory traces.
"""
from typing import Dict, Any, List
import time
from backend.app.services.memory.working_memory_engine import WorkingMemoryEngine
from backend.app.services.memory.temporal_graph_store import TemporalGraphStore


class SleepConsolidationEngine:
    """Consolidates episodic facts into the permanent temporal graph."""

    def __init__(self, working_memory: WorkingMemoryEngine, temporal_graph: TemporalGraphStore):
        self.working_memory = working_memory
        self.temporal_graph = temporal_graph
        self.last_consolidation_time: float = time.time()
        self.consolidated_cycles_count: int = 0

    def run_consolidation_cycle(self) -> Dict[str, Any]:
        """Performs a memory consolidation pass."""
        state = self.working_memory.get_state()
        consolidated_items: List[str] = []

        # 1. Consolidate frequently met interlocutors
        for person in state["interlocutors"]:
            self.temporal_graph.insert_fact(
                subject="wearer",
                predicate="interacted_with",
                object=person,
                source_context="episodic_working_memory_consolidation",
                tags=["social", "consolidated"]
            )
            consolidated_items.append(f"Person: {person}")

        # 2. Consolidate stable location patterns
        loc = state["location"]
        if loc and loc != "Unknown":
            self.temporal_graph.insert_fact(
                subject="wearer",
                predicate="visited_location",
                object=loc,
                source_context="episodic_working_memory_consolidation",
                tags=["spatial", "consolidated"]
            )
            consolidated_items.append(f"Location: {loc}")

        self.last_consolidation_time = time.time()
        self.consolidated_cycles_count += 1

        return {
            "cycle_index": self.consolidated_cycles_count,
            "timestamp": self.last_consolidation_time,
            "consolidated_items": consolidated_items,
            "status": "CONSOLIDATED_SUCCESS"
        }
