package com.smartglasses.ai.core.context

import java.util.UUID

data class ContextField<T>(
    val value: T,
    val source: String = "system",
    val timestamp: Long = System.currentTimeMillis(),
    val confidence: Float = 1.0f,
    val ttlMs: Long = 60_000L // 1 minute default TTL
) {
    val isFresh: Boolean
        get() = (System.currentTimeMillis() - timestamp) <= ttlMs
}

data class UserContext(
    val userId: String = "default_user",
    val name: String = "User",
    val email: String? = null,
    val phone: String? = null,
    val preferences: Map<String, Any> = emptyMap()
)

data class TemporalContext(
    val formattedTime: String = "",
    val formattedDate: String = "",
    val period: String = "morning", // morning, afternoon, evening, night
    val timezone: String = "UTC",
    val timestamp: Long = System.currentTimeMillis()
)

data class DeviceContext(
    val batteryPercentage: Int = 100,
    val isCharging: Boolean = false,
    val isScreenOn: Boolean = true,
    val volume: Int = 80,
    val storageFreeMb: Long = 1024L
)

data class ConnectivityContext(
    val isInternetAvailable: Boolean = true,
    val isWifiConnected: Boolean = true,
    val isCellularConnected: Boolean = false,
    val isBackendAvailable: Boolean = true,
    val backendLatencyMs: Double = 0.0
)

data class CalendarEventSummary(
    val id: String,
    val title: String,
    val startTime: String,
    val endTime: String,
    val location: String? = null,
    val isUrgent: Boolean = false
)

data class EmailSummary(
    val id: String,
    val sender: String,
    val subject: String,
    val snippet: String,
    val receivedTime: String,
    val isUnread: Boolean = true,
    val isImportant: Boolean = false
)

data class NotificationSummary(
    val id: String,
    val packageName: String,
    val title: String,
    val content: String,
    val timestamp: Long = System.currentTimeMillis(),
    val isUrgent: Boolean = false
)

data class ContactSummary(
    val id: String,
    val name: String,
    val phone: String?,
    val email: String? = null,
    val relationship: String? = null
)

data class GlassesContext(
    val isConnected: Boolean = false,
    val deviceName: String = "EVA-Glasses",
    val battery: Int = 100,
    val rssi: Int = -50,
    val firmwareVersion: String = "v1.0.0",
    val cameraReady: Boolean = false,
    val micReady: Boolean = false,
    val ipAddress: String? = null
)

data class ActiveTaskContext(
    val taskId: String = UUID.randomUUID().toString(),
    val type: String, // e.g. "job_application", "research_paper", "email_draft"
    val description: String,
    val progress: Float = 0.0f,
    val status: String = "RUNNING" // RUNNING, WAITING_CONFIRMATION, COMPLETED, FAILED
)

data class EvaContext(
    val sessionId: String = UUID.randomUUID().toString(),
    val user: ContextField<UserContext> = ContextField(UserContext(), ttlMs = 86400_000L),
    val temporal: ContextField<TemporalContext> = ContextField(TemporalContext(), ttlMs = 15_000L),
    val location: ContextField<String> = ContextField("Unavailable", ttlMs = 60_000L),
    val device: ContextField<DeviceContext> = ContextField(DeviceContext(), ttlMs = 30_000L),
    val connectivity: ContextField<ConnectivityContext> = ContextField(ConnectivityContext(), ttlMs = 15_000L),
    val calendarEvents: ContextField<List<CalendarEventSummary>> = ContextField(emptyList(), ttlMs = 300_000L),
    val unreadEmails: ContextField<List<EmailSummary>> = ContextField(emptyList(), ttlMs = 300_000L),
    val recentNotifications: ContextField<List<NotificationSummary>> = ContextField(emptyList(), ttlMs = 60_000L),
    val glasses: ContextField<GlassesContext> = ContextField(GlassesContext(), ttlMs = 5_000L),
    val recentActions: ContextField<List<String>> = ContextField(emptyList(), ttlMs = 120_000L),
    val activeTasks: ContextField<List<ActiveTaskContext>> = ContextField(emptyList(), ttlMs = 30_000L),
    val conversationHistory: List<Pair<String, String>> = emptyList() // Pair(User, Assistant)
)
