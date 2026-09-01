import pytest
from backend.app.services.llm_router import llm_router

def test_prompt_compaction_trims_large_messages():
    """Verify prompt compaction reduces message history and clips oversized texts."""
    oversized_messages = [
        {"role": "system", "content": "You are a very long and detailed system prompt..." * 20},
        {"role": "user", "content": "Old message 1 " * 50},
        {"role": "assistant", "content": "Old response 1 " * 50},
        {"role": "user", "content": "Old message 2 " * 50},
        {"role": "assistant", "content": "Old response 2 " * 50},
        {"role": "user", "content": "Current question " * 40}
    ]

    compacted = llm_router.compact_messages(oversized_messages)

    assert len(compacted) <= 4  # System + last 3 turns max
    assert any(m["role"] == "system" for m in compacted)
    for m in compacted:
        if m["role"] != "system":
            assert len(m["content"]) <= 320  # Max 300 + suffix
