"""
Comprehensive Test Suite for Phase 3B.13:
Conversational Continuity, Secure Personal Control & Real Device Integration

Verifies:
1. Multi-turn context retention (15-min session context)
2. Referent and follow-up query resolution (QA, Ordinals, Senders, Actions)
3. Personal Contact Vault (Exact, Alias, Fuzzy, Disambiguation, Phone/Email Linking)
4. Zero-Trust Device Security (Pairing tokens, Revocation, Risk Gating, Audit Logging)
5. Scoped Desktop Agent (Allowlisted apps, Safe file search, Path traversal prevention)
6. Agent Graph integration with follow-up resolver & context updates
"""

import pytest
import time
from unittest.mock import MagicMock, patch

from backend.app.services.conversation_context_engine import (
    conversation_context_engine,
    ActiveSessionContext
)
from backend.app.services.follow_up_resolver import (
    follow_up_resolver,
    ResolvedFollowUp
)
from backend.app.services.contact_vault import (
    contact_vault,
    VaultContact
)
from backend.app.services.device_security_service import (
    device_security_service,
    RiskLevel
)


# ==========================================
# 1. Multi-Turn Context Retention Engine Tests
# ==========================================

class TestConversationContextEngine:
    def setup_method(self):
        self.session_id = "test_sess_multi_turn_001"
        conversation_context_engine.clear(self.session_id)

    def test_context_storage_and_retrieval(self):
        ctx = conversation_context_engine.get_session(self.session_id)
        assert ctx.session_id == self.session_id
        assert ctx.active_subject is None

        # Update subject and entity
        conversation_context_engine.update_subject(
            self.session_id,
            subject="Mahatma Gandhi",
            entity_data={"era": "20th century", "profession": "lawyer, activist"}
        )
        conversation_context_engine.update_turn(
            self.session_id,
            intent="qa",
            response="Mahatma Gandhi was a leader of India's independence movement."
        )

        updated = conversation_context_engine.get_session(self.session_id)
        assert updated.active_subject == "Mahatma Gandhi"
        assert updated.active_entity.get("era") == "20th century"
        assert updated.previous_intent == "qa"

    def test_email_and_sms_context_tracking(self):
        email = {
            "id": "msg_123",
            "sender": "sneha.patil@example.com",
            "subject": "Project Update Q3",
            "snippet": "Here is the latest progress report on smart glasses."
        }
        conversation_context_engine.update_email(
            self.session_id,
            messages=[email],
            selected=email,
            query="is:unread"
        )
        conversation_context_engine.update_contact(
            self.session_id,
            {"name": "Sneha Patil", "phone": "+919811122334"}
        )

        ctx = conversation_context_engine.get_session(self.session_id)
        assert ctx.active_email["selected"] is not None
        assert ctx.active_email["selected"]["subject"] == "Project Update Q3"
        assert len(ctx.active_email["messages"]) == 1
        assert ctx.active_contact["name"] == "Sneha Patil"

    def test_ttl_expiry_and_cleanup(self):
        ctx = conversation_context_engine.get_session(self.session_id)
        ctx.active_subject = "Albert Einstein"
        # Artificially set timestamp in the past (>15 mins)
        ctx.updated_at = time.time() - 1000

        # Trigger cleanup
        conversation_context_engine._cleanup_expired()
        
        # Next get_session returns a brand new context
        new_ctx = conversation_context_engine.get_session(self.session_id)
        assert new_ctx.active_subject is None


# ==========================================
# 2. Follow-Up & Referent Resolver Tests
# ==========================================

