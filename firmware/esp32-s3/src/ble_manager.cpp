#include "ble_manager.h"
#include <esp_bt.h>
#include <esp_bt_main.h>
#include <esp_gap_ble_api.h>

class BleServerCallbacksHandler : public BLEServerCallbacks {
  void onConnect(BLEServer *pServer) override {
    BleManager::getInstance()._connected = true;
    Serial.println(
        "[BLE] Mobile phone connected to Smart Glasses GATT server!");

    // Boost TX power on all connection handles for robust coexistence with TWS
    esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_CONN_HDL0, ESP_PWR_LVL_P9);
    esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_CONN_HDL1, ESP_PWR_LVL_P9);
    esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_DEFAULT, ESP_PWR_LVL_P9);
  }

  void onDisconnect(BLEServer *pServer) override {
    BleManager::getInstance()._connected = false;
    Serial.println("[BLE] Mobile phone disconnected from Smart Glasses. "
                   "Restarting fast advertising for instant reconnect...");
    delay(20);
    BLEDevice::startAdvertising();
  }
};

class BleCommandCallbacksHandler : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) override {
    String val = pCharacteristic->getValue().c_str();
    if (val.length() > 0 && BleManager::getInstance()._commandCallback) {
      BleManager::getInstance()._commandCallback(val);
    }
  }
};

class BleAudioRxCallbacksHandler : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) override {
    uint8_t *pData = pCharacteristic->getData();
    size_t len = pCharacteristic->getLength();
    if (pData != nullptr && len > 0) {
      // Check if packet matches framed protocol header
      if (len >= sizeof(BlePacketHeader) && pData[0] == BLE_PROTOCOL_VERSION) {
        BlePacketHeader hdr;
        memcpy(&hdr, pData, sizeof(BlePacketHeader));
        size_t payloadOffset = sizeof(BlePacketHeader);
        size_t payloadLen = hdr.payloadLength;

        if (payloadOffset + payloadLen <= len) {
          const uint8_t *pPayload = pData + payloadOffset;
          if (hdr.type == PKT_TYPE_TEXT) {
            String textMsg((const char *)pPayload, payloadLen);
            Serial.printf("[BLE-FRAME] RX TEXT (Msg %d, Seq %d/%d): '%s'\n",
                          hdr.messageId, hdr.sequence + 1, hdr.totalChunks,
                          textMsg.c_str());
            if (BleManager::getInstance()._commandCallback) {
              BleManager::getInstance()._commandCallback("TEXT_OLED:" +
                                                         textMsg);
            }
          } else if (hdr.type == PKT_TYPE_AUDIO_DATA ||
                     hdr.type == PKT_TYPE_AUDIO_START) {
            if (BleManager::getInstance()._audioRxCallback && payloadLen > 0) {
              BleManager::getInstance()._audioRxCallback(pPayload, payloadLen);
            }
          } else if (hdr.type == PKT_TYPE_AUDIO_END) {
            Serial.printf("[BLE-FRAME] RX AUDIO_END (Msg %d)\n", hdr.messageId);
          }

          // Send ACK back to companion phone
          String ackPayload = "{\"msg_id\":" + String(hdr.messageId) +
                              ",\"seq\":" + String(hdr.sequence) +
                              ",\"status\":\"ACK\"}";
          BleManager::getInstance().sendEvent("AUDIO_ACK", ackPayload);
          return;
        }
      }

      // Raw PCM / Unframed fallback
      if (BleManager::getInstance()._audioRxCallback) {
        BleManager::getInstance()._audioRxCallback(pData, len);
      }
    }
  }
};

BleManager::BleManager() {}

void BleManager::init(const String &deviceName) {
  BLEDevice::init(deviceName.c_str());

  // 1. Maximize BLE RF Transmit Power (+9 dBm) for rock-solid TWS coexistence
  esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_DEFAULT, ESP_PWR_LVL_P9);
  esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_ADV, ESP_PWR_LVL_P9);
  esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_SCAN, ESP_PWR_LVL_P9);

  // 2. Set MTU to 512 for large telemetry and audio frames
  BLEDevice::setMTU(512);

  _server = BLEDevice::createServer();
  _server->setCallbacks(new BleServerCallbacksHandler());

  BLEService *pService = _server->createService(SERVICE_UUID);

  // Command Characteristic (Write)
  _commandChar = pService->createCharacteristic(
      CHAR_COMMAND_UUID,
      BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR);
  _commandChar->setCallbacks(new BleCommandCallbacksHandler());

  // Event Characteristic (Notify)
  _eventChar = pService->createCharacteristic(
      CHAR_EVENT_UUID, BLECharacteristic::PROPERTY_NOTIFY);
  _eventChar->addDescriptor(new BLE2902());

  // Status Characteristic (Read/Notify)
  _statusChar = pService->createCharacteristic(
      CHAR_STATUS_UUID,
      BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  _statusChar->addDescriptor(new BLE2902());

  // Battery Characteristic (Read/Notify)
  _batteryChar = pService->createCharacteristic(
      CHAR_BATTERY_UUID,
      BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  _batteryChar->addDescriptor(new BLE2902());

  // Audio RX Characteristic (Write / Write Without Response for streaming audio
  // to speaker)
  _audioRxChar = pService->createCharacteristic(
      CHAR_AUDIO_RX_UUID,
      BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR);
  _audioRxChar->setCallbacks(new BleAudioRxCallbacksHandler());

  pService->start();

  // 3. Configure Fast Advertising for phone discovery during A2DP playback
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);

  // Aggressive connection interval recommendations (7.5ms to 22.5ms)
  pAdvertising->setMinPreferred(0x06); // 7.5 ms
  pAdvertising->setMaxPreferred(0x12); // 22.5 ms

  // Fast, dense advertising interval (20ms to 40ms)
  pAdvertising->setMinInterval(0x20); // 32 * 0.625ms = 20ms
  pAdvertising->setMaxInterval(0x40); // 64 * 0.625ms = 40ms

  BLEDevice::startAdvertising();
  Serial.printf("[BLE] BLE Advertising started successfully for '%s' (TX: "
                "+9dBm, Interval: 20-40ms, MTU: 512)\n",
                deviceName.c_str());
}

void BleManager::sendEvent(const String &eventName, const String &payload) {
  if (_connected && _eventChar) {
    String json;
    if (payload.length() > 0 && payload != "{}") {
      json = "{\"event\":\"" + eventName + "\",\"payload\":" + payload + "}";
    } else {
      json = "{\"event\":\"" + eventName + "\"}";
    }
    _eventChar->setValue((uint8_t *)json.c_str(), json.length());
    _eventChar->notify();
    Serial.printf("[BLE] Sent Event Notification: %s\n", json.c_str());
  }
}

void BleManager::sendAudioChunk(const uint8_t *data, size_t len) {
  if (_connected && _eventChar && data && len > 0) {
    _eventChar->setValue((uint8_t *)data, len);
    _eventChar->notify();
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

void BleManager::updateStatus(const String &statusJson) {
  if (_statusChar) {
    _statusChar->setValue((uint8_t *)statusJson.c_str(), statusJson.length());
    if (_connected) {
      _statusChar->notify();
    }
  }
}

bool BleManager::isClientConnected() const { return _connected; }

void BleManager::setCommandCallback(std::function<void(const String &)> cb) {
  _commandCallback = cb;
}

void BleManager::setAudioRxCallback(
    std::function<void(const uint8_t *, size_t)> cb) {
  _audioRxCallback = cb;
}
