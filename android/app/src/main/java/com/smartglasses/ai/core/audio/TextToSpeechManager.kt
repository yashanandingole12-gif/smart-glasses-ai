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

    fun speak(text: String, onDone: (() -> Unit)? = null) {
        if (text.isBlank()) return
        onSpeechDoneCallback = onDone
        _ttsState.value = AndroidTTSState.SPEAKING
        val utteranceId = UUID.randomUUID().toString()
        // Strip markdown characters for natural speech synthesis
        val cleanText = text
            .replace(Regex("[#*`_\\[\\]]"), "")
            .replace(Regex("(?m)^\\s*-\\s+"), "")
            .trim()

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
