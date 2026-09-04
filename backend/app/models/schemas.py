from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid
import time

class RiskLevel(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    LOW_RISK_WRITE = "LOW_RISK_WRITE"
    HIGH_RISK_WRITE = "HIGH_RISK_WRITE"


class TimePeriod(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"

class TemporalContext(BaseModel):
    local_time: str = Field(description="Local time string, e.g. 08:15")
    period: TimePeriod = Field(description="Time of day: morning, afternoon, evening, night")
    timezone: str = Field(default="Asia/Kolkata", description="Timezone name, e.g. Asia/Kolkata")
    date_str: Optional[str] = Field(default=None, description="Date string, e.g. 2026-08-21")
    iso_timestamp: Optional[str] = Field(default=None, description="ISO timestamp")

class LocationContext(BaseModel):
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    city: str = Field(default="Unavailable")
    country: str = Field(default="")
    is_available: bool = Field(default=False)
    place_type: Optional[str] = Field(default=None, description="e.g. college, office, home, transit, mobile")

class CalendarEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    start_time: str
    end_time: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None

class CalendarContext(BaseModel):
    current_event: Optional[CalendarEvent] = None
    next_event: Optional[CalendarEvent] = None
    today_events: List[CalendarEvent] = Field(default_factory=list)

class DeviceContext(BaseModel):
    battery: int = Field(default=85, ge=0, le=100)
    battery_percent: Optional[int] = Field(default=None)
    camera_available: bool = True
    microphone_available: bool = True
    network: str = "WIFI"
    connection_type: str = "SIMULATOR"  # "SIMULATOR", "BLE_ESP32", "ANDROID_HUB"
    esp32_connected: bool = False

class ConversationContext(BaseModel):
    recent_topic: Optional[str] = None
    referenced_entities: Dict[str, Any] = Field(default_factory=dict)
    last_intent: Optional[str] = None

class VisionContext(BaseModel):
    recent_image_description: Optional[str] = None
    structured_attributes: Optional[Dict[str, Any]] = None

class FullContextPayload(BaseModel):
    time: TemporalContext
    location: LocationContext
    calendar: Optional[CalendarContext] = Field(default_factory=CalendarContext)
    device: DeviceContext
    conversation: Optional[ConversationContext] = Field(default_factory=ConversationContext)
    memory: Optional[List[str]] = Field(default_factory=list)
    vision: Optional[VisionContext] = None
    locale: Optional[str] = Field(default="en-IN")
    timezone: Optional[str] = Field(default="Asia/Kolkata")
    timestamp: Optional[str] = None

class AgentMessageRequest(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message: str = Field(description="User transcript or text message")
    language: Optional[str] = Field(default="auto", description="Detected or selected language code: en, hi, mr, hi-Latn, auto")
    locale: Optional[str] = Field(default="en-IN", description="Full locale identifier: en-IN, hi-IN, mr-IN, etc.")
    context: Optional[FullContextPayload] = None
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_timestamp: float = Field(default_factory=time.time)
    confirmed_action: Optional[bool] = None
    confirmed_action_id: Optional[str] = None

class AgentAction(BaseModel):
    tool_name: str
    tool_input: Dict[str, Any] = Field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.READ
    status: str = "executed"  # "executed", "pending_confirmation", "aborted"
    action_id: Optional[str] = None
    result: Optional[Any] = None

class AgentMessageResponse(BaseModel):
    session_id: str
    response: str
    actions: List[AgentAction] = Field(default_factory=list)
    requires_confirmation: bool = False
    confirmation_prompt: Optional[str] = None
    confirmation_action_id: Optional[str] = None
    sources: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    device_mode: str = "SIMULATOR_READY"
    llm_provider: str

class SessionCreateRequest(BaseModel):
    user_id: Optional[str] = "default_user"
    device_type: Optional[str] = "SIMULATOR"

class SessionResponse(BaseModel):
    session_id: str
    created_at: str
    device_type: str

class VisionAnalyzeRequest(BaseModel):
    session_id: str
    image_base64: str
    prompt: Optional[str] = "Describe what you see and extract any wearable/clothing details."

class VisionAnalyzeResponse(BaseModel):
    description: str
    structured_attributes: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    color: Optional[str] = None
    style: Optional[str] = None
