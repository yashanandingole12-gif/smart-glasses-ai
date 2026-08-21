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
    void playAudio(const uint8_t* data, size_t length);
    bool isRecording() const { return _isRecording; }

private:
    AudioManager();
    bool _isRecording = false;
    bool _initialized = false;
};
