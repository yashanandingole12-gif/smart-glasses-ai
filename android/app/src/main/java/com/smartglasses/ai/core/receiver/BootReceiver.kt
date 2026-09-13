package com.smartglasses.ai.core.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import com.smartglasses.ai.core.service.GlassesBackgroundService

/**
 * Boot Receiver: Auto-starts GlassesBackgroundService when Android phone boots or package is updated.
 */
class BootReceiver : BroadcastReceiver() {

    companion object {
        private const val TAG = "SmartGlasses.BootReceiver"
    }

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED || intent.action == Intent.ACTION_MY_PACKAGE_REPLACED) {
            Log.i(TAG, "Device booted or app updated. Starting Smart Glasses Background Daemon...")
            GlassesBackgroundService.startService(context)
        }
    }
}
