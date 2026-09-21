import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.event_repository import event_repository
from backend.app.services.storage_service import storage_service
from backend.app.services.capability_registry import capability_registry
from backend.app.services.follow_up_resolver import follow_up_resolver
from backend.app.services.conversation_context_engine import ActiveSessionContext

@pytest.fixture
def client():
    return TestClient(app)

def test_capability_registry_endpoint(client):
    resp = client.get("/api/v1/capabilities")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["count"] >= 6
    ids = [c["id"] for c in data["capabilities"]]
    assert "research" in ids
    assert "documents" in ids
    assert "activity_timeline" in ids

def test_capability_registry_filter(client):
    resp = client.get("/api/v1/capabilities?platform=glasses")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    for cap in data["capabilities"]:
        assert cap["available_on_glasses"] is True

def test_document_lifecycle(client):
    # 1. Upload a text document
    file_content = b"# Smart Glasses Research\nLow latency multimodal reasoning and edge perception."
    files = {"file": ("research_notes.md", file_content, "text/markdown")}
    upload_resp = client.post("/api/v1/documents/upload", files=files, data={"source": "test_suite"})
    assert upload_resp.status_code == 200
    upload_data = upload_resp.json()
    assert upload_data["success"] is True
    file_id = upload_data["document"]["file_id"]
    assert upload_data["document"]["filename"] == "research_notes.md"
    assert upload_data["document"]["has_extracted_text"] is True

    # 2. List documents
    list_resp = client.get("/api/v1/documents/list")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["success"] is True
    assert any(d["file_id"] == file_id for d in list_data["documents"])

    # 3. Search document by keyword
    search_resp = client.get("/api/v1/documents/search?query=multimodal")
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert search_data["success"] is True
    assert len(search_data["documents"]) >= 1
    assert search_data["documents"][0]["file_id"] == file_id

    # 4. Get document details
    get_resp = client.get(f"/api/v1/documents/{file_id}")
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["document"]["file_id"] == file_id
    assert "multimodal reasoning" in get_data["document"]["extracted_text"]

    # 5. Download document binary
    dl_resp = client.get(f"/api/v1/documents/{file_id}/download")
    assert dl_resp.status_code == 200
    assert dl_resp.content == file_content

    # 6. Delete document
    del_resp = client.delete(f"/api/v1/documents/{file_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # 7. Confirm 404 after deletion
    get_after_del = client.get(f"/api/v1/documents/{file_id}")
    assert get_after_del.status_code == 404

def test_events_and_sessions_timeline(client):
    # 1. Start a session
    s_resp = client.post("/api/v1/events/session/start", json={"session_id": "test_session_abc"})
    assert s_resp.status_code == 200
    assert s_resp.json()["session_id"] == "test_session_abc"

    # 2. Record custom event
    e_resp = client.post("/api/v1/events/record", json={
        "type": "TEST_ACTION",
        "source": "companion",
        "title": "Ran Test Diagnostics",
        "description": "Verification of telemetry pipeline",
        "session_id": "test_session_abc"
    })
    assert e_resp.status_code == 200
    assert e_resp.json()["success"] is True

    # 3. Fetch timeline
    t_resp = client.get("/api/v1/events/timeline?session_id=test_session_abc")
    assert t_resp.status_code == 200
    t_data = t_resp.json()
    assert t_data["success"] is True
    assert len(t_data["events"]) >= 1

    # 4. End session
    end_resp = client.post("/api/v1/events/session/end", json={
        "session_id": "test_session_abc",
        "summary": "Completed diagnostic run."
    })
    assert end_resp.status_code == 200

    # 5. Get sessions list
    sess_resp = client.get("/api/v1/events/sessions")
    assert sess_resp.status_code == 200
    sess_data = sess_resp.json()
    assert sess_data["success"] is True
    assert any(s["session_id"] == "test_session_abc" for s in sess_data["sessions"])

def test_research_summarize_endpoint(client):
    paper_payload = {
        "title": "Edge-Assisted Multimodal AI for Low-Power Wearable Devices",
        "authors": ["K. Tanaka", "M. Rossi"],
        "publication_year": "2024",
        "abstract": "Techniques for offloading audio and visual processing from resource-constrained microcontrollers.",
        "doi": "10.1145/3639120"
    }

    # Level 2 detail
    l2_resp = client.post("/api/v1/research/summarize", json={"paper": paper_payload, "level": 2})
    assert l2_resp.status_code == 200
    l2_data = l2_resp.json()["result"]
    assert l2_data["level"] == 2
    assert l2_data["zero_hallucination_verified"] is True
    assert "Edge-Assisted" in l2_data["formatted_content"]

    # Level 3 structured summary
    l3_resp = client.post("/api/v1/research/summarize", json={"paper": paper_payload, "level": 3})
    assert l3_resp.status_code == 200
    l3_data = l3_resp.json()["result"]
    assert l3_data["level"] == 3
    assert l3_data["source_basis"] == "verified_abstract"
    assert "Structured Academic Analysis" in l3_data["formatted_content"]

def test_research_follow_up_ordinal_resolution():
    ctx = ActiveSessionContext(session_id="test_sess_followup")
    ctx.active_research = {
        "query": "smart glasses latency",
        "papers": [
            {
                "paper_index": 1,
                "title": "Low-Latency Audio Streaming for ESP32 Wearables",
                "authors": ["Alice Smith", "Bob Jones"],
                "publication_year": "2024",
                "abstract": "Achieving sub-100ms round-trip voice interaction.",
                "doi": "10.1109/TEST.2024.1"
            },
            {
                "paper_index": 2,
                "title": "Optical Waveguides in AR Eyewear",
                "authors": ["Charlie Brown"],
                "publication_year": "2023",
                "abstract": "Diffractive waveguide optics for all-day wear.",
                "doi": "10.1109/TEST.2023.2"
            }
        ]
    }

    # Test "first paper"
    res1 = follow_up_resolver.resolve_research_follow_up("summarize the first paper", ctx)
    assert res1 is not None
    assert res1["action"] == "SUMMARIZE_PAPER"
    assert res1["paper"]["paper_index"] == 1
    assert "Alice Smith" in res1["spoken_response"]

    # Test "who wrote it?"
    res2 = follow_up_resolver.resolve_research_follow_up("who wrote it?", ctx)
    assert res2 is not None
    assert "Alice Smith" in res2["spoken_response"]

    # Test "second one"
    res3 = follow_up_resolver.resolve_research_follow_up("what method did the second paper use?", ctx)
    assert res3 is not None
    assert res3["paper"]["paper_index"] == 2
