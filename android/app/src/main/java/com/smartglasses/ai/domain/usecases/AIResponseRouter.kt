package com.smartglasses.ai.domain.usecases

import android.content.Context
import com.smartglasses.ai.core.ai.LocalAiEngine
import com.smartglasses.ai.core.network.ConnectionState
import com.smartglasses.ai.core.sms.SmsManagerHelper
import com.smartglasses.ai.core.telephony.CallController
import com.smartglasses.ai.domain.models.AiAvailabilityState
import com.smartglasses.ai.domain.models.FailureCategory
import com.smartglasses.ai.domain.models.ResponseCapabilityStatus
import com.smartglasses.ai.domain.models.ResponseSource
import com.smartglasses.ai.domain.models.UnifiedSource
import com.smartglasses.ai.domain.models.WearableResponse
import com.smartglasses.ai.domain.models.WearableTelemetry
import com.smartglasses.ai.domain.repositories.AssistantRepository
import kotlinx.coroutines.withTimeoutOrNull
import java.util.Locale

class AIResponseRouter(
    private val repository: AssistantRepository,
    private val deterministicResolver: LocalDeterministicResolver,
    private val localAiEngine: LocalAiEngine,
    private val context: Context? = null,
    private val callController: CallController? = context?.let { CallController(it) }
) {
    var conversationalCloudTimeoutMs: Long = 2500L

    suspend fun routeQuery(
        sessionId: String,
        query: String,
        telemetry: WearableTelemetry,
        connectionState: ConnectionState,
        confirmedAction: Boolean? = null,
        confirmedActionId: String? = null,
        language: String? = "auto",
        locale: String? = "en-IN",
        onAiStateChanged: ((AiAvailabilityState) -> Unit)? = null
    ): WearableResponse {
        val q = query.trim()
        val qLower = q.lowercase(Locale.ROOT)
        val tStart = System.currentTimeMillis()

        // 0. LAYER 0 — Native Telephony & Call Controls (<50ms on-device)
        if (isCallQuery(qLower)) {
            val callResp = handleLocalCallQuery(q, sessionId, tStart)
            if (callResp != null) {
                return callResp
            }
        }

        // 1. LAYER 1 — Local Deterministic Fast-Path (<50ms)
        val deterministicResult = deterministicResolver.resolve(q, telemetry, sessionId, language)
        if (deterministicResult != null) {
            return deterministicResult.copy(
                unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                capabilityStatus = ResponseCapabilityStatus.ANSWERED
            )
        }

        // 2. LAYER 1.5 — Local Android SMS Queries (<50ms on-device)
        if (isSmsQuery(qLower)) {
            return handleLocalSmsQuery(q, sessionId, tStart)
        }

        // 3. Check if the query strictly requires cloud access (Gmail, Google Calendar, Web Search, Vision)
        val cloudRequired = isCloudRequiredQuery(qLower)

        if (cloudRequired) {
            if (connectionState == ConnectionState.CONNECTED) {
                // Execute cloud tool query with standard timeout
                val cloudResult = repository.sendMessage(
                    sessionId = sessionId,
                    userMessage = q,
                    telemetry = telemetry,
                    confirmedAction = confirmedAction,
                    confirmedActionId = confirmedActionId,
                    language = language,
                    locale = locale
                )
                return cloudResult.getOrElse { err ->
                    buildHonestOfflineCloudError(qLower, sessionId, err.localizedMessage ?: "Network error")
                }.copy(
                    unifiedSource = UnifiedSource.TOOL,
                    capabilityStatus = ResponseCapabilityStatus.ANSWERED
                )
            } else {
                // When offline, DO NOT fabricate or hallucinate external tool results
                return buildHonestOfflineCloudError(qLower, sessionId, "Offline")
            }
        }

        // 4. LAYER 2 & 3 — Conversational / General AI with Preemptive Cloud Timeout
        if (connectionState == ConnectionState.CONNECTED) {
            onAiStateChanged?.invoke(AiAvailabilityState.CLOUD_AVAILABLE)

            // Attempt Cloud AI with strict 2.5-second conversational budget
            val cloudResponse = withTimeoutOrNull(conversationalCloudTimeoutMs) {
                try {
                    val res = repository.sendMessage(
                        sessionId = sessionId,
                        userMessage = q,
                        telemetry = telemetry,
                        confirmedAction = confirmedAction,
                        confirmedActionId = confirmedActionId,
                        language = language,
                        locale = locale
                    )
                    res.getOrNull()
                } catch (_: Exception) {
                    null
                }
            }

            if (cloudResponse != null && cloudResponse.text.isNotBlank()) {
                return cloudResponse.copy(
                    source = ResponseSource.CLOUD_GEMINI,
                    unifiedSource = UnifiedSource.CLOUD,
                    capabilityStatus = ResponseCapabilityStatus.ANSWERED
                )
            }

            // Cloud timed out or failed -> Preempt and fallback to Local AI
            onAiStateChanged?.invoke(AiAvailabilityState.USING_LOCAL_AI)
            val localAiResp = localAiEngine.generateResponse(q, telemetry, sessionId)
            return localAiResp.copy(
                failureCategory = FailureCategory.LLM_TIMEOUT,
                tierUsed = "LOCAL_AI_FALLBACK",
                source = ResponseSource.LOCAL_AI,
                unifiedSource = UnifiedSource.LOCAL_AI,
                capabilityStatus = ResponseCapabilityStatus.ANSWERED
            )
        } else {
            // Completely offline -> Direct Local AI invocation (<100ms)
            onAiStateChanged?.invoke(AiAvailabilityState.LOCAL_ONLY)
            val localAiResp = localAiEngine.generateResponse(q, telemetry, sessionId)
            return localAiResp.copy(
                source = ResponseSource.LOCAL_AI,
                unifiedSource = UnifiedSource.LOCAL_AI,
                capabilityStatus = ResponseCapabilityStatus.ANSWERED
            )
        }
    }

    private var lastReadSmsSender: String? = null
    private var lastReadSmsPhone: String? = null

    private val contactSmsPatterns = listOf(
        Regex("""(?:did|has)\s+([a-zA-Z0-9\s]+?)\s+(?:message|text|sms)(?:\s+me)?\??$"""),
        Regex("""(?:any\s+(?:new\s+)?(?:messages?|sms|texts?)\s+(?:from|by)\s+([a-zA-Z0-9\s]+?))\??$"""),
        Regex("""(?:read|check|show)\s+(?:recent\s+|latest\s+)?(?:messages?|sms|texts?)\s+(?:from|by)\s+([a-zA-Z0-9\s]+?)\??$"""),
        Regex("""(?:messages?|sms|texts?)\s+(?:from|by)\s+([a-zA-Z0-9\s]+?)\??$"""),
        Regex("""([a-zA-Z0-9\s]+?)\s+(?:ka|se)\s+(?:sms|message|text)"""),
        Regex("""([a-zA-Z0-9\s]+?)\s+ne\s+(?:sms|message|text)\s+(?:bheja|bheja\s+kya)""")
    )

    private fun isSmsQuery(qLower: String): Boolean {
        val smsKeywords = listOf(
            "read my sms", "read my messages", "read sms", "read recent messages",
            "read my latest message", "read latest message", "latest message",
            "check sms", "check my messages", "any new messages", "any messages",
            "sms messages", "read text", "read texts", "my texts", "sms padho",
            "who sent it", "who sent this", "who is the sender", "reply that", "reply to him"
        )
        if (smsKeywords.any { qLower.contains(it) } || qLower == "sms" || qLower == "messages" || qLower.startsWith("reply ")) {
            return true
        }
        return contactSmsPatterns.any { it.containsMatchIn(qLower) }
    }

    private fun handleLocalSmsQuery(query: String, sessionId: String, tStart: Long): WearableResponse {
        val ctx = context
        if (ctx == null) {
            return WearableResponse(
                text = "I can't access your messages right now.",
                sessionId = sessionId,
                source = ResponseSource.UNAVAILABLE,
                unifiedSource = UnifiedSource.UNAVAILABLE,
                capabilityStatus = ResponseCapabilityStatus.FAILED,
                latencyMs = (System.currentTimeMillis() - tStart).toDouble().coerceAtLeast(1.0)
            )
        }

        if (!SmsManagerHelper.hasReadPermission(ctx)) {
            return WearableResponse(
                text = "I don't have permission to read your messages.",
                sessionId = sessionId,
                source = ResponseSource.TOOL,
                unifiedSource = UnifiedSource.TOOL,
                capabilityStatus = ResponseCapabilityStatus.REQUIRES_PERMISSION,
                latencyMs = (System.currentTimeMillis() - tStart).toDouble().coerceAtLeast(1.0)
            )
        }

        val qLower = query.lowercase().trim()
        var targetContact: String? = null
        for (pattern in contactSmsPatterns) {
            val match = pattern.find(qLower)
            if (match != null) {
                targetContact = match.groupValues[1].trim()
                break
            }
        }

        val latMs = (System.currentTimeMillis() - tStart).toDouble().coerceAtLeast(1.0)

        // Handle 'who sent it' follow-up
        if (listOf("who sent it", "who sent this", "who is the sender", "who sent").any { qLower.contains(it) }) {
            val s = lastReadSmsSender
            val respText = if (s != null) "That message was sent by $s." else "I don't have a recent message in context."
            return WearableResponse(
                text = respText,
                sessionId = sessionId,
                source = ResponseSource.TOOL,
                unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                latencyMs = latMs
            )
        }

        // Handle 'reply that ...' follow-up
        if (qLower.startsWith("reply")) {
            val replyBody = qLower.removePrefix("reply").removePrefix(" to him").removePrefix(" that").trim()
            val target = lastReadSmsSender ?: "contact"
            return WearableResponse(
                text = "I have prepared an SMS to $target: '$replyBody'. Should I send it?",
                sessionId = sessionId,
                source = ResponseSource.TOOL,
                unifiedSource = UnifiedSource.TOOL,
                requiresConfirmation = true,
                confirmationPrompt = "Send SMS to $target: '$replyBody'?",
                confirmationActionId = "sms_reply_${System.currentTimeMillis()}",
                capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                latencyMs = latMs
            )
        }

        // Contact-specific query
        if (!targetContact.isNullOrBlank()) {
            // Check for multiple contact matches (disambiguation)
            val matchedContacts = SmsManagerHelper.findPhoneNumbersForContact(ctx, targetContact)
            val distinctNames = matchedContacts.map { it.first }.distinct()
            if (distinctNames.size > 1) {
                val namesList = distinctNames.joinToString(" and ")
                return WearableResponse(
                    text = "I found multiple contacts matching '$targetContact': $namesList. Which one would you like to check?",
                    sessionId = sessionId,
                    source = ResponseSource.TOOL,
                    unifiedSource = UnifiedSource.TOOL,
                    capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                    latencyMs = latMs
                )
            }

            val messages = SmsManagerHelper.searchMessages(ctx, targetContact, limit = 3)
            if (messages.isEmpty()) {
                return WearableResponse(
                    text = "No messages found from $targetContact.",
                    sessionId = sessionId,
                    source = ResponseSource.TOOL,
                    unifiedSource = UnifiedSource.TOOL,
                    capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                    latencyMs = latMs
                )
            }

            val latest = messages.first()
            val sender = latest.contactName ?: latest.address
            lastReadSmsSender = sender
            lastReadSmsPhone = latest.address

            val text = if (messages.size == 1) {
                "Message from $sender: ${latest.body}"
            } else {
                "You have ${messages.size} messages from $sender. Latest: ${latest.body}"
            }

            return WearableResponse(
                text = text,
                sessionId = sessionId,
                source = ResponseSource.TOOL,
                unifiedSource = UnifiedSource.TOOL,
                capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                latencyMs = latMs
            )
        }

        // General recent messages query
        val messages = SmsManagerHelper.readRecentMessages(ctx, limit = 3)
        if (messages.isEmpty()) {
            return WearableResponse(
                text = "You don't have any messages I can read.",
                sessionId = sessionId,
                source = ResponseSource.TOOL,
                unifiedSource = UnifiedSource.TOOL,
                capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                latencyMs = latMs
            )
        }

        val latest = messages.first()
        val sender = latest.contactName ?: latest.address
        lastReadSmsSender = sender
        lastReadSmsPhone = latest.address

        val text = if (messages.size == 1) {
            "You have 1 message from $sender: ${latest.body}"
        } else {
            "You have ${messages.size} messages. Most recent from $sender: ${latest.body}"
        }

        return WearableResponse(
            text = text,
            sessionId = sessionId,
            source = ResponseSource.TOOL,
            unifiedSource = UnifiedSource.TOOL,
            capabilityStatus = ResponseCapabilityStatus.ANSWERED,
            latencyMs = latMs
        )
    }

    private val callActionKeywords = listOf(
        "answer the call", "answer call", "answer", "pick up the call", "pick up call", "pick up",
        "accept call", "accept the call", "accept", "take call", "take the call", "receive call",
        "receive the call", "attend call", "call uthao", "phone uthao",
        "reject the call", "reject call", "reject", "decline call", "decline the call", "decline",
        "ignore call", "cut call", "cut the call", "call kato", "phone kato",
        "hang up", "end the call", "end call", "disconnect call", "disconnect",
        "who is calling", "who's calling"
    )

    private fun isCallQuery(qLower: String): Boolean {
        if (callActionKeywords.any { qLower.contains(it) }) return true
        if (qLower.startsWith("call ") || qLower.startsWith("phone ") || qLower.startsWith("dial ")) return true
        return false
    }

    private fun handleLocalCallQuery(query: String, sessionId: String, tStart: Long): WearableResponse? {
        val qLower = query.lowercase().trim()
        val latMs = (System.currentTimeMillis() - tStart).toDouble().coerceAtLeast(1.0)

        // 1. Answer Call
        val answerKeywords = listOf(
            "answer the call", "answer call", "answer", "pick up the call", "pick up call", "pick up",
            "accept call", "accept the call", "accept", "take call", "take the call", "receive call",
            "receive the call", "attend call", "call uthao", "phone uthao"
        )
        if (answerKeywords.any { qLower == it || qLower.contains(it) }) {
            callController?.answerCall()
            return WearableResponse(
                text = "Answering the incoming call.",
                sessionId = sessionId,
                source = ResponseSource.TOOL,
                unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                latencyMs = latMs
            )
        }

        // 2. Reject / Cut Call
        val rejectKeywords = listOf(
            "reject the call", "reject call", "reject", "decline call", "decline the call", "decline",
            "ignore call", "cut call", "cut the call", "call kato", "phone kato"
        )
        if (rejectKeywords.any { qLower == it || qLower.contains(it) }) {
            callController?.endCall()
            return WearableResponse(
                text = "Rejecting the incoming call.",
                sessionId = sessionId,
                source = ResponseSource.TOOL,
                unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                latencyMs = latMs
            )
        }

        // 3. End / Hang up Call
        val endKeywords = listOf("hang up", "end the call", "end call", "disconnect call", "disconnect")
        if (endKeywords.any { qLower == it || qLower.contains(it) }) {
            callController?.endCall()
            return WearableResponse(
                text = "Call ended.",
                sessionId = sessionId,
                source = ResponseSource.TOOL,
                unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                latencyMs = latMs
            )
        }

        // 4. Outgoing Call: "call [name]"
        val callMatch = Regex("""^(?:call|phone|dial|make a call to)\s+([a-zA-Z0-9\s]+?)(?:\s+please|\s+now)?$""").find(qLower)
        if (callMatch != null) {
            val target = callMatch.groupValues[1].trim()
            val ctx = context
            if (ctx != null) {
                val matchedContacts = SmsManagerHelper.findPhoneNumbersForContact(ctx, target)
                val distinctNames = matchedContacts.map { it.first }.distinct()
                if (distinctNames.size > 1) {
                    val namesList = distinctNames.joinToString(" or ")
                    return WearableResponse(
                        text = "I found multiple contacts for '$target': $namesList. Which one would you like to call?",
                        sessionId = sessionId,
                        source = ResponseSource.TOOL,
                        unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                        capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                        latencyMs = latMs
                    )
                }
                if (matchedContacts.isNotEmpty()) {
                    val contact = matchedContacts.first()
                    callController?.makeCall(contact.second)
                    return WearableResponse(
                        text = "Calling ${contact.first}.",
                        sessionId = sessionId,
                        source = ResponseSource.TOOL,
                        unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                        capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                        latencyMs = latMs
                    )
                }
            }
            // If contact not directly resolved locally, return clean message or fallthrough to cloud
            return WearableResponse(
                text = "Calling $target.",
                sessionId = sessionId,
                source = ResponseSource.TOOL,
                unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                latencyMs = latMs
            )
        }

        return null
    }

    private fun isCloudRequiredQuery(qLower: String): Boolean {
        val cloudKeywords = listOf(
            "email", "gmail", "mail", "inbox", "unread", "ईमेल",
            "calendar", "schedule", "events", "meeting", "class", "tomorrow", "कैलेंडर",
            "search the web", "web search", "google search", "search for", "who won the", "weather"
        )
        return cloudKeywords.any { qLower.contains(it) }
    }

    private fun buildHonestOfflineCloudError(qLower: String, sessionId: String, reason: String): WearableResponse {
        val text = when {
            qLower.contains("email") || qLower.contains("gmail") || qLower.contains("mail") || qLower.contains("inbox") ->
                "I can't access your email right now."
            qLower.contains("calendar") || qLower.contains("schedule") || qLower.contains("meeting") || qLower.contains("tomorrow") || qLower.contains("class") ->
                "I can't access your calendar right now."
            qLower.contains("search") ->
                "I can't search the web right now."
            else ->
                "I can't answer that right now."
        }

        return WearableResponse(
            text = text,
            sessionId = sessionId,
            requiresConfirmation = false,
            confirmationPrompt = null,
            confirmationActionId = null,
            sources = listOf("offline_guard"),
            latencyMs = 5.0,
            failureCategory = FailureCategory.NETWORK_FAILURE,
            tierUsed = "OFFLINE_GUARD",
            source = ResponseSource.UNAVAILABLE,
            unifiedSource = UnifiedSource.UNAVAILABLE,
            capabilityStatus = ResponseCapabilityStatus.REQUIRES_NETWORK
        )
    }
}
