package com.smartglasses.ai.core.sms

import java.util.Locale
import java.util.regex.Pattern

enum class SmsCategory {
    PERSONAL,
    IMPORTANT,
    NORMAL,
    PROMOTIONAL,
    SUSPICIOUS,
    SCAM,
    SPAM,
    SYSTEM
}

data class FilteredSmsResult(
    val category: SmsCategory,
    val isSpamOrPromo: Boolean,
    val reason: String,
    val confidence: Float,
    val isScamOrSuspicious: Boolean = false,
    val urgency: String = "LOW"
)

/**
 * On-Device Intelligent SMS Classification & Spam/Scam/Ad Filter.
 *
 * Evaluates 8 distinct categories: PERSONAL, IMPORTANT, NORMAL, PROMOTIONAL,
 * SUSPICIOUS, SCAM, SPAM, and SYSTEM in <1ms without cloud latency.
 */
object SmsSpamFilter {

    // 1. Critical Scams & Fraud Heuristics
    private val SCAM_PATTERNS = listOf(
        // Lottery / Prize scams
        Pattern.compile("""\b(?:congratulations|you\s+won|lottery|lucky\s+draw|claim\s+your\s+prize|jackpot|kbc\s+jackpot|kaun\s+banega\s+crorepati|won\s+(?:rs\.?|inr|₹|usd|\$)\s*[\d,]+)\b""", Pattern.CASE_INSENSITIVE),
        // Threat-based Scams (Electricity cut, KYC freeze, PAN card block)
        Pattern.compile("""\b(?:electricity|power\s+supply|meter)\b.*?\b(?:disconnected|bill\s+unpaid|power\s+cut|cut\s+tonight|disconnected\s+tonight)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:disconnected\s+tonight|power\s+cut\s+at|electricity\s+bill\s+unpaid|meter\s+disconnected)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:kyc\s+(?:expired|suspended|blocked|deactivated)|pan\s+card\s+(?:blocked|suspended|inoperative)|sim\s+(?:blocked|deactivated\s+within))\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:urgent\s+action\s+required|account\s+(?:suspended|blocked|frozen)|unauthorized\s+transaction\s+reported)\b""", Pattern.CASE_INSENSITIVE),
        // Crypto doubling / Work from home traps
        Pattern.compile("""\b(?:earn\s+from\s+home|daily\s+income\s+of|crypto\s+investment|guaranteed\s+returns?|double\s+your\s+money|part[- ]time\s+job\s+daily)\b""", Pattern.CASE_INSENSITIVE),
        // APK file distribution via SMS
        Pattern.compile("""(?:\.apk\b|download\s+(?:our\s+)?app\s+from|install\s+apk)""", Pattern.CASE_INSENSITIVE)
    )

    // 2. Suspicious Links & Urgency Traps
    private val SUSPICIOUS_URL_PATTERNS = listOf(
        // URL Shorteners
        Pattern.compile("""(?:bit\.ly|tinyurl\.com|t\.co|is\.gd|goo\.gl|cutt\.ly|rb\.gy|tiny\.cc|surl\.li|iplogger\.org|gg\.gg|ow\.ly)/[a-zA-Z0-9_\-]+""", Pattern.CASE_INSENSITIVE),
        // Raw IP Addresses in Links
        Pattern.compile("""https?://(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:/[^\s]*)?""", Pattern.CASE_INSENSITIVE),
        // Suspicious APK domains or unverified file endpoints
        Pattern.compile("""https?://[a-zA-Z0-9.\-]+\.(?:xyz|top|work|click|buzz|club|gq|cf|ml|ga|tk)/[^\s]*""", Pattern.CASE_INSENSITIVE)
    )

    // 3. OTP & Critical Financial/Operational Alerts (IMPORTANT)
    private val OTP_PATTERNS = listOf(
        Pattern.compile("""\b(?:otp|one[- ]time[- ]password|verification[- ]code|security[- ]code|passcode)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:code\s+is|otp\s+is|passcode\s+is|verification\s+code\s+is)\s*[:\-]?\s*(\d{4,8})\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:debited|credited|withdrawn|deposited|transferred)\s+(?:by|for|of)?\s*(?:rs\.?|inr|₹)\s*[\d,]+""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:acct|a/c|account)\s*(?:no\.?|xx+|\.\.\.)?\s*\d*\s*(?:debited|credited|available\s+bal)""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:txn|transaction)\s*(?:id|no\.?|ref|ref\s+no)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:salary\s+credited|payment\s+received|refund\s+processed)\b""", Pattern.CASE_INSENSITIVE)
    )

