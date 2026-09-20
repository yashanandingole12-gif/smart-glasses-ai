"""
EVA Latency & Performance Tracker
Provides structured, stage-by-stage latency logging and budget validation
across Wake, Capture, Transport, STT, Router, LLM, Tools, and TTS.
"""

import time
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("eva.telemetry.latency")

class StageMetric:
    def __init__(self, stage_name: str):
        self.stage_name = stage_name
        self.start_time = time.perf_counter()
        self.duration_ms: float = 0.0
        self.success: bool = True
        self.failure_reason: Optional[str] = None

    def finish(self, success: bool = True, failure_reason: Optional[str] = None) -> float:
        self.duration_ms = (time.perf_counter() - self.start_time) * 1000.0
        self.success = success
        self.failure_reason = failure_reason
        return self.duration_ms

class RequestLatencyTracker:
    def __init__(self, request_id: str, session_id: str, device_id: str = "android_esp32"):
        self.request_id = request_id
        self.session_id = session_id
        self.device_id = device_id
        self.start_timestamp = time.time()
        self.t0 = time.perf_counter()
        self.stages: Dict[str, StageMetric] = {}

    def start_stage(self, stage_name: str) -> StageMetric:
        metric = StageMetric(stage_name)
        self.stages[stage_name] = metric
        return metric

    def end_stage(self, stage_name: str, success: bool = True, failure_reason: Optional[str] = None) -> float:
        metric = self.stages.get(stage_name)
        if metric:
            dur = metric.finish(success, failure_reason)
            logger.debug(f"LATENCY [{self.request_id}] {stage_name}: {dur:.1f}ms (success={success})")
            return dur
        return 0.0

    def get_summary(self) -> Dict[str, Any]:
        total_duration = (time.perf_counter() - self.t0) * 1000.0
        stage_breakdown = {
            name: {
                "duration_ms": round(metric.duration_ms, 2),
                "success": metric.success,
                "failure_reason": metric.failure_reason
            }
            for name, metric in self.stages.items()
        }

        summary = {
            "request_id": self.request_id,
            "session_id": self.session_id,
            "device_id": self.device_id,
            "timestamp": self.start_timestamp,
            "total_latency_ms": round(total_duration, 2),
            "stages": stage_breakdown
        }

        logger.info(
            f"REQUEST_LATENCY_REPORT req={self.request_id} total={total_duration:.1f}ms "
            f"stages={list(stage_breakdown.keys())}"
        )
        return summary
