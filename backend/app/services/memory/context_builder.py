"""
EVA Context Builder & Topic Tracker:
Deterministic, token-bounded context synthesizer with conversational continuity,
topic stack unwinding, explicit recall resolver, and epistemic memory grounding.

Implements requirements from Sections 10, 12, 26, 27, 29:
- Rolling Context Architecture (Core Identity <=300 tokens + Topic + Memories + Summary + Turns)
- Topic Continuity State Machine & Recovery ("Coming back to what we were discussing...")
- Epistemic Recall Resolution ("I told you about this before" -> Grounded Recall or Honest Fallback)
- Intent-Aware Memory Category Boosting
"""
import time
import json
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from backend.app.services.memory.eva_memory_store import eva_memory_store, EvaMemoryStore

logger = logging.getLogger("SmartGlasses.ContextBuilder")

# Related topics semantic graph mapping
TOPIC_RELATIONS_GRAPH: Dict[str, List[str]] = {
    "EVA Architecture": ["Offline Storage", "Smart Glasses", "Book of Yash", "Android Companion", "FastAPI Gateway"],
    "Robotics & Hardware": ["Delta Robot", "Automatic Tool Changer", "Arduino Uno", "Servos & Steppers", "Ashirwaad Workshop"],
    "Career & Aspirations": ["Robotics R&D", "AI Autonomy", "Target Companies", "Technical Product Strategy"],
    "Personal & Emotional Reflections": ["Loneliness & Understanding", "Long-term Companion", "Self-Reflection", "Creative Writing"],
    "Education & Learning": ["Polytechnic Diploma", "Mechanical Engineering", "Industrial IoT (IIoT)", "Machine Learning"],
    "Strategy & Analysis": ["Ramayan Campaign", "Product Strategy", "Technical Marketing", "Market Positioning"]
}

# Topic recovery cue patterns
TOPIC_RECOVERY_PATTERNS = [
    r"coming back to",
    r"back to what we were (?:discussing|saying|talking about)",
    r"back to our topic",
    r"getting back to",
    r"as we were saying (?:earlier|before)",
    r"let's return to",
    r"anyway,? back to",
    r"returning to"
]

# Explicit memory recall patterns
EXPLICIT_RECALL_PATTERNS = [
    r"i told you about (?:this|that) before",
    r"remember when we (?:discussed|talked about)",
    r"do you remember (?:what|when|my|the)",
    r"what did i say about",
    r"as i mentioned earlier",
    r"do you know about my"
]


class TopicState(BaseModel):
    active_topic: str = "EVA Exploration"
    subtopic: Optional[str] = None
    previous_topic: Optional[str] = None
    related_topics: List[str] = Field(default_factory=list)
    topic_history_stack: List[str] = Field(default_factory=list)
    updated_at: float = Field(default_factory=time.time)


class ContextPayload(BaseModel):
    system_prompt: str
    core_identity: str
    active_topic: str
    subtopic: Optional[str] = None
    previous_topic: Optional[str] = None
    related_topics: List[str] = Field(default_factory=list)
    relevant_memories: List[Dict[str, Any]]
    recent_messages: List[Dict[str, str]]
    conversation_summary: Optional[str] = None
    is_recall_query: bool = False
    recall_found: bool = False
    token_estimate: int = 0
    offline_ready: bool = True
    debug_trace: Dict[str, Any] = Field(default_factory=dict)


