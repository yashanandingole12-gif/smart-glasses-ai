package com.smartglasses.ai.core.bluetooth

import android.annotation.SuppressLint
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import android.content.Context
import com.smartglasses.ai.core.permissions.PermissionManager
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow

enum class DeviceConnectionState {
    DISCONNECTED,
    CONNECTING,
    CONNECTED_SIMULATED,
    CONNECTED_ESP32
}

class BleManager(private val context: Context) {
    private val bluetoothManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager
    private val bluetoothAdapter: BluetoothAdapter? = bluetoothManager?.adapter

    private val _connectionState = MutableStateFlow(DeviceConnectionState.CONNECTED_SIMULATED)
    val connectionState: StateFlow<DeviceConnectionState> = _connectionState.asStateFlow()

    private val _batteryLevel = MutableStateFlow(72)
    val batteryLevel: StateFlow<Int> = _batteryLevel.asStateFlow()

    private val _buttonPressEvents = MutableSharedFlow<Unit>(extraBufferCapacity = 1)
    val buttonPressEvents: SharedFlow<Unit> = _buttonPressEvents.asSharedFlow()

    fun toggleConnectionMode() {
        _connectionState.value = when (_connectionState.value) {
            DeviceConnectionState.DISCONNECTED -> DeviceConnectionState.CONNECTED_SIMULATED
            DeviceConnectionState.CONNECTED_SIMULATED -> {
                if (isBleHardwareAvailable()) {
                    DeviceConnectionState.CONNECTED_ESP32
                } else {
                    DeviceConnectionState.DISCONNECTED
                }
            }
            DeviceConnectionState.CONNECTED_ESP32 -> DeviceConnectionState.DISCONNECTED
            DeviceConnectionState.CONNECTING -> DeviceConnectionState.DISCONNECTED
        }
    }

    fun isBleHardwareAvailable(): Boolean {
        return bluetoothAdapter != null && bluetoothAdapter.isEnabled && PermissionManager.hasBluetoothPermission(context)
    }

    fun simulateButtonPressed() {
        _buttonPressEvents.tryEmit(Unit)
    }

    fun setBatteryLevel(level: Int) {
        _batteryLevel.value = level.coerceIn(0, 100)
    }
}
