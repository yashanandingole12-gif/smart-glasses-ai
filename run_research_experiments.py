"""Run reproducible synthetic comparisons and ablations.

Outputs are simulated evidence only. They are not measurements from human
participants, a deployed factory, or a validated medical device.
"""

import json
from pathlib import Path

from factory_experiment import DEFAULT_DB, run_condition


MODES = ["none", "motion", "physiology", "glasses", "full"]
SCENARIOS = ["normal", "fatigue", "safety_zone", "machine_fault", "packet_loss", "sensor_drift", "latency"]


def main():
    results = []
    for index, mode in enumerate(MODES):
        result = run_condition(mode, scenario="normal", cycles=120, seed=100 + index, db_path=DEFAULT_DB)
        results.append(result)
    for index, scenario in enumerate(SCENARIOS):
        result = run_condition("full", scenario=scenario, cycles=120, seed=300 + index, db_path=DEFAULT_DB)
        results.append(result)

    output = Path(__file__).with_name("experiment_results.json")
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
    print(f"\nWrote synthetic experiment results to {output}")


if __name__ == "__main__":
    main()
