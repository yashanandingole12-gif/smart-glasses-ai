#pragma once

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "board_config.h"

class OledManager {
public:
    static OledManager& getInstance() {
        static OledManager instance;
        return instance;
    }

    bool init();
    void showWelcomeScreen(uint8_t battery = 85);
    void showStatus(const String& header, const String& sub1 = "", const String& sub2 = "");
    void showNotification(const String& sender, const String& preview);
    void showAiResponse(const String& query, const String& response);
    void showCustomText(const String& line1, const String& line2 = "", const String& line3 = "");
    void showCalling(const String& contactName);
    void showListening();
    void showThinking();
    void clear();
    void runDiagnostics();
    bool isInitialized() const;

private:
    OledManager();
    Adafruit_SSD1306 _display;
    bool _initialized = false;
    unsigned long _lastScreenUpdate = 0;
};
