"""
Cognitive memory subsystem package.
"""
from backend.app.services.memory.salience_gate import SalienceGate
from backend.app.services.memory.working_memory_engine import WorkingMemoryEngine, AttendedFact
from backend.app.services.memory.temporal_graph_store import TemporalGraphStore, TemporalEdge
from backend.app.services.memory.sleep_consolidation import SleepConsolidationEngine
from backend.app.services.memory.eva_memory_store import eva_memory_store, EvaMemoryStore, MemoryItem
from backend.app.services.memory.context_builder import context_builder, ContextBuilder, ContextPayload, TopicState
from backend.app.services.memory.contradiction_engine import contradiction_engine, ContradictionEngine
from backend.app.services.memory.conversation_compressor import conversation_compressor, ConversationCompressor

__all__ = [
    "SalienceGate",
    "WorkingMemoryEngine",
    "AttendedFact",
    "TemporalGraphStore",
    "TemporalEdge",
    "SleepConsolidationEngine",
    "eva_memory_store",
    "EvaMemoryStore",
    "MemoryItem",
    "context_builder",
    "ContextBuilder",
    "ContextPayload",
    "TopicState",
    "contradiction_engine",
    "ContradictionEngine",
    "conversation_compressor",
    "ConversationCompressor"
]
