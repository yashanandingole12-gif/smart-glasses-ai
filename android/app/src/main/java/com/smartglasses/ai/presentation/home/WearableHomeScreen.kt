package com.smartglasses.ai.presentation.home

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.core.bluetooth.DeviceConnectionState
import com.smartglasses.ai.core.network.ConnectionState
import com.smartglasses.ai.domain.models.AssistantState
import com.smartglasses.ai.presentation.components.*
import com.smartglasses.ai.presentation.settings.BackendConfigDialog
import com.smartglasses.ai.presentation.theme.*

/**
 * WearableHomeScreen: The Primary Android Experience for EVA.
 * A voice-first living digital environment featuring living darkness,
 * dynamic orbital presence, organic waveform, and seamless smart glasses perception.
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

    val isOnline = state.connectionState == ConnectionState.CONNECTED

    EvaAtmosphere {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 24.dp, vertical = 20.dp)
        ) {
            Column(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.SpaceBetween
            ) {
                // 1. Top Header: EVA Title & Atmospheric Online Vitality
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "EVA",
                            fontFamily = FontFamily.Serif,
                            fontWeight = FontWeight.Bold,
                            fontSize = 24.sp,
                            letterSpacing = 3.sp,
                            color = EvaTextPure
                        )

                        // Ambient Status Dot
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(7.dp)
                                    .clip(CircleShape)
                                    .background(if (isOnline) EvaTeal else EvaSlate)
                            )
                            Text(
                                text = if (isOnline) "Living" else "Offline Realm",
                                fontSize = 11.sp,
                                letterSpacing = 0.5.sp,
                                fontWeight = FontWeight.Medium,
                                color = if (isOnline) EvaTeal else EvaTextMuted
                            )
                        }
                    }

                    // Integrated Glasses Recognition Presence
                    EvaDevicePresence(
                        connectionState = state.deviceConnectionState,
                        onNavigateToDevices = onNavigateToDevices
                    )
                }

                // 2. Spatial Center: EVA Living Presence & Voice Cadence
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(16.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        // Central Living Presence Core
                        EvaPresence(
                            state = state.assistantState,
                            isOnline = isOnline,
                            onClick = { viewModel.onTalkButtonClicked() }
                        )

                        // Organic Waveform
                        EvaWaveform(
                            isActive = state.assistantState == AssistantState.LISTENING ||
                                    state.assistantState == AssistantState.SPEAKING
                        )

                        // Partial voice transcript stream
                        if (state.partialVoiceTranscript.isNotBlank()) {
                            Text(
                                text = "\"${state.partialVoiceTranscript}\"",
                                fontSize = 14.sp,
                                fontStyle = androidx.compose.ui.text.font.FontStyle.Italic,
                                color = EvaTextSecondary
                            )
                        }

                        // Luminous Response Surface (if EVA spoken response received)
                        AnimatedVisibility(
                            visible = state.latestSpeech.isNotBlank() &&
                                    !state.latestSpeech.contains("Ready on your smart glasses"),
                            enter = fadeIn(),
                            exit = fadeOut()
                        ) {
                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(18.dp))
                                    .background(EvaSurfaceGlass)
                                    .border(1.dp, EvaBorderSubtle, RoundedCornerShape(18.dp))
                                    .padding(18.dp),
                                verticalArrangement = Arrangement.spacedBy(10.dp)
                            ) {
                                // Render captured camera photo if available
                                val imageBitmap = remember(state.latestImageBase64) {
                                    state.latestImageBase64?.let { b64 ->
                                        try {
                                            val bytes = android.util.Base64.decode(b64, android.util.Base64.DEFAULT)
                                            val bmp = android.graphics.BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
                                            bmp?.asImageBitmap()
                                        } catch (_: Exception) { null }
                                    }
                                }

                                imageBitmap?.let { bmp ->
                                    androidx.compose.foundation.Image(
                                        bitmap = bmp,
                                        contentDescription = "Smart Glasses Perception Capture",
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .heightIn(max = 200.dp)
                                            .clip(RoundedCornerShape(10.dp)),
                                        contentScale = androidx.compose.ui.layout.ContentScale.Crop
                                    )
                                }

                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = "EVA SYNTHESIS",
                                        fontSize = 10.sp,
                                        fontWeight = FontWeight.Bold,
                                        letterSpacing = 1.2.sp,
                                        color = EvaTeal
                                    )
                                    IconButton(
                                        onClick = { viewModel.clearLatestSpeech() },
                                        modifier = Modifier.size(24.dp)
                                    ) {
                                        Icon(
                                            imageVector = Icons.Default.Close,
                                            contentDescription = "Dismiss",
                                            tint = EvaTextMuted,
                                            modifier = Modifier.size(14.dp)
                                        )
                                    }
                                }

                                Text(
                                    text = state.latestSpeech,
                                    fontSize = 14.sp,
                                    lineHeight = 22.sp,
                                    color = EvaTextPure
                                )
                            }
                        }
                    }
                }

                // 3. Command Instrument Bar
                EvaCommandField(
                    value = inputText,
                    onValueChange = { inputText = it },
                    onSend = {
                        if (inputText.isNotBlank()) {
                            viewModel.sendTextMessage(inputText)
                            inputText = ""
                        }
                    },
                    isListening = state.assistantState == AssistantState.LISTENING,
                    onToggleVoice = { viewModel.onTalkButtonClicked() },
                    modifier = Modifier.fillMaxWidth()
                )
            }

            // 4. Approval Confirmation Modal
            state.pendingConfirmation?.let { conf ->
                ModalBottomSheet(
                    onDismissRequest = { viewModel.cancelPendingAction() },
                    containerColor = EvaNight,
                    tonalElevation = 8.dp
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(24.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Text(
                            text = "ACTION APPROVAL",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            letterSpacing = 1.2.sp,
                            color = EvaGold
                        )

                        Text(
                            text = conf.text,
                            fontSize = 15.sp,
                            fontWeight = FontWeight.Medium,
                            color = EvaTextPure,
                            lineHeight = 22.sp
                        )

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            OutlinedButton(
                                onClick = { viewModel.cancelPendingAction() },
                                shape = RoundedCornerShape(12.dp),
                                modifier = Modifier.weight(1f)
                            ) {
                                Text(text = "Dismiss", color = EvaTextSecondary)
                            }

                            Button(
                                onClick = { viewModel.confirmPendingAction() },
                                shape = RoundedCornerShape(12.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = EvaTeal),
                                modifier = Modifier.weight(1f)
                            ) {
                                Text(text = "Approve", color = EvaVoid, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }
            }
        }
    }
}
