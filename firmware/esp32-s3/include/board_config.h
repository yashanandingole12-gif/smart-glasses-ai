#pragma once

// =============================================================================
// Smart Glasses Seeed Studio XIAO ESP32-S3 Sense Board Pin Configuration
// Matches the official Sense expansion board (OV2640 camera + PDM microphone).
// =============================================================================

// Push-to-talk Physical Button
#define PIN_BUTTON_PTT          0       // Active LOW with internal pull-up (BOOT button / User PTT)
#define BUTTON_DEBOUNCE_MS      35
#define BUTTON_LONG_PRESS_MS    1000

// Status Indicator LED
#define PIN_LED_STATUS          21      // Onboard User LED (Active LOW on XIAO ESP32-S3)

// Battery Monitoring (ADC)
#define PIN_BATTERY_ADC         1       // Analog voltage divider pin (A0 / GPIO 1)
#define BATTERY_ADC_R1          100000.0f
#define BATTERY_ADC_R2          100000.0f

// On-board PDM Digital Microphone (MSM261D3526H1CPM on XIAO Sense)
#define I2S_MIC_PORT            I2S_NUM_0
#define PDM_MIC_CLK             42      // PDM Clock
#define PDM_MIC_DATA            41      // PDM Data In
#define I2S_MIC_BCLK            41
#define I2S_MIC_LRCLK           42
#define I2S_MIC_DATA            41
#define I2S_MIC_SAMPLE_RATE     16000

// External I2S Speaker / DAC Pinout (MAX98357A / Bone Conduction)
#define I2S_SPK_PORT            I2S_NUM_1
#define I2S_SPK_BCLK            7
#define I2S_SPK_LRCLK           8
#define I2S_SPK_DATA            9
#define I2S_SPK_SAMPLE_RATE     16000

// On-board OV2640 Camera Pinout (Seeed Studio XIAO ESP32-S3 Sense Expansion)
#define CAM_PIN_PWDN            -1
#define CAM_PIN_RESET           -1
#define CAM_PIN_XCLK            10
#define CAM_PIN_SIOD            40      // SDA (SCCB)
#define CAM_PIN_SIOC            39      // SCL (SCCB)

#define CAM_PIN_D7              48      // Y9
#define CAM_PIN_D6              11      // Y8
#define CAM_PIN_D5              12      // Y7
#define CAM_PIN_D4              14      // Y6
#define CAM_PIN_D3              16      // Y5
#define CAM_PIN_D2              18      // Y4
#define CAM_PIN_D1              17      // Y3
#define CAM_PIN_D0              15      // Y2

#define CAM_PIN_VSYNC           38
#define CAM_PIN_HREF            47
#define CAM_PIN_PCLK            13

