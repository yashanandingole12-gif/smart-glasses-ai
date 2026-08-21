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

enum class BleDeviceEvent {
    BUTTON_PRESSED,
    BUTTON_LONG_PRESSED,
    CAMERA_READY,
    DEVICE_CONNECTED,
    DEVICE_DISCONNECTED,
    BATTERY_CHANGED
};

class BleManager {
public:
    static BleManager& getInstance() {
        static BleManager instance;
        return instance;
    }

    void init(const String& deviceName = "SmartGlasses-S3");
    void sendEvent(const String& eventName, const String& payload = "{}");
    void updateBattery(uint8_t percentage);
    void updateStatus(const String& statusJson);
    bool isClientConnected() const;

    void setCommandCallback(std::function<void(const String&)> cb);

private:
    BleManager();
    bool _connected = false;
    BLEServer* _server = nullptr;
    BLECharacteristic* _commandChar = nullptr;
    BLECharacteristic* _eventChar = nullptr;
    BLECharacteristic* _statusChar = nullptr;
    BLECharacteristic* _batteryChar = nullptr;
    std::function<void(const String&)> _commandCallback = nullptr;

    friend class BleServerCallbacksHandler;
    friend class BleCommandCallbacksHandler;
};
