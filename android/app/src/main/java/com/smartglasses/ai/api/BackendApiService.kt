package com.smartglasses.ai.api

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

data class AgentMessageRequestDto(
    val session_id: String,
    val message: String,
    val context: Map<String, Any>? = null,
    val client_timestamp: Double = System.currentTimeMillis() / 1000.0
)

data class AgentMessageResponseDto(
    val session_id: String,
    val response: String,
    val requires_confirmation: Boolean = false,
    val sources: List<String> = emptyList(),
    val metadata: Map<String, Any> = emptyMap()
)

data class HealthResponseDto(
    val status: String,
    val version: String,
    val device_mode: String,
    val llm_provider: String
)

interface BackendApiService {
    @GET("api/v1/health")
    suspend fun checkHealth(): HealthResponseDto

    @POST("api/v1/agent/message")
    suspend fun sendMessage(@Body request: AgentMessageRequestDto): AgentMessageResponseDto
}
