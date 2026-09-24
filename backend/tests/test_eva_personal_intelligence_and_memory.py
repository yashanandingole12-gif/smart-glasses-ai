"""
Comprehensive Test Suite for EVA Personal Intelligence, Book of Yash Knowledge Base,
Offline-First Memory Engine (SQLite + FTS5), Context Synthesizer, Contradiction Tracking,
and Conversational Continuity (Day 1 -> Day 2 -> Day 10).
"""
import pytest
import uuid
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.memory.eva_memory_store import eva_memory_store, MemoryItem
from backend.app.services.memory.context_builder import context_builder
from backend.app.services.memory.contradiction_engine import contradiction_engine
from backend.app.services.memory.conversation_compressor import conversation_compressor
from backend.app.services.agent_graph import run_agent

client = TestClient(app)


def test_eva_bootstrap_seeding_and_fts5_search():
    """Verify that Book of Yash bootstrap seed memories exist and FTS5 search operates instantly."""
    # 1. Delta robot search
    results_delta = eva_memory_store.search_memories(query="delta robot servos HC-05", limit=5)
    assert len(results_delta) > 0
    assert any("delta" in r["content"].lower() or "servo" in r["content"].lower() for r in results_delta)

    # 2. Career aspiration search
    results_career = eva_memory_store.search_memories(query="robotics R&D career", category="career", limit=5)
    assert len(results_career) > 0
    assert any("robotics" in r["content"].lower() for r in results_career)

    # 3. Education search
    results_edu = eva_memory_store.search_memories(query="mechanical engineering diploma polytechnic", limit=5)
    assert len(results_edu) > 0
    assert any("diploma" in r["content"].lower() or "mechanical" in r["content"].lower() for r in results_edu)


def test_core_identity_card_token_limit():
    """Verify that Core Identity Card is concise and <= 300 tokens (~1200 characters)."""
    card = eva_memory_store.get_core_identity_card()
    assert isinstance(card, str)
    assert len(card) > 50
    # ~4 chars per token -> 300 tokens is ~1200 chars
    token_est = len(card) // 4
    assert token_est <= 300, f"Core Identity Card exceeds 300 tokens: {token_est} tokens ({len(card)} chars)"
    assert "Yash" in card
    assert "EVA" in card


def test_contradiction_and_evolution_system():
    """Verify that evolving a preference preserves history and creates an 'evolved' relation."""
    # Clean up any leftover test memories
    with eva_memory_store._get_connection() as conn:
        conn.execute("DELETE FROM memories WHERE memory_id LIKE 'TEST.%'")
        conn.commit()

    test_id = f"TEST.{uuid.uuid4().hex[:6].upper()}"
    old_mem = MemoryItem(
        memory_id=test_id,
        category="career",
        content="Wants to work exclusively in traditional mechanical tooling and fabrication.",
        confidence=0.88,
        importance=4,
        sensitivity="S1",
        status="current",
        triggers=["career", "mechanical", "tooling"]
    )
    eva_memory_store.insert_memory(old_mem)

    # Now state an evolved ambition
    new_id, old_evolved_id = contradiction_engine.process_and_evolve_memory(
        new_content="Wants to work in AI robotics and intelligent autonomy R&D.",
        category="career",
        confidence=0.95,
        importance=5,
        triggers=["career", "robotics", "ai"]
    )

    try:
        assert new_id is not None
        assert old_evolved_id == test_id

        # Verify old memory is now EVOLVED (not deleted)
        with eva_memory_store._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM memories WHERE memory_id = ?", (test_id,))
            row = cursor.fetchone()
            assert row is not None
            assert row[0] == "evolved"

        # Verify graph relationship exists
        graph = eva_memory_store.get_memory_graph(new_id)
        assert len(graph["outgoing"]) > 0
        assert graph["outgoing"][0]["relation"] == "supersedes"
        assert graph["outgoing"][0]["dst"] == test_id
    finally:
        eva_memory_store.delete_memory(test_id)
        if new_id:
            eva_memory_store.delete_memory(new_id)


def test_context_builder_and_topic_continuity():
    """Verify ContextBuilder tracks active topics, unwinds topic stacks, and synthesizes token-bounded context."""
    session_id = f"test_sess_{uuid.uuid4().hex[:8]}"

    # Turn 1: Robotics hardware
    ctx1 = context_builder.build_context(session_id, "Let's review the Delta robot servo calibration.")
    assert ctx1.active_topic == "Robotics & Hardware"
    assert len(ctx1.relevant_memories) > 0
    assert ctx1.token_estimate > 0

    # Turn 2: Topic switch to Career
    ctx2 = context_builder.build_context(session_id, "What companies in Boston do robotics R&D?")
    assert ctx2.active_topic == "Career & Aspirations"
    assert ctx2.debug_trace["previous_topic"] == "Robotics & Hardware"

    # Turn 3: Topic Recovery ("Coming back to what we were discussing...")
    ctx3 = context_builder.build_context(session_id, "Coming back to what we were discussing about servos.")
    assert ctx3.active_topic == "Robotics & Hardware"

    # Turn 4: Explicit recall of past discussion
    ctx4 = context_builder.build_context(session_id, "Remember when we discussed the Delta Robot?")
    assert ctx4.is_recall_query is True
    assert ctx4.recall_found is True
    assert any("delta" in m["content"].lower() for m in ctx4.relevant_memories)

    # Context contains Core Identity
    assert "Yash" in ctx4.core_identity


