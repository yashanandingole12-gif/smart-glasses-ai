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
    Serial.printf("[POWER] Wakeup Source: Physical Button (Pin D4 / GPIO %d, Active LOW)\n", PIN_BUTTON_PTT);
    Serial.println("==================================================");
    Serial.flush();

    // 1. Send BLE Disconnect notification if connected
    if (BleManager::getInstance().isClientConnected()) {
        BleManager::getInstance().sendEvent("DEVICE_SLEEPING", "{\"reason\":\"" + String(reason) + "\"}");
        delay(100);
    }

    // 2. Play power down chime
    AudioManager::getInstance().playSound(SoundEffect::SOUND_ERROR);

    // 3. Stop audio & camera peripherals to eliminate leakage current
    AudioManager::getInstance().stopMicrophone();

    // 4. Ensure yellow status LED is off
    pinMode(PIN_LED_STATUS, OUTPUT);
    digitalWrite(PIN_LED_STATUS, HIGH);

    // 5. Configure GPIO 5 (PTT button on D4) as external wakeup source
    esp_sleep_enable_ext0_wakeup((gpio_num_t)PIN_BUTTON_PTT, 0);

    // 6. Enter Deep Sleep
    esp_deep_sleep_start();
}

void DeviceManager::init() {
    Serial.println("[DEVICE] Initializing Subsystems...");
    _lastActivityTime = millis();

    // 0. Ensure yellow user LED (GPIO 21) is explicitly set HIGH (Active LOW -> LED OFF)
    pinMode(PIN_LED_STATUS, OUTPUT);
    digitalWrite(PIN_LED_STATUS, HIGH);

    // 1. Push-To-Talk Button on Pin D4 (GPIO 5)
    ButtonManager::getInstance().init(PIN_BUTTON_PTT);
    Serial.printf("[DEVICE] Push-To-Talk Button Initialized on Pin D4 (GPIO %d)\n", PIN_BUTTON_PTT);

    // 2. Battery ADC
    BatteryManager::getInstance().init(PIN_BATTERY_ADC);
    uint8_t initialBatt = BatteryManager::getInstance().getBatteryPercentage();
    Serial.printf("[DEVICE] Battery ADC Initialized on GPIO %d (Initial: %d%%)\n", PIN_BATTERY_ADC, initialBatt);

    // 3. Audio Subsystem (INMP441 I2S Mic + MAX98357A I2S Speaker)
    AudioManager::getInstance().init();
    Serial.println("[DEVICE] Audio Manager Initialized (INMP441 Mic & MAX98357A Speaker ready)");

    // 4. Camera Subsystem (Optional / On Hold in Mic-Only Voice Mode)
    if (CameraManager::getInstance().init()) {
        Serial.println("[DEVICE] Camera Manager Initialized");
    }

    // 5. BLE Stack
    BleManager::getInstance().init("SmartGlasses-S3");
    Serial.println("[DEVICE] BLE Manager Initialized. Advertising as 'SmartGlasses-S3'");

    // 6. WiFi Subsystem
    WiFiManager::getInstance().init();

    // 7. Mini OLED Display Subsystem
    OledManager::getInstance().init();
    Serial.println("[DEVICE] OLED Display Subsystem Initialized");

    // Wire up incoming BLE Audio Stream Chunks to Speaker DAC
    BleManager::getInstance().setAudioRxCallback([this](const uint8_t* data, size_t len) {
        this->resetActivity();
        AudioManager::getInstance().streamPcmChunk(data, len);
    });

    // Setup button callbacks for Push-to-Talk and Actions
    ButtonManager::getInstance().setOnPressStartCallback([this]() {
        this->resetActivity();
        Serial.println("[PTT BUTTON] >>> PRESSED (D4=LOW) -> Starting Recording & Sending TALK_START to Phone");
        OledManager::getInstance().showListening();
        AudioManager::getInstance().playSound(SoundEffect::SOUND_PTT_START);
        AudioManager::getInstance().startMicrophone();
        BleManager::getInstance().sendEvent("TALK_START");
    });

    ButtonManager::getInstance().setOnReleaseCallback([this]() {
        this->resetActivity();
        Serial.println("[PTT BUTTON] <<< RELEASED (D4=HIGH) -> Stopping Recording & Sending TALK_STOP to Phone");
        OledManager::getInstance().showThinking();
        AudioManager::getInstance().stopMicrophone();
        AudioManager::getInstance().playSound(SoundEffect::SOUND_PTT_STOP);
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
        OledManager::getInstance().showStatus("EVA AI", "Wake Triggered", "Listening...");
        AudioManager::getInstance().playSound(SoundEffect::SOUND_WAKE);
        BleManager::getInstance().sendEvent("BUTTON_LONG_PRESSED");
    });

    // Setup BLE command callback
    BleManager::getInstance().setCommandCallback([this](const String& cmd) {
        this->resetActivity();
        Serial.printf("[BLE] Incoming Command: %s\n", cmd.c_str());
        this->handleIncomingCommand(cmd);
    });

    // Play startup chime on speaker
    AudioManager::getInstance().playSound(SoundEffect::SOUND_SUCCESS);
}

