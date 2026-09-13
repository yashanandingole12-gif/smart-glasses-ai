package com.smartglasses.ai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import com.smartglasses.ai.core.bluetooth.BleManager
import com.smartglasses.ai.core.permissions.PermissionManager
import com.smartglasses.ai.presentation.LaraMainScreen
import com.smartglasses.ai.presentation.home.WearableHomeViewModel
import com.smartglasses.ai.presentation.theme.LaraTheme

class MainActivity : ComponentActivity() {

    private val viewModel: WearableHomeViewModel by viewModels()
    private lateinit var bleManager: BleManager

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) {
        // Telemetry updates automatically after permission grant
        viewModel.checkBackendHealth()
        if (bleManager.isBleHardwareAvailable()) {
            bleManager.startScan()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        bleManager = BleManager.getInstance(this)

        // Request runtime permissions on launch
        if (!PermissionManager.hasAllEssentialPermissions(this)) {
            permissionLauncher.launch(PermissionManager.REQUIRED_PERMISSIONS)
        } else {
            if (bleManager.isBleHardwareAvailable()) {
                bleManager.startScan()
            }
        }

        // Auto-start 24/7 background wearable daemon service (Screen Off Ready)
        try {
            com.smartglasses.ai.core.service.GlassesBackgroundService.startService(this)
        } catch (e: Exception) {
            android.util.Log.w("MainActivity", "Could not start background daemon: ${e.message}")
        }

        setContent {
            LaraTheme {
                LaraMainScreen(
                    viewModel = viewModel,
                    bleManager = bleManager
                )
            }
        }
    }
}
