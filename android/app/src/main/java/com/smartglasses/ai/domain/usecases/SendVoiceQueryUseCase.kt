package com.smartglasses.ai.domain.usecases

import com.smartglasses.ai.domain.models.WearableResponse
import com.smartglasses.ai.domain.models.WearableTelemetry
import com.smartglasses.ai.domain.repositories.AssistantRepository

class SendVoiceQueryUseCase(private val repository: AssistantRepository) {
    suspend operator fun invoke(
        sessionId: String,
        query: String,
        telemetry: WearableTelemetry,
        confirmedAction: Boolean? = null,
        confirmedActionId: String? = null,
        language: String? = "auto",
        locale: String? = "en-IN"
    ): Result<WearableResponse> {
        return repository.sendMessage(sessionId, query, telemetry, confirmedAction, confirmedActionId, language, locale)
    }
}
