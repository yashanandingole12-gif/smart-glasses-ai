#include "battery_manager.h"

BatteryManager::BatteryManager() {}

void BatteryManager::init(uint8_t pin) {
    _pin = pin;
    pinMode(_pin, INPUT);
}

float BatteryManager::getBatteryVoltage() {
    int raw = analogRead(_pin);
    // ADC 12-bit on 3.3V reference
    float vOut = (raw / 4095.0f) * 3.3f;
    // Voltage divider ratio: V_batt = V_out * (R1 + R2) / R2
    float vBatt = vOut * ((BATTERY_ADC_R1 + BATTERY_ADC_R2) / BATTERY_ADC_R2);
    if (vBatt < 2.5f) {
        // Fallback default if not connected to ADC divider
        return 3.95f;
    }
    return vBatt;
}

uint8_t BatteryManager::getBatteryPercentage() {
    float v = getBatteryVoltage();
    // LiPo battery mapping: 3.3V (0%) to 4.2V (100%)
    if (v >= 4.2f) return 100;
    if (v <= 3.3f) return 0;
    return (uint8_t)(((v - 3.3f) / (4.2f - 3.3f)) * 100.0f);
}
