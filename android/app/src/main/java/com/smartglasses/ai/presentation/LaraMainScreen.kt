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
import com.smartglasses.ai.presentation.devices.DevicesHubScreen
import com.smartglasses.ai.presentation.home.WearableHomeScreen
import com.smartglasses.ai.presentation.home.WearableHomeViewModel
import com.smartglasses.ai.presentation.settings.BackendConfigDialog
import com.smartglasses.ai.presentation.theme.*
import com.smartglasses.ai.presentation.you.YouProfileScreen

enum class LaraTab(val label: String, val icon: ImageVector) {
    HOME("Home", Icons.Default.Adjust),
    ACTIVITY("Activity", Icons.Default.AccessTime),
    DEVICES("Devices", Icons.Default.Devices),
    YOU("You", Icons.Default.Person)
}

@Composable
fun LaraMainScreen(
    viewModel: WearableHomeViewModel,
    bleManager: BleManager
) {
    var selectedTab by remember { mutableStateOf(LaraTab.HOME) }
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
        containerColor = LaraIvory,
        bottomBar = {
            NavigationBar(
                containerColor = Color.White,
                contentColor = LaraCharcoal,
                tonalElevation = 6.dp,
                modifier = Modifier.height(64.dp)
            ) {
                LaraTab.values().forEach { tab ->
                    val isSelected = selectedTab == tab
                    NavigationBarItem(
                        selected = isSelected,
                        onClick = { selectedTab = tab },
                        icon = {
                            Icon(
                                imageVector = tab.icon,
                                contentDescription = tab.label,
                                tint = if (isSelected) LaraMutedOrange else LaraTextSecondaryLight,
                                modifier = Modifier.size(20.dp)
                            )
                        },
                        label = {
                            Text(
                                text = tab.label,
                                fontSize = 11.sp,
                                fontWeight = if (isSelected) androidx.compose.ui.text.font.FontWeight.SemiBold else androidx.compose.ui.text.font.FontWeight.Normal,
                                color = if (isSelected) LaraMutedOrange else LaraTextSecondaryLight
                            )
                        },
                        colors = NavigationBarItemDefaults.colors(
                            indicatorColor = LaraOrangeLight
                        )
                    )
                }
            }
        }
    ) { padding ->
        Box(modifier = Modifier.padding(padding)) {
            when (selectedTab) {
                LaraTab.HOME -> WearableHomeScreen(
                    viewModel = viewModel,
                    onNavigateToDevices = { selectedTab = LaraTab.DEVICES }
                )
                LaraTab.ACTIVITY -> ActivityScreen(
                    viewModel = viewModel,
                    onNavigateToHome = { selectedTab = LaraTab.HOME }
                )
                LaraTab.DEVICES -> DevicesHubScreen(
                    bleManager = bleManager,
                    viewModel = viewModel
                )
                LaraTab.YOU -> YouProfileScreen(
                    viewModel = viewModel,
                    onOpenConfigDialog = { viewModel.openConfigDialog() }
                )
            }
        }
    }
}
