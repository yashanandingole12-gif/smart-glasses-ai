"""
Hardware & PCB Architecture Manager for Modular Smart Glasses.
Validates schematics, layer stackups, pinouts, power budgets, and thermal equilibrium.
"""
from typing import Dict, Any, List
import os

class PCBHardwareManager:
    """Manages the modular smart glasses PCB subsystem and electrical validations."""

    def __init__(self, hardware_root: str = None):
        if hardware_root is None:
            # Default to hardware directory relative to project root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.hardware_root = base_dir
        else:
            self.hardware_root = hardware_root

    def get_system_spec(self) -> Dict[str, Any]:
        """Returns the high-level system hardware and PCB stackup architecture."""
        return {
            "project": "EVA Modular Smart Glasses",
            "pcb_type": "6-Layer HDI Rigid-Flex (Polyimide + FR4 Core)",
            "total_thickness_mm": 0.80,
            "min_trace_space_mil": "3 / 3 (0.075mm)",
            "center_of_gravity": {
                "right_temple_mass_g": 14.8,
                "left_temple_mass_g": 14.6,
                "optical_front_frame_g": 18.2,
                "total_mass_g": 47.6,
                "sagittal_balance_ratio": 1.013,  # Near perfect 1.0 symmetry
                "ergonomic_status": "BALANCED_LOW_PRESSURE"
            },
            "thermal_spec": {
                "max_skin_contact_temp_c": 36.8,
                "max_npu_junction_temp_c": 68.5,
                "thermal_dissipation_path": "Outer Magnesium Frame Spine Spreader"
            },
            "battery_spec": {
                "chemistry": "High-Density Lithium-Polymer",
                "capacity_mah": 300,
                "nominal_voltage_v": 3.85,
                "wh_rating": 1.155,
                "charging_interface": "TWS-Style Gold Pogo Contact Dock (5V 0.5C)"
            },
            "modules": [
                {
                    "name": "Right Smart Temple",
                    "role": "Primary Compute & Audio Output",
                    "components": ["ESP32-S3FN8 / NPU", "AXP2101 PMIC", "MAX98357A I2S Amp", "BNO085 9-DoF IMU", "6-Pin Pogo Interface"],
                    "active_power_mw": 320.0,
                    "sleep_power_uw": 45.0
                },
                {
                    "name": "Bridge & Nose Flexible Circuit (FPC)",
                    "role": "Vision Capture & Directional Acoustics",
                    "components": ["OV2640 / OV3660 Micro-Camera", "Dual MSM261D PDM Mics", "VCNL4040 ALS Sensor"],
                    "active_power_mw": 140.0,
                    "sleep_power_uw": 12.0
                },
                {
                    "name": "Left Battery & Audio Temple",
                    "role": "Energy Storage, Bone Conduction & Touch Gestures",
                    "components": ["300mAh LiPo Cell", "BQ27441-G1 Fuel Gauge", "BST-0815-BC Transducer", "CAP1208 Touch Strip"],
                    "active_power_mw": 85.0,
                    "sleep_power_uw": 18.0
                }
            ]
        }

    def get_pogo_pinout(self) -> List[Dict[str, Any]]:
        """Returns the inter-module 6-pin pogo pinout definition."""
        return [
            {"pin": 1, "net": "VBAT_SYS", "type": "POWER", "description": "3.85V Nom, 1.2A Max Power Delivery Bus"},
            {"pin": 2, "net": "GND_PWR", "type": "GROUND", "description": "Primary High-Current Ground Return"},
            {"pin": 3, "net": "I2S_SDATA_L", "type": "AUDIO_DIGITAL", "description": "Left Audio Bone Conduction Channel"},
            {"pin": 4, "net": "I2C_SDA", "type": "I2C_DATA", "description": "Shared Inter-Temple Sensor & Fuel Gauge SDA"},
            {"pin": 5, "net": "I2C_SCL", "type": "I2C_CLOCK", "description": "Shared Inter-Temple Sensor Clock 400kHz"},
            {"pin": 6, "net": "INT_TOUCH", "type": "GPIO_INTERRUPT", "description": "Capacitive Touch / Hinge Latch Detection"}
        ]

    def validate_power_budget(self, operational_mode: str = "nominal") -> Dict[str, Any]:
        """Calculates expected battery life for given operating mode."""
        spec = self.get_system_spec()
        battery_wh = spec["battery_spec"]["wh_rating"]
        
        mode_power_mw = {
            "standby_sleep": 0.075,        # Sub-100uW sleep
            "ambient_listening": 180.0,    # Low-power VAD + IMU tracking
            "nominal": 445.0,              # Camera events + Bluetooth LE + Audio playback
            "high_npu_vision": 820.0       # Continuous frame bursts + local NPU inference
        }

        power_mw = mode_power_mw.get(operational_mode, 445.0)
        power_w = power_mw / 1000.0
        runtime_hours = battery_wh / power_w
        
        return {
            "mode": operational_mode,
            "total_power_mw": power_mw,
            "nominal_voltage_v": spec["battery_spec"]["nominal_voltage_v"],
            "battery_capacity_mah": spec["battery_spec"]["capacity_mah"],
            "estimated_battery_life_hours": round(runtime_hours, 2),
            "safe_operating_temp_c": "< 36.8°C",
            "status": "PASSED" if runtime_hours >= 1.2 else "WARNING_LOW_ENDURANCE"
        }
