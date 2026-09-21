package com.smartglasses.ai.presentation

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.core.bluetooth.BleManager
import com.smartglasses.ai.presentation.activity.ActivityScreen
import com.smartglasses.ai.presentation.components.EvaAtmosphere
import com.smartglasses.ai.presentation.devices.DevicesHubScreen
import com.smartglasses.ai.presentation.home.WearableHomeScreen
import com.smartglasses.ai.presentation.home.WearableHomeViewModel
import com.smartglasses.ai.presentation.settings.BackendConfigDialog
import com.smartglasses.ai.presentation.theme.*
import com.smartglasses.ai.presentation.you.YouProfileScreen

enum class EvaTab(val label: String, val icon: ImageVector) {
    HOME("Presence", Icons.Default.Adjust),
    ACTIVITY("Stream", Icons.Default.AccessTime),
    DEVICES("Perception", Icons.Default.Devices),
    YOU("Profile", Icons.Default.Person)
}

// Alias for backward compatibility
typealias LaraTab = EvaTab

@Composable
fun EvaMainScreen(
    viewModel: WearableHomeViewModel,
    bleManager: BleManager
) {
    var selectedTab by remember { mutableStateOf(EvaTab.HOME) }
    val state by viewModel.uiState.collectAsState()

    if (state.isConfigDialogOpen) {
        BackendConfigDialog(
            currentUrl = state.serverUrl,
            onDismiss = { viewModel.closeConfigDialog() },
            onSaveUrl = { newUrl -> viewModel.updateServerUrl(newUrl) },
            onTestConnection = { testUrl, cb -> viewModel.testBackendConnection(testUrl, cb) }
        )
    }

    Scaffold(
        containerColor = EvaVoid,
        bottomBar = {
            NavigationBar(
                containerColor = EvaNight,
                contentColor = EvaTextPure,
                tonalElevation = 8.dp,
                modifier = Modifier.height(64.dp)
            ) {
                EvaTab.values().forEach { tab ->
                    val isSelected = selectedTab == tab
                    NavigationBarItem(
                        selected = isSelected,
                        onClick = { selectedTab = tab },
                        icon = {
                            Icon(
                                imageVector = tab.icon,
                                contentDescription = tab.label,
                                tint = if (isSelected) EvaTeal else EvaTextMuted,
                                modifier = Modifier.size(20.dp)
                            )
                        },
                        label = {
                            Text(
                                text = tab.label,
                                fontSize = 11.sp,
                                fontWeight = if (isSelected) androidx.compose.ui.text.font.FontWeight.SemiBold else androidx.compose.ui.text.font.FontWeight.Normal,
                                color = if (isSelected) EvaTeal else EvaTextMuted
                            )
                        },
                        colors = NavigationBarItemDefaults.colors(
                            indicatorColor = EvaTealGlow
                        )
                    )
                }
            }
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(EvaVoid)
        ) {
            when (selectedTab) {
                EvaTab.HOME -> WearableHomeScreen(
                    viewModel = viewModel,
                    onNavigateToDevices = { selectedTab = EvaTab.DEVICES }
                )
                EvaTab.ACTIVITY -> ActivityScreen(
                    viewModel = viewModel,
                    onNavigateToHome = { selectedTab = EvaTab.HOME }
                )
                EvaTab.DEVICES -> DevicesHubScreen(
                    bleManager = bleManager,
                    viewModel = viewModel
                )
                EvaTab.YOU -> YouProfileScreen(
                    viewModel = viewModel,
                    onOpenConfigDialog = { viewModel.openConfigDialog() }
                )
            }
        }
    }
}

// Backward-compatible entrypoint
@Composable
fun LaraMainScreen(
    viewModel: WearableHomeViewModel,
    bleManager: BleManager
) {
    EvaMainScreen(viewModel = viewModel, bleManager = bleManager)
}
