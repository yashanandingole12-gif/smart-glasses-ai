package com.smartglasses.ai.presentation

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
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

enum class EvaTab(val label: String, val icon: ImageVector) {
    HOME("Home", Icons.Default.Home),
    ACTIVITY("Activity", Icons.Default.InsertChartOutlined),
    DEVICES("Device", Icons.Default.Sensors),
    YOU("Settings", Icons.Default.Settings)
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
        containerColor = EvaIvory,
        bottomBar = {
            // Floating Frosted Glass Bottom Navigation Bar matching reference design
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(EvaIvory)
                    .padding(horizontal = 24.dp, vertical = 10.dp)
            ) {
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(66.dp),
                    shape = RoundedCornerShape(24.dp),
                    color = EvaPureWhite.copy(alpha = 0.95f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, EvaBorderSubtle),
                    shadowElevation = 8.dp
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(horizontal = 12.dp),
                        horizontalArrangement = Arrangement.SpaceAround,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        EvaTab.values().forEach { tab ->
                            val isSelected = selectedTab == tab

                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.Center,
                                modifier = Modifier
                                    .clip(RoundedCornerShape(18.dp))
                                    .clickable { selectedTab = tab }
                                    .padding(vertical = 4.dp, horizontal = 12.dp)
                            ) {
                                if (isSelected) {
                                    Box(
                                        modifier = Modifier
                                            .size(34.dp)
                                            .clip(CircleShape)
                                            .background(EvaDeepGreen),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Icon(
                                            imageVector = tab.icon,
                                            contentDescription = tab.label,
                                            tint = Color.White,
                                            modifier = Modifier.size(18.dp)
                                        )
                                    }
                                } else {
                                    Icon(
                                        imageVector = tab.icon,
                                        contentDescription = tab.label,
                                        tint = EvaMutedText,
                                        modifier = Modifier.size(20.dp)
                                    )
                                }

                                Text(
                                    text = tab.label,
                                    fontSize = 10.sp,
                                    fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                                    color = if (isSelected) EvaPrimaryBlack else EvaMutedText,
                                    modifier = Modifier.padding(top = 2.dp)
                                )
                            }
                        }
                    }
                }
            }
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(EvaIvory)
        ) {
            when (selectedTab) {
                EvaTab.HOME -> WearableHomeScreen(
                    viewModel = viewModel,
                    onNavigateToDevices = { selectedTab = EvaTab.DEVICES },
                    onNavigateToSettings = { selectedTab = EvaTab.YOU }
                )
                EvaTab.ACTIVITY -> ActivityScreen(
                    viewModel = viewModel,
                    onNavigateToHome = { selectedTab = EvaTab.HOME }
                )
                EvaTab.DEVICES -> DevicesHubScreen(
                    bleManager = bleManager,
                    viewModel = viewModel,
                    onNavigateBack = { selectedTab = EvaTab.HOME }
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
