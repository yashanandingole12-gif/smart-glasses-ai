package com.smartglasses.ai.core.audio

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.Locale

enum class STTState {
    IDLE,
    LISTENING,
    PROCESSING,
    ERROR
}

class SpeechRecognizerManager(
    private val context: Context,
    private val onResult: (String) -> Unit,
    private val onError: (String) -> Unit = {}
) {
    private var speechRecognizer: SpeechRecognizer? = null

    private val _sttState = MutableStateFlow(STTState.IDLE)
    val sttState: StateFlow<STTState> = _sttState.asStateFlow()

    private val _partialTranscript = MutableStateFlow("")
    val partialTranscript: StateFlow<String> = _partialTranscript.asStateFlow()

    private val _audioRms = MutableStateFlow(0f)
    val audioRms: StateFlow<Float> = _audioRms.asStateFlow()

    init {
        initRecognizer()
    }

    private fun initRecognizer() {
        if (SpeechRecognizer.isRecognitionAvailable(context)) {
            speechRecognizer = SpeechRecognizer.createSpeechRecognizer(context).apply {
                setRecognitionListener(object : RecognitionListener {
                    override fun onReadyForSpeech(params: Bundle?) {
                        _sttState.value = STTState.LISTENING
                    }

                    override fun onBeginningOfSpeech() {
                        _sttState.value = STTState.LISTENING
                    }

                    override fun onRmsChanged(rmsdB: Float) {
                        _audioRms.value = rmsdB
                    }

                    override fun onBufferReceived(buffer: ByteArray?) {}

                    override fun onEndOfSpeech() {
                        _sttState.value = STTState.PROCESSING
                    }

                    override fun onError(error: Int) {
                        _sttState.value = STTState.IDLE
                        val errMsg = getErrorMessage(error)
                        onError(errMsg)
                    }

                    override fun onResults(results: Bundle?) {
                        _sttState.value = STTState.IDLE
                        val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                        val text = matches?.firstOrNull() ?: ""
                        if (text.isNotBlank()) {
                            onResult(text)
                        }
                    }

                    override fun onPartialResults(partialResults: Bundle?) {
                        val matches = partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                        val text = matches?.firstOrNull() ?: ""
                        if (text.isNotBlank()) {
                            _partialTranscript.value = text
                        }
                    }

                    override fun onEvent(eventType: Int, params: Bundle?) {}
                })
            }
        }
    }

    fun startListening() {
        _partialTranscript.value = ""
        _sttState.value = STTState.LISTENING
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
        }
        try {
            speechRecognizer?.startListening(intent)
        } catch (e: Exception) {
            _sttState.value = STTState.ERROR
            onError(e.message ?: "STT failed to start")
        }
    }

    fun stopListening() {
        try {
            speechRecognizer?.stopListening()
        } catch (e: Exception) {
            // Ignore
        }
    }

    fun cancel() {
        try {
            speechRecognizer?.cancel()
            _sttState.value = STTState.IDLE
        } catch (e: Exception) {
            // Ignore
        }
    }

    fun destroy() {
        try {
            speechRecognizer?.destroy()
            speechRecognizer = null
        } catch (e: Exception) {
            // Ignore
        }
    }

    private fun getErrorMessage(errorCode: Int): String {
        return when (errorCode) {
            SpeechRecognizer.ERROR_AUDIO -> "Audio recording error"
            SpeechRecognizer.ERROR_CLIENT -> "Client side error"
            SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "Insufficient permissions"
            SpeechRecognizer.ERROR_NETWORK -> "Network error"
            SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> "Network timeout"
            SpeechRecognizer.ERROR_NO_MATCH -> "No speech detected"
            SpeechRecognizer.ERROR_RECOGNIZER_BUSY -> "Recognition service busy"
            SpeechRecognizer.ERROR_SERVER -> "Server error"
            SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "No speech input"
            else -> "Speech recognition error ($errorCode)"
        }
    }
}
