import sqlite3
import time
import secrets
import logging
import httpx
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode

from backend.app.config import settings

logger = logging.getLogger("SmartGlasses.TokenService")


def redact_sensitive(text: str) -> str:
    """Removes sensitive credentials, keys, and tokens from logging strings."""
    if not text:
        return ""
    import re
    redacted = re.sub(r"(?i)Bearer\s+[a-zA-Z0-9_\-\.]+", "Bearer [REDACTED]", text)
    redacted = re.sub(r"(?i)(client_secret|access_token|refresh_token|api_key|password)=[\"']?[^\"'&,\s]+", r"\1=[REDACTED]", redacted)
    return redacted


class TokenService:
    """
    Secure token management service for Google OAuth 2.0.
    
    Responsibilities:
    - Encapsulates token storage in SQLite database.
    - Manages CSRF OAuth state generation, validation, and single-use expiration.
    - Automatic token refresh before expiration.
    - Token revocation and disconnect.
    - Never exposes raw access/refresh tokens to agent LLM or client UI.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = db_path
        elif settings.DATABASE_URL.startswith("sqlite:///"):
            self.db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        else:
            self.db_path = "./smart_glasses.db"

        self._mem_conn = sqlite3.connect(":memory:", check_same_thread=False) if self.db_path == ":memory:" else None
        if self._mem_conn:
            self._mem_conn.row_factory = sqlite3.Row

        self._state_cache: Dict[str, Dict[str, Any]] = {}
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if self._mem_conn is not None:
            return self._mem_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Ensure the oauth_tokens and oauth_states tables exist."""
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS oauth_tokens (
                    user_id TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    access_token TEXT NOT NULL,
                    refresh_token TEXT,
                    token_expiry REAL NOT NULL,
                    scopes TEXT,
                    user_email TEXT,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS oauth_states (
                    state TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    client_redirect TEXT,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL
                )
            """)
            conn.commit()

    # -------------------------------------------------------------------------
    # CSRF State Management (Persistent, Single-Use, Encrypted Entropy)
    # -------------------------------------------------------------------------

    def create_oauth_state(self, user_id: str = "default_user", client_redirect: Optional[str] = None) -> str:
        """
        Generate a cryptographically secure (256-bit entropy), single-use state token for CSRF protection.
        Stored persistently in SQLite to survive server reloads, worker processes, and domain redirects.
        Expires in 10 minutes (600s TTL).
        """
        now = time.time()
        state_token = secrets.token_urlsafe(32)
        expires_at = now + 600.0  # 10 minutes TTL

        with self._get_conn() as conn:
            # Purge expired states first
            conn.execute("DELETE FROM oauth_states WHERE expires_at < ?", (now,))
            conn.execute(
                "INSERT INTO oauth_states (state, user_id, client_redirect, created_at, expires_at) VALUES (?, ?, ?, ?, ?)",
                (state_token, user_id, client_redirect, now, expires_at)
            )
            conn.commit()

        logger.info("Generated persistent OAuth CSRF state (user=%s, expires_in=600s)", user_id)
        return state_token

    def verify_and_consume_state(self, state: str) -> Optional[Dict[str, Any]]:
        """
        Verify state token against persistent database.
        If valid and unexpired, atomically consumes (removes) it immediately to guarantee single-use replay protection.
        """
        if not state:
            logger.warning("CSRF validation failed: Missing state parameter.")
            return None

        now = time.time()
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT user_id, client_redirect, expires_at FROM oauth_states WHERE state = ?",
                (state,)
            ).fetchone()

            if not row:
                logger.warning("CSRF validation failed: State token '%s...' not found or already consumed.", state[:8] if len(state) >= 8 else state)
                return None

            # Atomically delete to guarantee single-use consumption
            conn.execute("DELETE FROM oauth_states WHERE state = ?", (state,))
            conn.commit()

            if float(row["expires_at"]) < now:
                logger.warning("CSRF validation failed: State token has expired (now=%.1f, expires_at=%.1f).", now, float(row["expires_at"]))
                return None

            logger.info("CSRF validation successful for state token and user=%s", row["user_id"])
            return {
                "user_id": row["user_id"],
                "client_redirect": row["client_redirect"],
                "expires_at": float(row["expires_at"])
            }

    # -------------------------------------------------------------------------
    # OAuth URL Construction
    # -------------------------------------------------------------------------

    def get_authorization_url(self, user_id: str = "default_user", client_redirect: Optional[str] = None) -> str:
        """
        Build Google OAuth 2.0 authorization URL with CSRF state and required scopes.
        """
        if not settings.GOOGLE_CLIENT_ID:
            raise ValueError("GOOGLE_CLIENT_ID is not configured in backend settings.")

        state = self.create_oauth_state(user_id=user_id, client_redirect=client_redirect)
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(settings.GOOGLE_OAUTH_SCOPES),
            "access_type": "offline",
            "prompt": "consent",
            "state": state
        }
        return f"{settings.GOOGLE_AUTH_URI}?{urlencode(params)}"

    # -------------------------------------------------------------------------
    # Token Exchange & Refresh
    # -------------------------------------------------------------------------

    async def exchange_code_for_tokens(self, code: str, redirect_uri: Optional[str] = None) -> Dict[str, Any]:
        """
        Exchanges authorization code with Google Token endpoint.
        """
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise ValueError("Google OAuth credentials (CLIENT_ID / CLIENT_SECRET) are missing.")

        target_redirect_uri = redirect_uri or settings.GOOGLE_REDIRECT_URI

        payload = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": target_redirect_uri,
            "grant_type": "authorization_code"
        }

        logger.info("Exchanging OAuth code with Google (redirect_uri=%s)...", target_redirect_uri)

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(settings.GOOGLE_TOKEN_URI, data=payload)
            if resp.status_code != 200:
                err_text = redact_sensitive(resp.text)
                logger.error("Token exchange failed: HTTP %d: %s", resp.status_code, err_text)
                raise RuntimeError(f"Google token exchange failed: {resp.status_code} - {err_text}")

            token_data = resp.json()
            return token_data

    async def fetch_user_email(self, access_token: str) -> Optional[str]:
        """Fetch user email profile using access token."""
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(settings.GOOGLE_USERINFO_URI, headers=headers)
                if resp.status_code == 200:
                    return resp.json().get("email")
        except Exception as e:
            logger.warning("Failed to fetch user email from Google userinfo: %s", e)
        return None

    def save_tokens(
        self,
        user_id: str,
        access_token: str,
        refresh_token: Optional[str],
        expires_in: int,
        scopes: List[str],
        user_email: Optional[str] = None,
        provider: str = "google"
    ):
        """Persist tokens safely into database."""
        token_expiry = time.time() + float(expires_in)
        scopes_str = ",".join(scopes) if isinstance(scopes, list) else str(scopes)
        now_iso = datetime.now(timezone.utc).isoformat()

        with self._get_conn() as conn:
            # If refresh_token is not in this response, keep the existing refresh_token
            existing = conn.execute(
                "SELECT refresh_token, user_email FROM oauth_tokens WHERE user_id = ? AND provider = ?",
                (user_id, provider)
            ).fetchone()

            final_refresh_token = refresh_token
            final_email = user_email
            if existing:
                if not final_refresh_token:
                    final_refresh_token = existing["refresh_token"]
                if not final_email:
                    final_email = existing["user_email"]

            conn.execute("""
                INSERT INTO oauth_tokens (user_id, provider, access_token, refresh_token, token_expiry, scopes, user_email, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    access_token = excluded.access_token,
                    refresh_token = excluded.refresh_token,
                    token_expiry = excluded.token_expiry,
                    scopes = excluded.scopes,
                    user_email = excluded.user_email,
                    updated_at = excluded.updated_at
            """, (user_id, provider, access_token, final_refresh_token, token_expiry, scopes_str, final_email, now_iso))
            conn.commit()

        logger.info("OAuth tokens securely stored for user %s (email=%s, expires_in=%ds)", user_id, final_email or "unknown", expires_in)

    async def get_valid_token(self, user_id: str = "default_user", provider: str = "google") -> Optional[str]:
        """
        Retrieves a valid access token.
        Automatically refreshes the token if expired or close to expiration.
        """
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT access_token, refresh_token, token_expiry FROM oauth_tokens WHERE user_id = ? AND provider = ?",
                (user_id, provider)
            ).fetchone()

        if not row:
            return None

        access_token = row["access_token"]
        refresh_token = row["refresh_token"]
        token_expiry = float(row["token_expiry"])

        # If token is valid for at least another 60 seconds, return it
        if token_expiry - time.time() > 60.0:
            return access_token

        # Otherwise refresh if we have a refresh token
        if not refresh_token:
            logger.warning("Access token expired for user %s and no refresh token available.", user_id)
            return None

        logger.info("Access token expired for user %s. Refreshing using refresh_token...", user_id)
        refreshed = await self._refresh_access_token(user_id, refresh_token, provider)
        return refreshed

    async def _refresh_access_token(self, user_id: str, refresh_token: str, provider: str = "google") -> Optional[str]:
        """Performs token refresh request with Google Token endpoint."""
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            return None

        payload = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(settings.GOOGLE_TOKEN_URI, data=payload)
                if resp.status_code != 200:
                    logger.error("Token refresh failed: HTTP %d: %s", resp.status_code, redact_sensitive(resp.text))
                    return None

                data = resp.json()
                new_access_token = data["access_token"]
                expires_in = data.get("expires_in", 3600)
                new_refresh_token = data.get("refresh_token", refresh_token)

                self.save_tokens(
                    user_id=user_id,
                    access_token=new_access_token,
                    refresh_token=new_refresh_token,
                    expires_in=expires_in,
                    scopes=settings.GOOGLE_OAUTH_SCOPES,
                    provider=provider
                )
                return new_access_token
        except Exception as e:
            logger.error("Exception during token refresh: %s", e)
            return None

    # -------------------------------------------------------------------------
    # Status & Disconnect
    # -------------------------------------------------------------------------

    def get_status(self, user_id: str = "default_user", provider: str = "google") -> Dict[str, Any]:
        """
        Returns connection status without revealing sensitive token material.
        """
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT user_email, token_expiry, scopes, updated_at, (refresh_token IS NOT NULL AND length(refresh_token) > 0) AS has_refresh FROM oauth_tokens WHERE user_id = ? AND provider = ?",
                (user_id, provider)
            ).fetchone()

        if not row:
            return {
                "connected": False,
                "email": None,
                "scopes": [],
                "expires_at": None,
                "has_refresh_token": False
            }

        expiry_ts = float(row["token_expiry"])
        is_expired = time.time() >= expiry_ts
        expires_at_iso = datetime.fromtimestamp(expiry_ts, timezone.utc).isoformat()
        scopes_list = [s.strip() for s in (row["scopes"] or "").split(",") if s.strip()]
        has_refresh = bool(row["has_refresh"])

        return {
            "connected": True,
            "email": row["user_email"],
            "scopes": scopes_list,
            "is_expired": is_expired,
            "has_refresh_token": has_refresh,
            "expires_at": expires_at_iso,
            "updated_at": row["updated_at"]
        }

    async def disconnect(self, user_id: str = "default_user", provider: str = "google") -> bool:
        """Revokes tokens with Google and removes record from database."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT access_token, refresh_token FROM oauth_tokens WHERE user_id = ? AND provider = ?",
                (user_id, provider)
            ).fetchone()

        if not row:
            return False

        token_to_revoke = row["refresh_token"] or row["access_token"]
        if token_to_revoke:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(
                        settings.GOOGLE_REVOKE_URI,
                        params={"token": token_to_revoke},
                        headers={"Content-Type": "application/x-www-form-urlencoded"}
                    )
            except Exception as e:
                logger.warning("Token revocation request encountered non-fatal error: %s", e)

        with self._get_conn() as conn:
            conn.execute("DELETE FROM oauth_tokens WHERE user_id = ? AND provider = ?", (user_id, provider))
            conn.commit()

        logger.info("Google account successfully disconnected and tokens removed for user %s", user_id)
        return True


token_service = TokenService()
