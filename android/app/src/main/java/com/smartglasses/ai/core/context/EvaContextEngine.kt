package com.smartglasses.ai.core.context

import android.content.Context
import android.util.Log
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Date
import java.util.Locale
import java.util.TimeZone

class EvaContextEngine(private val context: Context) {
    companion object {
        private const val TAG = "EVA.ContextEngine"
    }

    private val _contextState = MutableStateFlow(EvaContext())
    val contextState: StateFlow<EvaContext> = _contextState.asStateFlow()

    init {
        refreshTemporalContext()
    }

    fun getOrRefreshContext(): EvaContext {
        val current = _contextState.value
        var updated = current

        // Validate freshness and selectively refresh stale components
        if (!current.temporal.isFresh) {
            updated = updated.copy(temporal = ContextField(computeTemporalContext(), ttlMs = 15_000L))
        }

        _contextState.value = updated
        return updated
    }

    fun updateTemporalContext(timeStr: String, dateStr: String, period: String) {
        val temporal = TemporalContext(
            formattedTime = timeStr,
            formattedDate = dateStr,
            period = period,
            timezone = TimeZone.getDefault().id
        )
        _contextState.value = _contextState.value.copy(
            temporal = ContextField(temporal, ttlMs = 15_000L)
        )
    }

    fun updateDeviceContext(battery: Int, isCharging: Boolean) {
        val dev = _contextState.value.device.value.copy(
            batteryPercentage = battery,
            isCharging = isCharging
        )
        _contextState.value = _contextState.value.copy(
            device = ContextField(dev, ttlMs = 30_000L)
        )
    }

    fun updateLocationContext(locationName: String) {
        _contextState.value = _contextState.value.copy(
            location = ContextField(locationName, ttlMs = 60_000L)
        )
    }

    fun updateGlassesContext(glasses: GlassesContext) {
        _contextState.value = _contextState.value.copy(
            glasses = ContextField(glasses, ttlMs = 5_000L)
        )
    }

    fun updateCalendarEvents(events: List<CalendarEventSummary>) {
        _contextState.value = _contextState.value.copy(
            calendarEvents = ContextField(events, ttlMs = 300_000L)
        )
    }

    fun updateUnreadEmails(emails: List<EmailSummary>) {
        _contextState.value = _contextState.value.copy(
            unreadEmails = ContextField(emails, ttlMs = 300_000L)
        )
    }

    fun updateRecentNotifications(notifs: List<NotificationSummary>) {
        _contextState.value = _contextState.value.copy(
            recentNotifications = ContextField(notifs, ttlMs = 60_000L)
        )
    }

    fun appendConversationTurn(userText: String, assistantText: String) {
        val history = _contextState.value.conversationHistory.takeLast(10).toMutableList()
        history.add(Pair(userText, assistantText))
        _contextState.value = _contextState.value.copy(conversationHistory = history)
    }

    fun generateContextAwareGreeting(): String {
        val ctx = getOrRefreshContext()
        val period = ctx.temporal.value.period
        val greetingWord = when (period) {
            "morning" -> "Good morning"
            "afternoon" -> "Good afternoon"
            "evening" -> "Good evening"
            else -> "Hello"
        }

        val highlights = mutableListOf<String>()

        // 1. Check for upcoming calendar events
        val events = ctx.calendarEvents.value
        if (events.isNotEmpty()) {
            val firstEvent = events.first()
            highlights.add("you have '${firstEvent.title}' scheduled at ${firstEvent.startTime}")
        }

        // 2. Check for important/unread emails
        val emails = ctx.unreadEmails.value
        val importantEmail = emails.firstOrNull { it.isImportant || it.subject.contains("internship", true) || it.subject.contains("offer", true) || it.subject.contains("urgent", true) }
        if (importantEmail != null) {
            highlights.add("a new email from ${importantEmail.sender} about '${importantEmail.subject}'")
        } else if (emails.isNotEmpty()) {
            highlights.add("${emails.size} unread email${if (emails.size > 1) "s" else ""}")
        }

        // 3. Check for urgent notifications
        val urgentNotif = ctx.recentNotifications.value.firstOrNull { it.isUrgent }
        if (urgentNotif != null) {
            highlights.add("an urgent alert: ${urgentNotif.title}")
        }

        return when {
            highlights.size >= 2 -> "$greetingWord. You have ${highlights[0]}, and ${highlights[1]}."
            highlights.size == 1 -> "$greetingWord. You have ${highlights[0]}."
            else -> "$greetingWord. You have no urgent updates right now."
        }
    }

    private fun computeTemporalContext(): TemporalContext {
        val now = Date()
        val cal = Calendar.getInstance()
        val hour = cal.get(Calendar.HOUR_OF_DAY)
        val period = when (hour) {
            in 5..11 -> "morning"
            in 12..16 -> "afternoon"
            in 17..21 -> "evening"
            else -> "night"
        }
        val timeFormat = SimpleDateFormat("h:mm a", Locale.getDefault()).format(now)
        val dateFormat = SimpleDateFormat("EEEE, MMMM d", Locale.getDefault()).format(now)
        return TemporalContext(
            formattedTime = timeFormat,
            formattedDate = dateFormat,
            period = period,
            timezone = TimeZone.getDefault().id,
            timestamp = System.currentTimeMillis()
        )
    }

    private fun refreshTemporalContext() {
        _contextState.value = _contextState.value.copy(
            temporal = ContextField(computeTemporalContext(), ttlMs = 15_000L)
        )
    }
}
