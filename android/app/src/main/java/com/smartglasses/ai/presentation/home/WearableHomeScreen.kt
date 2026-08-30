package com.smartglasses.ai.presentation.home

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.*
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.core.network.ConnectionState
import com.smartglasses.ai.core.network.NetworkDiagnostics
import com.smartglasses.ai.domain.models.AssistantState
import com.smartglasses.ai.domain.models.ChatMessage
import com.smartglasses.ai.domain.models.IntegrationState
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
        containerColor = WearableDarkBackground
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            // 1. Header Bar: SMART GLASSES AI
            item {
                HeaderBar(
                    onSettingsClicked = { viewModel.openConfigDialog() },
                    onDiagnosticsClicked = { viewModel.toggleDiagnostics() },
                    showDiagnostics = state.showDiagnostics
                )
            }

            // 2. Developer Network Diagnostics Screen (Section 20)
            if (state.showDiagnostics) {
                item {
                    NetworkDiagnosticsCard(
                        diagnostics = state.networkDiagnostics,
                        activeRequestId = state.activeRequestId
                    )
                }
            }

            // 3. Real System Telemetry Card (4-State Connection Machine + Sensors)
            item {
                SystemTelemetryCard(
                    connectionState = state.connectionState,
                    geminiConnected = state.llmConnected,
                    googleConnected = state.googleConnected,
                    gmailConnected = state.gmailStatus == IntegrationState.CONNECTED,
                    micReady = state.isMicrophoneReady,
                    ttsReady = state.isTtsReady,
                    locationAvailable = state.locationAvailable,
                    locationName = state.locationName,
                    batteryPercent = state.batteryPercentage,
                    isCharging = state.isCharging
                )
            }

            // 4. Assistant HUD & Conversation Area
            item {
                AssistantSectionCard(
                    assistantState = state.assistantState,
                    latestSpeech = state.latestSpeech,
                    partialTranscript = state.partialVoiceTranscript,
                    messages = state.messages,
                    lastLatencyMs = state.lastResponseLatencyMs
                )
            }

            // 5. Text Assistant Input Row (for dev testing)
            item {
                TextAssistantInputRow(
                    textInput = state.textInput,
                    isSending = state.isSendingText,
                    onTextChanged = { viewModel.onTextInputChanged(it) },
                    onSendClicked = { viewModel.sendTextMessage() }
                )
            }

            // 6. Action Buttons ([ TALK ] and [ CHECK GMAIL ])
            item {
                ActionButtonsRow(
                    assistantState = state.assistantState,
                    onTalkClicked = { viewModel.onTalkButtonClicked() },
                    onCheckGmailClicked = { viewModel.checkGmail() }
                )
            }

            // 7. Backend URL Configuration Card
            item {
                BackendUrlConfigCard(
                    urlInput = inlineUrlInput,
                    onUrlChange = { inlineUrlInput = it },
                    isTesting = isTesting,
                    feedback = testFeedback,
                    onTestClick = {
                        isTesting = true
                        testFeedback = "Testing connection..."
                        viewModel.testBackendConnection(inlineUrlInput) { success, msg ->
                            isTesting = false
                            testFeedback = if (success) "Connected: OK" else "Error: $msg"
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
fun HeaderBar(
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
                style = MaterialTheme.typography.headlineMedium,
                color = CyanNeon,
                letterSpacing = 1.5.sp,
                fontWeight = FontWeight.Black
            )
            Text(
                text = "MOBILE WEARABLE COMPANION",
                style = MaterialTheme.typography.labelSmall,
                color = TextMuted,
                letterSpacing = 1.sp
            )
        }

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            // Diagnostics toggle button
            IconButton(
                onClick = onDiagnosticsClicked,
                modifier = Modifier
                    .size(40.dp)
                    .background(if (showDiagnostics) CyanNeon.copy(alpha = 0.2f) else WearableDarkSurface, CircleShape)
                    .border(1.dp, if (showDiagnostics) CyanNeon else WearableCardBorder, CircleShape)
            ) {
                Icon(
                    imageVector = Icons.Default.Speed,
                    contentDescription = "Diagnostics",
                    tint = if (showDiagnostics) CyanNeon else TextMuted,
                    modifier = Modifier.size(18.dp)
                )
            }

            // Settings button
            IconButton(
                onClick = onSettingsClicked,
                modifier = Modifier
                    .size(40.dp)
                    .background(WearableDarkSurface, CircleShape)
                    .border(1.dp, WearableCardBorder, CircleShape)
            ) {
                Icon(
                    imageVector = Icons.Default.Settings,
                    contentDescription = "Server Settings",
                    tint = CyanNeon,
                    modifier = Modifier.size(18.dp)
                )
            }
        }
    }
}

