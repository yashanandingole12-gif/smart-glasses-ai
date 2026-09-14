package com.smartglasses.ai.presentation.security

import android.app.Activity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.core.permissions.PermissionManager
import com.smartglasses.ai.presentation.home.WearableHomeViewModel
import com.smartglasses.ai.presentation.theme.*

/**
 * LARA Permission Center, Real-Time Access Governance & Security Profile:
 * - Dynamic, live permission indicators checking actual Android system state
 * - One-click "Grant Missing Permissions" runtime dialog launcher
 * - Direct System App Settings shortcut for permanent authorization
 * - Temporary data access revocation and memory purging
 */
@Composable
fun PermissionSecurityScreen(
    viewModel: WearableHomeViewModel,
    onOpenConfigDialog: () -> Unit = {}
) {
    val context = LocalContext.current
    val state by viewModel.uiState.collectAsState()

    var refreshKey by remember { mutableStateOf(0) }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions()
    ) {
        refreshKey++
        viewModel.checkBackendHealth()
    }

    val hasAudio = remember(refreshKey) { PermissionManager.hasAudioPermission(context) }
    val hasLocation = remember(refreshKey) { PermissionManager.hasLocationPermission(context) }
    val hasSms = remember(refreshKey) { PermissionManager.hasSmsPermission(context) }
    val hasContacts = remember(refreshKey) { PermissionManager.hasContactsPermission(context) }
    val hasPhone = remember(refreshKey) { PermissionManager.hasPhonePermission(context) }
    val hasBluetooth = remember(refreshKey) { PermissionManager.hasBluetoothPermission(context) }

    val missingPermissions = remember(refreshKey) { PermissionManager.getMissingPermissions(context) }
    val allGranted = missingPermissions.isEmpty()

    Scaffold(
        containerColor = LaraIvory
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 20.dp, vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Header
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "SECURITY & PERMISSIONS",
                            fontFamily = FontFamily.Serif,
                            fontWeight = FontWeight.Bold,
                            fontSize = 20.sp,
                            color = LaraCharcoal,
                            letterSpacing = 1.sp
                        )
                        Text(
                            text = "Access Governance & Hardware Control",
                            fontSize = 12.sp,
                            color = LaraTextSecondaryLight
                        )
                    }
                    IconButton(onClick = onOpenConfigDialog) {
                        Icon(Icons.Default.Settings, contentDescription = "Config", tint = LaraCharcoal)
                    }
                }
            }

            // Quick Status & Action Card
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = if (allGranted) Color(0xFFF0FDF4) else Color(0xFFFFFBEB)
                    ),
                    border = androidx.compose.foundation.BorderStroke(
                        1.dp,
                        if (allGranted) LaraEmerald.copy(alpha = 0.4f) else LaraAmber.copy(alpha = 0.4f)
                    )
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(
                                    if (allGranted) Icons.Default.CheckCircle else Icons.Default.Warning,
                                    contentDescription = null,
                                    tint = if (allGranted) LaraEmerald else LaraAmber,
                                    modifier = Modifier.size(20.dp)
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    if (allGranted) "ALL PERMISSIONS ACTIVE" else "PERMISSIONS REQUIRED",
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 12.sp,
                                    color = LaraCharcoal
                                )
                            }
                            Text(
                                if (allGranted) "SECURE" else "${missingPermissions.size} MISSING",
                                color = if (allGranted) LaraEmerald else LaraAmber,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = if (allGranted)
                                "LARA has authoritative access for hands-free voice, real SMS read/write, calling, and contacts."
                            else
                                "Some capabilities like real SMS, voice calling, or contacts resolution are restricted until authorized.",
                            fontSize = 11.sp,
                            color = LaraTextSecondaryLight,
                            lineHeight = 15.sp
                        )
                        Spacer(modifier = Modifier.height(12.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            if (!allGranted) {
                                Button(
                                    onClick = {
                                        permissionLauncher.launch(PermissionManager.REQUIRED_PERMISSIONS)
                                    },
                                    modifier = Modifier.weight(1f),
                                    colors = ButtonDefaults.buttonColors(containerColor = LaraCharcoal),
                                    shape = RoundedCornerShape(8.dp),
                                    contentPadding = PaddingValues(vertical = 8.dp)
                                ) {
                                    Icon(Icons.Default.Security, contentDescription = null, modifier = Modifier.size(14.dp), tint = Color.White)
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text("Grant Missing", fontSize = 11.sp, color = Color.White, fontWeight = FontWeight.Bold)
                                }
                            }
                            OutlinedButton(
                                onClick = {
                                    PermissionManager.openAppSettings(context)
                                },
                                modifier = Modifier.weight(1f),
                                border = androidx.compose.foundation.BorderStroke(1.dp, LaraCharcoal.copy(alpha = 0.3f)),
                                shape = RoundedCornerShape(8.dp),
                                contentPadding = PaddingValues(vertical = 8.dp)
                            ) {
                                Icon(Icons.Default.Settings, contentDescription = null, modifier = Modifier.size(14.dp), tint = LaraCharcoal)
                                Spacer(modifier = Modifier.width(6.dp))
                                Text("App Settings", fontSize = 11.sp, color = LaraCharcoal, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }
            }

            // Backend Server Configuration Card
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
                            .padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text("FastAPI Backend Server", fontWeight = FontWeight.Bold, fontSize = 13.sp, color = LaraCharcoal)
                            Text(state.serverUrl, fontSize = 11.sp, color = LaraMutedOrange, maxLines = 1)
                        }
                        Button(
                            onClick = onOpenConfigDialog,
                            colors = ButtonDefaults.buttonColors(containerColor = LaraCharcoal),
                            shape = RoundedCornerShape(8.dp),
                            contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                        ) {
                            Text("Configure", fontSize = 11.sp, color = Color.White)
                        }
                    }
                }
            }

            // Group 1: Communication Permissions
            item {
                Text(
                    text = "COMMUNICATION PERMISSIONS",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    color = LaraTextSecondaryLight,
                    letterSpacing = 0.8.sp
                )
            }
            item {
                PermissionCategoryItem(
                    title = "Telephony & Calls",
                    description = "Enables hands-free dialing to contacts and call control upon voice command.",
                    stateText = if (hasPhone) "AUTHORIZED" else "ACTION REQUIRED",
                    isGranted = hasPhone
                )
            }
            item {
                PermissionCategoryItem(
                    title = "SMS Dispatch & Receiver",
                    description = "Allows reading real SMS messages and drafting replies with spam/ad filtering.",
                    stateText = if (hasSms) "AUTHORIZED" else "ACTION REQUIRED",
                    isGranted = hasSms
                )
            }
            item {
                PermissionCategoryItem(
                    title = "Contacts Directory",
                    description = "Resolves contact names, aliases, and phone numbers locally on-device.",
                    stateText = if (hasContacts) "AUTHORIZED" else "ACTION REQUIRED",
                    isGranted = hasContacts
                )
            }

            // Group 2: Intelligence & Sensors
            item {
                Text(
                    text = "INTELLIGENCE & SENSOR CAPABILITIES",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    color = LaraTextSecondaryLight,
                    letterSpacing = 0.8.sp
                )
            }
            item {
                PermissionCategoryItem(
                    title = "Microphone (Local & ESP32)",
                    description = "Captures audio bursts on push-to-talk or hands-free wake word.",
                    stateText = if (hasAudio) "AUTHORIZED" else "ACTION REQUIRED",
                    isGranted = hasAudio
                )
            }
            item {
                PermissionCategoryItem(
                    title = "Location Context",
                    description = "Provides local temporal and environmental awareness for weather and queries.",
                    stateText = if (hasLocation) "AUTHORIZED" else "ACTION REQUIRED",
                    isGranted = hasLocation
                )
            }
            item {
                PermissionCategoryItem(
                    title = "Bluetooth & BLE Glasses",
                    description = "Connects to Seeed Studio XIAO ESP32-S3 Sense smart glasses hardware.",
                    stateText = if (hasBluetooth) "AUTHORIZED" else "ACTION REQUIRED",
                    isGranted = hasBluetooth
                )
            }

            // Temporary Data Access Card
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFFFBFBF9)),
                    border = androidx.compose.foundation.BorderStroke(1.dp, LaraAmber.copy(alpha = 0.4f))
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Default.Timer, contentDescription = null, tint = LaraAmber, modifier = Modifier.size(18.dp))
                                Spacer(modifier = Modifier.width(6.dp))
                                Text("TEMPORARY DATA ACCESS", fontWeight = FontWeight.Bold, fontSize = 12.sp, color = LaraCharcoal)
                            }
                            Text("TIME-BOUND", color = LaraAmber, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "Active session context expires automatically after 15 minutes of inactivity. Sensitive tokens are never logged.",
                            fontSize = 11.sp,
                            color = LaraTextSecondaryLight,
                            lineHeight = 15.sp
                        )
                        Spacer(modifier = Modifier.height(10.dp))
                        OutlinedButton(
                            onClick = { viewModel.clearConversation() },
                            modifier = Modifier.fillMaxWidth(),
                            border = androidx.compose.foundation.BorderStroke(1.dp, LaraMutedRed.copy(alpha = 0.5f)),
                            shape = RoundedCornerShape(8.dp),
                            contentPadding = PaddingValues(vertical = 6.dp)
                        ) {
                            Text("Purge Active Session Context", color = LaraMutedRed, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun PermissionCategoryItem(
    title: String,
    description: String,
    stateText: String,
    isGranted: Boolean
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(10.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        border = androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(title, fontWeight = FontWeight.Bold, fontSize = 13.sp, color = LaraCharcoal)
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(6.dp))
                        .background(if (isGranted) LaraEmeraldBg else LaraAmberBg)
                        .padding(horizontal = 8.dp, vertical = 3.dp)
                ) {
                    Text(
                        text = stateText,
                        color = if (isGranted) LaraEmerald else LaraAmber,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text(description, fontSize = 11.sp, color = LaraTextSecondaryLight, lineHeight = 15.sp)
        }
    }
}
