package com.smartglasses.ai.presentation.info

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
 * LARA Unified Information Center:
 * - Cross-tool information retrieval across Mail, Calendar, Messages, Contacts, Files, Notes, Research
 * - Natural language search interface
 */
@Composable
fun InformationWorkspaceScreen(
    viewModel: WearableHomeViewModel,
    onNavigateToCommand: () -> Unit = {}
) {
    var searchQuery by remember { mutableStateOf("") }
    var selectedCategory by remember { mutableStateOf("All") }
    val categories = listOf("All", "Mail", "Calendar", "Messages", "Contacts", "Files", "Research")

    Scaffold(
        containerColor = LaraIvory
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 20.dp, vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            // Header
            item {
                Column {
                    Text(
                        text = "INFORMATION CENTER",
                        fontFamily = FontFamily.Serif,
                        fontWeight = FontWeight.Bold,
                        fontSize = 20.sp,
                        color = LaraCharcoal,
                        letterSpacing = 1.sp
                    )
                    Text(
                        text = "Unified Cross-Domain Executive Knowledge",
                        fontSize = 12.sp,
                        color = LaraTextSecondaryLight
                    )
                }
            }

            // Natural Language Search Bar
            item {
                OutlinedTextField(
                    value = searchQuery,
                    onValueChange = { searchQuery = it },
                    modifier = Modifier.fillMaxWidth(),
                    placeholder = { Text("Search emails, files, meetings, contacts...", fontSize = 13.sp, color = LaraTextSecondaryLight) },
                    leadingIcon = { Icon(Icons.Default.Search, contentDescription = null, tint = LaraMutedOrange) },
                    trailingIcon = {
                        if (searchQuery.isNotEmpty()) {
                            IconButton(onClick = {
                                viewModel.sendTextMessage(searchQuery)
                                onNavigateToCommand()
                            }) {
                                Icon(Icons.Default.ArrowForward, contentDescription = "Query", tint = LaraCharcoal)
                            }
                        }
                    },
                    shape = RoundedCornerShape(12.dp),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = LaraMutedOrange,
                        unfocusedBorderColor = LaraBorderLight,
                        focusedContainerColor = Color.White,
                        unfocusedContainerColor = Color.White
                    ),
                    singleLine = true
                )
            }

            // Category Chips Row
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    categories.take(4).forEach { cat ->
                        val isSelected = selectedCategory == cat
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(8.dp))
                                .background(if (isSelected) LaraCharcoal else Color.White)
                                .border(1.dp, if (isSelected) LaraCharcoal else LaraBorderLight, RoundedCornerShape(8.dp))
                                .clickable { selectedCategory = cat }
                                .padding(horizontal = 12.dp, vertical = 6.dp)
                        ) {
                            Text(
                                text = cat,
                                color = if (isSelected) Color.White else LaraCharcoal,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    }
                }
            }

            // Quick Info Query Chips
            item {
                Text(
                    text = "EXECUTIVE SHORTCUTS",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    color = LaraTextSecondaryLight,
                    letterSpacing = 0.8.sp
                )
            }

            item {
                InfoShortcutCard(
                    title = "Recent Communications",
                    query = "Check my unread emails and recent messages",
                    icon = Icons.Default.Email,
                    onQueryClick = {
                        viewModel.sendTextMessage("Check my unread emails and recent messages")
                        onNavigateToCommand()
                    }
                )
            }

            item {
                InfoShortcutCard(
                    title = "Today's Agenda & Schedule",
                    query = "What is on my calendar today and what meetings do I have?",
                    icon = Icons.Default.CalendarMonth,
                    onQueryClick = {
                        viewModel.sendTextMessage("What is on my calendar today and what meetings do I have?")
                        onNavigateToCommand()
                    }
                )
            }

            item {
                InfoShortcutCard(
                    title = "Key Contacts & Directory",
                    query = "Who is Rahul and show his contact details",
                    icon = Icons.Default.Person,
                    onQueryClick = {
                        viewModel.sendTextMessage("Who is Rahul?")
                        onNavigateToCommand()
                    }
                )
            }

            item {
                InfoShortcutCard(
                    title = "Uploaded Documents & Files",
                    query = "Summarize my active document and findings",
                    icon = Icons.Default.Folder,
                    onQueryClick = {
                        viewModel.sendTextMessage("Summarize my active document and findings")
                        onNavigateToCommand()
                    }
                )
            }
        }
    }
}

@Composable
fun InfoShortcutCard(
    title: String,
    query: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    onQueryClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onQueryClick() },
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        border = androidx.compose.foundation.BorderStroke(1.dp, LaraBorderLight)
    ) {
        Row(
            modifier = Modifier.padding(14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(36.dp)
                    .clip(RoundedCornerShape(8.dp))
                    .background(LaraIvory),
                contentAlignment = Alignment.Center
            ) {
                Icon(icon, contentDescription = null, tint = LaraCharcoal, modifier = Modifier.size(18.dp))
            }
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(title, fontWeight = FontWeight.Bold, fontSize = 13.sp, color = LaraCharcoal)
                Text("\"$query\"", fontSize = 11.sp, color = LaraTextSecondaryLight, lineHeight = 15.sp)
            }
            Icon(Icons.Default.ArrowOutward, contentDescription = null, tint = LaraMutedOrange, modifier = Modifier.size(16.dp))
        }
    }
}
