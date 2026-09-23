package com.smartglasses.ai.presentation.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

// =========================================================================
// EVA Premium Natural Theme — Clean Light Color Scheme
// =========================================================================
private val EvaNaturalColorScheme = lightColorScheme(
    primary = EvaPrimaryGreen,
    onPrimary = EvaPureWhite,
    primaryContainer = EvaMistGreen,
    onPrimaryContainer = EvaDeepGreen,
    secondary = EvaSoftGreen,
    onSecondary = EvaPureWhite,
    secondaryContainer = EvaPaleGreen,
    onSecondaryContainer = EvaDeepGreen,
    tertiary = EvaDeepGreen,
    background = EvaIvory,
    onBackground = EvaPrimaryBlack,
    surface = EvaPureWhite,
    onSurface = EvaPrimaryBlack,
    surfaceVariant = EvaWarmIvory,
    onSurfaceVariant = EvaMutedText,
    outline = EvaBorderSubtle
)

@Composable
fun EvaTheme(
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = EvaNaturalColorScheme,
        typography = WearableTypography,
        content = content
    )
}

// Backward Compatibility Aliases
@Composable
fun LaraTheme(
    content: @Composable () -> Unit
) {
    EvaTheme(content = content)
}

@Composable
fun SmartGlassesTheme(
    content: @Composable () -> Unit
) {
    EvaTheme(content = content)
}
