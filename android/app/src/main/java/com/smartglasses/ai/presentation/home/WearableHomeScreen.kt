package com.smartglasses.ai.presentation.home

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Headset
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Send
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
import com.smartglasses.ai.core.bluetooth.DeviceConnectionState
import com.smartglasses.ai.core.network.ConnectionState
import com.smartglasses.ai.domain.models.AssistantState
import com.smartglasses.ai.presentation.components.EvaAtmosphere
import com.smartglasses.ai.presentation.settings.BackendConfigDialog
import com.smartglasses.ai.presentation.theme.*

/**
 * WearableHomeScreen: The Everyday Mobile Companion for EVA.
 * A calm, premium, light interface focused on everyday voice assistance,
 * device readiness, and glanceable daily context.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WearableHomeScreen(
    viewModel: WearableHomeViewModel,
    onNavigateToDevices: () -> Unit = {}
) {
    val state by viewModel.uiState.collectAsState()
    var inputText by remember { mutableStateOf("") }

    if (state.isConfigDialogOpen) {
        BackendConfigDialog(
            currentUrl = state.serverUrl,
            onDismiss = { viewModel.closeConfigDialog() },
            onSaveUrl = { newUrl -> viewModel.updateServerUrl(newUrl) },
            onTestConnection = { testUrl, cb -> viewModel.testBackendConnection(testUrl, cb) }
        )
    }

    val isGlassesConnected = state.deviceConnectionState == DeviceConnectionState.CONNECTED
    val isOnline = state.connectionState == ConnectionState.CONNECTED

    EvaAtmosphere {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 24.dp, vertical = 20.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            // 1. Top Header: Brand & Live Status
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "EVA",
                        fontFamily = FontFamily.SansSerif,
                        fontWeight = FontWeight.Bold,
                        fontSize = 22.sp,
                        letterSpacing = 2.sp,
                        color = EvaPrimaryBlack
                    )

                    // Live Status Pill
                    Row(
                        modifier = Modifier
                            .background(EvaMistGreen, RoundedCornerShape(50))
                            .border(1.dp, EvaPaleGreen, RoundedCornerShape(50))
                            .padding(horizontal = 10.dp, vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(6.dp)
                                .clip(CircleShape)
                                .background(if (isGlassesConnected || isOnline) EvaPrimaryGreen else EvaMutedText)
                        )
                        Text(
                            text = if (isGlassesConnected) "Connected" else if (isOnline) "Ready" else "Standby",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Medium,
                            color = EvaDeepGreen
                        )
                    }
                }

                Text(
                    text = "Good morning, Yash.",
                    fontSize = 26.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = EvaPrimaryBlack,
                    letterSpacing = (-0.5).sp,
                    modifier = Modifier.padding(top = 12.dp)
                )

                Text(
                    text = "Your glasses are active and listening for your day.",
                    fontSize = 13.sp,
                    color = EvaMutedText
                )
            }

            // 2. Center: Refined Voice Interaction Surface
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 16.dp),
                contentAlignment = Alignment.Center
            ) {
                val isListening = state.assistantState == AssistantState.LISTENING
                val isResponding = state.assistantState == AssistantState.RESPONDING
                val isThinking = state.assistantState == AssistantState.THINKING

                val orbBorderColor by animateColorAsState(
                    targetValue = if (isListening) EvaPrimaryGreen else if (isResponding) EvaSoftGreen else EvaBorderSubtle,
                    animationSpec = tween(400),
                    label = "OrbBorder"
                )

                val orbBgColor by animateColorAsState(
                    targetValue = if (isListening) EvaMistGreen else EvaPureWhite,
                    animationSpec = tween(400),
                    label = "OrbBg"
                )

                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .size(130.dp)
                            .clip(CircleShape)
                            .background(orbBgColor)
                            .border(1.5.dp, orbBorderColor, CircleShape)
                            .clickable {
                                if (isListening) viewModel.stopListening() else viewModel.startListening()
                            },
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Mic,
                            contentDescription = "Talk to EVA",
                            tint = if (isListening) EvaPrimaryGreen else EvaPrimaryBlack,
                            modifier = Modifier.size(36.dp)
                        )
                    }

                    Text(
                        text = when (state.assistantState) {
                            AssistantState.LISTENING -> "Listening..."
                            AssistantState.THINKING -> "Thinking..."
                            AssistantState.RESPONDING -> "Responding..."
                            else -> "Talk to EVA"
                        },
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium,
                        color = if (isListening) EvaPrimaryGreen else EvaPrimaryBlack
                    )
                }
            }

            // 3. Bottom: Quick Everyday Context Cards
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                // Device Quick Glance
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(EvaPureWhite, RoundedCornerShape(14.dp))
                        .border(1.dp, EvaBorderSubtle, RoundedCornerShape(14.dp))
                        .clickable { onNavigateToDevices() }
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(36.dp)
                                .background(EvaMistGreen, RoundedCornerShape(8.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.Headset,
                                contentDescription = null,
                                tint = EvaPrimaryGreen,
                                modifier = Modifier.size(20.dp)
                            )
                        }
                        Column {
                            Text(
                                text = "EVA Glasses",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = EvaPrimaryBlack
                            )
                            Text(
                                text = "Battery 78% • TWS Audio Connected",
                                fontSize = 12.sp,
                                color = EvaMutedText
                            )
                        }
                    }

                    Text(
                        text = "Ready",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Medium,
                        color = EvaPrimaryGreen
                    )
                }

                // Today's Glance Card
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(EvaPureWhite, RoundedCornerShape(14.dp))
                        .border(1.dp, EvaBorderSubtle, RoundedCornerShape(14.dp))
                        .padding(16.dp)
                ) {
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(
                            text = "Today's Glance",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            color = EvaMutedText,
                            letterSpacing = 1.sp
                        )
                        Text(
                            text = "3 unread messages • 2 calendar events",
                            fontSize = 13.sp,
                            color = EvaPrimaryBlack,
                            fontWeight = FontWeight.Medium
                        )
                        Text(
                            text = "Next: Team sync at 2:30 PM",
                            fontSize = 12.sp,
                            color = EvaMutedText
                        )
                    }
                }

                // Text Input Bar
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(EvaPureWhite, RoundedCornerShape(50))
                        .border(1.dp, EvaBorderSubtle, RoundedCornerShape(50))
                        .padding(horizontal = 14.dp, vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    TextField(
                        value = inputText,
                        onValueChange = { inputText = it },
                        placeholder = { Text("Ask EVA anything...", color = EvaMutedText, fontSize = 13.sp) },
                        colors = TextFieldDefaults.colors(
                            focusedContainerColor = Color.Transparent,
                            unfocusedContainerColor = Color.Transparent,
                            disabledContainerColor = Color.Transparent,
                            focusedIndicatorColor = Color.Transparent,
                            unfocusedIndicatorColor = Color.Transparent
                        ),
                        modifier = Modifier.weight(1f)
                    )

                    IconButton(
                        onClick = {
                            if (inputText.isNotBlank()) {
                                viewModel.sendMessage(inputText)
                                inputText = ""
                            }
                        }
                    ) {
                        Icon(
                            imageVector = Icons.Default.Send,
                            contentDescription = "Send",
                            tint = EvaPrimaryGreen,
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }
            }
        }
    }
}
