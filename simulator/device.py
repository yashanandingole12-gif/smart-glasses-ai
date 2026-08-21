from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Dict, Any, Optional, List

class DeviceEvent(str, Enum):
    BUTTON_PRESSED = "BUTTON_PRESSED"
    BUTTON_LONG_PRESSED = "BUTTON_LONG_PRESSED"
    CAMERA_READY = "CAMERA_READY"
    DEVICE_CONNECTED = "DEVICE_CONNECTED"
    DEVICE_DISCONNECTED = "DEVICE_DISCONNECTED"
    BATTERY_CHANGED = "BATTERY_CHANGED"
    ERROR = "ERROR"

class DeviceCommand(str, Enum):
    START_LISTENING = "START_LISTENING"
    STOP_LISTENING = "STOP_LISTENING"
    CAPTURE_IMAGE = "CAPTURE_IMAGE"
    PLAY_AUDIO = "PLAY_AUDIO"
    STATUS_REQUEST = "STATUS_REQUEST"

class GlassesDevice(ABC):
    """
    Hardware-agnostic interface implemented by both:
    1. Laptop Simulator (SimulatedGlassesDevice)
    2. Android Companion Hub / Real ESP32-S3 BLE (RealEsp32BleDevice)
    """

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection with the glasses device."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the glasses device."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check connection status."""
        pass

    @abstractmethod
    async def send_command(self, command: DeviceCommand, payload: Optional[Dict[str, Any]] = None) -> bool:
        """Send command to the device."""
        pass

    @abstractmethod
    def register_event_listener(self, event: DeviceEvent, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register listener for hardware events."""
        pass

    @abstractmethod
    def get_battery(self) -> int:
        """Get current battery percentage (0-100)."""
        pass

class SimulatedGlassesDevice(GlassesDevice):
    """
    Laptop Simulator implementation of GlassesDevice.
    """
    def __init__(self, initial_battery: int = 82):
        self._connected = False
        self._battery = initial_battery
        self._listeners: Dict[DeviceEvent, List[Callable[[Dict[str, Any]], None]]] = {
            e: [] for e in DeviceEvent
        }

    async def connect(self) -> bool:
        self._connected = True
        self._emit(DeviceEvent.DEVICE_CONNECTED, {"device_type": "SIMULATED_ESP32", "battery": self._battery})
        return True

    async def disconnect(self) -> None:
        self._connected = False
        self._emit(DeviceEvent.DEVICE_DISCONNECTED, {})

    def is_connected(self) -> bool:
        return self._connected

    def get_battery(self) -> int:
        return self._battery

    def set_battery(self, level: int):
        self._battery = max(0, min(100, level))
        self._emit(DeviceEvent.BATTERY_CHANGED, {"battery": self._battery})

    async def send_command(self, command: DeviceCommand, payload: Optional[Dict[str, Any]] = None) -> bool:
        # In simulator mode, handles simulated hardware commands
        return True

    def register_event_listener(self, event: DeviceEvent, callback: Callable[[Dict[str, Any]], None]) -> None:
        if event in self._listeners:
            self._listeners[event].append(callback)

    def trigger_button_press(self):
        """Simulates physical hardware button press."""
        self._emit(DeviceEvent.BUTTON_PRESSED, {"timestamp_ms": 0})

    def _emit(self, event: DeviceEvent, data: Dict[str, Any]):
        for cb in self._listeners.get(event, []):
            try:
                cb(data)
            except Exception as ex:
                pass
