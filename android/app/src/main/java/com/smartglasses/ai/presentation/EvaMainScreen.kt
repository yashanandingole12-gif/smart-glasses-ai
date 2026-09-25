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
                    .navigationBarsPadding()
                    .padding(horizontal = 24.dp, vertical = 12.dp),
                contentAlignment = Alignment.Center
            ) {
                Surface(
                    shape = RoundedCornerShape(26.dp),
                    color = EvaPureWhite.copy(alpha = 0.92f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, EvaBorderSubtle),
                    shadowElevation = 8.dp,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 10.dp, horizontal = 14.dp),
                        horizontalArrangement = Arrangement.SpaceAround,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        EvaTab.values().forEach { tab ->
                            val isSelected = selectedTab == tab
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.spacedBy(4.dp),
                                modifier = Modifier
                                    .clip(RoundedCornerShape(16.dp))
                                    .clickable { selectedTab = tab }
                                    .padding(horizontal = 14.dp, vertical = 6.dp)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(36.dp)
                                        .clip(CircleShape)
                                        .background(if (isSelected) EvaMistGreen else Color.Transparent),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Icon(
                                        imageVector = tab.icon,
                                        contentDescription = tab.label,
                                        tint = if (isSelected) EvaPrimaryGreen else EvaMutedText,
                                        modifier = Modifier.size(20.dp)
                                    )
                                }
                                Text(
                                    text = tab.label,
                                    fontSize = 11.sp,
                                    fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                                    color = if (isSelected) EvaPrimaryBlack else EvaMutedText
                                )
                            }
                        }
                    }
                }
            }
        }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            when (selectedTab) {
                EvaTab.HOME -> WearableHomeScreen(
                    viewModel = viewModel,
                    bleManager = bleManager,
                    onNavigateToDevices = { selectedTab = EvaTab.DEVICES },
                    onNavigateToSettings = { selectedTab = EvaTab.YOU },
                    onNavigateToActivity = { selectedTab = EvaTab.ACTIVITY }
                )
                EvaTab.ACTIVITY -> ActivityScreen(
                    onNavigateToHome = { selectedTab = EvaTab.HOME }
                )
                EvaTab.DEVICES -> DevicesHubScreen(
                    bleManager = bleManager,
                    onNavigateBack = { selectedTab = EvaTab.HOME }
                )
                EvaTab.YOU -> YouProfileScreen(
                    viewModel = viewModel,
                    onNavigateBack = { selectedTab = EvaTab.HOME }
                )
            }
        }
    }
}
