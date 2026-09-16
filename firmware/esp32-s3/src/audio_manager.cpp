#include "audio_manager.h"
#include "ble_manager.h"
#include <driver/i2s.h>
#include <math.h>

AudioManager::AudioManager() {}

bool AudioManager::init() {
    bool micOk = initMicrophone();
    bool spkOk = initSpeaker();
    return micOk || spkOk;
}

bool AudioManager::initMicrophone() {
    // 1. Configure I2S driver in PDM RX mode (XIAO ESP32-S3 Sense on-board mic)
    i2s_config_t i2s_mic_config = {
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

    i2s_pin_config_t mic_pin_config = {
        .bck_io_num = I2S_PIN_NO_CHANGE,
        .ws_io_num = PDM_MIC_CLK,    // PDM CLK (GPIO 42 on XIAO Sense)
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = PDM_MIC_DATA   // PDM DATA (GPIO 41 on XIAO Sense)
    };

    esp_err_t err = i2s_driver_install(I2S_MIC_PORT, &i2s_mic_config, 0, NULL);
    if (err != ESP_OK) {
        // Fallback: Standard I2S Mode for external digital mic (INMP441)
        i2s_mic_config.mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX);
        mic_pin_config.bck_io_num = I2S_MIC_BCLK;
        mic_pin_config.ws_io_num = I2S_MIC_LRCLK;
        mic_pin_config.data_in_num = I2S_MIC_DATA;
        err = i2s_driver_install(I2S_MIC_PORT, &i2s_mic_config, 0, NULL);
    }

    if (err == ESP_OK) {
        i2s_set_pin(I2S_MIC_PORT, &mic_pin_config);
        i2s_set_clk(I2S_MIC_PORT, I2S_MIC_SAMPLE_RATE, I2S_BITS_PER_SAMPLE_16BIT, I2S_CHANNEL_MONO);
        _micInitialized = true;
        Serial.printf("[AUDIO] I2S/PDM Microphone Driver Active (16kHz Mono, CLK=%d, DATA=%d)\n", PDM_MIC_CLK, PDM_MIC_DATA);
    } else {
        Serial.printf("[AUDIO] I2S Mic Driver Install Failed (err=0x%x)\n", err);
        _micInitialized = false;
    }
    return _micInitialized;
}

bool AudioManager::initSpeaker() {
    // 2. Configure I2S driver in TX mode for External Speaker / MAX98357A DAC
    i2s_config_t i2s_spk_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
        .sample_rate = I2S_SPK_SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT, // Stereo frames ensure MAX98357A compatibility
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 6,
        .dma_buf_len = 256,
        .use_apll = false,
        .tx_desc_auto_clear = true, // Zero DMA buffer on underflow to prevent buzzing
        .fixed_mclk = 0
    };

    i2s_pin_config_t spk_pin_config = {
        .bck_io_num = I2S_SPK_BCLK,   // GPIO 7 / D8
        .ws_io_num = I2S_SPK_LRCLK,   // GPIO 8 / D9
        .data_out_num = I2S_SPK_DATA, // GPIO 9 / D10
        .data_in_num = I2S_PIN_NO_CHANGE
    };

    esp_err_t err = i2s_driver_install(I2S_SPK_PORT, &i2s_spk_config, 0, NULL);
    if (err == ESP_OK) {
        i2s_set_pin(I2S_SPK_PORT, &spk_pin_config);
        i2s_set_clk(I2S_SPK_PORT, I2S_SPK_SAMPLE_RATE, I2S_BITS_PER_SAMPLE_16BIT, I2S_CHANNEL_STEREO);
        i2s_zero_dma_buffer(I2S_SPK_PORT);
        _speakerInitialized = true;
        Serial.printf("[AUDIO] I2S Speaker Driver Active (16kHz Stereo-Out, BCLK=%d, LRC=%d, DATA=%d)\n", 
                      I2S_SPK_BCLK, I2S_SPK_LRCLK, I2S_SPK_DATA);
    } else {
        Serial.printf("[AUDIO] I2S Speaker Driver Install Failed (err=0x%x)\n", err);
        _speakerInitialized = false;
    }
    return _speakerInitialized;
}

