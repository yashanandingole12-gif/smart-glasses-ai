#include "device_manager.h"

DeviceManager::DeviceManager() {}

void DeviceManager::resetActivity() {
    _lastActivityTime = millis();
}

void DeviceManager::enterDeepSleep(const char* reason) {
    Serial.println();
    Serial.println("==================================================");
    Serial.printf("[POWER] Entering ESP32-S3 Deep Sleep Mode!\n");
    Serial.printf("[POWER] Reason: %s\n", reason);
    Serial.println("[POWER] Wakeup Source: Physical Button (GPIO 0 / Active LOW)");
    Serial.println("==================================================");
    Serial.flush();

    // 1. Send BLE Disconnect notification if connected
    if (BleManager::getInstance().isClientConnected()) {
        BleManager::getInstance().sendEvent("DEVICE_SLEEPING", "{\"reason\":\"" + String(reason) + "\"}");
        delay(100);
    }

    // 2. Stop audio & camera peripherals to eliminate leakage current
    AudioManager::getInstance().stopMicrophone();

    // 3. Configure GPIO 0 (PTT button) as external wakeup source
    esp_sleep_enable_ext0_wakeup((gpio_num_t)PIN_BUTTON_PTT, 0);

    // 4. Enter Deep Sleep
    esp_deep_sleep_start();
}

void DeviceManager::init() {
    Serial.println("[DEVICE] Initializing Subsystems...");
    _lastActivityTime = millis();

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
    ButtonManager::getInstance().setOnPressStartCallback([this]() {
        this->resetActivity();
        Serial.println("[BUTTON] >>> PRESS START -> Sending TALK_START");
        AudioManager::getInstance().startMicrophone();
        BleManager::getInstance().sendEvent("TALK_START");
    });

    ButtonManager::getInstance().setOnReleaseCallback([this]() {
        this->resetActivity();
        Serial.println("[BUTTON] <<< RELEASE -> Sending TALK_STOP");
        AudioManager::getInstance().stopMicrophone();
        BleManager::getInstance().sendEvent("TALK_STOP");
    });

    ButtonManager::getInstance().setOnPressCallback([this]() {
        this->resetActivity();
        Serial.println("[BUTTON] CLICK -> Sending BUTTON_PRESSED");
        BleManager::getInstance().sendEvent("BUTTON_PRESSED");
    });

    ButtonManager::getInstance().setOnLongPressCallback([this]() {
        this->resetActivity();
        Serial.println("[BUTTON] HOLD -> Sending BUTTON_LONG_PRESSED");
        BleManager::getInstance().sendEvent("BUTTON_LONG_PRESSED");
    });

    // Setup BLE command callback
    BleManager::getInstance().setCommandCallback([this](const String& cmd) {
        this->resetActivity();
        Serial.printf("[BLE] Incoming Command: %s\n", cmd.c_str());
        this->handleIncomingCommand(cmd);
    });
}

void DeviceManager::handleIncomingCommand(const String& cmdJson) {
    resetActivity();
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
    } else if (cmdJson.indexOf("SLEEP") >= 0 || cmdJson.indexOf("SHUTDOWN") >= 0) {
        enterDeepSleep("App Command Sleep Request");
    }
}

void DeviceManager::update() {
    ButtonManager::getInstance().update();
    AudioManager::getInstance().update();

    // While BLE is connected to phone, keep device active and responsive
    if (BleManager::getInstance().isClientConnected()) {
        _lastActivityTime = millis();
    }

    // 1. Check for inactivity timeout (25 minutes without interactions when disconnected)
    if (_lastActivityTime > 0 && (millis() - _lastActivityTime >= INACTIVITY_SLEEP_TIMEOUT_MS)) {
        if (!BleManager::getInstance().isClientConnected()) {
            enterDeepSleep("25-minute Disconnected Inactivity Timeout");
        }
    }

    // 2. Periodic battery report every 30 seconds when connected
    if (millis() - _lastBatteryReportTime > 30000) {
        _lastBatteryReportTime = millis();
        if (BleManager::getInstance().isClientConnected()) {
            uint8_t batt = BatteryManager::getInstance().getBatteryPercentage();
            Serial.printf("[TELEMETRY] Periodic Battery Telemetry: %d%%\n", batt);
            BleManager::getInstance().updateBattery(batt);
        }
    }
}
