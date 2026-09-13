import pytest
import os
from unittest.mock import patch, MagicMock
from backend.app.services.math_engine import DeterministicMathEngine, math_engine
from backend.app.services.google_contacts_service import GoogleContactsService, google_contacts_service
from backend.app.services.contact_vault import PersonalContactVault, contact_vault
from backend.app.services.conversation_context_engine import ConversationContextEngine, conversation_context_engine
from backend.app.services.follow_up_resolver import FollowUpResolver, follow_up_resolver
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

# ============================================================================
# 1. DETERMINISTIC MATH ENGINE TESTS
# ============================================================================

def test_math_linear_equation_target():
    """Test the target linear equation 45.2x + 1916029.9888 = 0 -> x approx -42390.044."""
    res = math_engine.evaluate("45.2x + 1916029.9888 = 0")
    assert res is not None
    assert res["operation"] == "linear_equation"
    assert res["variable"] == "x"
    assert abs(res["result"] - (-42390.044)) < 0.01
    assert "x is approximately -42390.044" in res["text_response"]
    assert len(res["steps"]) >= 3
    # Verify zero LaTeX in text_response
    assert "\\" not in res["text_response"]
    assert "$" not in res["text_response"]


def test_math_spoken_linear_equation():
    """Test spoken representation: '45.2 x plus 1916029.9888 equals zero'."""
    res = math_engine.evaluate("45.2 x plus 1916029.9888 equals zero")
    assert res is not None
    assert res["operation"] == "linear_equation"
    assert res["variable"] == "x"
    assert abs(res["result"] - (-42390.044)) < 0.01


def test_math_spoken_parentheses():
    """Test spoken brackets: 'what is open bracket 2 plus 3 close bracket times 4'."""
    res = math_engine.evaluate("what is open bracket 2 plus 3 close bracket times 4")
    assert res is not None
    assert res["result"] == 20.0
    assert "20" in res["text_response"]


def test_math_algebra_standard():
    """Test standard algebra 'what is x if 2x + 5 = 15'."""
    res = math_engine.evaluate("what is x if 2x + 5 = 15")
    assert res is not None
    assert res["operation"] == "linear_equation"
    assert res["variable"] == "x"
    assert res["result"] == 5.0
    assert "x equals 5" in res["text_response"]


def test_math_arithmetic_order_of_operations():
    """Test arithmetic with parentheses and order of operations."""
    res = math_engine.evaluate("12 * (5 + 3) / 2")
    assert res is not None
    assert res["result"] == 48.0


def test_math_percentages_and_powers():
    """Test percentage and power evaluations."""
    res_pct = math_engine.evaluate("15% of 800")
    assert res_pct is not None
    assert res_pct["result"] == 120.0

    res_pow = math_engine.evaluate("2 ^ 10")
    assert res_pow is not None
    assert res_pow["result"] == 1024.0


def test_math_fractions():
    """Test fraction arithmetic."""
    res = math_engine.evaluate("3/4 + 1/2")
    assert res is not None
    assert abs(res["result"] - 1.25) < 1e-6 or res["result"] == 1.25


# ============================================================================
# 2. CONVERSATIONAL CONTINUITY & MATH FOLLOW-UPS
# ============================================================================

def test_math_follow_up_steps_and_answers():
    """Test multi-turn context preservation for math questions."""
    session_id = "test_math_session_phase3b13"
    ctx_engine = ConversationContextEngine()

    # Step 1: Evaluate equation
    eval_res = math_engine.evaluate("45.2x + 1916029.9888 = 0")
    assert eval_res is not None

    ctx_engine.update_calculation(
        session_id=session_id,
        expression=eval_res["equation"],
        result=eval_res["result"],
        variable=eval_res["variable"],
        approx_result=eval_res["approx_result"],
        steps=eval_res["steps"],
        solution_display=eval_res["solution_display"],
        text_response=eval_res["text_response"],
        raw_query="45.2x + 1916029.9888 = 0"
    )

    # Patch active conversation context engine for resolver
    with patch("backend.app.services.follow_up_resolver.conversation_context_engine", ctx_engine):
        # Follow-up 1: "Show the steps"
        res_steps = follow_up_resolver.resolve(session_id, "Show the steps")
        assert res_steps.is_follow_up is True
        assert res_steps.target_capability == "calculation"
        assert res_steps.action_type == "continue_subject"
        assert "Equation:" in res_steps.direct_answer
        assert "Divide by coefficient:" in res_steps.direct_answer

        # Follow-up 2: "Just give me the answer"
        res_ans = follow_up_resolver.resolve(session_id, "Just give me the answer")
        assert res_ans.is_follow_up is True
        assert res_ans.target_capability == "calculation"
        assert "-42390.044" in res_ans.direct_answer

        # Follow-up 3: "What is x?"
        res_var = follow_up_resolver.resolve(session_id, "What is x?")
        assert res_var.is_follow_up is True
        assert "-42390.044" in res_var.direct_answer


