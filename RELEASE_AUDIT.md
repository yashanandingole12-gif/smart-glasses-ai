# Research Factory Release Audit

Date: 2026-09-08

## Scope

This audit covers the wearable-context smart-manufacturing research package, not every Android/backend feature in the parent smart-glasses repository.

## Canonical files for Git upload

- `factory_experiment.py`: synthetic factory engine, event loop, context policy, SQLite schema, persistence
- `research_dashboard.py`: Streamlit dashboard, factory floor, realtime stepping, analytics, SQL query runner, smart-glasses view
- `run_research_experiments.py`: baseline, ablation, and failure-scenario runner
- `test_research_factory.py`: focused automated tests
- `factory_layout.svg`: author-generated/reference-inspired static floor-plan visual
- `requirements-research.txt`: research dashboard dependencies
- `README_RESEARCH.md`: technical setup and architecture
- `WALKTHROUGH_RESEARCH_FACTORY.md`: operational walkthrough
- `FINAL_REVIEW_PAPER.md`: canonical review paper and proposed experimental framework

Generated SQLite files, experiment logs, JSON results, CSV exports, HTML snapshots, and earlier prototype scripts are excluded from the release by `.gitignore`.

## Verification performed

### Automated tests

Command:

```powershell
python -m unittest discover -v
```

Result: 3 research tests passed. The repository emitted a Starlette/httpx deprecation warning from an existing backend test dependency, but no test failed.

### Python compilation

Command:

```powershell
python -m py_compile factory_experiment.py research_dashboard.py run_research_experiments.py test_research_factory.py
```

Result: passed.

### Experiment execution

Command:

```powershell
python run_research_experiments.py
```

Result: completed baseline, ablation, and abnormal-scenario runs. The output is synthetic and is not included in Git.

### Database validation

The experiment generated and persisted synthetic telemetry, worker-state, context, safety, production, and factory-state records in `research_factory.sqlite`. The database itself is ignored because it is generated output.

### Dashboard validation

The Streamlit dashboard was served successfully and returned HTTP 200. The active dashboard database is `research_factory.sqlite` when running locally.

## Errors encountered and resolution

1. **Missing Plotly**: installed Plotly into the active Python 3.13 environment and retained the dependency in `requirements-research.txt`.
2. **Streamlit launched from the wrong directory**: documented that commands must run from the repository root.
3. **Ambiguous `fatigue_index` in dashboard SQL**: qualified columns using `wt`, `ws`, and `ce` table aliases.
4. **Incorrect `department` source in SQL**: changed the query to use `wt.department` because `worker_state` does not store department.
5. **SQLite file locking on Windows**: explicitly committed and closed SQLite connections in the production persistence path and test.
6. **Duplicate records during repeated realtime persistence**: persistence now replaces the current run's event rows before writing the updated event history.
7. **Incorrect run-mode metadata**: persisted the actual `none`, `motion`, `physiology`, `glasses`, or `full` mode.
8. **Shell quoting errors during manual SQL checks**: replaced fragile nested one-line commands with simpler validation commands.
9. **Malformed earlier static HTML dashboard**: selected the Streamlit dashboard as the canonical UI and excluded the generated HTML snapshot.

## Originality and plagiarism check

This repository does not include a licensed plagiarism-detection service or a complete bibliographic screening database, so no responsible claim of zero plagiarism can be made. The following checks were performed:

- searched repository Markdown for repeated distinctive phrases and marketing language;
- compared the three paper drafts by SHA-256 and identified them as distinct drafts rather than duplicate copies;
- removed the earlier slogan-like framing from the canonical paper;
- reframed claims as supported, proposed, or synthetic;
- cited standards and official sources where they are used;
- marked the factory architecture, diagrams, simulation, and metrics as author-generated or proposed;
- avoided presenting synthetic values as human-subject or industrial measurements.

Before journal submission, run the final paper through the institution's approved similarity checker and manually inspect every matched passage. Similarity is not by itself plagiarism: standard terminology, titles, legal names, and cited technical language may produce legitimate matches.

## Release decision

The research package is technically ready for a Git commit after reviewing the staged file list. It is not ready to claim industrial deployment, clinical validity, or publication acceptance. A remote push should occur only after the user reviews the staged files and confirms the destination repository.

## UI improvement recommendations

1. Add a run comparison page with paired baseline/full KPI cards and confidence intervals across seeds.
2. Add a visible data-status strip showing synthetic data, run ID, seed, sample age, packet loss, and confidence.
3. Add a department detail drawer instead of requiring hover for worker/robot state.
4. Add a timeline scrubber for replaying persisted factory states.
5. Add alert acknowledgment and an audit trail for every robot action.
6. Add CSV/JSON export for selected runs, not the whole database by default.
7. Replace free-form SQL execution with read-only validation or a query library before public deployment.
8. Add accessibility labels, color-blind-safe status symbols, and a high-contrast mode.
9. Keep the supplied/reference-inspired floor image as context, but clearly separate it from the synthetic operational overlay.

## Paper improvement recommendations

1. Add a reproducible search string, date range, databases searched, screening criteria, and a PRISMA flow before calling the review systematic.
2. Replace broad novelty claims with the narrower contribution: cross-layer, uncertainty-aware, ablation-based evaluation.
3. Report repeated-seed synthetic results with confidence intervals and effect sizes rather than one run.
4. Define a ground truth for each injected event and report precision, recall, F1, false-positive rate, and detection latency.
5. Separate worker-state estimation from robot safety control; wearable inference must not replace safety-rated mechanisms.
6. Add a human-subject protocol for later validation, including consent, calibration, privacy, workload instruments, and ethics approval.
7. Add a cost sensitivity analysis covering device management, calibration, network, storage, privacy, and human intervention.
8. Use the final paper's limitations section as a boundary on all claims.
