package com.smartglasses.ai.presentation.devices

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.core.bluetooth.BleManager
import com.smartglasses.ai.core.bluetooth.DeviceConnectionState
import com.smartglasses.ai.core.bluetooth.SmartGlassesState
import com.smartglasses.ai.presentation.glasses.WearableDiagnosticsCard
import com.smartglasses.ai.presentation.home.WearableHomeViewModel
import com.smartglasses.ai.presentation.theme.*

@Composable
fun DevicesHubScreen(
    bleManager: BleManager,
    viewModel: WearableHomeViewModel,
    onNavigateToPairing: () -> Unit = {}
) {
    val glassesState by bleManager.glassesState.collectAsState()
    val isScanning by bleManager.isScanningFlow.collectAsState()
    val discoveredList by bleManager.discoveredDevices.collectAsState()
    var showAdvancedDiagnostics by remember { mutableStateOf(false) }

    val isConnected = glassesState.connectionState == DeviceConnectionState.CONNECTED_ESP32 ||
            glassesState.connectionState == DeviceConnectionState.CONNECTED_SIMULATED

    Scaffold(
        containerColor = LaraIvory
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 24.dp, vertical = 20.dp),
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            // Header
            item {
                Column(modifier = Modifier.padding(top = 8.dp)) {
                    Text(
                        text = "Devices",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        color = LaraTextPrimaryLight
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Connected wearable hardware and device control.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = LaraTextSecondaryLight
                    )
                }
            }

            // SMART GLASSES Section
            item {
                Text(
                    text = "SMART GLASSES",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.SemiBold,
                    letterSpacing = 1.2.sp,
                    color = LaraMutedOrange
                )
            }

            // Smart Glasses Primary Card
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    border = androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight)
                ) {
                    Column(
                        modifier = Modifier.padding(20.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        // Title + Status
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                Text(
                                    text = glassesState.deviceName.ifBlank { "SmartGlasses-S3" },
                                    fontSize = 18.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = LaraTextPrimaryLight
                                )
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                                ) {
                                    Box(
                                        modifier = Modifier
                                            .size(7.dp)
                                            .clip(CircleShape)
                                            .background(if (isConnected) LaraEmerald else LaraTextSecondaryLight)
                                    )
                                    Text(
                                        text = if (isConnected) "Connected" else "Disconnected",
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Medium,
                                        color = if (isConnected) LaraEmerald else LaraTextSecondaryLight
                                    )
                                }
                            }

                            // Primary Action Button
                            Button(
                                onClick = {
                                    if (isConnected) {
                                        bleManager.disconnect()
                                    } else {
                                        bleManager.toggleConnectionMode()
                                    }
                                },
                                shape = RoundedCornerShape(8.dp),
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = if (isConnected) LaraIvory else LaraMutedOrange,
                                    contentColor = if (isConnected) LaraTextPrimaryLight else Color.White
                                ),
                                border = if (isConnected) androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight) else null
                            ) {
                                Text(
                                    text = if (isConnected) "Disconnect" else "Connect",
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.SemiBold
                                )
                            }
                        }

                        Divider(color = LaraBorderLight, thickness = 0.5.dp)

                        // Useful Information Grid (Camera, Mic, Battery)
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            DeviceStatusColumn(
                                label = "Camera",
                                value = if (glassesState.cameraAvailable) "Ready" else "Standby",
                                isPositive = glassesState.cameraAvailable
                            )
                            DeviceStatusColumn(
                                label = "Microphone",
                                value = if (glassesState.microphoneAvailable) "Ready" else "Standby",
                                isPositive = glassesState.microphoneAvailable
                            )
                            DeviceStatusColumn(
                                label = "Battery",
                                value = if (isConnected) "${glassesState.battery}%" else "Good",
                                isPositive = true
                            )
                        }
                    }
                }
            }

            // Pairing / Nearby Discovery Section
            item {
                Text(
                    text = "PAIRING & DISCOVERY",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.SemiBold,
                    letterSpacing = 1.2.sp,
                    color = LaraMutedOrange
                )
            }

            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    border = androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight)
                ) {
                    Column(
                        modifier = Modifier.padding(20.dp),
                        verticalArrangement = Arrangement.spacedBy(14.dp)
                    ) {
                        Text(
                            text = "Connect Your Glasses",
                            fontSize = 15.sp,
                            fontWeight = FontWeight.Bold,
                            color = LaraTextPrimaryLight
                        )
                        Text(
                            text = "Bring your LARA Smart Glasses nearby to discover and pair.",
                            fontSize = 13.sp,
                            color = LaraTextSecondaryLight,
                            lineHeight = 18.sp
                        )

                        OutlinedButton(
                            onClick = {
                                if (isScanning) bleManager.stopScan() else bleManager.startScan()
                            },
                            shape = RoundedCornerShape(8.dp),
                            border = androidx.compose.foundation.BorderStroke(1.dp, LaraMutedOrange),
                            colors = ButtonDefaults.outlinedButtonColors(contentColor = LaraMutedOrange),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            if (isScanning) {
                                CircularProgressIndicator(
                                    modifier = Modifier.size(16.dp),
                                    color = LaraMutedOrange,
                                    strokeWidth = 2.dp
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(text = "Searching for Glasses...", fontSize = 13.sp)
                            } else {
                                Icon(Icons.Default.Add, contentDescription = null, modifier = Modifier.size(16.dp))
                                Spacer(modifier = Modifier.width(6.dp))
                                Text(text = "Pair New Glasses", fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                            }
                        }

                        // Discovered devices list
                        if (discoveredList.isNotEmpty()) {
                            Divider(color = LaraBorderLight, thickness = 0.5.dp)
                            discoveredList.forEach { dev ->
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                                        Text(
                                            text = dev.name.ifBlank { "SmartGlasses-S3" },
                                            fontSize = 14.sp,
                                            fontWeight = FontWeight.SemiBold,
                                            color = LaraTextPrimaryLight
                                        )
                                        Text(
                                            text = "XIAO ESP32-S3 Sense · Available",
                                            fontSize = 11.sp,
                                            color = LaraTextSecondaryLight
                                        )
                                    }
                                    Button(
                                        onClick = { bleManager.pairDevice(dev.address, dev.name) },
                                        shape = RoundedCornerShape(6.dp),
                                        colors = ButtonDefaults.buttonColors(containerColor = LaraMutedOrange)
                                    ) {
                                        Text(text = "Connect", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Phone Device Companion Section
            item {
                Text(
                    text = "PHONE COMPANION",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.SemiBold,
                    letterSpacing = 1.2.sp,
                    color = LaraMutedOrange
                )
            }

            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    border = androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(18.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            Text(
                                text = "Local Phone Control Authority",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = LaraTextPrimaryLight
                            )
                            Text(
                                text = "Background service active · Screen-off execution enabled",
                                fontSize = 12.sp,
                                color = LaraTextSecondaryLight
                            )
                        }
                        Surface(
                            shape = RoundedCornerShape(4.dp),
                            color = LaraEmeraldBg
                        ) {
                            Text(
                                text = "Active",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = LaraEmerald,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                            )
                        }
                    }
                }
            }

            // Advanced Diagnostics (Collapsed by default)
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    border = androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable { showAdvancedDiagnostics = !showAdvancedDiagnostics },
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "Advanced Diagnostics",
                                fontSize = 13.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = LaraTextSecondaryLight
                            )
                            Icon(
                                imageVector = if (showAdvancedDiagnostics) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                                contentDescription = "Toggle",
                                tint = LaraTextSecondaryLight
                            )
                        }

                        AnimatedVisibility(visible = showAdvancedDiagnostics) {
                            Column(modifier = Modifier.padding(top = 12.dp)) {
                                WearableDiagnosticsCard(state = glassesState)
                            }
                        }
                    }
                }
            }

            item {
                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }
}

@Composable
private fun DeviceStatusColumn(
    label: String,
    value: String,
    isPositive: Boolean
) {
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Text(
            text = label,
            fontSize = 11.sp,
            color = LaraTextSecondaryLight
        )
        Text(
            text = value,
            fontSize = 13.sp,
            fontWeight = FontWeight.SemiBold,
            color = if (isPositive) LaraEmerald else LaraTextPrimaryLight
        )
    }
}
