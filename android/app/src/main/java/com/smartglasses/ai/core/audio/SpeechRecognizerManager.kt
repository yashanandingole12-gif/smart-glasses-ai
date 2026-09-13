package com.smartglasses.ai.core.audio

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.util.Log
import androidx.core.content.ContextCompat
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.Locale

enum class STTState {
    IDLE,
    LISTENING,
    PROCESSING,
    SUCCESS,
    ERROR
}

data class STTSessionMetadata(
    val requestedLanguage: SupportedLanguage,
    val actualLanguageTag: String,
    val startTimeMs: Long,
    val durationMs: Long = 0,
    val textLength: Int = 0,
    val errorCode: Int? = null,
    val retryAttempted: Boolean = false
)

class SpeechRecognizerManager(
    private val context: Context,
    val languageManager: SpeechLanguageManager = SpeechLanguageManager(),
    private val onResult: (String, STTSessionMetadata) -> Unit,
    private val onError: (String, STTSessionMetadata) -> Unit = { _, _ -> }
) {
    companion object {
        private const val TAG = "SmartGlasses.STT"
    }

    private val mainHandler = Handler(Looper.getMainLooper())
    private var speechRecognizer: SpeechRecognizer? = null
    private var isSessionActive = false
    private var sessionStartTime = 0L
    private var hasRetried = false

    private val _sttState = MutableStateFlow(STTState.IDLE)
    val sttState: StateFlow<STTState> = _sttState.asStateFlow()

    private val _partialTranscript = MutableStateFlow("")
    val partialTranscript: StateFlow<String> = _partialTranscript.asStateFlow()

    private val _audioRms = MutableStateFlow(0f)
    val audioRms: StateFlow<Float> = _audioRms.asStateFlow()

    init {
        mainHandler.post {
            initRecognizer()
        }
    }

    private fun initRecognizer() {
        if (!SpeechRecognizer.isRecognitionAvailable(context)) {
            Log.e(TAG, "STT_ERROR: Speech recognition service not available on this device")
            _sttState.value = STTState.ERROR
            return
        }

        try {
            speechRecognizer?.destroy()
            speechRecognizer = SpeechRecognizer.createSpeechRecognizer(context).apply {
                setRecognitionListener(createRecognitionListener())
            }
            Log.i(TAG, "STT_INIT: SpeechRecognizer created successfully on Main Thread.")
        } catch (e: Exception) {
            Log.e(TAG, "STT_ERROR: Failed to initialize SpeechRecognizer (${e.message})")
            _sttState.value = STTState.ERROR
        }
    }

    private fun createRecognitionListener(): RecognitionListener {
        return object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {
                _sttState.value = STTState.LISTENING
                val lang = languageManager.currentLanguage.value
                Log.i(TAG, "STT_READY: Listening for voice... (Language=${lang.localeTag})")
            }

            override fun onBeginningOfSpeech() {
                _sttState.value = STTState.LISTENING
                Log.i(TAG, "STT_START: Speech detected by phone microphone")
            }

            override fun onRmsChanged(rmsdB: Float) {
                _audioRms.value = rmsdB
            }

            override fun onBufferReceived(buffer: ByteArray?) {}

            override fun onEndOfSpeech() {
                _sttState.value = STTState.PROCESSING
                Log.i(TAG, "STT_STOP: End of speech detected, processing audio transcript...")
            }

            override fun onError(error: Int) {
                val durationMs = SystemClock.elapsedRealtime() - sessionStartTime
                val lang = languageManager.currentLanguage.value
                val errMsg = getErrorMessage(error)
                
                Log.w(TAG, "STT_ERROR: code=$error msg='$errMsg' lang=${lang.localeTag} duration=${durationMs}ms")
                isSessionActive = false

                // Controlled Single-Retry for regional languages or speech timeouts
                if (!hasRetried && (error == SpeechRecognizer.ERROR_NO_MATCH || error == SpeechRecognizer.ERROR_SPEECH_TIMEOUT || error == SpeechRecognizer.ERROR_CLIENT)) {
                    hasRetried = true
                    Log.i(TAG, "STT_RETRY: Attempting retry for language=${lang.localeTag}")
                    mainHandler.postDelayed({
                        startListeningInternal(isRetry = true)
                    }, 200)
                    return
                }

                _sttState.value = STTState.ERROR
                val meta = STTSessionMetadata(
                    requestedLanguage = lang,
                    actualLanguageTag = lang.localeTag,
                    startTimeMs = sessionStartTime,
                    durationMs = durationMs,
                    errorCode = error,
                    retryAttempted = hasRetried
                )
                onError(errMsg, meta)
            }

            override fun onResults(results: Bundle?) {
                val durationMs = SystemClock.elapsedRealtime() - sessionStartTime
                _sttState.value = STTState.SUCCESS
                isSessionActive = false

                val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                val text = matches?.firstOrNull()?.trim() ?: ""
                val textLen = text.length
                val lang = languageManager.currentLanguage.value
                
                Log.i(TAG, "STT_FINAL: Transcribed '${text}' (${textLen} chars, ${durationMs}ms, lang=${lang.localeTag})")

                val meta = STTSessionMetadata(
                    requestedLanguage = lang,
                    actualLanguageTag = lang.localeTag,
                    startTimeMs = sessionStartTime,
                    durationMs = durationMs,
                    textLength = textLen,
                    retryAttempted = hasRetried
                )

                if (text.isNotBlank()) {
                    onResult(text, meta)
                } else {
                    _sttState.value = STTState.IDLE
                }
            }

            override fun onPartialResults(partialResults: Bundle?) {
                val matches = partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                val text = matches?.firstOrNull() ?: ""
                if (text.isNotBlank()) {
                    _partialTranscript.value = text
                    Log.d(TAG, "STT_PARTIAL: '${text}'")
                }
            }

            override fun onEvent(eventType: Int, params: Bundle?) {}
        }
    }

    fun startListening() {
        mainHandler.post {
            hasRetried = false
            startListeningInternal(isRetry = false)
        }
    }

    private fun startListeningInternal(isRetry: Boolean) {
        // 1. Permission check
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            Log.e(TAG, "STT_ERROR: RECORD_AUDIO permission not granted")
            _sttState.value = STTState.ERROR
            onError("Microphone permission (RECORD_AUDIO) is required", STTSessionMetadata(
                requestedLanguage = languageManager.currentLanguage.value,
                actualLanguageTag = "unknown",
                startTimeMs = SystemClock.elapsedRealtime(),
                errorCode = SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS
            ))
            return
        }

        // 2. Prevent concurrent / overlapping sessions
        if (isSessionActive) {
            Log.w(TAG, "STT_WARN: Session already active, resetting recognizer before restart")
            try {
                speechRecognizer?.cancel()
            } catch (e: Exception) {
                Log.w(TAG, "Error cancelling previous session: ${e.message}")
            }
            isSessionActive = false
        }

        if (speechRecognizer == null) {
            initRecognizer()
        }

        val targetLang = languageManager.currentLanguage.value
        val targetLocale = targetLang.toLocale()

        _partialTranscript.value = ""
        _sttState.value = STTState.LISTENING
        isSessionActive = true
        sessionStartTime = SystemClock.elapsedRealtime()

        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, targetLocale.toLanguageTag())
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE, targetLocale.toLanguageTag())
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 3)
            putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, context.packageName)
            putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, false)
            putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS, 1500L)
            putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS, 1200L)
            putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_MINIMUM_LENGTH_MILLIS, 500L)
        }

        Log.i(TAG, "STT_START: SpeechRecognizer.startListening() initiated for ${targetLang.displayName} (${targetLocale.toLanguageTag()})")

        try {
            speechRecognizer?.startListening(intent)
        } catch (e: Exception) {
            Log.e(TAG, "STT_ERROR: startListening threw exception: ${e.message}")
            isSessionActive = false
            _sttState.value = STTState.ERROR
            onError(e.message ?: "STT failed to start", STTSessionMetadata(
                requestedLanguage = targetLang,
                actualLanguageTag = targetLang.localeTag,
                startTimeMs = sessionStartTime,
                errorCode = SpeechRecognizer.ERROR_CLIENT
            ))
        }
    }

    fun stopListening() {
        mainHandler.post {
            try {
                speechRecognizer?.stopListening()
                _sttState.value = STTState.PROCESSING
                Log.i(TAG, "STT_STOP: stopListening called.")
            } catch (e: Exception) {
                Log.w(TAG, "STT_WARN: stopListening error: ${e.message}")
            }
        }
    }

    fun cancel() {
        mainHandler.post {
            try {
                speechRecognizer?.cancel()
                isSessionActive = false
                _sttState.value = STTState.IDLE
                Log.i(TAG, "STT_CANCEL: Session cancelled.")
            } catch (e: Exception) {
                Log.w(TAG, "STT_WARN: cancel error: ${e.message}")
            }
        }
    }

    fun destroy() {
        mainHandler.post {
            try {
                isSessionActive = false
                speechRecognizer?.destroy()
                speechRecognizer = null
                _sttState.value = STTState.IDLE
                Log.i(TAG, "STT_DESTROY: Recognizer destroyed.")
            } catch (e: Exception) {
                Log.w(TAG, "STT_WARN: destroy error: ${e.message}")
            }
        }
    }

    private fun getErrorMessage(errorCode: Int): String {
        return when (errorCode) {
            SpeechRecognizer.ERROR_AUDIO -> "Audio recording error (check microphone)"
            SpeechRecognizer.ERROR_CLIENT -> "Client side error"
            SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "Microphone permission required"
            SpeechRecognizer.ERROR_NETWORK -> "Network error (speech recognition service unreachable)"
            SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> "Network timeout"
            SpeechRecognizer.ERROR_NO_MATCH -> "No speech recognized. Please try speaking clearly."
            SpeechRecognizer.ERROR_RECOGNIZER_BUSY -> "Speech recognizer is busy"
            SpeechRecognizer.ERROR_SERVER -> "Recognition server error"
            SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "No speech input detected"
            else -> "Speech recognition error (Code: $errorCode)"
        }
    }
}

