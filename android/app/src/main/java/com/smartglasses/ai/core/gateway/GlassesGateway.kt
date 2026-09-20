package com.smartglasses.ai.core.gateway

import com.smartglasses.ai.core.context.GlassesContext
import kotlinx.coroutines.flow.StateFlow

interface GlassesGateway {
    val isAvailable: Boolean
    val isConnected: StateFlow<Boolean>
    val batteryLevel: StateFlow<Int>
    val glassesContext: StateFlow<GlassesContext>

    fun connect()
    fun disconnect()
    fun startListening()
    fun stopListening()
    fun captureImage(onImageCaptured: (String?) -> Unit)
    fun sendCommand(command: String): Boolean
    fun sendWifiCredentials(ssid: String, pass: String): Boolean
}
