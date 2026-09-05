package com.smartglasses.ai.presentation.home

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.expandVertically
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.core.network.ConnectionState
import com.smartglasses.ai.core.network.NetworkDiagnostics
import com.smartglasses.ai.domain.models.AiAvailabilityState
import com.smartglasses.ai.domain.models.AssistantState
import com.smartglasses.ai.domain.models.ChatMessage
import com.smartglasses.ai.domain.models.IntegrationState
import com.smartglasses.ai.domain.models.ResponseSource
import com.smartglasses.ai.presentation.settings.BackendConfigDialog
import com.smartglasses.ai.presentation.theme.*

@Composable
fun WearableHomeScreen(
    viewModel: WearableHomeViewModel
) {
    val state by viewModel.uiState.collectAsState()
    var inlineUrlInput by remember(state.serverUrl) { mutableStateOf(state.serverUrl) }
    var testFeedback by remember { mutableStateOf<String?>(null) }
    var isTesting by remember { mutableStateOf(false) }

    if (state.isConfigDialogOpen) {
        BackendConfigDialog(
            currentUrl = state.serverUrl,
            onDismiss = { viewModel.closeConfigDialog() },
            onSaveUrl = { newUrl -> viewModel.updateServerUrl(newUrl) },
            onTestConnection = { testUrl, cb -> viewModel.testBackendConnection(testUrl, cb) }
        )
    }

    Scaffold(
        containerColor = LuxuryIvory
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 20.dp, vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // 1. Header Bar: SMART GLASSES AI + AI Status Indicator
            item {
                LuxuryHeaderBar(
                    aiState = state.aiAvailabilityState,
                    connectionState = state.connectionState,
                    onSettingsClicked = { viewModel.openConfigDialog() },
                    onDiagnosticsClicked = { viewModel.toggleDiagnostics() },
                    showDiagnostics = state.showDiagnostics
                )
            }

            // 2. Executive Main Assistant Section
            item {
                LuxuryAssistantMainSection(
                    period = state.period,
                    currentTime = state.currentTime,
                    locationName = if (state.locationAvailable) state.locationName else "Nagpur",
                    batteryPercent = state.batteryPercentage,
                    isCharging = state.isCharging,
                    assistantState = state.assistantState,
                    latestSpeech = state.latestSpeech,
                    partialTranscript = state.partialVoiceTranscript,
                    onTalkClicked = { viewModel.onTalkButtonClicked() }
                )
            }

            // 3. Pending Action Confirmation Dialog
            if (state.pendingConfirmation != null) {
                item {
                    LuxuryConfirmationDialogCard(
                        prompt = state.pendingConfirmation?.confirmationPrompt ?: "Please confirm this action.",
                        onConfirm = { viewModel.confirmPendingAction() },
                        onCancel = { viewModel.cancelPendingAction() }
                    )
                }
            }

            // 4. Conversation History Feed (Subtle, elegant bubbles)
            if (state.messages.isNotEmpty()) {
                item {
                    LuxuryConversationCard(
                        messages = state.messages,
                        lastLatencyMs = state.lastResponseLatencyMs
                    )
                }
            }

            // 5. Minimalist Text Input Bar
            item {
                LuxuryTextInputRow(
                    textInput = state.textInput,
                    isSending = state.isSendingText,
                    onTextChanged = { viewModel.onTextInputChanged(it) },
                    onSendClicked = { viewModel.sendTextMessage() }
                )
            }

            // 6. Connected Services (Google, Gmail, Calendar)
            item {
                LuxuryServicesCard(
                    connectionState = state.connectionState,
                    googleConnected = state.googleConnected,
                    gmailConnected = state.gmailStatus == IntegrationState.CONNECTED,
                    calendarConnected = state.calendarStatus == IntegrationState.CONNECTED,
                    onCheckGmail = { viewModel.checkGmail() },
                    onTodayEvents = { viewModel.fetchTodayEvents() },
                    onReadSms = { viewModel.readRecentSms() }
                )
            }

            // 7. Device Hardware Status (Microphone, TTS, Location, Glasses)
            item {
                LuxuryDeviceHardwareCard(
                    batteryPercent = state.batteryPercentage,
                    isCharging = state.isCharging,
                    locationName = if (state.locationAvailable) state.locationName else "Nagpur",
                    micReady = state.isMicrophoneReady,
                    ttsReady = state.isTtsReady,
                    glassesConnected = state.deviceConnectionState != com.smartglasses.ai.core.bluetooth.DeviceConnectionState.DISCONNECTED
                )
            }

            // 8. Developer Diagnostics (Discreet Accordion / Collapsed by default)
            item {
                LuxuryDiagnosticsAccordion(
                    isExpanded = state.showDiagnostics,
                    onToggle = { viewModel.toggleDiagnostics() },
                    diagnostics = state.networkDiagnostics,
                    activeRequestId = state.activeRequestId,
                    serverUrl = state.serverUrl,
                    activeProvider = state.activeAiProvider,
                    connectionState = state.connectionState,
                    ttfaMs = state.timeToFirstAudioMs,
                    sttMs = state.sttDurationMs,
                    ttsMs = state.ttsDurationMs
                )
            }

            // 9. Backend Gateway Configuration Card (Clean & Compact)
            item {
                LuxuryBackendConfigCard(
                    urlInput = inlineUrlInput,
                    onUrlChange = { inlineUrlInput = it },
                    isTesting = isTesting,
                    feedback = testFeedback,
                    onTestClick = {
                        isTesting = true
                        testFeedback = "Testing..."
                        viewModel.testBackendConnection(inlineUrlInput) { success, msg ->
                            isTesting = false
                            testFeedback = if (success) "Connected OK" else "Error: $msg"
                            if (success) {
                                viewModel.updateServerUrl(inlineUrlInput)
                            }
                        }
                    }
                )
            }
        }
    }
}

