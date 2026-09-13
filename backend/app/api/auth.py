import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Request, Response, Query
from fastapi.responses import RedirectResponse, HTMLResponse

from backend.app.config import settings
from backend.app.services.token_service import token_service, redact_sensitive

logger = logging.getLogger("SmartGlasses.AuthAPI")

router = APIRouter(prefix="/api/v1/auth", tags=["Google OAuth 2.0"])


@router.get("/google")
async def google_auth_login(
    user_id: str = Query("default_user", description="Identifier of the authenticated user"),
    client_redirect: Optional[str] = Query(None, description="Optional client deep-link URL after authorization"),
    format: Optional[str] = Query(None, description="Set to 'json' to get the auth URL directly")
):
    """
    Step 1: Initiate Google OAuth 2.0 Authorization Code Flow.
    Generates a cryptographically random CSRF state and redirects user to Google's consent screen.
    """
    try:
        auth_url = token_service.get_authorization_url(user_id=user_id, client_redirect=client_redirect)
        if format == "json":
            return {
                "auth_url": auth_url,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "scopes": settings.GOOGLE_OAUTH_SCOPES
            }
        return RedirectResponse(url=auth_url, status_code=307)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/google/callback")
async def google_auth_callback(
    code: Optional[str] = Query(None, description="Google OAuth authorization code"),
    state: Optional[str] = Query(None, description="CSRF state token"),
    error: Optional[str] = Query(None, description="Google OAuth error if authorization was denied")
):
    """
    Step 2: Google OAuth Callback Handler.
    - Validates single-use CSRF state token
    - Exchanges authorization code for tokens
    - Encrypts/stores credentials in TokenService
    - Redacts all token material from logs and responses
    """
    # 1. Handle user cancellation or Google error
    if error:
        logger.warning("Google OAuth error received in callback: %s", error)
        if state:
            token_service.verify_and_consume_state(state)
        
        detail_msg = f"Google returned error: <b>{error}</b>."
        if error == "access_denied":
            detail_msg += "<br/><br/><b>Action Required:</b> Because the Google Cloud OAuth app is in 'Testing' publishing status, you must add your Google email account (e.g. <code>smartglassesai01@gmail.com</code>) to the <b>Test Users</b> list in Google Cloud Console &gt; OAuth Consent Screen."
            
        return HTMLResponse(
            status_code=400,
            content=_render_result_html(
                title="Authorization Denied or Cancelled",
                message=detail_msg,
                is_success=False
            )
        )

    # 2. Validate CSRF State Token
    if not state:
        logger.warning("OAuth callback missing state parameter.")
        raise HTTPException(status_code=400, detail="Missing OAuth state parameter (CSRF verification failed).")

    state_data = token_service.verify_and_consume_state(state)
    if not state_data:
        logger.warning("OAuth callback invalid or expired state: %s", state)
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state parameter. Please restart authorization.")

    user_id = state_data.get("user_id", "default_user")

    # 3. Validate Authorization Code
    if not code:
        logger.warning("OAuth callback missing authorization code.")
        raise HTTPException(status_code=400, detail="Missing authorization code from Google.")

    # 4. Exchange code for access & refresh tokens
    try:
        token_data = await token_service.exchange_code_for_tokens(
            code=code,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )
    except Exception as e:
        logger.error("OAuth token exchange failed: %s", e)
        return HTMLResponse(
            status_code=400,
            content=_render_result_html(
                title="Token Exchange Failed",
                message="Failed to exchange authorization code with Google. Verify your client secret and redirect URI.",
                is_success=False
            )
        )

    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in", 3600)
    granted_scopes = token_data.get("scope", "").split() or settings.GOOGLE_OAUTH_SCOPES

    if not access_token:
        raise HTTPException(status_code=500, detail="Google response did not contain access_token.")

    # 5. Fetch user identity (Email)
    user_email = await token_service.fetch_user_email(access_token)

    # 6. Securely persist tokens
    token_service.save_tokens(
        user_id=user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        scopes=granted_scopes,
        user_email=user_email,
        provider="google"
    )

    logger.info("Successfully completed Google OAuth flow for user=%s (email=%s)", user_id, user_email or "unknown")

    return HTMLResponse(
        status_code=200,
        content=_render_result_html(
            title="Google Account Connected",
            message=f"Successfully connected Google Account: <b>{user_email or 'Authorized User'}</b>.<br/>Gmail & Google Calendar are now ready for your Smart Glasses assistant.",
            is_success=True
        )
    )


@router.get("/status")
@router.get("/google/status")
async def google_auth_status(
    user_id: str = Query("default_user", description="Identifier of the user")
):
    """
    Check current Google OAuth connection status.
    Returns status and email without exposing any tokens.
    """
    return token_service.get_status(user_id=user_id, provider="google")


@router.post("/google/disconnect")
async def google_auth_disconnect(
    user_id: str = Query("default_user", description="Identifier of the user")
):
    """
    Disconnect Google account, revoke credentials with Google, and remove local tokens.
    """
    disconnected = await token_service.disconnect(user_id=user_id, provider="google")
    return {
        "status": "disconnected" if disconnected else "not_connected",
        "user_id": user_id,
        "connected": False
    }


def _render_result_html(title: str, message: str, is_success: bool) -> str:
    status_color = "#00E676" if is_success else "#FF5252"
    badge_text = "CONNECTION ACTIVE" if is_success else "AUTHORIZATION ERROR"
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - Smart Glasses AI</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: #0A0E14;
                color: #F0F6FC;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            .card {{
                background-color: #151B23;
                border: 1px solid #30363D;
                border-radius: 16px;
                padding: 36px;
                max-width: 460px;
                text-align: center;
                box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
            }}
            .badge {{
                display: inline-block;
                background-color: rgba({ '0, 230, 118, 0.15' if is_success else '255, 82, 82, 0.15' });
                color: {status_color};
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
                padding: 6px 14px;
                border-radius: 20px;
                margin-bottom: 20px;
            }}
            h1 {{
                font-size: 22px;
                font-weight: 700;
                margin: 0 0 14px 0;
                color: #00E5FF;
                letter-spacing: 0.5px;
            }}
            p {{
                font-size: 15px;
                line-height: 1.6;
                color: #8B949E;
                margin: 0 0 24px 0;
            }}
            .btn {{
                display: inline-block;
                background-color: #00E5FF;
                color: #0A0E14;
                text-decoration: none;
                font-weight: 700;
                font-size: 14px;
                padding: 12px 28px;
                border-radius: 10px;
                transition: opacity 0.2s ease;
            }}
            .btn:hover {{
                opacity: 0.9;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="badge">{badge_text}</div>
            <h1>{title}</h1>
            <p>{message}</p>
            <p style="font-size: 12px; color: #6E7681;">You can close this window and return to the Smart Glasses application.</p>
        </div>
    </body>
    </html>
    """
