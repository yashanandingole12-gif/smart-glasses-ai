#include "diagnostic_manager.h"
#include <driver/i2s.h>
#include <math.h>
#include <stdio.h>

#define PDM_MIC_CLK_PIN 42
#define PDM_MIC_DATA_PIN 41
#define I2S_PORT I2S_NUM_0
#define SAMPLE_RATE 16000
#define BUFFER_SIZE 512

DiagnosticManager::DiagnosticManager() : _initialized(false) {
  memset(&_last_summary, 0, sizeof(HardwareDiagSummary));
}

bool DiagnosticManager::init() {
  _initialized = true;
  return true;
}

CameraDiagStatus DiagnosticManager::testCamera() {
  CameraDiagStatus status;
  memset(&status, 0, sizeof(CameraDiagStatus));

  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    status.detected = false;
    status.capture_success = false;
    status.error_msg = "";
    return status;
  }

  status.detected = true;
  status.capture_success = true;
  status.frame_size_bytes = fb->len;
  status.width = fb->width;
  status.height = fb->height;

  // Approximate luminance / brightness from JPEG/raw buffer samples
  uint64_t sum = 0;
  size_t sample_count = (fb->len > 1000) ? 1000 : fb->len;
  for (size_t i = 0; i < sample_count; i++) {
    sum += fb->buf[i];
  }
  status.avg_brightness =
      (sample_count > 0) ? (float)sum / (float)(sample_count * 255.0f) : 0.0f;
  status.error_msg = "";

  esp_camera_fb_return(fb);
  return status;
}

AudioDiagStatus DiagnosticManager::testMicrophone(uint32_t sample_duration_ms) {
  AudioDiagStatus status;
  memset(&status, 0, sizeof(AudioDiagStatus));
  status.sample_rate_hz = SAMPLE_RATE;

  // Allocate test sample buffer
  int16_t sample_buffer[BUFFER_SIZE];
  size_t bytes_read = 0;

  uint32_t start_time = millis();
  float sum_squares = 0.0f;
  float peak_val = 0.0f;
  size_t total_samples = 0;
  bool clipped = false;

  while (millis() - start_time < sample_duration_ms) {
    esp_err_t err =
        i2s_read(I2S_PORT, (void *)sample_buffer, sizeof(sample_buffer),
                 &bytes_read, pdMS_TO_TICKS(100));
    if (err != ESP_OK || bytes_read == 0) {
      continue;
    }

    status.i2s_initialized = true;
    status.dma_active = true;

    size_t samples_read = bytes_read / sizeof(int16_t);
    for (size_t i = 0; i < samples_read; i++) {
      float val = (float)sample_buffer[i] / 32768.0f;
      float abs_val = fabsf(val);
      if (abs_val > peak_val)
        peak_val = abs_val;
      if (abs_val >= 0.98f)
        clipped = true;
      sum_squares += val * val;
      total_samples++;
    }
  }

  if (total_samples > 0) {
    status.rms_energy = sqrtf(sum_squares / (float)total_samples);
    status.peak_amplitude = peak_val;
    status.vad_detected = (status.rms_energy > 0.02f);
    status.clip_warning = clipped;
    status.error_msg = "";
  } else {
    status.error_msg = "No audio samples captured from PDM microphone.";
  }

  return status;
}

HardwareDiagSummary DiagnosticManager::runFullSelfTest() {
  HardwareDiagSummary summary;
  summary.uptime_ms = millis();
  summary.free_heap_bytes = esp_get_free_heap_size();
  summary.min_free_heap_bytes = esp_get_minimum_free_heap_size();
  summary.psram_size_bytes = ESP.getPsramSize();
  summary.free_psram_bytes = ESP.getFreePsram();

  summary.camera = testCamera();
  summary.audio = testMicrophone(300);

  summary.passed = summary.audio.i2s_initialized &&
                   (summary.free_heap_bytes > 50000);
  _last_summary = summary;
  return summary;
}

String DiagnosticManager::getJsonReport() {
  HardwareDiagSummary s = runFullSelfTest();
  char buf[1024];
  snprintf(
      buf, sizeof(buf),
      "{\"board\":\"Seeed XIAO ESP32-S3 Sense\",\"passed\":%s,\"uptime_ms\":%u,"
      "\"heap\":{\"free_bytes\":%u,\"min_free_bytes\":%u},"
      "\"psram\":{\"total_bytes\":%u,\"free_bytes\":%u},"
      "\"camera\":{\"detected\":%s,\"capture_success\":%s,\"frame_size_bytes\":"
      "%u,\"width\":%d,\"height\":%d,\"avg_brightness\":%.3f,\"error\":\"%s\"},"
      "\"audio\":{\"i2s_initialized\":%s,\"dma_active\":%s,\"sample_rate_hz\":%"
      "d,\"rms_energy\":%.4f,\"peak_amplitude\":%.2f,\"vad_detected\":%s,"
      "\"clip_warning\":%s,\"error\":\"%s\"}}",
      s.passed ? "true" : "false", s.uptime_ms, s.free_heap_bytes,
      s.min_free_heap_bytes, s.psram_size_bytes, s.free_psram_bytes,
      s.camera.detected ? "true" : "false",
      s.camera.capture_success ? "true" : "false",
      (unsigned int)s.camera.frame_size_bytes, s.camera.width, s.camera.height,
      s.camera.avg_brightness, s.camera.error_msg ? s.camera.error_msg : "",
      s.audio.i2s_initialized ? "true" : "false",
      s.audio.dma_active ? "true" : "false", s.audio.sample_rate_hz,
      s.audio.rms_energy, s.audio.peak_amplitude,
      s.audio.vad_detected ? "true" : "false",
      s.audio.clip_warning ? "true" : "false",
      s.audio.error_msg ? s.audio.error_msg : "");
  return String(buf);
}

DiagnosticManager diagnosticManager;
