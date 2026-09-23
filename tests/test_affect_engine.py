"""
Test Suite for Affect Context Engine, Social Decoupling, HUD Attenuation, and Ethical Guardrails.
Validates slow decay tau, micro-expression noise rejection, user correction,
attenuation rendering matrix, and strict deception refusal.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.emotion.affect_engine import AffectEngine, AffectVector
from backend.app.services.emotion.social_affect_separator import SocialAffectSeparator
from backend.app.services.emotion.attenuation_policy import AttenuationPolicyEngine
from backend.app.services.emotion.ethical_guard import EmotionEthicalGuard, EthicalRefusalError

client = TestClient(app)


class TestAffectDynamicsAndAttenuation:
    """Validates affect vector math, slow time constant persistence, and HUD rendering."""

    def test_slow_decay_and_micro_expression_noise_filtering(self):
        engine = AffectEngine(decay_tau_seconds=240.0, micro_expression_weight=0.15)
        
        # Momentary extreme micro-expression (e.g. sudden smile +1.0)
        instant_affect = engine.update_from_telemetry(instantaneous_valence=1.0, instantaneous_arousal=0.8, source="facial_twitch")
        
        # Due to dampening (w=0.15), running vector should NOT violently jump to 1.0
        assert instant_affect.valence < 0.4
        assert instant_affect.arousal < 0.5

    def test_user_correctable_feedback_loop(self):
        engine = AffectEngine()
        corrected = engine.apply_user_correction(corrected_valence=-0.4, corrected_arousal=0.75)
        assert corrected.valence == -0.4
        assert corrected.arousal == 0.75
        assert "Stressed" in engine.get_affect_summary()

    def test_social_affect_wearer_surround_separation(self):
        separator = SocialAffectSeparator()
        wearer = AffectVector(valence=0.4, arousal=0.2)
        separator.record_surrounding_observation("person_1", "Colleague A", valence=-0.5, arousal=0.8)
        
        summary = separator.get_social_context_summary(wearer)
        # Verify strict delineation
        assert summary["wearer_internal"]["valence"] == 0.4
        assert summary["wearer_internal"]["is_private"] is True
        assert summary["surrounding_environment"]["ambient_room_energy"] == 0.8
        assert len(summary["surrounding_environment"]["individuals"]) == 1

    def test_hud_attenuation_render_policy(self):
        policy_engine = AttenuationPolicyEngine()
        
        # High stress / arousal -> Attenuation should rise, contrast should soften, overlays suppressed
        stressed_affect = AffectVector(valence=-0.3, arousal=0.85)
        render_stressed = policy_engine.compute_render_policy(stressed_affect, active_activity="walking")
        assert render_stressed.contrast_level <= 0.40
        assert render_stressed.allow_non_urgent_notifications is False
        assert render_stressed.glyph_mode == "SILENT_DOT"
        assert render_stressed.active_overlay_layer == "TURN_BY_TURN"
        assert render_stressed.attenuation_level_pct >= 80

        # Calm state -> Ambient layers allowed, high clarity contrast
        calm_affect = AffectVector(valence=0.5, arousal=0.15)
        render_calm = policy_engine.compute_render_policy(calm_affect, active_activity="idle")
        assert render_calm.contrast_level >= 0.85
        assert render_calm.allow_non_urgent_notifications is True
        assert render_calm.glyph_mode == "EXPANDED_ORBIT"


class TestEmotionEthicsAndGuardrails:
    """Validates propose-never-assert and strict refusal of appearance deception."""

    def test_tentative_proposal_generation(self):
        stressed = AffectVector(valence=-0.3, arousal=0.75)
        proposal = EmotionEthicalGuard.generate_tentative_proposal(stressed)
        assert proposal is not None
        assert proposal["type"] == "STRESS_ATTENUATION_PROPOSAL"
        assert "You seem a bit stressed" in proposal["spoken_prompt"]

    def test_refusal_of_appearance_manipulation_and_deception(self):
        # Safe self-directed request
        safe_req = {"intent": "soften_hud_contrast_for_wearer", "target_audience": "wearer"}
        verdict = EmotionEthicalGuard.validate_appearance_mutation_request(safe_req)
        assert verdict["status"] == "AUTHORIZED_SAFE"

        # Malicious / deceptive external appearance request
        deceptive_req = {
            "intent": "alter_external_lens_tint_covertly_to_deceive_police",
            "target_audience": "bystanders"
        }
        with pytest.raises(EthicalRefusalError) as exc_info:
            EmotionEthicalGuard.validate_appearance_mutation_request(deceptive_req)
        assert "ETHICAL VIOLATION REFUSAL" in str(exc_info.value)


class TestEmotionAPIEndpoints:
    """Tests FastAPI emotion and affect endpoints."""

    def test_affect_get_and_telemetry_update(self):
        resp = client.get("/api/v1/emotion/affect")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "wearer_affect" in data
        assert "hud_render_policy" in data

        resp_up = client.post("/api/v1/emotion/telemetry", json={"valence": 0.2, "arousal": 0.3})
        assert resp_up.status_code == 200
        assert resp_up.json()["success"] is True

        resp_corr = client.post("/api/v1/emotion/correct", json={"valence": -0.2, "arousal": 0.6})
        assert resp_corr.status_code == 200
        assert resp_corr.json()["status"] == "USER_GROUNDED"

    def test_appearance_mutation_check_endpoint(self):
        # Safe request -> 200 OK
        resp_safe = client.post("/api/v1/emotion/appearance-mutation-check", json={"intent": "dim_hud_brightness", "target_audience": "wearer"})
        assert resp_safe.status_code == 200

        # Deceptive request -> 403 Forbidden
        resp_deceptive = client.post("/api/v1/emotion/appearance-mutation-check", json={"intent": "fake_expression_to_manipulate_others", "target_audience": "bystanders"})
        assert resp_deceptive.status_code == 403
        assert "ETHICAL VIOLATION REFUSAL" in resp_deceptive.json()["detail"]
