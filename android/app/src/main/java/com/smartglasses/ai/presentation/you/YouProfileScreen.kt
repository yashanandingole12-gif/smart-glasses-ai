package com.smartglasses.ai.presentation.you

import android.content.Intent
import android.net.Uri
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.presentation.home.WearableHomeViewModel
import com.smartglasses.ai.presentation.theme.*

data class PermissionItem(
    val title: String,
    val purpose: String,
    val isGranted: Boolean = true,
    val icon: ImageVector
)

@Composable
fun YouProfileScreen(
    viewModel: WearableHomeViewModel,
    onOpenConfigDialog: () -> Unit = {}
) {
    val state by viewModel.uiState.collectAsState()
    var expandedCategory by remember { mutableStateOf<String?>("Communication") }

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
                        text = "You",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        color = LaraTextPrimaryLight
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Governance, device authority, background service & privacy.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = LaraTextSecondaryLight
                    )
                }
            }

            // Background & Pocket Operation Section
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    border = androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight)
                ) {
                    Column(
                        modifier = Modifier.padding(18.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Text(
                            text = "BACKGROUND & CONNECTIVITY",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold,
                            letterSpacing = 1.2.sp,
                            color = LaraMutedOrange
                        )

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(8.dp)
                                        .clip(CircleShape)
                                        .background(LaraEmerald)
                                )
                                Text(
                                    text = "LARA Background Service",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = LaraTextPrimaryLight
                                )
                            }
                            Text(
                                text = "Active",
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold,
                                color = LaraEmerald
                            )
                        }

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(8.dp)
                                        .clip(CircleShape)
                                        .background(LaraEmerald)
                                )
                                Text(
                                    text = "Smart Glasses Link",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = LaraTextPrimaryLight
                                )
                            }
                            Text(
                                text = "Connected",
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold,
                                color = LaraEmerald
                            )
                        }

                        Divider(color = LaraBorderLight, thickness = 0.5.dp)

                        Text(
                            text = "LARA can continue approved interactions when your screen is off or your phone is in your pocket, subject to Android system restrictions.",
                            fontSize = 12.sp,
                            color = LaraTextSecondaryLight,
                            lineHeight = 17.sp
                        )
                    }
                }
            }

            // Permissions by Category
            item {
                Text(
                    text = "PERMISSIONS & CAPABILITIES",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.SemiBold,
                    letterSpacing = 1.2.sp,
                    color = LaraMutedOrange
                )
            }

            // Communication Category
            item {
                PermissionCategoryCard(
                    categoryName = "Communication",
                    subtitle = "Calls, text messages & contact lookups",
                    isExpanded = expandedCategory == "Communication",
                    onToggle = { expandedCategory = if (expandedCategory == "Communication") null else "Communication" },
                    permissions = listOf(
                        PermissionItem("Phone Calls", "Placing authorized calls via hands-free or glasses.", true, Icons.Default.Phone),
                        PermissionItem("Messages", "Reading incoming SMS alerts & drafting replies.", true, Icons.Default.Message),
                        PermissionItem("Contacts", "Looking up phone numbers and contacts.", true, Icons.Default.Contacts)
                    )
                )
            }

            // Context Category
            item {
                PermissionCategoryCard(
                    categoryName = "Context",
                    subtitle = "Calendar schedule, location & notifications",
                    isExpanded = expandedCategory == "Context",
                    onToggle = { expandedCategory = if (expandedCategory == "Context") null else "Context" },
                    permissions = listOf(
                        PermissionItem("Calendar", "Daily schedules and upcoming agenda items.", true, Icons.Default.CalendarToday),
                        PermissionItem("Location", "Weather queries and localized contextual assistance.", state.locationAvailable, Icons.Default.LocationOn),
                        PermissionItem("Notifications", "Priority filtering of incoming notifications.", true, Icons.Default.Notifications)
                    )
                )
            }

            // Media Category
            item {
                PermissionCategoryCard(
                    categoryName = "Media & Wearable Hardware",
                    subtitle = "Camera capture, microphone & audio",
                    isExpanded = expandedCategory == "Media",
                    onToggle = { expandedCategory = if (expandedCategory == "Media") null else "Media" },
                    permissions = listOf(
                        PermissionItem("Smart Glasses Camera", "Analyzing scenes and scanning QR codes.", true, Icons.Default.CameraAlt),
                        PermissionItem("Digital Microphone", "Transcribing voice queries from glasses mic.", true, Icons.Default.Mic)
                    )
                )
            }

            // Documents Category
            item {
                PermissionCategoryCard(
                    categoryName = "Documents & Files",
                    subtitle = "Financial spreadsheets, legal PDFs & contracts",
                    isExpanded = expandedCategory == "Documents",
                    onToggle = { expandedCategory = if (expandedCategory == "Documents") null else "Documents" },
                    permissions = listOf(
                        PermissionItem("Files & Storage", "Document reasoning & bounded desk dataset analysis.", true, Icons.Default.Folder)
                    )
                )
            }

            // External Accounts & Integrations
            item {
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "INTEGRATIONS & ACCOUNTS",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.SemiBold,
                    letterSpacing = 1.2.sp,
                    color = LaraMutedOrange
                )
            }

            item {
                val context = LocalContext.current
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    border = androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight)
                ) {
                    Column(
                        modifier = Modifier.padding(18.dp),
                        verticalArrangement = Arrangement.spacedBy(14.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                                Text(
                                    text = "Google Workspace & Gmail",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = LaraTextPrimaryLight
                                )
                                Text(
                                    text = if (state.googleEmail != null) "Connected: ${state.googleEmail}" else "Not connected (Private OAuth)",
                                    fontSize = 12.sp,
                                    color = if (state.googleEmail != null) LaraEmerald else LaraTextSecondaryLight
                                )
                            }
                            Surface(
                                shape = RoundedCornerShape(4.dp),
                                color = if (state.googleEmail != null) LaraEmeraldBg else LaraIvory,
                                border = androidx.compose.foundation.BorderStroke(1.dp, if (state.googleEmail != null) LaraEmerald else LaraBorderLight)
                            ) {
                                Text(
                                    text = if (state.googleEmail != null) "Active" else "Required for Email",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = if (state.googleEmail != null) LaraEmerald else LaraTextSecondaryLight,
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                )
                            }
                        }

                        Button(
                            onClick = {
                                val baseUrl = if (state.serverUrl.endsWith("/")) state.serverUrl else "${state.serverUrl}/"
                                val authUrl = "${baseUrl}api/v1/auth/google"
                                try {
                                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(authUrl))
                                    context.startActivity(intent)
                                } catch (_: Exception) {}
                            },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = if (state.googleEmail != null) LaraGraphite else LaraCharcoal,
                                contentColor = LaraIvory
                            ),
                            shape = RoundedCornerShape(8.dp),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(
                                text = if (state.googleEmail != null) "Re-authenticate Google Account" else "Connect Google Account",
                                fontSize = 13.sp,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    }
                }
            }

            // Integrations & Server Settings
            item {
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "SYSTEM & SERVER",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.SemiBold,
                    letterSpacing = 1.2.sp,
                    color = LaraMutedOrange
                )
            }

            item {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onOpenConfigDialog() },
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    border = androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(18.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            Text(
                                text = "LARA Server Configuration",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = LaraTextPrimaryLight
                            )
                            Text(
                                text = state.serverUrl,
                                fontSize = 12.sp,
                                color = LaraTextSecondaryLight
                            )
                        }
                        Icon(
                            imageVector = Icons.Default.ChevronRight,
                            contentDescription = "Edit",
                            tint = LaraTextSecondaryLight
                        )
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
private fun PermissionCategoryCard(
    categoryName: String,
    subtitle: String,
    isExpanded: Boolean,
    onToggle: () -> Unit,
    permissions: List<PermissionItem>
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        border = androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onToggle() },
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    Text(
                        text = categoryName,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        color = LaraTextPrimaryLight
                    )
                    Text(
                        text = subtitle,
                        fontSize = 12.sp,
                        color = LaraTextSecondaryLight
                    )
                }
                Icon(
                    imageVector = if (isExpanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                    contentDescription = "Toggle",
                    tint = LaraTextSecondaryLight
                )
            }

            AnimatedVisibility(visible = isExpanded) {
                Column(
                    modifier = Modifier.padding(top = 14.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Divider(color = LaraBorderLight, thickness = 0.5.dp)
                    permissions.forEach { perm ->
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                modifier = Modifier.weight(1f),
                                horizontalArrangement = Arrangement.spacedBy(10.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = perm.icon,
                                    contentDescription = perm.title,
                                    tint = LaraMutedOrange,
                                    modifier = Modifier.size(18.dp)
                                )
                                Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                                    Text(
                                        text = perm.title,
                                        fontSize = 13.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        color = LaraTextPrimaryLight
                                    )
                                    Text(
                                        text = perm.purpose,
                                        fontSize = 11.sp,
                                        color = LaraTextSecondaryLight
                                    )
                                }
                            }
                            Surface(
                                shape = RoundedCornerShape(4.dp),
                                color = if (perm.isGranted) LaraEmeraldBg else LaraMutedRedBg,
                                modifier = Modifier.padding(start = 8.dp)
                            ) {
                                Text(
                                    text = if (perm.isGranted) "Authorized ✓" else "Not Granted",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = if (perm.isGranted) LaraEmerald else LaraMutedRed,
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
