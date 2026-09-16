import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.conversation_context_engine import conversation_context_engine
from backend.app.services.follow_up_resolver import follow_up_resolver
from backend.app.services.entity_resolver import entity_resolver, ResolutionStatus

client = TestClient(app)

class TestContactDisambiguation:
    """Tests Google Assistant-style contact disambiguation and follow-up resolution."""

    def test_context_engine_disambiguation_lifecycle(self):
        session_id = "test_disambig_session_1"
        candidates = [
            {"name": "Rahul Sharma", "phone": "+1 555-0101", "type": "mobile"},
            {"name": "Rahul Verma", "phone": "+1 555-0102", "type": "work"}
        ]
        conversation_context_engine.update_contact_disambiguation(
            session_id=session_id,
            action="call",
            candidates=candidates,
            target_query="call Rahul"
        )
        active = conversation_context_engine.get_active_contact_disambiguation(session_id)
        assert active is not None
        assert active["action"] == "call"
        assert len(active["candidates"]) == 2

        # Clear disambiguation
        conversation_context_engine.clear_contact_disambiguation(session_id)
        assert conversation_context_engine.get_active_contact_disambiguation(session_id) is None

    def test_follow_up_resolver_ordinal_first(self):
        session_id = "test_disambig_session_2"
        candidates = [
            {"name": "Rahul Sharma", "phone": "+1 555-0101", "type": "mobile"},
            {"name": "Rahul Verma", "phone": "+1 555-0102", "type": "work"}
        ]
        conversation_context_engine.update_contact_disambiguation(
            session_id=session_id,
            action="call",
            candidates=candidates,
            target_query="call Rahul"
        )

        res = follow_up_resolver.resolve(
            session_id=session_id,
            message="the first one"
        )
        assert res.is_follow_up is True
        assert res.target_capability == "contact"
        assert res.resolved_parameters.get("contact") == "Rahul Sharma"
        assert res.resolved_parameters.get("phone") == "+1 555-0101"
        assert "Calling Rahul Sharma" in res.direct_answer

    def test_follow_up_resolver_name_selection(self):
        session_id = "test_disambig_session_3"
        candidates = [
            {"name": "Rahul Sharma", "phone": "+1 555-0101", "type": "mobile"},
            {"name": "Rahul Verma", "phone": "+1 555-0102", "type": "work"}
        ]
        conversation_context_engine.update_contact_disambiguation(
            session_id=session_id,
            action="call",
            candidates=candidates,
            target_query="call Rahul"
        )

        res = follow_up_resolver.resolve(
            session_id=session_id,
            message="Rahul Verma"
        )
        assert res.is_follow_up is True
        assert res.target_capability == "contact"
        assert res.resolved_parameters.get("contact") == "Rahul Verma"
        assert "Calling Rahul Verma" in res.direct_answer

    def test_follow_up_resolver_type_selection(self):
        session_id = "test_disambig_session_4"
        candidates = [
            {"name": "Dr. Sarah Jenkins", "phone": "+1 555-0188", "relationship": "mobile", "notes": "mobile"},
            {"name": "Dr. Sarah Jenkins", "phone": "+1 555-0189", "relationship": "work", "notes": "work"}
        ]
        conversation_context_engine.update_contact_disambiguation(
            session_id=session_id,
            action="sms",
            candidates=candidates,
            target_query="text Dr Sarah saying I have arrived",
            body="I have arrived"
        )

        res = follow_up_resolver.resolve(
            session_id=session_id,
            message="work"
        )
        assert res.is_follow_up is True
        assert res.target_capability == "sms"
        assert res.resolved_parameters.get("phone") == "+1 555-0189"
        assert res.resolved_parameters.get("body") == "I have arrived"

class TestWorkspaceEnvironmentAPI:
    """Tests Workspace Environment API endpoints and Web Console rendering."""

    def test_workspace_environment_endpoint(self):
        resp = client.get("/api/v1/workspace/environment")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        assert "environment" in data
        assert "models" in data
        assert "connectors" in data
        assert "custom_ui_links" in data
        assert len(data["custom_ui_links"]) >= 4

    def test_telemetry_insights_endpoint(self):
        resp = client.get("/api/v1/telemetry/insights")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        assert "average_latency_ms" in data
        assert "fast_path_ratio_pct" in data

    def test_web_console_contains_workspace_tab(self):
        resp = client.get("/web")
        assert resp.status_code == 200
        content = resp.text
        assert "view-workspace" in content
        assert "Workspace & Environment" in content
        assert "side-telemetry-panel" in content
        assert "loadWorkspaceEnvironment" in content
