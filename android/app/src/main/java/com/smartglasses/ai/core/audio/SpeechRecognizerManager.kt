package com.smartglasses.ai.core.audio

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
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
        initRecognizer()
    }

    @Synchronized
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
                Log.i(TAG, "STT_READY: language=${lang.localeTag} timestamp=${System.currentTimeMillis()}")
            }

            override fun onBeginningOfSpeech() {
                _sttState.value = STTState.LISTENING
                Log.i(TAG, "STT_START: speech input detected")
            }

            override fun onRmsChanged(rmsdB: Float) {
                _audioRms.value = rmsdB
            }

            override fun onBufferReceived(buffer: ByteArray?) {}

            override fun onEndOfSpeech() {
                _sttState.value = STTState.PROCESSING
                Log.i(TAG, "STT_STOP: end of speech detected, processing results")
            }

            override fun onError(error: Int) {
                val durationMs = SystemClock.elapsedRealtime() - sessionStartTime
                val lang = languageManager.currentLanguage.value
                val errMsg = getErrorMessage(error)
                
                Log.w(TAG, "STT_ERROR: code=$error msg='$errMsg' lang=${lang.localeTag} duration=${durationMs}ms")
                isSessionActive = false

                // Controlled Single-Retry for Regional Languages on timeout or no match
                if (!hasRetried && (error == SpeechRecognizer.ERROR_NO_MATCH || error == SpeechRecognizer.ERROR_SPEECH_TIMEOUT)) {
                    hasRetried = true
                    Log.i(TAG, "STT_RETRY: Attempting controlled single retry for language=${lang.localeTag}")
                    startListeningInternal(isRetry = true)
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
                
                // Safe metadata log (do not print raw transcript in production)
                Log.i(TAG, "STT_FINAL: text_length=$textLen language=${lang.localeTag} duration=${durationMs}ms timestamp=${System.currentTimeMillis()}")

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
                    val lang = languageManager.currentLanguage.value
                    Log.d(TAG, "STT_PARTIAL: text_length=${text.length} language=${lang.localeTag} timestamp=${System.currentTimeMillis()}")
                }
            }

            override fun onEvent(eventType: Int, params: Bundle?) {}
        }
    }

    @Synchronized
    fun startListening() {
        hasRetried = false
        startListeningInternal(isRetry = false)
    }

    @Synchronized
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
            Log.w(TAG, "STT_WARN: Session already active, resetting recognizer before start")
            cancel()
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
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, context.packageName)
            // Enable offline / online hybrid recognition
            putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, false)
        }

        Log.i(TAG, "STT_START: requesting recognition for language=${targetLang.localeTag} (isRetry=$isRetry)")

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

    @Synchronized
    fun stopListening() {
        try {
            speechRecognizer?.stopListening()
            _sttState.value = STTState.PROCESSING
        } catch (e: Exception) {
            Log.w(TAG, "STT_WARN: stopListening error: ${e.message}")
        }
    }

    @Synchronized
    fun cancel() {
        try {
            speechRecognizer?.cancel()
            isSessionActive = false
            _sttState.value = STTState.IDLE
        } catch (e: Exception) {
            Log.w(TAG, "STT_WARN: cancel error: ${e.message}")
        }
    }

    @Synchronized
    fun destroy() {
        try {
            isSessionActive = false
            speechRecognizer?.destroy()
            speechRecognizer = null
            _sttState.value = STTState.IDLE
        } catch (e: Exception) {
            Log.w(TAG, "STT_WARN: destroy error: ${e.message}")
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
