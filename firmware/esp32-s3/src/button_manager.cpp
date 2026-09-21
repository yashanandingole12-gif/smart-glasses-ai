#include "button_manager.h"

ButtonManager::ButtonManager() {}

void ButtonManager::init(uint8_t pin) {
    _pin = pin;
    pinMode(_pin, INPUT_PULLUP);
    delay(20);

    int readVal = digitalRead(_pin);
    _lastState = HIGH;
    _stableState = HIGH;
    _isPressed = false;
    _lastDebounceTime = millis();

    Serial.printf("[BUTTON] Initialized PTT Push Button on Pin D%d (GPIO %d) -> State: %s\n",
                  _pin == 5 ? 4 : _pin, _pin,
                  readVal == LOW ? "LOW (CLOSED/PRESSED)" : "HIGH (OPEN/READY)");

    if (readVal == LOW) {
        Serial.println("[BUTTON WARNING] Pin D4 is LOW at boot! Ensure your 4-pin switch uses diagonal pins.");
    }
}

void ButtonManager::setOnPressStartCallback(std::function<void()> cb) {
    _onPressStartCallback = cb;
}

void ButtonManager::setOnReleaseCallback(std::function<void()> cb) {
    _onReleaseCallback = cb;
}

void ButtonManager::setOnPressCallback(std::function<void()> cb) {
    _onPressCallback = cb;
}

void ButtonManager::setOnLongPressCallback(std::function<void()> cb) {
    _onLongPressCallback = cb;
}

void ButtonManager::update() {
    int currentReading = digitalRead(_pin);

    if (currentReading != _lastState) {
        _lastDebounceTime = millis();
    }

    if ((millis() - _lastDebounceTime) > BUTTON_DEBOUNCE_MS) {
        if (currentReading != _stableState) {
            _stableState = currentReading;

            if (_stableState == LOW) {
                // Button transition: HIGH -> LOW (User pressed down button)
                _isPressed = true;
                _pressStartTime = millis();
                _longPressTriggered = false;
                Serial.println();
                Serial.println("==================================================");
                Serial.println("[BUTTON] >>> PUSH-TO-TALK PRESSED (Pin D4 -> LOW)");
                Serial.println("[BUTTON] >>> Starting INMP441 recording & sending TALK_START to Phone");
                Serial.println("==================================================");
                if (_onPressStartCallback) {
                    _onPressStartCallback();
                }
            } else {
                // Button transition: LOW -> HIGH (User released button)
                Serial.println();
                Serial.println("==================================================");
                Serial.println("[BUTTON] <<< PUSH-TO-TALK RELEASED (Pin D4 -> HIGH)");
                Serial.println("[BUTTON] <<< Stopping recording & sending TALK_STOP to Phone");
                Serial.println("==================================================");
                if (_onReleaseCallback) {
                    _onReleaseCallback();
                }
                if (_isPressed && !_longPressTriggered) {
                    if (_onPressCallback) {
                        _onPressCallback();
                    }
                }
                _isPressed = false;
            }
        }
    }

    // Long press check
    if (_isPressed && !_longPressTriggered) {
        if ((millis() - _pressStartTime) >= BUTTON_LONG_PRESS_MS) {
            _longPressTriggered = true;
            Serial.println("[BUTTON] >>> LONG PRESS DETECTED (Held > 900ms)");
            if (_onLongPressCallback) {
                _onLongPressCallback();
            }
        }
    }

    _lastState = currentReading;
}