void DeviceManager::handleIncomingCommand(const String& cmdJson) {
    if (cmdJson.startsWith("TEXT_OLED:")) {
        String msg = cmdJson.substring(10);
        Serial.println();
        Serial.println("==================================================");
        Serial.println("  [OLED DISPLAY]");
        Serial.println("  EVA");
        Serial.println("  BLE: OK");
        Serial.println();
        Serial.println("  RX:");
        Serial.printf("  %s\n", msg.c_str());
        Serial.println("==================================================");
        Serial.flush();
        OledManager::getInstance().showAiResponse("EVA", msg);
        AudioManager::getInstance().playSound(SoundEffect::SOUND_SUCCESS);
        return;
    }

    if (cmdJson.indexOf("START_LISTENING") >= 0 || cmdJson.indexOf("TALK_START") >= 0) {
        Serial.println("[AUDIO] Command: START_LISTENING");
        OledManager::getInstance().showListening();
        AudioManager::getInstance().playSound(SoundEffect::SOUND_WAKE);
        AudioManager::getInstance().startMicrophone();
    } else if (cmdJson.indexOf("STOP_LISTENING") >= 0 || cmdJson.indexOf("TALK_STOP") >= 0) {
        Serial.println("[AUDIO] Command: STOP_LISTENING");
        OledManager::getInstance().showThinking();
        AudioManager::getInstance().stopMicrophone();
        AudioManager::getInstance().playSound(SoundEffect::SOUND_PTT_STOP);
    } else if (cmdJson.indexOf("PLAY_MESSAGE_ALERT") >= 0 || cmdJson.indexOf("MESSAGE_NOTIFICATION") >= 0 || cmdJson.indexOf("NOTIFY") >= 0) {
        Serial.println("[SPEAKER] Command: Play Incoming Message Notification Chime");
        OledManager::getInstance().showNotification("New Alert", "Incoming Message");
        AudioManager::getInstance().playSound(SoundEffect::SOUND_MESSAGE_ALERT);
    } else if (cmdJson.indexOf("PLAY_AI_RESPONSE") >= 0 || cmdJson.indexOf("AI_RESPONSE") >= 0 || cmdJson.indexOf("SPEAK_ALERT") >= 0) {
        Serial.println("[SPEAKER] Command: Play AI Response Ready Tone");
        AudioManager::getInstance().playSound(SoundEffect::SOUND_AI_RESPONSE);
    } else if (cmdJson.indexOf("CALL_INCOMING") >= 0 || cmdJson.indexOf("RING") >= 0) {
        Serial.println("[SPEAKER] Command: Play Incoming Call Ringtone");
        OledManager::getInstance().showCalling("Incoming Call");
        AudioManager::getInstance().playSound(SoundEffect::SOUND_CALL_INCOMING);
    } else if (cmdJson.indexOf("SET_VOLUME") >= 0) {
        int volIdx = cmdJson.indexOf("volume");
        if (volIdx >= 0) {
            int colonIdx = cmdJson.indexOf(':', volIdx);
            if (colonIdx >= 0) {
                int volVal = cmdJson.substring(colonIdx + 1).toInt();
                AudioManager::getInstance().setVolume((uint8_t)volVal);
                AudioManager::getInstance().playSound(SoundEffect::SOUND_SUCCESS);
            }
        }
    } else if (cmdJson.indexOf("PLAY_TONE") >= 0) {
        uint16_t freq = 880;
        uint32_t dur = 300;
        int freqIdx = cmdJson.indexOf("freq");
        if (freqIdx >= 0) {
            int colon = cmdJson.indexOf(':', freqIdx);
            if (colon >= 0) freq = cmdJson.substring(colon + 1).toInt();
        }
        int durIdx = cmdJson.indexOf("dur");
        if (durIdx >= 0) {
            int colon = cmdJson.indexOf(':', durIdx);
            if (colon >= 0) dur = cmdJson.substring(colon + 1).toInt();
        }
        AudioManager::getInstance().playTone(freq, dur);
    } else if (cmdJson.indexOf("SPEAKER_TEST") >= 0 || cmdJson.indexOf("DIAGNOSE_SPK") >= 0) {
        Serial.println("[SPEAKER] Command: Run Speaker Diagnostic");
        AudioManager::getInstance().runSpeakerDiagnostic();
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
    } else if (cmdJson.indexOf("PROVISION_WIFI") >= 0 || cmdJson.indexOf("WIFI_CONNECT") >= 0) {
        String ssid = "";
        String pass = "";
        int ssidKey = cmdJson.indexOf("\"ssid\"");
        if (ssidKey >= 0) {
            int colon = cmdJson.indexOf(':', ssidKey);
            int q1 = cmdJson.indexOf('\"', colon);
            int q2 = cmdJson.indexOf('\"', q1 + 1);
            if (q1 >= 0 && q2 > q1) ssid = cmdJson.substring(q1 + 1, q2);
        }
        int passKey = cmdJson.indexOf("\"password\"");
        if (passKey >= 0) {
            int colon = cmdJson.indexOf(':', passKey);
            int q1 = cmdJson.indexOf('\"', colon);
            int q2 = cmdJson.indexOf('\"', q1 + 1);
            if (q1 >= 0 && q2 > q1) pass = cmdJson.substring(q1 + 1, q2);
        }
        Serial.printf("[WIFI] Received WiFi provisioning command for SSID: '%s'\n", ssid.c_str());
        WiFiManager::getInstance().connectToNetwork(ssid, pass);
    } else if (cmdJson.indexOf("SLEEP") >= 0 || cmdJson.indexOf("SHUTDOWN") >= 0) {
        enterDeepSleep("App Command Sleep Request");
    }
}