void AudioManager::setVolume(uint8_t volumePercent) {
    if (volumePercent > 100) volumePercent = 100;
    _volume = volumePercent;
    Serial.printf("[AUDIO] Speaker Volume set to %u%%\n", _volume);
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
    if (!_micInitialized || buffer == nullptr || maxSamples == 0) return 0;
    size_t bytesRead = 0;
    esp_err_t err = i2s_read(I2S_MIC_PORT, (void*)buffer, maxSamples * sizeof(int16_t), &bytesRead, pdMS_TO_TICKS(100));
    if (err == ESP_OK) {
        return bytesRead / sizeof(int16_t);
    }
    return 0;
}

float AudioManager::getAudioLevelRMS() {
    if (!_micInitialized) return 0.0f;
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
    if (!_micInitialized) {
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

// -----------------------------------------------------------------------------
// Speaker Synthesizer & Playback Functions
// -----------------------------------------------------------------------------

void AudioManager::playTone(uint16_t freqHz, uint32_t durationMs) {
    if (!_speakerInitialized || durationMs == 0) return;
    
    if (freqHz == 0) {
        delay(durationMs);
        return;
    }

    size_t totalSamples = (I2S_SPK_SAMPLE_RATE * durationMs) / 1000;
    const size_t CHUNK_SAMPLES = 128;
    int16_t stereoBuffer[CHUNK_SAMPLES * 2];

    float phase = 0.0f;
    float phaseInc = (2.0f * (float)M_PI * (float)freqHz) / (float)I2S_SPK_SAMPLE_RATE;
    float volScale = ((float)_volume / 100.0f) * 0.75f; // Scale to avoid clipping

    size_t samplesGenerated = 0;
    while (samplesGenerated < totalSamples) {
        size_t currentBatch = (totalSamples - samplesGenerated > CHUNK_SAMPLES) ? CHUNK_SAMPLES : (totalSamples - samplesGenerated);
        for (size_t i = 0; i < currentBatch; i++) {
            // Smooth 5ms envelope ramping to prevent audio popping
            float env = 1.0f;
            size_t sampleIdx = samplesGenerated + i;
            if (sampleIdx < 80) {
                env = (float)sampleIdx / 80.0f;
            } else if (totalSamples - sampleIdx < 80) {
                env = (float)(totalSamples - sampleIdx) / 80.0f;
            }

            float sampleVal = sinf(phase) * 30000.0f * volScale * env;
            int16_t s = (int16_t)sampleVal;
            stereoBuffer[i * 2] = s;     // Left channel
            stereoBuffer[i * 2 + 1] = s; // Right channel

            phase += phaseInc;
            if (phase >= 2.0f * (float)M_PI) phase -= 2.0f * (float)M_PI;
        }

        size_t bytesWritten = 0;
        i2s_write(I2S_SPK_PORT, (const void*)stereoBuffer, currentBatch * 2 * sizeof(int16_t), &bytesWritten, portMAX_DELAY);
        samplesGenerated += currentBatch;
    }
}

void AudioManager::playMelody(const uint16_t* freqs, const uint16_t* durationsMs, size_t count) {
    if (!_speakerInitialized || !freqs || !durationsMs || count == 0) return;
    for (size_t i = 0; i < count; i++) {
        playTone(freqs[i], durationsMs[i]);
        delay(15); // Short articulation gap
    }
}

void AudioManager::playSound(SoundEffect effect) {
    if (!_speakerInitialized) return;

    switch (effect) {
        case SoundEffect::SOUND_WAKE: {
            uint16_t notes[] = { 659, 988 };
            uint16_t durs[] = { 80, 140 };
            playMelody(notes, durs, 2);
            break;
        }
        case SoundEffect::SOUND_AI_RESPONSE: {
            uint16_t notes[] = { 523, 659, 784, 1046 };
            uint16_t durs[] = { 70, 70, 90, 150 };
            playMelody(notes, durs, 4);
            break;
        }
        case SoundEffect::SOUND_MESSAGE_ALERT: {
            uint16_t notes[] = { 784, 0, 1046 };
            uint16_t durs[] = { 90, 40, 180 };
            playMelody(notes, durs, 3);
            break;
        }
        case SoundEffect::SOUND_CALL_INCOMING: {
            uint16_t notes[] = { 880, 1046, 880, 1046 };
            uint16_t durs[] = { 100, 100, 100, 150 };
            playMelody(notes, durs, 4);
            break;
        }
        case SoundEffect::SOUND_SUCCESS: {
            uint16_t notes[] = { 523, 784, 1046 };
            uint16_t durs[] = { 60, 60, 140 };
            playMelody(notes, durs, 3);
            break;
        }
        case SoundEffect::SOUND_ERROR: {
            uint16_t notes[] = { 349, 261 };
            uint16_t durs[] = { 110, 200 };
            playMelody(notes, durs, 2);
            break;
        }
        case SoundEffect::SOUND_DEVICE_CONNECTED: {
            uint16_t notes[] = { 523, 784 };
            uint16_t durs[] = { 60, 120 };
            playMelody(notes, durs, 2);
            break;
        }
        case SoundEffect::SOUND_DEVICE_DISCONNECTED: {
            uint16_t notes[] = { 784, 523 };
            uint16_t durs[] = { 80, 140 };
            playMelody(notes, durs, 2);
            break;
        }
        case SoundEffect::SOUND_PTT_START: {
            playTone(1046, 40);
            break;
        }
        case SoundEffect::SOUND_PTT_STOP: {
            playTone(659, 40);
            break;
        }
    }
}

void AudioManager::playPcmAudio(const int16_t* samples, size_t sampleCount, uint32_t sampleRate) {
    if (!_speakerInitialized || !samples || sampleCount == 0) return;

    if (sampleRate != I2S_SPK_SAMPLE_RATE) {
        i2s_set_clk(I2S_SPK_PORT, sampleRate, I2S_BITS_PER_SAMPLE_16BIT, I2S_CHANNEL_STEREO);
    }

    const size_t BATCH_SIZE = 128;
    int16_t stereoBuffer[BATCH_SIZE * 2];
    float volScale = (float)_volume / 100.0f;

    size_t processed = 0;
    while (processed < sampleCount) {
        size_t toProcess = (sampleCount - processed > BATCH_SIZE) ? BATCH_SIZE : (sampleCount - processed);
        for (size_t i = 0; i < toProcess; i++) {
            int16_t s = (int16_t)((float)samples[processed + i] * volScale);
            stereoBuffer[i * 2] = s;     // Left
            stereoBuffer[i * 2 + 1] = s; // Right
        }
        size_t bytesWritten = 0;
        i2s_write(I2S_SPK_PORT, (const void*)stereoBuffer, toProcess * 2 * sizeof(int16_t), &bytesWritten, portMAX_DELAY);
        processed += toProcess;
    }

    if (sampleRate != I2S_SPK_SAMPLE_RATE) {
        i2s_set_clk(I2S_SPK_PORT, I2S_SPK_SAMPLE_RATE, I2S_BITS_PER_SAMPLE_16BIT, I2S_CHANNEL_STEREO);
    }
}

// 44-byte standard RIFF WAV Header
struct WavHeader {
    char riff_tag[4];        // "RIFF"
    uint32_t riff_size;      // total file size - 8
    char wave_tag[4];        // "WAVE"
    char fmt_tag[4];         // "fmt "
    uint32_t fmt_size;       // 16
    uint16_t audio_format;   // 1 (PCM)
    uint16_t num_channels;   // 1 (Mono) or 2 (Stereo)
    uint32_t sample_rate;    // e.g. 16000
    uint32_t byte_rate;      // sample_rate * num_channels * (bits_per_sample / 8)
    uint16_t block_align;    // num_channels * (bits_per_sample / 8)
    uint16_t bits_per_sample;// 16
    char data_tag[4];        // "data"
    uint32_t data_size;      // data bytes
};

void AudioManager::playWavAudio(const uint8_t* wavBytes, size_t wavLength) {
    if (!_speakerInitialized || !wavBytes || wavLength < sizeof(WavHeader)) return;

    const WavHeader* header = (const WavHeader*)wavBytes;
    if (strncmp(header->riff_tag, "RIFF", 4) != 0 || strncmp(header->wave_tag, "WAVE", 4) != 0) {
        Serial.println("[AUDIO] ERROR: Invalid WAV header format.");
        return;
    }

    // Locate "data" chunk
    size_t dataOffset = 12;
    while (dataOffset + 8 <= wavLength) {
        if (memcmp(wavBytes + dataOffset, "data", 4) == 0) {
            dataOffset += 8; // skip "data" tag and 4-byte size
            break;
        }
        uint32_t chunkSize = *(uint32_t*)(wavBytes + dataOffset + 4);
        dataOffset += 8 + chunkSize;
    }

    if (dataOffset >= wavLength) {
        dataOffset = sizeof(WavHeader);
    }

    const int16_t* pcmSamples = (const int16_t*)(wavBytes + dataOffset);
    size_t pcmBytes = wavLength - dataOffset;
    size_t sampleCount = pcmBytes / sizeof(int16_t);

    Serial.printf("[AUDIO] Playing WAV Audio: %u bytes (%u Hz, %d-channel, %u samples)\n",
                  (unsigned int)wavLength, header->sample_rate, header->num_channels, (unsigned int)sampleCount);

    if (header->num_channels == 1) {
        playPcmAudio(pcmSamples, sampleCount, header->sample_rate);
    } else {
        if (header->sample_rate != I2S_SPK_SAMPLE_RATE) {
            i2s_set_clk(I2S_SPK_PORT, header->sample_rate, I2S_BITS_PER_SAMPLE_16BIT, I2S_CHANNEL_STEREO);
        }
        size_t bytesWritten = 0;
        i2s_write(I2S_SPK_PORT, (const void*)pcmSamples, pcmBytes, &bytesWritten, portMAX_DELAY);
        if (header->sample_rate != I2S_SPK_SAMPLE_RATE) {
            i2s_set_clk(I2S_SPK_PORT, I2S_SPK_SAMPLE_RATE, I2S_BITS_PER_SAMPLE_16BIT, I2S_CHANNEL_STEREO);
        }
    }
}

void AudioManager::streamPcmChunk(const uint8_t* pcmChunk, size_t chunkSize) {
    if (!_speakerInitialized || !pcmChunk || chunkSize == 0) return;

    size_t sampleCount = chunkSize / sizeof(int16_t);
    const int16_t* inSamples = (const int16_t*)pcmChunk;
    const size_t BATCH_SIZE = 128;
    int16_t stereoBuf[BATCH_SIZE * 2];
    float volScale = (float)_volume / 100.0f;

    size_t processed = 0;
    while (processed < sampleCount) {
        size_t toProcess = (sampleCount - processed > BATCH_SIZE) ? BATCH_SIZE : (sampleCount - processed);
        for (size_t i = 0; i < toProcess; i++) {
            int16_t s = (int16_t)((float)inSamples[processed + i] * volScale);
            stereoBuf[i * 2] = s;
            stereoBuf[i * 2 + 1] = s;
        }
        size_t bytesWritten = 0;
        i2s_write(I2S_SPK_PORT, (const void*)stereoBuf, toProcess * 2 * sizeof(int16_t), &bytesWritten, pdMS_TO_TICKS(50));
        processed += toProcess;
    }
}

void AudioManager::stopPlayback() {
    if (_speakerInitialized) {
        i2s_zero_dma_buffer(I2S_SPK_PORT);
    }
}

void AudioManager::runSpeakerDiagnostic() {
    if (!_speakerInitialized) {
        Serial.println("[SPEAKER DIAGNOSTIC] ERROR: I2S Speaker driver not initialized.");
        return;
    }

    Serial.println();
    Serial.println("==================================================");
    Serial.println("  ESP32-S3 PHYSICAL SPEAKER LIVE DIAGNOSTIC");
    Serial.printf("  Sampling Rate: %d Hz | Port: I2S_NUM_%d\n", I2S_SPK_SAMPLE_RATE, I2S_SPK_PORT);
    Serial.printf("  Pins: BCLK=GPIO%d, LRCLK=GPIO%d, DATA=GPIO%d\n", I2S_SPK_BCLK, I2S_SPK_LRCLK, I2S_SPK_DATA);
    Serial.printf("  Current Volume: %u%%\n", _volume);
    Serial.println("  Playing Test Chimes & Message Notifications on Speaker...");
    Serial.println("==================================================");

    Serial.println("  1. Playing Wake-up Chime (Rising 2-tone)...");
    playSound(SoundEffect::SOUND_WAKE);
    delay(400);

    Serial.println("  2. Playing AI Response Ready Chime (4-note arpeggio)...");
    playSound(SoundEffect::SOUND_AI_RESPONSE);
    delay(400);

    Serial.println("  3. Playing Incoming Message Notification Alert...");
    playSound(SoundEffect::SOUND_MESSAGE_ALERT);
    delay(400);

    Serial.println("  4. Playing Success Tone...");
    playSound(SoundEffect::SOUND_SUCCESS);
    delay(300);

    Serial.println("--------------------------------------------------");
    Serial.println("  [PASS] Speaker Audio Test Complete!");
    Serial.println("==================================================");
    Serial.println();
}

void AudioManager::runFullAudioDiagnostic() {
    runSpeakerDiagnostic();
    delay(300);
    runMicrophoneDiagnostic(3000);
}

// -----------------------------------------------------------------------------
// Voice Wake, VAD & Recording
// -----------------------------------------------------------------------------

void AudioManager::triggerVoiceWakeSession() {
    _speechActive = true;
    _speechStartTime = millis();
    _lastSpeechTime = millis();
    _consecutiveVoiceFrames = 2;
    playSound(SoundEffect::SOUND_WAKE);
    startMicrophone();
    Serial.println("[VOICE WAKE] >>> WAKE TRIGGER ACTIVATED -> Sending TALK_START to Mobile Phone");
    BleManager::getInstance().sendEvent("TALK_START");
}

void AudioManager::stopVoiceWakeSession() {
    _speechActive = false;
    _consecutiveVoiceFrames = 0;
    stopMicrophone();
    playSound(SoundEffect::SOUND_PTT_STOP);
    Serial.println("[VOICE WAKE] <<< WAKE SESSION STOPPED -> Sending TALK_STOP to Mobile Phone");
    BleManager::getInstance().sendEvent("TALK_STOP");
}

void AudioManager::update() {
    if (!_micInitialized) return;

    if (millis() - _lastDiagnosticTime >= 100) {
        _lastDiagnosticTime = millis();
        float rms = getAudioLevelRMS();

        if (_vadEnabled) {
            if (rms > 250.0f) {
                _lastSpeechTime = millis();
                _consecutiveVoiceFrames++;

                if (!_speechActive && _consecutiveVoiceFrames >= 2) {
                    _speechActive = true;
                    _speechStartTime = millis();
                    playSound(SoundEffect::SOUND_WAKE);
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

                if (_speechActive && (millis() - _lastSpeechTime > 1200)) {
                    _speechActive = false;
                    _consecutiveVoiceFrames = 0;
                    stopMicrophone();
                    playSound(SoundEffect::SOUND_PTT_STOP);
                    Serial.println("[VOICE WAKE] <<< Silence Detected (1.2s) -> Sending TALK_STOP to Mobile Phone");
                    BleManager::getInstance().sendEvent("TALK_STOP");
                }
            }
        }
    }
}

bool AudioManager::recordWavAudio(uint32_t durationMs, uint8_t** outWavBuffer, size_t* outWavSize) {
    if (!_micInitialized || outWavBuffer == nullptr || outWavSize == nullptr) return false;
    if (durationMs == 0) durationMs = 3000;
    if (durationMs > 10000) durationMs = 10000;

    size_t totalSamples = (I2S_MIC_SAMPLE_RATE * durationMs) / 1000;
    size_t pcmDataBytes = totalSamples * sizeof(int16_t);
    size_t totalWavBytes = sizeof(WavHeader) + pcmDataBytes;

    uint8_t* wavBuf = (uint8_t*)(psramFound() ? ps_malloc(totalWavBytes) : malloc(totalWavBytes));
    if (!wavBuf) {
        Serial.printf("[AUDIO] ERROR: Failed to allocate %u bytes for WAV recording buffer\n", (unsigned int)totalWavBytes);
        return false;
    }

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
