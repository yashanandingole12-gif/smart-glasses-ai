import pytest
from backend.app.services.tool_registry import registry
from backend.app.models.schemas import RiskLevel

def test_registry_contains_initial_tools():
    tool_names = [t.name for t in registry.list_tools()]
    expected_tools = [
        "get_time",
        "get_location",
        "calendar_get_events",
        "calendar_find_free_time",
        "gmail_search",
        "gmail_read",
        "web_search",
        "product_search"
    ]
    for exp in expected_tools:
        assert exp in tool_names, f"Expected tool '{exp}' not found in registry"

def test_execute_get_time():
    result = registry.execute("get_time", timezone_str="Asia/Kolkata")
    assert "time" in result
    assert "period" in result
    assert result["timezone"] == "Asia/Kolkata"

def test_execute_get_location():
    result = registry.execute("get_location")
    assert result["city"] == "Nagpur"
    assert "latitude" in result

def test_execute_calendar_get_events():
    result = registry.execute("calendar_get_events")
    assert "events" in result
    assert len(result["events"]) > 0
    assert result["events"][0]["title"] == "Machine Learning Class"

def test_execute_product_search():
    result = registry.execute("product_search", category="cargo pants", color="black")
    assert "products" in result
    assert len(result["products"]) > 0
    assert "Pants" in result["products"][0]["name"]
