package com.smartglasses.ai.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.device.DeviceConnectionState

data class ChatMessage(val sender: String, val text: String)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GlassesMainScreen(
    connectionState: DeviceConnectionState,
    battery: Int,
    currentTime: String,
    currentLocation: String,
    messages: List<ChatMessage>,
    onTalkClicked: () -> Unit,
    onToggleConnection: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("SMART GLASSES AI", fontWeight = FontWeight.Bold) },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer
                )
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Status Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text("Connection: ${connectionState.name}", fontWeight = FontWeight.SemiBold)
                    Text("Battery: $battery%")
                    Text("Time: $currentTime | Location: $currentLocation")
                    Text("Backend: CONNECTED | Agent: READY", color = Color(0xFF2E7D32))
                }
            }

            // Conversation history
            Text("Conversation", fontWeight = FontWeight.Bold, fontSize = 18.sp)
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .background(MaterialTheme.colorScheme.background)
                    .padding(4.dp)
            ) {
                items(messages) { msg ->
                    Column(modifier = Modifier.padding(vertical = 4.dp)) {
                        Text(
                            text = "${msg.sender}:",
                            fontWeight = FontWeight.Bold,
                            color = if (msg.sender == "USER") MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.secondary
                        )
                        Text(text = msg.text, fontSize = 16.sp)
                    }
                }
            }

            // Action Buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Button(
                    onClick = onToggleConnection,
                    modifier = Modifier.weight(1f)
                ) {
                    Text("Switch Device Mode")
                }
                Button(
                    onClick = onTalkClicked,
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary)
                ) {
                    Text("TALK (Push-to-Talk)", fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}
