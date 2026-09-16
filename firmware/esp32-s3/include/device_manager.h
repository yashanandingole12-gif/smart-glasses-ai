#pragma once

#include <Arduino.h>
#include "board_config.h"
#include "ble_manager.h"
#include "button_manager.h"
#include "battery_manager.h"
#include "camera_manager.h"
#include "audio_manager.h"

// Default inactivity timeout before entering deep sleep (25 minutes)
#define INACTIVITY_SLEEP_TIMEOUT_MS  (25UL * 60UL * 1000UL)

class DeviceManager {
public:
    static DeviceManager& getInstance() {
        static DeviceManager instance;
        return instance;
    }

    void init();
    void update();
    void resetActivity();
    void enterDeepSleep(const char* reason = "Inactivity Timeout");

private:
    DeviceManager();
    bool _wasConnected = false;
    unsigned long _lastBatteryReportTime = 0;
    unsigned long _lastActivityTime = 0;
    void handleIncomingCommand(const String& cmdJson);
};

