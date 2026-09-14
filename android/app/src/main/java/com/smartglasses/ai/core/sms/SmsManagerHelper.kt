package com.smartglasses.ai.core.sms

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.ContactsContract
import android.provider.Telephony
import android.telephony.SmsManager
import androidx.core.content.ContextCompat

data class SmsItem(
    val id: String,
    val address: String,
    val body: String,
    val timestamp: Long,
    val dateFormatted: String,
    val contactName: String? = null,
    val type: String = "received"
)

object SmsManagerHelper {

    private const val CACHE_TTL_MS = 30_000L // 30s cache
    @Volatile
    private var cachedMessages: List<SmsItem> = emptyList()
    @Volatile
    private var cacheTimestamp: Long = 0L
    private val lock = Any()

    fun hasReadPermission(context: Context): Boolean {
        return ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.READ_SMS
        ) == PackageManager.PERMISSION_GRANTED
    }

    fun hasSendPermission(context: Context): Boolean {
        return ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.SEND_SMS
        ) == PackageManager.PERMISSION_GRANTED
    }

    fun hasContactsPermission(context: Context): Boolean {
        return ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.READ_CONTACTS
        ) == PackageManager.PERMISSION_GRANTED
    }

    fun invalidateCache() {
        synchronized(lock) {
            cacheTimestamp = 0L
            cachedMessages = emptyList()
        }
    }

    fun resolveContactName(context: Context, phoneNumber: String): String? {
        if (!hasContactsPermission(context) || phoneNumber.isBlank()) return null
        return try {
            val uri = Uri.withAppendedPath(ContactsContract.PhoneLookup.CONTENT_FILTER_URI, Uri.encode(phoneNumber))
            context.contentResolver.query(
                uri,
                arrayOf(ContactsContract.PhoneLookup.DISPLAY_NAME),
                null,
                null,
                null
            )?.use {
                if (it.moveToFirst()) {
                    it.getString(it.getColumnIndexOrThrow(ContactsContract.PhoneLookup.DISPLAY_NAME))
                } else null
            }
        } catch (_: Exception) {
            null
        }
    }

    fun findPhoneNumbersForContact(context: Context, nameQuery: String): List<Pair<String, String>> {
        if (!hasContactsPermission(context) || nameQuery.isBlank()) return emptyList()
        val results = mutableListOf<Pair<String, String>>()
        try {
            val uri = ContactsContract.CommonDataKinds.Phone.CONTENT_URI
            val selection = "${ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME} LIKE ?"
            val args = arrayOf("%$nameQuery%")
            context.contentResolver.query(
                uri,
                arrayOf(
                    ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME,
                    ContactsContract.CommonDataKinds.Phone.NUMBER
                ),
                selection,
                args,
                null
            )?.use {
                val nameIdx = it.getColumnIndexOrThrow(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)
                val numIdx = it.getColumnIndexOrThrow(ContactsContract.CommonDataKinds.Phone.NUMBER)
                while (it.moveToNext()) {
                    val name = it.getString(nameIdx) ?: nameQuery
                    val num = it.getString(numIdx) ?: ""
                    if (num.isNotBlank()) {
                        results.add(Pair(name, num.replace(Regex("""[\s\-]"""), "")))
                    }
                }
            }
        } catch (_: Exception) {}
        return results
    }

    fun readRecentMessages(context: Context, limit: Int = 5): List<SmsItem> {
        if (!hasReadPermission(context)) {
            android.util.Log.w("SmartGlasses.SMS", "READ_SMS permission not granted.")
            return emptyList()
        }

        val now = System.currentTimeMillis()
        synchronized(lock) {
            if (now - cacheTimestamp < CACHE_TTL_MS && cachedMessages.isNotEmpty()) {
                return cachedMessages.take(limit)
            }
        }

        val messages = mutableListOf<SmsItem>()
        val uriList = listOf(
            Telephony.Sms.Inbox.CONTENT_URI,
            Uri.parse("content://sms/inbox"),
            Uri.parse("content://sms")
        )
        val projection = arrayOf(
            Telephony.Sms._ID,
            Telephony.Sms.ADDRESS,
            Telephony.Sms.BODY,
            Telephony.Sms.DATE
        )

        val t0 = System.currentTimeMillis()
        for (uri in uriList) {
            try {
                val cursor = context.contentResolver.query(
                    uri,
                    projection,
                    null,
                    null,
                    "${Telephony.Sms.DATE} DESC LIMIT $limit"
                )

                cursor?.use {
                    val idIdx = it.getColumnIndex(Telephony.Sms._ID)
                    val addrIdx = it.getColumnIndex(Telephony.Sms.ADDRESS)
                    val bodyIdx = it.getColumnIndex(Telephony.Sms.BODY)
                    val dateIdx = it.getColumnIndex(Telephony.Sms.DATE)

                    while (it.moveToNext()) {
                        val id = if (idIdx >= 0) it.getString(idIdx) else "sms_${System.currentTimeMillis()}"
                        val address = if (addrIdx >= 0) (it.getString(addrIdx) ?: "Unknown") else "Unknown"
                        val body = if (bodyIdx >= 0) (it.getString(bodyIdx) ?: "") else ""
                        val date = if (dateIdx >= 0) it.getLong(dateIdx) else System.currentTimeMillis()

                        val trimmedBody = if (body.length > 160) body.substring(0, 160) + "..." else body
                        val dateStr = java.text.SimpleDateFormat("hh:mm a", java.util.Locale.US).format(java.util.Date(date))
                        val resolvedContact = resolveContactName(context, address)

                        messages.add(
                            SmsItem(
                                id = id,
                                address = address,
                                body = trimmedBody,
                                timestamp = date,
                                dateFormatted = dateStr,
                                contactName = resolvedContact,
                                type = "received"
                            )
                        )
                    }
                }
                if (messages.isNotEmpty()) break
            } catch (e: Exception) {
                android.util.Log.w("SmartGlasses.SMS", "Failed querying URI $uri: ${e.message}")
            }
        }

        val queryMs = System.currentTimeMillis() - t0
        android.util.Log.i("SmartGlasses.SMS", "SMS read query executed: count=${messages.size}, latencyMs=$queryMs")

        if (messages.isNotEmpty()) {
            synchronized(lock) {
                cachedMessages = messages
                cacheTimestamp = System.currentTimeMillis()
            }
        }

        return messages
    }

    /**
     * Reads recent SMS messages and applies on-device spam & promotional ad filtering.
     * Returns a pair of (filtered relevant messages, count of filtered-out spam/promos).
     */
    fun readFilteredMessages(context: Context, limit: Int = 10, includePromotions: Boolean = false): Pair<List<SmsItem>, Int> {
        val rawMessages = readRecentMessages(context, limit = 20)
        if (rawMessages.isEmpty()) {
            return Pair(emptyList(), 0)
        }
        val (filtered, promoCount) = SmsSpamFilter.filterRelevantMessages(rawMessages, includePromotions = includePromotions)
        return Pair(filtered.take(limit), promoCount)
    }

    fun searchMessages(context: Context, query: String, limit: Int = 5): List<SmsItem> {
        if (!hasReadPermission(context) || query.isBlank()) return emptyList()

        val messages = mutableListOf<SmsItem>()
        val uriList = listOf(
            Telephony.Sms.Inbox.CONTENT_URI,
            Uri.parse("content://sms/inbox"),
            Uri.parse("content://sms")
        )
        val projection = arrayOf(
            Telephony.Sms._ID,
            Telephony.Sms.ADDRESS,
            Telephony.Sms.BODY,
            Telephony.Sms.DATE
        )

        val contacts = findPhoneNumbersForContact(context, query)
        val phoneNumbers = contacts.map { it.second }.distinct()

        val selection: String
        val args: Array<String>

        if (phoneNumbers.isNotEmpty()) {
            val placeholders = phoneNumbers.joinToString(",") { "?" }
            selection = "(${Telephony.Sms.ADDRESS} IN ($placeholders) OR ${Telephony.Sms.BODY} LIKE ? OR ${Telephony.Sms.ADDRESS} LIKE ?)"
            val argList = mutableListOf<String>()
            argList.addAll(phoneNumbers)
            argList.add("%$query%")
            argList.add("%$query%")
            args = argList.toTypedArray()
        } else {
            selection = "${Telephony.Sms.BODY} LIKE ? OR ${Telephony.Sms.ADDRESS} LIKE ?"
            args = arrayOf("%$query%", "%$query%")
        }

        val t0 = System.currentTimeMillis()
        for (uri in uriList) {
            try {
                val cursor = context.contentResolver.query(
                    uri,
                    projection,
                    selection,
                    args,
                    "${Telephony.Sms.DATE} DESC LIMIT $limit"
                )

                cursor?.use {
                    val idIdx = it.getColumnIndex(Telephony.Sms._ID)
                    val addrIdx = it.getColumnIndex(Telephony.Sms.ADDRESS)
                    val bodyIdx = it.getColumnIndex(Telephony.Sms.BODY)
                    val dateIdx = it.getColumnIndex(Telephony.Sms.DATE)

                    while (it.moveToNext()) {
                        val id = if (idIdx >= 0) it.getString(idIdx) else "sms_${System.currentTimeMillis()}"
                        val address = if (addrIdx >= 0) (it.getString(addrIdx) ?: "Unknown") else "Unknown"
                        val body = if (bodyIdx >= 0) (it.getString(bodyIdx) ?: "") else ""
                        val date = if (dateIdx >= 0) it.getLong(dateIdx) else System.currentTimeMillis()

                        val trimmedBody = if (body.length > 160) body.substring(0, 160) + "..." else body
                        val dateStr = java.text.SimpleDateFormat("hh:mm a", java.util.Locale.US).format(java.util.Date(date))
                        val resolvedContact = resolveContactName(context, address)

                        messages.add(
                            SmsItem(
                                id = id,
                                address = address,
                                body = trimmedBody,
                                timestamp = date,
                                dateFormatted = dateStr,
                                contactName = resolvedContact,
                                type = "received"
                            )
                        )
                    }
                }
                if (messages.isNotEmpty()) break
            } catch (e: Exception) {
                android.util.Log.w("SmartGlasses.SMS", "Failed searching URI $uri: ${e.message}")
            }
        }

        val queryMs = System.currentTimeMillis() - t0
        android.util.Log.i("SmartGlasses.SMS", "SMS search query executed: query='<redacted>', count=${messages.size}, latencyMs=$queryMs")

        return messages
    }

    fun sendSms(context: Context, destination: String, message: String): Boolean {
        if (!hasSendPermission(context)) {
            android.util.Log.w("SmartGlasses.SMS", "SEND_SMS permission not granted")
            return false
        }
        try {
            val smsManager: SmsManager = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                context.getSystemService(SmsManager::class.java)
            } else {
                @Suppress("DEPRECATION")
                SmsManager.getDefault()
            }
            smsManager.sendTextMessage(destination, null, message, null, null)
            invalidateCache()
            android.util.Log.i("SmartGlasses.SMS", "SMS successfully dispatched to $destination")
            return true
        } catch (e: Exception) {
            android.util.Log.e("SmartGlasses.SMS", "Failed to send SMS to $destination: ${e.message}")
            return false
        }
    }
}
