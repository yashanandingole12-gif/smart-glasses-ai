package com.smartglasses.ai.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.presentation.theme.*

/**
 * EvaCommandField provides the instrument-like command surface
 * for interacting with EVA via voice or fluid text entry.
 */
@Composable
fun EvaCommandField(
    value: String,
    onValueChange: (String) -> Unit,
    onSend: () -> Unit,
    isListening: Boolean,
    onToggleVoice: () -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(24.dp))
            .background(EvaSurfaceGlass)
            .border(1.dp, EvaBorderSubtle, RoundedCornerShape(24.dp))
            .padding(horizontal = 14.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        // Voice Action Mic Button
        Box(
            modifier = Modifier
                .size(38.dp)
                .clip(CircleShape)
                .background(if (isListening) EvaRose else EvaSurfaceElevated)
                .clickable(onClick = onToggleVoice),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = if (isListening) Icons.Default.Stop else Icons.Default.Mic,
                contentDescription = "Voice Command",
                tint = if (isListening) EvaTextPure else EvaTeal,
                modifier = Modifier.size(18.dp)
            )
        }

        // Fluid Text Input
        Box(
            modifier = Modifier.weight(1f),
            contentAlignment = Alignment.CenterStart
        ) {
            if (value.isEmpty()) {
                Text(
                    text = if (isListening) "Listening to your voice..." else "Speak or enter command...",
                    color = EvaTextMuted,
                    fontSize = 14.sp
                )
            }
            BasicTextField(
                value = value,
                onValueChange = onValueChange,
                textStyle = TextStyle(
                    color = EvaTextPure,
                    fontSize = 14.sp
                ),
                cursorBrush = SolidColor(EvaTeal),
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                keyboardActions = KeyboardActions(onSend = { onSend() }),
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )
        }

        // Execute Send Button
        if (value.isNotBlank()) {
            Box(
                modifier = Modifier
                    .size(34.dp)
                    .clip(CircleShape)
                    .background(EvaTeal)
                    .clickable(onClick = onSend),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.Send,
                    contentDescription = "Send",
                    tint = EvaVoid,
                    modifier = Modifier.size(16.dp)
                )
            }
        }
    }
}
