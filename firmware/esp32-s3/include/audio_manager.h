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
    void update();
    void playAudio(const uint8_t* data, size_t length);
    bool isRecording() const { return _isRecording; }
    bool isInitialized() const { return _initialized; }

private:
    AudioManager();
    bool _isRecording = false;
    bool _initialized = false;
    uint32_t _lastDiagnosticTime = 0;
};

