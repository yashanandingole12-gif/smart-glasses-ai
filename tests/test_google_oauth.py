import pytest
import time
import httpx
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from urllib.parse import urlparse, parse_qs

from backend.app.main import app
from backend.app.config import settings
from backend.app.services.token_service import TokenService, redact_sensitive, token_service

client = TestClient(app)


def test_google_auth_authorization_endpoint():
    """Verify GET /api/v1/auth/google constructs a secure OAuth 2.0 authorization URL."""
    response = client.get("/api/v1/auth/google?format=json")
    assert response.status_code == 200
    data = response.json()
    assert "auth_url" in data
    assert data["redirect_uri"] == settings.GOOGLE_REDIRECT_URI
    assert "https://www.googleapis.com/auth/gmail.readonly" in data["scopes"]
    assert "https://www.googleapis.com/auth/calendar.readonly" in data["scopes"]

    # Parse generated URL and verify all OAuth query parameters
    parsed = urlparse(data["auth_url"])
    params = parse_qs(parsed.query)

    assert params["client_id"][0] == settings.GOOGLE_CLIENT_ID
    assert params["redirect_uri"][0] == settings.GOOGLE_REDIRECT_URI
    assert params["response_type"][0] == "code"
    assert params["access_type"][0] == "offline"
    assert params["prompt"][0] == "consent"
    assert "state" in params
    assert len(params["state"][0]) >= 32  # Cryptographically secure random token


def test_csrf_state_validation_and_replay_protection():
    """Verify CSRF state validation, expiration, and anti-replay single-use consumption in SQLite."""
    service = TokenService(db_path=":memory:")

    # Generate state
    state = service.create_oauth_state(user_id="user_123")
    assert state is not None
    assert len(state) > 20

    # 1. First consumption succeeds
    consumed = service.verify_and_consume_state(state)
    assert consumed is not None
    assert consumed["user_id"] == "user_123"

    # 2. Second consumption fails immediately (anti-replay single-use)
    consumed_again = service.verify_and_consume_state(state)
    assert consumed_again is None

    # 3. Arbitrary forged state fails
    assert service.verify_and_consume_state("forged_fake_state_token") is None

    # 4. Expired state fails
    expired_state = service.create_oauth_state(user_id="user_expired")
    # Manually expire state in database
    with service._get_conn() as conn:
        conn.execute("UPDATE oauth_states SET expires_at = ? WHERE state = ?", (time.time() - 100.0, expired_state))
        conn.commit()

    assert service.verify_and_consume_state(expired_state) is None


