package com.smartglasses.ai.core.service

import android.annotation.SuppressLint
import android.app.*
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import android.os.PowerManager
import android.util.Log
import androidx.core.app.NotificationCompat
import com.smartglasses.ai.MainActivity
import com.smartglasses.ai.core.bluetooth.BleManager
import com.smartglasses.ai.core.bluetooth.DeviceConnectionState
import kotlinx.coroutines.*

/**
 * 24/7 Foreground Background Service for EVA Smart Glasses:
 * - Keeps BLE connection to Seeed Studio XIAO ESP32-S3 Sense alive continuously.
 * - Operates even when the phone screen is locked/off, in pocket, or app is minimized.
 * - Handles incoming wearable push-to-talk events and SMS background sync.
 */
class GlassesBackgroundService : Service() {

    companion object {
        private const val TAG = "SmartGlasses.BgService"
        private const val NOTIFICATION_CHANNEL_ID = "smart_glasses_daemon_channel"
        private const val NOTIFICATION_ID = 1001
        private const val WAKE_LOCK_TAG = "SmartGlasses:DaemonWakeLock"

        const val ACTION_START = "com.smartglasses.ai.action.START_DAEMON"
        const val ACTION_STOP = "com.smartglasses.ai.action.STOP_DAEMON"
        const val ACTION_TWS_AI_TRIGGER = "com.smartglasses.ai.action.TWS_AI_TRIGGER"

        var onHandsFreeVoiceTriggered: (() -> Unit)? = null

        fun startService(context: Context) {
            val intent = Intent(context, GlassesBackgroundService::class.java).apply {
                action = ACTION_START
            }
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }

        fun stopService(context: Context) {
            val intent = Intent(context, GlassesBackgroundService::class.java).apply {
                action = ACTION_STOP
            }
            context.stopService(intent)
        }
    }

    private var wakeLock: PowerManager.WakeLock? = null
    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private lateinit var bleManager: BleManager

    override fun onCreate() {
        super.onCreate()
        Log.i(TAG, "GlassesBackgroundService created. Initializing background wearable daemon...")
        bleManager = BleManager.getInstance(applicationContext)

        acquireWakeLock()
        createNotificationChannel()
        startForegroundServiceNotification("Connecting to Smart Glasses...")

        // Observe BLE connection state and update persistent notification
        serviceScope.launch {
            bleManager.connectionState.collect { state ->
                val statusText = when (state) {
                    DeviceConnectionState.CONNECTED_ESP32 -> "👓 Smart Glasses: Connected (ESP32-S3)"
                    DeviceConnectionState.CONNECTED_SIMULATED -> "👓 Smart Glasses: Active (Local Companion)"
                    DeviceConnectionState.CONNECTING -> "👓 Smart Glasses: Scanning / Connecting..."
                    DeviceConnectionState.DISCONNECTED -> "👓 Smart Glasses: Background Daemon Active"
                }
                updateNotification(statusText)
            }
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) {
            stopSelf()
            return START_NOT_STICKY
        }

        if (intent?.action == ACTION_TWS_AI_TRIGGER) {
            Log.i(TAG, "Handling ACTION_TWS_AI_TRIGGER - Waking speech assistant hands-free")
            onHandsFreeVoiceTriggered?.invoke()
            return START_STICKY
        }

        Log.i(TAG, "GlassesBackgroundService onStartCommand - START_STICKY enabled.")
        return START_STICKY // OS will restart service automatically if killed
    }

    @SuppressLint("WakelockTimeout")
    private fun acquireWakeLock() {
        try {
            val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
            wakeLock = powerManager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, WAKE_LOCK_TAG).apply {
                setReferenceCounted(false)
                acquire()
            }
            Log.i(TAG, "Partial WakeLock acquired for screen-off execution.")
        } catch (e: Exception) {
            Log.w(TAG, "Could not acquire WakeLock: ${e.message}")
        }
    }

    private fun releaseWakeLock() {
        try {
            wakeLock?.let {
                if (it.isHeld) it.release()
            }
            Log.i(TAG, "WakeLock released.")
        } catch (e: Exception) {
            Log.w(TAG, "Error releasing WakeLock: ${e.message}")
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                NOTIFICATION_CHANNEL_ID,
                "EVA Smart Glasses Daemon",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Keeps connection to Smart Glasses active in background when screen is off"
                setShowBadge(false)
            }
            val manager = getSystemService(NotificationManager::class.java)
            manager?.createNotificationChannel(channel)
        }
    }

    private fun buildNotification(contentText: String): Notification {
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        return NotificationCompat.Builder(this, NOTIFICATION_CHANNEL_ID)
            .setContentTitle("EVA Executive Companion")
            .setContentText(contentText)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    private fun startForegroundServiceNotification(statusText: String) {
        val notification = buildNotification(statusText)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_CONNECTED_DEVICE or ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun updateNotification(contentText: String) {
        val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        manager.notify(NOTIFICATION_ID, buildNotification(contentText))
    }

    override fun onDestroy() {
        Log.i(TAG, "GlassesBackgroundService destroyed. Cleaning up resources...")
        serviceScope.cancel()
        releaseWakeLock()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
