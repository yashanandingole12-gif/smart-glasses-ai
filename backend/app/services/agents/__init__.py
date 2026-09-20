"""
EVA Agentic Engine Subsystem
Contains autonomous agents for LinkedIn, Email, GitHub, Google Workspace, and Research-Paper Discovery.
"""

from .linkedin_agent import LinkedInAgent
from .email_agent import EmailAgent
from .github_agent import GitHubAgent
from .workspace_agent import WorkspaceAgent
from .research_agent import ResearchAgent

__all__ = [
    "LinkedInAgent",
    "EmailAgent",
    "GitHubAgent",
    "WorkspaceAgent",
    "ResearchAgent",
]
