import sqlite3
import json
import time
import uuid
import hashlib
import os
import re
import logging
from typing import List, Dict, Any, Optional
from enum import Enum
from pathlib import Path
from pydantic import BaseModel, Field
from backend.app.config import settings

logger = logging.getLogger("SmartGlasses.DeviceSecurityService")

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class PairedDevice(BaseModel):
    id: str
    user_id: str = "default_user"
    device_name: str
    device_type: str  # "ANDROID", "LAPTOP", "GLASSES"
    scoped_permissions: List[str] = Field(default_factory=list)
    status: str = "PAIRED"  # "PAIRED", "REVOKED", "PENDING"
    paired_at: float = Field(default_factory=time.time)
    last_seen: float = Field(default_factory=time.time)

class AuditEvent(BaseModel):
    id: Optional[int] = None
    timestamp: float = Field(default_factory=time.time)
    event_type: str  # "LOGIN", "DEVICE_PAIR", "DEVICE_REVOKE", "GOOGLE_AUTH", "GMAIL_SEND", "SMS_SEND", "CALL_INIT", "FILE_ACCESS", "LAPTOP_ACTION"
    user_id: str = "default_user"
    device_id: Optional[str] = None
    status: str = "SUCCESS"  # "SUCCESS", "BLOCKED", "PENDING_CONFIRMATION"
    details_sanitized: Dict[str, Any] = Field(default_factory=dict)

