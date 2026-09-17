#pragma once

#include <Arduino.h>
#include <WiFi.h>

class WiFiManager {
public:
    static WiFiManager& getInstance() {
        static WiFiManager instance;
        return instance;
    }

    void init();
    bool connectToNetwork(const String& ssid, const String& password, uint32_t timeoutMs = 15000);
    void disconnect();
    bool isConnected() const;
    String getLocalIp() const;
    int getRssi() const;
    void update();

private:
    WiFiManager();
    bool _connected = false;
    bool _connecting = false;
    String _currentSsid = "";
    unsigned long _connectStartTime = 0;
    uint32_t _timeoutMs = 15000;
};
