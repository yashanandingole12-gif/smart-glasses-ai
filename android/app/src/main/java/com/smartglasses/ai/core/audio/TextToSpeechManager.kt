package com.smartglasses.ai.core.audio

import android.content.Context
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.Locale
import java.util.UUID

enum class AndroidTTSState {
    IDLE,
    INITIALIZING,
    READY,
    SPEAKING,
    COMPLETED,
    FAILED
}

class TextToSpeechManager(private val context: Context) {
    private var tts: TextToSpeech? = null

    private val _ttsState = MutableStateFlow(AndroidTTSState.INITIALIZING)
    val ttsState: StateFlow<AndroidTTSState> = _ttsState.asStateFlow()

    private var onSpeechDoneCallback: (() -> Unit)? = null

    init {
        initTTS()
    }

    private fun initTTS() {
        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale.getDefault()
                tts?.setSpeechRate(1.05f)
                tts?.setPitch(1.0f)
                tts?.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                    override fun onStart(utteranceId: String?) {
                        _ttsState.value = AndroidTTSState.SPEAKING
                    }

                    override fun onDone(utteranceId: String?) {
                        _ttsState.value = AndroidTTSState.COMPLETED
                        onSpeechDoneCallback?.invoke()
                        _ttsState.value = AndroidTTSState.READY
                    }

                    @Suppress("OVERRIDE_DEPRECATION")
                    override fun onError(utteranceId: String?) {
                        _ttsState.value = AndroidTTSState.FAILED
                        _ttsState.value = AndroidTTSState.READY
                    }
                })
                _ttsState.value = AndroidTTSState.READY
            } else {
                _ttsState.value = AndroidTTSState.FAILED
            }
        }
    }

    private fun normalizeForSpeech(raw: String): String {
        var res = raw
        // 1. Currency
        res = res.replace(Regex("₹\\s*(\\d+(?:\\.\\d+)?)"), "$1 rupees")
        res = res.replace(Regex("(?i)(?:Rs\\.?|INR)\\s*(\\d+(?:\\.\\d+)?)"), "$1 rupees")
        res = res.replace(Regex("\\$\\s*(\\d+(?:\\.\\d+)?)"), "$1 dollars")
        res = res.replace(Regex("€\\s*(\\d+(?:\\.\\d+)?)"), "$1 euros")

        // 2. OTP / Verification codes: "OTP is 482910" -> "OTP is 4 8 2 9 1 0"
        res = res.replace(Regex("(?i)\\b(OTP(?:\\s+is|\\s*:)?|code(?:\\s+is|\\s*:)?|pin(?:\\s+is|\\s*:)?|verification\\s+code(?:\\s+is|\\s*:)?)\\s*(\\d{4,8})\\b")) { match ->
            val prefix = match.groupValues[1]
            val digits = match.groupValues[2].toCharArray().joinToString(" ")
            "$prefix $digits"
        }

        // 3. International phone numbers: +1 5550100 or +91 9876543210
        res = res.replace(Regex("\\+(\\d{1,3})[\\s\\-]?(\\d{5})[\\s\\-]?(\\d{5})\\b")) { match ->
            val cc = match.groupValues[1]
            val p1 = match.groupValues[2].toCharArray().joinToString(" ")
            val p2 = match.groupValues[3].toCharArray().joinToString(" ")
            "plus $cc, $p1, $p2"
        }

        // 4. Standard 10-digit Phone numbers: 9876543210 -> "9 8 7 6 5, 4 3 2 1 0"
        res = res.replace(Regex("(?<![\\d\\.])(\\d{5})(\\d{5})(?![\\d\\.])")) { match ->
            val d1 = match.groupValues[1].toCharArray().joinToString(" ")
            val d2 = match.groupValues[2].toCharArray().joinToString(" ")
            "$d1, $d2"
        }

        // 5. Standalone 7-9 digit sequences
        res = res.replace(Regex("(?<![\\d\\.])(\\d{7,9})(?![\\d\\.])")) { match ->
            match.groupValues[1].toCharArray().joinToString(" ")
        }

        // 6. Strip markdown and excessive symbols
        res = res
            .replace(Regex("[#*`_\\[\\]{}<>]"), "")
            .replace(Regex("(?m)^\\s*-\\s+"), "")
            .replace(Regex("\\s+"), " ")
            .trim()

        return res
    }

    fun speak(text: String, onDone: (() -> Unit)? = null) {
        if (text.isBlank()) return
        onSpeechDoneCallback = onDone
        _ttsState.value = AndroidTTSState.SPEAKING
        val utteranceId = UUID.randomUUID().toString()
        val cleanText = normalizeForSpeech(text)

        tts?.speak(cleanText, TextToSpeech.QUEUE_FLUSH, null, utteranceId)
    }

    fun stop() {
        tts?.stop()
        _ttsState.value = AndroidTTSState.READY
    }

    fun shutdown() {
        tts?.stop()
        tts?.shutdown()
        tts = null
    }
}
