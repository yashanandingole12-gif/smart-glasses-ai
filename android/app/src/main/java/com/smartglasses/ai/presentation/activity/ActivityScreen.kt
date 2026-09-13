package com.smartglasses.ai.presentation.activity

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.presentation.home.WearableHomeViewModel
import com.smartglasses.ai.presentation.theme.*

data class ActivityItem(
    val time: String,
    val title: String,
    val detail: String? = null,
    val category: String = "Action",
    val isCompleted: Boolean = true
)

@Composable
fun ActivityScreen(
    viewModel: WearableHomeViewModel,
    onNavigateToHome: () -> Unit = {}
) {
    val state by viewModel.uiState.collectAsState()

    // Real dynamic activity list from user interactions & assistant responses
    val dynamicActivities = remember(state.messages) {
        val list = mutableListOf<ActivityItem>()
        state.messages.filter { it.sender == "USER" || it.sender == "ASSISTANT" }.forEach { msg ->
            if (msg.sender == "USER") {
                list.add(
                    ActivityItem(
                        time = state.currentTime,
                        title = "Asked LARA: \"${msg.text}\"",
                        detail = null,
                        category = "Query"
                    )
                )
            } else if (msg.sender == "ASSISTANT" && !msg.text.contains("Ready on your smart glasses")) {
                list.add(
                    ActivityItem(
                        time = state.currentTime,
                        title = "Response Received",
                        detail = if (msg.text.length > 120) msg.text.take(120) + "..." else msg.text,
                        category = "Intelligence"
                    )
                )
            }
        }
        list.reversed()
    }

    Scaffold(
        containerColor = LaraIvory
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 24.dp, vertical = 20.dp),
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            // Header
            item {
                Column(modifier = Modifier.padding(top = 8.dp)) {
                    Text(
                        text = "Activity",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        color = LaraTextPrimaryLight
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Real-time chronological record of your requests and executions.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = LaraTextSecondaryLight
                    )
                }
            }

            // Section: Current Session
            item {
                Text(
                    text = "CURRENT SESSION",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.SemiBold,
                    letterSpacing = 1.5.sp,
                    color = LaraMutedOrange
                )
            }

            if (dynamicActivities.isNotEmpty()) {
                items(dynamicActivities) { act ->
                    EditorialActivityRow(item = act)
                }
            } else {
                item {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        colors = CardDefaults.cardColors(containerColor = Color.White),
                        border = androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight)
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(24.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(
                                text = "No Activity Recorded",
                                fontSize = 15.sp,
                                fontWeight = FontWeight.Bold,
                                color = LaraTextPrimaryLight
                            )
                            Text(
                                text = "Your spoken commands, messages, and calls will appear here in chronological order.",
                                fontSize = 13.sp,
                                color = LaraTextSecondaryLight,
                                textAlign = androidx.compose.ui.text.style.TextAlign.Center,
                                lineHeight = 18.sp
                            )
                        }
                    }
                }
            }

            item {
                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }
}

@Composable
private fun EditorialActivityRow(item: ActivityItem) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.spacedBy(16.dp),
        verticalAlignment = Alignment.Top
    ) {
        Text(
            text = item.time,
            fontSize = 12.sp,
            fontWeight = FontWeight.Medium,
            color = LaraTextSecondaryLight,
            modifier = Modifier.width(68.dp)
        )

        Column(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(3.dp)
        ) {
            Text(
                text = item.title,
                fontSize = 14.sp,
                fontWeight = FontWeight.SemiBold,
                color = LaraTextPrimaryLight,
                lineHeight = 20.sp
            )
            if (!item.detail.isNullOrBlank()) {
                Text(
                    text = item.detail,
                    fontSize = 13.sp,
                    color = LaraTextSecondaryLight,
                    lineHeight = 18.sp
                )
            }
        }
    }
}
