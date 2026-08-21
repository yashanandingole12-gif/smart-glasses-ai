import pytest
from backend.app.config import settings

@pytest.fixture(autouse=True)
def default_mock_llm_for_unit_tests(monkeypatch, request):
    """
    Keep mock LLM active for automated test suites to ensure fast, deterministic tests,
    while allowing explicit live provider tests (e.g. Gemini) when requested.
    """
    if "gemini" in request.node.name:
        return
    monkeypatch.setattr(settings, "LLM_PROVIDER", "mock")