void DeviceManager::update() {
    ButtonManager::getInstance().update();
    AudioManager::getInstance().update();
    WiFiManager::getInstance().update();

    bool connected = BleManager::getInstance().isClientConnected();
    if (connected != _wasConnected) {
        _wasConnected = connected;
        if (connected) {
            Serial.println("[DEVICE] Phone connected -> Playing Connected Chime");
            OledManager::getInstance().showWelcomeScreen(BatteryManager::getInstance().getBatteryPercentage());
            AudioManager::getInstance().playSound(SoundEffect::SOUND_DEVICE_CONNECTED);
        } else {
            Serial.println("[DEVICE] Phone disconnected -> Playing Disconnected Chime");
            OledManager::getInstance().showWelcomeScreen(BatteryManager::getInstance().getBatteryPercentage());
            AudioManager::getInstance().playSound(SoundEffect::SOUND_DEVICE_DISCONNECTED);
        }
    }

    // While BLE is connected to phone, keep device active and responsive
    if (connected) {
        _lastActivityTime = millis();
    }

    // 1. Check for inactivity timeout (25 minutes without interactions when disconnected)
    if (_lastActivityTime > 0 && (millis() - _lastActivityTime >= INACTIVITY_SLEEP_TIMEOUT_MS)) {
        if (!connected) {
            enterDeepSleep("25-minute Disconnected Inactivity Timeout");
        }
    }

    // 2. Periodic battery report every 30 seconds when connected
    if (millis() - _lastBatteryReportTime > 30000) {
        _lastBatteryReportTime = millis();
        if (connected) {
            uint8_t batt = BatteryManager::getInstance().getBatteryPercentage();
            Serial.printf("[TELEMETRY] Periodic Battery Telemetry: %d%%\n", batt);
            BleManager::getInstance().updateBattery(batt);
        }
    }
}
