#pragma once

#include <Arduino.h>
#include "board_config.h"

class BatteryManager {
public:
    static BatteryManager& getInstance() {
        static BatteryManager instance;
        return instance;
    }

    void init(uint8_t pin = PIN_BATTERY_ADC);
    uint8_t getBatteryPercentage();
    float getBatteryVoltage();

private:
    BatteryManager();
    uint8_t _pin = PIN_BATTERY_ADC;
};
