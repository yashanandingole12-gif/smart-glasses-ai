package com.smartglasses.ai.presentation.home

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.*
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.core.bluetooth.DeviceConnectionState
import com.smartglasses.ai.core.network.ConnectionState
import com.smartglasses.ai.domain.models.AssistantState
import com.smartglasses.ai.presentation.settings.BackendConfigDialog
import com.smartglasses.ai.presentation.theme.*

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

    val isGlassesConnected = state.deviceConnectionState == DeviceConnectionState.CONNECTED_ESP32 ||
            state.deviceConnectionState == DeviceConnectionState.CONNECTED_SIMULATED

    val isOnline = state.connectionState == ConnectionState.CONNECTED

    Scaffold(
        containerColor = LaraIvory
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 24.dp, vertical = 20.dp)
        ) {
            Column(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.SpaceBetween
            ) {
                // 1. Top Bar: LARA & Minimal Connection Status + Smart Glasses Pill
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "LARA",
                            fontFamily = FontFamily.Serif,
                            fontWeight = FontWeight.Bold,
                            fontSize = 22.sp,
                            letterSpacing = 2.sp,
                            color = LaraCharcoal
                        )

                        // Top minimal status indicator
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(7.dp)
                                    .clip(CircleShape)
                                    .background(if (isOnline) LaraEmerald else LaraTextSecondaryLight)
                            )
                            Text(
                                text = if (isOnline) "Connected" else "Offline",
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Medium,
                                color = if (isOnline) LaraEmerald else LaraTextSecondaryLight
                            )
                        }
                    }

                    // Compact Smart Glasses Indicator Pill
                    Surface(
                        shape = RoundedCornerShape(20.dp),
                        color = Color.White,
                        border = androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight),
                        modifier = Modifier
                            .clickable { onNavigateToDevices() }
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(6.dp)
                                    .clip(CircleShape)
                                    .background(if (isGlassesConnected) LaraEmerald else LaraMutedOrange)
                            )
                            Text(
                                text = if (isGlassesConnected) "Smart Glasses Connected" else "Smart Glasses Disconnected",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = LaraTextPrimaryLight
                            )
                        }
                    }
                }

                // 2. Center Hero: Negative Space & Subtle Breathing Waveform
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(20.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        // Subtle interaction breathing indicator
                        SubtleBreathingIndicator(
                            assistantState = state.assistantState,
                            onClick = { viewModel.onTalkButtonClicked() }
                        )

                        // Optional Response Card (Editorial and restrained)
                        AnimatedVisibility(
                            visible = state.latestSpeech.isNotBlank() &&
                                    !state.latestSpeech.contains("Ready on your smart glasses"),
                            enter = fadeIn(),
                            exit = fadeOut()
                        ) {
                            Card(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(horizontal = 4.dp),
                                shape = RoundedCornerShape(12.dp),
                                colors = CardDefaults.cardColors(containerColor = Color.White),
                                border = androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight)
                            ) {
                                Column(
                                    modifier = Modifier.padding(18.dp),
                                    verticalArrangement = Arrangement.spacedBy(10.dp)
                                ) {
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
                                            contentDescription = "Smart Glasses Camera Capture",
                                            modifier = Modifier
                                                .fillMaxWidth()
                                                .heightIn(max = 200.dp)
                                                .clip(RoundedCornerShape(8.dp)),
                                            contentScale = androidx.compose.ui.layout.ContentScale.Crop
                                        )
                                        Row(
                                            verticalAlignment = Alignment.CenterVertically,
                                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                                        ) {
                                            Box(
                                                modifier = Modifier
                                                    .size(6.dp)
                                                    .clip(CircleShape)
                                                    .background(LaraEmerald)
                                            )
                                            Text(
                                                text = "Smart Glasses Photo • Saved to Gallery",
                                                fontSize = 11.sp,
                                                fontWeight = FontWeight.SemiBold,
                                                color = LaraEmerald
                                            )
                                        }
                                    }

                                    Text(
                                        text = state.latestSpeech,
                                        fontSize = 14.sp,
                                        fontWeight = FontWeight.Medium,
                                        color = LaraTextPrimaryLight,
                                        lineHeight = 21.sp
                                    )
                                    Text(
                                        text = "Dismiss",
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = LaraMutedOrange,
                                        modifier = Modifier
                                            .align(Alignment.End)
                                            .clickable { viewModel.clearLatestSpeech() }
                                    )
                                }
                            }
                        }

                        // Partial voice transcript if speaking
                        if (state.partialVoiceTranscript.isNotBlank()) {
                            Text(
                                text = "\"${state.partialVoiceTranscript}\"",
                                fontSize = 13.sp,
                                fontStyle = androidx.compose.ui.text.font.FontStyle.Italic,
                                color = LaraTextSecondaryLight
                            )
                        }
                    }
                }

                // 3. Command Bar: Refined Input Field + Small Mic Control
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = Color.White,
                    border = androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 14.dp, vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        TextField(
                            value = inputText,
                            onValueChange = { inputText = it },
                            placeholder = {
                                Text(
                                    text = "Ask LARA anything...",
                                    fontSize = 14.sp,
                                    color = LaraTextSecondaryLight
                                )
                            },
                            colors = TextFieldDefaults.colors(
                                focusedContainerColor = Color.Transparent,
                                unfocusedContainerColor = Color.Transparent,
                                disabledContainerColor = Color.Transparent,
                                focusedIndicatorColor = Color.Transparent,
                                unfocusedIndicatorColor = Color.Transparent
                            ),
                            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                            keyboardActions = KeyboardActions(onSend = {
                                if (inputText.isNotBlank()) {
                                    viewModel.sendTextMessage(inputText)
                                    inputText = ""
                                }
                            }),
                            singleLine = true,
                            modifier = Modifier.weight(1f)
                        )

                        // Small Microphone Control
                        IconButton(
                            onClick = { viewModel.onTalkButtonClicked() },
                            modifier = Modifier
                                .size(36.dp)
                                .clip(CircleShape)
                                .background(
                                    if (state.assistantState == AssistantState.LISTENING) LaraMutedOrange
                                    else LaraIvory
                                )
                        ) {
                            Icon(
                                imageVector = Icons.Default.Mic,
                                contentDescription = "Voice Input",
                                tint = if (state.assistantState == AssistantState.LISTENING) Color.White else LaraCharcoal,
                                modifier = Modifier.size(18.dp)
                            )
                        }

                        // Send Button (if text entered)
                        if (inputText.isNotBlank()) {
                            IconButton(
                                onClick = {
                                    viewModel.sendTextMessage(inputText)
                                    inputText = ""
                                },
                                modifier = Modifier
                                    .size(36.dp)
                                    .clip(CircleShape)
                                    .background(LaraMutedOrange)
                            ) {
                                Icon(
                                    imageVector = Icons.Default.ArrowUpward,
                                    contentDescription = "Send",
                                    tint = Color.White,
                                    modifier = Modifier.size(18.dp)
                                )
                            }
                        }
                    }
                }
            }

            // 4. Contextual Confirmation Bottom Sheet
            state.pendingConfirmation?.let { conf ->
                ModalBottomSheet(
                    onDismissRequest = { viewModel.cancelPendingAction() },
                    containerColor = Color.White,
                    tonalElevation = 8.dp
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(24.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Text(
                            text = "APPROVAL REQUIRED",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            letterSpacing = 1.2.sp,
                            color = LaraMutedOrange
                        )

                        Text(
                            text = conf.text,
                            fontSize = 16.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = LaraTextPrimaryLight,
                            lineHeight = 22.sp
                        )

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            OutlinedButton(
                                onClick = { viewModel.cancelPendingAction() },
                                shape = RoundedCornerShape(8.dp),
                                modifier = Modifier.weight(1f)
                            ) {
                                Text(text = "Dismiss", color = LaraTextSecondaryLight)
                            }

                            Button(
                                onClick = { viewModel.confirmPendingAction() },
                                shape = RoundedCornerShape(8.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = LaraMutedOrange),
                                modifier = Modifier.weight(1f)
                            ) {
                                Text(text = "Approve", color = Color.White, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }
            }
        }
    }
}