@Composable
fun LuxuryHeaderBar(
    aiState: AiAvailabilityState,
    connectionState: ConnectionState,
    onSettingsClicked: () -> Unit,
    onDiagnosticsClicked: () -> Unit,
    showDiagnostics: Boolean
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(
                text = "SMART GLASSES AI",
                style = MaterialTheme.typography.titleLarge,
                color = LuxuryEspresso,
                letterSpacing = 1.4.sp,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = "Personal AI Assistant",
                style = MaterialTheme.typography.labelSmall,
                color = LuxuryChampagneGold,
                letterSpacing = 0.8.sp,
                fontWeight = FontWeight.SemiBold
            )
        }

        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Subtle AI Availability Pill
            LuxuryAiStatusPill(aiState = aiState, connectionState = connectionState)

            // Diagnostics Toggle
            IconButton(
                onClick = onDiagnosticsClicked,
                modifier = Modifier
                    .size(36.dp)
                    .background(LuxuryWarmWhite, CircleShape)
                    .border(1.dp, if (showDiagnostics) LuxuryChampagneGold else LuxuryBorder, CircleShape)
            ) {
                Icon(
                    imageVector = Icons.Default.Speed,
                    contentDescription = "Diagnostics",
                    tint = if (showDiagnostics) LuxuryChampagneGold else LuxuryTextLight,
                    modifier = Modifier.size(16.dp)
                )
            }

            // Settings Button
            IconButton(
                onClick = onSettingsClicked,
                modifier = Modifier
                    .size(36.dp)
                    .background(LuxuryWarmWhite, CircleShape)
                    .border(1.dp, LuxuryBorder, CircleShape)
            ) {
                Icon(
                    imageVector = Icons.Default.Tune,
                    contentDescription = "Settings",
                    tint = LuxuryEspresso,
                    modifier = Modifier.size(16.dp)
                )
            }
        }
    }
}

