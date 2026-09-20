"""
Tests for EVA Academic Research Agent & Opportunity Matcher
Validates paper discovery, citation traceability, and resume scoring.
"""

import pytest
import asyncio
from backend.app.services.agents.research_agent import research_agent
from backend.app.services.agents.opportunity_agent import opportunity_agent
from backend.app.services.agents.resume_agent import resume_agent
from backend.app.services.integration_health_service import integration_health_service

@pytest.mark.asyncio
async def test_research_agent_paper_discovery():
    res = await research_agent.search_papers(query="Smart Glasses low latency audio", max_results=3)
    assert res["status"] == "SUCCESS"
    assert res["total_papers"] > 0
    assert len(res["papers"]) > 0
    assert "summary" in res
    
    # Check paper metadata structure
    top_p = res["papers"][0]
    assert "title" in top_p
    assert "authors" in top_p
    assert "published_date" in top_p
    assert "source" in top_p
    assert "doi" in top_p or "url" in top_p

@pytest.mark.asyncio
async def test_opportunity_matcher_with_user_profile():
    profile = resume_agent.get_profile()
    assert len(profile.skills) > 0
    assert "Robotics" in profile.education or "Computer Science" in profile.education

    res = await opportunity_agent.search_and_match(query="Robotics Intern", location="Bengaluru")
    assert res["status"] == "SUCCESS"
    assert res["total_matches"] > 0
    assert len(res["top_matches"]) > 0

    top_match = res["top_matches"][0]
    assert "match_score" in top_match
    assert top_match["match_score"] >= 50
    assert len(top_match["match_reasons"]) > 0
    assert "evidence" in top_match

def test_opportunity_application_human_confirmation():
    app_draft = opportunity_agent.prepare_application("opp_robo_01")
    assert app_draft["status"] == "APPLICATION_PREPARED"
    assert app_draft["requires_human_confirmation"] is True
    assert "confirmation_prompt" in app_draft

def test_integration_health_service_zero_secrets():
    health = integration_health_service.check_all_integrations()
    assert health["total_integrations"] >= 6
    assert "integrations" in health

    # Verify zero secrets leaked in health report
    for item in health["integrations"]:
        details_str = str(item.get("details", ""))
        assert "key" not in details_str.lower() or "configured" in details_str.lower() or "fallback" in details_str.lower() or "missing" in details_str.lower()
        assert "secret" not in details_str.lower() or "missing" in details_str.lower()
        assert "password" not in details_str.lower()
