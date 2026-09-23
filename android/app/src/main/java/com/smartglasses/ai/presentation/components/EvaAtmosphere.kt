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
 * EVA Atmosphere Modes — Adapted for Clean Light Ivory / Green Identity
 */
enum class EvaAtmosphereMode(
    val emotion: String,
    val foundation: Color,
    val accent: Color,
    val highlight: Color
) {
    GROUNDED("calm / grounded / stable", EvaIvory, EvaPrimaryGreen, EvaPaleGreen),
    FOCUSED("clarity / concentration / precision", EvaPureWhite, EvaDeepGreen, EvaMistGreen),
    CREATIVE("creative / intimate / expressive", EvaWarmIvory, EvaSoftGreen, EvaPaleGreen),
    CURIOUS("discovery / exploration / curiosity", EvaIvory, EvaPrimaryGreen, EvaMistGreen),
    REFLECTIVE("quiet / contemplative / deep", EvaLightStone, EvaSoftGreen, EvaPureWhite),
    ENERGETIC("momentum / action / vitality", EvaPureWhite, EvaPrimaryGreen, EvaPaleGreen),
    NIGHT("quiet / resting / soft light", EvaLightStone, EvaDeepGreen, EvaMistGreen),
    CUSTOM("adaptive / personal resonance", EvaIvory, EvaPrimaryGreen, EvaPaleGreen)
}

/**
 * EvaAtmosphere renders the calm, natural, light atmosphere of EVA.
 * Soft diffuse warm light with subtle natural green illumination.
 */
@Composable
fun EvaAtmosphere(
    modifier: Modifier = Modifier,
    mode: EvaAtmosphereMode = EvaAtmosphereMode.GROUNDED,
    content: @Composable () -> Unit
) {
    val animatedFoundation by animateColorAsState(
        targetValue = mode.foundation,
        animationSpec = tween(durationMillis = 1000, easing = FastOutSlowInEasing),
        label = "FoundationColor"
    )
    val animatedAccent by animateColorAsState(
        targetValue = mode.accent,
        animationSpec = tween(durationMillis = 1000, easing = FastOutSlowInEasing),
        label = "AccentColor"
    )

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(animatedFoundation)
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val centerOffset = Offset(
                x = size.width * 0.5f,
                y = size.height * 0.25f
            )

            // Ultra-subtle diffuse soft natural radiance
            drawCircle(
                brush = Brush.radialGradient(
                    colors = listOf(
                        animatedAccent.copy(alpha = 0.05f),
                        animatedFoundation.copy(alpha = 0.4f),
                        Color.Transparent
                    ),
                    center = centerOffset,
                    radius = size.maxDimension * 0.85f
                ),
                radius = size.maxDimension * 0.85f,
                center = centerOffset
            )
        }

        content()
    }
}