@Composable
fun LuxuryAiStatusPill(
    aiState: AiAvailabilityState,
    connectionState: ConnectionState
) {
    val (label, bg, fg) = when {
        connectionState == ConnectionState.DISCONNECTED ->
            Triple("OFFLINE MODE", LuxuryTerracottaBg, LuxuryTerracotta)
        aiState == AiAvailabilityState.USING_LOCAL_AI ->
            Triple("USING LOCAL AI", LuxuryGoldLight, LuxuryEspresso)
        aiState == AiAvailabilityState.LOCAL_ONLY ->
            Triple("LOCAL AI", LuxuryGoldLight, LuxuryEspresso)
        aiState == AiAvailabilityState.CLOUD_DEGRADED ->
            Triple("CLOUD DEGRADED", LuxuryGoldLight, LuxuryEspresso)
        else ->
            Triple("CLOUD", LuxurySageBg, LuxurySage)
    }

    Box(
        modifier = Modifier
            .background(bg, RoundedCornerShape(12.dp))
            .border(1.dp, fg.copy(alpha = 0.3f), RoundedCornerShape(12.dp))
            .padding(horizontal = 9.dp, vertical = 4.dp)
    ) {
        Text(
            text = label,
            color = fg,
            fontSize = 10.sp,
            fontWeight = FontWeight.Bold,
            letterSpacing = 0.6.sp
        )
    }
}

@Composable
fun LuxuryAssistantMainSection(
    period: String,
    currentTime: String,
    locationName: String,
    batteryPercent: Int,
    isCharging: Boolean,
    assistantState: AssistantState,
    latestSpeech: String,
    partialTranscript: String,
    onTalkClicked: () -> Unit
) {
    Card(
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = LuxuryWarmWhite),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, LuxuryBorder, RoundedCornerShape(16.dp))
    ) {
        Column(
            modifier = Modifier.padding(22.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Executive Greeting
            val greetingWord = when (period.lowercase()) {
                "morning" -> "Good morning."
                "afternoon" -> "Good afternoon."
                "evening" -> "Good evening."
                else -> "Good evening."
            }

            Column {
                Text(
                    text = greetingWord,
                    style = MaterialTheme.typography.headlineMedium,
                    color = LuxuryEspresso,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = "How may I assist?",
                    style = MaterialTheme.typography.bodyLarge,
                    color = LuxuryTextMuted
                )
            }

            // Integrated Concise Context Line: 12:42 PM · Nagpur · Battery 84%
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(LuxurySurfaceSubtle, RoundedCornerShape(8.dp))
                    .padding(horizontal = 14.dp, vertical = 9.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.Schedule,
                        contentDescription = "Time",
                        tint = LuxuryChampagneGold,
                        modifier = Modifier.size(13.dp)
                    )
                    Text(
                        text = currentTime,
                        color = LuxuryCharcoal,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                }

                Text(text = "·", color = LuxuryBorder)

                Row(
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.LocationOn,
                        contentDescription = "Location",
                        tint = LuxuryChampagneGold,
                        modifier = Modifier.size(13.dp)
                    )
                    Text(
                        text = locationName,
                        color = LuxuryCharcoal,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Medium
                    )
                }

                Text(text = "·", color = LuxuryBorder)

                Row(
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = if (isCharging) Icons.Default.BatteryChargingFull else Icons.Default.BatteryFull,
                        contentDescription = "Battery",
                        tint = LuxurySage,
                        modifier = Modifier.size(13.dp)
                    )
                    Text(
                        text = "$batteryPercent%",
                        color = LuxuryCharcoal,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }

            // Spoken Preview / Partial Transcription
            if (partialTranscript.isNotBlank() || (latestSpeech.isNotBlank() && latestSpeech != "Ready on your smart glasses. Tap TALK or type below.")) {
                val previewText = if (partialTranscript.isNotBlank()) partialTranscript else latestSpeech
                Text(
                    text = "\"$previewText\"",
                    color = LuxuryTextMuted,
                    fontSize = 13.sp,
                    fontStyle = FontStyle.Italic,
                    lineHeight = 18.sp
                )
            }

            // Primary Tactile TALK Control
            val (buttonLabel, buttonColor, textColor) = when (assistantState) {
                AssistantState.IDLE -> Triple("TALK", LuxuryGoldLight, LuxuryEspresso)
                AssistantState.LISTENING -> Triple("LISTENING...", LuxuryChampagneGold, LuxuryWarmWhite)
                AssistantState.PROCESSING, AssistantState.RESPONDING -> Triple("THINKING...", LuxurySurfaceSubtle, LuxuryEspresso)
                AssistantState.SPEAKING -> Triple("SPEAKING...", LuxuryEspresso, LuxuryWarmWhite)
                AssistantState.ERROR -> Triple("RETRY", LuxuryTerracottaBg, LuxuryTerracotta)
            }

            Button(
                onClick = onTalkClicked,
                colors = ButtonDefaults.buttonColors(containerColor = buttonColor),
                shape = RoundedCornerShape(10.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp)
                    .border(1.dp, LuxuryChampagneGold, RoundedCornerShape(10.dp))
            ) {
                Icon(
                    imageVector = Icons.Default.Mic,
                    contentDescription = "Mic",
                    tint = textColor,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = buttonLabel,
                    color = textColor,
                    fontWeight = FontWeight.Bold,
                    fontSize = 13.sp,
                    letterSpacing = 1.2.sp
                )
            }
        }
    }
}

