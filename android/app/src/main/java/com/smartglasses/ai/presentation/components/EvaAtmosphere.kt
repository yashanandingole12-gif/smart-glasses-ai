package com.smartglasses.ai.presentation.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import com.smartglasses.ai.presentation.theme.*

/**
 * EVA Atmosphere Modes — 8 Shared Semantic States
 */
enum class EvaAtmosphereMode(
    val emotion: String,
    val foundation: Color,
    val accent: Color,
    val highlight: Color
) {
    GROUNDED("calm / grounded / stable", EvaOliveBlack, EvaOlive, Color(0xFFB49E45)),
    FOCUSED("clarity / concentration / precision", EvaNight, EvaMoss, EvaGold),
    CREATIVE("creative / intimate / expressive", EvaEarthBlack, EvaWine, Color(0xFFB57B88)),
    CURIOUS("discovery / exploration / curiosity", EvaVoid, EvaAmberBrown, EvaGold),
    REFLECTIVE("quiet / contemplative / deep", EvaNight, EvaBronze, EvaSunlight),
    ENERGETIC("momentum / action / vitality", EvaUmber, EvaAmber, EvaSunlight),
    NIGHT("mysterious / quiet / expansive", EvaVoid, EvaEarthBlack, EvaGold),
    CUSTOM("adaptive / personal resonance", EvaVoid, EvaAmberBrown, EvaGold)
}

/**
 * EvaAtmosphere renders the organic living darkness atmosphere of EVA.
 * Performs smooth organic tone shifting across 800-1800ms when mode changes.
 */
@Composable
fun EvaAtmosphere(
    modifier: Modifier = Modifier,
    mode: EvaAtmosphereMode = EvaAtmosphereMode.GROUNDED,
    content: @Composable () -> Unit
) {
    // Smooth tone-shifting color interpolation (1400ms organic transition)
    val animatedFoundation by animateColorAsState(
        targetValue = mode.foundation,
        animationSpec = tween(durationMillis = 1400, easing = FastOutSlowInEasing),
        label = "FoundationColor"
    )
    val animatedAccent by animateColorAsState(
        targetValue = mode.accent,
        animationSpec = tween(durationMillis = 1400, easing = FastOutSlowInEasing),
        label = "AccentColor"
    )
    val animatedHighlight by animateColorAsState(
        targetValue = mode.highlight,
        animationSpec = tween(durationMillis = 1400, easing = FastOutSlowInEasing),
        label = "HighlightColor"
    )

    val infiniteTransition = rememberInfiniteTransition(label = "AtmosphereDrift")
    val driftAnim by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(14000, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "Drift"
    )

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(animatedFoundation)
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val centerOffset = Offset(
                x = size.width * (0.45f + 0.1f * driftAnim),
                y = size.height * (0.35f + 0.1f * (1f - driftAnim))
            )

            // Deep atmospheric radial illumination (Color Existing Inside Darkness)
            drawCircle(
                brush = Brush.radialGradient(
                    colors = listOf(
                        animatedAccent.copy(alpha = 0.28f),
                        animatedHighlight.copy(alpha = 0.12f),
                        Color.Transparent
                    ),
                    center = centerOffset,
                    radius = size.maxDimension * 0.70f
                ),
                radius = size.maxDimension * 0.70f,
                center = centerOffset
            )
        }

        content()
    }
}
