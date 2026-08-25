package com.smartglasses.ai.presentation.home

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.core.bluetooth.DeviceConnectionState
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
                    onSettingsClicked = { viewModel.openConfigDialog() }
                )
            }

            // 2. Status Badges Grid (Backend, LLM, Google, Gmail, Location)
            item {
                SystemStatusBadgesCard(
                    backendConnected = state.aiConnected,
                    llmConnected = state.llmConnected,
                    googleConnected = state.googleConnected,
                    gmailConnected = state.gmailStatus == IntegrationState.CONNECTED,
                    locationAvailable = state.locationAvailable,
                    locationName = state.locationName
                )
            }

            // 3. Assistant HUD & Conversation Area
            item {
                AssistantSectionCard(
                    assistantState = state.assistantState,
                    latestSpeech = state.latestSpeech,
                    partialTranscript = state.partialVoiceTranscript,
                    messages = state.messages
                )
            }

            // 4. Action Buttons ([ TALK ] and [ CHECK GMAIL ])
            item {
                ActionButtonsRow(
                    assistantState = state.assistantState,
                    onTalkClicked = { viewModel.onTalkButtonClicked() },
                    onCheckGmailClicked = { viewModel.checkGmail() }
                )
            }

            // 5. Backend URL Configuration Card
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
    onSettingsClicked: () -> Unit
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
                text = "WEARABLE CONTROLLER & COMPANION",
                style = MaterialTheme.typography.labelSmall,
                color = TextMuted,
                letterSpacing = 1.sp
            )
        }

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
                modifier = Modifier.size(20.dp)
            )
        }
    }
}

@Composable
fun SystemStatusBadgesCard(
    backendConnected: Boolean,
    llmConnected: Boolean,
    googleConnected: Boolean,
    gmailConnected: Boolean,
    locationAvailable: Boolean,
    locationName: String
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
                text = "SYSTEM STATUS",
                style = MaterialTheme.typography.labelSmall,
                color = TextMuted,
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = 1.sp
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                StatusIndicator(label = "Backend", isConnected = backendConnected)
                StatusIndicator(label = "LLM", isConnected = llmConnected)
                StatusIndicator(label = "Google", isConnected = googleConnected)
                StatusIndicator(label = "Gmail", isConnected = gmailConnected)
            }

            HorizontalDivider(color = WearableCardBorder.copy(alpha = 0.5f), thickness = 0.8.dp)

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.LocationOn,
                        contentDescription = "Location",
                        tint = CyanNeon,
                        modifier = Modifier.size(14.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "Location: $locationName",
                        color = TextSecondary,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Medium
                    )
                }

                StatusBadge(
                    text = if (locationAvailable) "AVAILABLE" else "OFFLINE",
                    isPositive = locationAvailable
                )
            }
        }
    }
}

@Composable
fun StatusIndicator(label: String, isConnected: Boolean) {
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
            text = "$label: ${if (isConnected) "CONNECTED" else "OFFLINE"}",
            color = if (isConnected) EmeraldNeon else TextMuted,
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
fun AssistantSectionCard(
    assistantState: AssistantState,
    latestSpeech: String,
    partialTranscript: String,
    messages: List<ChatMessage>
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
                    text = "ASSISTANT HUD",
                    style = MaterialTheme.typography.labelSmall,
                    color = CyanNeon,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 1.sp
                )

                StatusBadge(
                    text = assistantState.name,
                    isPositive = assistantState == AssistantState.SPEAKING || assistantState == AssistantState.IDLE
                )
            }

            // Live speech card
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
                        fontSize = 15.sp,
                        lineHeight = 20.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            }

            // Conversation history overview (last 2 items)
            if (messages.size > 1) {
                Text(
                    text = "RECENT CONVERSATION",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextMuted,
                    fontSize = 10.sp,
                    letterSpacing = 0.5.sp
                )

                messages.takeLast(2).forEach { msg ->
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = if (msg.sender == "USER") Arrangement.End else Arrangement.Start
                    ) {
                        Text(
                            text = "${msg.sender}: ${msg.text}",
                            color = if (msg.sender == "USER") CyanNeon.copy(alpha = 0.8f) else TextSecondary,
                            fontSize = 12.sp,
                            maxLines = 2
                        )
                    }
                }
            }
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
                    fontSize = 13.sp,
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
                text = "BACKEND SERVER URL (LAN / EMULATOR)",
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
                    textStyle = MaterialTheme.typography.bodyMedium.copy(fontSize = 13.sp)
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
