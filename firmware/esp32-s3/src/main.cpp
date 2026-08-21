#include <Arduino.h>
#include "device_manager.h"

void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println("=========================================");
    Serial.println("Context-Aware Smart Glasses (ESP32-S3)");
    Serial.println("Firmware Version 0.1.0 Initialized");
    Serial.println("=========================================");

    DeviceManager::getInstance().init();
}

void loop() {
    DeviceManager::getInstance().update();
    delay(5);
}
