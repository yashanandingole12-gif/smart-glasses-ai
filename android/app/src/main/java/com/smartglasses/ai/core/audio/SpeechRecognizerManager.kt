package com.smartglasses.ai.core.audio

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.media.AudioDeviceInfo
import android.media.AudioManager
import android.os.Build
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
    private val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as? AudioManager
    private var speechRecognizer: SpeechRecognizer? = null
    private var isSessionActive = false
    private var sessionStartTime = 0L
    private var hasRetried = false
    private var isBluetoothScoActive = false

    private val _sttState = MutableStateFlow(STTState.IDLE)
    val sttState: StateFlow<STTState> = _sttState.asStateFlow()

    private val _partialTranscript = MutableStateFlow("")
    val partialTranscript: StateFlow<String> = _partialTranscript.asStateFlow()

    private val _audioRms = MutableStateFlow(0f)
    val audioRms: StateFlow<Float> = _audioRms.asStateFlow()

    init {
        mainHandler.post {
            ensureRecognizerInitialized()
        }
    }

    private fun ensureRecognizerInitialized(): SpeechRecognizer? {
        if (speechRecognizer != null) return speechRecognizer

        return try {
            SpeechRecognizer.createSpeechRecognizer(context).also { recognizer ->
                recognizer.setRecognitionListener(createRecognitionListener())
                speechRecognizer = recognizer
                Log.i(TAG, "STT_INIT: SpeechRecognizer initialized and ready.")
            }
        } catch (e: Exception) {
            Log.e(TAG, "STT_ERROR: Failed to initialize SpeechRecognizer (${e.message})")
            _sttState.value = STTState.ERROR
            null
        }
    }

    private fun recreateRecognizer() {
        try {
            speechRecognizer?.destroy()
        } catch (e: Exception) {
            Log.w(TAG, "Error cleaning previous SpeechRecognizer: ${e.message}")
        }
        speechRecognizer = null
        ensureRecognizerInitialized()
    }

    private fun configureAudioRouting() {
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && audioManager != null) {
                val availableDevices = audioManager.availableCommunicationDevices
                val twsDevice = availableDevices.firstOrNull {
                    it.type == AudioDeviceInfo.TYPE_BLE_HEADSET ||
                    it.type == AudioDeviceInfo.TYPE_BLUETOOTH_SCO ||
                    it.type == AudioDeviceInfo.TYPE_BLUETOOTH_A2DP
                }
                if (twsDevice != null) {
                    audioManager.setCommunicationDevice(twsDevice)
                    isBluetoothScoActive = true
                    Log.d(TAG, "STT_AUDIO: Routed to communication device: ${twsDevice.productName}")
                }
            } else if (audioManager?.isBluetoothScoAvailableOffCall == true && !isBluetoothScoActive) {
                audioManager.startBluetoothSco()
                audioManager.isBluetoothScoOn = true
                isBluetoothScoActive = true
                Log.d(TAG, "STT_AUDIO: Bluetooth SCO audio input enabled.")
            }
        } catch (e: Exception) {
            Log.w(TAG, "STT_AUDIO: Notice during audio routing configuration: ${e.message}")
        }
    }

    private fun releaseAudioRouting() {
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && audioManager != null) {
                audioManager.clearCommunicationDevice()
            } else if (isBluetoothScoActive) {
                audioManager?.stopBluetoothSco()
                audioManager?.isBluetoothScoOn = false
            }
            isBluetoothScoActive = false
        } catch (e: Exception) {
            Log.w(TAG, "STT_AUDIO: Notice during audio routing release: ${e.message}")
        }
    }

    private fun createRecognitionListener(): RecognitionListener {
        return object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {
                _sttState.value = STTState.LISTENING
                val lang = languageManager.currentLanguage.value
                Log.i(TAG, "STT_READY: Listening for speech input... (${lang.localeTag})")
            }

            override fun onBeginningOfSpeech() {
                _sttState.value = STTState.LISTENING
                Log.i(TAG, "STT_START: User started speaking")
            }

            override fun onRmsChanged(rmsdB: Float) {
                _audioRms.value = rmsdB
            }

            override fun onBufferReceived(buffer: ByteArray?) {}

            override fun onEndOfSpeech() {
                _sttState.value = STTState.PROCESSING
                Log.i(TAG, "STT_STOP: User finished speaking, transcribing...")
            }

            override fun onError(error: Int) {
                val durationMs = SystemClock.elapsedRealtime() - sessionStartTime
                val lang = languageManager.currentLanguage.value
                val errMsg = getErrorMessage(error)

                Log.w(TAG, "STT_ERROR: code=$error msg='$errMsg' duration=${durationMs}ms")
                isSessionActive = false

                // Recreate recognizer if client/busy error corrupted binder
                if (error == SpeechRecognizer.ERROR_RECOGNIZER_BUSY || error == SpeechRecognizer.ERROR_CLIENT) {
                    recreateRecognizer()
                }

                _sttState.value = STTState.IDLE
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

                Log.i(TAG, "STT_FINAL: Transcribed '${text}' (${durationMs}ms)")

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
                }
            }

            override fun onEvent(eventType: Int, params: Bundle?) {}
        }
    }

    fun startListening() {
        mainHandler.post {
            hasRetried = false
            startListeningInternal()
        }
    }

    private fun startListeningInternal() {
        // 1. Permission check
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            Log.e(TAG, "STT_ERROR: RECORD_AUDIO permission missing")
            _sttState.value = STTState.ERROR
            onError("Microphone permission required", STTSessionMetadata(
                requestedLanguage = languageManager.currentLanguage.value,
                actualLanguageTag = "unknown",
                startTimeMs = SystemClock.elapsedRealtime(),
                errorCode = SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS
            ))
            return
        }

        val recognizer = ensureRecognizerInitialized()
        if (recognizer == null) {
            Log.e(TAG, "STT_ERROR: SpeechRecognizer instance unavailable.")
            _sttState.value = STTState.ERROR
            return
        }

        // Cancel previous active session if any
        if (isSessionActive) {
            try {
                recognizer.cancel()
            } catch (e: Exception) {
                Log.w(TAG, "Cancel previous session notice: ${e.message}")
            }
            isSessionActive = false
        }

        configureAudioRouting()

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
        }

        Log.i(TAG, "STT_START: startListening() initiated for ${targetLocale.toLanguageTag()}")

        try {
            recognizer.startListening(intent)
        } catch (e: Exception) {
            Log.e(TAG, "STT_ERROR: startListening failed: ${e.message}")
            isSessionActive = false
            _sttState.value = STTState.IDLE
            recreateRecognizer()
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
            } catch (e: Exception) {
                Log.w(TAG, "stopListening notice: ${e.message}")
            }
        }
    }

    fun cancel() {
        mainHandler.post {
            try {
                speechRecognizer?.cancel()
            } catch (e: Exception) {
                Log.w(TAG, "cancel notice: ${e.message}")
            }
            isSessionActive = false
            _sttState.value = STTState.IDLE
        }
    }

    fun destroy() {
        mainHandler.post {
            try {
                isSessionActive = false
                releaseAudioRouting()
                speechRecognizer?.destroy()
                speechRecognizer = null
                _sttState.value = STTState.IDLE
            } catch (e: Exception) {
                Log.w(TAG, "destroy notice: ${e.message}")
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
