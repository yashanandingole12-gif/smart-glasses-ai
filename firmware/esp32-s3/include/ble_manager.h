#pragma once

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <functional>

// Custom Smart Glasses GATT Service & Characteristic UUIDs
#define SERVICE_UUID           "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
#define CHAR_COMMAND_UUID      "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
#define CHAR_EVENT_UUID        "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
#define CHAR_STATUS_UUID       "6e400004-b5a3-f393-e0a9-e50e24dcca9e"
#define CHAR_BATTERY_UUID      "6e400005-b5a3-f393-e0a9-e50e24dcca9e"
#define CHAR_AUDIO_RX_UUID     "6e400006-b5a3-f393-e0a9-e50e24dcca9e"

// Framed Audio & Text Packet Protocol Specification
#define BLE_PROTOCOL_VERSION   0x01

enum BlePacketType : uint8_t {
    PKT_TYPE_TEXT           = 0x01,
    PKT_TYPE_AUDIO_START    = 0x02,
    PKT_TYPE_AUDIO_DATA     = 0x03,
    PKT_TYPE_AUDIO_END      = 0x04,
    PKT_TYPE_AUDIO_ACK      = 0x05,
    PKT_TYPE_AUDIO_NACK     = 0x06,
    PKT_TYPE_DEVICE_STATUS  = 0x07
};

#pragma pack(push, 1)
struct BlePacketHeader {
    uint8_t  version;        // Protocol version (0x01)
    uint8_t  messageId;      // Logical message ID
    uint8_t  type;           // BlePacketType
    uint16_t sequence;       // Chunk sequence number (0-indexed)
    uint16_t totalChunks;    // Total chunks in transmission
    uint16_t payloadLength;  // Byte length of payload
};
#pragma pack(pop)

enum class BleDeviceEvent {
    BUTTON_PRESSED,
    BUTTON_LONG_PRESSED,
    CAMERA_READY,
    DEVICE_CONNECTED,
    DEVICE_DISCONNECTED,
    BATTERY_CHANGED,
    AUDIO_RX_STARTED,
    AUDIO_RX_FINISHED
};

class BleManager {
public:
    static BleManager& getInstance() {
        static BleManager instance;
        return instance;
    }

    void init(const String& deviceName = "SmartGlasses-S3");
    void sendEvent(const String& eventName, const String& payload = "");
    void updateBattery(uint8_t percentage);
    void updateStatus(const String& statusJson);
    bool isClientConnected() const;

    void setCommandCallback(std::function<void(const String&)> cb);
    void setAudioRxCallback(std::function<void(const uint8_t*, size_t)> cb);

private:
    BleManager();
    bool _connected = false;
    BLEServer* _server = nullptr;
    BLECharacteristic* _commandChar = nullptr;
    BLECharacteristic* _eventChar = nullptr;
    BLECharacteristic* _statusChar = nullptr;
    BLECharacteristic* _batteryChar = nullptr;
    BLECharacteristic* _audioRxChar = nullptr;
    std::function<void(const String&)> _commandCallback = nullptr;
    std::function<void(const uint8_t*, size_t)> _audioRxCallback = nullptr;

    friend class BleServerCallbacksHandler;
    friend class BleCommandCallbacksHandler;
    friend class BleAudioRxCallbacksHandler;
};