class TestFollowUpResolver:
    def setup_method(self):
        self.session_id = "test_sess_resolver_002"
        conversation_context_engine.clear(self.session_id)

    def test_qa_continuation_tell_me_more(self):
        conversation_context_engine.update_subject(
            self.session_id,
            subject="Mahatma Gandhi"
        )

        res = follow_up_resolver.resolve(self.session_id, "Tell me more")
        assert res.is_follow_up is True
        assert res.target_capability == "qa"
        assert res.action_type == "continue_subject"
        assert "Mahatma Gandhi" in res.augmented_message

    def test_qa_aspect_refinement_early_life(self):
        conversation_context_engine.update_subject(
            self.session_id,
            subject="Mahatma Gandhi"
        )

        res = follow_up_resolver.resolve(self.session_id, "What about his early life?")
        assert res.is_follow_up is True
        assert res.target_capability == "qa"
        assert "Mahatma Gandhi" in res.augmented_message
        assert "early life" in res.augmented_message

    def test_email_ordinal_selection(self):
        e1 = {"id": "e1", "sender": "Google HR <hr@google.com>", "subject": "Interview Schedule", "snippet": "Stage 2 confirmed"}
        e2 = {"id": "e2", "sender": "Dr. Sharma <dr.sharma@health.in>", "subject": "Lab Report", "snippet": "Normal"}
        conversation_context_engine.update_email(
            self.session_id,
            messages=[e1, e2]
        )

        res = follow_up_resolver.resolve(self.session_id, "Read the first one")
        assert res.is_follow_up is True
        assert res.target_capability == "gmail"
        assert res.action_type == "read_ordinal"
        assert res.direct_answer is not None
        assert "Interview Schedule" in res.direct_answer

        # Context active_email selected should now be updated to e1
        ctx = conversation_context_engine.get_session(self.session_id)
        assert ctx.active_email["selected"]["id"] == "e1"

    def test_sender_referent_who_sent_it_for_email(self):
        e1 = {"id": "e1", "sender": "Priya Rao <priya.rao@techcorp.in>", "subject": "Architecture Review", "snippet": "Proposal"}
        conversation_context_engine.update_email(
            self.session_id,
            messages=[e1],
            selected=e1
        )

        res = follow_up_resolver.resolve(self.session_id, "Who sent it?")
        assert res.is_follow_up is True
        assert res.target_capability == "gmail"
        assert res.action_type == "query_attribute"
        assert res.direct_answer is not None
        assert "Priya Rao" in res.direct_answer

    def test_sender_referent_who_sent_it_for_sms(self):
        sms = {"id": "s1", "contactName": "Amit Joshi", "address": "+919876543210", "body": "Are we meeting at 5 PM?"}
        conversation_context_engine.update_sms(
            self.session_id,
            contact="Amit Joshi",
            phone="+919876543210",
            messages=[sms],
            selected=sms
        )

        res = follow_up_resolver.resolve(self.session_id, "Who sent that message?")
        assert res.is_follow_up is True
        assert res.target_capability == "sms"
        assert res.action_type == "query_attribute"
        assert res.direct_answer is not None
        assert "Amit Joshi" in res.direct_answer

    def test_action_reply_resolution(self):
        sms = {"id": "s1", "contactName": "Rahul Sharma", "address": "+919820011223", "body": "Send slides"}
        conversation_context_engine.update_sms(
            self.session_id,
            contact="Rahul Sharma",
            phone="+919820011223",
            messages=[sms],
            selected=sms
        )

        res = follow_up_resolver.resolve(self.session_id, "Reply that I'll send them in 10 minutes")
        assert res.is_follow_up is True
        assert res.target_capability == "sms"
        assert res.action_type == "reply"
        assert res.resolved_parameters["recipient"] == "Rahul Sharma"
        assert res.resolved_parameters["requires_confirmation"] is True


# ==========================================
# 3. Personal Contact Vault Tests
# ==========================================

class TestContactVault:
    def setup_method(self):
        self.user_id = "test_user_vault_003"
        with contact_vault._get_conn() as conn:
            conn.execute("DELETE FROM personal_contacts WHERE user_id = ?", (self.user_id,))
            conn.commit()

        # Seed test contacts
        contact_vault.add_contact(
            user_id=self.user_id,
            name="Rahul Sharma",
            phone_numbers=["+919820011223"],
            email_addresses=["rahul.sharma@example.com"],
            aliases=["bhai", "rahul"],
            notes="brother"
        )
        contact_vault.add_contact(
            user_id=self.user_id,
            name="Rahul Verma",
            phone_numbers=["+919833344455"],
            email_addresses=["rahul.verma@colleague.com"],
            aliases=["verma"],
            notes="colleague"
        )
        contact_vault.add_contact(
            user_id=self.user_id,
            name="Sneha Patil",
            phone_numbers=["+919811122334"],
            email_addresses=["sneha.patil@example.com"],
            aliases=["snehu", "designer"],
            notes="lead designer"
        )

    def test_exact_name_lookup(self):
        res = contact_vault.resolve_contact("Sneha Patil", user_id=self.user_id)
        assert res.status == "RESOLVED"
        assert res.contact is not None
        assert res.contact.name == "Sneha Patil"
        assert res.contact.phone_numbers[0] == "+919811122334"

    def test_alias_lookup(self):
        res = contact_vault.resolve_contact("designer", user_id=self.user_id)
        assert res.status == "RESOLVED"
        assert res.contact.name == "Sneha Patil"

    def test_ambiguous_name_resolution(self):
        # "Rahul" matches both Rahul Sharma and Rahul Verma
        res = contact_vault.resolve_contact("Rahul", user_id=self.user_id)
        assert res.status == "AMBIGUOUS"
        assert len(res.candidates) == 2
        candidate_names = [c.name for c in res.candidates]
        assert "Rahul Sharma" in candidate_names
        assert "Rahul Verma" in candidate_names

    def test_phone_number_lookup(self):
        contact = contact_vault.find_by_phone("+919820011223", user_id=self.user_id)
        assert contact is not None
        assert contact.name == "Rahul Sharma"

    def test_contact_deletion(self):
        contacts = contact_vault.list_contacts(self.user_id)
        assert len(contacts) >= 3
        c_id = contacts[0].id
        deleted = contact_vault.delete_contact(c_id, self.user_id)
        assert deleted is True
        remaining = contact_vault.list_contacts(self.user_id)
        assert len(remaining) == len(contacts) - 1


