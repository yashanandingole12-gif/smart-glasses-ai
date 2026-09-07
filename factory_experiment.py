"""Reproducible synthetic factory experiment for wearable-context HMI/HRI research.

All worker and wearable measurements produced here are SYNTHETIC/SIMULATED DATA.
The model is a research testbed, not a clinical or industrial safety system.
"""

from __future__ import annotations

import json
import random
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

ROOT = Path(__file__).resolve().parent
DEFAULT_DB = ROOT / "research_factory.sqlite"
DEPARTMENTS = [
    ("Raw Logistics", "Material receiving and kitting", 0.55, 0.02, "logistics"),
    ("Body Shop", "Panel and chassis assembly", 0.78, 0.025, "physical"),
    ("Welding", "Robotic weld cells", 0.72, 0.03, "thermal"),
    ("Painting", "Coating and curing", 0.70, 0.03, "thermal"),
    ("Powertrain", "Engine and drivetrain fitment", 0.80, 0.04, "precision"),
    ("Battery Electrical", "Battery and high-voltage assembly", 0.74, 0.035, "safety"),
    ("General Assembly", "Interior, doors, and trim", 0.68, 0.025, "precision"),
    ("Quality Inspection", "Vision and dimensional inspection", 0.58, 0.015, "cognitive"),
    ("Testing", "End-of-line functional tests", 0.62, 0.02, "cognitive"),
    ("Finished Dispatch", "Vehicle release and dispatch", 0.50, 0.01, "logistics"),
]

SCENARIOS = [
    "normal",
    "fatigue",
    "safety_zone",
    "machine_fault",
    "workload_spike",
    "bottleneck",
    "worker_absence",
    "packet_loss",
    "sensor_drift",
    "latency",
]


@dataclass
class Config:
    seed: int = 42
    sample_period_s: float = 1.0
    simulation_minutes: int = 120
    number_of_workers: int = 10
    number_of_robots: int = 10
    number_of_vehicles: int = 40
    fault_probability: float = 0.01
    packet_loss_probability: float = 0.02
    communication_latency_ms: int = 80
    db_path: Path = DEFAULT_DB


@dataclass
class Worker:
    worker_id: str
    name: str
    department: str
    profile: str
    skill: float
    fatigue: float = 0.18
    workload: float = 0.35
    posture: float = 0.20
    stress: float = 0.18
    attention: float = 0.90
    heart_rate: float = 72.0
    hrv_ms: float = 62.0
    skin_temperature: float = 32.5
    activity: str = "working"
    location_confidence: float = 0.98
    wearing_device: bool = True

    def update(self, load: float, minute: float, scenario: str, rng: random.Random) -> None:
        scenario_load = 0.28 if scenario in {"fatigue", "workload_spike"} else 0.0
        if scenario == "fatigue" and minute > 45:
            scenario_load += 0.25
        if scenario == "workload_spike" and 50 < minute < 75:
            scenario_load += 0.30
        effective_load = max(0.05, min(1.0, load + scenario_load))
        recovery = 0.035 if int(minute) % 45 == 0 and minute > 0 else 0.0
        self.fatigue = max(0.0, min(1.0, self.fatigue + 0.006 * effective_load - recovery + rng.gauss(0, 0.006)))
        self.workload = max(0.0, min(1.0, 0.25 + 0.70 * effective_load + rng.gauss(0, 0.025)))
        self.posture = max(0.0, min(1.0, 0.10 + 0.55 * effective_load + (1 - self.skill) * 0.20 + rng.gauss(0, 0.025)))
        self.stress = max(0.0, min(1.0, 0.12 + 0.50 * effective_load + 0.25 * self.fatigue + rng.gauss(0, 0.025)))
        self.attention = max(0.0, min(1.0, 0.96 - 0.42 * self.fatigue - 0.20 * self.stress + rng.gauss(0, 0.018)))
        self.heart_rate = max(55.0, min(150.0, 68 + 35 * effective_load + 18 * self.stress + rng.gauss(0, 3.0)))
        self.hrv_ms = max(18.0, 78 - 42 * self.stress - 26 * self.fatigue + rng.gauss(0, 3.0))
        self.skin_temperature = max(30.0, min(36.0, 32.1 + 1.4 * effective_load + 0.6 * self.stress + rng.gauss(0, 0.10)))
        self.activity = "walking" if self.profile == "logistics" and rng.random() < 0.20 else "working"

    def context(self) -> Dict[str, float]:
        ergonomic_risk = max(0.0, min(1.0, 0.45 * self.fatigue + 0.35 * self.posture + 0.20 * self.workload))
        safety_score = max(0.0, min(1.0, 1.0 - 0.45 * self.fatigue - 0.25 * self.stress - 0.30 * self.posture))
        return {
            "fatigue_index": round(self.fatigue, 4),
            "workload_index": round(self.workload, 4),
            "posture_risk": round(self.posture, 4),
            "stress_index": round(self.stress, 4),
            "attention_index": round(self.attention, 4),
            "ergonomic_risk": round(ergonomic_risk, 4),
            "safety_score": round(safety_score, 4),
        }