@Composable
fun LuxuryConfirmationDialogCard(
    prompt: String,
    onConfirm: () -> Unit,
    onCancel: () -> Unit
) {
    Card(
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = LuxuryWarmWhite),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, LuxuryChampagneGold, RoundedCornerShape(14.dp))
    ) {
        Column(
            modifier = Modifier.padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Default.Security,
                    contentDescription = "Security",
                    tint = LuxuryChampagneGold,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "ACTION CONFIRMATION",
                    style = MaterialTheme.typography.labelSmall,
                    color = LuxuryEspresso,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 0.8.sp
                )
            }

            Text(
                text = prompt,
                color = LuxuryCharcoal,
                fontSize = 14.sp,
                lineHeight = 20.sp
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.End,
                verticalAlignment = Alignment.CenterVertically
            ) {
                TextButton(onClick = onCancel) {
                    Text(text = "CANCEL", color = LuxuryTextMuted, fontWeight = FontWeight.SemiBold, fontSize = 12.sp)
                }
                Spacer(modifier = Modifier.width(8.dp))
                Button(
                    onClick = onConfirm,
                    colors = ButtonDefaults.buttonColors(containerColor = LuxuryEspresso),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(text = "CONFIRM", color = LuxuryWarmWhite, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                }
            }
        }
    }
}

@Composable
fun LuxuryConversationCard(
    messages: List<ChatMessage>,
    lastLatencyMs: Double?
) {
    Card(
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = LuxuryWarmWhite),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, LuxuryBorder, RoundedCornerShape(14.dp))
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Text(
                text = "CONVERSATION",
                style = MaterialTheme.typography.labelSmall,
                color = LuxuryTextLight,
                fontWeight = FontWeight.Bold,
                letterSpacing = 0.8.sp
            )

            messages.takeLast(4).forEach { msg ->
                val isUser = msg.sender.equals("USER", ignoreCase = true)
                val bubbleBg = if (isUser) LuxuryGoldLight else LuxurySurfaceSubtle
                val bubbleBorder = if (isUser) LuxuryChampagneGold.copy(alpha = 0.4f) else LuxuryBorder

                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .wrapContentWidth(if (isUser) Alignment.End else Alignment.Start)
                        .background(bubbleBg, RoundedCornerShape(10.dp))
                        .border(1.dp, bubbleBorder, RoundedCornerShape(10.dp))
                        .padding(horizontal = 12.dp, vertical = 8.dp)
                ) {
                    Row(
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = if (isUser) "You" else "Assistant",
                            color = if (isUser) LuxuryGoldHover else LuxuryEspresso,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold
                        )
                        if (!isUser && msg.source != null) {
                            Spacer(modifier = Modifier.width(8.dp))
                            val tag = when (msg.source) {
                                ResponseSource.LOCAL_DETERMINISTIC -> "Local"
                                ResponseSource.LOCAL_AI -> "Local AI"
                                ResponseSource.CLOUD_GEMINI -> "Gemini"
                                ResponseSource.CLOUD_SECONDARY -> "Secondary Cloud"
                                ResponseSource.TOOL -> "Tool"
                                ResponseSource.UNAVAILABLE -> "Unavailable"
                                ResponseSource.FALLBACK -> "Fallback"
                            }
                            Text(
                                text = tag,
                                color = LuxuryTextLight,
                                fontSize = 9.sp,
                                fontWeight = FontWeight.Medium
                            )
                        }
                    }
                    Text(
                        text = msg.text,
                        color = LuxuryCharcoal,
                        fontSize = 13.sp,
                        lineHeight = 18.sp
                    )
                }
            }

            if (lastLatencyMs != null && lastLatencyMs > 0) {
                Text(
                    text = "Response latency: ${lastLatencyMs.toInt()} ms",
                    color = LuxuryTextLight,
                    fontSize = 10.sp,
                    modifier = Modifier.align(Alignment.End)
                )
            }
        }
    }
}

