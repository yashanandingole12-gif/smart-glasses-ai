package com.smartglasses.ai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.*
import com.smartglasses.ai.device.DeviceConnectionState
import com.smartglasses.ai.device.SimulatedGlassesDevice
import com.smartglasses.ai.ui.ChatMessage
import com.smartglasses.ai.ui.GlassesMainScreen
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    private val simulatedDevice = SimulatedGlassesDevice()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val scope = rememberCoroutineScope()
            var connectionState by remember { mutableStateOf(DeviceConnectionState.CONNECTED_SIMULATED) }
            val battery by simulatedDevice.batteryPercentage.collectAsState()
            val messages = remember {
                mutableStateListOf(
                    ChatMessage("ASSISTANT", "Smart Glasses ready. Tap TALK or press glasses button.")
                )
            }

            GlassesMainScreen(
                connectionState = connectionState,
                battery = battery,
                currentTime = "08:15 AM",
                currentLocation = "Nagpur",
                messages = messages,
                onTalkClicked = {
                    scope.launch {
                        messages.add(ChatMessage("USER", "Good morning."))
                        // Simulates round trip to backend
                        messages.add(ChatMessage("ASSISTANT", "Good morning. It's 8:15 AM and you're in Nagpur. You have class at 10:30. How can I help?"))
                    }
                },
                onToggleConnection = {
                    connectionState = if (connectionState == DeviceConnectionState.CONNECTED_SIMULATED) {
                        DeviceConnectionState.CONNECTED_ESP32
                    } else {
                        DeviceConnectionState.CONNECTED_SIMULATED
                    }
                }
            )
        }
    }
}
