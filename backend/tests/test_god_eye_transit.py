import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_transit_traffic_endpoint():
    """Verify GET /api/v1/transit/traffic returns structured road telemetry."""
    resp = client.get("/api/v1/transit/traffic?location=western+express+highway")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "Western Express Highway" in data["data"]["name"]
    assert "spoken_response" in data
    assert "oled_lines" in data
    assert len(data["oled_lines"]) >= 2

def test_transit_metro_endpoint():
    """Verify GET /api/v1/transit/metro returns stations and arrival countdowns."""
    resp = client.get("/api/v1/transit/metro?query=andheri")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "Andheri Metro" in data["station"]["name"]
    assert "spoken_response" in data
    assert "oled_lines" in data
    assert len(data["all_stations"]) >= 3

def test_transit_trains_endpoint():
    """Verify GET /api/v1/transit/trains returns schedules and platform numbers."""
    resp = client.get("/api/v1/transit/trains?query=churchgate")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "train" in data
    assert "spoken_response" in data
    assert "oled_lines" in data

def test_transit_flights_endpoint():
    """Verify GET /api/v1/transit/flights returns gate, terminal, and carousel details."""
    resp = client.get("/api/v1/transit/flights?flight_number=6E204")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["flight"]["flight_number"] == "6E-204"
    assert "Gate 48B" in data["flight"]["gate"]
    assert "Terminal 2" in data["flight"]["terminal"]

def test_transit_query_post_endpoint():
    """Verify POST /api/v1/transit/query routes natural language glasses queries."""
    # 1. Traffic query
    t_resp = client.post("/api/v1/transit/query", json={"query": "where is the traffic on western express"})
    assert t_resp.status_code == 200
    t_data = t_resp.json()
    assert t_data["success"] is True
    assert "Western Express" in t_data["spoken_response"]

    # 2. Metro query
    m_resp = client.post("/api/v1/transit/query", json={"query": "where is the nearest metro station"})
    assert m_resp.status_code == 200
    m_data = m_resp.json()
    assert m_data["success"] is True
    assert "Metro" in m_data["spoken_response"]

    # 3. Flight query
    f_resp = client.post("/api/v1/transit/query", json={"query": "check flight status of 6E-204"})
    assert f_resp.status_code == 200
    f_data = f_resp.json()
    assert f_data["success"] is True
    assert "6E-204" in f_data["spoken_response"]