@Composable
fun LuxuryTextInputRow(
    textInput: String,
    isSending: Boolean,
    onTextChanged: (String) -> Unit,
    onSendClicked: () -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        OutlinedTextField(
            value = textInput,
            onValueChange = onTextChanged,
            placeholder = { Text(text = "Ask a question...", color = LuxuryTextLight, fontSize = 13.sp) },
            singleLine = true,
            shape = RoundedCornerShape(10.dp),
            colors = OutlinedTextFieldDefaults.colors(
                focusedContainerColor = LuxuryWarmWhite,
                unfocusedContainerColor = LuxuryWarmWhite,
                focusedBorderColor = LuxuryChampagneGold,
                unfocusedBorderColor = LuxuryBorder,
                focusedTextColor = LuxuryCharcoal,
                unfocusedTextColor = LuxuryCharcoal
            ),
            modifier = Modifier.weight(1f)
        )

        Button(
            onClick = onSendClicked,
            enabled = textInput.isNotBlank() && !isSending,
            colors = ButtonDefaults.buttonColors(containerColor = LuxuryEspresso),
            shape = RoundedCornerShape(10.dp),
            modifier = Modifier.height(52.dp)
        ) {
            Text(text = "SEND", color = LuxuryWarmWhite, fontWeight = FontWeight.Bold, fontSize = 12.sp)
        }
    }
}

@Composable
fun LuxuryServicesCard(
    connectionState: ConnectionState,
    googleConnected: Boolean,
    gmailConnected: Boolean,
    calendarConnected: Boolean,
    onCheckGmail: () -> Unit,
    onTodayEvents: () -> Unit,
    onReadSms: () -> Unit
) {
    Card(
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = LuxuryWarmWhite),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, LuxuryBorder, RoundedCornerShape(14.dp))
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "CONNECTED SERVICES",
                style = MaterialTheme.typography.labelSmall,
                color = LuxuryTextLight,
                fontWeight = FontWeight.Bold,
                letterSpacing = 0.8.sp
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                LuxuryStatusBadge(label = "Backend", isOk = connectionState == ConnectionState.CONNECTED)
                LuxuryStatusBadge(label = "Google", isOk = googleConnected)
                LuxuryStatusBadge(label = "Gmail", isOk = gmailConnected)
                LuxuryStatusBadge(label = "Calendar", isOk = calendarConnected)
            }

            HorizontalDivider(color = LuxurySurfaceSubtle, thickness = 1.dp)

            // Quick Actions
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedButton(
                    onClick = onTodayEvents,
                    shape = RoundedCornerShape(8.dp),
                    border = ButtonDefaults.outlinedButtonBorder.copy(brush = androidx.compose.ui.graphics.SolidColor(LuxuryBorder)),
                    modifier = Modifier.weight(1f)
                ) {
                    Text(text = "Today", color = LuxuryEspresso, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
                }

                OutlinedButton(
                    onClick = onCheckGmail,
                    shape = RoundedCornerShape(8.dp),
                    border = ButtonDefaults.outlinedButtonBorder.copy(brush = androidx.compose.ui.graphics.SolidColor(LuxuryBorder)),
                    modifier = Modifier.weight(1f)
                ) {
                    Text(text = "Gmail", color = LuxuryEspresso, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
                }

                OutlinedButton(
                    onClick = onReadSms,
                    shape = RoundedCornerShape(8.dp),
                    border = ButtonDefaults.outlinedButtonBorder.copy(brush = androidx.compose.ui.graphics.SolidColor(LuxuryBorder)),
                    modifier = Modifier.weight(1f)
                ) {
                    Text(text = "SMS", color = LuxuryEspresso, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
                }
            }
        }
    }
}

