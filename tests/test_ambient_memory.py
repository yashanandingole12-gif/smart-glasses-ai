"""
Test Suite for Ambient-First Perception Buffer & Cognitive Memory Engine.
Validates sub-second discard, salience gate thresholding, rolling working memory,
temporal knowledge graph relations, and sleep consolidation.
"""
import pytest
import time
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.perception.perception_buffer import PerceptionBuffer, RawSensorSnapshot, PerceptionEvent
from backend.app.services.perception.event_encoder import TinyEventEncoder
from backend.app.services.memory.salience_gate import SalienceGate
from backend.app.services.memory.working_memory_engine import WorkingMemoryEngine
from backend.app.services.memory.temporal_graph_store import TemporalGraphStore
from backend.app.services.memory.sleep_consolidation import SleepConsolidationEngine

client = TestClient(app)


class TestPerceptionBufferAndEncoder:
    """Validates high-frequency ephemeral buffering and event classification."""

    def test_perception_buffer_ephemeral_ttl_discard(self):
        buf = PerceptionBuffer(max_buffer_size=10, ttl_seconds=0.1)
        # Push raw sensor snapshot with image frame
        snap = RawSensorSnapshot(has_image_frame=True, audio_rms_energy=0.3)
        buf.push_snapshot(snap)
        assert len(buf.buffer) == 1

        # Wait for TTL expiry
        time.sleep(0.15)
        snap2 = RawSensorSnapshot(has_image_frame=True, audio_rms_energy=0.1)
        buf.push_snapshot(snap2)

        # Older frame should be purged immediately (zero-pixel persistence)
        stats = buf.get_telemetry_stats()
        assert stats["discarded_raw_frames"] >= 1
        assert stats["privacy_mode"] == "ZERO_PIXEL_PERSISTENCE"

    def test_tiny_event_encoder_emits_discrete_events(self):
        encoder = TinyEventEncoder()
        snap = RawSensorSnapshot(
            audio_vad_active=True,
            audio_rms_energy=0.75,
            imu_angular_velocity=[0.0, 0.0, 110.0],
            gaze_vector=[0.0, 0.0, 0.95]
        )
        entities = [{"label": "PERSON", "name": "Prof. Rao", "distance_m": 1.2}]
        events = encoder.encode_events([snap], entities)

        types = [e.event_type for e in events]
        assert "WEARER_SPEAKING" in types
        assert "RAPID_HEAD_TURN" in types
        assert "GAZE_STABLE_FOCUS" in types
        assert "PERSON_APPROACHING" in types


class TestCognitiveMemoryArchitecture:
    """Validates salience gate, working memory fresh assembly, and temporal graph."""

    def test_salience_gate_filtering(self):
        gate = SalienceGate(salience_threshold=0.55)
        evt_ambient = PerceptionEvent(event_type="AMBIENT_BACKGROUND_HUM", confidence=0.5)
        # Ambient low-arousal event should NOT breach gate
        assert gate.should_promote(evt_ambient, active_task_context="idle", wearer_arousal=0.1) is False

        # Highly relevant novel person event in active conversation context SHOULD breach gate
        evt_person = PerceptionEvent(
            event_type="PERSON_APPROACHING",
            confidence=0.95,
            metadata={"name": "Dr. Sarah", "distance_m": 1.1}
        )
        assert gate.should_promote(evt_person, active_task_context="conversation", wearer_arousal=0.6) is True

    def test_working_memory_fresh_turn_assembly(self):
        wm = WorkingMemoryEngine()
        wm.current_location = "Mumbai Central Metro Station"
        wm.active_interlocutors = ["Aarav"]
        wm.active_visual_target = "Platform 3 Express to Churchgate"
        wm.record_dialogue_turn("user", "Which train is arriving next?")
        wm.record_dialogue_turn("assistant", "The 18:45 Fast Local to Churchgate on Platform 3.")

        context_str = wm.assemble_fresh_turn_context(
            query="Is it on time?",
            relevant_long_term_facts=["User prefers express coaches"],
            wearer_affect_summary="Focused / Neutral Baseline"
        )

        assert "Mumbai Central Metro Station" in context_str
        assert "Aarav" in context_str
        assert "Platform 3 Express" in context_str
        assert "Temporal LTM: User prefers express coaches" in context_str
        assert "Affect Context: Focused / Neutral Baseline" in context_str

    def test_temporal_graph_superseding_facts(self):
        graph = TemporalGraphStore()
        # Insert initial fact
        edge1 = graph.insert_fact(
            subject="wearer",
            predicate="dietary_preference",
            object="omnivore",
            source_context="initial_intake"
        )
        assert edge1.valid_to is None

        # Supersede with new preference
        edge2 = graph.supersede_fact(
            subject="wearer",
            predicate="dietary_preference",
            new_object="vegan",
            transition_context="lifestyle change"
        )
        assert edge1.valid_to is not None
        assert edge2.valid_to is None

        history = graph.query_entity_history("wearer")
        assert len(history) == 2
        active_facts = graph.query_relevant_facts("dietary preference", active_only=True)
        assert len(active_facts) == 1
        assert "vegan (currently)" in active_facts[0]

    def test_sleep_consolidation_cycle(self):
        wm = WorkingMemoryEngine()
        graph = TemporalGraphStore()
        wm.current_location = "Shivaji Park Cafe"
        wm.active_interlocutors = ["Priya"]

        consolidator = SleepConsolidationEngine(wm, graph)
        res = consolidator.run_consolidation_cycle()

        assert res["status"] == "CONSOLIDATED_SUCCESS"
        assert res["cycle_index"] == 1
        assert len(res["consolidated_items"]) >= 2
        history = graph.query_entity_history("wearer")
        assert len(history) >= 2


class TestAmbientMemoryAPIEndpoints:
    """Tests FastAPI endpoints for perception buffer and working memory."""

    def test_perception_snapshot_and_memory_flow_api(self):
        payload = {
            "has_image_frame": True,
            "audio_rms_energy": 0.70,
            "audio_vad_active": True,
            "imu_angular_velocity": [15.0, 5.0, 10.0],
            "gaze_vector": [0.0, 0.0, 0.95],
            "detected_entities": [{"label": "PERSON", "name": "Karan", "distance_m": 1.2}]
        }
        resp = client.post("/api/v1/perception/snapshot", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["emitted_events"]) >= 1

        # Check working memory state endpoint
        resp_wm = client.get("/api/v1/memory/working")
        assert resp_wm.status_code == 200
        assert resp_wm.json()["success"] is True

        # Check fresh context assembly endpoint
        resp_ctx = client.post("/api/v1/memory/assemble-context", json={"query": "Hello"})
        assert resp_ctx.status_code == 200
        assert "assembled_prompt_context" in resp_ctx.json()

        # Check sleep consolidation endpoint
        resp_cons = client.post("/api/v1/memory/consolidate")
        assert resp_cons.status_code == 200
        assert resp_cons.json()["consolidation"]["status"] == "CONSOLIDATED_SUCCESS"
