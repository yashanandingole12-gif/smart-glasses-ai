#pragma once

#include <Arduino.h>
#include "board_config.h"
#include "esp_camera.h"

class CameraManager {
public:
    static CameraManager& getInstance() {
        static CameraManager instance;
        return instance;
    }

    bool init();
    bool captureImage(uint8_t** outBuffer, size_t* outLength);
    void releaseBuffer();
    bool isAvailable() const { return _initialized; }
    void setSensorParameters(int brightness = 1, int contrast = 1, int aec2 = 1);

private:
    CameraManager();
    bool _initialized = false;
    camera_fb_t* _lastFb = nullptr;
};

