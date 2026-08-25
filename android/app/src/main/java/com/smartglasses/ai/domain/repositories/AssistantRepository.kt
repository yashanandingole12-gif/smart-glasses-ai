package com.smartglasses.ai.domain.repositories

import com.smartglasses.ai.domain.models.WearableResponse
import com.smartglasses.ai.domain.models.WearableTelemetry

interface AssistantRepository {
    suspend fun sendMessage(
        sessionId: String,
        userMessage: String,
        telemetry: WearableTelemetry,
        confirmedAction: Boolean? = null
    ): Result<WearableResponse>

    suspend fun checkHealth(): Result<Boolean>

    suspend fun checkGoogleAuthStatus(): Result<Pair<Boolean, String?>>
}
