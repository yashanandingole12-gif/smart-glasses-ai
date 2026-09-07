from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from factory_experiment import Config, ResearchFactory, init_db, persist

DB_PATH = Path(__file__).with_name("research_factory.sqlite")
LAYOUT_PATH = Path(__file__).with_name("factory_layout.svg")
init_db(DB_PATH)

st.set_page_config(page_title="Factory Context Lab", page_icon="🏭", layout="wide")

DEPARTMENT_LAYOUT = {
    "Raw Logistics": (4, 1),
    "Body Shop": (1, 2),
    "Welding": (4, 2),
    "Painting": (7, 2),
    "Powertrain": (1, 4),
    "Battery Electrical": (4, 4),
    "General Assembly": (7, 4),
    "Quality Inspection": (1, 6),
    "Testing": (4, 6),
    "Finished Dispatch": (7, 6),
}


def query(sql: str, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn, params=params)


def start_factory(mode: str, scenario: str, seed: int):
    st.session_state.factory = ResearchFactory(Config(seed=seed, db_path=DB_PATH))
    st.session_state.mode = mode
    st.session_state.scenario = scenario
    st.session_state.last_step = None


def step_factory():
    factory = st.session_state.factory
    result = factory.step(st.session_state.mode, st.session_state.scenario)
    persist(factory, DB_PATH)
    st.session_state.last_step = result


def floor_plan(factory):
    st.image(str(LAYOUT_PATH), caption="Virtual vehicle-manufacturing floor layout; synthetic operational state is overlaid below.", use_container_width=True)
    rows = []
    position = factory.state.vehicle_position
    for index, department in enumerate(DEPARTMENT_LAYOUT):
        x, y = DEPARTMENT_LAYOUT[department]
        robot = factory.robots[department]
        worker = factory.workers[department]
        active = department == list(DEPARTMENT_LAYOUT)[position]
        rows.append({
            "department": department,
            "x": x,
            "y": y,
            "status": robot.state,
            "worker": worker.worker_id,
            "robot": robot.robot_id,
            "risk": worker.context()["ergonomic_risk"],
            "active": "Vehicle here" if active else "Station",
        })
    df = pd.DataFrame(rows)
    fig = px.scatter(
        df, x="x", y="y", text="department", color="status", size="risk",
        hover_data=["worker", "robot", "risk", "active"],
        color_discrete_map={"collaborative": "#0f766e", "risk-reduced": "#d97706", "safety-stop": "#dc2626", "fault-response": "#7c3aed"},
    )
    fig.update_traces(textposition="middle center", marker_line_width=1.5, marker_line_color="#0f172a")
    fig.update_layout(
        height=520, margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False, visible=False, range=[0, 8]),
        yaxis=dict(showgrid=False, visible=False, range=[0, 7]),
        legend_title="Robot state",
    )
    st.plotly_chart(fig, use_container_width=True, key=f"floor-{factory.state.cycle}")


def smart_glasses_view(factory):
    stage = list(DEPARTMENT_LAYOUT)[factory.state.vehicle_position]
    worker = factory.workers[stage]
    robot = factory.robots[stage]
    context = worker.context()
    st.markdown(f"""
    <div style='background:#101827;color:#eef2ff;border:1px solid #334155;border-radius:12px;padding:24px;min-height:250px'>
      <div style='color:#67e8f9;letter-spacing:2px;font-size:12px'>SMART-GLASSES CONCEPT VIEW · SIMULATED</div>
      <h2 style='margin:18px 0 8px'>{stage} · {worker.worker_id}</h2>
      <p style='color:#cbd5e1'>Task: {factory.departments[stage]['task']} · Robot: {robot.robot_id} · State: {robot.state}</p>
      <hr style='border-color:#334155'>
      <div style='display:grid;grid-template-columns:repeat(3,1fr);gap:16px'>
        <div><small>Worker state</small><br><strong>{'Elevated workload' if context['workload_index'] > .7 else 'Normal'}</strong></div>
        <div><small>Safety</small><br><strong>{'Review required' if context['safety_score'] < .5 else 'Normal'}</strong></div>
        <div><small>Instruction</small><br><strong>Step {(factory.state.cycle % 8) + 1} / 8</strong></div>
      </div>
      <p style='margin-top:22px;color:#67e8f9'>Factory context confidence: {factory.events[-1]['context_confidence'] if factory.events else 0:.2f}</p>
    </div>
    """, unsafe_allow_html=True)


