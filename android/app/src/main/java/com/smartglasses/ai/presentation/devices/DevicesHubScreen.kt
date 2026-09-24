package com.smartglasses.ai.presentation.devices

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.core.bluetooth.BleManager
import com.smartglasses.ai.core.bluetooth.DeviceConnectionState
import com.smartglasses.ai.presentation.home.WearableHomeViewModel
import com.smartglasses.ai.presentation.theme.*

/**
 * DevicesHubScreen: Matches Screen 2 (EVA Device) from the reference design.
 * Features the nature gradient hero banner, 3-metric quick cards (Battery, Audio, Firmware),
 * clean list options (Health, Connectivity, Permissions, Diagnostics), and the Manage Device CTA.
 */
@Composable
fun DevicesHubScreen(
    bleManager: BleManager,
    viewModel: WearableHomeViewModel,
    onNavigateBack: () -> Unit = {},
    onOpenDiagnostics: () -> Unit = {}
) {
    val glassesState by bleManager.glassesState.collectAsState()
    val homeState by viewModel.uiState.collectAsState()

    val isConnected = glassesState.connectionState == DeviceConnectionState.CONNECTED_ESP32 ||
            glassesState.connectionState == DeviceConnectionState.CONNECTED_SIMULATED ||
            homeState.deviceConnectionState == DeviceConnectionState.CONNECTED_ESP32 ||
            homeState.deviceConnectionState == DeviceConnectionState.CONNECTED_SIMULATED

    Scaffold(
        containerColor = EvaIvory
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 22.dp, vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // =============================================================
            // 1. TOP BAR: BACK ARROW + TITLE + MORE OPTIONS
            // =============================================================
            item {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 6.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = "Back",
                        tint = EvaPrimaryBlack,
                        modifier = Modifier
                            .size(22.dp)
                            .clickable { onNavigateBack() }
                    )

                    Text(
                        text = "EVA Device",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = EvaPrimaryBlack
                    )

                    Icon(
                        imageVector = Icons.Default.MoreHoriz,
                        contentDescription = "Options",
                        tint = EvaPrimaryBlack,
                        modifier = Modifier.size(24.dp)
                    )
                }
            }

            // =============================================================
            // 2. HERO DEVICE BANNER (DEEP NATURE GRADIENT CARD)
            // =============================================================
            item {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(22.dp))
                        .clickable { bleManager.toggleConnectionMode() },
                    shape = RoundedCornerShape(22.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.Transparent)
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(130.dp)
                            .background(
                                Brush.linearGradient(
                                    colors = listOf(
                                        EvaDeepGreen,
                                        EvaPrimaryGreen,
                                        Color(0xFF527D60)
                                    )
                                )
                            )
                            .padding(22.dp),
                        contentAlignment = Alignment.CenterStart
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                                Text(
                                    text = "EVA Glasses",
                                    fontSize = 20.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )

                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                                ) {
                                    Box(
                                        modifier = Modifier
                                            .size(7.dp)
                                            .clip(CircleShape)
                                            .background(if (isConnected) Color(0xFF66E88A) else EvaBorderSubtle)
                                    )
                                    Text(
                                        text = if (isConnected) "Connected" else "Disconnected",
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Medium,
                                        color = Color.White.copy(alpha = 0.90f)
                                    )
                                }
                            }

                            // Circular Chevron
                            Box(
                                modifier = Modifier
                                    .size(34.dp)
                                    .clip(CircleShape)
                                    .background(Color.White.copy(alpha = 0.18f)),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(
                                    imageVector = Icons.Default.ChevronRight,
                                    contentDescription = "Details",
                                    tint = Color.White,
                                    modifier = Modifier.size(20.dp)
                                )
                            }
                        }
                    }
                }
            }

            // =============================================================
            // 3. 3-METRIC QUICK CARDS: BATTERY, AUDIO, FIRMWARE
            // =============================================================
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    // Battery Card
                    Card(
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(18.dp),
                        colors = CardDefaults.cardColors(containerColor = EvaPureWhite),
                        border = androidx.compose.foundation.BorderStroke(1.dp, EvaBorderSubtle)
                    ) {
                        Column(
                            modifier = Modifier.padding(14.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.BatteryChargingFull,
                                contentDescription = "Battery",
                                tint = EvaPrimaryBlack,
                                modifier = Modifier.size(20.dp)
                            )
                            Text(
                                text = "Battery",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Medium,
                                color = EvaMutedText
                            )
                            Text(
                                text = "${homeState.batteryPercentage}%",
                                fontSize = 15.sp,
                                fontWeight = FontWeight.Bold,
                                color = EvaPrimaryBlack
                            )
                            // Progress bar
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(4.dp)
                                    .clip(RoundedCornerShape(50))
                                    .background(EvaMistGreen)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .fillMaxHeight()
                                        .fillMaxWidth(homeState.batteryPercentage / 100f)
                                        .background(EvaPrimaryGreen)
                                )
                            }
                        }
                    }

                    // Audio Card
                    Card(
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(18.dp),
                        colors = CardDefaults.cardColors(containerColor = EvaPureWhite),
                        border = androidx.compose.foundation.BorderStroke(1.dp, EvaBorderSubtle)
                    ) {
                        Column(
                            modifier = Modifier.padding(14.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.GraphicEq,
                                contentDescription = "Audio",
                                tint = EvaPrimaryBlack,
                                modifier = Modifier.size(20.dp)
                            )
                            Text(
                                text = "Audio",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Medium,
                                color = EvaMutedText
                            )
                            Text(
                                text = "TWS",
                                fontSize = 15.sp,
                                fontWeight = FontWeight.Bold,
                                color = EvaPrimaryBlack
                            )
                            Text(
                                text = "Active",
                                fontSize = 10.sp,
                                color = EvaMutedText
                            )
                        }
                    }

                    // Firmware Card
                    Card(
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(18.dp),
                        colors = CardDefaults.cardColors(containerColor = EvaPureWhite),
                        border = androidx.compose.foundation.BorderStroke(1.dp, EvaBorderSubtle)
                    ) {
                        Column(
                            modifier = Modifier.padding(14.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Memory,
                                contentDescription = "Firmware",
                                tint = EvaPrimaryBlack,
                                modifier = Modifier.size(20.dp)
                            )
                            Text(
                                text = "Firmware",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Medium,
                                color = EvaMutedText
                            )
                            Text(
                                text = "v1.2.3",
                                fontSize = 15.sp,
                                fontWeight = FontWeight.Bold,
                                color = EvaPrimaryBlack
                            )
                            Text(
                                text = "Up to date",
                                fontSize = 10.sp,
                                color = EvaMutedText
                            )
                        }
                    }
                }
            }

            // =============================================================
            // 4. INTERACTIVE LIST OPTIONS (HEALTH, CONNECTIVITY, PERMS, DIAG)
            // =============================================================
            item {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    DeviceMenuRow(
                        icon = Icons.Default.FavoriteBorder,
                        title = "Device Health",
                        subtitle = "All systems normal",
                        hasStatusDot = true,
                        onClick = { onOpenDiagnostics() }
                    )

                    DeviceMenuRow(
                        icon = Icons.Default.Sensors,
                        title = "Connectivity",
                        subtitle = "Bluetooth, Wi-Fi, Cloud",
                        onClick = { bleManager.toggleConnectionMode() }
                    )

                    DeviceMenuRow(
                        icon = Icons.Default.Lock,
                        title = "Permissions",
                        subtitle = "Camera, Mic, Location",
                        onClick = {}
                    )

                    DeviceMenuRow(
                        icon = Icons.Default.ShowChart,
                        title = "Diagnostics",
                        subtitle = "Run system check",
                        onClick = { onOpenDiagnostics() }
                    )
                }
            }

            // =============================================================
            // 5. BOTTOM CTA BANNER: MANAGE DEVICE
            // =============================================================
            item {
                Spacer(modifier = Modifier.height(4.dp))
                Button(
                    onClick = { onOpenDiagnostics() },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(54.dp),
                    shape = RoundedCornerShape(18.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = EvaDeepGreen)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(10.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Settings,
                                contentDescription = "Manage",
                                tint = Color.White,
                                modifier = Modifier.size(18.dp)
                            )
                            Text(
                                text = "Manage Device",
                                fontSize = 15.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = Color.White
                            )
                        }
                        Icon(
                            imageVector = Icons.Default.ChevronRight,
                            contentDescription = "Go",
                            tint = Color.White,
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun DeviceMenuRow(
    icon: ImageVector,
    title: String,
    subtitle: String,
    hasStatusDot: Boolean = false,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(containerColor = EvaPureWhite),
        border = androidx.compose.foundation.BorderStroke(1.dp, EvaBorderSubtle)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 14.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(36.dp)
                        .clip(CircleShape)
                        .background(EvaMistGreen),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = icon,
                        contentDescription = title,
                        tint = EvaPrimaryBlack,
                        modifier = Modifier.size(18.dp)
                    )
                }

                Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Text(
                            text = title,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = EvaPrimaryBlack
                        )
                        if (hasStatusDot) {
                            Box(
                                modifier = Modifier
                                    .size(6.dp)
                                    .clip(CircleShape)
                                    .background(EvaPrimaryGreen)
                            )
                        }
                    }
                    Text(
                        text = subtitle,
                        fontSize = 12.sp,
                        color = EvaMutedText
                    )
                }
            }

            Icon(
                imageVector = Icons.Default.ChevronRight,
                contentDescription = "Open",
                tint = EvaMutedText,
                modifier = Modifier.size(18.dp)
            )
        }
    }
}
