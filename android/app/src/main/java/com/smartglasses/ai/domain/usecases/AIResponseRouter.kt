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
    var conversationalCloudTimeoutMs: Long = 7500L

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

        // 0. Handle Confirmation of Pending Actions (SMS Dispatch, Call Confirmation, etc.)
        if ((confirmedAction == true && confirmedActionId != null) ||
            ((qLower in listOf("yes", "send it", "send", "proceed", "haan", "bhejo", "bhej do", "yes please", "sure", "ok send")) && pendingSendMessage != null)) {
            val ctx = context
            if (confirmedActionId != null && confirmedActionId.startsWith("call_dial_")) {
                val dialNumber = confirmedActionId.removePrefix("call_dial_")
                callController?.makeCall(dialNumber)
                return WearableResponse(
                    text = "Calling $dialNumber.",
                    sessionId = sessionId,
                    source = ResponseSource.TOOL,
                    unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                    capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                    latencyMs = (System.currentTimeMillis() - tStart).toDouble().coerceAtLeast(1.0)
                )
            }
            if (ctx != null) {
                val dest = pendingSendPhone ?: lastReadSmsPhone
                val body = pendingSendMessage
                if (!dest.isNullOrBlank() && !body.isNullOrBlank()) {
                    val ok = SmsManagerHelper.sendSms(ctx, dest, body)
                    val recName = pendingSendRecipient ?: lastReadSmsSender ?: dest
                    pendingSendMessage = null
                    pendingSendPhone = null
                    pendingSendRecipient = null
                    return WearableResponse(
                        text = if (ok) "Message sent to $recName." else "Failed to send message to $recName.",
                        sessionId = sessionId,
                        source = ResponseSource.TOOL,
                        unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                        capabilityStatus = if (ok) ResponseCapabilityStatus.ANSWERED else ResponseCapabilityStatus.FAILED,
                        latencyMs = (System.currentTimeMillis() - tStart).toDouble().coerceAtLeast(1.0)
                    )
                }
            }
        }

        // Handle Cancellation of Pending Drafts
        if (qLower in listOf("no", "cancel", "don't send", "mat bhejo", "cancel draft", "nahi", "stop draft") &&
            (pendingSendMessage != null || pendingDraftRecipient != null)) {
            pendingSendMessage = null
            pendingSendPhone = null
            pendingSendRecipient = null
            pendingDraftRecipient = null
            pendingDraftPhone = null
            return WearableResponse(
                text = "Draft cancelled.",
                sessionId = sessionId,
                source = ResponseSource.LOCAL_DETERMINISTIC,
                unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                latencyMs = (System.currentTimeMillis() - tStart).toDouble().coerceAtLeast(1.0)
            )
        }

        // Active Multi-Turn SMS Drafting Follow-up
        val activeDraftTarget = pendingDraftRecipient
        if (activeDraftTarget != null) {
            val politeBody = expandIntoPoliteMessage(activeDraftTarget, q)
            val destPhone = pendingDraftPhone
            pendingDraftRecipient = null
            pendingDraftPhone = null
            pendingSendMessage = politeBody
            pendingSendPhone = destPhone
            pendingSendRecipient = activeDraftTarget
            return WearableResponse(
                text = "I have drafted the following message for $activeDraftTarget: '$politeBody'. Shall I send it?",
                sessionId = sessionId,
                source = ResponseSource.TOOL,
                unifiedSource = UnifiedSource.TOOL,
                requiresConfirmation = true,
                confirmationPrompt = "Send SMS to $activeDraftTarget: '$politeBody'?",
                confirmationActionId = "sms_send_${System.currentTimeMillis()}",
                capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                latencyMs = (System.currentTimeMillis() - tStart).toDouble().coerceAtLeast(1.0)
            )
        }

        // 0.05 Handle Active Contact Disambiguation for Calls & SMS
        val disambigCallCandidates = pendingCallDisambiguation
        if (disambigCallCandidates != null && disambigCallCandidates.isNotEmpty()) {
            val selected = resolveDisambiguationOption(qLower, disambigCallCandidates)
            if (selected != null) {
                pendingCallDisambiguation = null
                callController?.makeCall(selected.second)
                return WearableResponse(
                    text = "Calling ${selected.first}.",
                    sessionId = sessionId,
                    source = ResponseSource.TOOL,
                    unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                    capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                    latencyMs = (System.currentTimeMillis() - tStart).toDouble().coerceAtLeast(1.0)
                )
            }
        }

        val disambigSmsCandidates = pendingSmsDisambiguation
        if (disambigSmsCandidates != null && disambigSmsCandidates.isNotEmpty()) {
            val selected = resolveDisambiguationOption(qLower, disambigSmsCandidates)
            if (selected != null) {
                val body = pendingSmsDisambiguationBody ?: "I will get back to you shortly."
                pendingSmsDisambiguation = null
                pendingSmsDisambiguationBody = null
                pendingSendMessage = body
                pendingSendPhone = selected.second
                pendingSendRecipient = selected.first
                return WearableResponse(
                    text = "I have drafted a message to ${selected.first}: '$body'. Shall I send it?",
                    sessionId = sessionId,
                    source = ResponseSource.TOOL,
                    unifiedSource = UnifiedSource.TOOL,
                    requiresConfirmation = true,
                    confirmationPrompt = "Send SMS to ${selected.first}: '$body'?",
                    confirmationActionId = "sms_send_${System.currentTimeMillis()}",
                    capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                    latencyMs = (System.currentTimeMillis() - tStart).toDouble().coerceAtLeast(1.0)
                )
            }
        }

        // 0.08 Conversational Lifecycle & Session Management
        val lifecycleGreetings = listOf(
            "eva start talk", "eva talk", "hey eva", "hi eva", "hello eva", "eva", "wake up eva",
            "hey lara", "hi lara", "hello lara", "lara", "wake up lara", "hey assistant",
            "start talk", "start listening", "talk"
        )
        if (lifecycleGreetings.any { qLower == it || qLower.startsWith("$it ") }) {
            val bat = telemetry.batteryPercentage
            val ctx = context
            val unreadCount = ctx?.let {
                try {
                    val (unread, _) = SmsManagerHelper.readFilteredMessages(it, limit = 5, includePromotions = false)
                    unread.size
                } catch (_: Exception) { 0 }
            } ?: 0
            val unreadPart = if (unreadCount > 0) " You have $unreadCount personal message${if (unreadCount > 1) "s" else ""}." else ""
            return WearableResponse(
                text = "Hello! EVA is active and ready. Battery is at $bat%.$unreadPart How can I help you today?",
                sessionId = sessionId,
                source = ResponseSource.LOCAL_DETERMINISTIC,
                unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                latencyMs = (System.currentTimeMillis() - tStart).toDouble().coerceAtLeast(1.0)
            )
        }

        val lifecycleDismiss = listOf(
            "goodbye eva", "bye eva", "sleep eva", "shutdown eva", "turn off eva",
            "goodbye lara", "bye lara", "sleep lara", "shutdown lara", "turn off lara",
            "goodbye", "alvida", "stop talk", "stop listening", "stop"
        )
        if (lifecycleDismiss.any { qLower == it || qLower.startsWith("$it ") }) {
            // Clean active session context
            lastReadSmsIndex = 0
            lastReadSmsList = emptyList()
            lastReadSmsSender = null
            lastReadSmsPhone = null
            pendingSendMessage = null
            pendingSendPhone = null
            pendingSendRecipient = null
            pendingCallDisambiguation = null
            pendingSmsDisambiguation = null
            pendingSmsDisambiguationBody = null
            return WearableResponse(
                text = "Goodbye! Putting EVA to sleep. Say 'Hey EVA' whenever you need me.",
                sessionId = sessionId,
                source = ResponseSource.LOCAL_DETERMINISTIC,
                unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                latencyMs = (System.currentTimeMillis() - tStart).toDouble().coerceAtLeast(1.0)
            )
        }

        // 0. LAYER 0 — Native Telephony & Call Controls (<50ms on-device)
        if (isCallQuery(qLower)) {
            val callResp = handleLocalCallQuery(q, sessionId, tStart)
            if (callResp != null) {
                return callResp
            }
        }

        // 1. LAYER 0.5 — Check if the query strictly requires cloud access (Gmail, Google Calendar, Web Search, Vision, Camera Capture)
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
                // When offline and it's a photo command, fallback to local BLE camera capture
                if (listOf("take a picture", "click the pic", "click the picture", "take photo", "capture image").any { qLower.contains(it) }) {
                    context?.let { com.smartglasses.ai.core.bluetooth.BleManager.getInstance(it).requestPhotoCapture() }
                    return WearableResponse(
                        text = "Photo captured and saved to your Gallery.",
                        sessionId = sessionId,
                        source = ResponseSource.LOCAL_DETERMINISTIC,
                        unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                        capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                        latencyMs = (System.currentTimeMillis() - tStart).toDouble().coerceAtLeast(1.0)
                    )
                }
                // When offline, DO NOT fabricate or hallucinate external tool results
                return buildHonestOfflineCloudError(qLower, sessionId, "Offline")
            }
        }

        // 2. LAYER 1 — Local Deterministic Fast-Path (<50ms)
        val deterministicResult = deterministicResolver.resolve(q, telemetry, sessionId, language)
        if (deterministicResult != null) {
            if (deterministicResult.text.contains("Photo captured")) {
                context?.let { com.smartglasses.ai.core.bluetooth.BleManager.getInstance(it).requestPhotoCapture() }
            }
            return deterministicResult.copy(
                unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                capabilityStatus = ResponseCapabilityStatus.ANSWERED
            )
        }

        // 3. LAYER 1.5 — Local Android SMS Queries (<50ms on-device)
        if (isSmsQuery(qLower)) {
            return handleLocalSmsQuery(q, sessionId, tStart)
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

    private var lastReadSmsIndex: Int = 0
    private var lastReadSmsList: List<com.smartglasses.ai.core.sms.SmsItem> = emptyList()
    private var lastReadSmsSender: String? = null
    private var lastReadSmsPhone: String? = null
    private var pendingSendMessage: String? = null
    private var pendingSendPhone: String? = null
    private var pendingSendRecipient: String? = null
    private var pendingDraftRecipient: String? = null
    private var pendingDraftPhone: String? = null
    private var pendingCallDisambiguation: List<Pair<String, String>>? = null
    private var pendingSmsDisambiguation: List<Pair<String, String>>? = null
    private var pendingSmsDisambiguationBody: String? = null

    private fun expandIntoPoliteMessage(recipient: String, intent: String): String {
        val trimmed = intent.trim().trimEnd('.', '!', '?')
        val lower = trimmed.lowercase(Locale.ROOT)
        val firstName = recipient.split(" ").firstOrNull()?.replaceFirstChar { it.uppercase() } ?: recipient

        return when {
            lower.contains("happy birthday") || lower.contains("birthday") || lower.contains("janmadin") ->
                "Hi $firstName, wishing you a very happy birthday! Hope you have a wonderful and joyous year ahead."
            lower.contains("meeting") || lower.contains("schedule") || lower.contains("reschedule") ->
                "Hi $firstName, just wanted to check in regarding our meeting. Please let me know what time works best for you."
            lower.contains("call me") || lower.contains("call when") || lower.contains("give me a call") || lower == "call" || lower.contains("call back") ->
                "Hi $firstName, please give me a call whenever you have a moment. Thank you!"
            lower.contains("reached") || lower.contains("arrived") || lower.contains("pahunch") ->
                "Hi $firstName, just wanted to let you know that I have reached safely."
            lower.contains("running late") || lower.contains("late") || lower.contains("traffic") || lower.contains("stuck") ->
                "Hi $firstName, I am running a few minutes late. I will be there as soon as possible."
            lower.contains("thank") || lower.contains("shukriya") || lower.contains("dhanyawad") ->
                "Hi $firstName, thank you so much for your help. Really appreciate it!"
            lower.contains("good morning") || lower.contains("shubh prabhat") ->
                "Hi $firstName, good morning! Hope you have a productive day ahead."
            lower.contains("good night") || lower.contains("shubh ratri") ->
                "Hi $firstName, wishing you a good night and restful sleep."
            lower.startsWith("hi ") || lower.startsWith("hello ") || lower.startsWith("hey ") ->
                trimmed
            else -> {
                val capitalized = trimmed.replaceFirstChar { if (it.isLowerCase()) it.titlecase(Locale.ROOT) else it.toString() }
                "Hi $firstName, $capitalized."
            }
        }
    }

    private fun resolveDisambiguationOption(qLower: String, candidates: List<Pair<String, String>>): Pair<String, String>? {
        if (candidates.isEmpty()) return null

        // 1. Ordinal / Index matching ("first", "1", "second", "2", "option 1", "pehla", "doosra")
        val ordinalMap = mapOf(
            "first" to 0, "1st" to 0, "1" to 0, "one" to 0, "pehla" to 0, "option 1" to 0, "option one" to 0,
            "second" to 1, "2nd" to 1, "2" to 1, "two" to 1, "doosra" to 1, "option 2" to 0, "option two" to 1,
            "third" to 2, "3rd" to 2, "3" to 2, "three" to 2, "teesra" to 2, "option 3" to 2,
            "fourth" to 3, "4th" to 3, "4" to 3, "four" to 3, "chautha" to 3,
            "fifth" to 4, "5th" to 4, "5" to 4, "five" to 4
        )

        for ((key, idx) in ordinalMap) {
            if (qLower.contains(key) || qLower == key) {
                if (idx in candidates.indices) {
                    return candidates[idx]
                }
            }
        }

        // 2. Direct name or substring matching
        for (cand in candidates) {
            val nameLower = cand.first.lowercase()
            val surname = if (nameLower.contains(" ")) nameLower.substringAfterLast(" ") else ""
            if (qLower.contains(nameLower) || (surname.isNotEmpty() && qLower.contains(surname))) {
                return cand
            }
        }

        // 3. Phone type / number matching
        for (cand in candidates) {
            val phoneClean = cand.second.replace(Regex("""[^\d]"""), "")
            if (phoneClean.isNotEmpty() && qLower.contains(phoneClean)) {
                return cand
            }
        }

        return null
    }

    private val contactSmsPatterns = listOf(
        Regex("""(?:did|has)\s+([a-zA-Z0-9\s]+?)\s+(?:message|text|sms)(?:\s+me)?\??$"""),
        Regex("""(?:any\s+(?:new\s+)?(?:messages?|sms|texts?)\s+(?:from|by)\s+([a-zA-Z0-9\s]+?))\??$"""),
        Regex("""(?:read|check|show)\s+(?:recent\s+|latest\s+)?(?:messages?|sms|texts?)\s+(?:from|by)\s+([a-zA-Z0-9\s]+?)\??$"""),
        Regex("""(?:messages?|sms|texts?)\s+(?:from|by)\s+([a-zA-Z0-9\s]+?)\??$"""),
        Regex("""([a-zA-Z0-9\s]+?)\s+(?:ka|se)\s+(?:sms|message|text)"""),
        Regex("""([a-zA-Z0-9\s]+?)\s+ne\s+(?:sms|message|text)\s+(?:bheja|bheja\s+kya)""")
    )

    private val openDraftSmsPatterns = listOf(
        Regex("""^(?:draft|write|compose)\s+(?:an?\s+)?(?:sms|message|text)\s+(?:to|for)\s+([a-zA-Z0-9\s]+?)$"""),
        Regex("""^(?:draft|write|compose)\s+to\s+([a-zA-Z0-9\s]+?)$"""),
        Regex("""^(?:send|draft)\s+([a-zA-Z0-9\s]+?)\s+(?:an?\s+)?(?:sms|message|text)$"""),
        Regex("""^([a-zA-Z0-9\s]+?)\s+ko\s+(?:message|sms|text)\s+(?:draft|karna|likhna|bhejna)"""),
        Regex("""^([a-zA-Z0-9\s]+?)\s+ko\s+(?:message|sms|text)\s+bhejo$""")
    )

    private val composeSmsPatterns = listOf(
        Regex("""^(?:send|compose|draft|write)\s+(?:an?\s+)?(?:sms|message|text)\s+(?:to|for)\s+([a-zA-Z0-9\s]+?)\s+(?:saying|that|:)\s+(.+)$"""),
        Regex("""^(?:send|draft|write)\s+to\s+([a-zA-Z0-9\s]+?)\s+(?:saying|that|:)\s+(.+)$"""),
        Regex("""^(?:text|message)\s+([a-zA-Z0-9\s]+?)\s+(?:saying|that|:)\s+(.+)$""")
    )

    private val paginationKeywords = listOf(
        "other message", "other messages", "next message", "read next message", "next sms",
        "read other", "more messages", "previous message", "purane message", "doosra message",
        "aur message", "read more messages"
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
        if (paginationKeywords.any { qLower.contains(it) }) {
            return true
        }
        if (openDraftSmsPatterns.any { it.containsMatchIn(qLower) }) {
            return true
        }
        if (composeSmsPatterns.any { it.containsMatchIn(qLower) }) {
            return true
        }
        return contactSmsPatterns.any { it.containsMatchIn(qLower) }
    }

    private fun handleLocalSmsQuery(query: String, sessionId: String, tStart: Long): WearableResponse {
        val ctx = context
        val qLower = query.lowercase().trim()
        val latMs = (System.currentTimeMillis() - tStart).toDouble().coerceAtLeast(1.0)

        // 1. Handle 'who sent it' follow-up
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

        // 2. Handle 'reply that ...' follow-up
        if (qLower.startsWith("reply")) {
            val replyBody = qLower.removePrefix("reply").removePrefix(" to him").removePrefix(" that").trim()
            val target = lastReadSmsSender ?: "contact"
            val politeReply = expandIntoPoliteMessage(target, replyBody)
            pendingSendMessage = politeReply
            pendingSendPhone = lastReadSmsPhone
            pendingSendRecipient = target
            return WearableResponse(
                text = "I have prepared an SMS to $target: '$politeReply'. Should I send it?",
                sessionId = sessionId,
                source = ResponseSource.TOOL,
                unifiedSource = UnifiedSource.TOOL,
                requiresConfirmation = true,
                confirmationPrompt = "Send SMS to $target: '$politeReply'?",
                confirmationActionId = "sms_reply_${System.currentTimeMillis()}",
                capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                latencyMs = latMs
            )
        }

        // 2.5 Handle Open-Ended Multi-Turn Draft SMS: "draft a message to Papa"
        for (pattern in openDraftSmsPatterns) {
            val match = pattern.find(qLower)
            if (match != null) {
                val recipient = match.groupValues[1].trim()
                val matchedContacts = if (ctx != null && SmsManagerHelper.hasContactsPermission(ctx)) {
                    SmsManagerHelper.findPhoneNumbersForContact(ctx, recipient)
                } else emptyList()

                val distinctNames = matchedContacts.map { it.first }.distinct()
                if (distinctNames.size > 1) {
                    pendingSmsDisambiguation = matchedContacts
                    pendingSmsDisambiguationBody = null
                    val namesList = distinctNames.joinToString(" or ")
                    return WearableResponse(
                        text = "I found multiple contacts for '$recipient': $namesList. Which one would you like to message?",
                        sessionId = sessionId,
                        source = ResponseSource.TOOL,
                        unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                        capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                        latencyMs = latMs
                    )
                }
                if (matchedContacts.size > 1) {
                    pendingSmsDisambiguation = matchedContacts
                    pendingSmsDisambiguationBody = null
                    val numbersList = matchedContacts.mapIndexed { idx, pair -> "option ${idx + 1}: ${pair.second}" }.joinToString(" or ")
                    return WearableResponse(
                        text = "I found multiple numbers for '${matchedContacts.first().first}': $numbersList. Which one would you like to message?",
                        sessionId = sessionId,
                        source = ResponseSource.TOOL,
                        unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                        capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                        latencyMs = latMs
                    )
                }

                val destPhone = if (matchedContacts.isNotEmpty()) {
                    matchedContacts.first().second
                } else if (recipient.replace(Regex("""[\s\-]"""), "").all { it.isDigit() || it == '+' }) {
                    recipient.replace(Regex("""[\s\-]"""), "")
                } else {
                    null
                }

                val resolvedName = (if (matchedContacts.isNotEmpty()) matchedContacts.first().first else recipient)
                    .replaceFirstChar { if (it.isLowerCase()) it.titlecase(Locale.ROOT) else it.toString() }
                pendingDraftRecipient = resolvedName
                pendingDraftPhone = destPhone

                return WearableResponse(
                    text = "Certainly! What message would you like to draft for $resolvedName?",
                    sessionId = sessionId,
                    source = ResponseSource.TOOL,
                    unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                    capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                    latencyMs = latMs
                )
            }
        }

        // 3. Handle Compose / Send SMS with Body: "send message to Papa saying I reached"
        for (pattern in composeSmsPatterns) {
            val match = pattern.find(qLower)
            if (match != null) {
                val recipient = match.groupValues[1].trim()
                val body = match.groupValues[2].trim()

                val matchedContacts = if (ctx != null && SmsManagerHelper.hasContactsPermission(ctx)) {
                    SmsManagerHelper.findPhoneNumbersForContact(ctx, recipient)
                } else emptyList()

                val distinctNames = matchedContacts.map { it.first }.distinct()
                val resolvedName = (if (matchedContacts.isNotEmpty()) matchedContacts.first().first else recipient)
                    .replaceFirstChar { if (it.isLowerCase()) it.titlecase(Locale.ROOT) else it.toString() }
                val politeBody = expandIntoPoliteMessage(resolvedName, body)

                if (distinctNames.size > 1) {
                    pendingSmsDisambiguation = matchedContacts
                    pendingSmsDisambiguationBody = politeBody
                    val namesList = distinctNames.joinToString(" or ")
                    return WearableResponse(
                        text = "I found multiple contacts for '$recipient': $namesList. Which one would you like to message?",
                        sessionId = sessionId,
                        source = ResponseSource.TOOL,
                        unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                        capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                        latencyMs = latMs
                    )
                }
                if (matchedContacts.size > 1) {
                    pendingSmsDisambiguation = matchedContacts
                    pendingSmsDisambiguationBody = politeBody
                    val numbersList = matchedContacts.mapIndexed { idx, pair -> "option ${idx + 1}: ${pair.second}" }.joinToString(" or ")
                    return WearableResponse(
                        text = "I found multiple numbers for '${matchedContacts.first().first}': $numbersList. Which one would you like to message?",
                        sessionId = sessionId,
                        source = ResponseSource.TOOL,
                        unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                        capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                        latencyMs = latMs
                    )
                }

                val destPhone = if (matchedContacts.isNotEmpty()) {
                    matchedContacts.first().second
                } else if (recipient.replace(Regex("""[\s\-]"""), "").all { it.isDigit() || it == '+' }) {
                    recipient.replace(Regex("""[\s\-]"""), "")
                } else {
                    null
                }

                pendingSendMessage = politeBody
                pendingSendPhone = destPhone
                pendingSendRecipient = resolvedName
                return WearableResponse(
                    text = "I have drafted a message to $resolvedName: '$politeBody'. Shall I send it?",
                    sessionId = sessionId,
                    source = ResponseSource.TOOL,
                    unifiedSource = UnifiedSource.TOOL,
                    requiresConfirmation = true,
                    confirmationPrompt = "Send SMS to $resolvedName: '$politeBody'?",
                    confirmationActionId = "sms_send_${System.currentTimeMillis()}",
                    capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                    latencyMs = latMs
                )
            }
        }

        // Reading SMS requires Context and READ_SMS permission
        if (ctx == null) {
            return WearableResponse(
                text = "I can't access your messages right now.",
                sessionId = sessionId,
                source = ResponseSource.UNAVAILABLE,
                unifiedSource = UnifiedSource.UNAVAILABLE,
                capabilityStatus = ResponseCapabilityStatus.FAILED,
                latencyMs = latMs
            )
        }

        if (!SmsManagerHelper.hasReadPermission(ctx)) {
            return WearableResponse(
                text = "I don't have permission to read your messages.",
                sessionId = sessionId,
                source = ResponseSource.TOOL,
                unifiedSource = UnifiedSource.TOOL,
                capabilityStatus = ResponseCapabilityStatus.REQUIRES_PERMISSION,
                latencyMs = latMs
            )
        }

        // 4. Handle Pagination: "other messages", "next message", "read more"
        if (paginationKeywords.any { qLower.contains(it) }) {
            if (lastReadSmsList.isEmpty()) {
                lastReadSmsList = SmsManagerHelper.readRecentMessages(ctx, limit = 10)
                lastReadSmsIndex = 0
            }
            val nextIdx = lastReadSmsIndex + 1
            if (nextIdx < lastReadSmsList.size) {
                lastReadSmsIndex = nextIdx
                val msg = lastReadSmsList[nextIdx]
                val sender = msg.contactName ?: msg.address
                lastReadSmsSender = sender
                lastReadSmsPhone = msg.address
                return WearableResponse(
                    text = "Message ${nextIdx + 1} from $sender: ${msg.body}",
                    sessionId = sessionId,
                    source = ResponseSource.TOOL,
                    unifiedSource = UnifiedSource.TOOL,
                    capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                    latencyMs = latMs
                )
            } else {
                return WearableResponse(
                    text = "You don't have any other unread messages.",
                    sessionId = sessionId,
                    source = ResponseSource.TOOL,
                    unifiedSource = UnifiedSource.TOOL,
                    capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                    latencyMs = latMs
                )
            }
        }

        // 5. Contact-specific query: "messages from Papa"
        var targetContact: String? = null
        for (pattern in contactSmsPatterns) {
            val match = pattern.find(qLower)
            if (match != null) {
                targetContact = match.groupValues[1].trim()
                break
            }
        }

        if (!targetContact.isNullOrBlank()) {
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

            val messages = SmsManagerHelper.searchMessages(ctx, targetContact, limit = 5)
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

            lastReadSmsList = messages
            lastReadSmsIndex = 0
            val latest = messages.first()
            val sender = latest.contactName ?: latest.address
            lastReadSmsSender = sender
            lastReadSmsPhone = latest.address

            val text = if (messages.size == 1) {
                "Message from $sender: ${latest.body}"
            } else {
                "You have ${messages.size} messages from $sender. Latest: ${latest.body}. Say 'next message' to hear more."
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

        // 6. General recent messages query with On-Device Spam & Ad Filter
        val wantsPromos = qLower.contains("promo") || qLower.contains("advertisement") || qLower.contains("ad") || qLower.contains("spam")
        val (messages, filteredCount) = SmsManagerHelper.readFilteredMessages(ctx, limit = 10, includePromotions = wantsPromos)
        if (messages.isEmpty()) {
            val emptyMsg = if (filteredCount > 0) {
                "You have no personal messages ($filteredCount promotional messages filtered out)."
            } else {
                "You don't have any messages right now."
            }
            return WearableResponse(
                text = emptyMsg,
                sessionId = sessionId,
                source = ResponseSource.TOOL,
                unifiedSource = UnifiedSource.TOOL,
                capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                latencyMs = latMs
            )
        }

        lastReadSmsList = messages
        lastReadSmsIndex = 0
        val latest = messages.first()
        val sender = latest.contactName ?: latest.address
        lastReadSmsSender = sender
        lastReadSmsPhone = latest.address

        val filterSuffix = if (filteredCount > 0 && !wantsPromos) " ($filteredCount promotions filtered)." else ""
        val text = if (messages.size == 1) {
            "You have 1 message from $sender: ${latest.body}$filterSuffix"
        } else {
            "You have ${messages.size} messages$filterSuffix. Latest from $sender: ${latest.body}. Say 'next message' to hear more."
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
        val callMatch = Regex("""^(?:call|phone|dial|make a call to)\s+([a-zA-Z0-9\s\-+]+?)(?:\s+please|\s+now)?$""").find(qLower)
        if (callMatch != null) {
            val target = callMatch.groupValues[1].trim()
            val cleanTarget = target.replace(Regex("""[\s\-]"""), "")
            val isNumeric = cleanTarget.isNotEmpty() && cleanTarget.all { it.isDigit() || it == '+' }

            // 4A. Direct phone number dialing & 10-digit safety rule
            if (isNumeric) {
                val pureDigits = cleanTarget.filter { it.isDigit() }
                val emergencyNumbers = setOf("100", "101", "102", "108", "112", "911", "1091", "1098")
                if (pureDigits in emergencyNumbers) {
                    callController?.makeCall(cleanTarget)
                    return WearableResponse(
                        text = "Calling emergency services at $cleanTarget.",
                        sessionId = sessionId,
                        source = ResponseSource.TOOL,
                        unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                        capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                        latencyMs = latMs
                    )
                } else if (pureDigits.length < 10) {
                    return WearableResponse(
                        text = "The number $cleanTarget has only ${pureDigits.length} digits, which is less than the standard 10-digit format. Shall I proceed to call anyway?",
                        sessionId = sessionId,
                        source = ResponseSource.TOOL,
                        unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                        requiresConfirmation = true,
                        confirmationPrompt = "Call $cleanTarget (${pureDigits.length} digits)?",
                        confirmationActionId = "call_dial_$cleanTarget",
                        capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                        latencyMs = latMs
                    )
                } else {
                    callController?.makeCall(cleanTarget)
                    return WearableResponse(
                        text = "Calling $cleanTarget.",
                        sessionId = sessionId,
                        source = ResponseSource.TOOL,
                        unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                        capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                        latencyMs = latMs
                    )
                }
            }

            // 4B. Contact Lookup & Disambiguation
            val ctx = context
            if (ctx != null) {
                val matchedContacts = SmsManagerHelper.findPhoneNumbersForContact(ctx, target)
                val distinctNames = matchedContacts.map { it.first }.distinct()
                if (distinctNames.size > 1) {
                    pendingCallDisambiguation = matchedContacts
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
                if (matchedContacts.size > 1) {
                    pendingCallDisambiguation = matchedContacts
                    val numbersList = matchedContacts.mapIndexed { idx, pair -> "option ${idx + 1}: ${pair.second}" }.joinToString(" or ")
                    return WearableResponse(
                        text = "I found multiple numbers for '${matchedContacts.first().first}': $numbersList. Which one would you like to call?",
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
            // If contact not directly resolved locally, return clean message
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
            "search the web", "web search", "google search", "search for", "who won the", "weather",
            "research paper", "research on", "arxiv", "semantic scholar", "paper on", "papers on",
            "pet shop", "kaha hai", "kahan hai", "near me", "best shop", "best restaurant",
            "python", "calculator", "write a", "plan a trip", "trip plan",
            "click the pic", "click the picture", "take a picture", "take picture", "take photo", "click photo",
            "capture image", "camera snapshot", "photo kheecho", "tasveer lo",
            "explain the pic", "explain picture", "what do you see", "what is this", "describe photo",
            "explain what you see", "what is in front of me", "describe what is in front of me",
            "what's in front of me", "kya dikh raha hai", "tasveer samjhao"
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
