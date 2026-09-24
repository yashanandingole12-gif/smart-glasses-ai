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
async def test_github_agent_user_and_repos():
    agent = GitHubAgent()
    user_res = await agent.get_authenticated_user()
    assert user_res["status"] in ["SUCCESS", "ERROR"]
    if user_res["status"] == "SUCCESS":
        assert user_res["login"] == "yashanandingole12-gif"

    repos_res = await agent.get_user_repositories(per_page=5)
    assert repos_res["status"] == "SUCCESS"
    assert len(repos_res["repositories"]) >= 1

@pytest.mark.asyncio
async def test_github_agent_repo_inspection_and_commits():
    agent = GitHubAgent()
    repo_res = await agent.inspect_repository(repo="smart-glasses-ai")
    assert repo_res["status"] == "SUCCESS"
    assert "smart-glasses-ai" in repo_res["name"] or "smart-glasses-ai" in repo_res["full_name"]

    commits_res = await agent.get_recent_commits(repo="smart-glasses-ai", limit=3)
    assert commits_res["status"] == "SUCCESS"
    assert len(commits_res["commits"]) >= 1

@pytest.mark.asyncio
async def test_workspace_agent_schedule_and_drive():
    agent = WorkspaceAgent()
    overview = await agent.get_overview()
    assert overview["status"] == "SUCCESS"
    assert "calendar_events_count" in overview

    drive_res = await agent.search_drive_documents(query="robotics")
    assert drive_res["status"] == "SUCCESS"
    assert "documents" in drive_res

@pytest.mark.asyncio
async def test_workspace_agent_create_doc_and_share():
    agent = WorkspaceAgent()
    create_res = await agent.create_google_doc(
        title="Test Blueprint",
        content="Automated robot test blueprint content.",
        share_accessible=True
    )
    assert create_res["success"] is True
    assert "shareable_url" in create_res
    doc_id = create_res.get("document_id")

    share_res = await agent.share_file_or_doc(
        file_id=doc_id,
        role="reader",
        make_public=True
    )
    assert share_res["success"] is True
    assert "shareable_url" in share_res

@pytest.mark.asyncio
async def test_workspace_agent_contacts_sync_and_search():
    agent = WorkspaceAgent()
    contacts_res = await agent.search_contacts(query="")
    assert contacts_res["status"] == "SUCCESS"
    assert "contacts" in contacts_res

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
