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
    stt_duration_ms: Optional[float] = None
    context_duration_ms: Optional[float] = None
    llm_duration_ms: Optional[float] = None
    tool_duration_ms: Optional[float] = None
    tts_duration_ms: Optional[float] = None
    total_latency_ms: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def finish(self) -> float:
        self.total_latency_ms = (time.time() - self.start_time) * 1000.0
        return self.total_latency_ms

    def formatted_log(self) -> str:
        t_str = datetime.fromtimestamp(self.start_time).strftime("%H:%M:%S")
        lines = [f"[{t_str}] REQ: {self.request_id[:8]} | SESSION: {self.session_id[:8]}"]
        if self.stt_duration_ms is not None:
            lines.append(f"  STT: {self.stt_duration_ms:.1f}ms")
        if self.context_duration_ms is not None:
            lines.append(f"  CONTEXT: {self.context_duration_ms:.1f}ms")
        if self.llm_duration_ms is not None:
            lines.append(f"  LLM: {self.llm_duration_ms:.1f}ms")
        if self.tool_duration_ms is not None:
            lines.append(f"  TOOL: {self.tool_duration_ms:.1f}ms")
        if self.tts_duration_ms is not None:
            lines.append(f"  TTS: {self.tts_duration_ms:.1f}ms")
        if self.total_latency_ms is not None:
            lines.append(f"  TOTAL: {self.total_latency_ms / 1000.0:.2f}s ({self.total_latency_ms:.1f}ms)")
        return "\n".join(lines)

def log_request_metrics(metrics: LatencyMetrics):
    logger.info("\n" + metrics.formatted_log())
