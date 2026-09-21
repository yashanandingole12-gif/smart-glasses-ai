package com.smartglasses.ai.presentation.activity

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.presentation.home.WearableHomeViewModel
import com.smartglasses.ai.presentation.theme.*

data class ActivityItem(
    val id: String = "",
    val time: String,
    val title: String,
    val detail: String? = null,
    val category: String = "Action",
    val status: String = "SUCCESS",
    val icon: ImageVector = Icons.Default.CheckCircle
)

@Composable
fun ActivityScreen(
    viewModel: WearableHomeViewModel,
    onNavigateToHome: () -> Unit = {}
) {
    val state by viewModel.uiState.collectAsState()
    var selectedFilter by remember { mutableStateOf("All") }

    val filterCategories = listOf("All", "Research", "Documents", "Google", "Hardware")

    // Dynamic activities reconstructed from state messages and companion events
    val dynamicActivities = remember(state.messages, selectedFilter) {
        val list = mutableListOf<ActivityItem>()
        state.messages.filter { it.sender == "USER" || it.sender == "ASSISTANT" }.forEach { msg ->
            if (msg.sender == "USER") {
                val cat = when {
                    msg.text.contains("paper", ignoreCase = true) || msg.text.contains("research", ignoreCase = true) -> "Research"
                    msg.text.contains("doc", ignoreCase = true) || msg.text.contains("file", ignoreCase = true) -> "Documents"
                    msg.text.contains("mail", ignoreCase = true) || msg.text.contains("calendar", ignoreCase = true) -> "Google"
                    else -> "Action"
                }
                list.add(
                    ActivityItem(
                        time = state.currentTime,
                        title = "Spoken Query: \"${msg.text}\"",
                        detail = null,
                        category = cat,
                        icon = Icons.Default.Mic
                    )
                )
            } else if (msg.sender == "ASSISTANT" && !msg.text.contains("Ready on your smart glasses")) {
                list.add(
                    ActivityItem(
                        time = state.currentTime,
                        title = "Intelligence Synthesis Delivered",
                        detail = if (msg.text.length > 140) msg.text.take(140) + "..." else msg.text,
                        category = "Intelligence",
                        icon = Icons.Default.AutoAwesome
                    )
                )
            }
        }
        val reversed = list.reversed()
        if (selectedFilter == "All") reversed
        else reversed.filter { it.category.equals(selectedFilter, ignoreCase = true) }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(EvaVoid)
    ) {
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 20.dp, vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(18.dp)
        ) {
            // Header Title
            item {
                Column(modifier = Modifier.padding(top = 4.dp)) {
                    Text(
                        text = "Activity Timeline",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        color = EvaTextPure
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Chronological record of operational sessions, discoveries, and companion executions.",
                        style = MaterialTheme.typography.bodySmall,
                        color = EvaTextSecondary,
                        lineHeight = 16.sp
                    )
                }
            }

            // Active Session Card
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = EvaSurfaceVelvet),
                    border = androidx.compose.foundation.BorderStroke(1.dp, EvaBorderRadiant)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(18.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(6.dp)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(8.dp)
                                        .clip(CircleShape)
                                        .background(EvaEmerald)
                                )
                                Text(
                                    text = "ACTIVE SESSION",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold,
                                    letterSpacing = 1.sp,
                                    color = EvaEmerald
                                )
                            }
                            Text(
                                text = "${dynamicActivities.size} Actions",
                                fontSize = 11.sp,
                                color = EvaTextMuted
                            )
                        }

                        Text(
                            text = "02:00 – Present • Active Wearable Intelligence",
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Medium,
                            color = EvaTextPure
                        )
                    }
                }
            }

            // Filter Chips Row
            item {
                LazyRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(filterCategories) { cat ->
                        val isSelected = selectedFilter == cat
                        Surface(
                            shape = RoundedCornerShape(20.dp),
                            color = if (isSelected) EvaTealGlow else EvaSurfaceVelvet,
                            border = androidx.compose.foundation.BorderStroke(
                                1.dp,
                                if (isSelected) EvaTeal else EvaBorderSubtle
                            ),
                            modifier = Modifier.clickable { selectedFilter = cat }
                        ) {
                            Text(
                                text = cat,
                                fontSize = 12.sp,
                                fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal,
                                color = if (isSelected) EvaTeal else EvaTextSecondary,
                                modifier = Modifier.padding(horizontal = 14.dp, vertical = 6.dp)
                            )
                        }
                    }
                }
            }

            // Activities List
            if (dynamicActivities.isNotEmpty()) {
                items(dynamicActivities) { act ->
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(14.dp),
                        colors = CardDefaults.cardColors(containerColor = EvaNight),
                        border = androidx.compose.foundation.BorderStroke(1.dp, EvaBorderSubtle)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp),
                            horizontalArrangement = Arrangement.spacedBy(14.dp),
                            verticalAlignment = Alignment.Top
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(36.dp)
                                    .clip(RoundedCornerShape(10.dp))
                                    .background(EvaSurfaceVelvet)
                                    .border(1.dp, EvaBorderSubtle, RoundedCornerShape(10.dp)),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(
                                    imageVector = act.icon,
                                    contentDescription = null,
                                    tint = EvaCyan,
                                    modifier = Modifier.size(18.dp)
                                )
                            }

                            Column(
                                modifier = Modifier.weight(1f),
                                verticalArrangement = Arrangement.spacedBy(4.dp)
                            ) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = act.title,
                                        fontSize = 13.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        color = EvaTextPure,
                                        modifier = Modifier.weight(1f)
                                    )
                                    Text(
                                        text = act.time,
                                        fontSize = 11.sp,
                                        color = EvaTextMuted
                                    )
                                }

                                if (!act.detail.isNullOrBlank()) {
                                    Text(
                                        text = act.detail,
                                        fontSize = 12.sp,
                                        color = EvaTextSecondary,
                                        lineHeight = 16.sp
                                    )
                                }
                            }
                        }
                    }
                }
            } else {
                item {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(14.dp),
                        colors = CardDefaults.cardColors(containerColor = EvaNight),
                        border = androidx.compose.foundation.BorderStroke(1.dp, EvaBorderSubtle)
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(32.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(
                                text = "No Activity Recorded",
                                fontSize = 15.sp,
                                fontWeight = FontWeight.Bold,
                                color = EvaTextPure
                            )
                            Text(
                                text = "Your spoken commands, research queries, and document queries will appear here in chronological order.",
                                fontSize = 13.sp,
                                color = EvaTextSecondary,
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
