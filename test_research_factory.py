import sqlite3
import tempfile
import unittest
from pathlib import Path

from factory_experiment import ResearchFactory, init_db, persist


class ResearchFactoryTests(unittest.TestCase):
    def test_step_emits_one_event_per_department_and_moves_state(self):
        factory = ResearchFactory()
        result = factory.step("full", "normal")
        self.assertEqual(len(result["events"]), 10)
        self.assertEqual(factory.state.cycle, 1)
        self.assertTrue(all("context_confidence" in event for event in result["events"]))

    def test_packet_loss_reduces_context_availability(self):
        factory = ResearchFactory()
        for _ in range(120):
            factory.step("full", "packet_loss")
        lost = [event for event in factory.events if event["packet_lost"]]
        self.assertGreater(len(lost), 0)
        self.assertTrue(all(event["wearable_context_used"] == 0 for event in lost))

    def test_persistence_is_idempotent_for_realtime_steps(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = Path(directory) / "factory.sqlite"
            factory = ResearchFactory()
            factory.step("physiology", "normal")
            persist(factory, db_path)
            factory.step("physiology", "normal")
            persist(factory, db_path)
            connection = sqlite3.connect(db_path)
            count = connection.execute("SELECT COUNT(*) FROM wearable_telemetry").fetchone()[0]
            connection.close()
            self.assertEqual(count, 20)


if __name__ == "__main__":
    unittest.main()
