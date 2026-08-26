package com.smartglasses.ai.presentation.home

import com.smartglasses.ai.core.bluetooth.DeviceConnectionState
import com.smartglasses.ai.domain.models.AssistantState
import com.smartglasses.ai.domain.models.ChatMessage
import com.smartglasses.ai.domain.models.IntegrationState
import com.smartglasses.ai.domain.models.WearableResponse

data class WearableHomeState(
    val assistantState: AssistantState = AssistantState.IDLE,
    val latestSpeech: String = "Ready on your smart glasses. Tap TALK or type below.",
    val partialVoiceTranscript: String = "",
    val deviceConnectionState: DeviceConnectionState = DeviceConnectionState.CONNECTED_SIMULATED,
    val batteryPercentage: Int = 85,
    val isCharging: Boolean = false,
    val aiConnected: Boolean = false,
    val llmConnected: Boolean = false,
    val googleConnected: Boolean = false,
    val googleEmail: String? = null,
    val locationAvailable: Boolean = false,
    val locationName: String = "Unavailable",
    val latitude: Double? = null,
    val longitude: Double? = null,
    val isMicrophoneReady: Boolean = false,
    val isTtsReady: Boolean = false,
    val currentTime: String = "08:15 AM",
    val period: String = "morning",
    val gmailStatus: IntegrationState = IntegrationState.DISCONNECTED,
    val calendarStatus: IntegrationState = IntegrationState.DISCONNECTED,
    val smsStatus: IntegrationState = IntegrationState.READY,
    val messages: List<ChatMessage> = listOf(
        ChatMessage(sender = "ASSISTANT", text = "Ready on your smart glasses. Tap TALK or type below.")
    ),
    val textInput: String = "",
    val isSendingText: Boolean = false,
    val lastResponseLatencyMs: Double? = null,
    val sttDurationMs: Long? = null,
    val ttsDurationMs: Long? = null,
    val pendingConfirmation: WearableResponse? = null,
    val isConfigDialogOpen: Boolean = false,
    val serverUrl: String = "http://192.168.243.120:8001/",
    val errorMessage: String? = null
)
