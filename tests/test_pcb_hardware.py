"""
Test Suite for Modular Smart Glasses Hardware & PCB Subsystem.
Validates 6-layer rigid-flex stackup, pogo-pin bus, power budgets, and center-of-gravity balance.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from hardware.pcb.pcb_manager import PCBHardwareManager

client = TestClient(app)


class TestPCBHardwareArchitecture:
    """Validates hardware PCB specifications and power/thermal constraints."""

    def test_pcb_manager_spec_and_balance(self):
        manager = PCBHardwareManager()
        spec = manager.get_system_spec()
        
        assert spec["pcb_type"] == "6-Layer HDI Rigid-Flex (Polyimide + FR4 Core)"
        assert spec["total_thickness_mm"] == 0.80
        cog = spec["center_of_gravity"]
        assert cog["total_mass_g"] == 47.6
        # Check bilateral weight symmetry
        assert 0.95 <= cog["sagittal_balance_ratio"] <= 1.05
        assert cog["ergonomic_status"] == "BALANCED_LOW_PRESSURE"

    def test_pogo_pinout_definition(self):
        manager = PCBHardwareManager()
        pins = manager.get_pogo_pinout()
        assert len(pins) == 6
        nets = [p["net"] for p in pins]
        assert "VBAT_SYS" in nets
        assert "GND_PWR" in nets
        assert "I2S_SDATA_L" in nets
        assert "I2C_SDA" in nets
        assert "I2C_SCL" in nets
        assert "INT_TOUCH" in nets

    def test_power_budget_and_thermal_safety(self):
        manager = PCBHardwareManager()
        nominal = manager.validate_power_budget("nominal")
        assert nominal["status"] == "PASSED"
        assert nominal["estimated_battery_life_hours"] >= 2.0

        vision = manager.validate_power_budget("high_npu_vision")
        assert vision["estimated_battery_life_hours"] >= 1.2

        sleep = manager.validate_power_budget("standby_sleep")
        assert sleep["estimated_battery_life_hours"] > 100.0

    def test_hardware_api_endpoints(self):
        resp = client.get("/api/v1/hardware/spec")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "spec" in data

        resp_pogo = client.get("/api/v1/hardware/pogo-pinout")
        assert resp_pogo.status_code == 200
        assert len(resp_pogo.json()["pinout"]) == 6

        resp_budget = client.post("/api/v1/hardware/power-budget", json={"mode": "ambient_listening"})
        assert resp_budget.status_code == 200
        assert resp_budget.json()["budget"]["estimated_battery_life_hours"] > 5.0