@Composable
fun NetworkDiagnosticsCard(
    diagnostics: NetworkDiagnostics,
    activeRequestId: String?
) {
    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = WearableDarkSurface),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, CyanNeon.copy(alpha = 0.6f), RoundedCornerShape(12.dp))
    ) {
        Column(
            modifier = Modifier.padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "NETWORK & LATENCY DIAGNOSTICS",
                    style = MaterialTheme.typography.labelSmall,
                    color = CyanNeon,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 1.sp
                )
                Text(
                    text = "REQ: ${activeRequestId?.take(8) ?: "N/A"}",
                    color = TextMuted,
                    fontSize = 9.sp,
                    fontFamily = FontFamily.Monospace
                )
            }

            HorizontalDivider(color = WearableCardBorder.copy(alpha = 0.5f), thickness = 0.8.dp)

            // Connection State & Endpoint
            Text(
                text = "Host: ${diagnostics.backendUrl}",
                color = TextSecondary,
                fontSize = 11.sp,
                fontFamily = FontFamily.Monospace
            )

            // Latency Metrics Grid
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                MetricItem(label = "Last", value = "${diagnostics.lastLatencyMs?.toInt() ?: 0}ms")
                MetricItem(label = "Average", value = "${diagnostics.averageLatencyMs.toInt()}ms")
                MetricItem(label = "P95", value = "${diagnostics.p95LatencyMs.toInt()}ms")
                MetricItem(label = "Min", value = "${diagnostics.minLatencyMs.toInt()}ms")
                MetricItem(label = "Max", value = "${diagnostics.maxLatencyMs.toInt()}ms")
            }

            // Requests & Failure Counts
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "Total Requests: ${diagnostics.totalRequests}",
                    color = TextMuted,
                    fontSize = 10.sp
                )
                Text(
                    text = "Failures: ${diagnostics.failedRequests}",
                    color = if (diagnostics.failedRequests > 0) CrimsonNeon else EmeraldNeon,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Bold
                )
                if (diagnostics.lastSuccessfulRequestTime != null) {
                    Text(
                        text = "Last OK: ${diagnostics.lastSuccessfulRequestTime}",
                        color = EmeraldNeon,
                        fontSize = 10.sp
                    )
                }
            }

            if (diagnostics.lastFailureReason != null) {
                Text(
                    text = "Last Error: ${diagnostics.lastFailureReason}",
                    color = CrimsonNeon,
                    fontSize = 10.sp,
                    maxLines = 1
                )
            }
        }
    }
}

@Composable
fun MetricItem(label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(text = label, color = TextMuted, fontSize = 9.sp)
        Text(text = value, color = CyanNeon, fontSize = 11.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
    }
}

@Composable
fun SystemTelemetryCard(
    connectionState: ConnectionState,
    geminiConnected: Boolean,
    googleConnected: Boolean,
    gmailConnected: Boolean,
    micReady: Boolean,
    ttsReady: Boolean,
    locationAvailable: Boolean,
    locationName: String,
    batteryPercent: Int,
    isCharging: Boolean
) {
    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = WearableDarkSurface),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, WearableCardBorder, RoundedCornerShape(12.dp))
    ) {
        Column(
            modifier = Modifier.padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Text(
                text = "REAL SYSTEM STATUS",
                style = MaterialTheme.typography.labelSmall,
                color = TextMuted,
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = 1.sp
            )

            // Primary Cloud Services with 4-State Connection Machine
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                ConnectionStatusIndicator(state = connectionState)
                StatusIndicator(label = "Gemini", isConnected = geminiConnected)
                StatusIndicator(label = "Google", isConnected = googleConnected)
                StatusIndicator(label = "Gmail", isConnected = gmailConnected)
            }

            HorizontalDivider(color = WearableCardBorder.copy(alpha = 0.5f), thickness = 0.8.dp)

            // Device Hardware & Sensor Telemetry (Mic, TTS, Location, Battery)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Mic
                StatusIndicator(
                    label = "Mic",
                    isConnected = micReady,
                    connectedText = "READY",
                    disconnectedText = "PERMISSION"
                )

                // TTS
                StatusIndicator(
                    label = "TTS",
                    isConnected = ttsReady,
                    connectedText = "READY",
                    disconnectedText = "INIT"
                )

                // Battery (Real Android)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = if (isCharging) Icons.Default.BatteryChargingFull else Icons.Default.BatteryFull,
                        contentDescription = "Battery",
                        tint = if (batteryPercent > 20) EmeraldNeon else CrimsonNeon,
                        modifier = Modifier.size(14.dp)
                    )
                    Spacer(modifier = Modifier.width(3.dp))
                    Text(
                        text = "$batteryPercent%",
                        color = if (batteryPercent > 20) EmeraldNeon else CrimsonNeon,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold
                    )
                }

                // Location
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.LocationOn,
                        contentDescription = "Location",
                        tint = if (locationAvailable) CyanNeon else TextMuted,
                        modifier = Modifier.size(14.dp)
                    )
                    Spacer(modifier = Modifier.width(2.dp))
                    Text(
                        text = if (locationAvailable) locationName else "UNAVAILABLE",
                        color = if (locationAvailable) CyanNeon else TextMuted,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }
    }
}