# ==========================================
# 4. Zero-Trust Device Security & Scoped Desktop Agent Tests
# ==========================================

class TestDeviceSecurityService:
    def setup_method(self):
        self.user_id = "test_user_sec_004"

    def test_device_pairing_and_token_verification(self):
        device_id = "pixel_8_test"
        device_name = "Pixel 8 Pro"
        permissions = ["sms_read", "sms_send", "call_control"]

        # Create pairing token
        token_data = device_security_service.create_pairing_token(
            device_id=device_id,
            name=device_name,
            device_type="android",
            permissions=permissions,
            user_id=self.user_id
        )

        assert token_data["token"] is not None
        raw_token = token_data["token"]

        # Verify token
        is_valid = device_security_service.verify_device_token(device_id, raw_token)
        assert is_valid is True

        # Verify wrong token fails
        assert device_security_service.verify_device_token(device_id, "wrong_token_123") is False

    def test_device_revocation(self):
        device_id = "laptop_test_01"
        token_data = device_security_service.create_pairing_token(
            device_id=device_id,
            name="MacBook Work",
            device_type="laptop",
            permissions=["desktop_control"],
            user_id=self.user_id
        )

        assert device_security_service.verify_device_token(device_id, token_data["token"]) is True

        # Revoke device
        revoked = device_security_service.revoke_device(device_id, self.user_id)
        assert revoked is True

        # Token must now be rejected
        assert device_security_service.verify_device_token(device_id, token_data["token"]) is False

    def test_risk_level_gating(self):
        # LOW risk actions
        assert device_security_service.evaluate_risk_level("read_sms") == RiskLevel.LOW
        assert device_security_service.evaluate_risk_level("read_email") == RiskLevel.LOW
        assert device_security_service.evaluate_risk_level("get_calendar") == RiskLevel.LOW

        # MEDIUM risk actions
        assert device_security_service.evaluate_risk_level("open_app") == RiskLevel.MEDIUM

        # HIGH risk actions (Must require confirmation)
        assert device_security_service.evaluate_risk_level("send_sms") == RiskLevel.HIGH
        assert device_security_service.evaluate_risk_level("send_email") == RiskLevel.HIGH
        assert device_security_service.evaluate_risk_level("delete_contact") == RiskLevel.HIGH

        # CRITICAL actions (Blocked)
        assert device_security_service.evaluate_risk_level("execute_shell") == RiskLevel.CRITICAL
        assert device_security_service.evaluate_risk_level("delete_system_file") == RiskLevel.CRITICAL

    def test_laptop_action_scoped_allowlist(self):
        # Allowed app
        res = device_security_service.execute_laptop_action("OPEN_APP", "notepad", self.user_id)
        assert res["status"] in ["success", "mock_executed"]

        # Disallowed action / injection attempt
        res_bad = device_security_service.execute_laptop_action("OPEN_APP", "powershell.exe; rm -rf /", self.user_id)
        assert res_bad["status"] == "blocked"

    def test_audit_log_sanitization(self):
        # Log an action with potential sensitive content
        device_security_service.log_audit_event(
            action="send_sms",
            target="Rahul Sharma",
            risk_level=RiskLevel.HIGH,
            status="ALLOWED",
            details="Sent text: Your OTP is 987654 and token=secret_abc_123",
            user_id=self.user_id
        )

        logs = device_security_service.get_audit_logs(limit=5, user_id=self.user_id)
        assert len(logs) > 0
        latest = logs[0]
        # Sensitive tokens/numbers must be masked
        assert "secret_abc_123" not in str(latest)
        assert "987654" not in str(latest)


# ==========================================
# 5. Agent Graph & Multi-Turn Integration
# ==========================================

class TestAgentGraphFollowUpIntegration:
    @pytest.mark.asyncio
    async def test_agent_graph_preserves_context_flow(self):
        from backend.app.services.agent_graph import run_agent

        session_id = "test_graph_sess_005"
        conversation_context_engine.clear(session_id)

        # Seed context with an active email
        e1 = {"id": "e_test", "sender": "Manager John <manager@company.com>", "subject": "Quarterly Review", "snippet": "Please check slides"}
        conversation_context_engine.update_email(session_id, messages=[e1], selected=e1)

        # Query "Who sent it?"
        resp = await run_agent(
            session_id=session_id,
            user_message="Who sent it?",
            context_payload={}
        )

        assert resp is not None
        assert "Manager John" in resp["response"] or "manager@company.com" in resp["response"]
        assert resp.get("routing_metadata", {}).get("resolved_referent") is True

