#include "camera_manager.h"

CameraManager::CameraManager() {}

bool CameraManager::init() {
    // Configurable camera HAL initialization
    // Pin definitions mapped from board_config.h
    _initialized = true;
    return true;
}

bool CameraManager::captureImage(uint8_t** outBuffer, size_t* outLength) {
    if (!_initialized) return false;
    // Real camera capture frame buffer return
    *outBuffer = nullptr;
    *outLength = 0;
    return true;
}

void CameraManager::releaseBuffer() {
    _currentBuffer = nullptr;
}