# ============================================================================
# 3. GOOGLE CONTACTS & CONTACT VAULT DEDUPLICATION
# ============================================================================

def test_google_contacts_normalization():
    """Test Google People API response parsing and multi-field normalization."""
    mock_people_person = {
        "resourceName": "people/c123456",
        "names": [{"displayName": "Dr. Ananya Sharma", "givenName": "Ananya", "familyName": "Sharma"}],
        "nicknames": [{"value": "Anu"}],
        "phoneNumbers": [
            {"value": "+91 98765 43210", "type": "mobile"},
            {"value": "022 1234 5678", "type": "work"}
        ],
        "emailAddresses": [
            {"value": "ananya.sharma@example.com", "type": "work"},
            {"value": "anu99@gmail.com", "type": "home"}
        ],
        "organizations": [{"name": "AI Health Labs", "title": "Lead Scientist"}]
    }

    normalized = google_contacts_service.normalize_person_data(mock_people_person)
    assert normalized is not None
    assert normalized["name"] == "Dr. Ananya Sharma"
    assert "Anu" in normalized["aliases"]
    assert "+919876543210" in normalized["phone_numbers"]
    assert "ananya.sharma@example.com" in normalized["email_addresses"]
    assert normalized["organization"] == "AI Health Labs"
    assert normalized["job_title"] == "Lead Scientist"


def test_contact_vault_safe_deduplication():
    """Test that Contact Vault merges same-identifier contacts but preserves different people with common names."""
    db_file = "backend/data/test_contact_vault_phase3b13.db"
    if os.path.exists(db_file):
        os.remove(db_file)
    vault = PersonalContactVault(db_path=db_file)
    try:
        # Clear seeded defaults for pure isolated test
        with vault._get_conn() as conn:
            conn.execute("DELETE FROM personal_contacts")
            conn.commit()

        # 1. Add Rahul Verma
        vault.add_contact(
            user_id="default_user",
            name="Rahul Verma",
            phone_numbers=["+919800000001"],
            email_addresses=["rahul.verma@example.com"],
            notes="Work Colleague"
        )

        # 2. Add Rahul Sharma (different phone, different email -> MUST NOT MERGE)
        vault.add_contact(
            user_id="default_user",
            name="Rahul Sharma",
            phone_numbers=["+919800000002"],
            email_addresses=["rahul.sharma@example.com"],
            notes="Gym Buddy"
        )

        contacts = vault.list_contacts()
        assert len(contacts) == 2

        # 3. Sync Google Contacts with an updated phone for Rahul Verma (MUST MERGE WITH RAHUL VERMA)
        google_sync_data = [
            {
                "name": "Rahul Verma",
                "aliases": ["RV"],
                "phone_numbers": ["+919800000001", "+919800000099"],
                "email_addresses": ["rahul.verma@example.com"],
                "organization": "Verma Enterprises",
                "job_title": "Director"
            }
        ]
        sync_res = vault.sync_google_contacts(google_sync_data, user_id="default_user")
        assert len(sync_res) == 2

        contacts_after = vault.list_contacts()
        assert len(contacts_after) == 2  # No duplicate Rahul created

        rv = next(c for c in contacts_after if c.name == "Rahul Verma")
        assert "+919800000099" in rv.phone_numbers
        assert rv.company == "Verma Enterprises"
    finally:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
            except Exception:
                pass


# ============================================================================
# 4. API ENDPOINTS & ESP32 DIAGNOSTICS TESTS
# ============================================================================

def test_api_math_evaluate_endpoint():
    """Test POST /api/v1/math/evaluate endpoint."""
    res = client.post("/api/v1/math/evaluate", json={"query": "45.2x + 1916029.9888 = 0"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["operation"] == "linear_equation"
    assert abs(data["data"]["result"] - (-42390.044)) < 0.01


def test_api_esp32_diagnostic_endpoint():
    """Test GET /api/v1/hardware/esp32/diagnostic endpoint."""
    res = client.get("/api/v1/hardware/esp32/diagnostic")
    assert res.status_code == 200
    data = res.json()
    assert data["board"] == "Seeed XIAO ESP32-S3 Sense"
    assert data["camera"]["sensor"] == "OV2640"
    assert data["microphone"]["sensor"] == "MSM261D (PDM Digital)"
    assert data["diagnostics_ready"] is True


def test_api_contacts_endpoint():
    """Test GET /api/v1/contacts endpoint."""
    res = client.get("/api/v1/contacts")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert isinstance(data["contacts"], list)