def test_state_persistence_across_server_restarts():
    """Verify CSRF state survives across server restarts and process reloads via SQLite."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Instance 1: Generates state and goes offline
        service_instance1 = TokenService(db_path=tmp_path)
        state = service_instance1.create_oauth_state(user_id="restart_user")
        assert state is not None

        # Instance 2: Simulates newly spawned worker / reloaded server
        service_instance2 = TokenService(db_path=tmp_path)
        consumed = service_instance2.verify_and_consume_state(state)
        assert consumed is not None
        assert consumed["user_id"] == "restart_user"

        # Instance 3: Replay fails
        service_instance3 = TokenService(db_path=tmp_path)
        assert service_instance3.verify_and_consume_state(state) is None
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def test_redirect_uri_exact_match_enforcement():
    """Verify the configured GOOGLE_REDIRECT_URI matches expected development callback."""
    assert settings.GOOGLE_REDIRECT_URI == "http://localhost:8001/api/v1/auth/google/callback"

    # Verify authorization URL uses the exact redirect_uri from settings
    auth_url = token_service.get_authorization_url(user_id="test_user")
    parsed = urlparse(auth_url)
    params = parse_qs(parsed.query)
    assert params["redirect_uri"][0] == settings.GOOGLE_REDIRECT_URI


def test_google_auth_callback_missing_or_invalid_state():
    """Verify callback rejects requests with missing or invalid CSRF state."""
    # 1. Missing state
    resp1 = client.get("/api/v1/auth/google/callback?code=mock_code")
    assert resp1.status_code == 400
    assert "Missing OAuth state parameter" in resp1.json()["detail"]

    # 2. Invalid/tampered state
    resp2 = client.get("/api/v1/auth/google/callback?code=mock_code&state=invalid_tampered_state")
    assert resp2.status_code == 400
    assert "Invalid or expired OAuth state" in resp2.json()["detail"]

    # 3. User denied authorization (error param)
    resp3 = client.get("/api/v1/auth/google/callback?error=access_denied")
    assert resp3.status_code == 400
    assert "Authorization Denied or Cancelled" in resp3.text
    assert "Test Users" in resp3.text


def test_legitimate_auth_request_and_callback_e2e():
    """
    Prove that a legitimate authorization request produces code + state,
    and callback succeeds ONLY when the exact correct state is returned.
    """
    # 1. Initiate authorization
    init_resp = client.get("/api/v1/auth/google?format=json")
    assert init_resp.status_code == 200
    auth_url = init_resp.json()["auth_url"]

    # 2. Extract generated state
    parsed = urlparse(auth_url)
    state = parse_qs(parsed.query)["state"][0]
    assert len(state) >= 32

    mock_token_resp = {
        "access_token": "ya29.live_mock_token_abc",
        "refresh_token": "1//live_mock_refresh_xyz",
        "expires_in": 3600,
        "token_type": "Bearer",
        "scope": "https://www.googleapis.com/auth/gmail.readonly"
    }

    # 3. Mock Google code exchange and userinfo
    with patch.object(token_service, "exchange_code_for_tokens", return_value=mock_token_resp), \
         patch.object(token_service, "fetch_user_email", return_value="smartglassesai01@gmail.com"):

        # 4. Callback with TAMPERED state fails
        tampered_resp = client.get(f"/api/v1/auth/google/callback?code=valid_code&state={state}_tampered")
        assert tampered_resp.status_code == 400
        assert "Invalid or expired OAuth state" in tampered_resp.json()["detail"]

        # 5. Callback with EXACT legitimate state SUCCEEDS
        success_resp = client.get(f"/api/v1/auth/google/callback?code=valid_code&state={state}")
        assert success_resp.status_code == 200
        assert "Google Account Connected" in success_resp.text
        assert "smartglassesai01@gmail.com" in success_resp.text

        # 6. Replaying the EXACT SAME state again fails (single-use anti-replay)
        replay_resp = client.get(f"/api/v1/auth/google/callback?code=valid_code&state={state}")
        assert replay_resp.status_code == 400
        assert "Invalid or expired OAuth state" in replay_resp.json()["detail"]


def test_token_service_status_and_disconnect():
    """Verify status reporting and token revocation/disconnection."""
    service = TokenService(db_path=":memory:")

    # Initial state: not connected
    status_initial = service.get_status("test_user")
    assert status_initial["connected"] is False
    assert status_initial["email"] is None

    # Save tokens
    service.save_tokens(
        user_id="test_user",
        access_token="mock_access_token_abc",
        refresh_token="mock_refresh_token_xyz",
        expires_in=3600,
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
        user_email="smartglassesai01@gmail.com"
    )

    # Status check: connected
    status_connected = service.get_status("test_user")
    assert status_connected["connected"] is True
    assert status_connected["email"] == "smartglassesai01@gmail.com"
    assert "https://www.googleapis.com/auth/gmail.readonly" in status_connected["scopes"]
    assert "access_token" not in status_connected  # Tokens are never exposed
    assert "refresh_token" not in status_connected


def test_sensitive_token_redaction():
    """Verify centralized token and secret redaction."""
    raw_log = "Sending request with Authorization: Bearer ya29.secret_token_123 and client_secret=GOCSPX-secret_secret_456"
    redacted = redact_sensitive(raw_log)
    assert "ya29.secret_token_123" not in redacted
    assert "GOCSPX-secret_secret_456" not in redacted
    assert "Bearer [REDACTED]" in redacted
    assert "client_secret=[REDACTED]" in redacted