@dataclass
class Robot:
    robot_id: str
    department: str
    base_speed: float = 1.0
    speed: float = 1.0
    state: str = "collaborative"
    utilization: float = 0.65
    faulted: bool = False


@dataclass
class Machine:
    machine_id: str
    department: str
    state: str = "running"
    production_count: int = 0
    cycle_time_s: float = 42.0
    faulted: bool = False


@dataclass
class FactoryState:
    clock: datetime
    cycle: int = 0
    vehicle_position: int = 0
    completed_vehicles: int = 0
    bottleneck_department: str = "None"
    active_alerts: List[str] = field(default_factory=list)


class ResearchFactory:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.rng = random.Random(self.config.seed)
        self.departments = self._build_departments()
        self.workers = self._build_workers()
        self.robots = {d[0]: Robot(f"R-{i+1:02d}", d[0]) for i, d in enumerate(DEPARTMENTS)}
        self.machines = {d[0]: Machine(f"M-{i+1:02d}", d[0], cycle_time_s=40 + i * 3) for i, d in enumerate(DEPARTMENTS)}
        self.state = FactoryState(datetime(2026, 1, 1, 6, 0, tzinfo=timezone.utc))
        self.run_id = f"run-{self.config.seed}-{uuid.uuid4().hex[:10]}"
        self.wearable_mode = "full"
        self.events: List[Dict] = []

    @staticmethod
    def _build_departments() -> Dict[str, Dict]:
        return {name: {"task": task, "load": load, "defect_base": defect, "profile": profile} for name, task, load, defect, profile in DEPARTMENTS}

    def _build_workers(self) -> Dict[str, Worker]:
        names = ["Asha", "Ravi", "Meera", "Karan", "Neha", "Sajid", "Priya", "Omar", "Isha", "Dev"]
        workers = {}
        for i, (department, _, load, _, profile) in enumerate(DEPARTMENTS[: self.config.number_of_workers]):
            workers[department] = Worker(f"W-{i+1:02d}", names[i], department, profile, 0.76 + self.rng.random() * 0.20)
        return workers

    def _wearable_event(self, worker: Worker, department: str, scenario: str) -> Dict:
        ctx = worker.context()
        packet_lost = scenario == "packet_loss" and self.rng.random() < 0.35
        drift = 0.0
        if scenario == "sensor_drift":
            drift = min(0.20, self.state.cycle * 0.002)
        location = department
        if scenario == "worker_absence" and self.state.cycle > 40 and worker.worker_id == "W-03":
            worker.wearing_device = False
            location = "unknown"
        return {
            "worker_id": worker.worker_id,
            "timestamp": self.state.clock.isoformat(),
            "location": location,
            "department": department,
            "task": self.departments[department]["task"],
            "heart_rate": None if packet_lost else round(worker.heart_rate + drift * 10, 2),
            "hrv_ms": None if packet_lost else round(worker.hrv_ms - drift * 15, 2),
            "skin_temperature": None if packet_lost else round(worker.skin_temperature + drift, 3),
            "acceleration": round(max(0.0, 0.4 + self.rng.gauss(0, 0.12)), 3),
            "activity_state": worker.activity,
            "posture": None if packet_lost else round(worker.posture, 4),
            "fatigue_index": None if packet_lost else ctx["fatigue_index"],
            "workload_index": None if packet_lost else ctx["workload_index"],
            "safety_state": "unknown" if packet_lost else ("elevated" if ctx["safety_score"] < 0.45 else "normal"),
            "machine_id": self.machines[department].machine_id,
            "robot_id": self.robots[department].robot_id,
            "packet_lost": int(packet_lost),
            "wearing_device": int(worker.wearing_device),
        }

    def _decision(self, department: str, wearable_mode: str, scenario: str, telemetry: Dict) -> Dict:
        robot = self.robots[department]
        machine = self.machines[department]
        ctx = self.workers[department].context()
        wearable_available = wearable_mode != "none" and not telemetry["packet_lost"] and telemetry["wearing_device"]
        confidence = 0.98 if wearable_available else 0.58
        if scenario == "latency":
            confidence -= 0.12
        if scenario == "sensor_drift":
            confidence -= 0.15
        confidence = max(0.0, confidence)
        if scenario == "safety_zone" and self.state.cycle in range(30, 45):
            proximity_risk = 1.0
        else:
            proximity_risk = 0.0
        if wearable_available and wearable_mode in {"full", "physiology"}:
            human_risk = max(ctx["fatigue_index"], ctx["stress_index"], ctx["workload_index"])
        elif wearable_available and wearable_mode == "motion":
            human_risk = max(ctx["posture_risk"], ctx["ergonomic_risk"] * 0.55)
        elif wearable_available and wearable_mode == "glasses":
            human_risk = 0.0
        else:
            human_risk = 0.0
        risk = max(human_risk, proximity_risk)
        if machine.faulted:
            robot.state, robot.speed = "fault-response", 0.0
            action = "machine-safe-stop"
        elif risk > 0.72 and confidence >= 0.70:
            robot.state, robot.speed = "risk-reduced", max(0.45, 1.0 - risk * 0.45)
            action = "reduce-speed"
        elif proximity_risk > 0:
            robot.state, robot.speed = "safety-stop", 0.0
            action = "safety-stop"
        else:
            robot.state, robot.speed = "collaborative", 1.0
            action = "continue"
        return {
            "context_confidence": round(confidence, 3),
            "risk_score": round(risk, 4),
            "robot_action": action,
            "robot_speed": round(robot.speed, 4),
            "robot_state": robot.state,
            "machine_state": machine.state,
            "wearable_context_used": int(wearable_available),
        }

    def step(self, wearable_mode: str = "full", scenario: str = "normal") -> Dict:
        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario}")
        self.wearable_mode = wearable_mode
        self.state.cycle += 1
        minute = self.state.cycle * self.config.sample_period_s / 60.0
        self.state.clock += timedelta(seconds=self.config.sample_period_s)
        self.state.active_alerts = []
        for department, worker in self.workers.items():
            base_load = self.departments[department]["load"]
            worker.update(base_load, minute, scenario, self.rng)
            machine = self.machines[department]
            if scenario == "machine_fault" and self.state.cycle in range(45, 60) and department == "Powertrain":
                machine.faulted, machine.state = True, "fault"
            else:
                machine.faulted = False
                machine.state = "running"
            telemetry = self._wearable_event(worker, department, scenario)
            decision = self._decision(department, wearable_mode, scenario, telemetry)
            if decision["robot_action"] != "continue":
                self.state.active_alerts.append(f"{department}: {decision['robot_action']}")
            machine.production_count += int(decision["robot_action"] == "continue")
            event = {
                "run_id": self.run_id,
                "cycle": self.state.cycle,
                "scenario": scenario,
                "timestamp": self.state.clock.isoformat(),
                "department": department,
                "task": self.departments[department]["task"],
                "vehicle_position": self.state.vehicle_position,
                "worker_id": worker.worker_id,
                "worker_name": worker.name,
                "robot_id": self.robots[department].robot_id,
                "machine_id": machine.machine_id,
                **telemetry,
                **worker.context(),
                **decision,
                "defect": int(self.rng.random() < self.departments[department]["defect_base"] + 0.08 * worker.fatigue),
                "event_type": "telemetry",
            }
            self.events.append(event)
        throughput_factor = sum(self.robots[d].speed for d in self.workers) / max(1, len(self.workers))
        if throughput_factor > 0.80:
            self.state.vehicle_position = (self.state.vehicle_position + 1) % len(DEPARTMENTS)
        if self.state.vehicle_position == len(DEPARTMENTS) - 1 and throughput_factor > 0.80:
            self.state.completed_vehicles += 1
        self.state.bottleneck_department = min(self.robots, key=lambda d: self.robots[d].speed)
        for event in self.events[-len(self.workers):]:
            event["completed_vehicles"] = self.state.completed_vehicles
        return {"state": self.state_as_dict(), "events": self.events[-len(self.workers):]}

    def state_as_dict(self) -> Dict:
        return {
            "run_id": self.run_id,
            "timestamp": self.state.clock.isoformat(),
            "cycle": self.state.cycle,
            "vehicle_position": self.state.vehicle_position,
            "vehicle_stage": DEPARTMENTS[self.state.vehicle_position][0],
            "completed_vehicles": self.state.completed_vehicles,
            "bottleneck_department": self.state.bottleneck_department,
            "active_alerts": self.state.active_alerts,
        }

    def run(self, cycles: Optional[int] = None, wearable_mode: str = "full", scenario: str = "normal") -> List[Dict]:
        for _ in range(cycles or int(self.config.simulation_minutes * 60 / self.config.sample_period_s)):
            self.step(wearable_mode, scenario)
        return self.events


