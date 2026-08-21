package com.smartglasses.ai.device

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow

class SimulatedGlassesDevice : GlassesDevice {
    private val _connectionState = MutableStateFlow(DeviceConnectionState.DISCONNECTED)
    override val connectionState: StateFlow<DeviceConnectionState> = _connectionState.asStateFlow()

    private val _batteryPercentage = MutableStateFlow(85)
    override val batteryPercentage: StateFlow<Int> = _batteryPercentage.asStateFlow()

    private val _events = MutableSharedFlow<Pair<DeviceEvent, Map<String, Any>>>()
    override val events: Flow<Pair<DeviceEvent, Map<String, Any>>> = _events.asSharedFlow()

    override suspend fun connect(): Boolean {
        _connectionState.value = DeviceConnectionState.CONNECTED_SIMULATED
        _events.emit(Pair(DeviceEvent.DEVICE_CONNECTED, mapOf("type" to "SIMULATED")))
        return true
    }

    override suspend fun disconnect() {
        _connectionState.value = DeviceConnectionState.DISCONNECTED
        _events.emit(Pair(DeviceEvent.DEVICE_DISCONNECTED, emptyMap()))
    }

    override suspend fun sendCommand(command: DeviceCommand, payload: Map<String, Any>): Boolean {
        return true
    }

    suspend fun simulateButtonPress() {
        _events.emit(Pair(DeviceEvent.BUTTON_PRESSED, emptyMap()))
    }
}
