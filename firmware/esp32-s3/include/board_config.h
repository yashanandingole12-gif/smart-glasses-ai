#pragma once

// =============================================================================
// Smart Glasses ESP32-S3 Hardware Board Pin Configuration
// All pins are configurable and adapt to the specific glasses board layout.
// =============================================================================

// Push-to-talk Physical Button
#define PIN_BUTTON_PTT          0       // Active LOW with internal pull-up (or GPIO 47 / 0)
#define BUTTON_DEBOUNCE_MS      35
#define BUTTON_LONG_PRESS_MS    1000

// Status Indicator LED
#define PIN_LED_STATUS          2       // Status LED or WS2812 RGB LED

// Battery Monitoring (ADC)
#define PIN_BATTERY_ADC         1       // Analog voltage divider pin
#define BATTERY_ADC_R1          100000.0f
#define BATTERY_ADC_R2          100000.0f

// I2S Microphone Pinout (Configurable for INMP441 / SPH0645)
#define I2S_MIC_PORT            I2S_NUM_0
#define I2S_MIC_BCLK            41
#define I2S_MIC_LRCLK           42
#define I2S_MIC_DATA            40
#define I2S_MIC_SAMPLE_RATE     16000

// I2S Speaker / DAC Pinout (Configurable for MAX98357A)
#define I2S_SPK_PORT            I2S_NUM_1
#define I2S_SPK_BCLK            15
#define I2S_SPK_LRCLK           16
#define I2S_SPK_DATA            17
#define I2S_SPK_SAMPLE_RATE     16000

// Camera Bus Pinout (Configurable for OV2640 / OV5640 modules)
#define CAM_PIN_PWDN            -1
#define CAM_PIN_RESET           -1
#define CAM_PIN_XCLK            10
#define CAM_PIN_SIOD            21
#define CAM_PIN_SIOC            14

#define CAM_PIN_D7              11
#define CAM_PIN_D6              9
#define CAM_PIN_D5              8
#define CAM_PIN_D4              6
#define CAM_PIN_D3              4
#define CAM_PIN_D2              5
#define CAM_PIN_D1              3
#define CAM_PIN_D0              46

#define CAM_PIN_VSYNC           13
#define CAM_PIN_HREF            12
#define CAM_PIN_PCLK            7
