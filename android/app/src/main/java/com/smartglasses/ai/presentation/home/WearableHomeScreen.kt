package com.smartglasses.ai.presentation.home

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.*
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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.core.bluetooth.DeviceConnectionState
import com.smartglasses.ai.domain.models.AssistantState
import com.smartglasses.ai.presentation.components.EvaAtmosphere
import com.smartglasses.ai.presentation.settings.BackendConfigDialog
import com.smartglasses.ai.presentation.theme.*

/**
 * WearableHomeScreen: High-End Nature-First Mobile Companion for EVA.
 * Matches the reference design with the ambient frosted orb, context header,
 * weather widget, and 3 frosted status chips.
 */
@Composable
fun WearableHomeScreen(
    viewModel: WearableHomeViewModel,
    onNavigateToDevices: () -> Unit = {},
    onNavigateToSettings: () -> Unit = {}
) {
    val state by viewModel.uiState.collectAsState()

    if (state.isConfigDialogOpen) {
        BackendConfigDialog(
            currentUrl = state.serverUrl,
            onDismiss = { viewModel.closeConfigDialog() },
            onSaveUrl = { newUrl -> viewModel.updateServerUrl(newUrl) },
            onTestConnection = { testUrl, cb -> viewModel.testBackendConnection(testUrl, cb) }
        )
    }

    val isGlassesConnected = state.deviceConnectionState == DeviceConnectionState.CONNECTED_ESP32 ||
            state.deviceConnectionState == DeviceConnectionState.CONNECTED_SIMULATED

    EvaAtmosphere {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 22.dp, vertical = 18.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            // =============================================================
            // 1. TOP BAR: HAMBURGER + E V A + PROFILE AVATAR
            // =============================================================
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(14.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Menu,
                        contentDescription = "Menu",
                        tint = EvaPrimaryBlack,
                        modifier = Modifier
                            .size(24.dp)
                            .clickable { onNavigateToSettings() }
                    )

                    Text(
                        text = "E V A",
                        fontFamily = FontFamily.SansSerif,
                        fontWeight = FontWeight.Bold,
                        fontSize = 18.sp,
                        letterSpacing = 4.sp,
                        color = EvaPrimaryBlack
                    )
                }

                // Yash Profile Avatar with Subtle Green Rim
                Box(
                    modifier = Modifier
                        .size(38.dp)
                        .clip(CircleShape)
                        .background(EvaMistGreen)
                        .border(1.5.dp, EvaPaleGreen, CircleShape)
                        .clickable { onNavigateToSettings() },
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.Person,
                        contentDescription = "Profile",
                        tint = EvaPrimaryGreen,
                        modifier = Modifier.size(22.dp)
                    )
                }
            }

            // =============================================================
            // 2. CONTEXT GREETING & FLOATING WEATHER CARD
            // =============================================================
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Good morning,",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Normal,
                        color = EvaPrimaryBlack,
                        letterSpacing = (-0.5).sp
                    )
                    Text(
                        text = "Yash.",
                        fontSize = 28.sp,
                        fontWeight = FontWeight.Bold,
                        color = EvaPrimaryBlack,
                        letterSpacing = (-0.5).sp
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "A calmer, brighter you",
                        fontSize = 13.sp,
                        color = EvaMutedText,
                        fontWeight = FontWeight.Normal
                    )
                }

                // Frosted Weather Pill
                Box(
                    modifier = Modifier
                        .background(EvaPureWhite.copy(alpha = 0.85f), RoundedCornerShape(16.dp))
                        .border(1.dp, EvaBorderSubtle, RoundedCornerShape(16.dp))
                        .padding(horizontal = 14.dp, vertical = 10.dp)
                ) {
                    Column(horizontalAlignment = Alignment.End) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.WbSunny,
                                contentDescription = "Weather",
                                tint = EvaAmberSun,
                                modifier = Modifier.size(16.dp)
                            )
                            Text(
                                text = "22°",
                                fontSize = 15.sp,
                                fontWeight = FontWeight.Bold,
                                color = EvaPrimaryBlack
                            )
                        }
                        Text(
                            text = "• Clear",
                            fontSize = 11.sp,
                            color = EvaMutedText,
                            fontWeight = FontWeight.Medium
                        )
                        Text(
                            text = "Delhi, IN",
                            fontSize = 10.sp,
                            color = EvaMutedText
                        )
                    }
                }
            }

            // =============================================================
            // 3. CENTER HERO: LARGE FROSTED GLASS INTERACTION ORB
            // =============================================================
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 12.dp),
                contentAlignment = Alignment.Center
            ) {
                val isListening = state.assistantState == AssistantState.LISTENING
                val isResponding = state.assistantState == AssistantState.RESPONDING
                val isThinking = state.assistantState == AssistantState.PROCESSING

                // Outer ambient glow ring
                Box(
                    modifier = Modifier
                        .size(240.dp)
                        .clip(CircleShape)
                        .background(
                            Brush.radialGradient(
                                colors = listOf(
                                    EvaPrimaryGreen.copy(alpha = if (isListening) 0.35f else 0.20f),
                                    EvaPaleGreen.copy(alpha = 0.15f),
                                    Color.Transparent
                                )
                            )
                        )
                )

                // Main Frosted Glass Sphere
                Box(
                    modifier = Modifier
                        .size(190.dp)
                        .clip(CircleShape)
                        .background(
                            Brush.radialGradient(
                                colors = listOf(
                                    EvaPureWhite.copy(alpha = 0.92f),
                                    EvaWarmIvory.copy(alpha = 0.75f),
                                    EvaMistGreen.copy(alpha = 0.85f)
                                )
                            )
                        )
                        .border(
                            width = 1.5.dp,
                            brush = Brush.verticalGradient(
                                colors = listOf(
                                    Color.White.copy(alpha = 0.95f),
                                    EvaBorderSubtle.copy(alpha = 0.60f)
                                )
                            ),
                            shape = CircleShape
                        )
                        .clickable {
                            viewModel.onTalkButtonClicked()
                        },
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        // Vertical Waveform Bars
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            val barHeights = if (isListening || isResponding) {
                                listOf(14.dp, 28.dp, 40.dp, 30.dp, 16.dp)
                            } else {
                                listOf(10.dp, 20.dp, 32.dp, 22.dp, 12.dp)
                            }

                            barHeights.forEach { height ->
                                Box(
                                    modifier = Modifier
                                        .width(3.5.dp)
                                        .height(height)
                                        .clip(RoundedCornerShape(50))
                                        .background(if (isListening) EvaPrimaryGreen else EvaSoftBlack)
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(2.dp))

                        Text(
                            text = when (state.assistantState) {
                                AssistantState.LISTENING -> "Listening..."
                                AssistantState.PROCESSING -> "Thinking..."
                                AssistantState.RESPONDING -> "Responding..."
                                else -> "Tap to talk"
                            },
                            fontSize = 15.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = if (isListening) EvaPrimaryGreen else EvaPrimaryBlack
                        )

                        Text(
                            text = if (isGlassesConnected) "EVA is ready" else "Standby",
                            fontSize = 11.sp,
                            color = EvaMutedText,
                            fontWeight = FontWeight.Normal
                        )
                    }
                }
            }

            // =============================================================
            // 4. BOTTOM QUICK STATUS CHIPS (3 FROSTED GLASS CARDS)
            // =============================================================
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 6.dp),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                // Card 1: Glasses Connected
                Card(
                    modifier = Modifier
                        .weight(1f)
                        .clickable { onNavigateToDevices() },
                    shape = RoundedCornerShape(18.dp),
                    colors = CardDefaults.cardColors(containerColor = EvaPureWhite.copy(alpha = 0.88f)),
                    border = androidx.compose.foundation.BorderStroke(1.dp, EvaBorderSubtle)
                ) {
                    Column(
                        modifier = Modifier.padding(14.dp),
                        verticalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Default.Visibility,
                                contentDescription = "Glasses",
                                tint = EvaPrimaryBlack,
                                modifier = Modifier.size(18.dp)
                            )
                            Box(
                                modifier = Modifier
                                    .size(7.dp)
                                    .clip(CircleShape)
                                    .background(if (isGlassesConnected) EvaPrimaryGreen else EvaMutedText)
                            )
                        }
                        Text(
                            text = "Glasses",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Medium,
                            color = EvaMutedText
                        )
                        Text(
                            text = if (isGlassesConnected) "Connected" else "Standby",
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Bold,
                            color = EvaPrimaryBlack
                        )
                    }
                }

                // Card 2: Battery 78%
                Card(
                    modifier = Modifier
                        .weight(1f)
                        .clickable { onNavigateToDevices() },
                    shape = RoundedCornerShape(18.dp),
                    colors = CardDefaults.cardColors(containerColor = EvaPureWhite.copy(alpha = 0.88f)),
                    border = androidx.compose.foundation.BorderStroke(1.dp, EvaBorderSubtle)
                ) {
                    Column(
                        modifier = Modifier.padding(14.dp),
                        verticalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Default.BatteryChargingFull,
                                contentDescription = "Battery",
                                tint = EvaPrimaryBlack,
                                modifier = Modifier.size(18.dp)
                            )
                            // Battery mini pill indicator
                            Box(
                                modifier = Modifier
                                    .width(16.dp)
                                    .height(6.dp)
                                    .clip(RoundedCornerShape(50))
                                    .background(EvaMistGreen)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .fillMaxHeight()
                                        .fillMaxWidth(0.78f)
                                        .background(EvaPrimaryGreen)
                                )
                            }
                        }
                        Text(
                            text = "Battery",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Medium,
                            color = EvaMutedText
                        )
                        Text(
                            text = "${state.batteryPercentage}%",
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Bold,
                            color = EvaPrimaryBlack
                        )
                    }
                }

                // Card 3: Audio TWS
                Card(
                    modifier = Modifier
                        .weight(1f)
                        .clickable { onNavigateToDevices() },
                    shape = RoundedCornerShape(18.dp),
                    colors = CardDefaults.cardColors(containerColor = EvaPureWhite.copy(alpha = 0.88f)),
                    border = androidx.compose.foundation.BorderStroke(1.dp, EvaBorderSubtle)
                ) {
                    Column(
                        modifier = Modifier.padding(14.dp),
                        verticalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Default.GraphicEq,
                                contentDescription = "Audio",
                                tint = EvaPrimaryBlack,
                                modifier = Modifier.size(18.dp)
                            )
                            Box(
                                modifier = Modifier
                                    .size(7.dp)
                                    .clip(CircleShape)
                                    .background(EvaPrimaryGreen)
                            )
                        }
                        Text(
                            text = "Audio",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Medium,
                            color = EvaMutedText
                        )
                        Text(
                            text = "TWS",
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Bold,
                            color = EvaPrimaryBlack
                        )
                    }
                }
            }
        }
    }
}
