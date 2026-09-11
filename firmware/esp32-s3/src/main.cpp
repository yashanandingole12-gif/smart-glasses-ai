#include <Arduino.h>
#include "device_manager.h"
#include <esp_system.h>
#include <esp_chip_info.h>
#include <mbedtls/base64.h>

void setup() {
    Serial.begin(115200);
    delay(500);
    
    Serial.println();
    Serial.println("==================================================");
    Serial.println("  LARA Smart Glasses AI Assistant (ESP32-S3)");
    Serial.println("  Firmware: v0.1.0 | Target: Seeed XIAO ESP32-S3");
    Serial.println("==================================================");

    esp_chip_info_t chip_info;
    esp_chip_info(&chip_info);
    Serial.printf("[SYSTEM] Chip: ESP32-S3 (Cores: %d, Rev: %d)\n", chip_info.cores, chip_info.revision);
    Serial.printf("[SYSTEM] Flash: %d MB | Free Heap: %d KB\n", ESP.getFlashChipSize() / (1024 * 1024), ESP.getFreeHeap() / 1024);
    Serial.printf("[SYSTEM] Reset Reason: %d | CPU Freq: %d MHz\n", esp_reset_reason(), getCpuFrequencyMhz());

    DeviceManager::getInstance().init();

    Serial.println("[SYSTEM] Device Initialization Complete. Ready.");
    Serial.println("==================================================");
}

static unsigned long lastHeartbeat = 0;
static bool liveMicStreaming = false;
static unsigned long lastMicStream = 0;

void loop() {
    DeviceManager::getInstance().update();

    if (millis() - lastHeartbeat >= 2000) {
        lastHeartbeat = millis();
        Serial.printf("[HEARTBEAT] Uptime: %lu ms | Free Heap: %d KB | BLE: %s | Camera: %s\n", 
                      millis(), 
                      ESP.getFreeHeap() / 1024,
                      BleManager::getInstance().isClientConnected() ? "CONNECTED" : "ADVERTISING (SmartGlasses-S3)",
                      CameraManager::getInstance().isAvailable() ? "READY" : "NOT_ATTACHED");
    }

    if (liveMicStreaming && (millis() - lastMicStream >= 100)) {
        lastMicStream = millis();
        float rms = AudioManager::getInstance().getAudioLevelRMS();
        bool isSpeech = (rms > 140.0f);
        Serial.printf("[MIC_STREAM] {\"rms\":%.1f,\"peak\":%.0f,\"speech\":%s,\"clipping\":false,\"rate\":16000,\"channels\":1}\n",
                      rms, rms * 1.8f, isSpeech ? "true" : "false");
    }

    if (Serial.available()) {
        String input = Serial.readStringUntil('\n');
        input.trim();
        if (input == "STATUS" || input == "PING") {
            Serial.printf("[DIAGNOSTIC] Board: Seeed XIAO ESP32-S3 | Free Heap: %d KB | Camera: %s | Mic: %s | CPU: %d MHz\n", 
                          ESP.getFreeHeap() / 1024, 
                          CameraManager::getInstance().isAvailable() ? "READY" : "NOT_ATTACHED",
                          AudioManager::getInstance().isInitialized() ? "READY" : "OFFLINE",
                          getCpuFrequencyMhz());
        } else if (input == "MIC_TEST" || input == "DIAGNOSE_MIC" || input == "MIC") {
            AudioManager::getInstance().runMicrophoneDiagnostic(3500);
        } else if (input == "MIC_SAMPLE") {
            float rms = AudioManager::getInstance().getAudioLevelRMS();
            bool isSpeech = (rms > 140.0f);
            Serial.printf("[MIC_SAMPLE_JSON] {\"rms\":%.1f,\"peak\":%.0f,\"speech\":%s,\"clipping\":false,\"sample_rate\":16000,\"channels\":1}\n",
                          rms, rms * 1.8f, isSpeech ? "true" : "false");
        } else if (input == "START_MIC_STREAM") {
            liveMicStreaming = true;
            Serial.println("[STREAM] Live Microphone Telemetry Stream STARTED");
        } else if (input == "STOP_MIC_STREAM") {
            liveMicStreaming = false;
            Serial.println("[STREAM] Live Microphone Telemetry Stream STOPPED");
        } else if (input == "CAPTURE_FRAME" || input == "CAMERA") {
            uint8_t* buf = nullptr;
            size_t len = 0;
            if (CameraManager::getInstance().captureImage(&buf, &len) && len > 0) {
                Serial.printf("[CAMERA_FRAME_START:%u]\n", len);
                size_t b64Max = (len * 4 / 3) + 128;
                unsigned char* b64buf = (unsigned char*)malloc(b64Max);
                if (b64buf) {
                    size_t b64len = 0;
                    mbedtls_base64_encode(b64buf, b64Max, &b64len, buf, len);
                    b64buf[b64len] = '\0';
                    Serial.println((char*)b64buf);
                    free(b64buf);
                }
                Serial.println("[CAMERA_FRAME_END]");
                CameraManager::getInstance().releaseBuffer();
            } else {
                Serial.println("[CAMERA] ERROR: Camera hardware frame capture failed or not attached.");
            }
        }
    }
    delay(5);
}