    // Travel, Courier & Official Tickets (IMPORTANT)
    private val TRAVEL_DELIVERY_PATTERNS = listOf(
        Pattern.compile("""\b(?:pnr\s*(?:no\.?|is|:)?\s*[a-z0-9]{8,12}|booking\s+confirmed|flight\s+ticket|boarding\s+pass)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:out\s+for\s+delivery|arriving\s+today|courier\s+delivered|package\s+delivered|dispatched\s+via)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:train\s+status|berth\s+no|coach\s+no)\b""", Pattern.CASE_INSENSITIVE)
    )

    // 4. Telecom / Carrier Alerts (SYSTEM)
    private val SYSTEM_PATTERNS = listOf(
        Pattern.compile("""\b(?:recharge\s+successful|data\s+pack|daily\s+data\s+limit|100%\s+daily\s+data|50%\s+daily\s+data|90%\s+daily\s+data)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:validity\s+expires\s+on|plan\s+expiry|sim\s+activated|welcome\s+to\s+(?:airtel|jio|vi|bsnl))\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:dnd\s+status|caller\s+tune\s+activated|roaming\s+pack|balance\s+enquiry)\b""", Pattern.CASE_INSENSITIVE)
    )

    // 5. Commercial Promotional / Marketing Offers (PROMOTIONAL)
    private val PROMO_PATTERNS = listOf(
        Pattern.compile("""\b(?:flat|upto|up\s+to)\s+\d+%\s+(?:off|discount|cashback)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:use\s+code|coupon\s+code|promo\s+code)\s+[:\-]?\s*[A-Z0-9]{3,12}\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:limited\s+time\s+offer|exclusive\s+deal|mega\s+sale|flash\s+sale|hurry|festive\s+offer)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:buy\s+\d+\s+get\s+\d+|free\s+shipping|shop\s+now|order\s+now|book\s+now|grab\s+now)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:pre-approved|instant\s+loan|credit\s+card\s+limit|apply\s+now|zero\s+downpayment|zero\s+interest\s+emi)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:subscribe|unsubscribe|to\s+opt\s+out|click\s+here|t&c\s+apply)\b""", Pattern.CASE_INSENSITIVE)
    )

    // Alphanumeric commercial SMS sender format (e.g. "AD-MYNTRA", "VM-HDFCBK", "IX-JIO", "HP-SWIGGY")
    private val COMMERCIAL_SENDER_PATTERN = Pattern.compile("""^[A-Z]{2}-[A-Z0-9]{4,10}$""", Pattern.CASE_INSENSITIVE)

