from __future__ import annotations

import json
import platform
import sqlite3
import time
from pathlib import Path
from typing import Iterable

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from factory_experiment import Config, ResearchFactory, init_db, persist

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "research_factory.sqlite"
LAYOUT_PATH = ROOT / "factory_layout.svg"
RESULTS_PATH = ROOT / "experiment_results.json"
DEPARTMENTS = [
    "Raw Logistics", "Body Shop", "Welding", "Painting", "Powertrain",
    "Battery Electrical", "General Assembly", "Quality Inspection", "Testing", "Finished Dispatch",
]
PAGES = [
    "COMMAND CENTER", "FACTORY DIGITAL TWIN", "WORKER MONITORING", "ROBOT & MACHINE",
    "WEARABLE CONTEXT", "PRODUCTION", "SAFETY", "EXPERIMENT LAB", "ANALYTICS",
    "DATABASE", "SMART GLASSES", "SYSTEM",
]
STATUS_COLORS = {
    "collaborative": "#22c55e", "risk-reduced": "#f59e0b", "safety-stop": "#ef4444",
    "fault-response": "#a78bfa", "running": "#22c55e", "fault": "#ef4444", "offline": "#64748b",
}

init_db(DB_PATH)
st.set_page_config(page_title="Smart Factory HMI/HRI Research Platform", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")


def inject_theme():
    st.markdown("""
    <style>
    :root { color-scheme: dark; }
    .stApp { background: #07111f; color: #dbe7f3; }
    [data-testid="stHeader"] { background: rgba(7,17,31,.94); }
    [data-testid="stSidebar"] { background: #0b1728; border-right: 1px solid #20334b; }
    [data-testid="stSidebar"] * { color: #cbd5e1; }
    .block-container { max-width: 1700px; padding: 1.2rem 1.7rem 2.5rem; }
    h1, h2, h3 { color: #f8fafc; letter-spacing: .02em; }
    h1 { font-size: 1.55rem !important; margin-bottom: .2rem; }
    h2 { font-size: 1.05rem !important; text-transform: uppercase; letter-spacing: .08em; }
    h3 { font-size: .92rem !important; }
    .topbar { display:flex; align-items:center; justify-content:space-between; gap:18px; background:#0d1b2e; border:1px solid #20334b; padding:14px 18px; margin-bottom:16px; }
    .brand { color:#f8fafc; font-size:14px; font-weight:800; letter-spacing:.12em; }
    .subbrand { color:#7f95ac; font-size:10px; letter-spacing:.12em; margin-top:4px; }
    .status-grid { display:grid; grid-template-columns:repeat(6, minmax(105px,1fr)); gap:12px; }
    .status-cell { border-left:1px solid #29415d; padding-left:12px; min-width:105px; }
    .status-label { color:#7890a8; font-size:9px; letter-spacing:.12em; text-transform:uppercase; }
    .status-value { color:#e2e8f0; font-size:12px; font-weight:700; margin-top:5px; white-space:nowrap; }
    .dot { color:#22c55e; }
    .kpi { background:#0d1b2e; border:1px solid #20334b; padding:14px 15px; min-height:96px; }
    .kpi-label { color:#7890a8; font-size:10px; letter-spacing:.1em; text-transform:uppercase; }
    .kpi-value { color:#f8fafc; font-size:25px; font-weight:800; margin-top:12px; }
    .kpi-note { color:#8ba2ba; font-size:10px; margin-top:4px; }
    .panel { background:#0d1b2e; border:1px solid #20334b; padding:15px; }
    .section-label { color:#86a5c4; font-size:10px; letter-spacing:.14em; text-transform:uppercase; margin:4px 0 9px; }
    .alert-row { border-left:3px solid #f59e0b; background:#17263a; padding:9px 11px; margin:6px 0; font-size:12px; }
    .research-note { border-left:3px solid #38bdf8; background:#0d2035; padding:10px 13px; color:#a8c4df; font-size:12px; }
    .critical-note { border-left:3px solid #ef4444; background:#321b28; padding:10px 13px; color:#fecaca; font-size:12px; }
    .metric-strip { color:#91a9c2; font-size:11px; padding:7px 0; border-bottom:1px solid #20334b; }
    div[data-testid="stDataFrame"] { border:1px solid #20334b; }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=2, show_spinner=False)
def read_sql(sql: str, params: tuple = ()) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn, params=params)


@st.cache_data(ttl=30, show_spinner=False)
def load_results() -> list[dict]:
    if not RESULTS_PATH.exists():
        return []
    return json.loads(RESULTS_PATH.read_text(encoding="utf-8"))


def start_factory(mode: str, scenario: str, seed: int, cycles: int):
    factory = ResearchFactory(Config(seed=seed, db_path=DB_PATH))
    factory.config.simulation_minutes = max(1, cycles)
    st.session_state.factory = factory
    st.session_state.mode = mode
    st.session_state.scenario = scenario
    st.session_state.running = False
    st.session_state.started_at = time.strftime("%H:%M:%S")
    read_sql.clear()


def get_factory() -> ResearchFactory:
    if "factory" not in st.session_state:
        start_factory("full", "normal", 42, 30)
    return st.session_state.factory


def step_factory() -> None:
    factory = get_factory()
    factory.step(st.session_state.mode, st.session_state.scenario)
    persist(factory, DB_PATH)
    read_sql.clear()


def latest_run_id(factory: ResearchFactory) -> str:
    return factory.run_id


def current_events(factory: ResearchFactory, limit: int = 500) -> pd.DataFrame:
    return read_sql("SELECT * FROM wearable_telemetry WHERE run_id = ? ORDER BY id DESC LIMIT ?", (latest_run_id(factory), limit))


def context_events(factory: ResearchFactory, limit: int = 500) -> pd.DataFrame:
    return read_sql("SELECT * FROM context_events WHERE run_id = ? ORDER BY id DESC LIMIT ?", (latest_run_id(factory), limit))


def worker_state(factory: ResearchFactory, limit: int = 500) -> pd.DataFrame:
    return read_sql("SELECT * FROM worker_state WHERE run_id = ? ORDER BY id DESC LIMIT ?", (latest_run_id(factory), limit))


def kpi(label: str, value: str, note: str = "") -> None:
    st.markdown(f"<div class='kpi'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div><div class='kpi-note'>{note}</div></div>", unsafe_allow_html=True)


def header(factory: ResearchFactory) -> None:
    events = current_events(factory, 100)
    context = worker_state(factory, 100)
    confidence = float(context["context_confidence"].mean()) if not context.empty else 0.0
    availability = 1.0 - float(events["packet_lost"].mean()) if not events.empty else 1.0
    simulation = "RUNNING" if st.session_state.get("running", False) else "READY"
    st.markdown(f"""
    <div class='topbar'>
      <div><div class='brand'>SMART FACTORY HMI / HRI RESEARCH PLATFORM</div><div class='subbrand'>WEARABLE CONTEXT · DIGITAL TWIN TESTBED · SYNTHETIC DATA</div></div>
      <div class='status-grid'>
        <div class='status-cell'><div class='status-label'>System</div><div class='status-value'><span class='dot'>●</span> ONLINE</div></div>
        <div class='status-cell'><div class='status-label'>Simulation</div><div class='status-value'><span class='dot'>●</span> {simulation}</div></div>
        <div class='status-cell'><div class='status-label'>Cycle</div><div class='status-value'>{factory.state.cycle}</div></div>
        <div class='status-cell'><div class='status-label'>Simulation time</div><div class='status-value'>{factory.state.clock.strftime('%H:%M:%S')}</div></div>
        <div class='status-cell'><div class='status-label'>Database</div><div class='status-value'><span class='dot'>●</span> CONNECTED</div></div>
        <div class='status-cell'><div class='status-label'>Wearable network</div><div class='status-value'>{availability * 100:.1f}% AVAILABLE</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def controls() -> None:
    with st.sidebar:
        st.markdown("### CONTROL ROOM")
        page = st.radio("Navigate", PAGES, label_visibility="collapsed")
        st.divider()
        st.markdown("#### EXPERIMENT CONTROL")
        mode = st.selectbox("Context condition", ["none", "motion", "physiology", "glasses", "full"], index=4)
        scenario = st.selectbox("Scenario", ["normal", "fatigue", "safety_zone", "machine_fault", "workload_spike", "bottleneck", "worker_absence", "packet_loss", "sensor_drift", "latency"])
        seed = st.number_input("Random seed", min_value=1, value=42, step=1)
        cycles = st.slider("Periodic cycles", min_value=1, max_value=120, value=30)
        if st.button("INITIALIZE EXPERIMENT", use_container_width=True):
            start_factory(mode, scenario, int(seed), cycles)
        left, right = st.columns(2)
        with left:
            if st.button("STEP", use_container_width=True):
                step_factory()
        with right:
            if st.button("RESET", use_container_width=True):
                start_factory(mode, scenario, int(seed), cycles)
        if st.button("RUN PERIODIC", use_container_width=True):
            if "factory" not in st.session_state:
                start_factory(mode, scenario, int(seed), cycles)
            st.session_state.running = True
            for _ in range(cycles):
                step_factory()
            st.session_state.running = False
            st.success(f"{cycles} synthetic cycles persisted")
        if st.button("PAUSE", use_container_width=True):
            st.session_state.running = False
        st.divider()
        st.caption("Research prototype. Worker, wearable, robot, and factory measurements are synthetic/simulated data unless explicitly identified otherwise.")
    return page


def factory_plot(factory: ResearchFactory, height: int = 520):
    rows = []
    for index, department in enumerate(DEPARTMENTS):
        worker = factory.workers[department]
        robot = factory.robots[department]
        x = [1, 4, 7][index % 3] + (index // 3) * 0.2
        y = [1, 2, 3, 4, 5, 6, 7][index % 7]
        rows.append({"department": department, "x": x, "y": y, "status": robot.state, "worker": worker.worker_id, "robot": robot.robot_id, "risk": worker.context()["ergonomic_risk"], "task": factory.departments[department]["task"]})
    df = pd.DataFrame(rows)
    fig = px.scatter(df, x="x", y="y", text="department", color="status", size="risk", hover_data=["worker", "robot", "task", "risk"], color_discrete_map=STATUS_COLORS)
    fig.update_traces(textposition="middle center", marker_line_width=1, marker_line_color="#dbeafe")
    stage_index = factory.state.vehicle_position
    vehicle_x = [1, 4, 7][stage_index % 3] + (stage_index // 3) * 0.2
    vehicle_y = [1, 2, 3, 4, 5, 6, 7][stage_index % 7] - .32
    fig.add_trace(go.Scatter(x=[vehicle_x], y=[vehicle_y], mode="markers+text", text=["VEHICLE"], textposition="bottom center", marker=dict(size=18, color="#38bdf8", symbol="diamond"), name="Vehicle position"))
    fig.update_layout(height=height, template="plotly_dark", paper_bgcolor="#0d1b2e", plot_bgcolor="#0d1b2e", margin=dict(l=12, r=12, t=20, b=12), xaxis=dict(visible=False, range=[0, 8]), yaxis=dict(visible=False, range=[0, 8]), legend_title="Status")
    st.plotly_chart(fig, use_container_width=True, key=f"factory-{factory.state.cycle}-{height}")


def event_panel(factory: ResearchFactory, limit: int = 12):
    events = context_events(factory, limit)
    if events.empty:
        st.info("No events yet. Press STEP or RUN PERIODIC.")
        return
    for row in events.itertuples():
        severity = "critical-note" if row.robot_action in {"safety-stop", "machine-safe-stop"} else "alert-row"
        st.markdown(f"<div class='{severity}'><b>{row.timestamp[-8:]}</b> · {row.department}<br>{row.robot_action.upper()} · risk {row.risk_score:.2f} · confidence {row.context_confidence:.2f}</div>", unsafe_allow_html=True)


def command_center(factory: ResearchFactory):
    st.title("Command Center")
    events = current_events(factory)
    ctx = worker_state(factory)
    robots = len(factory.robots)
    k = st.columns(8)
    values = [
        ("Factory", "RUNNING", "simulation state"), ("Active workers", str(len(factory.workers)), "synthetic workers"),
        ("Active robots", str(robots), "configured robots"), ("Vehicles in process", str(factory.state.vehicle_position + 1), "current stage"),
        ("Production today", str(factory.state.completed_vehicles), "completed vehicles"), ("Safety events", str(len(factory.state.active_alerts)), "current cycle"),
        ("Active alerts", str(len(factory.state.active_alerts)), "current cycle"), ("Context confidence", f"{ctx.context_confidence.mean() * 100:.1f}%" if not ctx.empty else "--", "proposed metric"),
    ]
    for col, item in zip(k, values):
        with col: kpi(*item)
    st.markdown("<div class='research-note'>Primary view: factory state, then worker state, robot/machine state, wearable context, production, safety, and analytics. All live values are synthetic.</div>", unsafe_allow_html=True)
    left, right = st.columns([2.25, 1])
    with left:
        st.markdown("### FACTORY FLOOR / DIGITAL TWIN STATE")
        if LAYOUT_PATH.exists(): st.image(str(LAYOUT_PATH), use_container_width=True)
        factory_plot(factory, 470)
    with right:
        st.markdown("### LIVE EVENT STREAM")
        event_panel(factory)
    st.markdown("### RECENT WEARABLE CONTEXT")
    st.dataframe(events[["cycle", "department", "worker_id", "heart_rate", "hrv_ms", "fatigue_index", "workload_index", "safety_state"]].head(20) if not events.empty else events, use_container_width=True, hide_index=True)


def digital_twin(factory: ResearchFactory):
    st.title("Factory Digital Twin")
    st.markdown("<div class='research-note'>Twin-like simulated state representation. This is not a validated physical-plant digital twin.</div>", unsafe_allow_html=True)
    factory_plot(factory, 650)
    selected = st.selectbox("Department detail", DEPARTMENTS)
    worker = factory.workers[selected]; robot = factory.robots[selected]; machine = factory.machines[selected]
    cols = st.columns(8)
    for col, item in zip(cols, [("Department", selected, ""), ("Worker", worker.worker_id, worker.name), ("Robot", robot.robot_id, robot.state), ("Machine", machine.machine_id, machine.state), ("Worker workload", f"{worker.workload:.2f}", "synthetic"), ("Fatigue", f"{worker.fatigue:.2f}", "indicator"), ("Robot speed", f"{robot.speed:.2f}", "relative"), ("Risk", f"{worker.context()['ergonomic_risk']:.2f}", "proposed")]):
        with col: kpi(*item)


def worker_monitoring(factory: ResearchFactory):
    st.title("Worker Monitoring")
    st.markdown("<div class='research-note'>Synthetic worker-state indicators. Heart rate, HRV, posture, fatigue, and workload are not clinical diagnoses.</div>", unsafe_allow_html=True)
    events = current_events(factory, 1000)
    if events.empty: st.info("Run a cycle to populate worker monitoring."); return
    search = st.text_input("Filter worker or department")
    latest = events.sort_values("id").groupby("worker_id", as_index=False).tail(1)
    if search: latest = latest[latest.astype(str).apply(lambda row: row.str.contains(search, case=False).any(), axis=1)]
    st.dataframe(latest[["worker_id", "worker_name", "department", "task", "heart_rate", "hrv_ms", "fatigue_index", "workload_index", "posture", "safety_state"]], use_container_width=True, hide_index=True)
    worker_id = st.selectbox("Worker detail", latest["worker_id"].tolist())
    history = events[events.worker_id == worker_id].sort_values("cycle")
    if not history.empty:
        st.markdown(f"### {worker_id} / {history.iloc[-1]['worker_name']}")
        chart = history.melt(id_vars=["cycle"], value_vars=["fatigue_index", "workload_index", "posture"], var_name="indicator", value_name="value")
        st.plotly_chart(px.line(chart, x="cycle", y="value", color="indicator", template="plotly_dark", title="Synthetic worker-state indicators"), use_container_width=True)


def robot_machine(factory: ResearchFactory):
    st.title("Robot & Machine")
    robot_df = context_events(factory, 1000)
    rows = []
    for department, robot in factory.robots.items():
        machine = factory.machines[department]
        rows.append({"robot_id": robot.robot_id, "department": department, "state": robot.state, "speed": robot.speed, "machine_id": machine.machine_id, "machine_state": machine.state, "production_count": machine.production_count})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    if not robot_df.empty:
        st.markdown("### Robot action history")
        st.dataframe(robot_df[["timestamp", "department", "robot_action", "robot_speed", "risk_score", "context_confidence"]].head(50), use_container_width=True, hide_index=True)


def wearable_context(factory: ResearchFactory):
    st.title("Wearable Context")
    st.markdown("""
    <div class='panel'><div class='section-label'>Sense → Stream → Process → Fuse → Understand → Decide → Act → Record</div>
    <div class='metric-strip'>WEARABLE → EDGE PROCESSING → STREAM → CONTEXT ENGINE → HUMAN STATE → HMI/HRI POLICY → ROBOT / MACHINE</div>
    </div>
    """, unsafe_allow_html=True)
    events = current_events(factory, 500)
    ctx = worker_state(factory, 500)
    if events.empty: st.info("Run a cycle to populate the context pipeline."); return
    latest = events.sort_values("id").iloc[0]
    c = ctx[ctx.worker_id == latest.worker_id].iloc[0] if not ctx[ctx.worker_id == latest.worker_id].empty else None
    left, right = st.columns(2)
    with left:
        st.markdown("### WEARABLE TELEMETRY")
        st.dataframe(pd.DataFrame([{"Heart rate": latest.heart_rate, "HRV ms": latest.hrv_ms, "Skin temperature": latest.skin_temperature, "Motion": latest.acceleration, "Activity": latest.activity_state, "Location": latest.location}]), use_container_width=True, hide_index=True)
    with right:
        st.markdown("### PROPOSED EXPERIMENTAL CONTEXT CONFIDENCE")
        value = float(c.context_confidence) if c is not None else 0.0
        st.progress(value, text=f"{value * 100:.1f}% · not a validated universal metric")
        st.dataframe(pd.DataFrame([{"Worker state": latest.worker_id, "Task": latest.task, "Fatigue indicator": latest.fatigue_index, "Workload indicator": latest.workload_index, "Safety": latest.safety_state, "Robot": latest.robot_id}]), use_container_width=True, hide_index=True)
    st.markdown("### WHAT DOES THE MACHINE KNOW?")
    st.code(f"{latest.worker_id}\n↓ At {latest.department}\n↓ Performing {latest.task}\n↓ Workload indicator {latest.workload_index:.2f}\n↓ Fatigue indicator {latest.fatigue_index:.2f}\n↓ Robot {latest.robot_id} nearby\n↓ HRI action from context event log", language="text")


def production(factory: ResearchFactory):
    st.title("Production")
    events = current_events(factory, 2000)
    ctx = context_events(factory, 2000)
    cols = st.columns(5)
    for col, item in zip(cols, [("Vehicles completed", str(factory.state.completed_vehicles), "synthetic"), ("Current stage", list(factory.departments)[factory.state.vehicle_position], "flow position"), ("Cycle", str(factory.state.cycle), "event loop"), ("Bottleneck", factory.state.bottleneck_department, "lowest robot speed"), ("Data rows", str(len(events)), "current run")]):
        with col: kpi(*item)
    if not events.empty:
        chart = events.groupby("cycle", as_index=False).agg(fatigue=("fatigue_index", "mean"), workload=("workload_index", "mean"))
        st.plotly_chart(px.line(chart, x="cycle", y=["fatigue", "workload"], template="plotly_dark", title="Synthetic production-context trend"), use_container_width=True)
    st.dataframe(events[["cycle", "department", "task", "packet_lost", "fatigue_index", "workload_index", "safety_state"]].head(80) if not events.empty else events, use_container_width=True, hide_index=True)


def safety(factory: ResearchFactory):
    st.title("Safety")
    ctx = context_events(factory, 2000)
    if ctx.empty: st.info("No safety/context events in the current run."); return
    alerts = ctx[ctx.robot_action != "continue"]
    cols = st.columns(4)
    for col, item in zip(cols, [("Interventions", str(len(alerts)), "current run"), ("Safety stops", str((alerts.robot_action == "safety-stop").sum()), "simulated"), ("Machine stops", str((alerts.robot_action == "machine-safe-stop").sum()), "simulated"), ("Mean confidence", f"{ctx.context_confidence.mean() * 100:.1f}%", "proposed metric")]):
        with col: kpi(*item)
    st.dataframe(alerts[["timestamp", "department", "robot_action", "risk_score", "context_confidence"]].head(100), use_container_width=True, hide_index=True)
    if not alerts.empty: st.plotly_chart(px.histogram(alerts, x="department", color="robot_action", template="plotly_dark", title="Interventions by department"), use_container_width=True)


def experiment_lab(factory: ResearchFactory):
    st.title("Experiment Lab")
    st.markdown("<div class='research-note'>Run controls change the synthetic event loop. Comparison values below are loaded from experiment_results.json and are not fabricated by the dashboard.</div>", unsafe_allow_html=True)
    results = load_results()
    if not results:
        st.warning("No experiment_results.json found. Run run_research_experiments.py first.")
        return
    df = pd.DataFrame([{**r["summary"], "mode": r["mode"], "scenario": r["scenario"], "run_id": r["run_id"]} for r in results])
    normal = df[df.scenario == "normal"]
    st.dataframe(normal[["mode", "cycles", "mean_context_confidence", "mean_robot_speed", "mean_ergonomic_risk", "alerts", "defects"]], use_container_width=True, hide_index=True)
    metric = st.selectbox("Comparison metric", ["mean_context_confidence", "mean_robot_speed", "mean_ergonomic_risk", "alerts", "defects", "packet_loss_rate"])
    st.plotly_chart(px.bar(normal, x="mode", y=metric, color="mode", template="plotly_dark", title=f"Observed synthetic result: {metric}"), use_container_width=True)
    st.download_button("EXPORT RESULTS JSON", RESULTS_PATH.read_bytes(), file_name="experiment_results.json", mime="application/json")


def analytics(factory: ResearchFactory):
    st.title("Analytics")
    events = current_events(factory, 5000)
    if events.empty: st.info("Run a cycle to populate analytics."); return
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.line(events.sort_values("id"), x="cycle", y="fatigue_index", color="department", template="plotly_dark", title="Synthetic fatigue by department"), use_container_width=True)
    with right:
        st.plotly_chart(px.scatter(events, x="workload_index", y="posture", color="department", template="plotly_dark", title="Workload versus posture indicator"), use_container_width=True)
    st.dataframe(events.head(100), use_container_width=True, hide_index=True)


def database(factory: ResearchFactory):
    st.title("Database")
    tables = read_sql("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")["name"].tolist()
    table = st.selectbox("Table", tables)
    limit = st.slider("Rows", 10, 500, 50)
    st.dataframe(read_sql(f"SELECT * FROM [{table}] ORDER BY rowid DESC LIMIT {limit}"), use_container_width=True, hide_index=True)
    st.download_button("EXPORT TABLE CSV", read_sql(f"SELECT * FROM [{table}] LIMIT {limit}").to_csv(index=False), file_name=f"{table}.csv", mime="text/csv")
    st.markdown("### Read-only SQL query")
    sql = st.text_area("SQL", "SELECT wt.department, AVG(ws.fatigue_index) AS mean_fatigue, AVG(ws.context_confidence) AS mean_confidence FROM worker_state AS ws JOIN wearable_telemetry AS wt ON wt.run_id = ws.run_id AND wt.cycle = ws.cycle AND wt.worker_id = ws.worker_id GROUP BY wt.department;", height=110)
    if st.button("RUN QUERY"):
        if not sql.lstrip().lower().startswith(("select", "with", "pragma")):
            st.error("Only SELECT, WITH, and PRAGMA queries are allowed.")
        else:
            try: st.dataframe(read_sql(sql), use_container_width=True, hide_index=True)
            except Exception as exc: st.error(str(exc))


def smart_glasses(factory: ResearchFactory):
    st.title("Smart Glasses")
    st.markdown("<div class='research-note'>Simulated smart-glasses interface — not a representation of a specific commercial device.</div>", unsafe_allow_html=True)
    stage = DEPARTMENTS[factory.state.vehicle_position]
    worker = factory.workers[stage]; robot = factory.robots[stage]; context = worker.context()
    st.markdown(f"""
    <div style='background:#050b14;border:1px solid #38bdf8;padding:28px;max-width:720px;min-height:390px;margin:12px auto;color:#e0f2fe'>
      <div style='color:#38bdf8;font-size:11px;letter-spacing:.18em'>AR WORKER VIEW / SIMULATION</div>
      <h2 style='font-size:25px!important;margin-top:28px'>STATION {stage.upper()}</h2>
      <p>TASK · {factory.departments[stage]['task']}</p><p>WORKER · {worker.worker_id}</p><p>ROBOT · {robot.robot_id} / {robot.state.upper()}</p>
      <hr style='border-color:#164e63'><p>STEP · {(factory.state.cycle % 8) + 1} / 8</p><p>SAFETY · {'REVIEW REQUIRED' if context['safety_score'] < .5 else 'NORMAL'}</p><p>WORKLOAD · {'ELEVATED' if context['workload_index'] > .7 else 'NORMAL'}</p><p>→ Continue task and confirm upper hinge</p>
    </div>
    """, unsafe_allow_html=True)


def system(factory: ResearchFactory):
    st.title("System")
    rows = [("Simulation Engine", "ONLINE"), ("Wearable Generator", "ONLINE"), ("Streaming/Event Loop", "ONLINE"), ("Context Engine", "ONLINE"), ("SQLite Database", "CONNECTED"), ("Dashboard", "ONLINE")]
    st.dataframe(pd.DataFrame(rows, columns=["component", "status"]), use_container_width=True, hide_index=True)
    st.json({"python": platform.python_version(), "streamlit": st.__version__, "database": DB_PATH.name, "cycle": factory.state.cycle, "last_update": factory.state.clock.isoformat(), "current_run": factory.run_id, "data_classification": "synthetic/simulated"})


def main():
    inject_theme()
    page = controls()
    factory = get_factory()
    header(factory)
    renderers = {"COMMAND CENTER": command_center, "FACTORY DIGITAL TWIN": digital_twin, "WORKER MONITORING": worker_monitoring, "ROBOT & MACHINE": robot_machine, "WEARABLE CONTEXT": wearable_context, "PRODUCTION": production, "SAFETY": safety, "EXPERIMENT LAB": experiment_lab, "ANALYTICS": analytics, "DATABASE": database, "SMART GLASSES": smart_glasses, "SYSTEM": system}
    renderers[page](factory)


if __name__ == "__main__":
    main()
