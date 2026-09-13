#include "ble_manager.h"

class BleServerCallbacksHandler : public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) override {
        BleManager::getInstance()._connected = true;
        Serial.println("[BLE] Mobile phone connected to Smart Glasses GATT server!");
        // Note: Do not send notifications immediately in onConnect.
        // Wait for the mobile client to subscribe to the CCCD descriptor (0x2902).
    }

    void onDisconnect(BLEServer* pServer) override {
        BleManager::getInstance()._connected = false;
        Serial.println("[BLE] Mobile phone disconnected from Smart Glasses. Restarting advertising...");
        delay(50);
        BLEDevice::startAdvertising();
    }
};

class BleCommandCallbacksHandler : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic* pCharacteristic) override {
        String val = pCharacteristic->getValue().c_str();
        if (val.length() > 0 && BleManager::getInstance()._commandCallback) {
            BleManager::getInstance()._commandCallback(val);
        }
    }
};

BleManager::BleManager() {}

void BleManager::init(const String& deviceName) {
    BLEDevice::init(deviceName.c_str());
    _server = BLEDevice::createServer();
    _server->setCallbacks(new BleServerCallbacksHandler());

    BLEService* pService = _server->createService(SERVICE_UUID);

    // Command Characteristic (Write)
    _commandChar = pService->createCharacteristic(
        CHAR_COMMAND_UUID,
        BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR
    );
    _commandChar->setCallbacks(new BleCommandCallbacksHandler());

    // Event Characteristic (Notify)
    _eventChar = pService->createCharacteristic(
        CHAR_EVENT_UUID,
        BLECharacteristic::PROPERTY_NOTIFY
    );
    _eventChar->addDescriptor(new BLE2902());

    // Status Characteristic (Read/Notify)
    _statusChar = pService->createCharacteristic(
        CHAR_STATUS_UUID,
        BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
    );
    _statusChar->addDescriptor(new BLE2902());

    // Battery Characteristic (Read/Notify)
    _batteryChar = pService->createCharacteristic(
        CHAR_BATTERY_UUID,
        BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
    );
    _batteryChar->addDescriptor(new BLE2902());

    pService->start();

    BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->setScanResponse(true);
    pAdvertising->setMinPreferred(0x06); // iOS / Android connection interval recommendations
    pAdvertising->setMaxPreferred(0x12);
    pAdvertising->setMinInterval(0x20);  // 20ms advertising interval
    pAdvertising->setMaxInterval(0x40);  // 40ms advertising interval
    BLEDevice::startAdvertising();
    Serial.printf("[BLE] BLE Advertising started successfully for '%s'\n", deviceName.c_str());
}

void BleManager::sendEvent(const String& eventName, const String& payload) {
    if (_connected && _eventChar) {
        String json;
        if (payload.length() > 0 && payload != "{}") {
            json = "{\"event\":\"" + eventName + "\",\"payload\":" + payload + "}";
        } else {
            json = "{\"event\":\"" + eventName + "\"}";
        }
        _eventChar->setValue(json.c_str());
        _eventChar->notify();
        Serial.printf("[BLE] Sent Event Notification: %s\n", json.c_str());
    }
}

void BleManager::updateBattery(uint8_t percentage) {
    if (_batteryChar) {
        _batteryChar->setValue(&percentage, 1);
        if (_connected) {
            _batteryChar->notify();
        }
    }
}

void BleManager::updateStatus(const String& statusJson) {
    if (_statusChar) {
        _statusChar->setValue(statusJson.c_str());
        if (_connected) {
            _statusChar->notify();
        }
    }
}

bool BleManager::isClientConnected() const {
    return _connected;
}

void BleManager::setCommandCallback(std::function<void(const String&)> cb) {
    _commandCallback = cb;
}
