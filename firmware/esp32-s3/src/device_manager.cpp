#include "device_manager.h"

DeviceManager::DeviceManager() {}

void DeviceManager::init() {
    Serial.println("[DEVICE] Initializing Subsystems...");

    // 1. Button PTT
    ButtonManager::getInstance().init(PIN_BUTTON_PTT);
    Serial.printf("[DEVICE] Button PTT initialized on GPIO %d (Debounce: %d ms)\n", PIN_BUTTON_PTT, BUTTON_DEBOUNCE_MS);

    // 2. Battery ADC
    BatteryManager::getInstance().init(PIN_BATTERY_ADC);
    uint8_t initialBatt = BatteryManager::getInstance().getBatteryPercentage();
    Serial.printf("[DEVICE] Battery ADC initialized on GPIO %d (Initial: %d%%)\n", PIN_BATTERY_ADC, initialBatt);

    // 3. Audio Subsystem
    AudioManager::getInstance().init();
    Serial.println("[DEVICE] Audio Manager initialized (I2S Mic/Spk ready)");

    // 4. Camera Subsystem
    CameraManager::getInstance().init();
    Serial.println("[DEVICE] Camera Manager initialized");

    // 5. BLE Stack
    BleManager::getInstance().init("SmartGlasses-S3");
    Serial.println("[DEVICE] BLE Manager initialized. Advertising as 'SmartGlasses-S3'");

    // Setup button callbacks for Push-to-Talk and Gesture Actions
    ButtonManager::getInstance().setOnPressStartCallback([]() {
        Serial.println("[BUTTON] >>> PRESS START -> Sending TALK_START");
        AudioManager::getInstance().startMicrophone();
        BleManager::getInstance().sendEvent("TALK_START", "{\"action\":\"listen\"}");
    });

    ButtonManager::getInstance().setOnReleaseCallback([]() {
        Serial.println("[BUTTON] <<< RELEASE -> Sending TALK_STOP");
        AudioManager::getInstance().stopMicrophone();
        BleManager::getInstance().sendEvent("TALK_STOP", "{\"action\":\"stop_listen\"}");
    });

    ButtonManager::getInstance().setOnPressCallback([]() {
        Serial.println("[BUTTON] CLICK -> Sending BUTTON_PRESSED (short_press)");
        BleManager::getInstance().sendEvent("BUTTON_PRESSED", "{\"type\":\"short_press\"}");
    });

    ButtonManager::getInstance().setOnLongPressCallback([]() {
        Serial.println("[BUTTON] HOLD -> Sending BUTTON_LONG_PRESSED (long_press)");
        BleManager::getInstance().sendEvent("BUTTON_LONG_PRESSED", "{\"type\":\"long_press\"}");
    });

    // Setup BLE command callback
    BleManager::getInstance().setCommandCallback([this](const String& cmd) {
        Serial.printf("[BLE] Incoming Command: %s\n", cmd.c_str());
        this->handleIncomingCommand(cmd);
    });
}

void DeviceManager::handleIncomingCommand(const String& cmdJson) {
    if (cmdJson.indexOf("START_LISTENING") >= 0) {
        Serial.println("[AUDIO] Command: START_LISTENING");
        AudioManager::getInstance().startMicrophone();
    } else if (cmdJson.indexOf("STOP_LISTENING") >= 0) {
        Serial.println("[AUDIO] Command: STOP_LISTENING");
        AudioManager::getInstance().stopMicrophone();
    } else if (cmdJson.indexOf("MIC_TEST") >= 0 || cmdJson.indexOf("DIAGNOSE_MIC") >= 0) {
        Serial.println("[AUDIO] Command: Run Microphone Diagnostic");
        AudioManager::getInstance().runMicrophoneDiagnostic(3000);
    } else if (cmdJson.indexOf("CAPTURE_IMAGE") >= 0) {
        Serial.println("[CAMERA] Command: CAPTURE_IMAGE");
        uint8_t* buf = nullptr;
        size_t len = 0;
        if (CameraManager::getInstance().captureImage(&buf, &len)) {
            BleManager::getInstance().sendEvent("CAMERA_READY", "{\"status\":\"captured\"}");
            CameraManager::getInstance().releaseBuffer();
        }
    } else if (cmdJson.indexOf("STATUS_REQUEST") >= 0) {
        uint8_t batt = BatteryManager::getInstance().getBatteryPercentage();
        Serial.printf("[BATTERY] Status Request -> Battery: %d%%\n", batt);
        BleManager::getInstance().updateBattery(batt);
        BleManager::getInstance().sendEvent("BATTERY_CHANGED", "{\"battery\":" + String(batt) + "}");
    }
}

void DeviceManager::update() {
    ButtonManager::getInstance().update();
    AudioManager::getInstance().update();

    // Periodic battery report every 30 seconds
    if (millis() - _lastBatteryReportTime > 30000) {
        _lastBatteryReportTime = millis();
        uint8_t batt = BatteryManager::getInstance().getBatteryPercentage();
        Serial.printf("[TELEMETRY] Periodic Battery Telemetry: %d%%\n", batt);
        BleManager::getInstance().updateBattery(batt);
    }
}
