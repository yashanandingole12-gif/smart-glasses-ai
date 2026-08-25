package com.smartglasses.ai.data.repositories

import com.smartglasses.ai.core.network.NetworkClient
import com.smartglasses.ai.data.models.AgentMessageRequestDto
import com.smartglasses.ai.data.models.DeviceContextDto
import com.smartglasses.ai.data.models.FullContextPayloadDto
import com.smartglasses.ai.data.models.LocationContextDto
import com.smartglasses.ai.data.models.TemporalContextDto
import com.smartglasses.ai.domain.models.WearableResponse
import com.smartglasses.ai.domain.models.WearableTelemetry
import com.smartglasses.ai.domain.repositories.AssistantRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.UUID

class AssistantRepositoryImpl : AssistantRepository {

    override suspend fun sendMessage(
        sessionId: String,
        userMessage: String,
        telemetry: WearableTelemetry,
        confirmedAction: Boolean?
    ): Result<WearableResponse> = withContext(Dispatchers.IO) {
        try {
            val api = NetworkClient.getApiService()

            val contextDto = FullContextPayloadDto(
                time = TemporalContextDto(
                    localTime = telemetry.timeFormatted,
                    period = telemetry.period,
                    timezone = "Asia/Kolkata"
                ),
                location = LocationContextDto(
                    latitude = 21.1458,
                    longitude = 79.0882,
                    city = telemetry.locationName,
                    country = "India",
                    placeType = "college campus"
                ),
                device = DeviceContextDto(
                    battery = telemetry.batteryPercentage,
                    cameraAvailable = true,
                    microphoneAvailable = true,
                    network = "WIFI",
                    connectionType = if (telemetry.glassesConnected) "BLE_ESP32" else "ANDROID_HUB"
                )
            )

            val request = AgentMessageRequestDto(
                sessionId = sessionId,
                message = userMessage,
                context = contextDto,
                requestId = UUID.randomUUID().toString(),
                clientTimestamp = System.currentTimeMillis() / 1000.0,
                confirmedAction = confirmedAction
            )

            val response = api.sendMessage(request)

            val latency = (response.metadata["latency_ms"] as? Number)?.toDouble() ?: 0.0

            Result.success(
                WearableResponse(
                    text = response.response,
                    sessionId = response.sessionId,
                    requiresConfirmation = response.requiresConfirmation,
                    confirmationPrompt = response.confirmationPrompt,
                    sources = response.sources,
                    latencyMs = latency
                )
            )
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun checkHealth(): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val api = NetworkClient.getApiService()
            val health = api.checkHealth()
            Result.success(health.status == "ok")
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun checkGoogleAuthStatus(): Result<Pair<Boolean, String?>> = withContext(Dispatchers.IO) {
        try {
            val api = NetworkClient.getApiService()
            val status = api.getGoogleStatus()
            Result.success(Pair(status.connected, status.email))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
