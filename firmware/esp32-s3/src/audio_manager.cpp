#include "audio_manager.h"
#include "ble_manager.h"
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

    // 1. Calculate DC mean to eliminate hardware PDM bias
    double sum = 0.0;
    for (size_t i = 0; i < count; i++) {
        sum += (double)samples[i];
    }
    double mean = sum / (double)count;

    // 2. Compute true AC RMS energy without DC offset
    double sumSq = 0.0;
    for (size_t i = 0; i < count; i++) {
        double acVal = (double)samples[i] - mean;
        sumSq += acVal * acVal;
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
    Serial.println("  ESP32-S3 PHYSICAL MICROPHONE LIVE DIAGNOSTIC");
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
            
            // Remove DC offset for diagnostic
            double sum = 0.0;
            for (size_t i = 0; i < samplesRead; i++) sum += (double)buffer[i];
            double mean = sum / (double)samplesRead;

            double sumSq = 0.0;
            int16_t framePeak = 0;
            for (size_t i = 0; i < samplesRead; i++) {
                double ac = (double)buffer[i] - mean;
                if (abs((int)ac) > framePeak) framePeak = abs((int)ac);
                sumSq += ac * ac;
            }

            float rms = (float)sqrt(sumSq / (double)samplesRead);
            if (rms > maxRMS) maxRMS = rms;
            if (framePeak > absolutePeak) absolutePeak = framePeak;

            // Visual VU Meter bar (16 levels)
            int bars = (int)(rms / 50.0f);
            if (bars > 16) bars = 16;
            if (bars < 0) bars = 0;

            String vuMeter = "";
            for (int b = 0; b < 16; b++) {
                vuMeter += (b < bars) ? "#" : ".";
            }

            bool isVoice = (rms > 200.0f);
            if (isVoice) voiceFrames++;

            Serial.printf("[MIC VU] [%s] RMS:%5.0f | Peak:%5d | Status: %s\n",
                          vuMeter.c_str(),
                          rms,
                          framePeak,
                          isVoice ? "SOUND DETECTED" : "QUIET");
        }
        delay(60);
    }

    Serial.println("--------------------------------------------------");
    Serial.println("  MICROPHONE DIAGNOSTIC SUMMARY");
    Serial.printf("  - Max RMS Energy: %.1f\n", maxRMS);
    Serial.printf("  - Absolute Peak Amplitude: %d / 32767\n", absolutePeak);
    Serial.printf("  - Sound Detection Ratio: %u / %u frames (%.1f%%)\n",
                  voiceFrames, totalFrames,
                  totalFrames > 0 ? (voiceFrames * 100.0f / totalFrames) : 0.0f);
    
    if (maxRMS > 150.0f || absolutePeak > 300) {
        Serial.println("  - Final Verdict: [PASS] ESP32 Microphone is active & receiving audio!");
    } else {
        Serial.println("  - Final Verdict: [NOTE] Low audio signal received.");
    }
    Serial.println("==================================================");
    Serial.println();
}

void AudioManager::triggerVoiceWakeSession() {
    _speechActive = true;
    _speechStartTime = millis();
    _lastSpeechTime = millis();
    _consecutiveVoiceFrames = 2;
    startMicrophone();
    Serial.println("[VOICE WAKE] >>> WAKE TRIGGER ACTIVATED -> Sending TALK_START to Mobile Phone");
    BleManager::getInstance().sendEvent("TALK_START");
}

void AudioManager::stopVoiceWakeSession() {
    _speechActive = false;
    _consecutiveVoiceFrames = 0;
    stopMicrophone();
    Serial.println("[VOICE WAKE] <<< WAKE SESSION STOPPED -> Sending TALK_STOP to Mobile Phone");
    BleManager::getInstance().sendEvent("TALK_STOP");
}

void AudioManager::update() {
    if (!_initialized) return;

    if (millis() - _lastDiagnosticTime >= 100) {
        _lastDiagnosticTime = millis();
        float rms = getAudioLevelRMS();

        if (_vadEnabled) {
            // Threshold: > 250 RMS is active human voice (calibrated with DC bias subtracted)
            if (rms > 250.0f) {
                _lastSpeechTime = millis();
                _consecutiveVoiceFrames++;

                if (!_speechActive && _consecutiveVoiceFrames >= 2) {
                    // Start of voice query detected
                    _speechActive = true;
                    _speechStartTime = millis();
                    startMicrophone();
                    Serial.printf("[VOICE WAKE] >>> Speech Detected (RMS: %.0f) -> Sending TALK_START to Mobile Phone\n", rms);
                    BleManager::getInstance().sendEvent("TALK_START");
                } else if (_speechActive) {
                    Serial.printf("[ESP32 MIC] Live Audio RMS: %.0f (Speaking)\n", rms);
                }
            } else {
                if (_consecutiveVoiceFrames > 0 && !_speechActive) {
                    _consecutiveVoiceFrames--;
                }

                // If currently active and silence persists for > 1200ms, conclude turn
                if (_speechActive && (millis() - _lastSpeechTime > 1200)) {
                    _speechActive = false;
                    _consecutiveVoiceFrames = 0;
                    stopMicrophone();
                    Serial.println("[VOICE WAKE] <<< Silence Detected (1.2s) -> Sending TALK_STOP to Mobile Phone");
                    BleManager::getInstance().sendEvent("TALK_STOP");
                }
            }
        }
    }
}

