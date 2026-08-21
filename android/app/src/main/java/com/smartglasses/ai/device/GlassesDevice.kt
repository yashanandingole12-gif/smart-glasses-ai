package com.smartglasses.ai.device

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.StateFlow

enum class DeviceEvent {
    BUTTON_PRESSED,
    BUTTON_LONG_PRESSED,
    CAMERA_READY,
    DEVICE_CONNECTED,
    DEVICE_DISCONNECTED,
    BATTERY_CHANGED
}

enum class DeviceCommand {
    START_LISTENING,
    STOP_LISTENING,
    CAPTURE_IMAGE,
    PLAY_AUDIO,
    STATUS_REQUEST
}

enum class DeviceConnectionState {
    DISCONNECTED,
    CONNECTING,
    CONNECTED_SIMULATED,
    CONNECTED_ESP32
}

interface GlassesDevice {
    val connectionState: StateFlow<DeviceConnectionState>
    val batteryPercentage: StateFlow<Int>
    val events: Flow<Pair<DeviceEvent, Map<String, Any>>>

    suspend fun connect(): Boolean
    suspend fun disconnect()
    suspend fun sendCommand(command: DeviceCommand, payload: Map<String, Any> = emptyMap()): Boolean
}