@Composable
fun ConnectionStatusIndicator(state: ConnectionState) {
    val (color, text) = when (state) {
        ConnectionState.CONNECTED -> Pair(EmeraldNeon, "CONNECTED")
        ConnectionState.CONNECTING -> Pair(CyanNeon, "CONNECTING")
        ConnectionState.DEGRADED -> Pair(Color(0xFFFFA500), "DEGRADED")
        ConnectionState.DISCONNECTED -> Pair(CrimsonNeon, "DISCONNECTED")
    }

    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        Box(
            modifier = Modifier
                .size(7.dp)
                .background(color, CircleShape)
        )
        Text(
            text = "Backend: $text",
            color = color,
            fontSize = 10.sp,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
fun StatusIndicator(
    label: String,
    isConnected: Boolean,
    connectedText: String = "CONNECTED",
    disconnectedText: String = "DISCONNECTED"
) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        Box(
            modifier = Modifier
                .size(7.dp)
                .background(if (isConnected) EmeraldNeon else CrimsonNeon, CircleShape)
        )
        Text(
            text = "$label: ${if (isConnected) connectedText else disconnectedText}",
            color = if (isConnected) EmeraldNeon else TextMuted,
            fontSize = 10.sp,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
fun AssistantSectionCard(
    assistantState: AssistantState,
    latestSpeech: String,
    partialTranscript: String,
    messages: List<ChatMessage>,
    lastLatencyMs: Double?
) {
    Card(
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = WearableDarkSurface),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, WearableCardBorder, RoundedCornerShape(14.dp))
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "ASSISTANT CONVERSATION",
                    style = MaterialTheme.typography.labelSmall,
                    color = CyanNeon,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 1.sp
                )

                Row(horizontalArrangement = Arrangement.spacedBy(6.dp), verticalAlignment = Alignment.CenterVertically) {
                    if (lastLatencyMs != null && lastLatencyMs > 0.0) {
                        Text(
                            text = "⏱️ ${lastLatencyMs.toInt()}ms",
                            color = TextMuted,
                            fontSize = 10.sp,
                            fontFamily = FontFamily.Monospace
                        )
                    }
                    StatusBadge(
                        text = assistantState.name,
                        isPositive = assistantState == AssistantState.SPEAKING || assistantState == AssistantState.IDLE
                    )
                }
            }

            // Live speech HUD card
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(WearableDarkBackground, RoundedCornerShape(10.dp))
                    .border(1.dp, WearableCardBorder.copy(alpha = 0.6f), RoundedCornerShape(10.dp))
                    .padding(14.dp)
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text(
                        text = if (partialTranscript.isNotBlank()) "Listening: \"$partialTranscript\"" else latestSpeech,
                        style = MaterialTheme.typography.bodyLarge,
                        color = if (partialTranscript.isNotBlank()) CyanNeon else TextPrimary,
                        fontSize = 14.sp,
                        lineHeight = 20.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            }

            // Message history (last 3 messages)
            if (messages.size > 1) {
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    messages.takeLast(3).forEach { msg ->
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = if (msg.sender == "USER") Arrangement.End else Arrangement.Start
                        ) {
                            Text(
                                text = "${msg.sender}: ${msg.text}",
                                color = if (msg.sender == "USER") CyanNeon.copy(alpha = 0.85f) else TextSecondary,
                                fontSize = 12.sp,
                                maxLines = 3
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun TextAssistantInputRow(
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
            placeholder = { Text("Type a query (e.g. 'What time is it?')", color = TextMuted, fontSize = 12.sp) },
            modifier = Modifier.weight(1f),
            singleLine = true,
            colors = OutlinedTextFieldDefaults.colors(
                focusedTextColor = TextPrimary,
                unfocusedTextColor = TextPrimary,
                focusedBorderColor = CyanNeon,
                unfocusedBorderColor = WearableCardBorder,
                focusedContainerColor = WearableDarkSurface,
                unfocusedContainerColor = WearableDarkSurface
            ),
            textStyle = MaterialTheme.typography.bodyMedium.copy(fontSize = 13.sp)
        )

        Button(
            onClick = onSendClicked,
            enabled = !isSending && textInput.isNotBlank(),
            shape = RoundedCornerShape(10.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = CyanNeon,
                contentColor = WearableDarkBackground
            ),
            modifier = Modifier.height(52.dp)
        ) {
            Text(
                text = if (isSending) "..." else "SEND",
                fontWeight = FontWeight.Bold,
                fontSize = 13.sp
            )
        }
    }
}

@Composable
fun ActionButtonsRow(
    assistantState: AssistantState,
    onTalkClicked: () -> Unit,
    onCheckGmailClicked: () -> Unit
) {
    val isListening = assistantState == AssistantState.LISTENING

    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        // Prominent TALK button
        Button(
            onClick = onTalkClicked,
            shape = RoundedCornerShape(12.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = if (isListening) CrimsonNeon else CyanNeon,
                contentColor = WearableDarkBackground
            ),
            modifier = Modifier
                .weight(1.3f)
                .height(52.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center
            ) {
                Icon(
                    imageVector = if (isListening) Icons.Default.Stop else Icons.Default.Mic,
                    contentDescription = "Talk",
                    tint = WearableDarkBackground,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = if (isListening) "STOP" else "TALK",
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Black,
                    letterSpacing = 1.sp
                )
            }
        }

        // CHECK GMAIL Button
        Button(
            onClick = onCheckGmailClicked,
            shape = RoundedCornerShape(12.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = WearableDarkSurface,
                contentColor = CyanNeon
            ),
            modifier = Modifier
                .weight(1.3f)
                .height(52.dp)
                .border(1.dp, CyanNeon.copy(alpha = 0.6f), RoundedCornerShape(12.dp))
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center
            ) {
                Icon(
                    imageVector = Icons.Default.Email,
                    contentDescription = "Gmail",
                    tint = CyanNeon,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = "CHECK GMAIL",
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 0.5.sp
                )
            }
        }
    }
}

