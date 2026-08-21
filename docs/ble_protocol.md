# ESP32-S3 BLE Protocol Specification

## Service UUID
- **Smart Glasses GATT Service**: `6e400001-b5a3-f393-e0a9-e50e24dcca9e`

---

## Characteristics

| Characteristic | UUID | Properties | Description |
|---|---|---|---|
| **COMMAND** | `6e400002-b5a3-f393-e0a9-e50e24dcca9e` | Write, Write Without Response | Commands sent from Android to ESP32 (`START_LISTENING`, `STOP_LISTENING`, `CAPTURE_IMAGE`, `PLAY_AUDIO`, `STATUS_REQUEST`) |
| **EVENT** | `6e400003-b5a3-f393-e0a9-e50e24dcca9e` | Notify | Hardware events from ESP32 to Android (`BUTTON_PRESSED`, `BUTTON_LONG_PRESSED`, `CAMERA_READY`, `DEVICE_CONNECTED`) |
| **STATUS** | `6e400004-b5a3-f393-e0a9-e50e24dcca9e` | Read, Notify | Device state JSON (connection, sensors, memory) |
| **BATTERY** | `6e400005-b5a3-f393-e0a9-e50e24dcca9e` | Read, Notify | 1-byte battery percentage (0-100) |

---

## Event Payload Formats (ESP32 -> Phone)

### 1. `BUTTON_PRESSED`
```json
{
  "event": "BUTTON_PRESSED",
  "payload": {
    "type": "short_press",
    "timestamp_ms": 12450
  }
}
```

### 2. `CAMERA_READY`
```json
{
  "event": "CAMERA_READY",
  "payload": {
    "status": "captured",
    "size_bytes": 48200
  }
}
```

### 3. `BATTERY_CHANGED`
```json
{
  "event": "BATTERY_CHANGED",
  "payload": {
    "battery": 82
  }
}
```

---

## Command Payload Formats (Phone -> ESP32)

### 1. `START_LISTENING`
```json
{
  "command": "START_LISTENING",
  "payload": {}
}
```

### 2. `CAPTURE_IMAGE`
```json
{
  "command": "CAPTURE_IMAGE",
  "payload": {
    "quality": "high"
  }
}
```
