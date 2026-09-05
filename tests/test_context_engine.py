import pytest
from backend.app.services.context_engine import context_engine
from backend.app.models.schemas import TimePeriod, FullContextPayload

def test_compute_temporal_context():
    ctx = context_engine.compute_temporal_context("Asia/Kolkata")
    assert ctx.local_time is not None
    assert ctx.period in [TimePeriod.MORNING, TimePeriod.AFTERNOON, TimePeriod.EVENING, TimePeriod.NIGHT]
    assert ctx.timezone == "Asia/Kolkata"

def test_get_relevant_context_default():
    full_ctx = context_engine.get_relevant_context("Good morning.")
    assert full_ctx.time is not None
    assert full_ctx.location.city == "Nagpur"
    assert full_ctx.calendar is not None
    assert full_ctx.device.battery > 0

def test_get_relevant_context_with_client_override():
    client_ctx = context_engine.get_relevant_context("test")
    client_ctx.location.city = "Mumbai"
    client_ctx.device.battery = 95

    merged_ctx = context_engine.get_relevant_context("Good morning", client_context=client_ctx)
    assert merged_ctx.location.city == "Mumbai"
    assert merged_ctx.device.battery == 95
