"""
Test Suite for EVA Master 3-Tier Architecture & Autonomous Agents
Validates Rule-Based Engine, LinkedIn Agent, Research Agent (arXiv),
Email Agent, GitHub Agent, Workspace Agent, and Latency Tracker.
"""

import pytest
from backend.app.services.agents.linkedin_agent import LinkedInAgent
from backend.app.services.agents.research_agent import ResearchAgent
from backend.app.services.agents.email_agent import EmailAgent
from backend.app.services.agents.github_agent import GitHubAgent
from backend.app.services.agents.workspace_agent import WorkspaceAgent
from backend.app.services.latency_tracker import RequestLatencyTracker

@pytest.mark.asyncio
async def test_linkedin_agent_opportunity_search_and_matching():
    agent = LinkedInAgent()
    res = await agent.search_opportunities(
        query="robotics",
        location="India",
        user_skills=["Python", "C++", "ROS2"]
    )
    assert res["status"] == "SUCCESS"
    assert res["total_found"] >= 1
    first_opp = res["opportunities"][0]
    assert "Python" in first_opp["matched_skills"]
    assert first_opp["match_percentage"] > 0
    assert "apply_url" in first_opp

@pytest.mark.asyncio
async def test_linkedin_agent_honest_application_preparation():
    agent = LinkedInAgent()
    prep = await agent.prepare_application(
        opportunity_id="opp_rob_01",
        user_profile={"name": "Yash", "email": "yash@example.com"}
    )
    assert prep["status"] == "PREPARED_REQUIRES_CONFIRMATION"
    assert prep["opportunity_id"] == "opp_rob_01"
    assert "application_payload" in prep
    assert prep["application_payload"]["applicant_name"] == "Yash"

@pytest.mark.asyncio
async def test_research_agent_real_paper_discovery():
    agent = ResearchAgent()
    res = await agent.search_papers(query="multimodal AI robotics", max_results=3)
    assert res["status"] == "SUCCESS"
    assert res["total_papers"] >= 1
    assert len(res["papers"]) >= 1

    first_paper = res["papers"][0]
    assert "title" in first_paper
    assert "authors" in first_paper
    assert len(first_paper["authors"]) >= 1
    assert "arxiv_id" in first_paper
    assert "summary" in res
    assert first_paper["title"] in res["summary"]

@pytest.mark.asyncio
async def test_github_agent_repository_search():
    agent = GitHubAgent()
    res = await agent.search_repositories(query="smart-glasses-ai")
    assert res["status"] == "SUCCESS"
    assert res["total_found"] >= 1
    assert len(res["repositories"]) >= 1
    first_repo = res["repositories"][0]
    assert "name" in first_repo
    assert "url" in first_repo

@pytest.mark.asyncio
async def test_workspace_agent_schedule_and_drive():
    agent = WorkspaceAgent()
    overview = await agent.get_overview()
    assert overview["status"] == "SUCCESS"
    assert "calendar_events_count" in overview

    drive_res = await agent.search_drive_documents(query="robotics")
    assert drive_res["status"] == "SUCCESS"
    assert len(drive_res["documents"]) >= 1

def test_request_latency_tracker_breakdown():
    tracker = RequestLatencyTracker(request_id="req_test_123", session_id="sess_456")
    tracker.start_stage("wake")
    tracker.end_stage("wake", success=True)
    
    tracker.start_stage("stt")
    tracker.end_stage("stt", success=True)

    tracker.start_stage("router")
    tracker.end_stage("router", success=True)

    summary = tracker.get_summary()
    assert summary["request_id"] == "req_test_123"
    assert "total_latency_ms" in summary
    assert "wake" in summary["stages"]
    assert "stt" in summary["stages"]
    assert "router" in summary["stages"]
    assert summary["stages"]["wake"]["success"] is True
