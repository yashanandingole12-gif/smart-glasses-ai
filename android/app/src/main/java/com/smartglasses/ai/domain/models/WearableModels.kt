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
    READY,
    PERMISSION_REQUIRED
}

enum class AiAvailabilityState {
    CLOUD_AVAILABLE,
    LOCAL_ONLY,
    CLOUD_DEGRADED,
    USING_LOCAL_AI
}

enum class ResponseSource {
    LOCAL_DETERMINISTIC,
    LOCAL_AI,
    CLOUD_GEMINI,
    CLOUD_SECONDARY,
    TOOL,
    UNAVAILABLE,
    FALLBACK
}

enum class UnifiedSource {
    LOCAL_DETERMINISTIC,
    LOCAL_AI,
    CLOUD,
    TOOL,
    UNAVAILABLE
}

enum class ResponseCapabilityStatus {
    ANSWERED,
    REQUIRES_NETWORK,
    REQUIRES_PERMISSION,
    FAILED
}

data class ResponseResult(
    val source: UnifiedSource,
    val status: ResponseCapabilityStatus,
    val text: String,
    val sessionId: String,
    val latencyMs: Double = 0.0,
    val requiresConfirmation: Boolean = false,
    val confirmationPrompt: String? = null,
    val confirmationActionId: String? = null,
    val failureCategory: FailureCategory = FailureCategory.NONE,
    val tierUsed: String? = null,
    val sources: List<String> = emptyList()
)

data class ChatMessage(
    val id: String = UUID.randomUUID().toString(),
    val sender: String, // "USER" or "ASSISTANT"
    val text: String,
    val timestamp: Long = System.currentTimeMillis(),
    val requiresConfirmation: Boolean = false,
    val confirmationActionId: String? = null,
    val latencyMs: Double? = null,
    val failureCategory: FailureCategory = FailureCategory.NONE,
    val source: ResponseSource = ResponseSource.LOCAL_DETERMINISTIC,
    val unifiedSource: UnifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
    val capabilityStatus: ResponseCapabilityStatus = ResponseCapabilityStatus.ANSWERED,
    val imageBase64: String? = null,
    val imageUri: String? = null
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
    val confirmationActionId: String? = null,
    val sources: List<String> = emptyList(),
    val latencyMs: Double = 0.0,
    val failureCategory: FailureCategory = FailureCategory.NONE,
    val tierUsed: String? = null,
    val source: ResponseSource = ResponseSource.LOCAL_DETERMINISTIC,
    val unifiedSource: UnifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
    val capabilityStatus: ResponseCapabilityStatus = ResponseCapabilityStatus.ANSWERED,
    val imageBase64: String? = null,
    val imageUri: String? = null
)
