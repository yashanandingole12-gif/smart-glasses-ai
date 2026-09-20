package com.smartglasses.ai.core.gateway

import android.content.Context
import com.smartglasses.ai.core.bluetooth.BleManager
import com.smartglasses.ai.core.bluetooth.DeviceConnectionState
import com.smartglasses.ai.core.context.GlassesContext
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class RealGlassesGateway(
    private val context: Context,
    private val bleManager: BleManager = BleManager.getInstance(context)
) : GlassesGateway {

    private val scope = CoroutineScope(Dispatchers.Default)
    private val _isConnected = MutableStateFlow(false)
    override val isConnected: StateFlow<Boolean> = _isConnected.asStateFlow()

    private val _glassesContext = MutableStateFlow(GlassesContext())
    override val glassesContext: StateFlow<GlassesContext> = _glassesContext.asStateFlow()

    override val batteryLevel: StateFlow<Int> = bleManager.batteryLevel
    override val isAvailable: Boolean
        get() = bleManager.isBleHardwareAvailable()

    init {
        scope.launch {
            bleManager.connectionState.collect { state ->
                val connected = (state == DeviceConnectionState.CONNECTED_ESP32 || state == DeviceConnectionState.CONNECTED_SIMULATED)
                _isConnected.value = connected
                _glassesContext.value = _glassesContext.value.copy(
                    isConnected = connected,
                    battery = bleManager.batteryLevel.value,
                    rssi = bleManager.rssiLevel.value,
                    cameraReady = connected,
                    micReady = connected
                )
            }
        }
    }

    override fun connect() {
        bleManager.startScan()
    }

    override fun disconnect() {
        bleManager.disconnect()
    }

    override fun startListening() {
        // Trigger glasses hardware mic or state if needed
    }

    override fun stopListening() {
        // Stop glasses hardware mic state
    }

    override fun captureImage(onImageCaptured: (String?) -> Unit) {
        val sent = bleManager.requestPhotoCapture()
        if (!sent) {
            onImageCaptured(null)
        }
    }

    override fun sendCommand(command: String): Boolean {
        return bleManager.sendCommand(command)
    }

    override fun sendWifiCredentials(ssid: String, pass: String): Boolean {
        return bleManager.sendWifiCredentials(ssid, pass)
    }
}
