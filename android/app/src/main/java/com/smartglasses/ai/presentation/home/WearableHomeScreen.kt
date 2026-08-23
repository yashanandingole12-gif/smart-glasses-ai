package com.smartglasses.ai.presentation.home

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.*
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
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 20.dp, vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Header Bar
            HeaderBar(
                onSettingsClicked = { viewModel.openConfigDialog() }
            )

            // Status Card (Glasses, Battery, AI, Location, Time)
            TelemetryStatusCard(
                glassesState = state.deviceConnectionState,
                battery = state.batteryPercentage,
                aiConnected = state.aiConnected,
                locationAvailable = state.locationAvailable,
                locationName = state.locationName,
                currentTime = state.currentTime,
                onToggleGlasses = { viewModel.toggleDeviceConnectionMode() }
            )

            // Center Wearable Assistant Card
            AssistantWearableCard(
                assistantState = state.assistantState,
                latestSpeech = state.latestSpeech,
                partialTranscript = state.partialVoiceTranscript,
                modifier = Modifier.weight(1f)
            )

            // TALK Push-to-Talk Button
            TalkButton(
                assistantState = state.assistantState,
                onTalkClicked = { viewModel.onTalkButtonClicked() }
            )

            // Integrations Card (Gmail, Calendar, SMS)
            IntegrationsCard(
                gmailState = state.gmailStatus,
                calendarState = state.calendarStatus,
                smsState = state.smsStatus
            )
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
                text = "CONTEXT AI",
                style = MaterialTheme.typography.headlineLarge,
                color = CyanNeon,
                letterSpacing = 2.sp,
                fontWeight = FontWeight.Black
            )
            Text(
                text = "SMART GLASSES CONTROLLER",
                style = MaterialTheme.typography.labelSmall,
                color = TextMuted
            )
        }

        IconButton(
            onClick = onSettingsClicked,
            modifier = Modifier
                .size(42.dp)
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
fun TelemetryStatusCard(
    glassesState: DeviceConnectionState,
    battery: Int,
    aiConnected: Boolean,
    locationAvailable: Boolean,
    locationName: String,
    currentTime: String,
    onToggleGlasses: () -> Unit
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
                StatusItem(
                    label = "Glasses",
                    value = when (glassesState) {
                        DeviceConnectionState.CONNECTED_ESP32 -> "CONNECTED (ESP32)"
                        DeviceConnectionState.CONNECTED_SIMULATED -> "CONNECTED (SIM)"
                        DeviceConnectionState.CONNECTING -> "CONNECTING"
                        DeviceConnectionState.DISCONNECTED -> "DISCONNECTED"
                    },
                    statusColor = if (glassesState != DeviceConnectionState.DISCONNECTED) EmeraldNeon else CrimsonNeon,
                    modifier = Modifier.clickable { onToggleGlasses() }
                )

                StatusItem(
                    label = "Battery",
                    value = "$battery%",
                    statusColor = if (battery > 20) EmeraldNeon else CrimsonNeon
                )
            }

            HorizontalDivider(color = WearableCardBorder.copy(alpha = 0.5f), thickness = 0.8.dp)

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                StatusItem(
                    label = "AI",
                    value = if (aiConnected) "CONNECTED" else "CONNECTING",
                    statusColor = if (aiConnected) EmeraldNeon else AmberNeon
                )

                StatusItem(
                    label = "Location",
                    value = if (locationAvailable) "AVAILABLE ($locationName)" else "UNAVAILABLE",
                    statusColor = if (locationAvailable) EmeraldNeon else AmberNeon
                )
            }

            HorizontalDivider(color = WearableCardBorder.copy(alpha = 0.5f), thickness = 0.8.dp)

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                StatusItem(
                    label = "Time",
                    value = currentTime,
                    statusColor = TextPrimary
                )

                StatusItem(
                    label = "Mode",
                    value = "MOBILE HUB",
                    statusColor = CyanNeon
                )
            }
        }
    }
}

@Composable
fun StatusItem(
    label: String,
    value: String,
    statusColor: Color,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) {
        Text(
            text = label.uppercase(),
            style = MaterialTheme.typography.labelSmall,
            color = TextMuted,
            fontSize = 10.sp
        )
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = statusColor,
            fontSize = 13.sp
        )
    }
}

