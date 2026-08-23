package com.smartglasses.ai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import com.smartglasses.ai.core.permissions.PermissionManager
import com.smartglasses.ai.presentation.home.WearableHomeScreen
import com.smartglasses.ai.presentation.home.WearableHomeViewModel
import com.smartglasses.ai.presentation.theme.SmartGlassesTheme

class MainActivity : ComponentActivity() {

    private val viewModel: WearableHomeViewModel by viewModels()

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) {
        // Telemetry updates automatically after permission grant
        viewModel.checkBackendHealth()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Request runtime permissions on launch
        if (!PermissionManager.hasAllEssentialPermissions(this)) {
            permissionLauncher.launch(PermissionManager.REQUIRED_PERMISSIONS)
        }

        setContent {
            SmartGlassesTheme {
                WearableHomeScreen(viewModel = viewModel)
            }
        }
    }
}
