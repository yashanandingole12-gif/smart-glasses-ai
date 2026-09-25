package com.smartglasses.ai.presentation.screens

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Public
import androidx.compose.material.icons.filled.Navigation
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
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
    val tagColor: Color,
    val lat: Double = 21.1458,
    val lon: Double = 79.0882
)

@Composable
fun GodEyeTransitScreen(
    onNavigateBack: () -> Unit = {},
    onQueryTransit: (String) -> Unit = {}
) {
    val context = LocalContext.current
    val transitItems = remember {
        listOf(
            TransitStatusItem(
                title = "Sitabuldi Interchange Metro Station",
                category = "MAHA METRO NAGPUR",
                primaryText = "0.5 km away (6 min walk)",
                secondaryText = "Orange Line: Khapri in 2 min (Plat 1) • Aqua Line: Lokmanya Nagar in 3 min (Plat 3)",
                statusTag = "LIVE SYNC",
                tagColor = EvaPrimaryGreen,
                lat = 21.1458,
                lon = 79.0832
            ),
            TransitStatusItem(
                title = "Wardha Road / Airport Corridor",
                category = "ROAD TRAFFIC (NAGPUR)",
                primaryText = "Smooth Flow along Wardha Flyover",
                secondaryText = "Avg Speed: 58 km/h • +0 min delay • Direct Airport Expressway",
                statusTag = "CLEAR",
                tagColor = EvaPrimaryGreen,
                lat = 21.1050,
                lon = 79.0620
            ),
            TransitStatusItem(
                title = "Nagpur - Bilaspur Vande Bharat (20826)",
                category = "INDIAN RAILWAYS (NGP)",
                primaryText = "Boarding on Platform 1, Nagpur Junction",
                secondaryText = "Departure: 14:05 • Stops: Gondia, Rajnandgaon, Durg, Raipur, Bilaspur",
                statusTag = "BOARDING",
                tagColor = EvaPrimaryGreen,
                lat = 21.1524,
                lon = 79.0889
            ),
            TransitStatusItem(
                title = "Samruddhi Mahamarg (Super Expressway)",
                category = "EXPRESSWAY RADAR",
                primaryText = "Zero Point Nagpur to Shirdi / Mumbai",
                secondaryText = "Speed: 115 km/h • High-speed smooth corridor • +0 min delay",
                statusTag = "FREE FLOW",
                tagColor = EvaPrimaryGreen,
                lat = 21.1350,
                lon = 79.0120
            ),
            TransitStatusItem(
                title = "IndiGo 6E-412 (NAG -> BOM)",
                category = "FLIGHT RADAR (NAG)",
                primaryText = "Dr. Babasaheb Ambedkar Airport (NAG), Gate 3",
                secondaryText = "Status: BOARDING • Departure: 08:35 • Baggage Carousel 2",
                statusTag = "ON TIME",
                tagColor = EvaPrimaryGreen,
                lat = 21.0922,
                lon = 79.0472
            )
        )
    }

    EvaAtmosphere(mode = EvaAtmosphereMode.GROUNDED) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 20.dp, vertical = 24.dp)
        ) {
            // Header with Back Button
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = "Back",
                        tint = EvaPrimaryBlack,
                        modifier = Modifier
                            .size(24.dp)
                            .clickable { onNavigateBack() }
                    )
                    Column {
                        Text(
                            text = "GOD'S EYE LIVE",
                            color = EvaPrimaryBlack,
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            letterSpacing = 2.sp
                        )
                        Text(
                            text = "Nagpur Spatial & Transit Radar",
                            color = EvaMutedText,
                            fontSize = 12.sp
                        )
                    }
                }

                Box(
                    modifier = Modifier
                        .background(EvaMistGreen, RoundedCornerShape(50))
                        .border(1.dp, EvaPaleGreen, RoundedCornerShape(50))
                        .padding(horizontal = 10.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = "ORBIT SYNC",
                        color = EvaDeepGreen,
                        fontSize = 10.sp,
                        fontFamily = FontFamily.Monospace,
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Google Live Earth 3D Action Card
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(
                        color = EvaDeepGreen,
                        shape = RoundedCornerShape(16.dp)
                    )
                    .padding(16.dp)
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Public,
                                contentDescription = "Google Earth 3D",
                                tint = Color.White,
                                modifier = Modifier.size(20.dp)
                            )
                            Text(
                                text = "Google Live Earth 3D Navigation",
                                color = Color.White,
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }

                    Text(
                        text = "Explore Nagpur & global terrain in real-time 3D photorealistic satellite view with smart glasses waypoint tracking.",
                        color = Color.White.copy(alpha = 0.85f),
                        fontSize = 11.sp,
                        lineHeight = 15.sp
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Button(
                            onClick = {
                                val url = "https://earth.google.com/web/@21.1458,79.0882,312a,950d,35y,0h,45t,0r"
                                val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                                context.startActivity(intent)
                            },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = EvaPureWhite,
                                contentColor = EvaDeepGreen
                            ),
                            shape = RoundedCornerShape(10.dp),
                            modifier = Modifier.weight(1f),
                            contentPadding = PaddingValues(vertical = 6.dp)
                        ) {
                            Text(text = "Open Earth 3D", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }

                        OutlinedButton(
                            onClick = {
                                val url = "https://www.google.com/maps/dir/?api=1&destination=21.1458,79.0882&travelmode=driving"
                                val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                                context.startActivity(intent)
                            },
                            colors = ButtonDefaults.outlinedButtonColors(
                                contentColor = Color.White
                            ),
                            border = androidx.compose.foundation.BorderStroke(1.dp, Color.White.copy(alpha = 0.5f)),
                            shape = RoundedCornerShape(10.dp),
                            modifier = Modifier.weight(1f),
                            contentPadding = PaddingValues(vertical = 6.dp)
                        ) {
                            Text(text = "Live GPS Nav", fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // Transit List
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(transitItems) { item ->
                    TransitCard(
                        item = item,
                        onOpenMap = {
                            val uri = Uri.parse("geo:${item.lat},${item.lon}?q=${item.lat},${item.lon}(${Uri.encode(item.title)})")
                            val intent = Intent(Intent.ACTION_VIEW, uri)
                            context.startActivity(intent)
                        }
                    )
                }
            }
        }
    }
}

@Composable
fun TransitCard(item: TransitStatusItem, onOpenMap: () -> Unit = {}) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .background(EvaPureWhite, RoundedCornerShape(14.dp))
            .border(1.dp, EvaBorderSubtle, RoundedCornerShape(14.dp))
            .clickable { onOpenMap() }
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
