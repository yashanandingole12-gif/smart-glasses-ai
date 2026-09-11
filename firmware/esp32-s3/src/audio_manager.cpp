#include "audio_manager.h"
#include <driver/i2s.h>
#include <math.h>

AudioManager::AudioManager() {}

bool AudioManager::init() {
    // 1. Configure I2S driver in PDM RX mode (XIAO ESP32-S3 Sense on-board mic)
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_PDM),
        .sample_rate = I2S_MIC_SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_RIGHT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = 512,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_PIN_NO_CHANGE,
        .ws_io_num = 42,    // PDM CLK (GPIO 42 on XIAO Sense)
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = 41   // PDM DATA (GPIO 41 on XIAO Sense)
    };

    esp_err_t err = i2s_driver_install(I2S_MIC_PORT, &i2s_config, 0, NULL);
    if (err != ESP_OK) {
        // Fallback: Standard I2S Mode for external digital mic (INMP441)
        i2s_config.mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX);
        pin_config.bck_io_num = I2S_MIC_BCLK;
        pin_config.ws_io_num = I2S_MIC_LRCLK;
        pin_config.data_in_num = I2S_MIC_DATA;
        err = i2s_driver_install(I2S_MIC_PORT, &i2s_config, 0, NULL);
    }

    if (err == ESP_OK) {
        i2s_set_pin(I2S_MIC_PORT, &pin_config);
        i2s_set_clk(I2S_MIC_PORT, I2S_MIC_SAMPLE_RATE, I2S_BITS_PER_SAMPLE_16BIT, I2S_CHANNEL_MONO);
        _initialized = true;
        Serial.println("[AUDIO] I2S/PDM Microphone Driver Active (16kHz 16-bit Mono, PDM_CLK=42, PDM_DATA=41)");
        return true;
    } else {
        Serial.printf("[AUDIO] I2S Driver Install Failed (err=0x%x)\n", err);
        _initialized = false;
        return false;
    }
}

void AudioManager::startMicrophone() {
    _isRecording = true;
    Serial.println("[AUDIO] Microphone Recording Stream Started");
}

void AudioManager::stopMicrophone() {
    _isRecording = false;
    Serial.println("[AUDIO] Microphone Recording Stream Stopped");
}

size_t AudioManager::readMicrophone(int16_t* buffer, size_t maxSamples) {
    if (!_initialized || buffer == nullptr || maxSamples == 0) return 0;
    size_t bytesRead = 0;
    esp_err_t err = i2s_read(I2S_MIC_PORT, (void*)buffer, maxSamples * sizeof(int16_t), &bytesRead, pdMS_TO_TICKS(100));
    if (err == ESP_OK) {
        return bytesRead / sizeof(int16_t);
    }
    return 0;
}

float AudioManager::getAudioLevelRMS() {
    if (!_initialized) return 0.0f;
    int16_t samples[128];
    size_t count = readMicrophone(samples, 128);
    if (count == 0) return 0.0f;

    double sumSq = 0.0;
    for (size_t i = 0; i < count; i++) {
        sumSq += (double)samples[i] * (double)samples[i];
    }
    return (float)sqrt(sumSq / (double)count);
}

void AudioManager::runMicrophoneDiagnostic(uint32_t durationMs) {
    if (!_initialized) {
        Serial.println("[MIC DIAGNOSTIC] ERROR: I2S Driver not initialized.");
        return;
    }

    Serial.println();
    Serial.println("==================================================");
    Serial.println("  🎙️ ESP32-S3 PHYSICAL MICROPHONE LIVE DIAGNOSTIC");
    Serial.printf("  Sampling Rate: %d Hz | Channels: 1 (Mono 16-bit)\n", I2S_MIC_SAMPLE_RATE);
    Serial.println("  Speak into the XIAO ESP32-S3 microphone now...");
    Serial.println("==================================================");

    uint32_t startTime = millis();
    int16_t buffer[256];
    float maxRMS = 0.0f;
    int16_t absolutePeak = 0;
    uint32_t voiceFrames = 0;
    uint32_t totalFrames = 0;

    while (millis() - startTime < durationMs) {
        size_t samplesRead = readMicrophone(buffer, 256);
        if (samplesRead > 0) {
            totalFrames++;
            double sumSq = 0.0;
            int16_t framePeak = 0;

            for (size_t i = 0; i < samplesRead; i++) {
                int16_t val = buffer[i];
                if (abs(val) > framePeak) framePeak = abs(val);
                sumSq += (double)val * (double)val;
            }

            float rms = (float)sqrt(sumSq / (double)samplesRead);
            if (rms > maxRMS) maxRMS = rms;
            if (framePeak > absolutePeak) absolutePeak = framePeak;

            // Visual VU Meter bar (16 levels)
            int bars = (int)(rms / 200.0f);
            if (bars > 16) bars = 16;
            if (bars < 0) bars = 0;

            String vuMeter = "";
            for (int b = 0; b < 16; b++) {
                vuMeter += (b < bars) ? "#" : ".";
            }

            bool isVoice = (rms > 120.0f);
            if (isVoice) voiceFrames++;

            Serial.printf("[MIC VU] [%s] RMS:%5.0f | Peak:%5d | Status: %s\n",
                          vuMeter.c_str(),
                          rms,
                          framePeak,
                          isVoice ? "🔊 SOUND DETECTED" : "🔇 QUIET");
        }
        delay(60);
    }

    Serial.println("--------------------------------------------------");
    Serial.println("  📊 MICROPHONE DIAGNOSTIC SUMMARY");
    Serial.printf("  - Max RMS Energy: %.1f\n", maxRMS);
    Serial.printf("  - Absolute Peak Amplitude: %d / 32767\n", absolutePeak);
    Serial.printf("  - Sound Detection Ratio: %u / %u frames (%.1f%%)\n",
                  voiceFrames, totalFrames,
                  totalFrames > 0 ? (voiceFrames * 100.0f / totalFrames) : 0.0f);
    
    if (maxRMS > 150.0f || absolutePeak > 500) {
        Serial.println("  - Final Verdict: [PASS] ESP32 Microphone is active & receiving audio!");
    } else {
        Serial.println("  - Final Verdict: [NOTE] Low audio signal received (check pin orientation or microphone add-on).");
    }
    Serial.println("==================================================");
    Serial.println();
}

void AudioManager::update() {
    // If recording is active during a Push-to-Talk session, sample audio periodically
    if (_isRecording && (millis() - _lastDiagnosticTime >= 150)) {
        _lastDiagnosticTime = millis();
        float rms = getAudioLevelRMS();
        if (rms > 120.0f) {
            Serial.printf("[ESP32 MIC] Live Audio Level RMS: %.0f (Voice Detected)\n", rms);
        }
    }
}

void AudioManager::playAudio(const uint8_t* data, size_t length) {
    if (!_initialized || !data || length == 0) return;
    // I2S Speaker DAC write
}
