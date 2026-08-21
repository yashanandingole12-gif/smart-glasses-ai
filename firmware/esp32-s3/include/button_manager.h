#pragma once

#include <Arduino.h>
#include <functional>
#include "board_config.h"

class ButtonManager {
public:
    static ButtonManager& getInstance() {
        static ButtonManager instance;
        return instance;
    }

    void init(uint8_t pin = PIN_BUTTON_PTT);
    void update();
    void setOnPressCallback(std::function<void()> cb);
    void setOnLongPressCallback(std::function<void()> cb);

private:
    ButtonManager();
    uint8_t _pin = PIN_BUTTON_PTT;
    int _lastState = HIGH;
    int _stableState = HIGH;
    unsigned long _lastDebounceTime = 0;
    unsigned long _pressStartTime = 0;
    bool _isPressed = false;
    bool _longPressTriggered = false;

    std::function<void()> _onPressCallback = nullptr;
    std::function<void()> _onLongPressCallback = nullptr;
};
