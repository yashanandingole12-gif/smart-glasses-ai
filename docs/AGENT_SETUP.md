# EVA Agent Ecosystem & Tool Security Guide

## 1. Composable Multi-Agent Architecture

The EVA Agentic tier orchestrates 8 specialized, composable agents:

```
                               ┌────────────────────────────────┐
                               │       Agent Orchestrator       │
                               └───────────────┬────────────────┘
                                               │
       ┌───────────────┬───────────────┬───────┴───────┬───────────────┬───────────────┐
       ▼               ▼               ▼               ▼               ▼               ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│  Email Agent ││  Workspace   ││ GitHub Agent ││LinkedIn Agent││Research Agent││ Opportunity  │
│(Gmail/OAuth) ││  Coordinator ││(Repos/Issues)││ (Job Search) ││(arXiv/OpenAl)││   Matcher    │
└──────────────┘└──────────────┘└──────────────┘└──────────────┘└──────────────┘└──────────────┘
```

---

## 2. Agent Catalog & Capabilities

### 1. Email Agent (`email_agent.py`)
* **Backend**: Google OAuth 2.0 (`gmail.readonly`, `gmail.send`, `gmail.compose`).
* **Capabilities**: Search emails, read threads, filter by sender/date/unread, compose drafts, send replies.
* **Security**: Never exposes OAuth access/refresh tokens to the LLM. LLM issues typed tool calls (`gmail.search`, `gmail.draft`).

### 2. Google Workspace Agent (`workspace_agent.py`)
* **Capabilities**: Unified schedule overview, calendar conflict detection, Google Drive document search, and Google Contacts lookup.
* **Tools**: `calendar.get_events`, `calendar.create_event`, `drive.search`, `contacts.search`.

### 3. GitHub Agent (`github_agent.py`)
* **Capabilities**: Repository search, issue inspection, pull request tracking, and code exploration.
* **Authentication**: Personal Access Token (`repo`, `read:user`) or GitHub App.

### 4. LinkedIn Agent (`linkedin_agent.py`)
* **Capabilities**: Official job discovery, requirements extraction, and application preparation.
* **Safeguards**: Never claims an application was submitted without explicit API confirmation. Halts at human-confirmation step.

### 5. Academic Research Agent (`research_agent.py`)
* **Providers**: arXiv, OpenAlex, Semantic Scholar, Crossref.
* **Zero Hallucination**: Preserves verified DOIs, author lists, publication years, and abstract snippets.

### 6. Opportunity Matcher & Resume Agent (`opportunity_agent.py`, `resume_agent.py`)
* **UserProfile**: Education, skills, robotics experience, projects, preferred locations, and career objectives.
* **Scoring Algorithm**: Computes fit score (0-100%) with explicit matching reasons, missing criteria, and evidence summary.
* **Application Safeguards**: Prepares application package and enforces mandatory user confirmation before submission.

### 7. Web Research Agent (`web_research_agent.py`)
* **Providers**: Pluggable Tavily, SerpApi, or local knowledge graph.

---

## 3. Human Confirmation & Risk Gating

High-impact actions require explicit two-step user confirmation:
* **Sending Emails** (`RiskLevel.HIGH`)
* **Sending SMS Messages** (`RiskLevel.HIGH`)
* **Creating / Modifying Calendar Events** (`RiskLevel.MEDIUM`)
* **Submitting Job Applications** (`RiskLevel.CRITICAL`)

Read-only operations (`RiskLevel.READ`) execute automatically without interrupting user flow.
