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
    
    // High-clarity resolution for Math OCR & QR reading: VGA (640x480)
    config.pixel_format = PIXFORMAT_JPEG;
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
    config.fb_location = CAMERA_FB_IN_PSRAM;
    config.jpeg_quality = 10; // High clarity (lower is better, 10 is crisp for OCR & QR)
    config.frame_size = FRAMESIZE_VGA; // 640x480
    config.fb_count = 2;      // Double buffering in 8MB Octal PSRAM

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        // Fallback: QVGA (320x240) if PSRAM is constrained
        config.frame_size = FRAMESIZE_QVGA;
        config.fb_count = 1;
        config.jpeg_quality = 12;
        err = esp_camera_init(&config);
    }

    if (err == ESP_OK) {
        _initialized = true;
        setSensorParameters(1, 1, 1); // Boost brightness, contrast & enable auto-exposure AEC2
        Serial.println("[CAMERA] Onboard Camera Initialized (VGA 640x480 PSRAM High-Clarity Mode Ready)");
        return true;
    } else {
        _initialized = false;
        Serial.printf("[CAMERA] Camera Init Notice: Hardware camera module not detected (err=0x%x)\n", err);
        return false;
    }
}

void CameraManager::setSensorParameters(int brightness, int contrast, int aec2) {
    sensor_t* s = esp_camera_sensor_get();
    if (s != nullptr) {
        s->set_brightness(s, brightness); // 1 = slightly brighter for indoor/glasses use
        s->set_contrast(s, contrast);     // 1 = higher contrast for sharp equation lines & QR codes
        s->set_saturation(s, 0);
        s->set_special_effect(s, 0);     // Normal
        s->set_whitebal(s, 1);           // Auto White Balance
        s->set_awb_gain(s, 1);
        s->set_wb_mode(s, 0);            // Auto WB
        s->set_exposure_ctrl(s, 1);      // Auto Exposure Control
        s->set_aec2(s, aec2);            // Enable AEC2 for rapid lighting adaptation
        s->set_gain_ctrl(s, 1);          // Auto Gain
        s->set_agc_gain(s, 0);
        s->set_gainceiling(s, (gainceiling_t)2);
        s->set_bpc(s, 1);                // Black pixel correction
        s->set_wpc(s, 1);                // White pixel correction
        s->set_raw_gma(s, 1);            // Gamma correction
        s->set_lenc(s, 1);               // Lens correction
        
        // Handle OV3660 specific registers if detected
        if (s->id.PID == OV3660_PID) {
            s->set_vflip(s, 1);
            s->set_brightness(s, brightness);
            s->set_contrast(s, contrast);
        }
        Serial.println("[CAMERA] Sensor parameters tuned (Brightness+1, Contrast+1, AEC2 Auto-Exposure Active)");
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
    Serial.printf("[CAMERA] Frame Captured: %u bytes (%dx%d JPEG)\n", 
                  (unsigned int)fb->len, fb->width, fb->height);
    return true;
}

void CameraManager::releaseBuffer() {
    if (_lastFb) {
        esp_camera_fb_return(_lastFb);
        _lastFb = nullptr;
    }
}

