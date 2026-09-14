package com.smartglasses.ai.core.sms

import java.util.Locale
import java.util.regex.Pattern

enum class SmsCategory {
    PERSONAL,
    OTP_TRANSACTION,
    PROMOTION_AD,
    SPAM
}

data class FilteredSmsResult(
    val category: SmsCategory,
    val isSpamOrPromo: Boolean,
    val reason: String,
    val confidence: Float
)

/**
 * On-Device Intelligent SMS Classification & Spam/Ad Filter.
 *
 * Runs in <1ms without cloud dependency to filter out promotional noise,
 * lottery scams, and spam before presenting unread or recent messages to the user.
 */
object SmsSpamFilter {

    private val OTP_PATTERNS = listOf(
        Pattern.compile("""\b(?:otp|one[- ]time[- ]password|verification[- ]code|security[- ]code)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:code\s+is|otp\s+is|passcode\s+is)\s*[:\-]?\s*(\d{4,8})\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:debited|credited|withdrawn|deposited|transferred)\s+(?:by|for|of)?\s*(?:rs\.?|inr|₹)\s*[\d,]+""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:acct|a/c|account)\s*(?:no\.?|xx+|\.\.\.)?\s*\d*\s*(?:debited|credited)""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:txn|transaction)\s*(?:id|no\.?|ref)\b""", Pattern.CASE_INSENSITIVE)
    )

    private val PROMO_PATTERNS = listOf(
        Pattern.compile("""\b(?:flat|upto|up\s+to)\s+\d+%\s+(?:off|discount|cashback)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:use\s+code|coupon\s+code|promo\s+code)\s+[:\-]?\s*[A-Z0-9]{3,12}\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:limited\s+time\s+offer|exclusive\s+deal|mega\s+sale|flash\s+sale|hurry)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:buy\s+\d+\s+get\s+\d+|free\s+shipping|shop\s+now|order\s+now|book\s+now)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:pre-approved|instant\s+loan|credit\s+card\s+limit|apply\s+now|zero\s+downpayment)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:subscribe|unsubscribe|to\s+opt\s+out|click\s+here|t&c\s+apply)\b""", Pattern.CASE_INSENSITIVE)
    )

    private val SPAM_PATTERNS = listOf(
        Pattern.compile("""\b(?:congratulations|you\s+won|lottery|lucky\s+draw|claim\s+your\s+prize|jackpot)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:earn\s+from\s+home|daily\s+income|crypto\s+investment|guaranteed\s+returns)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""\b(?:urgent\s+action\s+required|account\s+suspended|kyc\s+expired|pan\s+card\s+blocked|electricity\s+power\s+cut)\b""", Pattern.CASE_INSENSITIVE),
        Pattern.compile("""(?:bit\.ly|tinyurl\.com|t\.co|is\.gd|goo\.gl|cutt\.ly)/[a-zA-Z0-9]+""", Pattern.CASE_INSENSITIVE)
    )

    // Common commercial alphanumeric SMS sender prefixes (e.g. "AD-MYNTRA", "VM-HDFCBK", "IX-JIO")
    private val COMMERCIAL_SENDER_PATTERN = Pattern.compile("""^[A-Z]{2}-[A-Z0-9]{4,10}$""", Pattern.CASE_INSENSITIVE)

    fun classify(senderAddress: String, body: String, contactName: String?): FilteredSmsResult {
        val trimmedBody = body.trim()
        val address = senderAddress.trim()

        // 1. If sender is a saved contact with a verified name, it's Personal
        if (!contactName.isNullOrBlank() && contactName != address && !contactName.equals("Unknown", ignoreCase = true)) {
            return FilteredSmsResult(
                category = SmsCategory.PERSONAL,
                isSpamOrPromo = false,
                reason = "Sender is saved in contacts ($contactName)",
                confidence = 0.95f
            )
        }

        // 2. Check for Fraudulent / Malicious Spam
        for (pattern in SPAM_PATTERNS) {
            if (pattern.matcher(trimmedBody).find()) {
                return FilteredSmsResult(
                    category = SmsCategory.SPAM,
                    isSpamOrPromo = true,
                    reason = "Matched spam/phishing heuristics",
                    confidence = 0.90f
                )
            }
        }

        // 3. Check for OTP / Banking Transaction
        for (pattern in OTP_PATTERNS) {
            if (pattern.matcher(trimmedBody).find()) {
                return FilteredSmsResult(
                    category = SmsCategory.OTP_TRANSACTION,
                    isSpamOrPromo = false,
                    reason = "Transactional / OTP alert",
                    confidence = 0.92f
                )
            }
        }

        // 4. Check for Promotional / Marketing Messages
        for (pattern in PROMO_PATTERNS) {
            if (pattern.matcher(trimmedBody).find()) {
                return FilteredSmsResult(
                    category = SmsCategory.PROMOTION_AD,
                    isSpamOrPromo = true,
                    reason = "Promotional offer or marketing discount",
                    confidence = 0.88f
                )
            }
        }

        // 5. Commercial Sender Header check
        if (COMMERCIAL_SENDER_PATTERN.matcher(address).matches()) {
            return FilteredSmsResult(
                category = SmsCategory.PROMOTION_AD,
                isSpamOrPromo = true,
                reason = "Commercial SMS sender header format ($address)",
                confidence = 0.80f
            )
        }

        // 6. Default to Personal if it's a standard phone number
        val cleanDigits = address.replace(Regex("""[\s\-+()]"""), "")
        if (cleanDigits.length in 7..15 && cleanDigits.all { it.isDigit() }) {
            return FilteredSmsResult(
                category = SmsCategory.PERSONAL,
                isSpamOrPromo = false,
                reason = "Direct individual phone number",
                confidence = 0.75f
            )
        }

        return FilteredSmsResult(
            category = SmsCategory.PERSONAL,
            isSpamOrPromo = false,
            reason = "General message",
            confidence = 0.60f
        )
    }

    /**
     * Filters a list of SMS messages, returning clean messages while filtering out promo/spam.
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
