package com.smartglasses.ai.presentation.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.smartglasses.ai.presentation.theme.*

/**
 * EvaContextCard renders proactive, ambient contextual awareness
 * (calendar events, incoming messages, research suggestions) with quiet elegance.
 */
@Composable
fun EvaContextCard(
    title: String,
    subtitle: String,
    category: String = "AWARENESS",
    onClick: () -> Unit = {},
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(EvaSurfaceGlass)
            .border(1.dp, EvaBorderSubtle, RoundedCornerShape(16.dp))
            .clickable(onClick = onClick)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = category,
                color = EvaTeal,
                fontSize = 10.sp,
                letterSpacing = 1.sp
            )
            Text(
                text = "Context",
                color = EvaTextMuted,
                fontSize = 10.sp
            )
        }

        Text(
            text = title,
            color = EvaTextPure,
            fontSize = 14.sp
        )

        Text(
            text = subtitle,
            color = EvaTextSecondary,
            fontSize = 12.sp,
            lineHeight = 16.sp
        )
    }
}
