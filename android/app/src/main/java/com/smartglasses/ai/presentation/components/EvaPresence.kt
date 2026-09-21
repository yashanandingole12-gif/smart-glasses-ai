package com.smartglasses.ai.presentation.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.unit.dp
import com.smartglasses.ai.domain.models.AssistantState
import com.smartglasses.ai.presentation.theme.*
import kotlin.math.cos
import kotlin.math.sin

/**
 * EvaPresence is the living, breathing environmental signature of EVA.
 * It dynamically adapts its luminescence, orbital frequency, and chromatic core
 * based on real-time AssistantState.
 */
@Composable
fun EvaPresence(
    state: AssistantState,
    isOnline: Boolean = true,
    onClick: () -> Unit = {},
    modifier: Modifier = Modifier
) {
    val infiniteTransition = rememberInfiniteTransition(label = "EvaPresenceMotion")

    // Breathing expansion
    val breatheScale by infiniteTransition.animateFloat(
        initialValue = 0.92f,
        targetValue = 1.14f,
        animationSpec = infiniteRepeatable(
            animation = tween(
                durationMillis = when (state) {
                    AssistantState.LISTENING -> 1400
                    AssistantState.PROCESSING -> 800
                    AssistantState.RESPONDING, AssistantState.SPEAKING -> 1000
                    else -> 4200
                },
                easing = FastOutSlowInEasing
            ),
            repeatMode = RepeatMode.Reverse
        ),
        label = "BreatheScale"
    )

    // Orbital rotation
    val orbitalAngle by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(
                durationMillis = when (state) {
                    AssistantState.PROCESSING -> 3000
                    AssistantState.LISTENING -> 6000
                    else -> 14000
                },
                easing = LinearEasing
            )
        ),
        label = "OrbitalAngle"
    )

    // Dynamic core color transition
    val targetColor = when {
        !isOnline -> EvaSlate
        state == AssistantState.LISTENING -> EvaCyan
        state == AssistantState.PROCESSING -> EvaViolet
        state == AssistantState.RESPONDING || state == AssistantState.SPEAKING -> EvaTeal
        state == AssistantState.ERROR -> EvaRose
        else -> EvaTeal
    }

    val animatedColor by animateColorAsState(
        targetValue = targetColor,
        animationSpec = tween(600),
        label = "PresenceColor"
    )

    Box(
        modifier = modifier
            .size(130.dp)
            .clickable(
                interactionSource = remember { MutableInteractionSource() },
                indication = null,
                onClick = onClick
            ),
        contentAlignment = Alignment.Center
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val center = Offset(size.width / 2f, size.height / 2f)
            val baseRadius = size.minDimension / 2f * 0.7f

            // 1. Atmospheric Outer Halo
            drawCircle(
                brush = Brush.radialGradient(
                    colors = listOf(
                        animatedColor.copy(alpha = if (state == AssistantState.LISTENING) 0.45f else 0.25f),
                        animatedColor.copy(alpha = 0.08f),
                        Color.Transparent
                    ),
                    center = center,
                    radius = baseRadius * breatheScale * 1.5f
                ),
                radius = baseRadius * breatheScale * 1.5f,
                center = center
            )

            // 2. Fine Orbital Ring
            drawCircle(
                color = animatedColor.copy(alpha = 0.35f),
                radius = baseRadius * 0.95f,
                center = center,
                style = Stroke(width = 1.5.dp.toPx())
            )

            // 3. Orbital Satellite Particle
            val rad = Math.toRadians(orbitalAngle.toDouble())
            val satellitePos = Offset(
                x = center.x + (baseRadius * 0.95f * cos(rad)).toFloat(),
                y = center.y + (baseRadius * 0.95f * sin(rad)).toFloat()
            )
            drawCircle(
                color = animatedColor,
                radius = 3.dp.toPx(),
                center = satellitePos
            )

            // 4. Radiant Living Core
            drawCircle(
                brush = Brush.radialGradient(
                    colors = listOf(
                        EvaTextPure,
                        animatedColor,
                        EvaIndigo
                    ),
                    center = center,
                    radius = baseRadius * 0.48f * breatheScale
                ),
                radius = baseRadius * 0.48f * breatheScale,
                center = center
            )
        }
    }
}
