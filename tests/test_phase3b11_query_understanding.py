import os
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.schemas import AgentMessageRequest
from backend.app.services.structured_request_parser import structured_request_parser, ParsedIntent
from backend.app.services.smart_glass_formatter import smart_glass_formatter
from backend.app.services.entity_resolver import entity_resolver, ResolutionStatus

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_mock_env(monkeypatch):
    monkeypatch.setenv("USE_MOCK_EMAIL", "1")
    monkeypatch.setenv("USE_MOCK_CALENDAR", "1")

class TestStructuredRequestParser:
    """Tests natural language constraint extraction into structured slots."""

    def test_email_topic_extraction(self):
        req = structured_request_parser.parse("check my mail related to internship")
        assert req.intent == ParsedIntent.EMAIL_SEARCH
        assert req.topic == "internship"

    def test_email_topic_with_temporal(self):
        req = structured_request_parser.parse("find emails about project from last week")
        assert req.intent == ParsedIntent.EMAIL_SEARCH
        assert req.topic == "project"
        assert req.filters.get("date") == "last_week"

    def test_email_sender_entity(self):
        req = structured_request_parser.parse("read the email from LinkedIn")
        assert req.intent == ParsedIntent.EMAIL_READ
        assert req.sender == "linkedin"
        assert req.is_read_content is True

    def test_calendar_temporal_target(self):
        req = structured_request_parser.parse("what is on my calendar tomorrow?")
        assert req.intent == ParsedIntent.CALENDAR_QUERY
        assert req.date_target == "tomorrow"

    def test_calendar_follow_up(self):
        history = [
            {"role": "user", "content": "what do I have on my calendar today?"},
            {"role": "assistant", "content": "You have 1 event today: ML Lecture at 10:30 AM."}
        ]
        req = structured_request_parser.parse("what about tomorrow?", conversation_history=history)
        assert req.intent == ParsedIntent.CALENDAR_QUERY
        assert req.date_target == "tomorrow"
        assert req.is_follow_up is True

    def test_call_controls(self):
        req_call = structured_request_parser.parse("call Rahul Sharma")
        assert req_call.intent == ParsedIntent.CALL_MAKE
        assert req_call.entity == "rahul sharma"

        req_ans = structured_request_parser.parse("answer the call")
        assert req_ans.intent == ParsedIntent.CALL_ANSWER

        req_rej = structured_request_parser.parse("reject call")
        assert req_rej.intent == ParsedIntent.CALL_REJECT

        req_hang = structured_request_parser.parse("hang up")
        assert req_hang.intent == ParsedIntent.CALL_HANGUP

        req_who = structured_request_parser.parse("who is calling?")
        assert req_who.intent == ParsedIntent.CALL_INCOMING_QUERY

    def test_deterministic_math(self):
        req = structured_request_parser.parse("calculate 25 * 4")
        assert req.intent == ParsedIntent.DETERMINISTIC_MATH

    def test_general_knowledge_qa(self):
        req = structured_request_parser.parse("how do I cook a biryani?")
        assert req.intent == ParsedIntent.GENERAL_QA

        req2 = structured_request_parser.parse("how do I tie a shoelace?")
        assert req2.intent == ParsedIntent.GENERAL_QA


class TestSmartGlassFormatter:
    """Tests speakable, 1-3 sentence concise formatting without markdown tables or lists."""

    def test_clean_text(self):
        raw = "### Header\n* Item 1\n* Item 2\nCheck https://example.com for **more** info."
        cleaned = smart_glass_formatter.clean_text_for_speech(raw)
        assert "###" not in cleaned
        assert "*" not in cleaned
        assert "https://" not in cleaned
        assert "**" not in cleaned

    def test_email_search_formatting(self):
        results = [
            {"sender": "careers@internshala.com", "subject": "Internship Shortlist", "snippet": "3 companies shortlisted you"}
        ]
        text = smart_glass_formatter.format_email_search(results, query_topic="internship")
        assert "internship" in text.lower()
        assert "internshala" in text.lower()

    def test_email_search_empty_topic(self):
        text = smart_glass_formatter.format_email_search([], query_topic="internship")
        assert "couldn't find any emails related to internship" in text.lower()

    def test_call_action_formatting(self):
        text = smart_glass_formatter.format_call_action("call_make", "Rahul Sharma", "+919876543210")
        assert "Calling Rahul Sharma" in text
        assert "9 8 7 6 5" in text or "98765" in text


class TestEntityResolver:
    """Tests entity resolution for contacts, ambiguity, and domain mappings."""

    def test_unique_contact_resolution(self):
        res = entity_resolver.resolve_contact("Rahul Sharma")
        assert res.status == ResolutionStatus.RESOLVED
        assert res.contact is not None
        assert res.contact.name == "Rahul Sharma"

    def test_ambiguous_contact_resolution(self):
        res = entity_resolver.resolve_contact("Rahul")
        assert res.status == ResolutionStatus.AMBIGUOUS
        assert len(res.candidates) >= 2
        assert "multiple contacts" in res.clarification_prompt

    def test_domain_resolution(self):
        assert entity_resolver.resolve_domain("linkedin") == "linkedin.com"
        assert entity_resolver.resolve_domain("amazon") == "amazon.in"
        assert entity_resolver.resolve_domain("swiggy") == "swiggy.in"


class TestEndToEndApiRouting:
    """Tests API level queries for Phase 3B.11."""

    def test_api_email_topic_search(self):
        resp = client.post("/api/v1/agent/message", json={
            "session_id": "test_phase3b11",
            "message": "check my mail related to internship"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "internship" in data["response"].lower() or "internshala" in data["response"].lower()
        assert data["metadata"]["fast_path"] is True

    def test_api_calendar_tomorrow(self):
        resp = client.post("/api/v1/agent/message", json={
            "session_id": "test_phase3b11",
            "message": "what is on my calendar tomorrow?"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "tomorrow" in data["response"].lower() or "event" in data["response"].lower()

    def test_api_call_control(self):
        resp = client.post("/api/v1/agent/message", json={
            "session_id": "test_phase3b11",
            "message": "answer the call"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "answering" in data["response"].lower()
        assert len(data["actions"]) == 1
        assert data["actions"][0]["tool_name"] == "call_controller"
        assert data["actions"][0]["tool_input"]["action"] == "call_answer"

    def test_api_deterministic_math(self):
        resp = client.post("/api/v1/agent/message", json={
            "session_id": "test_phase3b11",
            "message": "what is 20 * 5?"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "100" in data["response"]
