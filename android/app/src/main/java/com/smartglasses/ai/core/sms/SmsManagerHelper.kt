package com.smartglasses.ai.core.sms

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.Telephony
import android.telephony.SmsManager
import androidx.core.content.ContextCompat

data class SmsItem(
    val id: String,
    val address: String,
    val body: String,
    val timestamp: Long,
    val dateFormatted: String
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

    fun invalidateCache() {
        synchronized(lock) {
            cacheTimestamp = 0L
            cachedMessages = emptyList()
        }
    }

    fun readRecentMessages(context: Context, limit: Int = 5): List<SmsItem> {
        if (!hasReadPermission(context)) return emptyList()

        val now = System.currentTimeMillis()
        synchronized(lock) {
            if (now - cacheTimestamp < CACHE_TTL_MS && cachedMessages.isNotEmpty()) {
                return cachedMessages.take(limit)
            }
        }

        val messages = mutableListOf<SmsItem>()
        val uri: Uri = Telephony.Sms.Inbox.CONTENT_URI
        val projection = arrayOf(
            Telephony.Sms._ID,
            Telephony.Sms.ADDRESS,
            Telephony.Sms.BODY,
            Telephony.Sms.DATE
        )

        try {
            val cursor = context.contentResolver.query(
                uri,
                projection,
                null,
                null,
                "${Telephony.Sms.DATE} DESC LIMIT $limit"
            )

            cursor?.use {
                val idIdx = it.getColumnIndexOrThrow(Telephony.Sms._ID)
                val addrIdx = it.getColumnIndexOrThrow(Telephony.Sms.ADDRESS)
                val bodyIdx = it.getColumnIndexOrThrow(Telephony.Sms.BODY)
                val dateIdx = it.getColumnIndexOrThrow(Telephony.Sms.DATE)

                while (it.moveToNext()) {
                    val id = it.getString(idIdx)
                    val address = it.getString(addrIdx) ?: "Unknown"
                    val body = it.getString(bodyIdx) ?: ""
                    val date = it.getLong(dateIdx)

                    // Data minimization: trim body to max 160 chars
                    val trimmedBody = if (body.length > 160) body.substring(0, 160) + "..." else body

                    val dateStr = java.text.SimpleDateFormat("hh:mm a", java.util.Locale.US).format(java.util.Date(date))

                    messages.add(
                        SmsItem(
                            id = id,
                            address = address,
                            body = trimmedBody,
                            timestamp = date,
                            dateFormatted = dateStr
                        )
                    )
                }
            }
        } catch (e: Exception) {
            android.util.Log.e("SmartGlasses.SMS", "Failed to query SMS content provider: ${e.message}")
        }

        if (messages.isNotEmpty()) {
            synchronized(lock) {
                cachedMessages = messages
                cacheTimestamp = System.currentTimeMillis()
            }
        }

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
