#include "device_manager.h"
#include "diagnostic_manager.h"
#include "oled_manager.h"
#include <Arduino.h>
#include <esp_chip_info.h>
#include <esp_system.h>
#include <mbedtls/base64.h>

void streamBase64Data(const uint8_t *data, size_t len) {
  if (!data || len == 0)
    return;
  const size_t chunkSize = 1536; // multiple of 3 (1536 raw = 2048 base64 bytes)
  unsigned char b64Chunk[2048 + 4];
  size_t offset = 0;
  while (offset < len) {
    size_t currentChunk =
        (len - offset > chunkSize) ? chunkSize : (len - offset);
    size_t b64len = 0;
    mbedtls_base64_encode(b64Chunk, sizeof(b64Chunk), &b64len, data + offset,
                          currentChunk);
    b64Chunk[b64len] = '\0';
    Serial.print((char *)b64Chunk);
    offset += currentChunk;
  }
  Serial.println();
}

void decodeAndPlayBase64Audio(const String &b64Str) {
  if (b64Str.length() == 0)
    return;
  size_t outLen = 0;
  size_t maxDecoded = (b64Str.length() * 3) / 4 + 4;
  uint8_t *pcmBuf =
      (uint8_t *)(psramFound() ? ps_malloc(maxDecoded) : malloc(maxDecoded));
  if (!pcmBuf) {
    Serial.println("[SPEAKER] ERROR: Memory allocation failed for audio decode.");
    return;
  }
  int ret = mbedtls_base64_decode(pcmBuf, maxDecoded, &outLen,
                                  (const unsigned char *)b64Str.c_str(),
                                  b64Str.length());
  if (ret == 0 && outLen > 0) {
    Serial.printf("[SPEAKER] Playing decoded audio stream (%u bytes)...\n",
                  (unsigned int)outLen);
    if (outLen > 44 && memcmp(pcmBuf, "RIFF", 4) == 0) {
      AudioManager::getInstance().playWavAudio(pcmBuf, outLen);
    } else {
      AudioManager::getInstance().playPcmAudio((const int16_t *)pcmBuf,
                                               outLen / sizeof(int16_t));
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
  Serial.println("  EVA Smart Glasses AI Assistant (XIAO ESP32-S3)");
  Serial.println("  Firmware: v1.0.0 | INMP441 Mic + MAX98357A Spk + PTT");
  Serial.println("==================================================");

  esp_chip_info_t chip_info;
  esp_chip_info(&chip_info);
  Serial.printf("[SYSTEM] Chip: ESP32-S3 (Cores: %d, Rev: %d)\n",
                chip_info.cores, chip_info.revision);
  Serial.printf("[SYSTEM] Flash: %d MB | PSRAM: %s | Free Heap: %d KB\n",
                ESP.getFlashChipSize() / (1024 * 1024),
                psramFound() ? "8MB Octal Active" : "Disabled",
                ESP.getFreeHeap() / 1024);
  Serial.printf("[SYSTEM] Reset Reason: %d | CPU Freq: %d MHz\n",
                esp_reset_reason(), getCpuFrequencyMhz());

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
    int btnD4 = digitalRead(PIN_BUTTON_PTT);
    float liveRms = AudioManager::getInstance().getAudioLevelRMS();

    String micStatus = "OFFLINE";
    if (AudioManager::getInstance().isInitialized()) {
      micStatus = "LIVE (INMP441 RMS: " + String((int)liveRms) + ")";
    }

    Serial.printf(
        "[HEARTBEAT] Uptime: %lu ms | Heap: %d KB | BLE: %s | Mic: %s | Speaker: %s | Button(D4=%s)\n",
        millis(), ESP.getFreeHeap() / 1024,
        BleManager::getInstance().isClientConnected()
            ? "CONNECTED"
            : "ADVERTISING (SmartGlasses-S3)",
        micStatus.c_str(),
        AudioManager::getInstance().isSpeakerInitialized() ? "READY (MAX98357A I2S)"
                                                           : "OFFLINE",
        btnD4 == LOW ? "LOW (PRESSED - RECORDING)" : "HIGH (OPEN/IDLE - Hold to Talk)");
  }

  if (liveMicStreaming && (millis() - lastMicStream >= 100)) {
    lastMicStream = millis();
    float rms = AudioManager::getInstance().getAudioLevelRMS();
    bool isSpeech = (rms > 200.0f);
    Serial.printf("[MIC_STREAM] {\"rms\":%.1f,\"peak\":%.0f,\"speech\":%s,\"rate\":16000,\"channels\":1}\n",
                  rms, rms * 1.8f, isSpeech ? "true" : "false");
  }

  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    String cmdUpper = input;
    cmdUpper.toUpperCase();

    if (cmdUpper == "STATUS" || cmdUpper == "PING") {
      int btnD4 = digitalRead(PIN_BUTTON_PTT);
      Serial.printf(
          "[DIAGNOSTIC] Board: Seeed XIAO ESP32-S3 | Mode: PTT_VOICE_AI | Free Heap: %d KB | Mic: %s | Spk: %s | D4: %s\n",
          ESP.getFreeHeap() / 1024,
          AudioManager::getInstance().isInitialized() ? "READY (INMP441 16kHz)" : "OFFLINE",
          AudioManager::getInstance().isSpeakerInitialized() ? "READY (MAX98357A)" : "OFFLINE",
          btnD4 == LOW ? "LOW (PRESSED/CLOSED)" : "HIGH (RELEASED/OPEN)");
    } else if (cmdUpper == "BUTTON" || cmdUpper == "BTN" || cmdUpper == "BTN_TEST") {
      int btnD4 = digitalRead(PIN_BUTTON_PTT);
      Serial.println();
      Serial.println("==================================================");
      Serial.println("  PUSH-TO-TALK BUTTON REAL-TIME PIN STATUS");
      Serial.printf("  - Pin D4 (GPIO %d) [External Button]: %s (Raw: %d)\n",
                    PIN_BUTTON_PTT,
                    btnD4 == LOW ? "LOW -> PRESSED / SHORTED TO GND" : "HIGH -> OPEN / IDLE",
                    btnD4);
      if (btnD4 == LOW) {
        Serial.println("  [!] NOTE: If you are NOT holding the button, your 4-pin switch");
        Serial.println("      is wired across shorted pins. Rotate it 90 degrees or use diagonal pins.");
      } else {
        Serial.println("  [OK] Pin D4 is HIGH at rest. Pressing it will pull it LOW to start talk.");
      }
      Serial.println("==================================================");
      Serial.println();
    } else if (cmdUpper == "TEST_VOICE" || cmdUpper == "VOICE_TEST" ||
               cmdUpper == "LOOPBACK" || cmdUpper == "TEST_LOOPBACK") {
      Serial.println("[TEST] Starting Voice Loopback Hardware Diagnostic...");
      AudioManager::getInstance().runVoiceLoopbackTest(3500);
    } else if (cmdUpper == "EVA START TALK" || cmdUpper == "EVA TALK" ||
               cmdUpper == "START TALK" || cmdUpper == "HEY EVA" ||
               cmdUpper == "EVA" || cmdUpper == "WAKE" || cmdUpper == "TALK" ||
               cmdUpper == "START" || cmdUpper == "START_TALK" ||
               cmdUpper == "TALK_START") {
      Serial.printf("[COMMAND] Recognized Wake / Talk Command: '%s'\n", input.c_str());
      AudioManager::getInstance().triggerVoiceWakeSession();
    } else if (cmdUpper == "STOP" || cmdUpper == "STOP_TALK" ||
               cmdUpper == "EVA STOP" || cmdUpper == "EVA STOP TALK" ||
               cmdUpper == "TALK_STOP") {
      Serial.printf("[COMMAND] Recognized Stop Command: '%s'\n", input.c_str());
      AudioManager::getInstance().stopVoiceWakeSession();
    } else if (cmdUpper == "ENABLE_VAD" || cmdUpper == "VAD ON") {
      AudioManager::getInstance().setVadEnabled(true);
      Serial.println("[VAD] Automatic Hands-Free Voice Detection ENABLED (Threshold: 300 RMS)");
    } else if (cmdUpper == "DISABLE_VAD" || cmdUpper == "VAD OFF") {
      AudioManager::getInstance().setVadEnabled(false);
      Serial.println("[VAD] Automatic Hands-Free Voice Detection DISABLED (PTT Button Active)");
    } else if (cmdUpper == "LED_OFF" || cmdUpper == "FIX_LED") {
      pinMode(PIN_LED_STATUS, OUTPUT);
      digitalWrite(PIN_LED_STATUS, HIGH);
      Serial.println("[LED] Status Yellow LED forced OFF (GPIO 21 set HIGH)");
    } else if (cmdUpper == "LED_ON") {
      pinMode(PIN_LED_STATUS, OUTPUT);
      digitalWrite(PIN_LED_STATUS, LOW);
      Serial.println("[LED] Status Yellow LED turned ON (GPIO 21 set LOW)");
    } else if (cmdUpper == "PLAY_MESSAGE_ALERT" ||
               cmdUpper == "MESSAGE_ALERT" || cmdUpper == "PLAY_ALERT") {
      Serial.println("[SPEAKER] Playing Incoming Message Notification Chime");
      AudioManager::getInstance().playSound(SoundEffect::SOUND_MESSAGE_ALERT);
    } else if (cmdUpper == "PLAY_AI_RESPONSE" || cmdUpper == "AI_RESPONSE") {
      Serial.println("[SPEAKER] Playing AI Response Ready Chime");
      AudioManager::getInstance().playSound(SoundEffect::SOUND_AI_RESPONSE);
    } else if (cmdUpper == "PLAY_WAKE") {
      Serial.println("[SPEAKER] Playing Wake-up Prompt Chime");
      AudioManager::getInstance().playSound(SoundEffect::SOUND_WAKE);
    } else if (cmdUpper == "PLAY_CALL") {
      Serial.println("[SPEAKER] Playing Incoming Call Ringtone");
      AudioManager::getInstance().playSound(SoundEffect::SOUND_CALL_INCOMING);
    } else if (cmdUpper == "PLAY_SUCCESS") {
      AudioManager::getInstance().playSound(SoundEffect::SOUND_SUCCESS);
    } else if (cmdUpper == "PLAY_ERROR") {
      AudioManager::getInstance().playSound(SoundEffect::SOUND_ERROR);
    } else if (cmdUpper.startsWith("PLAY_TONE")) {
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
    } else if (cmdUpper.startsWith("SET_VOLUME") || cmdUpper.startsWith("VOLUME")) {
      int spaceIdx = input.indexOf(' ');
      if (spaceIdx > 0) {
        uint8_t vol = input.substring(spaceIdx + 1).toInt();
        AudioManager::getInstance().setVolume(vol);
        AudioManager::getInstance().playSound(SoundEffect::SOUND_SUCCESS);
      }
    } else if (cmdUpper.startsWith("PLAY_AUDIO_BASE64")) {
      int spaceIdx = input.indexOf(' ');
      if (spaceIdx > 0) {
        String b64 = input.substring(spaceIdx + 1);
        decodeAndPlayBase64Audio(b64);
      }
    } else if (cmdUpper == "SPK_TEST" || cmdUpper == "SPEAKER_TEST" ||
               cmdUpper == "DIAGNOSE_SPK" || cmdUpper == "SPK") {
      AudioManager::getInstance().runSpeakerDiagnostic();
    } else if (cmdUpper == "AUDIO_TEST" || cmdUpper == "DIAGNOSE_AUDIO") {
      AudioManager::getInstance().runFullAudioDiagnostic();
    } else if (cmdUpper == "MIC_TEST" || cmdUpper == "DIAGNOSE_MIC" ||
               cmdUpper == "MIC") {
      AudioManager::getInstance().runMicrophoneDiagnostic(3500);
    } else if (cmdUpper == "MIC_SAMPLE") {
      float rms = AudioManager::getInstance().getAudioLevelRMS();
      bool isSpeech = (rms > 200.0f);
      Serial.printf("[MIC_SAMPLE_JSON] {\"rms\":%.1f,\"peak\":%.0f,\"speech\":%s,\"rate\":16000,\"channels\":1}\n",
                    rms, rms * 1.8f, isSpeech ? "true" : "false");
    } else if (cmdUpper == "START_MIC_STREAM") {
      liveMicStreaming = true;
      Serial.println("[STREAM] Live Microphone Telemetry Stream STARTED");
    } else if (cmdUpper == "STOP_MIC_STREAM") {
      liveMicStreaming = false;
      Serial.println("[STREAM] Live Microphone Telemetry Stream STOPPED");
    } else if (cmdUpper.startsWith("RECORD_AUDIO") || cmdUpper.startsWith("RECORD")) {
      uint32_t durationMs = 3000;
      int spaceIdx = input.indexOf(' ');
      if (spaceIdx > 0) {
        durationMs = input.substring(spaceIdx + 1).toInt();
      }
      if (durationMs < 500)
        durationMs = 3000;
      if (durationMs > 10000)
        durationMs = 10000;

      uint8_t *wavBuf = nullptr;
      size_t wavLen = 0;
      if (AudioManager::getInstance().recordWavAudio(durationMs, &wavBuf, &wavLen) &&
          wavBuf && wavLen > 0) {
        Serial.printf("[AUDIO_RECORDING_START:%u]\n", (unsigned int)wavLen);
        streamBase64Data(wavBuf, wavLen);
        Serial.println("[AUDIO_RECORDING_END]");
        AudioManager::getInstance().releaseWavBuffer(wavBuf);
      } else {
        Serial.println("[AUDIO] ERROR: Audio recording failed.");
      }
    } else if (cmdUpper == "HELP" || cmdUpper == "?") {
      Serial.println();
      Serial.println("==================================================");
      Serial.println("  AVAILABLE EVA SERIAL TEST COMMANDS");
      Serial.println("==================================================");
      Serial.println("  SPK_TEST         - Test speaker (plays 440Hz + 880Hz tones)");
      Serial.println("  MIC_TEST         - Test mic (prints live RMS & VU meter)");
      Serial.println("  PLAY_TONE <f> <d>- Play frequency (Hz) for duration (ms)");
      Serial.println("  TEST_VOICE       - Record 3.5s and playback on speaker");
      Serial.println("  RECORD_AUDIO <ms>- Record audio and stream base64 WAV");
      Serial.println("  BUTTON           - Check PTT button (D4) and BOOT button state");
      Serial.println("  STATUS           - Check board status, heap, BLE, mic, speaker");
      Serial.println("==================================================");
      Serial.println();
    } else if (input == "OLED_TEST" || input == "TEST_OLED" ||
               input == "DIAGNOSE_OLED") {
      Serial.println("[OLED] Running OLED Diagnostics Test...");
      OledManager::getInstance().runDiagnostics();
    } else if (input == "OLED_ON" || input == "OLED_WELCOME") {
      Serial.println("[OLED] Displaying Welcome Screen");
      OledManager::getInstance().showWelcomeScreen(85);
    } else if (input == "OLED_CLEAR") {
      Serial.println("[OLED] Clearing OLED Display");
      OledManager::getInstance().clear();
    } else if (input.startsWith("OLED_TEXT ") ||
               input.startsWith("TEXT_OLED ")) {
      String msg = input.substring(10);
      Serial.printf("[OLED] Displaying text: %s\n", msg.c_str());
      OledManager::getInstance().showAiResponse("EVA", msg);
    } else if (input.startsWith("OLED_STATUS ")) {
      String msg = input.substring(12);
      Serial.printf("[OLED] Displaying status: %s\n", msg.c_str());
      OledManager::getInstance().showStatus("EVA SMART GLASS", msg, "");
    } else if (input == "REPORT" || input == "DIAG" || input == "SELF_TEST") {
      Serial.println("[SELF_TEST_START]");
      String report = diagnosticManager.getJsonReport();
      Serial.println(report);
      Serial.println("[SELF_TEST_END]");
    } else if (input == "SLEEP" || input == "SHUTDOWN" ||
               input == "DEEP_SLEEP") {
      DeviceManager::getInstance().enterDeepSleep("Serial Sleep Request");
    }
  }
  delay(5);
}
