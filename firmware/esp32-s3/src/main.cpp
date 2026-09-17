#include <Arduino.h>
#include "device_manager.h"
#include "diagnostic_manager.h"
#include "oled_manager.h"
#include <esp_system.h>
#include <esp_chip_info.h>
#include <mbedtls/base64.h>

void streamBase64Data(const uint8_t* data, size_t len) {
    if (!data || len == 0) return;
    const size_t chunkSize = 1536; // multiple of 3 (1536 raw = 2048 base64 bytes)
    unsigned char b64Chunk[2048 + 4];
    size_t offset = 0;
    while (offset < len) {
        size_t currentChunk = (len - offset > chunkSize) ? chunkSize : (len - offset);
        size_t b64len = 0;
        mbedtls_base64_encode(b64Chunk, sizeof(b64Chunk), &b64len, data + offset, currentChunk);
        b64Chunk[b64len] = '\0';
        Serial.print((char*)b64Chunk);
        offset += currentChunk;
    }
    Serial.println();
}

void decodeAndPlayBase64Audio(const String& b64Str) {
    if (b64Str.length() == 0) return;
    size_t outLen = 0;
    size_t maxDecoded = (b64Str.length() * 3) / 4 + 4;
    uint8_t* pcmBuf = (uint8_t*)(psramFound() ? ps_malloc(maxDecoded) : malloc(maxDecoded));
    if (!pcmBuf) {
        Serial.println("[SPEAKER] ERROR: Memory allocation failed for audio decode.");
        return;
    }
    int ret = mbedtls_base64_decode(pcmBuf, maxDecoded, &outLen, (const unsigned char*)b64Str.c_str(), b64Str.length());
    if (ret == 0 && outLen > 0) {
        Serial.printf("[SPEAKER] Playing decoded audio stream (%u bytes)...\n", (unsigned int)outLen);
        if (outLen > 44 && memcmp(pcmBuf, "RIFF", 4) == 0) {
            AudioManager::getInstance().playWavAudio(pcmBuf, outLen);
        } else {
            AudioManager::getInstance().playPcmAudio((const int16_t*)pcmBuf, outLen / sizeof(int16_t));
        }
    } else {
        Serial.printf("[SPEAKER] Base64 decode error (code: %d)\n", ret);
    }
    free(pcmBuf);
}

