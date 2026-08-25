package com.smartglasses.ai.presentation.home

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.smartglasses.ai.core.audio.AndroidTTSState
import com.smartglasses.ai.core.audio.STTState
import com.smartglasses.ai.core.audio.SpeechRecognizerManager
import com.smartglasses.ai.core.audio.TextToSpeechManager
import com.smartglasses.ai.core.bluetooth.BleManager
import com.smartglasses.ai.core.location.AndroidLocationProvider
import com.smartglasses.ai.core.network.BackendConfig
import com.smartglasses.ai.data.repositories.AssistantRepositoryImpl
import com.smartglasses.ai.domain.models.AssistantState
import com.smartglasses.ai.domain.models.ChatMessage
import com.smartglasses.ai.domain.models.IntegrationState
import com.smartglasses.ai.domain.models.WearableTelemetry
import com.smartglasses.ai.domain.usecases.SendVoiceQueryUseCase
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class WearableHomeViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = AssistantRepositoryImpl()
    private val sendVoiceQueryUseCase = SendVoiceQueryUseCase(repository)

    private val locationProvider = AndroidLocationProvider(application)
    private val bleManager = BleManager(application)

    private var speechRecognizerManager: SpeechRecognizerManager? = null
    private val textToSpeechManager = TextToSpeechManager(application)

    private val sessionId = UUID.randomUUID().toString()

    private val _uiState = MutableStateFlow(
        WearableHomeState(
            serverUrl = BackendConfig.getBaseUrl(),
            currentTime = getCurrentFormattedTime(),
            period = calculateTimePeriod()
        )
    )
    val uiState: StateFlow<WearableHomeState> = _uiState.asStateFlow()

    init {
        initSpeechRecognizer()
        observeTelemetry()
        refreshAllStatuses()
    }

    private fun initSpeechRecognizer() {
        speechRecognizerManager = SpeechRecognizerManager(
            context = getApplication(),
            onResult = { transcript ->
                handleUserVoiceInput(transcript)
            },
            onError = { errMsg ->
                _uiState.update {
                    it.copy(
                        assistantState = AssistantState.IDLE,
                        errorMessage = errMsg
                    )
                }
            }
        )

        // Observe STT state
        viewModelScope.launch {
            speechRecognizerManager?.sttState?.collect { stt ->
                when (stt) {
                    STTState.LISTENING -> _uiState.update { it.copy(assistantState = AssistantState.LISTENING) }
                    STTState.PROCESSING -> _uiState.update { it.copy(assistantState = AssistantState.PROCESSING) }
                    STTState.IDLE -> {
                        if (_uiState.value.assistantState == AssistantState.LISTENING) {
                            _uiState.update { it.copy(assistantState = AssistantState.IDLE) }
                        }
                    }
                    STTState.ERROR -> _uiState.update { it.copy(assistantState = AssistantState.ERROR) }
                }
            }
        }

        // Observe partial transcripts
        viewModelScope.launch {
            speechRecognizerManager?.partialTranscript?.collect { partial ->
                _uiState.update { it.copy(partialVoiceTranscript = partial) }
            }
        }

        // Observe TTS state
        viewModelScope.launch {
            textToSpeechManager.ttsState.collect { tts ->
                when (tts) {
                    AndroidTTSState.SPEAKING -> _uiState.update { it.copy(assistantState = AssistantState.SPEAKING) }
                    AndroidTTSState.COMPLETED, AndroidTTSState.READY -> {
                        if (_uiState.value.assistantState == AssistantState.SPEAKING) {
                            _uiState.update { it.copy(assistantState = AssistantState.IDLE) }
                        }
                    }
                    else -> {}
                }
            }
        }
    }

    private fun observeTelemetry() {
        // Observe BLE connection and battery
        viewModelScope.launch {
            bleManager.connectionState.collect { conn ->
                _uiState.update { it.copy(deviceConnectionState = conn) }
            }
        }

        viewModelScope.launch {
            bleManager.batteryLevel.collect { bat ->
                _uiState.update { it.copy(batteryPercentage = bat) }
            }
        }

        // Observe Location
        viewModelScope.launch {
            locationProvider.locationState.collect { loc ->
                _uiState.update {
                    it.copy(
                        locationAvailable = loc.isAvailable,
                        locationName = loc.city
                    )
                }
            }
        }

        // Periodic clock update and backend status polling
        viewModelScope.launch(Dispatchers.Default) {
            while (true) {
                val formattedTime = getCurrentFormattedTime()
                val period = calculateTimePeriod()
                _uiState.update {
                    it.copy(
                        currentTime = formattedTime,
                        period = period
                    )
                }
                refreshAllStatuses()
                kotlinx.coroutines.delay(10000)
            }
        }
    }

    fun refreshAllStatuses() {
        checkBackendHealth()
        checkGoogleStatus()
    }

    fun checkBackendHealth() {
        viewModelScope.launch {
            val result = repository.checkHealth()
            val isConnected = result.getOrDefault(false)
            _uiState.update {
                it.copy(
                    aiConnected = isConnected,
                    llmConnected = isConnected
                )
            }
        }
    }

    fun checkGoogleStatus() {
        viewModelScope.launch {
            val result = repository.checkGoogleAuthStatus()
            if (result.isSuccess) {
                val (connected, email) = result.getOrThrow()
                _uiState.update {
                    it.copy(
                        googleConnected = connected,
                        googleEmail = email,
                        gmailStatus = if (connected) IntegrationState.CONNECTED else IntegrationState.DISCONNECTED
                    )
                }
            } else {
                _uiState.update {
                    it.copy(
                        googleConnected = false,
                        gmailStatus = IntegrationState.DISCONNECTED
                    )
                }
            }
        }
    }

    fun checkGmail() {
        handleUserVoiceInput("Check my email.")
    }

    fun onTalkButtonClicked() {
        if (_uiState.value.assistantState == AssistantState.LISTENING) {
            speechRecognizerManager?.stopListening()
        } else {
            textToSpeechManager.stop()
            _uiState.update {
                it.copy(
                    assistantState = AssistantState.LISTENING,
                    partialVoiceTranscript = "",
                    errorMessage = null
                )
            }
            speechRecognizerManager?.startListening()
        }
    }

    fun handleUserVoiceInput(message: String) {
        if (message.isBlank()) return

        val userChat = ChatMessage(sender = "USER", text = message)
        _uiState.update {
            it.copy(
                assistantState = AssistantState.PROCESSING,
                partialVoiceTranscript = "",
                messages = it.messages + userChat
            )
        }

        viewModelScope.launch {
            val telemetry = WearableTelemetry(
                glassesConnected = _uiState.value.deviceConnectionState != com.smartglasses.ai.core.bluetooth.DeviceConnectionState.DISCONNECTED,
                batteryPercentage = _uiState.value.batteryPercentage,
                aiConnected = _uiState.value.aiConnected,
                locationAvailable = _uiState.value.locationAvailable,
                locationName = _uiState.value.locationName,
                timeFormatted = _uiState.value.currentTime,
                period = _uiState.value.period
            )

            val result = sendVoiceQueryUseCase(
                sessionId = sessionId,
                query = message,
                telemetry = telemetry
            )

            result.onSuccess { resp ->
                val assistantChat = ChatMessage(
                    sender = "ASSISTANT",
                    text = resp.text,
                    requiresConfirmation = resp.requiresConfirmation
                )

                _uiState.update {
                    it.copy(
                        assistantState = AssistantState.SPEAKING,
                        latestSpeech = resp.text,
                        messages = it.messages + assistantChat,
                        pendingConfirmation = if (resp.requiresConfirmation) resp else null,
                        aiConnected = true,
                        llmConnected = true
                    )
                }

                // Speak via native Android TTS
                textToSpeechManager.speak(resp.text) {
                    _uiState.update { it.copy(assistantState = AssistantState.IDLE) }
                }
            }.onFailure { err ->
                val fallbackText = "Backend error: ${err.localizedMessage ?: "Could not reach backend"}"
                _uiState.update {
                    it.copy(
                        assistantState = AssistantState.ERROR,
                        latestSpeech = fallbackText,
                        errorMessage = err.localizedMessage,
                        aiConnected = false,
                        llmConnected = false
                    )
                }
            }
        }
    }

    fun toggleDeviceConnectionMode() {
        bleManager.toggleConnectionMode()
    }

    fun openConfigDialog() {
        _uiState.update { it.copy(isConfigDialogOpen = true) }
    }

    fun closeConfigDialog() {
        _uiState.update { it.copy(isConfigDialogOpen = false) }
    }

    fun updateServerUrl(newUrl: String) {
        BackendConfig.setBaseUrl(newUrl)
        _uiState.update { it.copy(serverUrl = BackendConfig.getBaseUrl()) }
        refreshAllStatuses()
    }

    fun testBackendConnection(url: String, callback: (Boolean, String) -> Unit) {
        viewModelScope.launch {
            val normalized = BackendConfig.normalizeUrl(url)
            val prev = BackendConfig.getBaseUrl()
            BackendConfig.setBaseUrl(normalized)
            val result = repository.checkHealth()
            if (result.isSuccess && result.getOrNull() == true) {
                _uiState.update { it.copy(serverUrl = normalized, aiConnected = true, llmConnected = true) }
                checkGoogleStatus()
                callback(true, "Connected successfully!")
            } else {
                BackendConfig.setBaseUrl(prev)
                callback(false, result.exceptionOrNull()?.localizedMessage ?: "Failed to connect")
            }
        }
    }

    private fun getCurrentFormattedTime(): String {
        val sdf = SimpleDateFormat("hh:mm a", Locale.getDefault())
        return sdf.format(Date())
    }

    private fun calculateTimePeriod(): String {
        val hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY)
        return when (hour) {
            in 5..11 -> "morning"
            in 12..16 -> "afternoon"
            in 17..21 -> "evening"
            else -> "night"
        }
    }

    override fun onCleared() {
        super.onCleared()
        speechRecognizerManager?.destroy()
        textToSpeechManager.shutdown()
    }
}
