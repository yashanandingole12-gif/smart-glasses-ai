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

        // 0. Handle Confirmation of Pending Actions (SMS Dispatch, Call Confirmation, etc.)
        if (confirmedAction == true && confirmedActionId != null) {
            val ctx = context
            if (confirmedActionId.startsWith("call_dial_")) {
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
            if (ctx != null && confirmedActionId.startsWith("sms_")) {
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
        val lifecycleGreetings = listOf("hey lara", "hi lara", "hello lara", "lara", "wake up lara", "hey assistant")
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
                text = "Hello! LARA is active and ready. Battery is at $bat%.$unreadPart How can I help you today?",
                sessionId = sessionId,
                source = ResponseSource.LOCAL_DETERMINISTIC,
                unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                latencyMs = (System.currentTimeMillis() - tStart).toDouble().coerceAtLeast(1.0)
            )
        }

        val lifecycleDismiss = listOf("goodbye lara", "bye lara", "sleep lara", "shutdown lara", "turn off lara", "goodbye", "alvida")
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
                text = "Goodbye! Putting LARA to sleep. Say 'Hey LARA' whenever you need me.",
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

    private var lastReadSmsIndex: Int = 0
    private var lastReadSmsList: List<com.smartglasses.ai.core.sms.SmsItem> = emptyList()
    private var lastReadSmsSender: String? = null
    private var lastReadSmsPhone: String? = null
    private var pendingSendMessage: String? = null
    private var pendingSendPhone: String? = null
    private var pendingSendRecipient: String? = null
    private var pendingCallDisambiguation: List<Pair<String, String>>? = null
    private var pendingSmsDisambiguation: List<Pair<String, String>>? = null
    private var pendingSmsDisambiguationBody: String? = null

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

    private val composeSmsPatterns = listOf(
        Regex("""^(?:send|compose)\s+(?:an?\s+)?(?:sms|message|text)\s+to\s+([a-zA-Z0-9\s]+?)\s+(?:saying|that|:)\s+(.+)$"""),
        Regex("""^(?:send\s+to)\s+([a-zA-Z0-9\s]+?)\s+(?:saying|that|:)\s+(.+)$"""),
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
        if (composeSmsPatterns.any { it.containsMatchIn(qLower) }) {
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
            pendingSendMessage = replyBody
            pendingSendPhone = lastReadSmsPhone
            pendingSendRecipient = target
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

        // 3. Handle Compose / Send SMS: "send message to Papa saying I reached"
        for (pattern in composeSmsPatterns) {
            val match = pattern.find(qLower)
            if (match != null) {
                val recipient = match.groupValues[1].trim()
                val body = match.groupValues[2].trim()

                val matchedContacts = SmsManagerHelper.findPhoneNumbersForContact(ctx, recipient)
                val distinctNames = matchedContacts.map { it.first }.distinct()
                if (distinctNames.size > 1) {
                    pendingSmsDisambiguation = matchedContacts
                    pendingSmsDisambiguationBody = body
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
                    pendingSmsDisambiguationBody = body
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

                val resolvedName = if (matchedContacts.isNotEmpty()) matchedContacts.first().first else recipient

                if (destPhone != null) {
                    pendingSendMessage = body
                    pendingSendPhone = destPhone
                    pendingSendRecipient = resolvedName
                    return WearableResponse(
                        text = "I have drafted a message to $resolvedName: '$body'. Shall I send it?",
                        sessionId = sessionId,
                        source = ResponseSource.TOOL,
                        unifiedSource = UnifiedSource.TOOL,
                        requiresConfirmation = true,
                        confirmationPrompt = "Send SMS to $resolvedName: '$body'?",
                        confirmationActionId = "sms_send_${System.currentTimeMillis()}",
                        capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                        latencyMs = latMs
                    )
                } else {
                    return WearableResponse(
                        text = "I couldn't find a phone number for $recipient.",
                        sessionId = sessionId,
                        source = ResponseSource.TOOL,
                        unifiedSource = UnifiedSource.LOCAL_DETERMINISTIC,
                        capabilityStatus = ResponseCapabilityStatus.ANSWERED,
                        latencyMs = latMs
                    )
                }
            }
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
