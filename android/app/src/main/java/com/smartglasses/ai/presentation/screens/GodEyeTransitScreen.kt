package com.smartglasses.ai.presentation.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.presentation.components.EvaAtmosphere
import com.smartglasses.ai.presentation.components.EvaAtmosphereMode
import com.smartglasses.ai.presentation.theme.*

data class TransitStatusItem(
    val title: String,
    val category: String,
    val primaryText: String,
    val secondaryText: String,
    val statusTag: String,
    val tagColor: Color
)

@Composable
fun GodEyeTransitScreen(
    onNavigateBack: () -> Unit = {},
    onQueryTransit: (String) -> Unit = {}
) {
    val transitItems = remember {
        listOf(
            TransitStatusItem(
                title = "Western Express Highway",
                category = "ROAD TRAFFIC",
                primaryText = "Heavy Traffic near Santacruz Flyover",
                secondaryText = "Avg Speed: 22 km/h • +18 min delay • Alt: Coastal Road Link",
                statusTag = "HEAVY (+18m)",
                tagColor = EvaStatusWarning
            ),
            TransitStatusItem(
                title = "Andheri Metro Station (Line 1)",
                category = "METRO NETWORK",
                primaryText = "0.4 km away (5 min walk)",
                secondaryText = "Next to Ghatkopar: 2 min (Platform 1) • Versova: 4 min (Platform 2)",
                statusTag = "LIVE SYNC",
                tagColor = EvaPrimaryGreen
            ),
            TransitStatusItem(
                title = "Churchgate Fast Local",
                category = "SUBURBAN TRAIN",
                primaryText = "Arriving on Platform 4 in 3 min",
                secondaryText = "Stops: Andheri, Bandra, Dadar, Mumbai Central, Churchgate",
                statusTag = "ON TIME",
                tagColor = EvaPrimaryGreen
            ),
            TransitStatusItem(
                title = "IndiGo Flight 6E-204 (DEL)",
                category = "FLIGHT RADAR",
                primaryText = "Terminal 2, Gate 48B",
                secondaryText = "Status: BOARDING • Departure: 14:35 • Carousel 5 (Arrival)",
                statusTag = "BOARDING",
                tagColor = EvaPrimaryGreen
            )
        )
    }

    EvaAtmosphere(mode = EvaAtmosphereMode.GROUNDED) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 20.dp, vertical = 24.dp)
        ) {
            // Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "GOD'S EYE LIVE",
                        color = EvaPrimaryBlack,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 2.sp
                    )
                    Text(
                        text = "Real-Time Spatial & Transit Telemetry",
                        color = EvaMutedText,
                        fontSize = 12.sp
                    )
                }

                Box(
                    modifier = Modifier
                        .background(EvaMistGreen, RoundedCornerShape(50))
                        .border(1.dp, EvaPaleGreen, RoundedCornerShape(50))
                        .padding(horizontal = 10.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = "GLASSES SYNC",
                        color = EvaDeepGreen,
                        fontSize = 10.sp,
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // Transit List
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                items(transitItems) { item ->
                    TransitCard(item = item)
                }
            }
        }
    }
}

@Composable
fun TransitCard(item: TransitStatusItem) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .background(EvaPureWhite, RoundedCornerShape(14.dp))
            .border(1.dp, EvaBorderSubtle, RoundedCornerShape(14.dp))
            .padding(16.dp)
    ) {
        Column {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = item.category,
                    color = EvaMutedText,
                    fontSize = 10.sp,
                    fontFamily = FontFamily.Monospace,
                    letterSpacing = 1.sp
                )
                Box(
                    modifier = Modifier
                        .background(item.tagColor.copy(alpha = 0.12f), RoundedCornerShape(4.dp))
                        .border(1.dp, item.tagColor.copy(alpha = 0.35f), RoundedCornerShape(4.dp))
                        .padding(horizontal = 6.dp, vertical = 2.dp)
                ) {
                    Text(
                        text = item.statusTag,
                        color = item.tagColor,
                        fontSize = 10.sp,
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            Spacer(modifier = Modifier.height(6.dp))

            Text(
                text = item.title,
                color = EvaPrimaryBlack,
                fontSize = 15.sp,
                fontWeight = FontWeight.SemiBold
            )

            Text(
                text = item.primaryText,
                color = EvaPrimaryBlack,
                fontSize = 13.sp,
                modifier = Modifier.padding(top = 2.dp)
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = item.secondaryText,
                color = EvaMutedText,
                fontSize = 11.sp,
                fontFamily = FontFamily.Monospace,
                lineHeight = 16.sp
            )
        }
    }
}