@Composable
fun BackendUrlConfigCard(
    urlInput: String,
    onUrlChange: (String) -> Unit,
    isTesting: Boolean,
    feedback: String?,
    onTestClick: () -> Unit
) {
    Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = WearableDarkSurface),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, WearableCardBorder, RoundedCornerShape(12.dp))
    ) {
        Column(
            modifier = Modifier.padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "BACKEND SERVER URL (WI-FI LAN / HOTSPOT)",
                style = MaterialTheme.typography.labelSmall,
                color = TextMuted,
                fontSize = 10.sp,
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
                    modifier = Modifier.weight(1f),
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = TextPrimary,
                        unfocusedTextColor = TextPrimary,
                        focusedBorderColor = CyanNeon,
                        unfocusedBorderColor = WearableCardBorder,
                        focusedContainerColor = WearableDarkBackground,
                        unfocusedContainerColor = WearableDarkBackground
                    ),
                    textStyle = MaterialTheme.typography.bodyMedium.copy(fontSize = 12.sp)
                )

                Button(
                    onClick = onTestClick,
                    enabled = !isTesting,
                    shape = RoundedCornerShape(8.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = CyanNeon,
                        contentColor = WearableDarkBackground
                    ),
                    modifier = Modifier.height(48.dp)
                ) {
                    Text(
                        text = if (isTesting) "..." else "TEST",
                        fontWeight = FontWeight.Bold,
                        fontSize = 12.sp
                    )
                }
            }

            if (feedback != null) {
                Text(
                    text = feedback,
                    color = if (feedback.contains("OK") || feedback.contains("Connected")) EmeraldNeon else CrimsonNeon,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Medium
                )
            }
        }
    }
}

@Composable
fun StatusBadge(text: String, isPositive: Boolean) {
    val bgColor = if (isPositive) EmeraldNeon.copy(alpha = 0.15f) else TextMuted.copy(alpha = 0.15f)
    val textColor = if (isPositive) EmeraldNeon else TextSecondary

    Box(
        modifier = Modifier
            .background(bgColor, RoundedCornerShape(6.dp))
            .padding(horizontal = 8.dp, vertical = 3.dp)
    ) {
        Text(
            text = text,
            color = textColor,
            fontSize = 10.sp,
            fontWeight = FontWeight.Bold,
            letterSpacing = 0.5.sp
        )
    }
}
