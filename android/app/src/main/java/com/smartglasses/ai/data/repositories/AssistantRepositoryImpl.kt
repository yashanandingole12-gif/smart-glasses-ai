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
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.UUID

class AssistantRepositoryImpl : AssistantRepository {

    override suspend fun sendMessage(
        sessionId: String,
        userMessage: String,
        telemetry: WearableTelemetry,
        confirmedAction: Boolean?,
        language: String?,
        locale: String?
    ): Result<WearableResponse> = withContext(Dispatchers.IO) {
        try {
            val api = NetworkClient.getApiService()

            val nowIso = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX", Locale.US).format(Date())

            val contextDto = FullContextPayloadDto(
                time = TemporalContextDto(
                    localTime = telemetry.timeFormatted,
                    period = telemetry.period,
                    timezone = telemetry.timezone,
                    isoTimestamp = nowIso
                ),
                location = LocationContextDto(
                    latitude = telemetry.latitude,
                    longitude = telemetry.longitude,
                    city = telemetry.locationName,
                    country = if (telemetry.locationAvailable) "India" else "",
                    isAvailable = telemetry.locationAvailable,
                    placeType = if (telemetry.locationAvailable) "mobile" else null
                ),
                device = DeviceContextDto(
                    battery = telemetry.batteryPercentage,
                    batteryPercent = telemetry.batteryPercentage,
                    cameraAvailable = true,
                    microphoneAvailable = true,
                    network = "WIFI",
                    connectionType = if (telemetry.glassesConnected) "BLE_ESP32" else "ANDROID_HUB",
                    esp32Connected = telemetry.glassesConnected
                ),
                locale = telemetry.locale,
                timezone = telemetry.timezone,
                timestamp = nowIso
            )

            val request = AgentMessageRequestDto(
                sessionId = sessionId,
                message = userMessage,
                language = language ?: "auto",
                locale = locale ?: telemetry.locale,
                context = contextDto,
                requestId = UUID.randomUUID().toString(),
                clientTimestamp = System.currentTimeMillis() / 1000.0,
                confirmedAction = confirmedAction
            )

            val response = api.sendMessage(request)

            val latency = (response.metadata["latency_ms"] as? Number)?.toDouble() ?: 0.0
            val failCatStr = response.metadata["failure_category"] as? String ?: "NONE"
            val failCat = try {
                com.smartglasses.ai.domain.models.FailureCategory.valueOf(failCatStr)
            } catch (_: Exception) {
                com.smartglasses.ai.domain.models.FailureCategory.NONE
            }
            val tier = (response.metadata["routing"] as? Map<*, *>)?.get("tier_used") as? String

            Result.success(
                WearableResponse(
                    text = response.response,
                    sessionId = response.sessionId,
                    requiresConfirmation = response.requiresConfirmation,
                    confirmationPrompt = response.confirmationPrompt,
                    sources = response.sources,
                    latencyMs = latency,
                    failureCategory = failCat,
                    tierUsed = tier
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