void AudioManager::playAudio(const uint8_t* data, size_t length) {
    if (!_initialized || !data || length == 0) return;
    // I2S Speaker DAC write
}

// 44-byte standard RIFF WAV Header
struct WavHeader {
    char riff_tag[4];        // "RIFF"
    uint32_t riff_size;      // total file size - 8
    char wave_tag[4];        // "WAVE"
    char fmt_tag[4];         // "fmt "
    uint32_t fmt_size;       // 16
    uint16_t audio_format;   // 1 (PCM)
    uint16_t num_channels;   // 1 (Mono)
    uint32_t sample_rate;    // 16000
    uint32_t byte_rate;      // sample_rate * num_channels * (bits_per_sample / 8) = 32000
    uint16_t block_align;    // num_channels * (bits_per_sample / 8) = 2
    uint16_t bits_per_sample;// 16
    char data_tag[4];        // "data"
    uint32_t data_size;      // num_samples * 2
};

bool AudioManager::recordWavAudio(uint32_t durationMs, uint8_t** outWavBuffer, size_t* outWavSize) {
    if (!_initialized || outWavBuffer == nullptr || outWavSize == nullptr) return false;
    if (durationMs == 0) durationMs = 3000;
    if (durationMs > 10000) durationMs = 10000; // Cap at 10s for safety

    size_t totalSamples = (I2S_MIC_SAMPLE_RATE * durationMs) / 1000;
    size_t pcmDataBytes = totalSamples * sizeof(int16_t);
    size_t totalWavBytes = sizeof(WavHeader) + pcmDataBytes;

    // Allocate in PSRAM if available, or heap
    uint8_t* wavBuf = (uint8_t*)(psramFound() ? ps_malloc(totalWavBytes) : malloc(totalWavBytes));
    if (!wavBuf) {
        Serial.printf("[AUDIO] ERROR: Failed to allocate %u bytes for WAV recording buffer\n", (unsigned int)totalWavBytes);
        return false;
    }

    // Populate RIFF WAV Header
    WavHeader* header = (WavHeader*)wavBuf;
    memcpy(header->riff_tag, "RIFF", 4);
    header->riff_size = (uint32_t)(totalWavBytes - 8);
    memcpy(header->wave_tag, "WAVE", 4);
    memcpy(header->fmt_tag, "fmt ", 4);
    header->fmt_size = 16;
    header->audio_format = 1; // PCM
    header->num_channels = 1; // Mono
    header->sample_rate = I2S_MIC_SAMPLE_RATE;
    header->byte_rate = I2S_MIC_SAMPLE_RATE * 1 * sizeof(int16_t);
    header->block_align = 1 * sizeof(int16_t);
    header->bits_per_sample = 16;
    memcpy(header->data_tag, "data", 4);
    header->data_size = (uint32_t)pcmDataBytes;

    int16_t* pcmPayload = (int16_t*)(wavBuf + sizeof(WavHeader));
    size_t samplesRecorded = 0;
    uint32_t startTime = millis();
    int16_t tempChunk[256];

    Serial.printf("[AUDIO] 🎙️ Recording %u ms audio from ESP32 digital mic (16kHz 16-bit Mono WAV)...\n", (unsigned int)durationMs);

    while (samplesRecorded < totalSamples && (millis() - startTime < durationMs + 500)) {
        size_t toRead = (totalSamples - samplesRecorded > 256) ? 256 : (totalSamples - samplesRecorded);
        size_t readCount = readMicrophone(tempChunk, toRead);
        if (readCount > 0) {
            memcpy(pcmPayload + samplesRecorded, tempChunk, readCount * sizeof(int16_t));
            samplesRecorded += readCount;
        } else {
            delay(5);
        }
    }

    // Update actual data size if fewer samples recorded
    if (samplesRecorded < totalSamples) {
        pcmDataBytes = samplesRecorded * sizeof(int16_t);
        totalWavBytes = sizeof(WavHeader) + pcmDataBytes;
        header->riff_size = (uint32_t)(totalWavBytes - 8);
        header->data_size = (uint32_t)pcmDataBytes;
    }

    *outWavBuffer = wavBuf;
    *outWavSize = totalWavBytes;
    Serial.printf("[AUDIO] Audio recording complete: %u bytes (%u samples, %u ms)\n", 
                  (unsigned int)totalWavBytes, (unsigned int)samplesRecorded, (unsigned int)(samplesRecorded * 1000 / I2S_MIC_SAMPLE_RATE));
    return true;
}

void AudioManager::releaseWavBuffer(uint8_t* wavBuffer) {
    if (wavBuffer) {
        free(wavBuffer);
    }
}
