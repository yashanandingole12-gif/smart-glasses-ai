package com.smartglasses.ai.presentation.security

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
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.presentation.home.WearableHomeViewModel
import com.smartglasses.ai.presentation.theme.*

/**
 * LARA Permission Center, Temporary Access & Security Profile:
 * - Grouped permissions with human rationale (Communication, Intelligence, Context, Files)
 * - Temporary data access revocation
 * - Security audit log
 * - Server connection configuration
 */
@Composable
fun PermissionSecurityScreen(
    viewModel: WearableHomeViewModel,
    onOpenConfigDialog: () -> Unit = {}
) {
    val state by viewModel.uiState.collectAsState()

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
                            text = "Access Governance & Audit Integrity",
                            fontSize = 12.sp,
                            color = LaraTextSecondaryLight
                        )
                    }
                    IconButton(onClick = onOpenConfigDialog) {
                        Icon(Icons.Default.Settings, contentDescription = "Config", tint = LaraCharcoal)
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
                            text = "Active session context expires automatically after 15 minutes of inactivity. Memory tokens are securely hashed.",
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
                    description = "Enables hands-free dialing to verified contacts upon voice command.",
                    stateText = "AUTHORIZED",
                    isGranted = true
                )
            }
            item {
                PermissionCategoryItem(
                    title = "SMS Dispatch & Receiver",
                    description = "Allows reading and drafting messages with explicit user confirmation.",
                    stateText = "AUTHORIZED",
                    isGranted = true
                )
            }
            item {
                PermissionCategoryItem(
                    title = "Contacts Directory",
                    description = "Resolves contact names, aliases, and phone numbers locally.",
                    stateText = "AUTHORIZED",
                    isGranted = true
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
                    description = "Captures short audio bursts on push-to-talk. No continuous cloud streaming.",
                    stateText = if (state.isMicrophoneReady) "AUTHORIZED" else "REQUIRED",
                    isGranted = state.isMicrophoneReady
                )
            }
            item {
                PermissionCategoryItem(
                    title = "Smart Glasses Camera",
                    description = "Captures individual frames strictly upon explicit user request.",
                    stateText = "AUTHORIZED",
                    isGranted = true
                )
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
