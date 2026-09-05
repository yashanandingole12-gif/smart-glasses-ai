package com.smartglasses.ai.domain.usecases

import com.smartglasses.ai.domain.models.FailureCategory
import com.smartglasses.ai.domain.models.ResponseSource
import com.smartglasses.ai.domain.models.WearableResponse
import com.smartglasses.ai.domain.models.WearableTelemetry
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class LocalDeterministicResolver {

    fun resolve(
        query: String,
        telemetry: WearableTelemetry,
        sessionId: String,
        language: String? = "auto"
    ): WearableResponse? {
        val q = query.trim().lowercase(Locale.ROOT).replace(Regex("[?.!,]"), "").trim()
        if (q.isBlank()) return null

        val tStart = System.currentTimeMillis()

        // 1. Time queries
        val timePatterns = listOf(
            "what time is it", "whats the time", "what is the time", "time please",
            "tell me the time", "current time", "what time", "time now", "time",
            "kitne baje", "time kya hua", "kya time hai", "kiti vaajle", "kitne baje hai",
            "कितने बजे हैं", "समय क्या है", "टाइम क्या हुआ", "टाइम क्या है", "आता किती वाजले", "वेळ काय झाली"
        )
        if (timePatterns.any { q == it || q.startsWith(it) || q.endsWith(it) }) {
            val timeStr = if (telemetry.timeFormatted.isNotBlank()) telemetry.timeFormatted else {
                SimpleDateFormat("h:mm a", Locale.getDefault()).format(Date())
            }
            val text = when {
                q.contains("बजे") || q.contains("समय") || q.contains("टाइम") -> "अभी $timeStr बजे हैं।"
                q.contains("वाजले") || q.contains("वेळ") -> "आता $timeStr वाजले आहेत."
                q.contains("kya") || q.contains("kitne") -> "Abhi $timeStr hue hain."
                else -> "It's $timeStr."
            }
            return buildResponse(text, sessionId, tStart)
        }

        // 2. Date queries
        val datePatterns = listOf(
            "whats the date", "what is the date", "whats todays date", "what is todays date",
            "today date", "todays date", "what day is today", "what day is it", "what is today",
            "date today", "aaj konsi date hai", "aaj ki date", "आज कौन सी तारीख है", "आजची तारीख काय आहे"
        )
        if (datePatterns.any { q == it || q.startsWith(it) || q.endsWith(it) }) {
            val sdf = SimpleDateFormat("EEEE, MMMM d, yyyy", Locale.US)
            val dateStr = sdf.format(Date())
            val text = when {
                q.contains("तारीख") -> "आज की तारीख $dateStr है।"
                q.contains("aaj") -> "Aaj $dateStr hai."
                else -> "Today is $dateStr."
            }
            return buildResponse(text, sessionId, tStart)
        }

        // 3. Battery queries
        val batteryPatterns = listOf(
            "whats my battery", "what is my battery", "battery percentage", "battery level",
            "battery status", "check battery", "how much battery", "my battery", "battery",
            "battery percent", "battery kitni hai", "battery kitna hai",
            "बैटरी कितनी है", "बैटरी लेवल", "बॅटरी किती आहे"
        )
        if (batteryPatterns.any { q == it || q.startsWith(it) || q.endsWith(it) }) {
            val bat = telemetry.batteryPercentage
            val text = when {
                q.contains("बैटरी") -> "आपकी बैटरी $bat प्रतिशत है।"
                q.contains("बॅटरी") -> "तुमची बॅटरी $bat टक्के आहे."
                q.contains("kitni") || q.contains("kitna") -> "Battery $bat percent hai."
                else -> "Battery is $bat percent."
            }
            return buildResponse(text, sessionId, tStart)
        }

        // 4. Location queries
        val locationPatterns = listOf(
            "where am i", "what is my location", "whats my location", "current location",
            "my location", "where are we", "location", "meri location", "kahan hoon",
            "main kahan hoon", "kaha hu", "मैं कहाँ हूँ", "मी कुठे आहे", "स्थान काय आहे"
        )
        if (locationPatterns.any { q == it || q.startsWith(it) || q.endsWith(it) }) {
            val loc = telemetry.locationName
            val hasLoc = telemetry.locationAvailable && loc != "Unavailable" && loc != "Unknown"
            val text = when {
                hasLoc && (q.contains("कहाँ") || q.contains("kahan")) -> "आप अभी $loc में हैं।"
                hasLoc && q.contains("कुठे") -> "तुम्ही आता $loc मध्ये आहात."
                hasLoc -> "You are currently in $loc."
                q.contains("कहाँ") || q.contains("kahan") -> "लोकेशन अभी उपलब्ध नहीं है।"
                else -> "Location is currently unavailable."
            }
            return buildResponse(text, sessionId, tStart)
        }

        // 5. Basic greetings
        val greetingPatterns = listOf(
            "good morning", "good afternoon", "good evening", "good night", "hello", "hi",
            "hey assistant", "hey glasses", "सुप्रभात", "नमस्ते", "शुभ सकाळ", "नमस्कार"
        )
        if (greetingPatterns.any { q == it || q == "hey" }) {
            val period = telemetry.period
            val text = when {
                q.contains("सुप्रभात") || q.contains("नमस्ते") -> "सुप्रभात! मैं आपकी क्या मदद कर सकता हूँ?"
                q.contains("सकाळ") || q.contains("नमस्कार") -> "शुभ सकाळ! मी काय मदत करू शकतो?"
                period == "night" -> "Good evening. How may I assist?"
                else -> "Good $period. How may I assist?"
            }
            return buildResponse(text, sessionId, tStart)
        }

        // 6. Acknowledgements and status
        if (q in listOf("thank you", "thanks", "thank you assistant", "dhanyawad", "shukriya")) {
            return buildResponse("You're welcome.", sessionId, tStart)
        }

        if (q in listOf("stop", "cancel", "dismiss", "chup")) {
            return buildResponse("Stopped.", sessionId, tStart)
        }

        if (q in listOf("status", "device status", "system status")) {
            val bat = telemetry.batteryPercentage
            return buildResponse("System operational. Battery is $bat percent.", sessionId, tStart)
        }

        return null
    }

    private fun buildResponse(text: String, sessionId: String, tStart: Long): WearableResponse {
        val latMs = (System.currentTimeMillis() - tStart).toDouble().coerceAtLeast(1.0)
        return WearableResponse(
            text = text,
            sessionId = sessionId,
            requiresConfirmation = false,
            confirmationPrompt = null,
            confirmationActionId = null,
            sources = listOf("local_deterministic"),
            latencyMs = latMs,
            failureCategory = FailureCategory.NONE,
            tierUsed = "LOCAL_DETERMINISTIC",
            source = ResponseSource.LOCAL_DETERMINISTIC
        )
    }
}