@Composable
fun AssistantWearableCard(
    assistantState: AssistantState,
    latestSpeech: String,
    partialTranscript: String,
    modifier: Modifier = Modifier
) {
    Card(
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = WearableDarkSurface),
        modifier = modifier
            .fillMaxWidth()
            .border(
                1.dp,
                if (assistantState == AssistantState.LISTENING) CyanNeon else WearableCardBorder,
                RoundedCornerShape(16.dp)
            )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(18.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            // Assistant State Badge
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "ASSISTANT",
                    style = MaterialTheme.typography.labelSmall,
                    color = CyanNeon,
                    letterSpacing = 1.sp,
                    fontWeight = FontWeight.Bold
                )

                AssistantStateBadge(state = assistantState)
            }

            // Live Speech Display
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 8.dp),
                verticalArrangement = Arrangement.Center
            ) {
                if (assistantState == AssistantState.LISTENING && partialTranscript.isNotBlank()) {
                    Text(
                        text = "Listening: \"$partialTranscript\"",
                        style = MaterialTheme.typography.bodyLarge,
                        color = CyanNeon,
                        fontSize = 17.sp,
                        fontWeight = FontWeight.Medium
                    )
                } else {
                    Text(
                        text = "\"$latestSpeech\"",
                        style = MaterialTheme.typography.headlineMedium,
                        color = TextPrimary,
                        fontSize = 17.sp,
                        lineHeight = 24.sp,
                        fontWeight = FontWeight.Normal
                    )
                }
            }

            // Ambient Wearable Indicator
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.End,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Wearable Speech Audio Active",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextMuted,
                    fontSize = 10.sp
                )
            }
        }
    }
}

@Composable
fun AssistantStateBadge(state: AssistantState) {
    val (bgColor, textColor, text) = when (state) {
        AssistantState.IDLE -> Triple(WearableDarkSurfaceVariant, TextSecondary, "IDLE")
        AssistantState.LISTENING -> Triple(CyanNeon.copy(alpha = 0.2f), CyanNeon, "LISTENING")
        AssistantState.PROCESSING -> Triple(AmberNeon.copy(alpha = 0.2f), AmberNeon, "PROCESSING")
        AssistantState.SPEAKING -> Triple(EmeraldNeon.copy(alpha = 0.2f), EmeraldNeon, "SPEAKING")
        AssistantState.ERROR -> Triple(CrimsonNeon.copy(alpha = 0.2f), CrimsonNeon, "ERROR")
    }

    Box(
        modifier = Modifier
            .background(bgColor, RoundedCornerShape(8.dp))
            .padding(horizontal = 8.dp, vertical = 4.dp)
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

@Composable
fun TalkButton(
    assistantState: AssistantState,
    onTalkClicked: () -> Unit
) {
    val isListening = assistantState == AssistantState.LISTENING
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = if (isListening) 1.08f else 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(600, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse_scale"
    )

    Button(
        onClick = onTalkClicked,
        shape = RoundedCornerShape(16.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = if (isListening) CrimsonNeon else CyanNeon,
            contentColor = WearableDarkBackground
        ),
        modifier = Modifier
            .fillMaxWidth()
            .height(58.dp)
            .scale(pulseScale)
    ) {
        Row(
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth()
        ) {
            Icon(
                imageVector = if (isListening) Icons.Default.Stop else Icons.Default.Mic,
                contentDescription = "Talk",
                tint = WearableDarkBackground,
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.width(10.dp))
            Text(
                text = if (isListening) "STOP LISTENING" else "TALK",
                fontSize = 18.sp,
                fontWeight = FontWeight.Black,
                letterSpacing = 2.sp
            )
        }
    }
}

@Composable
fun IntegrationsCard(
    gmailState: IntegrationState,
    calendarState: IntegrationState,
    smsState: IntegrationState
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
            Text(
                text = "INTEGRATIONS",
                style = MaterialTheme.typography.labelSmall,
                color = TextMuted,
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = 1.sp
            )

            IntegrationRow(
                name = "Gmail",
                status = gmailState.name,
                statusColor = if (gmailState == IntegrationState.CONNECTED) EmeraldNeon else TextSecondary
            )

            HorizontalDivider(color = WearableCardBorder.copy(alpha = 0.5f), thickness = 0.8.dp)

            IntegrationRow(
                name = "Calendar",
                status = calendarState.name,
                statusColor = if (calendarState == IntegrationState.CONNECTED) EmeraldNeon else TextSecondary
            )

            HorizontalDivider(color = WearableCardBorder.copy(alpha = 0.5f), thickness = 0.8.dp)

            IntegrationRow(
                name = "SMS",
                status = smsState.name,
                statusColor = if (smsState == IntegrationState.READY) CyanNeon else TextSecondary
            )
        }
    }
}

@Composable
fun IntegrationRow(
    name: String,
    status: String,
    statusColor: Color
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = name,
            style = MaterialTheme.typography.bodyLarge,
            color = TextPrimary,
            fontWeight = FontWeight.Medium
        )
        Text(
            text = status,
            style = MaterialTheme.typography.labelSmall,
            color = statusColor,
            fontWeight = FontWeight.Bold,
            fontSize = 11.sp
        )
    }
}