def kpis(factory):
    worker = list(factory.workers.values())
    robots = list(factory.robots.values())
    context = [w.context() for w in worker]
    cols = st.columns(6)
    cols[0].metric("Simulation cycle", factory.state.cycle)
    cols[1].metric("Vehicle stage", list(DEPARTMENT_LAYOUT)[factory.state.vehicle_position])
    cols[2].metric("Completed vehicles", factory.state.completed_vehicles)
    cols[3].metric("Mean fatigue", f"{sum(x['fatigue_index'] for x in context)/len(context):.3f}")
    cols[4].metric("Mean robot speed", f"{sum(r.speed for r in robots)/len(robots):.3f}")
    cols[5].metric("Active alerts", len(factory.state.active_alerts))


def analytics():
    df = query("SELECT * FROM wearable_telemetry ORDER BY id DESC LIMIT 300")
    if df.empty:
        st.info("Start a cycle to populate the event stream.")
        return
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.line(df.sort_values("id"), x="cycle", y="fatigue_index", color="department", title="Synthetic fatigue stream"), use_container_width=True)
    with right:
        st.plotly_chart(px.scatter(df, x="workload_index", y="posture", color="department", title="Workload versus posture risk"), use_container_width=True)
    st.dataframe(df.head(30), use_container_width=True)


def query_runner():
    sql = st.text_area("SQL query", "SELECT wt.department, AVG(ws.fatigue_index) AS mean_fatigue, AVG(ws.context_confidence) AS mean_confidence FROM worker_state AS ws JOIN wearable_telemetry AS wt ON wt.run_id = ws.run_id AND wt.cycle = ws.cycle AND wt.worker_id = ws.worker_id GROUP BY wt.department;", height=130)
    if st.button("Run query", type="primary"):
        try:
            st.dataframe(query(sql), use_container_width=True)
        except Exception as exc:
            st.error(str(exc))


def main():
    st.title("Factory Context Lab")
    st.caption("Synthetic research testbed · all worker and wearable measurements are simulated, not clinical or real-worker data")
    with st.sidebar:
        st.header("Experiment controls")
        mode = st.selectbox("Context condition", ["none", "motion", "physiology", "glasses", "full"], index=4)
        scenario = st.selectbox("Scenario injection", ["normal", "fatigue", "safety_zone", "machine_fault", "workload_spike", "bottleneck", "worker_absence", "packet_loss", "sensor_drift", "latency"])
        seed = st.number_input("Random seed", min_value=1, value=42, step=1)
        if st.button("Initialize run"):
            start_factory(mode, scenario, int(seed))
        if st.button("Start / step realtime cycle", type="primary"):
            if "factory" not in st.session_state:
                start_factory(mode, scenario, int(seed))
            step_factory()
        if st.button("Run 30-cycle periodic analysis"):
            if "factory" not in st.session_state:
                start_factory(mode, scenario, int(seed))
            for _ in range(30):
                step_factory()
            st.success("30 synthetic cycles persisted to SQLite.")
    if "factory" not in st.session_state:
        start_factory(mode, scenario, int(seed))
    factory = st.session_state.factory
    kpis(factory)
    st.subheader("Interactive factory floor")
    st.caption(f"Active database: {DB_PATH.name} · The reference-style layout is static; the state below advances with each simulation cycle.")
    floor_plan(factory)
    tabs = st.tabs(["Live telemetry", "Periodic analytics", "Smart-glasses concept", "SQL query runner", "Protocol"])
    with tabs[0]:
        if factory.state.active_alerts:
            for alert in factory.state.active_alerts:
                st.warning(alert)
        events = query("""
            SELECT
                wt.cycle,
                wt.department,
                wt.worker_id,
                wt.heart_rate,
                wt.hrv_ms,
                wt.fatigue_index,
                wt.workload_index,
                wt.posture,
                wt.safety_state,
                ce.robot_action,
                ce.context_confidence
            FROM wearable_telemetry AS wt
            JOIN worker_state AS ws
                ON ws.run_id = wt.run_id
                AND ws.cycle = wt.cycle
                AND ws.worker_id = wt.worker_id
            JOIN context_events AS ce
                ON ce.run_id = wt.run_id
                AND ce.cycle = wt.cycle
                AND ce.department = wt.department
            ORDER BY wt.id DESC
            LIMIT 40
        """)
        st.dataframe(events, use_container_width=True)
    with tabs[1]:
        analytics()
    with tabs[2]:
        smart_glasses_view(factory)
    with tabs[3]:
        query_runner()
    with tabs[4]:
        st.markdown("""
### Sense → Stream → Process → Fuse → Understand → Decide → Act → Record

The live button advances one deterministic event-loop step. Each step synthesizes wearable telemetry, combines it with machine and robot state, applies confidence-aware HMI/HRI rules, persists normalized records in SQLite, and updates the floor state. The dashboard is evidence of execution, not evidence of a deployed factory or validated medical measurement.

**Fallback rule:** missing, delayed, drifting, or absent wearable data lowers context confidence; the robot does not blindly trust it and falls back to conservative machine/environment behavior.
        """)


if __name__ == "__main__":
    main()