class ContextBuilder:
    """
    Synthesizes deterministic, token-bounded, and epistemic LLM context.
    Provides topic tracking, stack unwinding, and explicit memory recall verification.
    """

    def __init__(self, memory_store: Optional[EvaMemoryStore] = None):
        self.memory_store = memory_store or eva_memory_store
        self._topic_states: Dict[str, TopicState] = {}

    def get_or_create_topic(self, session_id: str) -> TopicState:
        if session_id not in self._topic_states:
            self._topic_states[session_id] = TopicState(
                active_topic="EVA Exploration",
                related_topics=TOPIC_RELATIONS_GRAPH.get("EVA Architecture", [])
            )
        return self._topic_states[session_id]

    def set_active_topic(self, session_id: str, new_topic: str, subtopic: Optional[str] = None):
        current = self.get_or_create_topic(session_id)
        if current.active_topic.lower() != new_topic.lower():
            # Push current to history stack
            if current.active_topic not in current.topic_history_stack:
                current.topic_history_stack.append(current.active_topic)
                if len(current.topic_history_stack) > 5:
                    current.topic_history_stack.pop(0)

            current.previous_topic = current.active_topic
            current.active_topic = new_topic
            current.related_topics = TOPIC_RELATIONS_GRAPH.get(new_topic, [])

        current.subtopic = subtopic
        current.updated_at = time.time()

    def handle_topic_recovery(self, session_id: str, user_message: str) -> bool:
        """
        Checks if user is requesting to return to a previous discussion.
        If so, unwinds the topic stack.
        """
        t_low = user_message.lower()
        is_recovery = any(re.search(pat, t_low) for pat in TOPIC_RECOVERY_PATTERNS)
        if is_recovery:
            current = self.get_or_create_topic(session_id)
            if current.previous_topic and current.previous_topic != current.active_topic:
                recovered = current.previous_topic
                current.previous_topic = current.active_topic
                current.active_topic = recovered
                current.related_topics = TOPIC_RELATIONS_GRAPH.get(recovered, [])
                logger.info(f"Topic recovered for session {session_id}: '{recovered}'")
                return True
            elif current.topic_history_stack:
                recovered = current.topic_history_stack.pop()
                current.previous_topic = current.active_topic
                current.active_topic = recovered
                current.related_topics = TOPIC_RELATIONS_GRAPH.get(recovered, [])
                logger.info(f"Topic popped from history stack for session {session_id}: '{recovered}'")
                return True
        return False

    def detect_explicit_recall(self, user_message: str) -> bool:
        """Checks if the user is explicitly challenging or asking EVA's memory."""
        t_low = user_message.lower()
        return any(re.search(pat, t_low) for pat in EXPLICIT_RECALL_PATTERNS)

    def build_context(
        self,
        session_id: str,
        user_message: str,
        max_memories: int = 5,
        max_turns: int = 10,
        max_sensitivity: str = "S3"
    ) -> ContextPayload:
        """
        Synthesizes the complete minimal context payload for an incoming turn.
        """
        t0 = time.time()
        topic_state = self.get_or_create_topic(session_id)

        # 1. Topic recovery check (unwinds topic if user says "Coming back to...")
        recovered_topic = self.handle_topic_recovery(session_id, user_message)

        # 2. Topic inference if not recovering
        if not recovered_topic:
            detected_topic, detected_subtopic = self._infer_topic(user_message, topic_state.active_topic)
            if detected_topic != topic_state.active_topic:
                self.set_active_topic(session_id, detected_topic, subtopic=detected_subtopic)

        # 3. Explicit recall detection
        is_recall = self.detect_explicit_recall(user_message)

        # 4. Core Identity Card (deterministic, <=300 tokens)
        core_identity = self.memory_store.get_core_identity_card()

        # 5. Category-boosted search query
        category_hint = self._get_category_hint(user_message)
        search_query = f"{user_message} {topic_state.active_topic}"

        relevant_memories = self.memory_store.search_memories(
            query=search_query,
            category=category_hint,
            max_sensitivity=max_sensitivity,
            min_confidence=0.40,
            active_only=not is_recall,  # if asking recall, include historical/evolved
            limit=max_memories
        )

        recall_found = len(relevant_memories) > 0 if is_recall else False

        # 6. Rolling Conversation Turns
        raw_turns = self.memory_store.get_session_turns(session_id, limit=max_turns)
        recent_messages: List[Dict[str, str]] = []
        for t in raw_turns:
            recent_messages.append({
                "role": t.get("role", "user"),
                "content": t.get("content", "")
            })

        # 7. Latest Session Summary
        session_summary_obj = self.memory_store.get_latest_session_summary(session_id)
        summary_text = session_summary_obj.get("summary") if session_summary_obj else None

        # 8. Assemble System Prompt
        memories_block = ""
        if relevant_memories:
            mem_lines = []
            for m in relevant_memories:
                cat = m.get('category', 'FACT').upper()
                kind = f"[{m.get('kind', 'said').upper()}]"
                stat = f"({m.get('status', 'current')})"
                mem_lines.append(f"- {kind} [{cat}] {m.get('content', '')} {stat}")
            memories_block = "\nRELEVANT USER MEMORIES (Epistemic truth; do not parrot verbatim):\n" + "\n".join(mem_lines)

        summary_block = f"\nPREVIOUS SESSION CONTEXT: {summary_text}" if summary_text else ""

        recall_instruction = ""
        if is_recall:
            if recall_found:
                recall_instruction = "\nRECALL INSTRUCTION: User is recalling past history. Confirm naturally using the retrieved memory (e.g. 'Yeah, I remember...')."
            else:
                recall_instruction = "\nRECALL INSTRUCTION: User is asking about a past discussion not found in active records. DO NOT FABRICATE A MEMORY. State honestly: 'I don't have that part of our history available right now. Tell me the detail again.'"

        system_prompt = f"""You are EVA, an ambient personal AI companion designed for continuous relationship and long-term memory.

USER CORE IDENTITY:
{core_identity}
{memories_block}
{summary_block}

CURRENT ACTIVE TOPIC: {topic_state.active_topic} (Previous: {topic_state.previous_topic or 'None'})
SUBTOPIC: {topic_state.subtopic or 'None'} | RELATED: {', '.join(topic_state.related_topics) if topic_state.related_topics else 'None'}
{recall_instruction}

COMMUNICATION PRINCIPLES:
- Conversational continuity: If user refers to past discussions or projects ('the project', 'remember when'), use memory.
- Be concise, natural, warm, and direct. Avoid generic AI boilerplate ('Certainly! As an AI...').
- If Yash is mistaken or exploring a questionable hypothesis, tell him kindly and critically.
- Mix of English & Hindi is natural for casual dialogue."""

        # 9. Token estimation (~4 chars per token)
        total_chars = len(system_prompt) + sum(len(m.get("content", "")) for m in recent_messages) + len(user_message)
        est_tokens = total_chars // 4

        debug_trace = {
            "retrieval_ms": (time.time() - t0) * 1000.0,
            "memories_count": len(relevant_memories),
            "memory_ids": [m.get("memory_id") for m in relevant_memories],
            "active_topic": topic_state.active_topic,
            "subtopic": topic_state.subtopic,
            "previous_topic": topic_state.previous_topic,
            "is_recall_query": is_recall,
            "recall_found": recall_found
        }

        return ContextPayload(
            system_prompt=system_prompt,
            core_identity=core_identity,
            active_topic=topic_state.active_topic,
            subtopic=topic_state.subtopic,
            previous_topic=topic_state.previous_topic,
            related_topics=topic_state.related_topics,
            relevant_memories=relevant_memories,
            recent_messages=recent_messages,
            conversation_summary=summary_text,
            is_recall_query=is_recall,
            recall_found=recall_found,
            token_estimate=est_tokens,
            offline_ready=True,
            debug_trace=debug_trace
        )

    def _infer_topic(self, text: str, current_topic: str) -> Tuple[str, Optional[str]]:
        """Lightweight deterministic topic classifier with subtopics."""
        t_low = text.lower()
        if any(w in t_low for w in ["companies in", "career", "job", "r&d", "interview", "application", "mahindra", "boston", "work in"]):
            sub = "Target Companies" if "company" in t_low or "boston" in t_low else "R&D Aspirations"
            return ("Career & Aspirations", sub)
        elif any(w in t_low for w in ["delta robot", "servo", "stepper", "nema", "atc", "arduino", "inmp441", "motor", "lathe"]):
            sub = "Delta Robot" if "delta" in t_low else "Hardware Components"
            return ("Robotics & Hardware", sub)
        elif any(w in t_low for w in ["eva", "lara", "glasses", "smart glasses", "companion"]):
            sub = "Memory Engine" if "memory" in t_low else "System Architecture"
            return ("EVA Architecture", sub)
        elif any(w in t_low for w in ["love", "lonely", "feeling", "relationship", "jealousy", "poem", "heart"]):
            sub = "Personal Reflections"
            return ("Personal & Emotional Reflections", sub)
        elif any(w in t_low for w in ["marketing", "ramayan", "strategy", "campaign"]):
            sub = "Media & Strategic Analysis"
            return ("Strategy & Analysis", sub)
        elif any(w in t_low for w in ["study", "diploma", "iiot", "college", "polytechnic", "ashirwaad"]):
            sub = "Mechanical Diploma" if "diploma" in t_low else "Industrial IoT"
            return ("Education & Learning", sub)
        elif "robot" in t_low:
            return ("Robotics & Hardware", None)
        return (current_topic, None)

    def _get_category_hint(self, text: str) -> Optional[str]:
        """Maps query intent keywords to memory categories for focused retrieval."""
        t_low = text.lower()
        if any(w in t_low for w in ["losing", "hate", "criticism", "ambition", "compare"]):
            return "personality"
        elif any(w in t_low for w in ["delta", "robot", "servo", "nema", "atc"]):
            return "project"
        elif any(w in t_low for w in ["diploma", "polytechnic", "ashirwaad", "internship", "college"]):
            return "education"
        elif any(w in t_low for w in ["career", "job", "r&d", "mahindra"]):
            return "career"
        elif any(w in t_low for w in ["love", "lonely", "poem", "feeling"]):
            return "emotional"
        return None


# Global Singleton
context_builder = ContextBuilder()
