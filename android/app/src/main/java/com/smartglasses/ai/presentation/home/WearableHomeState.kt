package com.smartglasses.ai.presentation.home

import com.smartglasses.ai.core.bluetooth.DeviceConnectionState
import com.smartglasses.ai.domain.models.AssistantState
import com.smartglasses.ai.domain.models.ChatMessage
import com.smartglasses.ai.domain.models.IntegrationState
import com.smartglasses.ai.domain.models.WearableResponse

data class WearableHomeState(
    val assistantState: AssistantState = AssistantState.IDLE,
    val latestSpeech: String = "Good morning. You have class at 10:30.",
    val partialVoiceTranscript: String = "",
    val deviceConnectionState: DeviceConnectionState = DeviceConnectionState.CONNECTED_SIMULATED,
    val batteryPercentage: Int = 72,
    val aiConnected: Boolean = true,
    val locationAvailable: Boolean = true,
    val locationName: String = "Nagpur",
    val currentTime: String = "08:15 AM",
    val period: String = "morning",
    val gmailStatus: IntegrationState = IntegrationState.CONNECTED,
    val calendarStatus: IntegrationState = IntegrationState.CONNECTED,
    val smsStatus: IntegrationState = IntegrationState.READY,
    val messages: List<ChatMessage> = listOf(
        ChatMessage(sender = "ASSISTANT", text = "Good morning. You have class at 10:30.")
    ),
    val pendingConfirmation: WearableResponse? = null,
    val isConfigDialogOpen: Boolean = false,
    val serverUrl: String = "http://10.0.2.2:8001/",
    val errorMessage: String? = null
)
