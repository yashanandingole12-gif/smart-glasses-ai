package com.smartglasses.ai.presentation.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val LuxuryColorScheme = lightColorScheme(
    primary = LuxuryEspresso,
    secondary = LuxuryChampagneGold,
    tertiary = LuxurySage,
    background = LuxuryIvory,
    surface = LuxuryWarmWhite,
    surfaceVariant = LuxurySurfaceSubtle,
    onPrimary = LuxuryWarmWhite,
    onSecondary = LuxuryEspresso,
    onBackground = LuxuryCharcoal,
    onSurface = LuxuryCharcoal,
    onSurfaceVariant = LuxuryTextMuted,
    outline = LuxuryBorder
)

@Composable
fun SmartGlassesTheme(
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = LuxuryColorScheme,
        typography = WearableTypography,
        content = content
    )
}
