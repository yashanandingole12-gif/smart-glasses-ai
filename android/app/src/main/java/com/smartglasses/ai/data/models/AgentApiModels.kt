package com.smartglasses.ai.data.models

import com.google.gson.annotations.SerializedName

data class AgentMessageRequestDto(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("message") val message: String,
    @SerializedName("context") val context: FullContextPayloadDto? = null,
    @SerializedName("request_id") val requestId: String? = null,
    @SerializedName("client_timestamp") val clientTimestamp: Double = System.currentTimeMillis() / 1000.0,
    @SerializedName("confirmed_action") val confirmedAction: Boolean? = null
)

data class AgentActionDto(
    @SerializedName("tool_name") val toolName: String,
    @SerializedName("tool_input") val toolInput: Map<String, Any>? = null,
    @SerializedName("risk_level") val riskLevel: String = "READ",
    @SerializedName("status") val status: String = "executed",
    @SerializedName("result") val result: Any? = null
)

data class AgentMessageResponseDto(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("response") val response: String,
    @SerializedName("actions") val actions: List<AgentActionDto> = emptyList(),
    @SerializedName("requires_confirmation") val requiresConfirmation: Boolean = false,
    @SerializedName("confirmation_prompt") val confirmationPrompt: String? = null,
    @SerializedName("sources") val sources: List<String> = emptyList(),
    @SerializedName("metadata") val metadata: Map<String, Any> = emptyMap()
)

data class TemporalContextDto(
    @SerializedName("local_time") val localTime: String,
    @SerializedName("period") val period: String,
    @SerializedName("timezone") val timezone: String = "UTC",
    @SerializedName("date_str") val dateStr: String? = null,
    @SerializedName("iso_timestamp") val isoTimestamp: String? = null
)

data class LocationContextDto(
    @SerializedName("latitude") val latitude: Double = 0.0,
    @SerializedName("longitude") val longitude: Double = 0.0,
    @SerializedName("city") val city: String = "Unknown",
    @SerializedName("country") val country: String = "Unknown",
    @SerializedName("place_type") val placeType: String? = null
)

data class CalendarEventDto(
    @SerializedName("id") val id: String? = null,
    @SerializedName("title") val title: String,
    @SerializedName("start_time") val startTime: String,
    @SerializedName("end_time") val endTime: String? = null,
    @SerializedName("location") val location: String? = null,
    @SerializedName("description") val description: String? = null
)

data class CalendarContextDto(
    @SerializedName("current_event") val currentEvent: CalendarEventDto? = null,
    @SerializedName("next_event") val nextEvent: CalendarEventDto? = null,
    @SerializedName("today_events") val todayEvents: List<CalendarEventDto> = emptyList()
)

data class DeviceContextDto(
    @SerializedName("battery") val battery: Int = 100,
    @SerializedName("camera_available") val cameraAvailable: Boolean = true,
    @SerializedName("microphone_available") val microphoneAvailable: Boolean = true,
    @SerializedName("network") val network: String = "WIFI",
    @SerializedName("connection_type") val connectionType: String = "ANDROID_HUB"
)

data class ConversationContextDto(
    @SerializedName("recent_topic") val recentTopic: String? = null,
    @SerializedName("referenced_entities") val referencedEntities: Map<String, Any> = emptyMap(),
    @SerializedName("last_intent") val lastIntent: String? = null
)

data class FullContextPayloadDto(
    @SerializedName("time") val time: TemporalContextDto,
    @SerializedName("location") val location: LocationContextDto,
    @SerializedName("calendar") val calendar: CalendarContextDto? = null,
    @SerializedName("device") val device: DeviceContextDto,
    @SerializedName("conversation") val conversation: ConversationContextDto? = null
)

data class HealthResponseDto(
    @SerializedName("status") val status: String,
    @SerializedName("version") val version: String,
    @SerializedName("device_mode") val deviceMode: String,
    @SerializedName("llm_provider") val llmProvider: String
)

data class GoogleAuthStatusDto(
    @SerializedName("connected") val connected: Boolean = false,
    @SerializedName("email") val email: String? = null,
    @SerializedName("scopes") val scopes: List<String> = emptyList(),
    @SerializedName("is_expired") val isExpired: Boolean? = false,
    @SerializedName("expires_at") val expiresAt: String? = null
)
