"""
Integration Health Service for EVA
Validates and reports connection status across all external integrations:
LLMs, Google Workspace, GitHub, LinkedIn, Academic Research, and Search providers.
Guarantees zero leakage of secrets or token values.
"""

import logging
from typing import Dict, List, Any
from backend.app.integrations import integration_settings, IntegrationStatus
from backend.app.services.token_service import token_service

logger = logging.getLogger("eva.services.integration_health")

class IntegrationHealthService:
    def __init__(self):
        logger.info("IntegrationHealthService initialized.")

    def check_all_integrations(self) -> Dict[str, Any]:
        """
        Comprehensive health check of all active and optional integration endpoints.
        """
        statuses = [
            self._check_llm_status(),
            self._check_google_workspace_status(),
            self._check_github_status(),
            self._check_linkedin_status(),
            self._check_research_providers_status(),
            self._check_web_search_status(),
            self._check_opportunity_providers_status()
        ]

        # Overall health summary
        configured_count = sum(1 for s in statuses if s.status in ["CONNECTED", "AUTH_REQUIRED"])
        total_count = len(statuses)

        return {
            "service": "EVA Integration Health Service",
            "version": "1.0.0",
            "total_integrations": total_count,
            "active_configured": configured_count,
            "integrations": [s.model_dump() for s in statuses]
        }

    def _check_llm_status(self) -> IntegrationStatus:
        has_gemini = bool(integration_settings.GEMINI_API_KEY)
        has_openai = bool(integration_settings.OPENAI_API_KEY)
        has_anthropic = bool(integration_settings.ANTHROPIC_API_KEY)
        has_deepseek = bool(integration_settings.DEEPSEEK_API_KEY)

        if has_gemini or has_openai or has_anthropic or has_deepseek:
            status = "CONNECTED"
            active_providers = []
            if has_gemini: active_providers.append(f"Gemini ({integration_settings.GEMINI_MODEL})")
            if has_openai: active_providers.append(f"OpenAI ({integration_settings.OPENAI_MODEL})")
            if has_anthropic: active_providers.append(f"Anthropic ({integration_settings.ANTHROPIC_MODEL})")
            if has_deepseek: active_providers.append(f"DeepSeek ({integration_settings.DEEPSEEK_MODEL})")

            return IntegrationStatus(
                name="LLM Intelligence Tier",
                status=status,
                auth_type="API_KEY",
                is_optional=False,
                details={
                    "primary_provider": integration_settings.PRIMARY_LLM_PROVIDER,
                    "active_providers": active_providers,
                    "fallback": integration_settings.FALLBACK_LLM_PROVIDER
                }
            )
        else:
            return IntegrationStatus(
                name="LLM Intelligence Tier",
                status="NOT_CONFIGURED",
                auth_type="API_KEY",
                is_optional=False,
                details={"fallback": "Local Mock / Deterministic Rule Engine"}
            )

    def _check_google_workspace_status(self) -> IntegrationStatus:
        has_oauth_config = bool(integration_settings.GOOGLE_CLIENT_ID and integration_settings.GOOGLE_CLIENT_SECRET)
        token_info = token_service.get_status("default_user")

        if not has_oauth_config:
            return IntegrationStatus(
                name="Google Workspace (Gmail/Calendar/Drive)",
                status="NOT_CONFIGURED",
                auth_type="OAUTH2",
                is_optional=True,
                details={"message": "OAuth Client ID / Secret missing in .env"}
            )

        if token_info and token_info.get("connected"):
            return IntegrationStatus(
                name="Google Workspace (Gmail/Calendar/Drive)",
                status="CONNECTED",
                auth_type="OAUTH2",
                is_optional=True,
                details={
                    "user_email": token_info.get("email", "Authenticated User"),
                    "scopes_count": len(integration_settings.GOOGLE_OAUTH_SCOPES),
                    "services": ["Gmail", "Calendar", "Drive", "Contacts"]
                }
            )
        else:
            return IntegrationStatus(
                name="Google Workspace (Gmail/Calendar/Drive)",
                status="AUTH_REQUIRED",
                auth_type="OAUTH2",
                is_optional=True,
                details={
                    "oauth_configured": True,
                    "auth_url": "/api/v1/auth/google/login",
                    "message": "User login required to authorize Gmail/Calendar tools"
                }
            )

    def _check_github_status(self) -> IntegrationStatus:
        has_token = bool(integration_settings.GITHUB_TOKEN)
        has_app = bool(integration_settings.GITHUB_APP_ID and integration_settings.GITHUB_PRIVATE_KEY)

        if has_token or has_app:
            return IntegrationStatus(
                name="GitHub Agent",
                status="CONNECTED",
                auth_type="TOKEN" if has_token else "GITHUB_APP",
                is_optional=True,
                details={
                    "auth_method": "Personal Access Token" if has_token else "GitHub App",
                    "capabilities": ["Repository Inspection", "Issues", "Pull Requests", "Code Search"]
                }
            )
        else:
            return IntegrationStatus(
                name="GitHub Agent",
                status="NOT_CONFIGURED",
                auth_type="TOKEN",
                is_optional=True,
                details={"message": "GITHUB_TOKEN not configured"}
            )

    def _check_linkedin_status(self) -> IntegrationStatus:
        has_oauth = bool(integration_settings.LINKEDIN_CLIENT_ID and integration_settings.LINKEDIN_CLIENT_SECRET)
        has_token = bool(integration_settings.LINKEDIN_ACCESS_TOKEN)

        if has_token:
            return IntegrationStatus(
                name="LinkedIn Integration",
                status="CONNECTED",
                auth_type="OAUTH2",
                is_optional=True,
                details={
                    "capabilities": ["Profile Inspection", "Job Preparation", "Opportunity Matching"],
                    "note": "Submissions gated by user confirmation"
                }
            )
        elif has_oauth:
            return IntegrationStatus(
                name="LinkedIn Integration",
                status="AUTH_REQUIRED",
                auth_type="OAUTH2",
                is_optional=True,
                details={"auth_url": "/api/v1/auth/linkedin/login"}
            )
        else:
            return IntegrationStatus(
                name="LinkedIn Integration",
                status="NOT_CONFIGURED",
                auth_type="OAUTH2",
                is_optional=True,
                details={"message": "LINKEDIN_CLIENT_ID not configured"}
            )

    def _check_research_providers_status(self) -> IntegrationStatus:
        active_providers = []
        if integration_settings.ARXIV_ENABLED:
            active_providers.append("arXiv (Open Access)")
        if integration_settings.OPENALEX_API_KEY or integration_settings.OPENALEX_EMAIL:
            active_providers.append("OpenAlex (Academic Graph)")
        else:
            active_providers.append("OpenAlex (Public Tier)")
        if integration_settings.SEMANTIC_SCHOLAR_API_KEY:
            active_providers.append("Semantic Scholar (Authenticated)")
        else:
            active_providers.append("Semantic Scholar (Public Tier)")
        if integration_settings.CROSSREF_EMAIL:
            active_providers.append("Crossref (Polite Pool)")
        else:
            active_providers.append("Crossref (Public)")

        return IntegrationStatus(
            name="Academic Research Engine",
            status="CONNECTED",
            auth_type="PUBLIC",
            is_optional=False,
            details={
                "providers": active_providers,
                "citation_traceability": "Enabled (DOIs, authors, publication years preserved)"
            }
        )

    def _check_web_search_status(self) -> IntegrationStatus:
        has_key = bool(integration_settings.WEB_SEARCH_API_KEY)
        engine = integration_settings.WEB_SEARCH_ENGINE

        if has_key:
            return IntegrationStatus(
                name="Live Web Search",
                status="CONNECTED",
                auth_type="API_KEY",
                is_optional=True,
                details={"engine": engine}
            )
        else:
            return IntegrationStatus(
                name="Live Web Search",
                status="NOT_CONFIGURED",
                auth_type="API_KEY",
                is_optional=True,
                details={"engine": engine, "fallback": "Local knowledge base & Academic research"}
            )

    def _check_opportunity_providers_status(self) -> IntegrationStatus:
        providers = []
        if integration_settings.LINKEDIN_OPPORTUNITY_ENABLED:
            providers.append("LinkedIn Opportunity Matcher")
        if integration_settings.INTERNSHALA_ENABLED:
            providers.append("Internshala (Official)")
        if integration_settings.INDEED_ENABLED:
            providers.append("Indeed (Authorized)")

        return IntegrationStatus(
            name="Opportunity & Career Matcher",
            status="CONNECTED" if providers else "NOT_CONFIGURED",
            auth_type="NONE",
            is_optional=True,
            details={
                "active_providers": providers,
                "matching_algorithm": "UserProfile Context Matcher (Skills, Experience, Projects)"
            }
        )

integration_health_service = IntegrationHealthService()
