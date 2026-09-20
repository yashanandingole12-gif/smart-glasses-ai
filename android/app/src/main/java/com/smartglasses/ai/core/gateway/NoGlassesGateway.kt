package com.smartglasses.ai.core.gateway

import com.smartglasses.ai.core.context.GlassesContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class NoGlassesGateway : GlassesGateway {
    override val isAvailable: Boolean = false
    override val isConnected: StateFlow<Boolean> = MutableStateFlow(false).asStateFlow()
    override val batteryLevel: StateFlow<Int> = MutableStateFlow(100).asStateFlow()
    override val glassesContext: StateFlow<GlassesContext> = MutableStateFlow(
        GlassesContext(
            isConnected = false,
            deviceName = "No Glasses",
            battery = 100,
            cameraReady = false,
            micReady = false
        )
    ).asStateFlow()

    override fun connect() {}
    override fun disconnect() {}
    override fun startListening() {}
    override fun stopListening() {}
    override fun captureImage(onImageCaptured: (String?) -> Unit) {
        onImageCaptured(null)
    }
    override fun sendCommand(command: String): Boolean = false
    override fun sendWifiCredentials(ssid: String, pass: String): Boolean = false
}