def test_conversation_compressor():
    """Verify ConversationCompressor extracts summaries and decisions for long chats."""
    session_id = f"test_compress_{uuid.uuid4().hex[:8]}"

    # Save multiple turns
    for i in range(14):
        role = "user" if i % 2 == 0 else "assistant"
        eva_memory_store.save_conversation_turn(
            session_id,
            role,
            f"Turn {i}: We decided to use SQLite FTS5 for offline local memory."
        )

    assert conversation_compressor.should_compress(session_id) is True

    result = conversation_compressor.compress_session(session_id, active_topic="Offline Storage")
    assert result.get("summary") is not None
    assert result["topic"] == "Offline Storage"
    assert len(result["decisions"]) > 0

    # Verify latest session summary query retrieves it
    summary_obj = eva_memory_store.get_latest_session_summary(session_id)
    assert summary_obj is not None
    assert summary_obj["active_topic"] == "Offline Storage"


def test_sensitivity_and_confidence_gating():
    """Verify that high sensitivity memories (S4) are gated out of low-sensitivity requests."""
    s4_id = f"S4.{uuid.uuid4().hex[:6].upper()}"
    s4_mem = MemoryItem(
        memory_id=s4_id,
        category="security",
        content="Critical security master override phrase: SecretOmegaAlpha.",
        confidence=0.99,
        importance=5,
        sensitivity="S4",
        status="current",
        triggers=["override", "secret", "omega"]
    )
    eva_memory_store.insert_memory(s4_mem)

    # Search with max_sensitivity S1 (personal only, not S4 critical)
    results_s1 = eva_memory_store.search_memories(query="SecretOmegaAlpha", max_sensitivity="S1")
    assert not any(r["memory_id"] == s4_id for r in results_s1)

    # Search with max_sensitivity S4
    results_s4 = eva_memory_store.search_memories(query="SecretOmegaAlpha", max_sensitivity="S4")
    assert any(r["memory_id"] == s4_id for r in results_s4)

    # Cleanup
    eva_memory_store.delete_memory(s4_id)


def test_memory_management_rest_endpoints():
    """Verify REST APIs for search, core identity, export, create, update, delete, debug."""
    # 1. Core identity endpoint
    resp_core = client.get("/api/v1/memory/core-identity")
    assert resp_core.status_code == 200
    assert resp_core.json()["success"] is True
    assert "core_identity_card" in resp_core.json()

    # 2. Search endpoint
    resp_search = client.get("/api/v1/memory/search?query=robotics&limit=3")
    assert resp_search.status_code == 200
    assert resp_search.json()["success"] is True
    assert len(resp_search.json()["memories"]) > 0

    # 3. Export endpoint
    resp_export = client.get("/api/v1/memory/export")
    assert resp_export.status_code == 200
    assert resp_export.json()["count"] > 0

    # 4. Create endpoint
    custom_id = f"REST.{uuid.uuid4().hex[:6].upper()}"
    resp_create = client.post("/api/v1/memory/create", json={
        "memory_id": custom_id,
        "category": "project",
        "content": "Designing high-efficiency power distribution board for glasses.",
        "importance": 4,
        "confidence": 0.90,
        "sensitivity": "S1",
        "triggers": ["power", "pcb", "battery"]
    })
    assert resp_create.status_code == 200
    assert resp_create.json()["memory_id"] == custom_id

    # 5. Update endpoint
    resp_update = client.put(f"/api/v1/memory/{custom_id}", json={
        "importance": 5,
        "last_confirmed": "2026-09-24"
    })
    assert resp_update.status_code == 200
    assert resp_update.json()["updated"] is True

    # 6. Context debug endpoint
    resp_debug = client.get(f"/api/v1/memory/context-debug?session_id=debug_sess_1&query=Delta%20robot")
    assert resp_debug.status_code == 200
    assert resp_debug.json()["success"] is True
    assert resp_debug.json()["token_estimate"] > 0

    # 7. Delete endpoint
    resp_delete = client.delete(f"/api/v1/memory/{custom_id}")
    assert resp_delete.status_code == 200
    assert resp_delete.json()["deleted"] is True


@pytest.mark.asyncio
async def test_agent_graph_conversational_continuity():
    """
    Simulates multi-day conversational continuity sequence:
    Day 1: User introduces a project detail.
    Day 2: User asks follow-up referencing 'the project'.
    Day 10: User asks about long-term memory.
    """
    sess_id = f"continuity_{uuid.uuid4().hex[:8]}"

    # Day 1
    resp1 = await run_agent(
        session_id=sess_id,
        user_message="I'm developing the EVA smart-glasses AI assistant.",
        context_payload={},
        language="en",
        locale="en-IN"
    )
    assert resp1["response"] is not None
    assert len(resp1["response"]) > 0

    # Day 2 (User asks what to work on next without re-explaining the project)
    resp2 = await run_agent(
        session_id=sess_id,
        user_message="What should I focus on next for my project?",
        context_payload={},
        language="en",
        locale="en-IN"
    )
    assert resp2["response"] is not None
    # Context builder injected smart-glasses & EVA memory into prompt
    assert len(resp2["response"]) > 0

    # Day 10 (User asks about Delta robot memory)
    resp3 = await run_agent(
        session_id=sess_id,
        user_message="Do you remember the hardware components in my Delta Robot?",
        context_payload={},
        language="en",
        locale="en-IN"
    )
    assert resp3["response"] is not None
    assert len(resp3["response"]) > 0
