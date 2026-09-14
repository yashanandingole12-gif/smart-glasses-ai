package com.smartglasses.ai.core.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.SystemClock
import android.util.Log
import android.view.KeyEvent
import com.smartglasses.ai.core.service.GlassesBackgroundService

/**
 * TWS Earbuds & Bluetooth Headset Multi-Tap AI Action Detector.
 *
 * Catches hardware media button presses (3-5 rapid presses or triple tap on TWS action button)
 * and starts the hands-free Gemini AI assistant immediately, even with the phone screen locked.
 */
class TwsMediaButtonReceiver : BroadcastReceiver() {

    companion object {
        private const val TAG = "SmartGlasses.TwsReceiver"
        private const val MULTI_TAP_WINDOW_MS = 1400L // Window for counting clicks
        private const val REQUIRED_TAP_COUNT = 3      // 3 or more taps triggers AI Assistant

        @Volatile
        private var tapCount = 0
        @Volatile
        private var lastTapTimestamp = 0L

        var onMultiTapAiTriggered: (() -> Unit)? = null
    }

    override fun onReceive(context: Context, intent: Intent?) {
        if (intent?.action != Intent.ACTION_MEDIA_BUTTON) return

        @Suppress("DEPRECATION")
        val keyEvent = intent.getParcelableExtra<KeyEvent>(Intent.EXTRA_KEY_EVENT) ?: return

        // Only register KEY_DOWN events to avoid double counting UP and DOWN
        if (keyEvent.action != KeyEvent.ACTION_DOWN) return

        val keyCode = keyEvent.keyCode
        Log.d(TAG, "Media button press detected: keyCode=$keyCode")

        if (keyCode == KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE ||
            keyCode == KeyEvent.KEYCODE_HEADSETHOOK ||
            keyCode == KeyEvent.KEYCODE_MEDIA_PLAY ||
            keyCode == KeyEvent.KEYCODE_MEDIA_PAUSE ||
            keyCode == KeyEvent.KEYCODE_MEDIA_NEXT
        ) {
            val now = SystemClock.uptimeMillis()
            if (now - lastTapTimestamp > MULTI_TAP_WINDOW_MS) {
                tapCount = 1
            } else {
                tapCount++
            }
            lastTapTimestamp = now

            Log.i(TAG, "TWS action tap registered: count=$tapCount/$REQUIRED_TAP_COUNT")

            if (tapCount >= REQUIRED_TAP_COUNT) {
                tapCount = 0 // Reset counter
                Log.i(TAG, ">>> TWS MULTI-TAP TRIGGER DETECTED! Waking Hands-Free Gemini Assistant <<<")
                
                // 1. Invoke active listener callback if running
                onMultiTapAiTriggered?.invoke()

                // 2. Dispatch intent to GlassesBackgroundService to trigger voice wake
                val serviceIntent = Intent(context, GlassesBackgroundService::class.java).apply {
                    action = GlassesBackgroundService.ACTION_TWS_AI_TRIGGER
                }
                context.startService(serviceIntent)
            }
        }
    }
}
