package com.smartglasses.ai.presentation.activity

import androidx.compose.foundation.Canvas
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
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.presentation.home.WearableHomeViewModel
import com.smartglasses.ai.presentation.theme.*

data class ActivityTimelineItem(
    val time: String,
    val title: String,
    val detail: String,
    val category: String,
    val icon: ImageVector
)

/**
 * ActivityScreen: Matches Screen 3 (Activity & Insights) from the reference design.
 * Features category filter pills, vertical connected timeline entries, and the Usage & Insights chart card.
 */
@Composable
fun ActivityScreen(
    viewModel: WearableHomeViewModel,
    onNavigateToHome: () -> Unit = {}
) {
    val state by viewModel.uiState.collectAsState()
    var selectedFilter by remember { mutableStateOf("All") }

    val filterCategories = listOf("All", "Voice", "Vision", "Context", "System")

    // Default timeline records matching the reference design + dynamic session additions
    val timelineEvents = remember(state.messages, selectedFilter) {
        val baseList = mutableListOf(
            ActivityTimelineItem("09:12", "Voice session", "Asked about \"robotics research\"", "Voice", Icons.Default.Mic),
            ActivityTimelineItem("09:08", "Document opened", "Robotics architecture.pdf", "Context", Icons.Default.Description),
            ActivityTimelineItem("08:54", "Location captured", "University area", "Context", Icons.Default.LocationOn),
            ActivityTimelineItem("08:41", "Camera query", "Identified building · Confidence 92%", "Vision", Icons.Default.CameraAlt),
            ActivityTimelineItem("08:32", "System update", "EVA synced with your phone", "System", Icons.Default.Sync)
        )

        // Inject live user conversation if available
        state.messages.filter { it.sender == "USER" }.forEach { msg ->
            baseList.add(
                0,
                ActivityTimelineItem(
                    time = state.currentTime,
                    title = "Voice query",
                    detail = msg.text,
                    category = "Voice",
                    icon = Icons.Default.Mic
                )
            )
        }

        if (selectedFilter == "All") baseList
        else baseList.filter { it.category.equals(selectedFilter, ignoreCase = true) }
    }

    Scaffold(
        containerColor = EvaIvory
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 22.dp, vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // =============================================================
            // 1. TOP BAR: BACK ARROW + TITLE + CALENDAR + MORE
            // =============================================================
            item {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 6.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = "Back",
                        tint = EvaPrimaryBlack,
                        modifier = Modifier
                            .size(22.dp)
                            .clickable { onNavigateToHome() }
                    )

                    Text(
                        text = "Activity",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = EvaPrimaryBlack
                    )

                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(14.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.CalendarToday,
                            contentDescription = "Calendar",
                            tint = EvaPrimaryBlack,
                            modifier = Modifier.size(20.dp)
                        )
                        Icon(
                            imageVector = Icons.Default.MoreHoriz,
                            contentDescription = "Options",
                            tint = EvaPrimaryBlack,
                            modifier = Modifier.size(24.dp)
                        )
                    }
                }
            }

            // =============================================================
            // 2. FILTER PILLS: ALL, VOICE, VISION, CONTEXT, SYSTEM
            // =============================================================
            item {
                LazyRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    items(filterCategories) { category ->
                        val isSelected = selectedFilter == category
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(50))
                                .background(if (isSelected) EvaDeepGreen else EvaPureWhite)
                                .border(
                                    width = 1.dp,
                                    color = if (isSelected) EvaDeepGreen else EvaBorderSubtle,
                                    shape = RoundedCornerShape(50)
                                )
                                .clickable { selectedFilter = category }
                                .padding(horizontal = 16.dp, vertical = 8.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = category,
                                fontSize = 12.sp,
                                fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Medium,
                                color = if (isSelected) Color.White else EvaSoftBlack
                            )
                        }
                    }
                }
            }

            // =============================================================
            // 3. TIMELINE SECTION: TODAY
            // =============================================================
            item {
                Text(
                    text = "Today",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    color = EvaPrimaryBlack,
                    modifier = Modifier.padding(top = 4.dp, bottom = 2.dp)
                )
            }

            items(timelineEvents.size) { index ->
                val item = timelineEvents[index]
                val isLast = index == timelineEvents.size - 1

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.Top
                ) {
                    // Time
                    Text(
                        text = item.time,
                        fontSize = 11.sp,
                        fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                        color = EvaMutedText,
                        modifier = Modifier
                            .width(42.dp)
                            .padding(top = 2.dp)
                    )

                    // Vertical Connected Line & Icon Node
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        modifier = Modifier.width(28.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(24.dp)
                                .clip(CircleShape)
                                .background(EvaMistGreen)
                                .border(1.dp, EvaPaleGreen, CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = item.icon,
                                contentDescription = item.title,
                                tint = EvaPrimaryGreen,
                                modifier = Modifier.size(13.dp)
                            )
                        }

                        if (!isLast) {
                            Box(
                                modifier = Modifier
                                    .width(1.5.dp)
                                    .height(34.dp)
                                    .background(EvaBorderSubtle)
                            )
                        }
                    }

                    // Content
                    Column(
                        modifier = Modifier
                            .weight(1f)
                            .padding(bottom = if (!isLast) 12.dp else 0.dp),
                        verticalArrangement = Arrangement.spacedBy(2.dp)
                    ) {
                        Text(
                            text = item.title,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = EvaPrimaryBlack
                        )
                        Text(
                            text = item.detail,
                            fontSize = 12.sp,
                            color = EvaMutedText,
                            lineHeight = 16.sp
                        )
                    }
                }
            }

            // =============================================================
            // 4. USAGE & INSIGHTS CARD WITH SMOOTH WAVE CHART
            // =============================================================
            item {
                Spacer(modifier = Modifier.height(6.dp))
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(22.dp),
                    colors = CardDefaults.cardColors(containerColor = EvaPureWhite),
                    border = androidx.compose.foundation.BorderStroke(1.dp, EvaBorderSubtle)
                ) {
                    Column(
                        modifier = Modifier.padding(20.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        // Title + Dropdown
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "Usage & Insights",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold,
                                color = EvaPrimaryBlack
                            )

                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(4.dp)
                            ) {
                                Text(
                                    text = "Last 7 days",
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = EvaMutedText
                                )
                                Icon(
                                    imageVector = Icons.Default.KeyboardArrowDown,
                                    contentDescription = "Select",
                                    tint = EvaMutedText,
                                    modifier = Modifier.size(16.dp)
                                )
                            }
                        }

                        // 4 Metrics Grid
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            MetricColumn("23", "Voice sessions", "+15%")
                            MetricColumn("12", "Documents", "+8%")
                            MetricColumn("48", "Queries", "+22%")
                            MetricColumn("3.4h", "Active time", "+27%")
                        }

                        // Tooltip & Wave Chart Canvas
                        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            // Active Point Tooltip
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(horizontal = 40.dp),
                                contentAlignment = Alignment.Center
                            ) {
                                Box(
                                    modifier = Modifier
                                        .background(EvaPureWhite, RoundedCornerShape(8.dp))
                                        .border(1.dp, EvaBorderSubtle, RoundedCornerShape(8.dp))
                                        .padding(horizontal = 10.dp, vertical = 4.dp)
                                ) {
                                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                        Text(
                                            text = "1h 42m",
                                            fontSize = 12.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = EvaPrimaryBlack
                                        )
                                        Text(
                                            text = "Thu, 12 Oct",
                                            fontSize = 10.sp,
                                            color = EvaMutedText
                                        )
                                    }
                                }
                            }

                            // Smooth Wave Canvas
                            Canvas(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(90.dp)
                            ) {
                                val width = size.width
                                val height = size.height

                                val points = listOf(
                                    Offset(0f, height * 0.85f),
                                    Offset(width * 0.16f, height * 0.70f),
                                    Offset(width * 0.33f, height * 0.80f),
                                    Offset(width * 0.50f, height * 0.35f), // Peak
                                    Offset(width * 0.66f, height * 0.55f),
                                    Offset(width * 0.83f, height * 0.75f),
                                    Offset(width, height * 0.65f)
                                )

                                val path = Path().apply {
                                    moveTo(points[0].x, points[0].y)
                                    for (i in 1 until points.size) {
                                        val p0 = points[i - 1]
                                        val p1 = points[i]
                                        val cx = (p0.x + p1.x) / 2
                                        cubicTo(cx, p0.y, cx, p1.y, p1.x, p1.y)
                                    }
                                }

                                val fillPath = Path().apply {
                                    addPath(path)
                                    lineTo(width, height)
                                    lineTo(0f, height)
                                    close()
                                }

                                // Draw Gradient Fill
                                drawPath(
                                    path = fillPath,
                                    brush = Brush.verticalGradient(
                                        colors = listOf(
                                            EvaPrimaryGreen.copy(alpha = 0.25f),
                                            Color.Transparent
                                        )
                                    )
                                )

                                // Draw Wave Line
                                drawPath(
                                    path = path,
                                    color = EvaPrimaryGreen,
                                    style = Stroke(width = 2.5.dp.toPx())
                                )

                                // Draw Peak Circle Node
                                val peak = points[3]
                                drawCircle(
                                    color = EvaPrimaryGreen,
                                    radius = 5.dp.toPx(),
                                    center = peak
                                )
                                drawCircle(
                                    color = Color.White,
                                    radius = 2.5.dp.toPx(),
                                    center = peak
                                )
                            }

                            // Days Row
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                listOf("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun").forEach { day ->
                                    Text(
                                        text = day,
                                        fontSize = 10.sp,
                                        color = EvaMutedText,
                                        fontWeight = FontWeight.Medium
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun MetricColumn(
    value: String,
    label: String,
    delta: String
) {
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Text(
            text = value,
            fontSize = 16.sp,
            fontWeight = FontWeight.Bold,
            color = EvaPrimaryBlack
        )
        Text(
            text = label,
            fontSize = 10.sp,
            color = EvaMutedText
        )
        Text(
            text = delta,
            fontSize = 9.sp,
            fontWeight = FontWeight.SemiBold,
            color = EvaPrimaryGreen
        )
    }
}
