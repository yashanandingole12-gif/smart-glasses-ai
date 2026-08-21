from typing import Dict, Any, Callable, Optional, List
from pydantic import BaseModel, Field
import inspect
from backend.app.models.schemas import RiskLevel
from backend.app.tools import (
    get_time,
    get_location,
    calendar_get_events,
    calendar_find_free_time,
    gmail_search,
    gmail_read,
    web_search,
    product_search
)

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    risk_level: RiskLevel = RiskLevel.READ
    requires_confirmation: bool = False
    func: Optional[Any] = Field(default=None, exclude=True)

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

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

    def execute(self, name: str, **kwargs) -> Any:
        tool = self.get_tool(name)
        if not tool or not tool.func:
            raise ValueError(f"Tool '{name}' not found or has no executable function.")
        return tool.func(**kwargs)

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
