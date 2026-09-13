#pragma once

#include <Arduino.h>
#include <esp_camera.h>

struct CameraDiagStatus {
    bool detected;
    uint32_t sensor_pid;
    bool capture_success;
    size_t frame_size_bytes;
    int width;
    int height;
    float avg_brightness;
    const char* error_msg;
};

struct AudioDiagStatus {
    bool i2s_initialized;
    bool dma_active;
    int sample_rate_hz;
    float peak_amplitude;
    float rms_energy;
    bool vad_detected;
    bool clip_warning;
    const char* error_msg;
};

struct HardwareDiagSummary {
    bool passed;
    uint32_t uptime_ms;
    uint32_t free_heap_bytes;
    uint32_t min_free_heap_bytes;
    uint32_t psram_size_bytes;
    uint32_t free_psram_bytes;
    CameraDiagStatus camera;
    AudioDiagStatus audio;
};

class DiagnosticManager {
public:
    DiagnosticManager();
    bool init();
    HardwareDiagSummary runFullSelfTest();
    CameraDiagStatus testCamera();
    AudioDiagStatus testMicrophone(uint32_t sample_duration_ms = 500);
    String getJsonReport();
    const char* getDiagnosticHtml();

private:
    bool _initialized;
    HardwareDiagSummary _last_summary;
};

extern DiagnosticManager diagnosticManager;