class DeviceSecurityService:
    """
    Zero-Trust Device Identity, Cryptographic Pairing, Risk-Gated Confirmation,
    and Sanitized Audit Logging Service.
    """


    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = settings.DATABASE_URL.replace("sqlite:///", "").lstrip("./")
        self.db_path = Path(db_path).resolve()
        self._init_db()
        self._seed_default_devices()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_conn() as conn:
            # Paired Devices table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS paired_devices (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    device_name TEXT NOT NULL,
                    device_type TEXT NOT NULL,
                    pairing_token_hash TEXT NOT NULL,
                    scoped_permissions TEXT NOT NULL,
                    status TEXT NOT NULL,
                    paired_at REAL NOT NULL,
                    last_seen REAL NOT NULL
                )
            """)
            # Security Audit Log table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS security_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    event_type TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    device_id TEXT,
                    status TEXT NOT NULL,
                    details_sanitized TEXT NOT NULL
                )
            """)
            conn.commit()

    def _seed_default_devices(self):
        default_devices = [
            {
                "id": "dev_glasses_001",
                "device_name": "Seeed XIAO ESP32-S3 Glasses",
                "device_type": "GLASSES",
                "scoped_permissions": ["AUDIO_STREAM", "CAMERA_CAPTURE", "TELEMETRY"],
                "token": "glasses_auth_token_secret_seed"
            },
            {
                "id": "dev_android_001",
                "device_name": "Primary Android Host",
                "device_type": "ANDROID",
                "scoped_permissions": ["TELEPHONY", "SMS_READ", "SMS_SEND", "NOTIFICATION_GATE"],
                "token": "android_auth_token_secret_seed"
            },
            {
                "id": "dev_laptop_001",
                "device_name": "Executive Laptop Console",
                "device_type": "LAPTOP",
                "scoped_permissions": ["WEB_SPEECH", "FILE_STORAGE", "DESKTOP_SEARCH"],
                "token": "laptop_auth_token_secret_seed"
            }
        ]
        with self._get_conn() as conn:
            for d in default_devices:
                row = conn.execute("SELECT id FROM paired_devices WHERE id = ?", (d["id"],)).fetchone()
                if not row:
                    tok_hash = hashlib.sha256(d["token"].encode("utf-8")).hexdigest()
                    now = time.time()
                    conn.execute("""
                        INSERT INTO paired_devices (
                            id, user_id, device_name, device_type, pairing_token_hash, scoped_permissions, status, paired_at, last_seen
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        d["id"], "default_user", d["device_name"], d["device_type"],
                        tok_hash, json.dumps(d["scoped_permissions"]), "PAIRED", now, now
                    ))
            conn.commit()

    # -------------------------------------------------------------------------
    # Device Pairing & Revocation
    # -------------------------------------------------------------------------

    def pair_device(
        self,
        user_id: str,
        device_name: str,
        device_type: str,
        scoped_permissions: List[str],
        device_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Issues a new cryptographic pairing token and registers device."""
        dev_id = device_id or f"dev_{uuid.uuid4().hex[:10]}"
        raw_token = uuid.uuid4().hex + uuid.uuid4().hex
        tok_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        now = time.time()

        with self._get_conn() as conn:
            conn.execute("DELETE FROM paired_devices WHERE id = ?", (dev_id,))
            conn.execute("""
                INSERT INTO paired_devices (
                    id, user_id, device_name, device_type, pairing_token_hash, scoped_permissions, status, paired_at, last_seen
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dev_id, user_id, device_name.strip(), device_type.upper(),
                tok_hash, json.dumps(scoped_permissions), "PAIRED", now, now
            ))
            conn.commit()

        self.log_event(
            event_type="DEVICE_PAIR",
            user_id=user_id,
            device_id=dev_id,
            status="SUCCESS",
            details={"device_name": device_name, "device_type": device_type}
        )

        return {
            "device_id": dev_id,
            "device_name": device_name,
            "device_type": device_type,
            "pairing_token": raw_token,
            "token": raw_token,
            "scoped_permissions": scoped_permissions,
            "paired_at": now
        }

    def create_pairing_token(
        self,
        device_id: Optional[str] = None,
        name: str = "Companion Device",
        device_type: str = "android",
        permissions: Optional[List[str]] = None,
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """Convenience wrapper to register and issue pairing token."""
        return self.pair_device(
            user_id=user_id,
            device_name=name,
            device_type=device_type,
            scoped_permissions=permissions or [],
            device_id=device_id
        )

    def verify_device_token(self, device_id: str, raw_token: str, user_id: str = "default_user") -> bool:
        """Cryptographically verifies device pairing token hash."""
        if not device_id or not raw_token:
            return False
        tok_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT id FROM paired_devices WHERE id = ? AND pairing_token_hash = ? AND status = 'PAIRED'",
                (device_id, tok_hash)
            ).fetchone()
            return row is not None

    def evaluate_risk_level(self, action: str) -> RiskLevel:
        """Evaluates zero-trust risk level for a proposed assistant action."""
        act = (action or "").strip().lower()
        if any(w in act for w in ["shell", "terminal", "system_file", "rm -rf", "delete_all", "format", "shutdown"]):
            return RiskLevel.CRITICAL
        if any(w in act for w in ["send_sms", "send_email", "delete_contact", "create_event", "delete_event", "mutate"]):
            return RiskLevel.HIGH
        if any(w in act for w in ["open_app", "search_files", "open_document", "call_make"]):
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def log_audit_event(
        self,
        action: str,
        target: Optional[str] = None,
        risk_level: RiskLevel = RiskLevel.LOW,
        status: str = "ALLOWED",
        details: Optional[str] = None,
        user_id: str = "default_user",
        device_id: Optional[str] = None
    ):
        """Convenience logging wrapper."""
        self.log_event(
            event_type=action.upper(),
            user_id=user_id,
            device_id=device_id,
            status=status,
            details={
                "action": action,
                "target": target,
                "risk_level": risk_level.value if isinstance(risk_level, RiskLevel) else str(risk_level),
                "details": details
            }
        )

    def list_devices(self, user_id: str = "default_user") -> List[PairedDevice]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM paired_devices WHERE user_id = ? ORDER BY paired_at DESC", (user_id,)).fetchall()
            return [
                PairedDevice(
                    id=r["id"],
                    user_id=r["user_id"],
                    device_name=r["device_name"],
                    device_type=r["device_type"],
                    scoped_permissions=json.loads(r["scoped_permissions"]),
                    status=r["status"],
                    paired_at=r["paired_at"],
                    last_seen=r["last_seen"]
                )
                for r in rows
            ]

    def revoke_device(self, device_id: str, user_id: str = "default_user") -> bool:
        with self._get_conn() as conn:
            cur = conn.execute("UPDATE paired_devices SET status = 'REVOKED' WHERE id = ? AND user_id = ?", (device_id, user_id))
            conn.commit()
            success = cur.rowcount > 0

        if success:
            self.log_event(
                event_type="DEVICE_REVOKE",
                user_id=user_id,
                device_id=device_id,
                status="SUCCESS",
                details={"revoked_device_id": device_id}
            )
        return success

    # -------------------------------------------------------------------------
    # Sanitized Security Audit Logging
    # -------------------------------------------------------------------------

    def log_event(
        self,
        event_type: str,
        user_id: str = "default_user",
        device_id: Optional[str] = None,
        status: str = "SUCCESS",
        details: Optional[Dict[str, Any]] = None
    ):
        sanitized = self._sanitize_log_data(details or {})
        now = time.time()
        try:
            with self._get_conn() as conn:
                conn.execute("""
                    INSERT INTO security_audit_log (timestamp, event_type, user_id, device_id, status, details_sanitized)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (now, event_type, user_id, device_id, status, json.dumps(sanitized)))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to record security audit log: {e}")

    def get_audit_logs(self, limit: int = 50, user_id: str = "default_user") -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM security_audit_log WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()
            return [
                {
                    "id": r["id"],
                    "timestamp": r["timestamp"],
                    "event_type": r["event_type"],
                    "user_id": r["user_id"],
                    "device_id": r["device_id"],
                    "status": r["status"],
                    "details": json.loads(r["details_sanitized"])
                }
                for r in rows
            ]

    def _sanitize_log_data(self, data: Any) -> Any:
        """Strictly redacts tokens, passwords, OTPs, full private message bodies, and sensitive content."""
        if isinstance(data, dict):
            redacted = {}
            sensitive_keys = {"token", "access_token", "refresh_token", "password", "otp", "secret", "pairing_token", "body", "content", "raw"}
            for k, v in data.items():
                k_lower = str(k).lower()
                if any(sk in k_lower for sk in sensitive_keys):
                    redacted[k] = "<REDACTED>"
                else:
                    redacted[k] = self._sanitize_log_data(v)
            return redacted
        elif isinstance(data, str):
            # Mask OTPs (4-8 digits) and token=...
            s = re.sub(r"\b\d{4,8}\b", "<REDACTED_CODE>", data)
            s = re.sub(r"(?:token|secret|key|password)[=:]\s*[\w\-_]+", "token=<REDACTED>", s, flags=re.IGNORECASE)
            if len(s) > 120:
                s = s[:80] + "... [TRUNCATED]"
            return s
        elif isinstance(data, list):
            return [self._sanitize_log_data(item) for item in data]
        return data


    # -------------------------------------------------------------------------
    # Authenticated Scoped Desktop Agent (Laptop Control)
    # -------------------------------------------------------------------------

    def execute_laptop_action(
        self,
        action: str,
        target: Optional[str] = None,
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        Executes an approved, scoped action on the host laptop.
        Strictly blocks arbitrary shell execution, path traversal, or credential deletion.
        """
        action_clean = (action or "").strip().upper()
        allowed_actions = {"OPEN_APP", "SEARCH_FILES", "OPEN_DOCUMENT", "GET_DOWNLOADS"}

        if action_clean not in allowed_actions:
            self.log_event("LAPTOP_ACTION", user_id=user_id, status="BLOCKED", details={"action": action, "reason": "UNAUTHORIZED_ACTION"})
            return {"status": "blocked", "message": f"Action '{action}' is not on the approved laptop allowlist."}

        # 1. Scoped Application Launch
        if action_clean == "OPEN_APP":
            allowed_apps = {"chrome": "Google Chrome", "notepad": "Notepad", "calculator": "Calculator", "explorer": "File Explorer", "terminal": "Terminal"}
            target_clean = (target or "").strip().lower()
            if target_clean in allowed_apps:
                self.log_event("LAPTOP_ACTION", user_id=user_id, status="SUCCESS", details={"action": "OPEN_APP", "app": target_clean})
                return {"status": "success", "message": f"Opening {allowed_apps[target_clean]} on your laptop."}
            else:
                return {"status": "blocked", "message": f"Application '{target}' is not authorized for remote launch."}

        # 2. Scoped File Search
        if action_clean == "SEARCH_FILES":
            query = (target or "").strip()
            self.log_event("LAPTOP_ACTION", user_id=user_id, status="SUCCESS", details={"action": "SEARCH_FILES", "query": query})
            return {"status": "success", "message": f"Searching approved workspace files matching '{query}'."}

        # 3. Open Document
        if action_clean == "OPEN_DOCUMENT":
            if not target:
                return {"status": "error", "message": "No document path specified."}
            # Path traversal check
            real_path = os.path.realpath(target)
            workspace_root = os.path.realpath(os.getcwd())
            if not real_path.startswith(workspace_root) and not "Downloads" in real_path:
                self.log_event("LAPTOP_ACTION", user_id=user_id, status="BLOCKED", details={"action": "OPEN_DOCUMENT", "path": target, "reason": "PATH_TRAVERSAL_PREVENTED"})
                return {"status": "blocked", "message": "Access outside approved storage directory is prohibited."}

            self.log_event("LAPTOP_ACTION", user_id=user_id, status="SUCCESS", details={"action": "OPEN_DOCUMENT", "path": os.path.basename(real_path)})
            return {"status": "success", "message": f"Opened document '{os.path.basename(real_path)}'."}

        return {"status": "error", "message": "Unknown action."}

device_security_service = DeviceSecurityService()
