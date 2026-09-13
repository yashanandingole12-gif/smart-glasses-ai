package com.smartglasses.ai.presentation.intelligence

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.presentation.home.WearableHomeViewModel
import com.smartglasses.ai.presentation.theme.*

/**
 * LARA Desk Analysis & Document Intelligence Workspace:
 * - Tabular data analysis (CSV, XLSX, PDF tables)
 * - Contract & document reasoning
 * - Structured summaries & anomaly extraction
 */
@Composable
fun IntelligenceScreen(
    viewModel: WearableHomeViewModel,
    onNavigateToCommand: () -> Unit = {}
) {
    var selectedDataset by remember { mutableStateOf("Quarterly_Financials.xlsx") }
    var activeOperation by remember { mutableStateOf<String?>(null) }
    var analysisResult by remember { mutableStateOf<String?>(null) }

    Scaffold(
        containerColor = LaraIvory
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 20.dp, vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Header
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "LARA INTELLIGENCE",
                            fontFamily = FontFamily.Serif,
                            fontWeight = FontWeight.Bold,
                            fontSize = 20.sp,
                            color = LaraCharcoal,
                            letterSpacing = 1.sp
                        )
                        Text(
                            text = "Desk Analysis & Document Reasoning",
                            fontSize = 12.sp,
                            color = LaraTextSecondaryLight
                        )
                    }
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(8.dp))
                            .background(LaraEmeraldBg)
                            .padding(horizontal = 8.dp, vertical = 4.dp)
                    ) {
                        Text("AI READY", color = LaraEmerald, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }

            // Active Dataset Card
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    border = androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight)
                ) {
                    Column(modifier = Modifier.padding(18.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Default.TableChart, contentDescription = null, tint = LaraMutedOrange, modifier = Modifier.size(22.dp))
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(selectedDataset, fontWeight = FontWeight.Bold, fontSize = 15.sp, color = LaraCharcoal)
                            }
                            Text("24,582 rows · 18 cols", fontSize = 11.sp, color = LaraTextSecondaryLight)
                        }

                        Spacer(modifier = Modifier.height(12.dp))
                        Divider(color = LaraBorderLight, thickness = 0.8.dp)
                        Spacer(modifier = Modifier.height(12.dp))

                        // Desk Action Buttons
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Button(
                                onClick = {
                                    activeOperation = "Summarize"
                                    analysisResult = "Dataset contains 24,582 sales records across 4 regions. Q3 revenue grew by +14.2% YoY driven by enterprise subscriptions."
                                },
                                modifier = Modifier.weight(1f),
                                colors = ButtonDefaults.buttonColors(containerColor = LaraCharcoal),
                                shape = RoundedCornerShape(8.dp),
                                contentPadding = PaddingValues(vertical = 8.dp)
                            ) {
                                Text("Summarize", fontSize = 11.sp, color = Color.White)
                            }

                            Button(
                                onClick = {
                                    activeOperation = "Anomalies"
                                    analysisResult = "Detected 3 regional variance anomalies: APAC discount rate exceeded 28% threshold in August (Record #1,402 and #8,912)."
                                },
                                modifier = Modifier.weight(1f),
                                colors = ButtonDefaults.buttonColors(containerColor = LaraMutedOrange),
                                shape = RoundedCornerShape(8.dp),
                                contentPadding = PaddingValues(vertical = 8.dp)
                            ) {
                                Text("Anomalies", fontSize = 11.sp, color = Color.White)
                            }

                            OutlinedButton(
                                onClick = {
                                    activeOperation = "Ask LARA"
                                    viewModel.sendTextMessage("Analyze dataset $selectedDataset for quarterly sales trends")
                                    onNavigateToCommand()
                                },
                                modifier = Modifier.weight(1f),
                                border = androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight),
                                shape = RoundedCornerShape(8.dp),
                                contentPadding = PaddingValues(vertical = 8.dp)
                            ) {
                                Text("Ask LARA", fontSize = 11.sp, color = LaraCharcoal)
                            }
                        }
                    }
                }
            }

            // Analysis Result Presentation
            if (analysisResult != null) {
                item {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(14.dp),
                        colors = CardDefaults.cardColors(containerColor = Color(0xFFF9FAF8)),
                        border = androidx.compose.foundation.BorderStroke(1.dp, LaraEmerald.copy(alpha = 0.4f))
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Default.CheckCircle, contentDescription = null, tint = LaraEmerald, modifier = Modifier.size(18.dp))
                                Spacer(modifier = Modifier.width(6.dp))
                                Text(
                                    text = "OPERATION: ${activeOperation?.uppercase()}",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = LaraEmerald
                                )
                            }
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = analysisResult ?: "",
                                fontSize = 13.sp,
                                color = LaraCharcoal,
                                lineHeight = 18.sp
                            )
                        }
                    }
                }
            }

            // Quick Document Intelligence Capabilities
            item {
                Text(
                    text = "AVAILABLE INTELLIGENCE TOOLS",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    color = LaraTextSecondaryLight,
                    letterSpacing = 0.8.sp
                )
            }

            item {
                IntelligenceToolRow(
                    icon = Icons.Default.Description,
                    title = "Legal Contract Analysis",
                    description = "Extract indemnity clauses, termination dates, and liability caps.",
                    onClick = {
                        viewModel.sendTextMessage("Analyze the active contract for liability limits")
                        onNavigateToCommand()
                    }
                )
            }

            item {
                IntelligenceToolRow(
                    icon = Icons.Default.Calculate,
                    title = "Deterministic Math & Algebraic Engine",
                    description = "Instant step-by-step solving for quadratic, linear, and polynomial equations.",
                    onClick = {
                        viewModel.sendTextMessage("Solve quadratic equation x^2 + 5x + 6 = 0")
                        onNavigateToCommand()
                    }
                )
            }

            item {
                IntelligenceToolRow(
                    icon = Icons.Default.Visibility,
                    title = "Multimodal Smart Glasses Vision",
                    description = "Instant scene understanding, OCR text extraction, and QR scanning from glasses.",
                    onClick = {
                        viewModel.sendTextMessage("What do you see in front of me?")
                        onNavigateToCommand()
                    }
                )
            }
        }
    }
}

@Composable
fun IntelligenceToolRow(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
    description: String,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        border = androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(LaraOrangeLight),
                contentAlignment = Alignment.Center
            ) {
                Icon(icon, contentDescription = null, tint = LaraMutedOrange, modifier = Modifier.size(20.dp))
            }
            Spacer(modifier = Modifier.width(14.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(title, fontWeight = FontWeight.Bold, fontSize = 13.sp, color = LaraCharcoal)
                Text(description, fontSize = 11.sp, color = LaraTextSecondaryLight, lineHeight = 15.sp)
            }
            Icon(Icons.Default.ChevronRight, contentDescription = null, tint = LaraTextSecondaryLight, modifier = Modifier.size(18.dp))
        }
    }
}
