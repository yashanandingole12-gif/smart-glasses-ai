# Smart Glasses AI Assistant - REST & WebSocket API

Base URL: `http://127.0.0.1:8000`

---

## Endpoints

### 1. Health Check
`GET /api/v1/health`
- **Response**:
```json
{
  "status": "ok",
  "version": "0.1.0",
  "device_mode": "SIMULATOR_READY",
  "llm_provider": "mock"
}
```

---

### 2. Process Agent Message
`POST /api/v1/agent/message`
- **Request Body**:
```json
{
  "session_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "message": "Good morning.",
  "context": {
    "time": {
      "local_time": "08:15 AM",
      "period": "morning",
      "timezone": "Asia/Kolkata"
    },
    "location": {
      "city": "Nagpur",
      "country": "India"
    },
    "calendar": {
      "next_event": {
        "title": "Machine Learning Class",
        "start_time": "10:30 AM"
      }
    },
    "device": {
      "battery": 82,
      "camera_available": true,
      "microphone_available": true
    }
  }
}
```

- **Response Body**:
```json
{
  "session_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "response": "Good morning. It's 8:15 AM and you're in Nagpur. You have class at 10:30. How can I help?",
  "actions": [],
  "requires_confirmation": false,
  "sources": ["context_engine", "calendar", "sqlite_memory"],
  "metadata": {
    "latency_ms": 42.5,
    "period": "morning"
  }
}
```

---

### 3. Vision Analysis
`POST /api/v1/vision/analyze`
- **Request**:
```json
{
  "session_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "image_base64": "<base64_encoded_jpeg>"
}
```
- **Response**:
```json
{
  "description": "A person wearing black cargo pants with side pockets and a casual jacket.",
  "structured_attributes": {
    "category": "pants",
    "color": "black",
    "style": "cargo"
  }
}
```

---

### 4. WebSocket Streaming
`ws://127.0.0.1:8000/ws/assistant`
- Bi-directional JSON stream for low-latency voice interaction.