@Composable
fun LuxuryStatusBadge(label: String, isOk: Boolean) {
    val bg = if (isOk) LuxurySageBg else LuxuryTerracottaBg
    val fg = if (isOk) LuxurySage else LuxuryTerracotta

    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(text = label, color = LuxuryTextMuted, fontSize = 11.sp)
        Spacer(modifier = Modifier.height(2.dp))
        Box(
            modifier = Modifier
                .background(bg, RoundedCornerShape(12.dp))
                .padding(horizontal = 8.dp, vertical = 2.dp)
        ) {
            Text(
                text = if (isOk) "Active" else "Off",
                color = fg,
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

@Composable
fun LuxuryDeviceHardwareCard(
    batteryPercent: Int,
    isCharging: Boolean,
    locationName: String,
    micReady: Boolean,
    ttsReady: Boolean,
    glassesConnected: Boolean
) {
    Card(
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = LuxuryWarmWhite),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, LuxuryBorder, RoundedCornerShape(14.dp))
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "DEVICE",
                style = MaterialTheme.typography.labelSmall,
                color = LuxuryTextLight,
                fontWeight = FontWeight.Bold,
                letterSpacing = 0.8.sp
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(text = "Glasses ESP32", color = LuxuryCharcoal, fontSize = 13.sp)
                Text(
                    text = if (glassesConnected) "Connected" else "Simulated",
                    color = if (glassesConnected) LuxurySage else LuxuryTextMuted,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.SemiBold
                )
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(text = "Battery", color = LuxuryCharcoal, fontSize = 13.sp)
                Text(
                    text = "$batteryPercent% ${if (isCharging) "(Charging)" else ""}",
                    color = LuxuryCharcoal,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.SemiBold
                )
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(text = "Microphone", color = LuxuryCharcoal, fontSize = 13.sp)
                Text(
                    text = if (micReady) "Ready" else "No Permission",
                    color = if (micReady) LuxurySage else LuxuryTerracotta,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.SemiBold
                )
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(text = "TTS Speaker", color = LuxuryCharcoal, fontSize = 13.sp)
                Text(
                    text = if (ttsReady) "Ready" else "Initializing",
                    color = if (ttsReady) LuxurySage else LuxuryTextMuted,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.SemiBold
                )
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(text = "Location", color = LuxuryCharcoal, fontSize = 13.sp)
                Text(
                    text = locationName,
                    color = LuxuryCharcoal,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Medium
                )
            }
        }
    }
}

