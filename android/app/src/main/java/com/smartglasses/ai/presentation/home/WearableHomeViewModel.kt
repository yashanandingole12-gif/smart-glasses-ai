package com.smartglasses.ai.presentation.home

import android.app.Application
import android.os.SystemClock
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.smartglasses.ai.core.audio.AndroidTTSState
import com.smartglasses.ai.core.audio.STTState
import com.smartglasses.ai.core.audio.SpeechRecognizerManager
import com.smartglasses.ai.core.audio.TextToSpeechManager
import com.smartglasses.ai.core.bluetooth.BleManager
import com.smartglasses.ai.core.device.AndroidBatteryProvider
import com.smartglasses.ai.core.location.AndroidLocationProvider
import com.smartglasses.ai.core.network.BackendConfig
import com.smartglasses.ai.core.network.ConnectionState
import com.smartglasses.ai.core.network.NetworkDiagnostics
import com.smartglasses.ai.core.permissions.PermissionManager
import com.smartglasses.ai.core.ai.LocalAiEngine
import com.smartglasses.ai.data.repositories.AssistantRepositoryImpl
import com.smartglasses.ai.domain.models.AiAvailabilityState
import com.smartglasses.ai.domain.models.AssistantState
import com.smartglasses.ai.domain.models.ChatMessage
import com.smartglasses.ai.domain.models.FailureCategory
import com.smartglasses.ai.domain.models.IntegrationState
import com.smartglasses.ai.domain.models.ResponseSource
import com.smartglasses.ai.domain.models.WearableTelemetry
import com.smartglasses.ai.domain.usecases.AIResponseRouter
import com.smartglasses.ai.domain.usecases.LocalDeterministicResolver
import com.smartglasses.ai.domain.usecases.SendVoiceQueryUseCase
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class WearableHomeViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = AssistantRepositoryImpl()
    private val sendVoiceQueryUseCase = SendVoiceQueryUseCase(repository)
    private val deterministicResolver = LocalDeterministicResolver()
    private val localAiEngine = LocalAiEngine(application)
    private val responseRouter = AIResponseRouter(repository, deterministicResolver, localAiEngine, application)

    private val batteryProvider = AndroidBatteryProvider(application)
    private val locationProvider = AndroidLocationProvider(application)
    private val bleManager = BleManager(application)

    private var speechRecognizerManager: SpeechRecognizerManager? = null
    private val textToSpeechManager = TextToSpeechManager(application)

    private val sessionId = UUID.randomUUID().toString()

    // Section 4 & 17: Connection State Machine & Active In-Flight Job
    private var consecutiveFailures = 0
    private val latencyHistory = mutableListOf<Double>()
    private var totalRequestsCount = 0
    private var failedRequestsCount = 0
    private var currentAssistantJob: Job? = null

    private val _uiState = MutableStateFlow(
        WearableHomeState(
            serverUrl = BackendConfig.getBaseUrl(),
            currentTime = getCurrentFormattedTime(),
            period = calculateTimePeriod(),
            isMicrophoneReady = PermissionManager.hasAudioPermission(application),
            connectionState = ConnectionState.CONNECTING,
            aiAvailabilityState = AiAvailabilityState.CLOUD_AVAILABLE,
            networkDiagnostics = NetworkDiagnostics(
                backendUrl = BackendConfig.getBaseUrl(),
                connectionState = ConnectionState.CONNECTING
            )
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
            onResult = { transcript, metadata ->
                _uiState.update { it.copy(sttDurationMs = metadata.durationMs) }
                handleUserVoiceInput(transcript, metadata.actualLanguageTag)
            },
            onError = { errMsg, metadata ->
                _uiState.update {
                    it.copy(
                        assistantState = AssistantState.IDLE,
                        errorMessage = errMsg,
                        sttDurationMs = metadata.durationMs
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
                    STTState.SUCCESS -> {}
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
                    AndroidTTSState.READY -> _uiState.update { it.copy(isTtsReady = true) }
                    AndroidTTSState.SPEAKING -> _uiState.update { it.copy(assistantState = AssistantState.SPEAKING) }
                    AndroidTTSState.COMPLETED -> {
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
        // 1. Real Device Battery
        viewModelScope.launch {
            batteryProvider.batteryLevel.collect { bat ->
                _uiState.update { it.copy(batteryPercentage = bat) }
            }
        }
        viewModelScope.launch {
            batteryProvider.isCharging.collect { charging ->
                _uiState.update { it.copy(isCharging = charging) }
            }
        }

        // 2. Real Device Location
        viewModelScope.launch {
            locationProvider.locationState.collect { loc ->
                _uiState.update {
                    it.copy(
                        locationAvailable = loc.isAvailable,
                        locationName = loc.city,
                        latitude = loc.latitude,
                        longitude = loc.longitude
                    )
                }
            }
        }

        // 3. Bluetooth Glasses State
        viewModelScope.launch {
            bleManager.connectionState.collect { bleState ->
                _uiState.update { it.copy(deviceConnectionState = bleState) }
            }
        }

        // 4. Section 5: Periodic clock update & lightweight background health polling (every 15s)
        viewModelScope.launch(Dispatchers.Default) {
            while (true) {
                val formattedTime = getCurrentFormattedTime()
                val period = calculateTimePeriod()
                val micReady = PermissionManager.hasAudioPermission(getApplication())
                _uiState.update {
                    it.copy(
                        currentTime = formattedTime,
                        period = period,
                        isMicrophoneReady = micReady
                    )
                }
                checkBackendHealth()
                delay(15000)
            }
        }
    }

    fun refreshAllStatuses() {
        checkBackendHealth()
        checkGoogleStatus()
        viewModelScope.launch {
            locationProvider.refreshLocation()
        }
    }

    // Section 4 & 5: Health Check with 4-State Machine (CONNECTED, CONNECTING, DEGRADED, DISCONNECTED)
    fun checkBackendHealth() {
        viewModelScope.launch {
            val t0 = SystemClock.elapsedRealtime()
            val result = repository.checkHealth()
            val dur = (SystemClock.elapsedRealtime() - t0).toDouble()
            if (result.isSuccess && result.getOrDefault(false)) {
                handleConnectionSuccess(dur)
            } else {
                val reason = result.exceptionOrNull()?.localizedMessage ?: "Health check failed"
                handleConnectionFailure(reason)
            }
        }
    }

    private fun handleConnectionSuccess(latencyMs: Double) {
        consecutiveFailures = 0
        totalRequestsCount++
        latencyHistory.add(latencyMs)
        if (latencyHistory.size > 50) latencyHistory.removeAt(0)

        val sorted = latencyHistory.sorted()
        val avg = latencyHistory.average()
        val p95Index = (sorted.size * 0.95).toInt().coerceAtMost(sorted.size - 1)
        val p95 = if (sorted.isNotEmpty()) sorted[p95Index] else latencyMs
        val min = sorted.firstOrNull() ?: latencyMs
        val max = sorted.lastOrNull() ?: latencyMs

        val timeStr = SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())

        val diag = NetworkDiagnostics(
            backendUrl = BackendConfig.getBaseUrl(),
            connectionState = ConnectionState.CONNECTED,
            lastSuccessfulRequestTime = timeStr,
            lastFailureReason = null,
            lastLatencyMs = latencyMs,
            averageLatencyMs = avg,
            p95LatencyMs = p95,
            minLatencyMs = min,
            maxLatencyMs = max,
            totalRequests = totalRequestsCount,
            failedRequests = failedRequestsCount
        )

        _uiState.update {
            it.copy(
                connectionState = ConnectionState.CONNECTED,
                aiConnected = true,
                llmConnected = true,
                networkDiagnostics = diag
            )
        }
    }

    private fun handleConnectionFailure(reason: String) {
        consecutiveFailures++
        totalRequestsCount++
        failedRequestsCount++

        val nextState = if (consecutiveFailures < 3) {
            ConnectionState.DEGRADED
        } else {
            ConnectionState.DISCONNECTED
        }

        val diag = _uiState.value.networkDiagnostics.copy(
            backendUrl = BackendConfig.getBaseUrl(),
            connectionState = nextState,
            lastFailureReason = reason,
            totalRequests = totalRequestsCount,
            failedRequests = failedRequestsCount
        )

        _uiState.update {
            it.copy(
                connectionState = nextState,
                aiConnected = nextState != ConnectionState.DISCONNECTED,
                networkDiagnostics = diag
            )
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
                        gmailStatus = if (connected) IntegrationState.CONNECTED else IntegrationState.DISCONNECTED,
                        calendarStatus = if (connected) IntegrationState.CONNECTED else IntegrationState.DISCONNECTED
                    )
                }
            } else {
                _uiState.update {
                    it.copy(
                        googleConnected = false,
                        gmailStatus = IntegrationState.DISCONNECTED,
                        calendarStatus = IntegrationState.DISCONNECTED
                    )
                }
            }
        }
    }

    fun checkGmail() {
        sendTextMessage("Check my email.")
    }

    fun fetchTodayEvents() {
        sendTextMessage("What do I have today?")
    }

    fun fetchNextEvent() {
        sendTextMessage("What's my next event?")
    }

    fun readRecentSms() {
        sendTextMessage("Read my recent messages.")
    }

    fun confirmPendingAction() {
        val pending = _uiState.value.pendingConfirmation ?: return
        val actionId = pending.confirmationActionId
        _uiState.update { it.copy(pendingConfirmation = null) }
        executeAssistantQuery(
            message = "Confirm",
            language = "auto",
            locale = Locale.getDefault().toLanguageTag(),
            confirmedAction = true,
            confirmedActionId = actionId
        )
    }

    fun cancelPendingAction() {
        _uiState.update {
            it.copy(
                pendingConfirmation = null,
                latestSpeech = "Action cancelled.",
                assistantState = AssistantState.IDLE
            )
        }
    }

    fun onTalkButtonClicked() {
        if (!PermissionManager.hasAudioPermission(getApplication())) {
            _uiState.update {
                it.copy(
                    errorMessage = "Microphone permission is required.",
                    isMicrophoneReady = false
                )
            }
            return
        }

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

    fun onTextInputChanged(newText: String) {
        _uiState.update { it.copy(textInput = newText) }
    }

    fun sendTextMessage(query: String? = null) {
        val message = (query ?: _uiState.value.textInput).trim()
        if (message.isBlank()) return

        _uiState.update { it.copy(textInput = "", isSendingText = true) }
        executeAssistantQuery(message = message, language = "auto", locale = Locale.getDefault().toLanguageTag())
    }

    private fun handleUserVoiceInput(transcript: String, languageTag: String) {
        if (transcript.isBlank()) return
        executeAssistantQuery(message = transcript, language = languageTag, locale = languageTag)
    }

    // Section 17 & Phase 3B.6: Response Routing, TTFA Streaming, & Fast Preemption
    private fun executeAssistantQuery(
        message: String,
        language: String,
        locale: String,
        confirmedAction: Boolean? = null,
        confirmedActionId: String? = null
    ) {
        // Cancel in-flight assistant request if user speaks again
        currentAssistantJob?.cancel()

        val userChat = ChatMessage(sender = "USER", text = message)
        val reqId = UUID.randomUUID().toString()

        _uiState.update {
            it.copy(
                assistantState = AssistantState.PROCESSING,
                partialVoiceTranscript = "",
                messages = it.messages + userChat,
                activeRequestId = reqId
            )
        }

        currentAssistantJob = viewModelScope.launch {
            val telemetry = WearableTelemetry(
                glassesConnected = _uiState.value.deviceConnectionState != com.smartglasses.ai.core.bluetooth.DeviceConnectionState.DISCONNECTED,
                batteryPercentage = _uiState.value.batteryPercentage,
                aiConnected = _uiState.value.aiConnected,
                locationAvailable = _uiState.value.locationAvailable,
                locationName = _uiState.value.locationName,
                latitude = _uiState.value.latitude,
                longitude = _uiState.value.longitude,
                timeFormatted = _uiState.value.currentTime,
                period = _uiState.value.period,
                timezone = TimeZone.getDefault().id,
                locale = locale
            )

            val tStart = SystemClock.elapsedRealtime()
            try {
                val resp = responseRouter.routeQuery(
                    sessionId = sessionId,
                    query = message,
                    telemetry = telemetry,
                    connectionState = _uiState.value.connectionState,
                    confirmedAction = confirmedAction,
                    confirmedActionId = confirmedActionId,
                    language = language,
                    locale = locale,
                    onAiStateChanged = { newAiState ->
                        _uiState.update {
                            it.copy(
                                aiAvailabilityState = newAiState,
                                activeAiProvider = when (newAiState) {
                                    AiAvailabilityState.CLOUD_AVAILABLE -> "Gemini Flash"
                                    AiAvailabilityState.LOCAL_ONLY -> "On-Device SLM"
                                    AiAvailabilityState.USING_LOCAL_AI -> "Local AI (Fallback)"
                                    AiAvailabilityState.CLOUD_DEGRADED -> "Cloud Degraded"
                                }
                            )
                        }
                    }
                )

                val durationMs = (SystemClock.elapsedRealtime() - tStart).toDouble()

                if (resp.source == ResponseSource.CLOUD_GEMINI || resp.source == ResponseSource.CLOUD_SECONDARY) {
                    handleConnectionSuccess(durationMs)
                }

                val assistantChat = ChatMessage(
                    sender = "ASSISTANT",
                    text = resp.text,
                    requiresConfirmation = resp.requiresConfirmation,
                    confirmationActionId = resp.confirmationActionId,
                    latencyMs = resp.latencyMs.takeIf { it > 0.0 } ?: durationMs,
                    failureCategory = resp.failureCategory,
                    source = resp.source,
                    unifiedSource = resp.unifiedSource,
                    capabilityStatus = resp.capabilityStatus
                )

                _uiState.update {
                    it.copy(
                        assistantState = AssistantState.RESPONDING,
                        latestSpeech = resp.text,
                        messages = it.messages + assistantChat,
                        pendingConfirmation = if (resp.requiresConfirmation) resp else null,
                        lastResponseLatencyMs = resp.latencyMs.takeIf { lat -> lat > 0.0 } ?: durationMs,
                        isSendingText = false
                    )
                }

                // Section 10 & 13: Voice playback transition & TTFA tracking
                val ttsStart = SystemClock.elapsedRealtime()
                val ttfa = SystemClock.elapsedRealtime() - tStart
                _uiState.update { it.copy(timeToFirstAudioMs = ttfa) }

                textToSpeechManager.speak(resp.text) {
                    val ttsDur = SystemClock.elapsedRealtime() - ttsStart
                    _uiState.update {
                        it.copy(
                            assistantState = AssistantState.IDLE,
                            ttsDurationMs = ttsDur
                        )
                    }
                }
            } catch (e: CancellationException) {
                // Request was safely cancelled by subsequent user action
                _uiState.update { it.copy(assistantState = AssistantState.IDLE, isSendingText = false) }
            } catch (e: Exception) {
                val durationMs = (SystemClock.elapsedRealtime() - tStart).toDouble()
                val errorMsg = "Error: ${e.localizedMessage ?: "Could not complete request"}"
                val assistantChat = ChatMessage(
                    sender = "ASSISTANT",
                    text = errorMsg,
                    latencyMs = durationMs,
                    failureCategory = FailureCategory.NETWORK_FAILURE
                )
                _uiState.update {
                    it.copy(
                        assistantState = AssistantState.ERROR,
                        latestSpeech = errorMsg,
                        errorMessage = e.localizedMessage,
                        messages = it.messages + assistantChat,
                        isSendingText = false,
                        lastResponseLatencyMs = durationMs
                    )
                }
            }
        }
    }

    fun toggleDiagnostics() {
        _uiState.update { it.copy(showDiagnostics = !it.showDiagnostics) }
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
            _uiState.update { it.copy(connectionState = ConnectionState.CONNECTING) }
            val normalized = BackendConfig.normalizeUrl(url)
            val prev = BackendConfig.getBaseUrl()
            BackendConfig.setBaseUrl(normalized)
            val t0 = SystemClock.elapsedRealtime()
            val result = repository.checkHealth()
            val dur = (SystemClock.elapsedRealtime() - t0).toDouble()

            if (result.isSuccess && result.getOrNull() == true) {
                handleConnectionSuccess(dur)
                _uiState.update { it.copy(serverUrl = normalized) }
                checkGoogleStatus()
                callback(true, "Connected successfully!")
            } else {
                BackendConfig.setBaseUrl(prev)
                val err = result.exceptionOrNull()?.localizedMessage ?: "Backend is unavailable."
                handleConnectionFailure(err)
                callback(false, err)
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
        currentAssistantJob?.cancel()
        batteryProvider.unregister()
        speechRecognizerManager?.destroy()
        textToSpeechManager.shutdown()
    }
}