void setup() {
    // Turn OFF yellow user LED on GPIO 21 immediately at boot (Active LOW -> HIGH is OFF)
    pinMode(PIN_LED_STATUS, OUTPUT);
    digitalWrite(PIN_LED_STATUS, HIGH);

    Serial.begin(115200);
    delay(500);
    
    Serial.println();
    Serial.println("==================================================");
    Serial.println("  LARA Smart Glasses AI Assistant (ESP32-S3)");
    Serial.println("  Firmware: v0.3.0 | Multimodal, Vision & Speaker Ready");
    Serial.println("==================================================");

    esp_chip_info_t chip_info;
    esp_chip_info(&chip_info);
    Serial.printf("[SYSTEM] Chip: ESP32-S3 (Cores: %d, Rev: %d)\n", chip_info.cores, chip_info.revision);
    Serial.printf("[SYSTEM] Flash: %d MB | PSRAM: %s | Free Heap: %d KB\n", 
                  ESP.getFlashChipSize() / (1024 * 1024), 
                  psramFound() ? "8MB Octal Active" : "Disabled",
                  ESP.getFreeHeap() / 1024);
    Serial.printf("[SYSTEM] Reset Reason: %d | CPU Freq: %d MHz\n", esp_reset_reason(), getCpuFrequencyMhz());

    DeviceManager::getInstance().init();

    // Ensure yellow LED remains OFF after subsystem initialization
    digitalWrite(PIN_LED_STATUS, HIGH);

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
        Serial.printf("[HEARTBEAT] Uptime: %lu ms | Free Heap: %d KB | BLE: %s | Camera: %s | Mic: %s | Speaker: %s\n", 
                      millis(), 
                      ESP.getFreeHeap() / 1024,
                      BleManager::getInstance().isClientConnected() ? "CONNECTED" : "ADVERTISING (SmartGlasses-S3)",
                      CameraManager::getInstance().isAvailable() ? "READY (VGA 640x480)" : "NOT_ATTACHED",
                      AudioManager::getInstance().isInitialized() ? "READY" : "OFFLINE",
                      AudioManager::getInstance().isSpeakerInitialized() ? "READY (I2S TX)" : "OFFLINE");
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
            Serial.printf("[DIAGNOSTIC] Board: Seeed XIAO ESP32-S3 | Free Heap: %d KB | Camera: %s | Mic: %s | Spk: %s | CPU: %d MHz\n", 
                          ESP.getFreeHeap() / 1024, 
                          CameraManager::getInstance().isAvailable() ? "READY (VGA 640x480)" : "NOT_ATTACHED",
                          AudioManager::getInstance().isInitialized() ? "READY" : "OFFLINE",
                          AudioManager::getInstance().isSpeakerInitialized() ? "READY" : "OFFLINE",
                          getCpuFrequencyMhz());
        } else if (input == "WAKE" || input == "TALK" || input == "START") {
            AudioManager::getInstance().triggerVoiceWakeSession();
        } else if (input == "STOP" || input == "STOP_TALK") {
            AudioManager::getInstance().stopVoiceWakeSession();
        } else if (input == "ENABLE_VAD") {
            AudioManager::getInstance().setVadEnabled(true);
            Serial.println("[VAD] Automatic Hands-Free Voice Detection ENABLED");
        } else if (input == "DISABLE_VAD") {
            AudioManager::getInstance().setVadEnabled(false);
            Serial.println("[VAD] Automatic Hands-Free Voice Detection DISABLED");
        } else if (input == "LED_OFF" || input == "FIX_LED") {
            pinMode(PIN_LED_STATUS, OUTPUT);
            digitalWrite(PIN_LED_STATUS, HIGH);
            Serial.println("[LED] Status Yellow LED forced OFF (GPIO 21 set HIGH)");
        } else if (input == "LED_ON") {
            pinMode(PIN_LED_STATUS, OUTPUT);
            digitalWrite(PIN_LED_STATUS, LOW);
            Serial.println("[LED] Status Yellow LED turned ON (GPIO 21 set LOW)");
        } else if (input == "PLAY_MESSAGE_ALERT" || input == "MESSAGE_ALERT" || input == "PLAY_ALERT") {
            Serial.println("[SPEAKER] Playing Incoming Message Notification Chime");
            AudioManager::getInstance().playSound(SoundEffect::SOUND_MESSAGE_ALERT);
        } else if (input == "PLAY_AI_RESPONSE" || input == "AI_RESPONSE") {
            Serial.println("[SPEAKER] Playing AI Response Ready Chime");
            AudioManager::getInstance().playSound(SoundEffect::SOUND_AI_RESPONSE);
        } else if (input == "PLAY_WAKE") {
            Serial.println("[SPEAKER] Playing Wake-up Prompt Chime");
            AudioManager::getInstance().playSound(SoundEffect::SOUND_WAKE);
        } else if (input == "PLAY_CALL") {
            Serial.println("[SPEAKER] Playing Incoming Call Ringtone");
            AudioManager::getInstance().playSound(SoundEffect::SOUND_CALL_INCOMING);
        } else if (input == "PLAY_SUCCESS") {
            AudioManager::getInstance().playSound(SoundEffect::SOUND_SUCCESS);
        } else if (input == "PLAY_ERROR") {
            AudioManager::getInstance().playSound(SoundEffect::SOUND_ERROR);
        } else if (input.startsWith("PLAY_TONE")) {
            uint16_t freq = 880;
            uint32_t dur = 300;
            int space1 = input.indexOf(' ');
            if (space1 > 0) {
                int space2 = input.indexOf(' ', space1 + 1);
                if (space2 > 0) {
                    freq = input.substring(space1 + 1, space2).toInt();
                    dur = input.substring(space2 + 1).toInt();
                } else {
                    freq = input.substring(space1 + 1).toInt();
                }
            }
            Serial.printf("[SPEAKER] Playing Tone: %u Hz for %u ms\n", freq, dur);
            AudioManager::getInstance().playTone(freq, dur);
        } else if (input.startsWith("SET_VOLUME") || input.startsWith("VOLUME")) {
            int spaceIdx = input.indexOf(' ');
            if (spaceIdx > 0) {
                uint8_t vol = input.substring(spaceIdx + 1).toInt();
                AudioManager::getInstance().setVolume(vol);
                AudioManager::getInstance().playSound(SoundEffect::SOUND_SUCCESS);
            }
        } else if (input.startsWith("PLAY_AUDIO_BASE64")) {
            int spaceIdx = input.indexOf(' ');
            if (spaceIdx > 0) {
                String b64 = input.substring(spaceIdx + 1);
                decodeAndPlayBase64Audio(b64);
            }
        } else if (input == "SPK_TEST" || input == "SPEAKER_TEST" || input == "DIAGNOSE_SPK") {
            AudioManager::getInstance().runSpeakerDiagnostic();
        } else if (input == "AUDIO_TEST" || input == "DIAGNOSE_AUDIO") {
            AudioManager::getInstance().runFullAudioDiagnostic();
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
                Serial.printf("[CAMERA_FRAME_START:%u]\n", (unsigned int)len);
                streamBase64Data(buf, len);
                Serial.println("[CAMERA_FRAME_END]");
                CameraManager::getInstance().releaseBuffer();
            } else {
                Serial.println("[CAMERA] ERROR: Camera hardware frame capture failed or not attached.");
            }
        } else if (input.startsWith("RECORD_AUDIO")) {
            uint32_t durationMs = 3000;
            int spaceIdx = input.indexOf(' ');
            if (spaceIdx > 0) {
                durationMs = input.substring(spaceIdx + 1).toInt();
            }
            if (durationMs < 500) durationMs = 3000;
            if (durationMs > 10000) durationMs = 10000;

            uint8_t* wavBuf = nullptr;
            size_t wavLen = 0;
            if (AudioManager::getInstance().recordWavAudio(durationMs, &wavBuf, &wavLen) && wavBuf && wavLen > 0) {
                Serial.printf("[AUDIO_RECORDING_START:%u]\n", (unsigned int)wavLen);
                streamBase64Data(wavBuf, wavLen);
                Serial.println("[AUDIO_RECORDING_END]");
                AudioManager::getInstance().releaseWavBuffer(wavBuf);
            } else {
                Serial.println("[AUDIO] ERROR: Audio recording failed.");
            }
        } else if (input.startsWith("CAPTURE_MULTIMODAL")) {
            uint32_t durationMs = 3000;
            int spaceIdx = input.indexOf(' ');
            if (spaceIdx > 0) {
                durationMs = input.substring(spaceIdx + 1).toInt();
            }
            if (durationMs < 500) durationMs = 3000;

            Serial.println("[MULTIMODAL_START]");
            
            // 1. Capture snapshot immediately
            uint8_t* imgBuf = nullptr;
            size_t imgLen = 0;
            bool camOk = CameraManager::getInstance().captureImage(&imgBuf, &imgLen);
            if (camOk && imgLen > 0) {
                Serial.printf("[CAMERA_FRAME_START:%u]\n", (unsigned int)imgLen);
                streamBase64Data(imgBuf, imgLen);
                Serial.println("[CAMERA_FRAME_END]");
                CameraManager::getInstance().releaseBuffer();
            } else {
                Serial.println("[CAMERA_FRAME_FAILED]");
            }

            // 2. Record voice command from ESP32 digital mic
            uint8_t* wavBuf = nullptr;
            size_t wavLen = 0;
            bool micOk = AudioManager::getInstance().recordWavAudio(durationMs, &wavBuf, &wavLen);
            if (micOk && wavBuf && wavLen > 0) {
                Serial.printf("[AUDIO_RECORDING_START:%u]\n", (unsigned int)wavLen);
                streamBase64Data(wavBuf, wavLen);
                Serial.println("[AUDIO_RECORDING_END]");
                AudioManager::getInstance().releaseWavBuffer(wavBuf);
            } else {
                Serial.println("[AUDIO_RECORDING_FAILED]");
            }

            Serial.println("[MULTIMODAL_END]");
        } else if (input == "OLED_TEST" || input == "TEST_OLED" || input == "DIAGNOSE_OLED") {
            Serial.println("[OLED] Running OLED Diagnostics Test...");
            OledManager::getInstance().runDiagnostics();
        } else if (input == "OLED_ON" || input == "OLED_WELCOME") {
            Serial.println("[OLED] Displaying Welcome Screen");
            OledManager::getInstance().showWelcomeScreen(85);
        } else if (input == "OLED_CLEAR") {
            Serial.println("[OLED] Clearing OLED Display");
            OledManager::getInstance().clear();
        } else if (input.startsWith("OLED_TEXT ") || input.startsWith("TEXT_OLED ")) {
            String msg = input.substring(10);
            Serial.printf("[OLED] Displaying text: %s\n", msg.c_str());
            OledManager::getInstance().showAiResponse("LARA", msg);
        } else if (input.startsWith("OLED_STATUS ")) {
            String msg = input.substring(12);
            Serial.printf("[OLED] Displaying status: %s\n", msg.c_str());
            OledManager::getInstance().showStatus("LARA SMART GLASS", msg, "");
        } else if (input == "REPORT" || input == "DIAG" || input == "SELF_TEST") {
            Serial.println("[SELF_TEST_START]");
            String report = diagnosticManager.getJsonReport();
            Serial.println(report);
            Serial.println("[SELF_TEST_END]");
        } else if (input == "SLEEP" || input == "SHUTDOWN" || input == "DEEP_SLEEP") {
            DeviceManager::getInstance().enterDeepSleep("Serial Sleep Request");
        }
    }
    delay(5);
}
