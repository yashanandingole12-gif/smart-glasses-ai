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
    String _currentSsid = "";
    unsigned long _lastReconnectAttempt = 0;
};
