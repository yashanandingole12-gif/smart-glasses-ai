import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)

logger = logging.getLogger("SmartGlasses")

class LatencyMetrics(BaseModel):
    request_id: str
    session_id: str
    start_time: float = Field(default_factory=time.time)
    stt_ms: Optional[float] = None
    network_upload_ms: Optional[float] = None
    backend_queue_ms: Optional[float] = None
    context_ms: Optional[float] = None
    fast_path_ms: Optional[float] = None
    agent_ms: Optional[float] = None
    llm_first_response_ms: Optional[float] = None
    tool_ms: Optional[float] = None
    llm_final_response_ms: Optional[float] = None
    network_download_ms: Optional[float] = None
    tts_start_ms: Optional[float] = None
    tts_total_ms: Optional[float] = None
    total_ms: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Backwards compatibility properties
    @property
    def stt_duration_ms(self) -> Optional[float]:
        return self.stt_ms

    @stt_duration_ms.setter
    def stt_duration_ms(self, val: Optional[float]):
        self.stt_ms = val

    @property
    def context_duration_ms(self) -> Optional[float]:
        return self.context_ms

    @context_duration_ms.setter
    def context_duration_ms(self, val: Optional[float]):
        self.context_ms = val

    @property
    def llm_duration_ms(self) -> Optional[float]:
        return self.llm_first_response_ms or self.agent_ms

    @llm_duration_ms.setter
    def llm_duration_ms(self, val: Optional[float]):
        self.llm_first_response_ms = val
        self.agent_ms = val

    @property
    def tool_duration_ms(self) -> Optional[float]:
        return self.tool_ms

    @tool_duration_ms.setter
    def tool_duration_ms(self, val: Optional[float]):
        self.tool_ms = val

    @property
    def tts_duration_ms(self) -> Optional[float]:
        return self.tts_total_ms

    @tts_duration_ms.setter
    def tts_duration_ms(self, val: Optional[float]):
        self.tts_total_ms = val

    @property
    def total_latency_ms(self) -> Optional[float]:
        return self.total_ms

    @total_latency_ms.setter
    def total_latency_ms(self, val: Optional[float]):
        self.total_ms = val

    def finish(self) -> float:
        self.total_ms = (time.time() - self.start_time) * 1000.0
        return self.total_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "session_id": self.session_id,
            "stt_ms": self.stt_ms,
            "network_upload_ms": self.network_upload_ms,
            "backend_queue_ms": self.backend_queue_ms,
            "context_ms": self.context_ms,
            "fast_path_ms": self.fast_path_ms,
            "agent_ms": self.agent_ms,
            "llm_first_response_ms": self.llm_first_response_ms,
            "tool_ms": self.tool_ms,
            "llm_final_response_ms": self.llm_final_response_ms,
            "network_download_ms": self.network_download_ms,
            "tts_start_ms": self.tts_start_ms,
            "tts_total_ms": self.tts_total_ms,
            "total_ms": self.total_ms
        }

    def formatted_log(self) -> str:
        t_str = datetime.fromtimestamp(self.start_time).strftime("%H:%M:%S")
        lines = [f"[{t_str}] [REQ_ID: {self.request_id}] [SESSION: {self.session_id[:8]}]"]
        if self.fast_path_ms is not None:
            lines.append(f"  FAST_PATH: {self.fast_path_ms:.1f}ms")
        if self.context_ms is not None:
            lines.append(f"  CONTEXT: {self.context_ms:.1f}ms")
        if self.agent_ms is not None:
            lines.append(f"  AGENT_LANGGRAPH: {self.agent_ms:.1f}ms")
        if self.llm_first_response_ms is not None:
            lines.append(f"  LLM_FIRST: {self.llm_first_response_ms:.1f}ms")
        if self.tool_ms is not None:
            lines.append(f"  TOOL_EXECUTION: {self.tool_ms:.1f}ms")
        if self.llm_final_response_ms is not None:
            lines.append(f"  LLM_FINAL: {self.llm_final_response_ms:.1f}ms")
        if self.total_ms is not None:
            lines.append(f"  BACKEND_TOTAL: {self.total_ms / 1000.0:.2f}s ({self.total_ms:.1f}ms)")
        return "\n".join(lines)

def log_request_metrics(metrics: LatencyMetrics, query: str = "", status: str = "SUCCESS", error: Optional[str] = None):
    logger.info("\n" + metrics.formatted_log())
    try:
        from backend.app.services.hardware_bridge import hardware_bridge
        hardware_bridge.log_request_status(
            request_id=metrics.request_id,
            query=query or metrics.metadata.get("query", "Voice Command"),
            status=status,
            latency_ms=metrics.total_ms or 0.0,
            error=error
        )
    except Exception:
        pass
