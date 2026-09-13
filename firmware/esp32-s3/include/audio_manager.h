#pragma once

#include <Arduino.h>
#include "board_config.h"

class AudioManager {
public:
    static AudioManager& getInstance() {
        static AudioManager instance;
        return instance;
    }

    bool init();
    void startMicrophone();
    void stopMicrophone();
    size_t readMicrophone(int16_t* buffer, size_t maxSamples);
    float getAudioLevelRMS();
    void runMicrophoneDiagnostic(uint32_t durationMs = 3000);
    
    // Direct WAV Audio Recording from ESP32 Onboard Digital Mic (MSM261D)
    bool recordWavAudio(uint32_t durationMs, uint8_t** outWavBuffer, size_t* outWavSize);
    void releaseWavBuffer(uint8_t* wavBuffer);

    void update();
    void playAudio(const uint8_t* data, size_t length);
    bool isRecording() const { return _isRecording; }
    bool isInitialized() const { return _initialized; }
    
    // Hands-free Voice Activity Detection (VAD) & Wake Trigger
    void setVadEnabled(bool enabled) { _vadEnabled = enabled; }
    bool isVadEnabled() const { return _vadEnabled; }
    void triggerVoiceWakeSession();
    void stopVoiceWakeSession();

private:
    AudioManager();
    bool _isRecording = false;
    bool _initialized = false;
    uint32_t _lastDiagnosticTime = 0;
    
    // VAD State Machine
    bool _vadEnabled = true;
    bool _speechActive = false;
    uint32_t _speechStartTime = 0;
    uint32_t _lastSpeechTime = 0;
    uint8_t _consecutiveVoiceFrames = 0;
};

