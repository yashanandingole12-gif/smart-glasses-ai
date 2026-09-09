#include "button_manager.h"

ButtonManager::ButtonManager() {}

void ButtonManager::init(uint8_t pin) {
    _pin = pin;
    pinMode(_pin, INPUT_PULLUP);
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
    int reading = digitalRead(_pin);

    if (reading != _lastState) {
        _lastDebounceTime = millis();
    }

    if ((millis() - _lastDebounceTime) > BUTTON_DEBOUNCE_MS) {
        if (reading != _stableState) {
            _stableState = reading;

            if (_stableState == LOW) {
                // Button just pressed down (Push-to-Talk Start)
                _isPressed = true;
                _pressStartTime = millis();
                _longPressTriggered = false;
                if (_onPressStartCallback) {
                    _onPressStartCallback();
                }
            } else {
                // Button released (Push-to-Talk Stop)
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
