package com.smartglasses.ai.presentation.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.smartglasses.ai.presentation.theme.EvaCyan
import com.smartglasses.ai.presentation.theme.EvaTeal
import kotlin.random.Random

/**
 * EvaWaveform renders a continuous organic audio visualizer
 * that reflects live speech or listening activity.
 */
@Composable
fun EvaWaveform(
    isActive: Boolean,
    modifier: Modifier = Modifier,
    waveColor: Color = EvaTeal
) {
    val barCount = 18
    val infiniteTransition = rememberInfiniteTransition(label = "WaveformAnim")

    val pulse by infiniteTransition.animateFloat(
        initialValue = 0.2f,
        targetValue = 1.0f,
        animationSpec = infiniteRepeatable(
            animation = tween(400, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "Pulse"
    )

    Canvas(
        modifier = modifier
            .fillMaxWidth()
            .height(28.dp)
    ) {
        val spacing = size.width / (barCount * 2)
        val barWidth = 3.dp.toPx()

        for (i in 0 until barCount) {
            val normalizedX = (i * 2 + 1) * spacing
            val baseHeight = if (isActive) {
                val seed = (i * 17 + pulse * 10).toInt()
                val randomFactor = (Random(seed).nextFloat() * 0.7f + 0.3f)
                size.height * randomFactor * pulse
            } else {
                3.dp.toPx()
            }

            val barHeight = baseHeight.coerceAtLeast(3.dp.toPx())
            val topY = (size.height - barHeight) / 2f

            drawRoundRect(
                color = if (isActive) waveColor else waveColor.copy(alpha = 0.2f),
                topLeft = Offset(normalizedX - barWidth / 2f, topY),
                size = Size(barWidth, barHeight),
                cornerRadius = CornerRadius(barWidth / 2f, barWidth / 2f)
            )
        }
    }
}
