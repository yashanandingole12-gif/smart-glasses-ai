package com.smartglasses.ai.presentation.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable

private val DarkColorScheme = darkColorScheme(
    primary = CyanNeon,
    secondary = EmeraldNeon,
    tertiary = AmberNeon,
    background = WearableDarkBackground,
    surface = WearableDarkSurface,
    surfaceVariant = WearableDarkSurfaceVariant,
    onPrimary = WearableDarkBackground,
    onSecondary = WearableDarkBackground,
    onBackground = TextPrimary,
    onSurface = TextPrimary,
    onSurfaceVariant = TextSecondary,
    outline = WearableCardBorder
)

@Composable
fun SmartGlassesTheme(
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        typography = WearableTypography,
        content = content
    )
}
