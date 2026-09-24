"""
EVA Conversation Compressor:
Automatically compresses long multi-turn sessions into concise summaries,
key decisions, and unfinished topics to prevent context explosion.
"""
import time
import logging
from typing import Dict, Any, List, Optional
from backend.app.services.memory.eva_memory_store import eva_memory_store, EvaMemoryStore

logger = logging.getLogger("SmartGlasses.ConversationCompressor")

COMPRESSION_TRIGGER_TURNS = 12


class ConversationCompressor:
    """
    Monitors active dialogue length and produces structured summaries.
    """

    def __init__(self, memory_store: Optional[EvaMemoryStore] = None):
        self.memory_store = memory_store or eva_memory_store

    def should_compress(self, session_id: str) -> bool:
        turns = self.memory_store.get_session_turns(session_id, limit=COMPRESSION_TRIGGER_TURNS + 2)
        return len(turns) >= COMPRESSION_TRIGGER_TURNS

    def compress_session(
        self,
        session_id: str,
        active_topic: str = "General",
        custom_summary: Optional[str] = None,
        decisions: Optional[List[str]] = None,
        unfinished_topics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compresses dialogue turns into a persistent summary record.
        """
        turns = self.memory_store.get_session_turns(session_id, limit=50)
        if not turns:
            return {"status": "empty"}

        # Deterministic extractive summary generation if no custom summary provided
        if not custom_summary:
            user_queries = [t.get("content", "") for t in turns if t.get("role") == "user"]
            assistant_points = [t.get("content", "") for t in turns if t.get("role") == "assistant"]
            
            topics_mentioned = set()
            for q in user_queries:
                for w in q.split():
                    if len(w) > 4 and w.isalnum():
                        topics_mentioned.add(w)

            sample_topics = list(topics_mentioned)[:4]
            custom_summary = f"Session regarding {active_topic}. User explored {', '.join(sample_topics) if sample_topics else 'various topics'}. Discussed architecture and operational plans."

        decisions_list = decisions or []
        if not decisions_list:
            for t in turns:
                content = t.get("content", "").lower()
                if "decided" in content or "agreed on" in content or "will use" in content:
                    decisions_list.append(t.get("content", "")[:120])

        unfinished_list = unfinished_topics or []

        self.memory_store.update_session_summary(
            session_id=session_id,
            topic=active_topic,
            summary=custom_summary,
            decisions=decisions_list,
            unfinished=unfinished_list
        )

        logger.info(f"Compressed session {session_id} into topic '{active_topic}'.")
        return {
            "session_id": session_id,
            "topic": active_topic,
            "summary": custom_summary,
            "decisions": decisions_list,
            "unfinished": unfinished_list,
            "compressed_turns_count": len(turns)
        }


# Global Singleton
conversation_compressor = ConversationCompressor()
