package com.smartglasses.ai.core.telephony

import android.annotation.SuppressLint
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.telecom.TelecomManager
import android.telephony.TelephonyManager

class CallController(private val context: Context) {

    fun makeCall(phoneNumber: String): Boolean {
        return try {
            val cleanNumber = phoneNumber.replace(Regex("[^0-9+]"), "")
            val intent = Intent(Intent.ACTION_CALL).apply {
                data = Uri.parse("tel:$cleanNumber")
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
            true
        } catch (_: Exception) {
            try {
                // Fallback to dialer if CALL_PHONE permission not granted
                val dialIntent = Intent(Intent.ACTION_DIAL).apply {
                    data = Uri.parse("tel:${phoneNumber.trim()}")
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK
                }
                context.startActivity(dialIntent)
                true
            } catch (_: Exception) {
                false
            }
        }
    }

    @SuppressLint("MissingPermission")
    fun answerCall(): Boolean {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as? TelecomManager
            return try {
                telecomManager?.acceptRingingCall()
                true
            } catch (_: Exception) {
                false
            }
        }
        return false
    }

    @SuppressLint("MissingPermission")
    fun endCall(): Boolean {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as? TelecomManager
            return try {
                telecomManager?.endCall() ?: false
            } catch (_: Exception) {
                false
            }
        }
        return false
    }

    fun getCallState(): Int {
        val telephonyManager = context.getSystemService(Context.TELEPHONY_SERVICE) as? TelephonyManager
        return telephonyManager?.callState ?: TelephonyManager.CALL_STATE_IDLE
    }
}
