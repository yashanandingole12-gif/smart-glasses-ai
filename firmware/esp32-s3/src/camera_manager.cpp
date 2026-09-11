#include "camera_manager.h"
#include "esp_camera.h"

CameraManager::CameraManager() {}

bool CameraManager::init() {
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = CAM_PIN_D0;
    config.pin_d1 = CAM_PIN_D1;
    config.pin_d2 = CAM_PIN_D2;
    config.pin_d3 = CAM_PIN_D3;
    config.pin_d4 = CAM_PIN_D4;
    config.pin_d5 = CAM_PIN_D5;
    config.pin_d6 = CAM_PIN_D6;
    config.pin_d7 = CAM_PIN_D7;
    config.pin_xclk = CAM_PIN_XCLK;
    config.pin_pclk = CAM_PIN_PCLK;
    config.pin_vsync = CAM_PIN_VSYNC;
    config.pin_href = CAM_PIN_HREF;
    config.pin_sccb_sda = CAM_PIN_SIOD;
    config.pin_sccb_scl = CAM_PIN_SIOC;
    config.pin_pwdn = CAM_PIN_PWDN;
    config.pin_reset = CAM_PIN_RESET;
    config.xclk_freq_hz = 20000000;
    config.frame_size = FRAMESIZE_QVGA;     // 320x240 for reliable low-latency capture
    config.pixel_format = PIXFORMAT_JPEG;
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
    config.fb_location = CAMERA_FB_IN_PSRAM;
    config.jpeg_quality = 12;
    config.fb_count = 1;

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        // Fallback: DRAM frame buffer with lower resolution
        config.fb_location = CAMERA_FB_IN_DRAM;
        config.frame_size = FRAMESIZE_QQVGA; // 160x120
        err = esp_camera_init(&config);
    }

    if (err == ESP_OK) {
        _initialized = true;
        Serial.println("[CAMERA] OV2640 Onboard Camera Initialized (320x240 JPEG Ready)");
        return true;
    } else {
        _initialized = false;
        Serial.printf("[CAMERA] Camera Init Notice: Hardware camera module not detected (err=0x%x)\n", err);
        return false;
    }
}

bool CameraManager::captureImage(uint8_t** outBuffer, size_t* outLength) {
    if (!_initialized || outBuffer == nullptr || outLength == nullptr) return false;
    
    releaseBuffer(); // Return any previous frame buffer

    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("[CAMERA] Frame capture failed.");
        return false;
    }
    
    *outBuffer = fb->buf;
    *outLength = fb->len;
    _lastFb = fb;
    Serial.printf("[CAMERA] Frame Captured: %u bytes (JPEG)\n", (unsigned int)fb->len);
    return true;
}

void CameraManager::releaseBuffer() {
    if (_lastFb) {
        esp_camera_fb_return(_lastFb);
        _lastFb = nullptr;
    }
}