    fun classify(senderAddress: String, body: String, contactName: String?): FilteredSmsResult {
        val trimmedBody = body.trim()
        val address = senderAddress.trim()

        // 1. Saved Contacts -> Always PERSONAL
        if (!contactName.isNullOrBlank() && contactName != address && !contactName.equals("Unknown", ignoreCase = true)) {
            val isUrgent = trimmedBody.contains("emergency", ignoreCase = true) ||
                    trimmedBody.contains("urgent", ignoreCase = true) ||
                    trimmedBody.contains("call me now", ignoreCase = true)
            return FilteredSmsResult(
                category = SmsCategory.PERSONAL,
                isSpamOrPromo = false,
                reason = "Sender is saved in contacts ($contactName)",
                confidence = 0.95f,
                isScamOrSuspicious = false,
                urgency = if (isUrgent) "HIGH" else "LOW"
            )
        }

        // 2. Scam Detection (Threats, fake lotteries, illegal APKs)
        for (pattern in SCAM_PATTERNS) {
            if (pattern.matcher(trimmedBody).find()) {
                return FilteredSmsResult(
                    category = SmsCategory.SCAM,
                    isSpamOrPromo = true,
                    reason = "Matched critical scam / extortion pattern",
                    confidence = 0.95f,
                    isScamOrSuspicious = true,
                    urgency = "HIGH"
                )
            }
        }

        // 3. Suspicious Links & Shorteners from Unknown Senders
        for (pattern in SUSPICIOUS_URL_PATTERNS) {
            if (pattern.matcher(trimmedBody).find()) {
                return FilteredSmsResult(
                    category = SmsCategory.SUSPICIOUS,
                    isSpamOrPromo = true,
                    reason = "Contains unverified shortened link or suspicious URL",
                    confidence = 0.88f,
                    isScamOrSuspicious = true,
                    urgency = "HIGH"
                )
            }
        }

        // 4. Important Alerts (OTP, Banking, Travel, Deliveries)
        for (pattern in OTP_PATTERNS) {
            if (pattern.matcher(trimmedBody).find()) {
                return FilteredSmsResult(
                    category = SmsCategory.IMPORTANT,
                    isSpamOrPromo = false,
                    reason = "Transactional alert / OTP verification",
                    confidence = 0.93f,
                    isScamOrSuspicious = false,
                    urgency = "HIGH"
                )
            }
        }

        for (pattern in TRAVEL_DELIVERY_PATTERNS) {
            if (pattern.matcher(trimmedBody).find()) {
                return FilteredSmsResult(
                    category = SmsCategory.IMPORTANT,
                    isSpamOrPromo = false,
                    reason = "Travel booking / Courier delivery update",
                    confidence = 0.91f,
                    isScamOrSuspicious = false,
                    urgency = "MEDIUM"
                )
            }
        }

        // 5. System & Telecom Alerts
        for (pattern in SYSTEM_PATTERNS) {
            if (pattern.matcher(trimmedBody).find()) {
                return FilteredSmsResult(
                    category = SmsCategory.SYSTEM,
                    isSpamOrPromo = false,
                    reason = "Telecom / Carrier status notification",
                    confidence = 0.86f,
                    isScamOrSuspicious = false,
                    urgency = "LOW"
                )
            }
        }

        // 6. Promotional Marketing Offers
        for (pattern in PROMO_PATTERNS) {
            if (pattern.matcher(trimmedBody).find()) {
                return FilteredSmsResult(
                    category = SmsCategory.PROMOTIONAL,
                    isSpamOrPromo = true,
                    reason = "Promotional offer or marketing discount",
                    confidence = 0.89f,
                    isScamOrSuspicious = false,
                    urgency = "LOW"
                )
            }
        }

        // 7. Commercial Sender Header Check
        if (COMMERCIAL_SENDER_PATTERN.matcher(address).matches()) {
            return FilteredSmsResult(
                category = SmsCategory.PROMOTIONAL,
                isSpamOrPromo = true,
                reason = "Commercial SMS sender header format ($address)",
                confidence = 0.80f,
                isScamOrSuspicious = false,
                urgency = "LOW"
            )
        }

        // 8. Direct standard individual phone numbers -> PERSONAL or NORMAL
        val cleanDigits = address.replace(Regex("""[\s\-+()]"""), "")
        if (cleanDigits.length in 7..15 && cleanDigits.all { it.isDigit() }) {
            return FilteredSmsResult(
                category = SmsCategory.PERSONAL,
                isSpamOrPromo = false,
                reason = "Direct individual phone number",
                confidence = 0.75f,
                isScamOrSuspicious = false,
                urgency = "LOW"
            )
        }

        return FilteredSmsResult(
            category = SmsCategory.NORMAL,
            isSpamOrPromo = false,
            reason = "General message",
            confidence = 0.60f,
            isScamOrSuspicious = false,
            urgency = "LOW"
        )
    }

    /**
     * Filters a list of SMS messages, returning clean messages while filtering out promo/spam/scam.
     */
    fun filterRelevantMessages(
        messages: List<SmsItem>,
        includePromotions: Boolean = false
    ): Pair<List<SmsItem>, Int> {
        var filteredOutCount = 0
        val relevant = mutableListOf<SmsItem>()

        for (msg in messages) {
            val res = classify(msg.address, msg.body, msg.contactName)
            if (res.isSpamOrPromo && !includePromotions) {
                filteredOutCount++
            } else {
                relevant.add(msg)
            }
        }

        return Pair(relevant, filteredOutCount)
    }
}
