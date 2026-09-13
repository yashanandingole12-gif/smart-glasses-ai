package com.smartglasses.ai.presentation.settings

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import com.smartglasses.ai.presentation.theme.*

@Composable
fun BackendConfigDialog(
    currentUrl: String,
    onDismiss: () -> Unit,
    onSaveUrl: (String) -> Unit,
    onTestConnection: (String, (Boolean, String) -> Unit) -> Unit
) {
    var urlInput by remember { mutableStateOf(currentUrl) }
    var testResult by remember { mutableStateOf<Pair<Boolean, String>?>(null) }
    var isTesting by remember { mutableStateOf(false) }

    Dialog(onDismissRequest = onDismiss) {
        Card(
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, LaraBorderLight, RoundedCornerShape(16.dp))
        ) {
            Column(
                modifier = Modifier
                    .padding(24.dp)
                    .fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Text(
                    text = "BACKEND CONFIGURATION",
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                    color = LaraMutedOrange,
                    letterSpacing = 1.2.sp
                )

                Text(
                    text = "Configure FastAPI backend host URL. Support Android emulator (10.0.2.2), physical LAN IP, or HTTPS domain.",
                    fontSize = 13.sp,
                    color = LaraTextSecondaryLight,
                    lineHeight = 18.sp
                )

                // Presets
                Text(
                    text = "Quick Presets:",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = LaraTextSecondaryLight
                )
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    SuggestionChip(
                        onClick = { urlInput = "http://10.0.2.2:8001/" },
                        label = { Text("Emulator", fontSize = 11.sp) }
                    )
                    SuggestionChip(
                        onClick = { urlInput = "http://192.168.1.100:8001/" },
                        label = { Text("LAN IP", fontSize = 11.sp) }
                    )
                    SuggestionChip(
                        onClick = { urlInput = "http://127.0.0.1:8001/" },
                        label = { Text("Localhost", fontSize = 11.sp) }
                    )
                }

                // URL Input
                OutlinedTextField(
                    value = urlInput,
                    onValueChange = {
                        urlInput = it
                        testResult = null
                    },
                    label = { Text("Server URL", color = LaraTextSecondaryLight) },
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = LaraTextPrimaryLight,
                        unfocusedTextColor = LaraTextPrimaryLight,
                        focusedBorderColor = LaraMutedOrange,
                        unfocusedBorderColor = LaraBorderLight,
                        cursorColor = LaraMutedOrange
                    ),
                    modifier = Modifier.fillMaxWidth()
                )

                // Test Status
                testResult?.let { (success, message) ->
                    Text(
                        text = if (success) "✓ $message" else "✗ $message",
                        color = if (success) LaraEmerald else LaraMutedRed,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Medium
                    )
                }

                // Buttons
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    OutlinedButton(
                        onClick = {
                            isTesting = true
                            testResult = null
                            onTestConnection(urlInput) { success, msg ->
                                isTesting = false
                                testResult = Pair(success, msg)
                            }
                        },
                        enabled = !isTesting,
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = LaraMutedOrange),
                        border = androidx.compose.foundation.BorderStroke(1.dp, LaraMutedOrange),
                        modifier = Modifier.weight(1f)
                    ) {
                        if (isTesting) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(16.dp),
                                color = LaraMutedOrange,
                                strokeWidth = 2.dp
                            )
                        } else {
                            Text("Test Link", fontSize = 12.sp)
                        }
                    }

                    Button(
                        onClick = {
                            onSaveUrl(urlInput)
                            onDismiss()
                        },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = LaraMutedOrange,
                            contentColor = Color.White
                        ),
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Save", fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}
