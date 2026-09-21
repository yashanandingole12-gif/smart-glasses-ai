#pragma once

// =============================================================================
// Smart Glasses Seeed Studio XIAO ESP32-S3 Board Configuration
// Peripherals: INMP441 I2S Digital Mic + MAX98357A I2S DAC Speaker + PTT Button
// Standard XIAO ESP32-S3 (Non-Sense): All connections use the 14 standard front header pins (D0 - D10)
// =============================================================================

// --- Push-to-Talk (PTT) Physical Buttons ---
// 1. External Push Button: Connect between Pin D4 (GPIO 5) and GND
#define PIN_BUTTON_PTT          5       // D4 / GPIO 5 (External Push-To-Talk Button, Active LOW with INPUT_PULLUP)
// 2. Onboard BOOT Button: Built right on the XIAO ESP32-S3 PCB (GPIO 0)
#define PIN_BUTTON_BOOT         0       // GPIO 0 (Onboard BOOT Button as secondary/debug PTT, Active LOW)
#define BUTTON_DEBOUNCE_MS      35      // Milliseconds debounce window
#define BUTTON_LONG_PRESS_MS    900     // Hold duration for voice wake session trigger

// --- Status Indicator LED ---
#define PIN_LED_STATUS          21      // Onboard User LED (Active LOW: LOW=ON, HIGH=OFF)

// --- Battery Monitoring (ADC) ---
#define PIN_BATTERY_ADC         -1      // Disabled (-1) to avoid pin conflict with I2S_SPK_DATA (GPIO 1 / D0)
#define BATTERY_ADC_R1          100000.0f
#define BATTERY_ADC_R2          100000.0f

// --- INMP441 I2S Digital Microphone (I2S Port 0 RX - Full Duplex) ---
// Wiring to XIAO ESP32-S3 Header Pins:
//   - INMP441 SCK/BCLK (Bit Clock)       -> XIAO D8  (GPIO 7)
//   - INMP441 WS/LRCL  (Word Select)     -> XIAO D3  (GPIO 4)
//   - INMP441 SD/DOUT  (Serial Data Out) -> XIAO D10 (GPIO 9)
//   - INMP441 VDD                        -> 3.3V (XIAO 3V3 Pin)
//   - INMP441 GND                        -> GND  (XIAO GND Pin)
//   - INMP441 L/R                        -> GND  (Left Channel Audio)
#define I2S_MIC_PORT            I2S_NUM_0
#define I2S_MIC_BCLK            7       // D8  / GPIO 7 (SCK)
#define I2S_MIC_LRCLK           4       // D3  / GPIO 4 (WS)
#define I2S_MIC_DATA            9       // D10 / GPIO 9 (SD)
#define I2S_MIC_SAMPLE_RATE     16000   // 16kHz standard audio capture

// --- MAX98357A I2S Class-D Amplifier / Speaker (I2S Port 1 TX - Full Duplex) ---
// Wiring to XIAO ESP32-S3 Header Pins:
//   - MAX98357A DIN    (Data In)         -> XIAO D0  (GPIO 1)
//   - MAX98357A BCLK   (Bit Clock)       -> XIAO D1  (GPIO 2)
//   - MAX98357A LRC/WS (Left/Right)      -> XIAO D2  (GPIO 3)
//   - MAX98357A VIN                      -> 5V   (XIAO 5V / VBUS Pin for max loudness & clarity) or 3V3
//   - MAX98357A GND                      -> GND  (XIAO GND Pin)
//   - MAX98357A GAIN                     -> GND  (12dB gain) or Open (9dB gain)
//   - MAX98357A SD/EN                    -> Open or pulled high to 3V3
#define I2S_SPK_PORT            I2S_NUM_1
#define I2S_SPK_DATA            1       // D0 / GPIO 1 (DIN)
#define I2S_SPK_BCLK            2       // D1 / GPIO 2 (BCLK)
#define I2S_SPK_LRCLK           3       // D2 / GPIO 3 (LRC)
#define I2S_SPK_SAMPLE_RATE     16000   // 16kHz default sample rate (supports 8kHz - 48kHz)

// --- Optional Mini I2C OLED Display (0.96" / 0.42" / 0.91" SSD1306) ---
#define OLED_PIN_SDA            43      // D6 / GPIO 43
#define OLED_PIN_SCL            6       // D5 / GPIO 6
#define OLED_I2C_ADDR           0x3C    // Standard I2C Address
#define OLED_SCREEN_WIDTH       128
#define OLED_SCREEN_HEIGHT      64
#define OLED_RESET_PIN          -1

// --- Camera Hardware Pins (On Hold in Pure Audio/PTT Mode) ---
#define CAM_PIN_PWDN            -1
#define CAM_PIN_RESET           -1
#define CAM_PIN_XCLK            -1
#define CAM_PIN_SIOD            -1
#define CAM_PIN_SIOC            -1
#define CAM_PIN_D7              -1
#define CAM_PIN_D6              -1
#define CAM_PIN_D5              -1
#define CAM_PIN_D4              -1
#define CAM_PIN_D3              -1
#define CAM_PIN_D2              -1
#define CAM_PIN_D1              -1
#define CAM_PIN_D0              -1
#define CAM_PIN_VSYNC           -1
#define CAM_PIN_HREF            -1
#define CAM_PIN_PCLK            -1
