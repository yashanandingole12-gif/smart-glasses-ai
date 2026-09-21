package com.smartglasses.ai.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Bluetooth
import androidx.compose.material.icons.filled.Headphones
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.core.bluetooth.DeviceConnectionState
import com.smartglasses.ai.presentation.theme.*

/**
 * EvaDevicePresence renders the recognition status of the ESP32 Smart Glasses
 * and TWS earbud audio routing as a calm, integrated presence.
 */
@Composable
fun EvaDevicePresence(
    connectionState: DeviceConnectionState,
    onNavigateToDevices: () -> Unit,
    modifier: Modifier = Modifier
) {
    val isConnected = connectionState == DeviceConnectionState.CONNECTED_ESP32 ||
            connectionState == DeviceConnectionState.CONNECTED_SIMULATED

    Row(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(EvaSurfaceGlass)
            .border(1.dp, EvaBorderSubtle, RoundedCornerShape(16.dp))
            .clickable(onClick = onNavigateToDevices)
            .padding(horizontal = 16.dp, vertical = 12.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(36.dp)
                    .clip(CircleShape)
                    .background(if (isConnected) EvaTeal.copy(alpha = 0.15f) else EvaSurfaceElevated),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.Bluetooth,
                    contentDescription = "Glasses Presence",
                    tint = if (isConnected) EvaTeal else EvaTextMuted,
                    modifier = Modifier.size(18.dp)
                )
            }

            Column {
                Text(
                    text = if (isConnected) "EVA Glasses Active" else "EVA Glasses in Standby",
                    color = EvaTextPure,
                    fontSize = 13.sp
                )
                Text(
                    text = if (isConnected) "Input: 16kHz PCM Stream | Output: TWS" else "Tap to pair or manage perception",
                    color = EvaTextSecondary,
                    fontSize = 11.sp
                )
            }
        }

        // Live Recognition Dot
        Box(
            modifier = Modifier
                .size(8.dp)
                .clip(CircleShape)
                .background(if (isConnected) EvaEmerald else EvaSlate)
        )
    }
}
