package com.smartglasses.ai.domain.models

import java.util.UUID

enum class AssistantState {
    IDLE,
    LISTENING,
    PROCESSING,
    RESPONDING,
    SPEAKING,
    ERROR
}

enum class FailureCategory {
    NONE,
    NETWORK_FAILURE,
    LLM_TIMEOUT,
    LLM_RATE_LIMIT,
    LLM_PROVIDER_ERROR,
    TOOL_TIMEOUT,
    STT_FAILURE,
    TTS_FAILURE
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
    val requiresConfirmation: Boolean = false,
    val latencyMs: Double? = null,
    val failureCategory: FailureCategory = FailureCategory.NONE
)

data class WearableTelemetry(
    val glassesConnected: Boolean = false,
    val batteryPercentage: Int = 85,
    val aiConnected: Boolean = true,
    val locationAvailable: Boolean = false,
    val locationName: String = "Unavailable",
    val latitude: Double? = null,
    val longitude: Double? = null,
    val timeFormatted: String = "08:15 AM",
    val period: String = "morning",
    val timezone: String = "Asia/Kolkata",
    val locale: String = "en-IN"
)

data class WearableResponse(
    val text: String,
    val sessionId: String,
    val requiresConfirmation: Boolean = false,
    val confirmationPrompt: String? = null,
    val sources: List<String> = emptyList(),
    val latencyMs: Double = 0.0,
    val failureCategory: FailureCategory = FailureCategory.NONE,
    val tierUsed: String? = null
)
