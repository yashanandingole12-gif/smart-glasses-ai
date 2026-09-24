"""
EVA Usage Governor & Cost Controller:
Enforces daily and hourly quotas, token caps, and zero-cost guardrails
to keep cloud deployment completely within free or controlled budgets.
"""

import time
import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

from backend.app.config import settings, PROJECT_ROOT

logger = logging.getLogger("SmartGlasses.UsageGovernor")

class UsageGovernor:
    """
    Guarantees that AWS and LLM cloud usage never exceeds user-defined limits.
    Maintains persistent usage tallies in SQLite and provides live quota statistics.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path(settings.DATABASE_URL.replace("sqlite:///", "").lstrip("./")).resolve()
        
        self.daily_request_limit = getattr(settings, "DAILY_REQUEST_LIMIT", 500)
        self.hourly_request_limit = getattr(settings, "HOURLY_REQUEST_LIMIT", 100)
        self.daily_vision_limit = getattr(settings, "DAILY_VISION_LIMIT", 100)
        self.max_output_tokens = settings.MAX_OUTPUT_TOKENS
        
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_tallies (
                    period_key TEXT PRIMARY KEY,
                    period_type TEXT NOT NULL,
                    request_count INTEGER NOT NULL DEFAULT 0,
                    input_tokens INTEGER NOT NULL DEFAULT 0,
                    output_tokens INTEGER NOT NULL DEFAULT 0,
                    vision_captures INTEGER NOT NULL DEFAULT 0,
                    updated_at REAL NOT NULL
                )
            """)
            conn.commit()

    def _get_period_keys(self) -> Tuple[str, str]:
        now = datetime.now(timezone.utc)
        day_key = f"day_{now.strftime('%Y-%m-%d')}"
        hour_key = f"hour_{now.strftime('%Y-%m-%d_%H')}"
        return day_key, hour_key

    def check_allow_request(self, is_vision: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Validates whether an incoming voice/agent request is within quota.
        Returns (True, None) if allowed, or (False, reason) if limit exceeded.
        """
        day_key, hour_key = self._get_period_keys()
        
        with self._get_conn() as conn:
            day_row = conn.execute(
                "SELECT request_count, vision_captures FROM usage_tallies WHERE period_key = ?",
                (day_key,)
            ).fetchone()
            hour_row = conn.execute(
                "SELECT request_count FROM usage_tallies WHERE period_key = ?",
                (hour_key,)
            ).fetchone()

        day_reqs = day_row["request_count"] if day_row else 0
        day_vision = day_row["vision_captures"] if day_row else 0
        hour_reqs = hour_row["request_count"] if hour_row else 0

        if self.daily_request_limit > 0 and day_reqs >= self.daily_request_limit:
            msg = f"Daily request quota ({self.daily_request_limit} reqs/day) reached to protect your budget."
            logger.warning(msg)
            return False, msg

        if self.hourly_request_limit > 0 and hour_reqs >= self.hourly_request_limit:
            msg = f"Hourly request cap ({self.hourly_request_limit} reqs/hr) reached. Rate-limited temporarily."
            logger.warning(msg)
            return False, msg

        if is_vision and self.daily_vision_limit > 0 and day_vision >= self.daily_vision_limit:
            msg = f"Daily vision capture cap ({self.daily_vision_limit} images/day) reached."
            logger.warning(msg)
            return False, msg

        return True, None

    def record_usage(
        self,
        input_tokens: int = 0,
        output_tokens: int = 0,
        is_vision: bool = False
    ):
        """Records token and request count in both hourly and daily tallies."""
        day_key, hour_key = self._get_period_keys()
        now_ts = time.time()
        vis_count = 1 if is_vision else 0

        with self._get_conn() as conn:
            for pkey, ptype in [(day_key, "DAY"), (hour_key, "HOUR")]:
                conn.execute("""
                    INSERT INTO usage_tallies (period_key, period_type, request_count, input_tokens, output_tokens, vision_captures, updated_at)
                    VALUES (?, ?, 1, ?, ?, ?, ?)
                    ON CONFLICT(period_key) DO UPDATE SET
                        request_count = request_count + 1,
                        input_tokens = input_tokens + excluded.input_tokens,
                        output_tokens = output_tokens + excluded.output_tokens,
                        vision_captures = vision_captures + excluded.vision_captures,
                        updated_at = excluded.updated_at
                """, (pkey, ptype, input_tokens, output_tokens, vis_count, now_ts))
            conn.commit()

    def get_stats(self) -> Dict[str, Any]:
        """Returns current usage statistics, remaining quotas, and cost estimate."""
        day_key, hour_key = self._get_period_keys()
        with self._get_conn() as conn:
            day_row = conn.execute("SELECT * FROM usage_tallies WHERE period_key = ?", (day_key,)).fetchone()
            hour_row = conn.execute("SELECT * FROM usage_tallies WHERE period_key = ?", (hour_key,)).fetchone()

        day_reqs = day_row["request_count"] if day_row else 0
        day_in = day_row["input_tokens"] if day_row else 0
        day_out = day_row["output_tokens"] if day_row else 0
        day_vision = day_row["vision_captures"] if day_row else 0

        hour_reqs = hour_row["request_count"] if hour_row else 0

        # Estimated cost in USD (Gemini 1.5 Flash is Free for <15 RPM, or $0.075/1M input)
        est_cost_usd = (day_in * 0.000000075) + (day_out * 0.00000030)

        return {
            "status": "HEALTHY",
            "today": {
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "requests_used": day_reqs,
                "requests_limit": self.daily_request_limit,
                "requests_remaining": max(0, self.daily_request_limit - day_reqs) if self.daily_request_limit > 0 else "Unlimited",
                "input_tokens": day_in,
                "output_tokens": day_out,
                "total_tokens": day_in + day_out,
                "vision_captures": day_vision,
                "vision_limit": self.daily_vision_limit,
                "estimated_cost_usd": round(est_cost_usd, 5)
            },
            "current_hour": {
                "requests_used": hour_reqs,
                "requests_limit": self.hourly_request_limit
            },
            "limits": {
                "daily_request_limit": self.daily_request_limit,
                "hourly_request_limit": self.hourly_request_limit,
                "max_output_tokens_per_response": self.max_output_tokens
            }
        }

    def update_limits(
        self,
        daily_limit: Optional[int] = None,
        hourly_limit: Optional[int] = None,
        vision_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Dynamically adjusts usage limits."""
        if daily_limit is not None:
            self.daily_request_limit = daily_limit
        if hourly_limit is not None:
            self.hourly_request_limit = hourly_limit
        if vision_limit is not None:
            self.daily_vision_limit = vision_limit
        return self.get_stats()

usage_governor = UsageGovernor()
