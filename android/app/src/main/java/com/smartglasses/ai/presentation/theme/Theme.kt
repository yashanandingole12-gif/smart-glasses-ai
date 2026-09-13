package com.smartglasses.ai.presentation.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val LaraExecutiveColorScheme = lightColorScheme(
    primary = LaraCharcoal,
    secondary = LaraMutedOrange,
    tertiary = LaraEmerald,
    background = LaraIvory,
    surface = LaraWarmWhite,
    surfaceVariant = LaraSurfaceSubtle,
    onPrimary = LaraWarmWhite,
    onSecondary = LaraCharcoal,
    onBackground = LaraCharcoal,
    onSurface = LaraCharcoal,
    onSurfaceVariant = LaraTextSecondaryLight,
    outline = LaraBorderLight
)

@Composable
fun LaraTheme(
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = LaraExecutiveColorScheme,
        typography = WearableTypography,
        content = content
    )
}

// Backward Compatibility Alias
@Composable
fun SmartGlassesTheme(
    content: @Composable () -> Unit
) {
    LaraTheme(content = content)
}
