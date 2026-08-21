#pragma once

#include <Arduino.h>
#include "ble_manager.h"
#include "button_manager.h"
#include "battery_manager.h"
#include "camera_manager.h"
#include "audio_manager.h"

class DeviceManager {
public:
    static DeviceManager& getInstance() {
        static DeviceManager instance;
        return instance;
    }

    void init();
    void update();

private:
    DeviceManager();
    unsigned long _lastBatteryReportTime = 0;
    void handleIncomingCommand(const String& cmdJson);
};