@Composable
fun LuxuryDiagnosticsAccordion(
    isExpanded: Boolean,
    onToggle: () -> Unit,
    diagnostics: NetworkDiagnostics,
    activeRequestId: String?,
    serverUrl: String,
    activeProvider: String,
    connectionState: ConnectionState,
    ttfaMs: Long?,
    sttMs: Long?,
    ttsMs: Long?
) {
    val rotationAngle by animateFloatAsState(targetValue = if (isExpanded) 180f else 0f, label = "acc_arrow")

    Card(
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = LuxurySurfaceSubtle),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, LuxuryBorder, RoundedCornerShape(14.dp))
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onToggle() },
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "DEVELOPER DIAGNOSTICS",
                    style = MaterialTheme.typography.labelSmall,
                    color = LuxuryTextLight,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 0.8.sp
                )
                Icon(
                    imageVector = Icons.Default.ExpandMore,
                    contentDescription = "Expand",
                    tint = LuxuryTextLight,
                    modifier = Modifier.rotate(rotationAngle)
                )
            }

            AnimatedVisibility(
                visible = isExpanded,
                enter = expandVertically() + fadeIn(),
                exit = shrinkVertically() + fadeOut()
            ) {
                Column(
                    modifier = Modifier
                        .padding(top = 12.dp),
                    verticalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    Text(text = "Server Gateway: $serverUrl", color = LuxuryTextMuted, fontSize = 11.sp, fontFamily = FontFamily.Monospace)
                    Text(text = "Active AI Provider: $activeProvider", color = LuxuryEspresso, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                    Text(text = "Connection State: ${connectionState.name}", color = LuxuryTextMuted, fontSize = 11.sp)
                    if (sttMs != null) {
                        Text(text = "STT Latency: $sttMs ms", color = LuxuryTextMuted, fontSize = 11.sp)
                    }
                    if (ttfaMs != null) {
                        Text(text = "Time to First Audio (TTFA): $ttfaMs ms", color = LuxurySage, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                    if (ttsMs != null) {
                        Text(text = "TTS Duration: $ttsMs ms", color = LuxuryTextMuted, fontSize = 11.sp)
                    }
                    Text(text = "Last Latency: ${diagnostics.lastLatencyMs?.toInt() ?: 0} ms", color = LuxuryCharcoal, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                    Text(text = "Avg Latency: ${diagnostics.averageLatencyMs.toInt()} ms · P95: ${diagnostics.p95LatencyMs.toInt()} ms", color = LuxuryTextMuted, fontSize = 11.sp)
                    Text(text = "Total Requests: ${diagnostics.totalRequests} · Failed: ${diagnostics.failedRequests}", color = LuxuryTextMuted, fontSize = 11.sp)
                    Text(text = "Request ID: ${activeRequestId?.take(8) ?: "None"}", color = LuxuryTextMuted, fontSize = 10.sp, fontFamily = FontFamily.Monospace)
                }
            }
        }
    }
}

@Composable
fun LuxuryBackendConfigCard(
    urlInput: String,
    onUrlChange: (String) -> Unit,
    isTesting: Boolean,
    feedback: String?,
    onTestClick: () -> Unit
) {
    Card(
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = LuxuryWarmWhite),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, LuxuryBorder, RoundedCornerShape(14.dp))
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Text(
                text = "BACKEND GATEWAY CONFIGURATION",
                style = MaterialTheme.typography.labelSmall,
                color = LuxuryTextLight,
                fontWeight = FontWeight.Bold,
                letterSpacing = 0.8.sp
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                OutlinedTextField(
                    value = urlInput,
                    onValueChange = onUrlChange,
                    singleLine = true,
                    shape = RoundedCornerShape(8.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedContainerColor = LuxuryWarmWhite,
                        unfocusedContainerColor = LuxuryWarmWhite,
                        focusedBorderColor = LuxuryChampagneGold,
                        unfocusedBorderColor = LuxuryBorder,
                        focusedTextColor = LuxuryCharcoal,
                        unfocusedTextColor = LuxuryCharcoal
                    ),
                    modifier = Modifier.weight(1f)
                )

                Button(
                    onClick = onTestClick,
                    enabled = !isTesting,
                    colors = ButtonDefaults.buttonColors(containerColor = LuxuryGoldLight),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(
                        text = if (isTesting) "..." else "TEST",
                        color = LuxuryEspresso,
                        fontWeight = FontWeight.Bold,
                        fontSize = 11.sp
                    )
                }
            }

            if (feedback != null) {
                Text(
                    text = feedback,
                    color = if (feedback.contains("OK", ignoreCase = true)) LuxurySage else LuxuryTerracotta,
                    fontSize = 11.sp
                )
            }
        }
    }
}
