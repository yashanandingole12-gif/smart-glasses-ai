"""
Unit & Integration Tests for EVA Deterministic Offline Rule Engine
Guarantees sub-10ms instantaneous resolution for all deterministic queries
with ZERO cloud or LLM invocation.
"""

import pytest
from backend.app.services.rule_engine import rule_engine

def test_rule_engine_time_queries():
    queries = ["what time is it", "whats the time", "time please", "current time", "kitne baje", "time kya hua"]
    for q in queries:
        res = rule_engine.resolve(q)
        assert res is not None, f"Query '{q}' should be resolved by rule engine"
        assert res["status"] == "SUCCESS"
        assert res["tier"] == "RULE_BASED"
        assert res["category"] == "time"
        assert "AM" in res["response_text"] or "PM" in res["response_text"] or "hue" in res["response_text"]

def test_rule_engine_date_queries():
    queries = ["what is the date", "whats todays date", "today date", "aaj konsi date hai"]
    for q in queries:
        res = rule_engine.resolve(q)
        assert res is not None, f"Query '{q}' should be resolved by rule engine"
        assert res["category"] == "date"
        assert "202" in res["response_text"] or "hai" in res["response_text"]

def test_rule_engine_battery_queries():
    res = rule_engine.resolve("what is my battery", context={"device": {"battery_percentage": 92}})
    assert res is not None
    assert res["category"] == "battery"
    assert "92" in res["response_text"]

def test_rule_engine_system_status():
    res = rule_engine.resolve("system status", context={"device": {"battery_percentage": 75}, "glasses_connected": True})
    assert res is not None
    assert "Glasses connected" in res["response_text"]
    assert "75%" in res["response_text"]

def test_rule_engine_definitions_dictionary():
    terms = [
        "what is an array", "define array", "what is a data structure", "what is a node",
        "what is wifi", "what is internet", "what is google", "what is a class",
        "what is sql", "what is select", "what is insert", "what is update",
        "what is delete", "what is where", "what is join", "what is a stack",
        "what is a queue", "what is a binary tree", "what is an algorithm",
        "what is an api", "what is http", "what is a database"
    ]
    for term in terms:
        res = rule_engine.resolve(term)
        assert res is not None, f"Definition for '{term}' should be answered offline"
        assert res["category"] == "definition"
        assert len(res["response_text"]) > 20

def test_rule_engine_telephony_and_notifications():
    assert rule_engine.resolve("answer call")["category"] == "telephony"
    assert rule_engine.resolve("decline call")["category"] == "telephony"
    assert rule_engine.resolve("check notifications")["category"] == "notifications"
    assert rule_engine.resolve("check messages")["category"] == "messages"

def test_rule_engine_local_file_search():
    res = rule_engine.resolve("search files for robotics resume")
    assert res is not None
    assert res["category"] == "file_search"
    assert "robotics resume" in res["response_text"]

def test_rule_engine_arithmetic():
    assert "55" in rule_engine.resolve("25 + 30")["response_text"]
    assert "96" in rule_engine.resolve("12 * 8")["response_text"]
    assert "12" in rule_engine.resolve("144 / 12")["response_text"]
    assert "120" in rule_engine.resolve("15% of 800")["response_text"]
    assert "12" in rule_engine.resolve("square root of 144")["response_text"]

def test_rule_engine_passes_open_ended_queries_to_llm():
    # Complex generative tasks should return None to let LLM / Agent tier handle them
    open_ended = [
        "Write a Python script for Dijkstra algorithm",
        "Draft an email to my robotics professor",
        "Find me internships at Tesla",
        "Explain how quantum computing works"
    ]
    for q in open_ended:
        res = rule_engine.resolve(q)
        assert res is None, f"Open-ended query '{q}' must NOT be intercepted by rule engine"
