#include "device_manager.h"

DeviceManager::DeviceManager() {}

void DeviceManager::init() {
    // Initialize subsystems
    ButtonManager::getInstance().init(PIN_BUTTON_PTT);
    BatteryManager::getInstance().init(PIN_BATTERY_ADC);
    AudioManager::getInstance().init();
    CameraManager::getInstance().init();
    BleManager::getInstance().init("SmartGlasses-S3");

    // Setup button callbacks for Push-to-Talk and Gesture Actions
    ButtonManager::getInstance().setOnPressStartCallback([]() {
        BleManager::getInstance().sendEvent("TALK_START", "{\"action\":\"listen\"}");
    });

    ButtonManager::getInstance().setOnReleaseCallback([]() {
        BleManager::getInstance().sendEvent("TALK_STOP", "{\"action\":\"stop_listen\"}");
    });

    ButtonManager::getInstance().setOnPressCallback([]() {
        BleManager::getInstance().sendEvent("BUTTON_PRESSED", "{\"type\":\"short_press\"}");
    });

    ButtonManager::getInstance().setOnLongPressCallback([]() {
        BleManager::getInstance().sendEvent("BUTTON_LONG_PRESSED", "{\"type\":\"long_press\"}");
    });

    // Setup BLE command callback
    BleManager::getInstance().setCommandCallback([this](const String& cmd) {
        this->handleIncomingCommand(cmd);
    });
}

void DeviceManager::handleIncomingCommand(const String& cmdJson) {
    if (cmdJson.indexOf("START_LISTENING") >= 0) {
        AudioManager::getInstance().startMicrophone();
    } else if (cmdJson.indexOf("STOP_LISTENING") >= 0) {
        AudioManager::getInstance().stopMicrophone();
    } else if (cmdJson.indexOf("CAPTURE_IMAGE") >= 0) {
        uint8_t* buf = nullptr;
        size_t len = 0;
        if (CameraManager::getInstance().captureImage(&buf, &len)) {
            BleManager::getInstance().sendEvent("CAMERA_READY", "{\"status\":\"captured\"}");
            CameraManager::getInstance().releaseBuffer();
        }
    } else if (cmdJson.indexOf("STATUS_REQUEST") >= 0) {
        uint8_t batt = BatteryManager::getInstance().getBatteryPercentage();
        BleManager::getInstance().updateBattery(batt);
        BleManager::getInstance().sendEvent("BATTERY_CHANGED", "{\"battery\":" + String(batt) + "}");
    }
}

void DeviceManager::update() {
    ButtonManager::getInstance().update();

    // Periodic battery report every 30 seconds
    if (millis() - _lastBatteryReportTime > 30000) {
        _lastBatteryReportTime = millis();
        uint8_t batt = BatteryManager::getInstance().getBatteryPercentage();
        BleManager::getInstance().updateBattery(batt);
    }
}
