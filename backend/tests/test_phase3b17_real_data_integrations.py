import pytest
from fastapi.testclient import TestClient
import io
import re

from backend.app.main import app

client = TestClient(app)

def test_google_auth_status_endpoint():
    """Verify GET /api/v1/auth/status returns valid auth status."""
    resp = client.get("/api/v1/auth/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "connected" in data
    assert "email" in data

def test_external_integrations_status_endpoint():
    """Verify GET /api/v1/integrations/status and github status."""
    resp = client.get("/api/v1/integrations/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "integrations" in data
    assert "github" in data["integrations"]
    assert "linkedin" in data["integrations"]
    assert "google_workspace" in data["integrations"]

    gh_resp = client.get("/api/v1/integrations/github/status?repo=org/smart-glasses-ai")
    assert gh_resp.status_code == 200
    gh_data = gh_resp.json()
    assert "github" in gh_data
    assert "repository" in gh_data["github"]
    assert "workflow_status" in gh_data["github"]

def test_staff_desk_upload_and_query_flow():
    """Verify staff can upload a dataset and user can query it via chat."""
    csv_content = b"Month,Revenue,Burn,Runway_Months\nJan,120000,45000,18\nFeb,145000,42000,20\nMar,180000,40000,24\n"
    
    files = {"file": ("q1_financials.csv", io.BytesIO(csv_content), "text/csv")}
    upload_resp = client.post("/api/v1/desk/upload", files=files)
    assert upload_resp.status_code == 200
    upload_data = upload_resp.json()
    assert upload_data["status"] == "uploaded"
    assert upload_data["dataset"]["filename"] == "q1_financials.csv"
    assert upload_data["dataset"]["row_count"] == 3

    # Check latest dataset endpoint
    latest_resp = client.get("/api/v1/desk/latest")
    assert latest_resp.status_code == 200
    latest_data = latest_resp.json()
    assert latest_data["available"] is True
    assert latest_data["dataset"]["filename"] == "q1_financials.csv"

    # Query via chat
    chat_resp = client.post("/api/v1/chat", json={
        "sessionId": "test_desk_session",
        "userMessage": "Analyze the dataset uploaded by staff",
        "telemetry": {"batteryPercentage": 90, "locationName": "Office"}
    })
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert "q1_financials.csv" in chat_data["text"] or "dataset" in chat_data["text"].lower()

def test_github_chat_query_routing():
    """Verify chat query about github repository status responds with live/connector status."""
    chat_resp = client.post("/api/v1/chat", json={
        "sessionId": "test_gh_session",
        "userMessage": "What is the status of our github repository?",
        "telemetry": {"batteryPercentage": 85}
    })
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert "github" in chat_data["text"].lower() or "repository" in chat_data["text"].lower() or "ci" in chat_data["text"].lower()

def test_web_ui_contains_zero_emojis():
    """Verify that the web console does not contain decorative emojis."""
    resp = client.get("/")
    assert resp.status_code == 200
    html_content = resp.text
    
    # Range of common emoji Unicode code points
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-a
        "]+", 
        flags=re.UNICODE
    )
    matches = emoji_pattern.findall(html_content)
    assert len(matches) == 0, f"Found emojis in Web UI: {matches}"