def init_db(path: Path = DEFAULT_DB) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS simulation_runs (run_id TEXT PRIMARY KEY, started_at TEXT, seed INTEGER, scenario TEXT, wearable_mode TEXT, cycles INTEGER, synthetic_data INTEGER);
            CREATE TABLE IF NOT EXISTS departments (department TEXT PRIMARY KEY, task TEXT, base_load REAL, defect_base REAL, profile TEXT);
            CREATE TABLE IF NOT EXISTS workers (worker_id TEXT PRIMARY KEY, name TEXT, department TEXT, skill REAL, profile TEXT);
            CREATE TABLE IF NOT EXISTS wearable_devices (device_id TEXT PRIMARY KEY, worker_id TEXT, device_type TEXT, sampling_hz REAL, status TEXT);
            CREATE TABLE IF NOT EXISTS wearable_telemetry (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, cycle INTEGER, timestamp TEXT, worker_id TEXT, department TEXT, location TEXT, task TEXT, heart_rate REAL, hrv_ms REAL, skin_temperature REAL, acceleration REAL, activity_state TEXT, posture REAL, fatigue_index REAL, workload_index REAL, safety_state TEXT, machine_id TEXT, robot_id TEXT, packet_lost INTEGER, wearing_device INTEGER);
            CREATE TABLE IF NOT EXISTS worker_state (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, cycle INTEGER, worker_id TEXT, fatigue_index REAL, workload_index REAL, posture_risk REAL, stress_index REAL, attention_index REAL, ergonomic_risk REAL, safety_score REAL, context_confidence REAL);
            CREATE TABLE IF NOT EXISTS machines (machine_id TEXT PRIMARY KEY, department TEXT, state TEXT, production_count INTEGER);
            CREATE TABLE IF NOT EXISTS machine_telemetry (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, cycle INTEGER, machine_id TEXT, department TEXT, state TEXT, faulted INTEGER, production_count INTEGER, cycle_time_s REAL);
            CREATE TABLE IF NOT EXISTS robots (robot_id TEXT PRIMARY KEY, department TEXT, state TEXT, utilization REAL);
            CREATE TABLE IF NOT EXISTS robot_telemetry (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, cycle INTEGER, robot_id TEXT, department TEXT, state TEXT, speed REAL, action TEXT, utilization REAL);
            CREATE TABLE IF NOT EXISTS tasks (task_id TEXT PRIMARY KEY, department TEXT, task TEXT);
            CREATE TABLE IF NOT EXISTS production_events (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, cycle INTEGER, timestamp TEXT, department TEXT, vehicle_position INTEGER, completed_vehicles INTEGER, defect INTEGER, event_type TEXT);
            CREATE TABLE IF NOT EXISTS safety_events (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, cycle INTEGER, timestamp TEXT, department TEXT, worker_id TEXT, event TEXT, risk_score REAL);
            CREATE TABLE IF NOT EXISTS context_events (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, cycle INTEGER, timestamp TEXT, department TEXT, context_confidence REAL, wearable_context_used INTEGER, robot_action TEXT, risk_score REAL);
            CREATE TABLE IF NOT EXISTS factory_state (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, cycle INTEGER, timestamp TEXT, vehicle_position INTEGER, vehicle_stage TEXT, bottleneck_department TEXT, completed_vehicles INTEGER);
            """
        )
        conn.commit()
    finally:
        conn.close()


def persist(factory: ResearchFactory, path: Path = DEFAULT_DB) -> None:
    init_db(path)
    conn = sqlite3.connect(path)
    try:
        for table in ("wearable_telemetry", "worker_state", "robot_telemetry", "machine_telemetry", "context_events", "safety_events", "production_events", "factory_state"):
            conn.execute(f"DELETE FROM {table} WHERE run_id = ?", (factory.run_id,))
        conn.execute("INSERT OR REPLACE INTO simulation_runs VALUES (?, ?, ?, ?, ?, ?, ?)", (factory.run_id, factory.state.clock.isoformat(), factory.config.seed, factory.events[0]["scenario"] if factory.events else "normal", factory.wearable_mode, factory.state.cycle, 1))
        for name, info in factory.departments.items():
            conn.execute("INSERT OR REPLACE INTO departments VALUES (?, ?, ?, ?, ?)", (name, info["task"], info["load"], info["defect_base"], info["profile"]))
        for worker in factory.workers.values():
            conn.execute("INSERT OR REPLACE INTO workers VALUES (?, ?, ?, ?, ?)", (worker.worker_id, worker.name, worker.department, worker.skill, worker.profile))
            conn.execute("INSERT OR REPLACE INTO wearable_devices VALUES (?, ?, ?, ?, ?)", (f"WD-{worker.worker_id}", worker.worker_id, "synthetic-multimodal", 1.0, "simulated"))
        for event in factory.events:
            telemetry = (event["run_id"], event["cycle"], event["timestamp"], event["worker_id"], event["department"], event["location"], event["task"], event["heart_rate"], event["hrv_ms"], event["skin_temperature"], event["acceleration"], event["activity_state"], event["posture"], event["fatigue_index"], event["workload_index"], event["safety_state"], event["machine_id"], event["robot_id"], event["packet_lost"], event["wearing_device"])
            conn.execute("INSERT INTO wearable_telemetry (run_id, cycle, timestamp, worker_id, department, location, task, heart_rate, hrv_ms, skin_temperature, acceleration, activity_state, posture, fatigue_index, workload_index, safety_state, machine_id, robot_id, packet_lost, wearing_device) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", telemetry)
            conn.execute("INSERT INTO worker_state (run_id, cycle, worker_id, fatigue_index, workload_index, posture_risk, stress_index, attention_index, ergonomic_risk, safety_score, context_confidence) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (event["run_id"], event["cycle"], event["worker_id"], event["fatigue_index"], event["workload_index"], event["posture_risk"], event["stress_index"], event["attention_index"], event["ergonomic_risk"], event["safety_score"], event["context_confidence"]))
            conn.execute("INSERT INTO robot_telemetry (run_id, cycle, robot_id, department, state, speed, action, utilization) VALUES (?,?,?,?,?,?,?,?)", (event["run_id"], event["cycle"], event["robot_id"], event["department"], event["robot_state"], event["robot_speed"], event["robot_action"], event["robot_speed"]))
            conn.execute("INSERT INTO machine_telemetry (run_id, cycle, machine_id, department, state, faulted, production_count, cycle_time_s) VALUES (?,?,?,?,?,?,?,?)", (event["run_id"], event["cycle"], event["machine_id"], event["department"], event["machine_state"], int(event["machine_state"] == "fault"), 0, 42.0))
            conn.execute("INSERT INTO context_events (run_id, cycle, timestamp, department, context_confidence, wearable_context_used, robot_action, risk_score) VALUES (?,?,?,?,?,?,?,?)", (event["run_id"], event["cycle"], event["timestamp"], event["department"], event["context_confidence"], event["wearable_context_used"], event["robot_action"], event["risk_score"]))
            if event["robot_action"] != "continue":
                conn.execute("INSERT INTO safety_events (run_id, cycle, timestamp, department, worker_id, event, risk_score) VALUES (?,?,?,?,?,?,?)", (event["run_id"], event["cycle"], event["timestamp"], event["department"], event["worker_id"], event["robot_action"], event["risk_score"]))
            conn.execute("INSERT INTO production_events (run_id, cycle, timestamp, department, vehicle_position, completed_vehicles, defect, event_type) VALUES (?,?,?,?,?,?,?,?)", (event["run_id"], event["cycle"], event["timestamp"], event["department"], event["vehicle_position"], factory.state.completed_vehicles, event["defect"], event["event_type"]))
        state = factory.state_as_dict()
        conn.execute("INSERT INTO factory_state (run_id, cycle, timestamp, vehicle_position, vehicle_stage, bottleneck_department, completed_vehicles) VALUES (?,?,?,?,?,?,?)", (factory.run_id, state["cycle"], state["timestamp"], state["vehicle_position"], state["vehicle_stage"], state["bottleneck_department"], state["completed_vehicles"]))
        conn.commit()
    finally:
        conn.close()


def summarize(events: Iterable[Dict]) -> Dict[str, float]:
    rows = list(events)
    if not rows:
        return {"events": 0}
    mean = lambda key: sum((r[key] or 0) for r in rows) / len(rows)
    return {
        "events": len(rows),
        "cycles": len({r["cycle"] for r in rows}),
        "completed_vehicles": max(r.get("completed_vehicles", 0) for r in rows),
        "mean_fatigue": round(mean("fatigue_index"), 4),
        "mean_workload": round(mean("workload_index"), 4),
        "mean_ergonomic_risk": round(mean("ergonomic_risk"), 4),
        "mean_context_confidence": round(mean("context_confidence"), 4),
        "mean_robot_speed": round(mean("robot_speed"), 4),
        "alerts": sum(r["robot_action"] != "continue" for r in rows),
        "packet_loss_rate": round(sum(r["packet_lost"] for r in rows) / len(rows), 4),
        "defects": sum(r["defect"] for r in rows),
    }


def run_condition(mode: str, scenario: str = "normal", cycles: int = 60, seed: int = 42, db_path: Path = DEFAULT_DB) -> Dict:
    factory = ResearchFactory(Config(seed=seed, db_path=db_path))
    factory.run(cycles=cycles, wearable_mode=mode, scenario=scenario)
    persist(factory, db_path)
    return {"run_id": factory.run_id, "mode": mode, "scenario": scenario, "summary": summarize(factory.events)}


if __name__ == "__main__":
    init_db()
    for mode in ("none", "motion", "physiology", "glasses", "full"):
        print(json.dumps(run_condition(mode, cycles=60), indent=2))
