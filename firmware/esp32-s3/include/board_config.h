#pragma once

// =============================================================================
// Smart Glasses Seeed Studio XIAO ESP32-S3 Pin Configuration
// Uses external INMP441 I2S Digital Mic & MAX98357A I2S DAC Speaker
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

// INMP441 I2S Digital Microphone Pinout:
//   - INMP441 SCK / BCLK -> XIAO D8  (GPIO 7)
//   - INMP441 WS / LRCL  -> XIAO D3  (GPIO 4)
//   - INMP441 SD / DOUT  -> XIAO D10 (GPIO 9)
//   - INMP441 VDD        -> 3.3V
//   - INMP441 GND        -> GND
//   - INMP441 L/R        -> GND (Left Channel)
#define I2S_MIC_PORT            I2S_NUM_0
#define I2S_MIC_BCLK            7       // D8 / GPIO 7 (Bit Clock / SCK)
#define I2S_MIC_LRCLK           4       // D3 / GPIO 4 (Word Select / WS / LRCL)
#define I2S_MIC_DATA            9       // D10 / GPIO 9 (Serial Data / SD / DOUT)
#define I2S_MIC_SAMPLE_RATE     16000   // 16kHz sample rate

// External I2S Speaker / DAC Pinout (MAX98357A / Bone Conduction Transducer Amp)
// Wiring to XIAO ESP32-S3:
//   - MAX98357A DIN      -> XIAO D11 (GPIO 38)
//   - MAX98357A BCLK     -> XIAO D12 (GPIO 39)
//   - MAX98357A LRC / WS -> XIAO D13 (GPIO 40)
//   - MAX98357A VIN      -> 3.3V
//   - MAX98357A GND      -> GND
//   - MAX98357A GAIN     -> GND (12dB gain) or open (9dB)
//   - MAX98357A SD_MODE  -> Open or pull-up to VIN (Stereo / Left / Right)
#define I2S_SPK_PORT            I2S_NUM_1
#define I2S_SPK_DATA            38      // D11 / GPIO 38 (Data Out -> DAC DIN)
#define I2S_SPK_BCLK            39      // D12 / GPIO 39 (Bit Clock)
#define I2S_SPK_LRCLK           40      // D13 / GPIO 40 (Left/Right Clock / WS)
#define I2S_SPK_SAMPLE_RATE     16000   // 16kHz default sample rate (supports 8kHz - 48kHz)

// On-board Camera Pinout (Pins 38, 39, 40 reallocated for I2S DAC Audio Output)
#define CAM_PIN_PWDN            -1
#define CAM_PIN_RESET           -1
#define CAM_PIN_XCLK            10
#define CAM_PIN_SIOD            -1      // Reallocated
#define CAM_PIN_SIOC            -1      // Reallocated

#define CAM_PIN_D7              48      // Y9
#define CAM_PIN_D6              11      // Y8
#define CAM_PIN_D5              12      // Y7
#define CAM_PIN_D4              14      // Y6
#define CAM_PIN_D3              16      // Y5
#define CAM_PIN_D2              18      // Y4
#define CAM_PIN_D1              17      // Y3
#define CAM_PIN_D0              15      // Y2

#define CAM_PIN_VSYNC           -1      // Reallocated
#define CAM_PIN_HREF            47
#define CAM_PIN_PCLK            13

// Mini I2C OLED Display (0.96" / 0.42" / 0.91" SSD1306 / SH1106)
#define OLED_PIN_SDA            5       // D4 / GPIO 5
#define OLED_PIN_SCL            6       // D5 / GPIO 6
#define OLED_I2C_ADDR           0x3C    // Standard I2C Address (0x3C or 0x3D)
#define OLED_SCREEN_WIDTH       128
#define OLED_SCREEN_HEIGHT      64
#define OLED_RESET_PIN          -1      // Reset pin (-1 if sharing Arduino reset pin)

