package com.smartglasses.ai.domain.models

import java.util.UUID

enum class AssistantState {
    IDLE,
    LISTENING,
    PROCESSING,
    SPEAKING,
    ERROR
}

enum class IntegrationState {
    CONNECTED,
    DISCONNECTED,
    READY
}

data class ChatMessage(
    val id: String = UUID.randomUUID().toString(),
    val sender: String, // "USER" or "ASSISTANT"
    val text: String,
    val timestamp: Long = System.currentTimeMillis(),
    val requiresConfirmation: Boolean = false
)

data class WearableTelemetry(
    val glassesConnected: Boolean = true,
    val batteryPercentage: Int = 72,
    val aiConnected: Boolean = true,
    val locationAvailable: Boolean = true,
    val locationName: String = "Nagpur",
    val timeFormatted: String = "08:15 AM",
    val period: String = "morning"
)

data class WearableResponse(
    val text: String,
    val sessionId: String,
    val requiresConfirmation: Boolean = false,
    val confirmationPrompt: String? = null,
    val sources: List<String> = emptyList(),
    val latencyMs: Double = 0.0
)
