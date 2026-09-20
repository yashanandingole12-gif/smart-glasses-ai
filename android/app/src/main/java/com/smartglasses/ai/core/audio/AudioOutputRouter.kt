package com.smartglasses.ai.core.audio

import android.content.Context
import android.media.AudioDeviceCallback
import android.media.AudioDeviceInfo
import android.media.AudioManager
import android.os.Build
import android.util.Log
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

enum class AudioRoute {
    TWS_BLUETOOTH,
    PHONE_SPEAKER,
    WIRED_HEADPHONES
}

/**
 * Authoritative Audio Output Router for EVA.
 * Manages dynamic routing to TWS Earbuds / Bluetooth Headsets with zero-latency
 * fallback to Phone Speaker on disconnect, and automatic TWS restoration on reconnect.
 */
class AudioOutputRouter(private val context: Context) {
    companion object {
        private const val TAG = "EVA.AudioRouter"
    }

    private val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as? AudioManager

    private val _currentRoute = MutableStateFlow(AudioRoute.PHONE_SPEAKER)
    val currentRoute: StateFlow<AudioRoute> = _currentRoute.asStateFlow()

    private var audioDeviceCallback: AudioDeviceCallback? = null

    init {
        updateActiveRoute()
        registerDeviceCallbacks()
    }

    private fun registerDeviceCallbacks() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && audioManager != null) {
            audioDeviceCallback = object : AudioDeviceCallback() {
                override fun onAudioDevicesAdded(addedDevices: Array<out AudioDeviceInfo>?) {
                    Log.i(TAG, "Audio device connected -> Evaluating routing")
                    updateActiveRoute()
                }

                override fun onAudioDevicesRemoved(removedDevices: Array<out AudioDeviceInfo>?) {
                    Log.i(TAG, "Audio device disconnected -> Falling back to Phone Speaker")
                    updateActiveRoute()
                }
            }
            audioManager.registerAudioDeviceCallback(audioDeviceCallback, null)
        }
    }

    fun getActiveOutputRoute(): AudioRoute {
        updateActiveRoute()
        return _currentRoute.value
    }

    private fun updateActiveRoute() {
        if (audioManager == null) {
            _currentRoute.value = AudioRoute.PHONE_SPEAKER
            return
        }

        val newRoute = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val devices = audioManager.getDevices(AudioManager.GET_DEVICES_OUTPUTS)
            when {
                devices.any {
                    it.type == AudioDeviceInfo.TYPE_BLE_HEADSET ||
                    it.type == AudioDeviceInfo.TYPE_BLUETOOTH_A2DP ||
                    it.type == AudioDeviceInfo.TYPE_BLUETOOTH_SCO
                } -> AudioRoute.TWS_BLUETOOTH
                devices.any {
                    it.type == AudioDeviceInfo.TYPE_WIRED_HEADSET ||
                    it.type == AudioDeviceInfo.TYPE_WIRED_HEADPHONES
                } -> AudioRoute.WIRED_HEADPHONES
                else -> AudioRoute.PHONE_SPEAKER
            }
        } else {
            if (audioManager.isBluetoothA2dpOn || audioManager.isBluetoothScoOn) {
                AudioRoute.TWS_BLUETOOTH
            } else if (audioManager.isWiredHeadsetOn) {
                AudioRoute.WIRED_HEADPHONES
            } else {
                AudioRoute.PHONE_SPEAKER
            }
        }

        if (_currentRoute.value != newRoute) {
            Log.i(TAG, "Active audio route transitioned: ${_currentRoute.value} -> $newRoute")
            _currentRoute.value = newRoute
        }
    }

    fun optimizeForVoicePlayback() {
        try {
            audioManager?.mode = AudioManager.MODE_NORMAL
            updateActiveRoute()
            Log.d(TAG, "Audio output route optimized: ${_currentRoute.value}")
        } catch (e: Exception) {
            Log.w(TAG, "Notice optimizing audio output: ${e.message}")
        }
    }

    fun cleanup() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && audioManager != null && audioDeviceCallback != null) {
            try {
                audioManager.unregisterAudioDeviceCallback(audioDeviceCallback)
            } catch (e: Exception) {
                Log.w(TAG, "Notice unregistering audio callbacks: ${e.message}")
            }
        }
    }
}
