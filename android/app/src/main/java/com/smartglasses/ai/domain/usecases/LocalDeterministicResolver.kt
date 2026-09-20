package com.smartglasses.ai.domain.usecases

import com.smartglasses.ai.domain.models.FailureCategory
import com.smartglasses.ai.domain.models.ResponseSource
import com.smartglasses.ai.domain.models.WearableResponse
import com.smartglasses.ai.domain.models.WearableTelemetry
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class LocalDeterministicResolver {

    companion object {
        // Offline Definitional Dictionary (sub-10ms, zero LLM dependency)
        private val DEFINITIONS = mapOf(
            "array" to "An array is a linear data structure that stores elements of the same type in contiguous memory locations, accessible by numerical index.",
            "data structure" to "A data structure is a specialized format for organizing, processing, retrieving, and storing data efficiently.",
            "node" to "A node is a fundamental building block in data structures like linked lists, trees, and graphs that contains data and references or pointers to other nodes.",
            "wifi" to "Wi-Fi is a wireless networking technology that uses radio frequencies to connect devices to local area networks and the internet.",
            "wi-fi" to "Wi-Fi is a wireless networking technology that uses radio frequencies to connect devices to local area networks and the internet.",
            "internet" to "The Internet is a global system of interconnected computer networks that communicate using the standard Internet Protocol Suite (TCP/IP).",
            "google" to "Google is a multinational technology company specializing in online search, cloud computing, software, hardware, and artificial intelligence.",
            "class" to "In object-oriented programming, a class is an extensible program-code template for creating objects, defining initial state and implementations of behavior.",
            "sql" to "SQL (Structured Query Language) is a standardized programming language used to manage, query, and manipulate relational databases.",
            "select" to "In SQL, the SELECT statement is used to fetch data from one or more tables in a database.",
            "insert" to "In SQL, the INSERT statement is used to add new records or rows to a database table.",
            "update" to "In SQL, the UPDATE statement modifies existing data within specified columns of a database table.",
            "delete" to "In SQL, the DELETE statement removes existing records from a database table based on specified conditions.",
            "where" to "In SQL, the WHERE clause filters records to extract only those that satisfy a specified condition.",
            "join" to "In SQL, a JOIN clause combines rows from two or more tables based on a related column between them.",
            "stack" to "A stack is a linear data structure following the LIFO (Last-In, First-Out) principle, supporting push and pop operations.",
            "queue" to "A queue is a linear data structure following the FIFO (First-In, First-Out) principle, supporting enqueue and dequeue operations.",
            "binary tree" to "A binary tree is a hierarchical tree data structure in which each node has at most two children, referred to as left and right child.",
            "algorithm" to "An algorithm is a step-by-step procedure or set of rules designed to solve a specific problem or perform a computation.",
            "api" to "An API (Application Programming Interface) is a set of defined rules and protocols that enables different software applications to communicate with each other.",
            "http" to "HTTP (Hypertext Transfer Protocol) is the application layer protocol used for transmitting hypermedia documents, such as HTML, over the World Wide Web.",
            "database" to "A database is an organized collection of structured data stored electronically and accessed via a database management system (DBMS)."
        )
    }

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

        // 5. Basic greetings & Conversation Control
        val greetingPatterns = listOf(
            "good morning", "good afternoon", "good evening", "good night", "hello", "hi",
            "hey eva", "hey assistant", "hey glasses", "सुप्रभात", "नमस्ते", "शुभ सकाळ", "नमस्कार"
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

        if (q in listOf("thank you", "thanks", "thank you eva", "dhanyawad", "shukriya")) {
            return buildResponse("You're welcome.", sessionId, tStart)
        }

        if (q in listOf("stop", "cancel", "dismiss", "chup", "shant", "pause", "resume", "clear")) {
            return buildResponse("Stopped.", sessionId, tStart)
        }

        if (q in listOf("status", "device status", "system status", "connectivity status", "wifi status")) {
            val bat = telemetry.batteryPercentage
            val glassesStatus = if (telemetry.glassesConnected) "Glasses connected" else "Glasses standalone"
            return buildResponse("System operational. Battery $bat%. $glassesStatus.", sessionId, tStart)
        }

        // 6. Definitional Questions (Offline Dictionary)
        val defMatch = Regex("""^(?:what\s+is\s+(?:an?|the)?|define|explain\s+(?:an?|the)?|definition\s+of)\s+([a-z\s-]+)$""").find(q)
        if (defMatch != null) {
            val term = defMatch.groupValues[1].trim()
            val definition = DEFINITIONS[term] ?: DEFINITIONS[term.replace("-", "")] ?: DEFINITIONS[term.replace(" ", "")]
            if (definition != null) {
                return buildResponse(definition, sessionId, tStart)
            }
        }
        // Direct term definition check
        if (DEFINITIONS.containsKey(q)) {
            return buildResponse(DEFINITIONS[q]!!, sessionId, tStart)
        }

        // 7. Device Call & Telephony Commands
        if (q in listOf("answer call", "answer the call", "pick up", "accept call", "pick call")) {
            return buildResponse("Answering the incoming call.", sessionId, tStart)
        }
        if (q in listOf("decline call", "decline the call", "reject call", "hang up", "cut call", "end call")) {
            return buildResponse("Call declined.", sessionId, tStart)
        }

        // 8. Device Messages & Notifications
        if (q in listOf("check notifications", "read notifications", "notifications", "unread notifications")) {
            return buildResponse("Checking your recent notifications.", sessionId, tStart)
        }
        if (q in listOf("check messages", "read messages", "unread messages", "inbox")) {
            return buildResponse("Checking your recent SMS messages.", sessionId, tStart)
        }

        // 9. Local Document & File Search
        val fileSearchMatch = Regex("""^(?:search\s+files?|find\s+files?|search\s+documents?|find\s+documents?)\s*(?:for\s+)?(.*)$""").find(q)
        if (fileSearchMatch != null) {
            val queryTerm = fileSearchMatch.groupValues[1].trim()
            val text = if (queryTerm.isNotBlank()) "Searching local storage for '$queryTerm'." else "Searching device files."
            return buildResponse(text, sessionId, tStart)
        }

        // 10. Camera Photo Capture Commands
        val photoPatterns = listOf(
            "take a picture", "take a photo", "take photo", "take pic", "take the pic", "take the picture",
            "click a picture", "click a photo", "click photo", "click pic", "click the pic", "click the picture",
            "click the photo", "capture photo", "capture a photo", "capture picture", "capture the picture",
            "snap a photo", "snap picture", "photo kheecho", "photo khicho", "photo click karo",
            "picture lo", "tasveer kheecho", "tasveer lo", "save photo to gallery", "save picture to gallery",
            "save photo"
        )
        if (photoPatterns.any { q == it || q.startsWith(it) || q.endsWith(it) || q.contains(it) }) {
            return buildResponse("Photo captured and saved to your Gallery.", sessionId, tStart)
        }

        // 11. Deterministic Math Engine (<5ms on-device)
        if (!listOf("python", "code", "script", "program", "app", "write", "build", "create", "plan", "trip", "shop").any { q.contains(it) }) {
            val mathResult = resolveMath(query)
            if (mathResult != null) {
                return buildResponse(mathResult, sessionId, tStart)
            }
        }

        return null
    }

    private fun resolveMath(raw: String): String? {
        val q = raw.trim().lowercase(Locale.ROOT)

        // Tables: "table of 7", "7 ka table", "7 times table"
        val tableMatch = Regex("""(?:table\s+of\s+|table\s+)(\d+)""").find(q)
            ?: Regex("""(\d+)\s*(?:ka|cha|ke)\s+table""").find(q)
            ?: Regex("""(\d+)\s+times\s+table""").find(q)
        if (tableMatch != null) {
            val n = tableMatch.groupValues[1].toLongOrNull() ?: return null
            if (n in 1..1000) {
                val vals = (1..10).map { "$it × $n = ${it * n}" }.joinToString(", ")
                return "The table of $n is $vals."
            }
        }

        // Percentage: "15% of 800", "15 percent of 800"
        val pctMatch = Regex("""([\d,.]+)\s*(?:%|percent)\s+of\s+([\d,.]+)""").find(q)
        if (pctMatch != null) {
            val pct = pctMatch.groupValues[1].replace(",", "").toDoubleOrNull() ?: return null
            val base = pctMatch.groupValues[2].replace(",", "").toDoubleOrNull() ?: return null
            val ans = base * (pct / 100.0)
            val ansFmt = if (ans % 1.0 == 0.0) ans.toLong().toString() else "%.2f".format(ans)
            return "$pct% of $base is $ansFmt."
        }

        // Reciprocals: "reciprocal of 5", "1/8"
        val recipMatch = Regex("""reciprocal\s+of\s+([\d,.]+)""").find(q)
        if (recipMatch != null) {
            val v = recipMatch.groupValues[1].replace(",", "").toDoubleOrNull() ?: return null
            if (v == 0.0) return "The reciprocal of zero is undefined."
            val ans = 1.0 / v
            val ansFmt = if (ans % 1.0 == 0.0) ans.toLong().toString() else "$ans"
            return "The reciprocal of $v is $ansFmt."
        }
        if (Regex("""1\s*/\s*([\d,.]+)""").matches(q)) {
            val v = q.substringAfter("/").trim().replace(",", "").toDoubleOrNull() ?: return null
            if (v == 0.0) return "1 divided by zero is undefined."
            val ans = 1.0 / v
            return "1 divided by $v is $ans."
        }

        // Square root / Roots: "square root of 144", "sqrt 144"
        val sqrtMatch = Regex("""(?:square\s+root\s+of|sqrt)\s*\(?\s*([\d,.]+)\s*\)?""").find(q)
        if (sqrtMatch != null) {
            val v = sqrtMatch.groupValues[1].replace(",", "").toDoubleOrNull() ?: return null
            if (v < 0.0) return "Square root of a negative number is not real."
            val ans = Math.sqrt(v)
            val ansFmt = if (ans % 1.0 == 0.0) ans.toLong().toString() else "%.2f".format(ans)
            return "Square root of $v is $ansFmt."
        }

        // Powers: "2 squared", "5 cubed", "2^10"
        val sqMatch = Regex("""([\d,.]+)\s+squared""").find(q)
        if (sqMatch != null) {
            val v = sqMatch.groupValues[1].replace(",", "").toDoubleOrNull() ?: return null
            val ans = v * v
            val ansFmt = if (ans % 1.0 == 0.0) ans.toLong().toString() else "$ans"
            return "$v squared is $ansFmt."
        }
        val cbMatch = Regex("""([\d,.]+)\s+cubed""").find(q)
        if (cbMatch != null) {
            val v = cbMatch.groupValues[1].replace(",", "").toDoubleOrNull() ?: return null
            val ans = v * v * v
            val ansFmt = if (ans % 1.0 == 0.0) ans.toLong().toString() else "$ans"
            return "$v cubed is $ansFmt."
        }
        val powMatch = Regex("""([\d,.]+)\s*(?:\^|\*\*|\braised\s+to\s+)\s*([\d,.]+)""").find(q)
        if (powMatch != null) {
            val base = powMatch.groupValues[1].replace(",", "").toDoubleOrNull() ?: return null
            val exp = powMatch.groupValues[2].replace(",", "").toDoubleOrNull() ?: return null
            if (Math.abs(exp) > 100) return "Exponent is too large."
            val ans = Math.pow(base, exp)
            val ansFmt = if (ans % 1.0 == 0.0) ans.toLong().toString() else "$ans"
            return "$base to the power of $exp is $ansFmt."
        }

        // Fractions: "3/4 + 1/2"
        val fracMatch = Regex("""(\d+)\s*/\s*(\d+)\s*([+\-*x×/])\s*(\d+)\s*/\s*(\d+)""").find(q)
        if (fracMatch != null) {
            val n1 = fracMatch.groupValues[1].toDoubleOrNull() ?: return null
            val d1 = fracMatch.groupValues[2].toDoubleOrNull() ?: return null
            val op = fracMatch.groupValues[3]
            val n2 = fracMatch.groupValues[4].toDoubleOrNull() ?: return null
            val d2 = fracMatch.groupValues[5].toDoubleOrNull() ?: return null
            if (d1 == 0.0 || d2 == 0.0) return "Denominator cannot be zero."
            val v1 = n1 / d1
            val v2 = n2 / d2
            val res = when (op) {
                "+" -> v1 + v2
                "-" -> v1 - v2
                "*", "x", "×" -> v1 * v2
                "/" -> if (v2 != 0.0) v1 / v2 else return "Division by zero is undefined."
                else -> return null
            }
            return "${n1.toLong()}/${d1.toLong()} $op ${n2.toLong()}/${d2.toLong()} is $res."
        }

        // General arithmetic: "27 × 38", "125 * 16", "144 / 12", "25 + 37", "100 - 43"
        var clean = q.replace(Regex("""[?!.,;]"""), " ").trim()
        clean = clean
            .replace(Regex("""^(?:what\s+is|whats|calculate|compute|solve|bhai|batao|bataiye)\s+"""), "")
            .replace(Regex("""\s+(?:kitna\s+hota\s+hai|kitna\s+hoga|kitna\s+hai|hoga|batao|bataiye)$"""), "")
            .replace("multiplied by", "*")
            .replace("divided by", "/")
            .replace("plus", "+")
            .replace("minus", "-")
            .replace("into", "*")
            .replace("times", "*")
            .replace("×", "*")
            .replace("÷", "/")
            .replace("aur", "+")
            .replace("and", "+")
            .replace("jodo", "+")
            .replace("me se", "-")
            .replace("se", "-")
            .replace("ghatao", "-")
            .replace("guna", "*")
            .replace("bhag", "/")
            .replace(Regex("""\s+"""), " ")
            .trim()

        val arithMatch = Regex("""^([\d,.]+)\s*([+\-*/%])\s*([\d,.]+)$""").find(clean)
        if (arithMatch != null) {
            val a = arithMatch.groupValues[1].replace(",", "").toDoubleOrNull() ?: return null
            val op = arithMatch.groupValues[2]
            val b = arithMatch.groupValues[3].replace(",", "").toDoubleOrNull() ?: return null
            val res = when (op) {
                "+" -> a + b
                "-" -> a - b
                "*" -> a * b
                "/" -> if (b != 0.0) a / b else return "Division by zero is undefined."
                "%" -> a % b
                else -> return null
            }
            val aFmt = if (a % 1.0 == 0.0) a.toLong().toString() else "$a"
            val bFmt = if (b % 1.0 == 0.0) b.toLong().toString() else "$b"
            val resFmt = if (res % 1.0 == 0.0) res.toLong().toString() else "%.2f".format(res)
            val opName = when (op) {
                "*" -> "times"
                "/" -> "divided by"
                "+" -> "plus"
                "-" -> "minus"
                else -> op
            }
            return "$aFmt $opName $bFmt is $resFmt."
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
