import time
import uuid
import inspect
import logging
from typing import Dict, Any, Callable, Optional, List
from pydantic import BaseModel, Field
from backend.app.models.schemas import RiskLevel
from backend.app.tools import (
    get_time,
    get_location,
    calendar_get_events,
    calendar_find_free_time,
    calendar_create_event,
    gmail_search,
    gmail_read,
    sms_read_recent,
    sms_search,
    sms_send_message,
    web_search,
    product_search
)

logger = logging.getLogger("SmartGlasses.ToolRegistry")

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    risk_level: RiskLevel = RiskLevel.READ
    requires_confirmation: bool = False
    func: Optional[Any] = Field(default=None, exclude=True)

class PendingAction(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool_name: str
    tool_input: Dict[str, Any]
    risk_level: RiskLevel
    created_at: float = Field(default_factory=time.time)
    expires_at: float
    confirmed: bool = False
    status: str = "pending"  # "pending", "executed", "cancelled", "expired"

class ToolRegistry:
    """
    Unified Tool Registry & Security Layer:
    - Enforces permission and risk levels (READ vs WRITE vs HIGH_RISK_WRITE).
    - Manages short-lived confirmation tokens for side-effects (60s TTL).
    - Sanitizes tool results before passing back to LLM.
    """

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._pending_actions: Dict[str, PendingAction] = {}

    def register(
        self,
        name: str,
        description: str,
        risk_level: RiskLevel = RiskLevel.READ,
        requires_confirmation: bool = False
    ):
        def decorator(func: Callable):
            sig = inspect.signature(func)
            parameters = {
                "type": "object",
                "properties": {},
                "required": []
            }
            for param_name, param in sig.parameters.items():
                param_type = "string"
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == dict:
                    param_type = "object"
                elif param.annotation == list:
                    param_type = "array"

                parameters["properties"][param_name] = {
                    "type": param_type,
                    "description": f"Parameter {param_name}"
                }
                if param.default == inspect.Parameter.empty:
                    parameters["required"].append(param_name)

            tool_def = ToolDefinition(
                name=name,
                description=description,
                parameters=parameters,
                risk_level=risk_level,
                requires_confirmation=requires_confirmation,
                func=func
            )
            self._tools[name] = tool_def
            return func
        return decorator

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def create_pending_action(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        ttl_seconds: float = 60.0
    ) -> PendingAction:
        """Create short-lived pending action token for high-risk write operations."""
        tool = self.get_tool(tool_name)
        risk = tool.risk_level if tool else RiskLevel.HIGH_RISK_WRITE
        now = time.time()
        action = PendingAction(
            tool_name=tool_name,
            tool_input=self.sanitize_result(tool_input),
            risk_level=risk,
            created_at=now,
            expires_at=now + ttl_seconds,
            status="pending"
        )
        self._pending_actions[action.action_id] = action
        return action

    def validate_and_consume_action(self, action_id: str) -> Optional[PendingAction]:
        """Validate confirmation token and mark as executed. Rejects expired / invalid tokens."""
        action = self._pending_actions.get(action_id)
        if not action:
            return None
        if time.time() > action.expires_at:
            action.status = "expired"
            return None
        if action.status != "pending":
            return None
        action.status = "executed"
        action.confirmed = True
        return action

    def cancel_action(self, action_id: str) -> bool:
        """Cancel a pending action."""
        action = self._pending_actions.get(action_id)
        if action and action.status == "pending":
            action.status = "cancelled"
            return True
        return False

    def sanitize_result(self, result: Any) -> Any:
        """Redacts sensitive credentials or private tokens from tool results and inputs."""
        sensitive_keys = {
            "access_token", "refresh_token", "client_secret", "api_key",
            "password", "authorization", "auth_token", "cookie", "token", "secret"
        }
        if isinstance(result, dict):
            sanitized = {}
            for k, v in result.items():
                if str(k).lower() in sensitive_keys:
                    sanitized[k] = "[REDACTED]"
                else:
                    sanitized[k] = self.sanitize_result(v)
            return sanitized
        elif isinstance(result, list):
            return [self.sanitize_result(item) for item in result]
        return result

    def execute(self, name: str, **kwargs) -> Any:
        tool = self.get_tool(name)
        if not tool or not tool.func:
            raise ValueError(f"Tool '{name}' not found or has no executable function.")
        raw_result = tool.func(**kwargs)
        return self.sanitize_result(raw_result)

# Global Tool Registry instance
registry = ToolRegistry()

# Register core tools
@registry.register(
    name="get_time",
    description="Get the current local time, period of day (morning/afternoon/evening/night), and timezone.",
    risk_level=RiskLevel.READ,
    requires_confirmation=False
)
def _tool_get_time(timezone_str: str = "Asia/Kolkata"):
    return get_time(timezone_str)

@registry.register(
    name="get_location",
    description="Get user's current city, country, and geographic coordinates.",
    risk_level=RiskLevel.READ,
    requires_confirmation=False
)
def _tool_get_location(custom_city: str = None, custom_country: str = None):
    return get_location(custom_city, custom_country)

@registry.register(
    name="calendar_get_events",
    description="Get scheduled calendar events for today or matching a search query.",
    risk_level=RiskLevel.READ,
    requires_confirmation=False
)
def _tool_calendar_get_events(query: str = None):
    return calendar_get_events(query)

@registry.register(
    name="calendar_find_free_time",
    description="Find available free time slots in the user's schedule today.",
    risk_level=RiskLevel.READ,
    requires_confirmation=False
)
def _tool_calendar_find_free_time():
    return calendar_find_free_time()

@registry.register(
    name="calendar_create_event",
    description="Create or schedule a new event on the user's calendar.",
    risk_level=RiskLevel.WRITE,
    requires_confirmation=False
)
def _tool_calendar_create_event(title: str, start_time: str, end_time: str = None, location: str = None, description: str = None):
    return calendar_create_event(title=title, start_time=start_time, end_time=end_time, location=location, description=description)


@registry.register(
    name="gmail_search",
    description="Search emails by sender, subject, or query string.",
    risk_level=RiskLevel.READ,
    requires_confirmation=False
)
def _tool_gmail_search(query: str = None):
    return gmail_search(query)

@registry.register(
    name="gmail_read",
    description="Read full content of an email by ID or index number (1-based).",
    risk_level=RiskLevel.READ,
    requires_confirmation=False
)
def _tool_gmail_read(message_id: str = None, index: int = None):
    return gmail_read(message_id, index)

@registry.register(
    name="sms_read_recent",
    description="Retrieve recent SMS messages received on the user's phone.",
    risk_level=RiskLevel.READ,
    requires_confirmation=False
)
def _tool_sms_read_recent(limit: int = 5):
    return sms_read_recent(limit)

@registry.register(
    name="sms_search",
    description="Search SMS messages by sender contact name or message text content.",
    risk_level=RiskLevel.READ,
    requires_confirmation=False
)
def _tool_sms_search(query: str = None, sender: str = None):
    return sms_search(query=query, sender=sender)

@registry.register(
    name="sms_send_message",
    description="Send an SMS message to a recipient contact name or phone number. Requires explicit confirmation.",
    risk_level=RiskLevel.HIGH_RISK_WRITE,
    requires_confirmation=True
)
def _tool_sms_send_message(recipient: str, text: str):
    return sms_send_message(recipient=recipient, text=text)

@registry.register(
    name="web_search",
    description="Search the web for current facts, places, or general questions.",
    risk_level=RiskLevel.READ,
    requires_confirmation=False
)
def _tool_web_search(query: str):
    return web_search(query)

@registry.register(
    name="product_search",
    description="Search for products or clothing matching category, color, and style.",
    risk_level=RiskLevel.READ,
    requires_confirmation=False
)
def _tool_product_search(category: str, color: str = None, style: str = None):
    return product_search(category, color, style)
