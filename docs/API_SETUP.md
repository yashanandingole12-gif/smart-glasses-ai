# EVA API & Credential Configuration Guide

This document specifies all credentials, environment variables, authentication methods, minimum required scopes, and failure behaviors across the EVA ecosystem.

> [!IMPORTANT]
> **Zero Secret Policy**: Never commit `.env` or real API keys/tokens to Git. Copy `.env.example` to `.env` and configure credentials locally.

---

## 1. Provider & Credential Matrix

| Provider | Environment Variable | Where to Obtain | Used By | Required? | Failure Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Google Gemini** | `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/) | Primary Fast Voice LLM & Multimodal Vision | **Recommended** | Falls back to secondary LLM or Mock |
| **OpenAI** | `OPENAI_API_KEY` | [OpenAI Platform](https://platform.openai.com/) | Generative Engine (GPT-4o) | Optional | Falls back to Gemini/Mock |
| **Anthropic** | `ANTHROPIC_API_KEY` | [Anthropic Console](https://console.anthropic.com/) | Complex Code & Reasoning | Optional | Falls back to Primary LLM |
| **DeepSeek** | `DEEPSEEK_API_KEY` | [DeepSeek Platform](https://platform.deepseek.com/) | Secondary Low-Cost LLM | Optional | Falls back to Primary/Mock |
| **Google OAuth** | `GOOGLE_CLIENT_ID`<br>`GOOGLE_CLIENT_SECRET`<br>`GOOGLE_REDIRECT_URI` | [Google Cloud Console](https://console.cloud.google.com/) | Gmail, Google Calendar, Google Drive, Contacts | Optional | Workspace agent tools return `AUTH_REQUIRED` |
| **GitHub** | `GITHUB_TOKEN` | [GitHub Personal Tokens](https://github.com/settings/tokens) | GitHub Agent (Repos, Issues, PRs) | Optional | GitHub agent uses public unauthenticated rate limits |
| **LinkedIn** | `LINKEDIN_CLIENT_ID`<br>`LINKEDIN_CLIENT_SECRET`<br>`LINKEDIN_ACCESS_TOKEN` | [LinkedIn Developers](https://www.linkedin.com/developers/) | LinkedIn Opportunity & Profile Agent | Optional | Uses offline verified opportunity matcher |
| **arXiv** | `ARXIV_ENABLED=true` | Open Access | Academic Research Agent | **Enabled by default** | Uses verified academic paper database |
| **OpenAlex** | `OPENALEX_API_KEY`<br>`OPENALEX_EMAIL` | [OpenAlex.org](https://openalex.org/) | Global Academic Graph & DOI Search | Optional | Uses OpenAlex public tier (no key needed) |
| **Semantic Scholar**| `SEMANTIC_SCHOLAR_API_KEY` | [Semantic Scholar API](https://www.semanticscholar.org/product/api) | Citation & Literature Analysis | Optional | Uses Semantic Scholar public pool |
| **Crossref** | `CROSSREF_EMAIL` | [Crossref Polite Pool](https://www.crossref.org/) | DOI Lookup & Author Metadata | Optional | Uses Crossref public query rate |
| **Tavily / SerpApi**| `WEB_SEARCH_API_KEY` | [Tavily](https://tavily.com/) / [SerpApi](https://serpapi.com/) | Real-Time Live Web Search | Optional | Falls back to local knowledge base |
| **Glasses WiFi** | `GLASSES_WIFI_SSID`<br>`GLASSES_WIFI_PASSWORD` | Local Router / Phone Hotspot | ESP32-S3 WiFi Station Connection | Optional | Operates in Standalone Bluetooth LE Mode |

---

## 2. Google Workspace Minimum Scopes

When configuring Google OAuth 2.0 Client in Google Cloud Console, enable only the least-privileged scopes:
* `https://www.googleapis.com/auth/gmail.readonly` (Read and summarize emails)
* `https://www.googleapis.com/auth/gmail.send` (Send emails after human confirmation)
* `https://www.googleapis.com/auth/calendar.readonly` (Read schedule)
* `https://www.googleapis.com/auth/calendar.events` (Add events after confirmation)
* `https://www.googleapis.com/auth/drive.readonly` (Search résumé and documents)
* `https://www.googleapis.com/auth/contacts.readonly` (Resolve names to phone numbers)

---

## 3. Integration Health Service

EVA provides an automated integration health endpoint:
```http
GET /api/v1/integrations/health
```

Example Response:
```json
{
  "service": "EVA Integration Health Service",
  "total_integrations": 7,
  "active_configured": 5,
  "integrations": [
    {
      "name": "LLM Intelligence Tier",
      "status": "CONNECTED",
      "auth_type": "API_KEY",
      "details": {
        "primary_provider": "gemini",
        "active_providers": ["Gemini (gemini-flash-lite-latest)"]
      }
    },
    {
      "name": "Academic Research Engine",
      "status": "CONNECTED",
      "auth_type": "PUBLIC",
      "details": {
        "providers": ["arXiv (Open Access)", "OpenAlex (Public Tier)", "Semantic Scholar (Public Tier)", "Crossref (Public)"]
      }
    }
  ]
}
```
