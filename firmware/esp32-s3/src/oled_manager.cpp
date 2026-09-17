#include "oled_manager.h"
#include "ble_manager.h"

OledManager::OledManager() : _display(OLED_SCREEN_WIDTH, OLED_SCREEN_HEIGHT, &Wire, OLED_RESET_PIN) {}

bool OledManager::init() {
    Serial.printf("[OLED] Initializing I2C bus on SDA=%d, SCL=%d...\n", OLED_PIN_SDA, OLED_PIN_SCL);
    Wire.begin(OLED_PIN_SDA, OLED_PIN_SCL, 400000);

    // Try primary I2C address 0x3C, fallback to 0x3D
    if (_display.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDR)) {
        _initialized = true;
    } else if (_display.begin(SSD1306_SWITCHCAPVCC, 0x3D)) {
        _initialized = true;
    } else {
        _initialized = false;
        Serial.println("[OLED] WARNING: SSD1306 OLED display not detected on I2C bus.");
        return false;
    }

    _display.clearDisplay();
    _display.setTextColor(SSD1306_WHITE);
    showWelcomeScreen(85);
    Serial.println("[OLED] SSD1306 128x64 Mini Display Initialized Successfully!");
    return true;
}

void OledManager::showWelcomeScreen(uint8_t battery) {
    if (!_initialized) return;
    _display.clearDisplay();
    
    // Top Title Bar
    _display.setTextSize(1);
    _display.setCursor(16, 2);
    _display.print("LARA SMART GLASS");
    _display.drawFastHLine(0, 12, 128, SSD1306_WHITE);

    // Centered Welcome
    _display.setTextSize(2);
    _display.setCursor(38, 20);
    _display.print("LARA");

    // Status Footer
    _display.setTextSize(1);
    _display.setCursor(4, 42);
    _display.printf("BLE: %s", BleManager::getInstance().isClientConnected() ? "CONNECTED" : "PAIRING");
    
    _display.setCursor(4, 54);
    _display.printf("BATT: %d%%  AI: READY", battery);

    // Battery bar frame
    _display.drawRect(102, 54, 22, 8, SSD1306_WHITE);
    uint8_t fillW = (battery * 18) / 100;
    _display.fillRect(104, 56, fillW, 4, SSD1306_WHITE);

    _display.display();
}

void OledManager::showStatus(const String& header, const String& sub1, const String& sub2) {
    if (!_initialized) return;
    _display.clearDisplay();

    // Header
    _display.setTextSize(1);
    _display.setCursor(0, 0);
    _display.print(header);
    _display.drawFastHLine(0, 10, 128, SSD1306_WHITE);

    // Sub 1
    if (sub1.length() > 0) {
        _display.setCursor(0, 16);
        _display.print(sub1);
    }

    // Sub 2
    if (sub2.length() > 0) {
        _display.setCursor(0, 32);
        _display.print(sub2);
    }

    _display.display();
}

void OledManager::showNotification(const String& sender, const String& preview) {
    if (!_initialized) return;
    _display.clearDisplay();

    // Top alert banner
    _display.fillRect(0, 0, 128, 12, SSD1306_WHITE);
    _display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
    _display.setTextSize(1);
    _display.setCursor(4, 2);
    _display.printf("MSG: %s", sender.c_str());

    // Message body with text wrap
    _display.setTextColor(SSD1306_WHITE);
    _display.setCursor(0, 16);
    _display.setTextWrap(true);
    _display.print(preview);

    _display.display();
}

void OledManager::showAiResponse(const String& query, const String& response) {
    if (!_initialized) return;
    _display.clearDisplay();

    // Top Header
    _display.setTextSize(1);
    _display.setCursor(0, 0);
    _display.print("LARA AI RESPONSE");
    _display.drawFastHLine(0, 10, 128, SSD1306_WHITE);

    // Body
    _display.setCursor(0, 14);
    _display.setTextWrap(true);
    _display.print(response);

    _display.display();
}

void OledManager::showCalling(const String& contactName) {
    if (!_initialized) return;
    _display.clearDisplay();

    _display.setTextSize(1);
    _display.setCursor(20, 4);
    _display.print("INCOMING CALL");
    _display.drawFastHLine(0, 14, 128, SSD1306_WHITE);

    _display.setTextSize(2);
    _display.setCursor(6, 24);
    _display.print(contactName);

    _display.setTextSize(1);
    _display.setCursor(12, 50);
    _display.print("Press PTT to Answer");

    _display.display();
}

void OledManager::showCustomText(const String& line1, const String& line2, const String& line3) {
    if (!_initialized) return;
    _display.clearDisplay();
    _display.setTextColor(SSD1306_WHITE);

    _display.setTextSize(1);
    _display.setCursor(0, 0);
    _display.print("LARA SMART GLASS");
    _display.drawFastHLine(0, 10, 128, SSD1306_WHITE);

    if (line1.length() > 0) {
        _display.setCursor(0, 16);
        _display.print(line1);
    }
    if (line2.length() > 0) {
        _display.setCursor(0, 32);
        _display.print(line2);
    }
    if (line3.length() > 0) {
        _display.setCursor(0, 48);
        _display.print(line3);
    }
    _display.display();
}

void OledManager::showListening() {
    if (!_initialized) return;
    _display.clearDisplay();
    _display.setTextColor(SSD1306_WHITE);

    _display.setTextSize(1);
    _display.setCursor(0, 0);
    _display.print("LARA SMART GLASS");
    _display.drawFastHLine(0, 10, 128, SSD1306_WHITE);

    _display.setTextSize(2);
    _display.setCursor(10, 22);
    _display.print("Listening");

    _display.setTextSize(1);
    _display.setCursor(18, 48);
    _display.print("Speak into glasses");

    _display.display();
}

void OledManager::showThinking() {
    if (!_initialized) return;
    _display.clearDisplay();
    _display.setTextColor(SSD1306_WHITE);

    _display.setTextSize(1);
    _display.setCursor(0, 0);
    _display.print("LARA SMART GLASS");
    _display.drawFastHLine(0, 10, 128, SSD1306_WHITE);

    _display.setTextSize(2);
    _display.setCursor(16, 22);
    _display.print("Thinking");

    _display.setTextSize(1);
    _display.setCursor(22, 48);
    _display.print("Generating reply");

    _display.display();
}

void OledManager::clear() {
    if (!_initialized) return;
    _display.clearDisplay();
    _display.display();
}

void OledManager::runDiagnostics() {
    if (!_initialized) {
        Serial.println("[OLED] Display not initialized.");
        return;
    }
    Serial.println("[OLED] Running Visual Diagnostic Sweep...");
    _display.clearDisplay();
    _display.setTextSize(1);
    _display.setCursor(10, 10);
    _display.print("DISPLAY TEST: OK");
    _display.drawRect(4, 4, 120, 56, SSD1306_WHITE);
    _display.drawCircle(64, 32, 14, SSD1306_WHITE);
    _display.display();
    delay(1000);
    showWelcomeScreen(100);
}

bool OledManager::isInitialized() const {
    return _initialized;
}
