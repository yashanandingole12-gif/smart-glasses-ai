package com.smartglasses.ai.core.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import android.util.Log
import com.smartglasses.ai.core.sms.SmsManagerHelper
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

/**
 * Real-time SMS Broadcast Receiver for Smart Glasses:
 * Intercepts incoming SMS messages on Android, resolves sender name,
 * and relays payload to the backend server even when the phone screen is locked.
 */
class SmsBroadcastReceiver : BroadcastReceiver() {

    companion object {
        private const val TAG = "SmartGlasses.SmsReceiver"
        private const val BACKEND_URL = "http://10.0.2.2:8001/api/v1/sms/receive" // Standard Android emulator loopback or LAN IP
    }

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Telephony.Sms.Intents.SMS_RECEIVED_ACTION) {
            val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent)
            if (messages.isNullOrEmpty()) return

            for (sms in messages) {
                val rawSender = sms.originatingAddress ?: "Unknown"
                val body = sms.messageBody ?: ""
                val contactName = SmsManagerHelper.resolveContactName(context, rawSender) ?: rawSender

                Log.i(TAG, "Incoming SMS intercepted: From '$contactName' ($rawSender): $body")

                // Relay to Backend Server in background coroutine
                CoroutineScope(Dispatchers.IO).launch {
                    try {
                        val payload = JSONObject().apply {
                            put("sender", contactName)
                            put("phone", rawSender)
                            put("body", body)
                            put("timestamp", System.currentTimeMillis())
                        }

                        val url = URL(BACKEND_URL)
                        val conn = url.openConnection() as HttpURLConnection
                        conn.requestMethod = "POST"
                        conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8")
                        conn.connectTimeout = 3000
                        conn.readTimeout = 3000
                        conn.doOutput = true

                        conn.outputStream.use { os ->
                            os.write(payload.toString().toByteArray(Charsets.UTF_8))
                        }

                        val responseCode = conn.responseCode
                        Log.i(TAG, "Relayed SMS to backend: Response $responseCode")
                        conn.disconnect()
                    } catch (e: Exception) {
                        Log.w(TAG, "Could not relay SMS to backend: ${e.message}")
                    }
                }
            }
        }
    }
}
