package com.smartglasses.ai.core.audio

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.Locale

enum class SupportedLanguage(
    val code: String,
    val localeTag: String,
    val displayName: String,
    val nativeName: String,
    val isRtl: Boolean = false
) {
    ENGLISH_IN("en", "en-IN", "English (India)", "English"),
    ENGLISH_US("en", "en-US", "English (US)", "English"),
    HINDI("hi", "hi-IN", "Hindi", "हिन्दी"),
    MARATHI("mr", "mr-IN", "Marathi", "मराठी"),
    HINGLISH("hi-Latn", "hi-Latn-IN", "Hinglish", "Hinglish"),
    AUTO("auto", "auto", "Auto Detect", "Auto");

    fun toLocale(): Locale {
        return when (this) {
            ENGLISH_IN -> Locale("en", "IN")
            ENGLISH_US -> Locale("en", "US")
            HINDI -> Locale("hi", "IN")
            MARATHI -> Locale("mr", "IN")
            HINGLISH -> Locale("en", "IN") // Hinglish uses Latin script on en-IN / hi-IN acoustic models
            AUTO -> Locale.getDefault()
        }
    }

    companion object {
        fun fromLocaleTag(tag: String?): SupportedLanguage {
            if (tag.isNullOrBlank()) return ENGLISH_IN
            return entries.firstOrNull { 
                it.localeTag.equals(tag, ignoreCase = true) || it.code.equals(tag, ignoreCase = true)
            } ?: ENGLISH_IN
        }

        fun detectLanguageFromScript(text: String): SupportedLanguage {
            if (text.isBlank()) return ENGLISH_IN
            
            // Check Devanagari Unicode Block (U+0900 to U+097F)
            var devanagariCount = 0
            var latinCount = 0
            for (char in text) {
                val block = Character.UnicodeBlock.of(char)
                if (block == Character.UnicodeBlock.DEVANAGARI) {
                    devanagariCount++
                } else if (block == Character.UnicodeBlock.BASIC_LATIN || block == Character.UnicodeBlock.LATIN_1_SUPPLEMENT) {
                    if (char.isLetter()) latinCount++
                }
            }

            if (devanagariCount > 0) {
                // Marathi specific vocabulary markers
                val marathiMarkers = listOf("आहे", "काय", "सकाळ", "शुभ", "कसा", "कशी", "नाही", "होय", "माझं", "माझा")
                val lower = text.lowercase()
                for (marker in marathiMarkers) {
                    if (lower.contains(marker)) return MARATHI
                }
                return HINDI
            }

            // Latin script check for Hinglish markers
            val hinglishMarkers = listOf("aaj", "mera", "meri", "karo", "batao", "kya", "hai", "kaise", "samay", "kaha")
            val words = text.lowercase().split("\\s+".toRegex())
            for (w in words) {
                if (hinglishMarkers.contains(w)) return HINGLISH
            }

            return ENGLISH_IN
        }
    }
}

class SpeechLanguageManager {
    private val _currentLanguage = MutableStateFlow(SupportedLanguage.ENGLISH_IN)
    val currentLanguage: StateFlow<SupportedLanguage> = _currentLanguage.asStateFlow()

    val availableLanguages: List<SupportedLanguage> = listOf(
        SupportedLanguage.ENGLISH_IN,
        SupportedLanguage.HINDI,
        SupportedLanguage.MARATHI,
        SupportedLanguage.HINGLISH,
        SupportedLanguage.ENGLISH_US,
        SupportedLanguage.AUTO
    )

    fun setLanguage(language: SupportedLanguage) {
        _currentLanguage.value = language
    }

    fun setLanguageByCode(codeOrTag: String) {
        _currentLanguage.value = SupportedLanguage.fromLocaleTag(codeOrTag)
    }

    fun detectLanguage(transcript: String): SupportedLanguage {
        return SupportedLanguage.detectLanguageFromScript(transcript)
    }
}
