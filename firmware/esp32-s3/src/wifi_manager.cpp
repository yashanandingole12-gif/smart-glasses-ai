#include "wifi_manager.h"
#include "ble_manager.h"

WiFiManager::WiFiManager() {}

void WiFiManager::init() {
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    Serial.println("[WIFI] WiFi Subsystem initialized in Station (STA) mode.");
}

bool WiFiManager::connectToNetwork(const String& ssid, const String& password, uint32_t timeoutMs) {
    if (ssid.length() == 0) return false;
    
    Serial.println();
    Serial.println("==================================================");
    Serial.printf("[WIFI] Initiating Non-blocking Connection to SSID: '%s'...\n", ssid.c_str());
    Serial.println("==================================================");

    WiFi.disconnect(true);
    delay(20);
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid.c_str(), password.c_str());

    _connecting = true;
    _connected = false;
    _currentSsid = ssid;
    _connectStartTime = millis();
    _timeoutMs = timeoutMs;
    return true;
}

void WiFiManager::disconnect() {
    WiFi.disconnect(true);
    _connected = false;
    _connecting = false;
    _currentSsid = "";
    Serial.println("[WIFI] Disconnected from WiFi network.");
    BleManager::getInstance().sendEvent("WIFI_STATUS", "{\"connected\":false}");
}

bool WiFiManager::isConnected() const {
    return WiFi.status() == WL_CONNECTED;
}

String WiFiManager::getLocalIp() const {
    if (WiFi.status() == WL_CONNECTED) {
        return WiFi.localIP().toString();
    }
    return "0.0.0.0";
}

int WiFiManager::getRssi() const {
    if (WiFi.status() == WL_CONNECTED) {
        return WiFi.RSSI();
    }
    return 0;
}

void WiFiManager::update() {
    // 1. Asynchronous non-blocking connection handler
    if (_connecting) {
        if (WiFi.status() == WL_CONNECTED) {
            _connected = true;
            _connecting = false;
            String ip = WiFi.localIP().toString();
            int rssi = WiFi.RSSI();
            Serial.printf("[WIFI] Connected successfully in background!\n");
            Serial.printf("[WIFI] IP Address: %s | RSSI: %d dBm | Gateway: %s\n", 
                          ip.c_str(), rssi, WiFi.gatewayIP().toString().c_str());

            // Notify companion app over BLE without freezing connection
            String statusJson = "{\"connected\":true,\"ip\":\"" + ip + "\",\"ssid\":\"" + _currentSsid + "\",\"rssi\":" + String(rssi) + "}";
            BleManager::getInstance().sendEvent("WIFI_STATUS", statusJson);
        } else if (millis() - _connectStartTime > _timeoutMs) {
            _connecting = false;
            _connected = false;
            Serial.printf("[WIFI] Connection attempt to '%s' timed out (Status: %d)\n", _currentSsid.c_str(), WiFi.status());
            String statusJson = "{\"connected\":false,\"ssid\":\"" + _currentSsid + "\",\"error\":\"TIMEOUT_OR_AUTH_FAILURE\"}";
            BleManager::getInstance().sendEvent("WIFI_STATUS", statusJson);
        }
    }

    // 2. Monitor ongoing connection health
    if (_connected && WiFi.status() != WL_CONNECTED && !_connecting) {
        _connected = false;
        Serial.println("[WIFI] WARNING: Lost connection to WiFi network.");
        BleManager::getInstance().sendEvent("WIFI_STATUS", "{\"connected\":false,\"error\":\"CONNECTION_LOST\"}");
    }
}
