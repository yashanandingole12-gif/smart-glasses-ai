#include "button_manager.h"

ButtonManager::ButtonManager() {}

void ButtonManager::init(uint8_t pin) {
    _pin = pin;
    pinMode(_pin, INPUT_PULLUP);
}

void ButtonManager::setOnPressCallback(std::function<void()> cb) {
    _onPressCallback = cb;
}

void ButtonManager::setOnLongPressCallback(std::function<void()> cb) {
    _onLongPressCallback = cb;
}

void ButtonManager::update() {
    int reading = digitalRead(_pin);

    if (reading != _lastState) {
        _lastDebounceTime = millis();
    }

    if ((millis() - _lastDebounceTime) > BUTTON_DEBOUNCE_MS) {
        if (reading != _stableState) {
            _stableState = reading;

            if (_stableState == LOW) {
                // Button just pressed down
                _isPressed = true;
                _pressStartTime = millis();
                _longPressTriggered = false;
            } else {
                // Button released
                if (_isPressed && !_longPressTriggered) {
                    if (_onPressCallback) {
                        _onPressCallback();
                    }
                }
                _isPressed = false;
            }
        }
    }

    // Check for long press while held
    if (_isPressed && !_longPressTriggered) {
        if ((millis() - _pressStartTime) >= BUTTON_LONG_PRESS_MS) {
            _longPressTriggered = true;
            if (_onLongPressCallback) {
                _onLongPressCallback();
            }
        }
    }

    _lastState = reading;
}