/**
 * Subtle Breathing / Waveform interaction indicator.
 * Communicates Idle, Listening, Processing, and Responding with calm restraint.
 */
@Composable
private fun SubtleBreathingIndicator(
    assistantState: AssistantState,
    onClick: () -> Unit
) {
    val infiniteTransition = rememberInfiniteTransition(label = "breathing")

    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 1.0f,
        targetValue = if (assistantState == AssistantState.LISTENING) 1.25f else 1.05f,
        animationSpec = infiniteRepeatable(
            animation = tween(
                durationMillis = if (assistantState == AssistantState.LISTENING) 900 else 2400,
                easing = FastOutSlowInEasing
            ),
            repeatMode = RepeatMode.Reverse
        ),
        label = "scale"
    )

    val waveAlpha by infiniteTransition.animateFloat(
        initialValue = 0.2f,
        targetValue = if (assistantState == AssistantState.LISTENING) 0.7f else 0.35f,
        animationSpec = infiniteRepeatable(
            animation = tween(
                durationMillis = if (assistantState == AssistantState.LISTENING) 900 else 2400,
                easing = FastOutSlowInEasing
            ),
            repeatMode = RepeatMode.Reverse
        ),
        label = "alpha"
    )

    Box(
        modifier = Modifier
            .size(110.dp)
            .clickable { onClick() },
        contentAlignment = Alignment.Center
    ) {
        // Outer soft breathing ring
        Box(
            modifier = Modifier
                .size(90.dp)
                .graphicsLayer(scaleX = pulseScale, scaleY = pulseScale)
                .clip(CircleShape)
                .background(
                    when (assistantState) {
                        AssistantState.LISTENING -> LaraMutedOrange.copy(alpha = waveAlpha)
                        AssistantState.PROCESSING -> LaraEmerald.copy(alpha = waveAlpha)
                        else -> LaraBorderLight.copy(alpha = waveAlpha)
                    }
                )
        )

        // Center static core
        Box(
            modifier = Modifier
                .size(48.dp)
                .clip(CircleShape)
                .background(Color.White)
                .border(1.dp, LaraBorderLight, CircleShape),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = when (assistantState) {
                    AssistantState.LISTENING -> Icons.Default.GraphicEq
                    AssistantState.PROCESSING -> Icons.Default.Sync
                    AssistantState.SPEAKING -> Icons.Default.VolumeUp
                    else -> Icons.Default.Mic
                },
                contentDescription = "Interaction State",
                tint = when (assistantState) {
                    AssistantState.LISTENING -> LaraMutedOrange
                    AssistantState.PROCESSING -> LaraEmerald
                    else -> LaraTextSecondaryLight
                },
                modifier = Modifier.size(20.dp)
            )
        }
    }
}
