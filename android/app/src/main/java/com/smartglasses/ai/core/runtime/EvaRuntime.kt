package com.smartglasses.ai.core.runtime

import android.content.Context
import android.util.Log
import com.smartglasses.ai.core.ai.LocalAiEngine
import com.smartglasses.ai.core.audio.AudioOutputRouter
import com.smartglasses.ai.core.audio.SpeechRecognizerManager
import com.smartglasses.ai.core.audio.TextToSpeechManager
import com.smartglasses.ai.core.context.EvaContext
import com.smartglasses.ai.core.context.EvaContextEngine
import com.smartglasses.ai.core.conversation.ConversationState
import com.smartglasses.ai.core.conversation.ConversationStateMachine
import com.smartglasses.ai.core.gateway.GlassesGateway
import com.smartglasses.ai.core.gateway.NoGlassesGateway
import com.smartglasses.ai.core.gateway.RealGlassesGateway
import com.smartglasses.ai.core.network.ConnectionState
import com.smartglasses.ai.data.repositories.AssistantRepositoryImpl
import com.smartglasses.ai.domain.models.ChatMessage
import com.smartglasses.ai.domain.models.ResponseSource
import com.smartglasses.ai.domain.models.WearableResponse
import com.smartglasses.ai.domain.models.WearableTelemetry
import com.smartglasses.ai.domain.usecases.AIResponseRouter
import com.smartglasses.ai.domain.usecases.LocalDeterministicResolver
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class EvaRuntimeState(
    val conversationState: ConversationState = ConversationState.IDLE,
    val context: EvaContext = EvaContext(),
    val messages: List<ChatMessage> = emptyList(),
    val latestSpeech: String = "",
    val partialTranscript: String = "",
    val isGlassesConnected: Boolean = false,
    val isMicrophoneActive: Boolean = false,
    val isSpeaking: Boolean = false,
    val activeRequestId: String? = null,
    val errorMessage: String? = null
)

class EvaRuntime private constructor(private val appContext: Context) {
    companion object {
        private const val TAG = "EVA.Runtime"

        @Volatile
        private var instance: EvaRuntime? = null

        fun getInstance(context: Context): EvaRuntime {
            return instance ?: synchronized(this) {
                instance ?: EvaRuntime(context.applicationContext).also { instance = it }
            }
        }
    }

    val contextEngine = EvaContextEngine(appContext)
    val stateMachine = ConversationStateMachine()
    val audioRouter = AudioOutputRouter(appContext)
    val textToSpeechManager = TextToSpeechManager(appContext)
    private val repository = AssistantRepositoryImpl()
    private val deterministicResolver = LocalDeterministicResolver()
    private val localAiEngine = LocalAiEngine(appContext)
    val responseRouter = AIResponseRouter(repository, deterministicResolver, localAiEngine, appContext)

    var glassesGateway: GlassesGateway = RealGlassesGateway(appContext)
        private set

    private val scope = CoroutineScope(Dispatchers.Main)
    private var activeQueryJob: Job? = null

    private val _runtimeState = MutableStateFlow(EvaRuntimeState())
    val runtimeState: StateFlow<EvaRuntimeState> = _runtimeState.asStateFlow()

    var speechRecognizerManager: SpeechRecognizerManager? = null

    init {
        initSpeechRecognizer()
        observeComponents()
        Log.i(TAG, "EVA Runtime initialized as primary Android authority.")
    }

    private fun initSpeechRecognizer() {
        speechRecognizerManager = SpeechRecognizerManager(
            context = appContext,
            onResult = { transcript, metadata ->
                handleVoiceTranscript(transcript, metadata.actualLanguageTag)
            },
            onError = { errMsg, _ ->
                stateMachine.handleError(errMsg)
                _runtimeState.update { it.copy(errorMessage = errMsg) }
            }
        )
    }

    private fun observeComponents() {
        scope.launch {
            stateMachine.state.collect { st ->
                _runtimeState.update { it.copy(conversationState = st) }
            }
        }
        scope.launch {
            contextEngine.contextState.collect { ctx ->
                _runtimeState.update { it.copy(context = ctx) }
            }
        }
        scope.launch {
            glassesGateway.isConnected.collect { conn ->
                _runtimeState.update { it.copy(isGlassesConnected = conn) }
            }
        }
        scope.launch {
            speechRecognizerManager?.partialTranscript?.collect { partial ->
                _runtimeState.update { it.copy(partialTranscript = partial) }
            }
        }
    }

    fun startVoiceInteraction() {
        // Preempt any active speech or ongoing query
        interruptOutput()

        stateMachine.transitionTo(ConversationState.WAKE_DETECTED, "Voice wake trigger")
        stateMachine.transitionTo(ConversationState.LISTENING, "Listening for speech")

        _runtimeState.update {
            it.copy(
                isMicrophoneActive = true,
                partialTranscript = "",
                errorMessage = null
            )
        }
        speechRecognizerManager?.startListening()
    }

    fun stopVoiceInteraction() {
        speechRecognizerManager?.stopListening()
        stateMachine.transitionTo(ConversationState.TRANSCRIBING, "Voice capture ended")
        _runtimeState.update { it.copy(isMicrophoneActive = false) }
    }

    fun interruptOutput() {
        Log.i(TAG, "INTERRUPT: Cancelling in-flight query and halting audio output.")
        activeQueryJob?.cancel()
        activeQueryJob = null
        textToSpeechManager.stop()
        speechRecognizerManager?.cancel()
        stateMachine.stopConversation("Interruption by user")
        _runtimeState.update {
            it.copy(
                isSpeaking = false,
                isMicrophoneActive = false,
                errorMessage = null
            )
        }
    }

    private fun handleVoiceTranscript(transcript: String, languageTag: String) {
        if (transcript.isBlank()) {
            stateMachine.transitionTo(ConversationState.IDLE, "Blank transcript")
            return
        }

        // Check if user said "stop", "cancel", "shant raho"
        val lower = transcript.trim().lowercase()
        if (lower == "stop" || lower == "cancel" || lower == "pause" || lower == "chup" || lower == "shant") {
            interruptOutput()
            return
        }

        // Check for context-aware greeting
        if (lower.contains("good morning") || lower.contains("good afternoon") || lower.contains("good evening") || lower == "hey eva" || lower == "hello eva") {
            val greeting = contextEngine.generateContextAwareGreeting()
            deliverAssistantResponse(greeting, ResponseSource.LOCAL_DETERMINISTIC)
            return
        }

        executeQuery(transcript, languageTag)
    }

    fun executeQuery(query: String, languageTag: String = "auto") {
        activeQueryJob?.cancel()

        stateMachine.transitionTo(ConversationState.UNDERSTANDING, "Analyzing query: '$query'")

        val userMessage = ChatMessage(sender = "USER", text = query)
        _runtimeState.update {
            it.copy(
                messages = it.messages + userMessage,
                partialTranscript = ""
            )
        }

        activeQueryJob = scope.launch {
            val telemetry = WearableTelemetry(
                glassesConnected = _runtimeState.value.isGlassesConnected,
                batteryPercentage = _runtimeState.value.context.device.value.batteryPercentage,
                locationAvailable = _runtimeState.value.context.location.value != "Unavailable",
                locationName = _runtimeState.value.context.location.value,
                timeFormatted = _runtimeState.value.context.temporal.value.formattedTime,
                period = _runtimeState.value.context.temporal.value.period,
                locale = languageTag
            )

            stateMachine.transitionTo(ConversationState.EXECUTING, "Routing query to intelligence tiers")

            val response = responseRouter.routeQuery(
                sessionId = _runtimeState.value.context.sessionId,
                query = query,
                telemetry = telemetry,
                connectionState = ConnectionState.CONNECTED,
                language = languageTag,
                locale = languageTag
            )

            deliverAssistantResponse(response.text, response.source, response.imageBase64)
        }
    }

    private fun deliverAssistantResponse(text: String, source: ResponseSource, imageBase64: String? = null) {
        stateMachine.transitionTo(ConversationState.RESPONDING, "Delivering response")

        val assistantMessage = ChatMessage(
            sender = "ASSISTANT",
            text = text,
            source = source,
            imageBase64 = imageBase64
        )

        contextEngine.appendConversationTurn(_runtimeState.value.messages.lastOrNull()?.text ?: "", text)

        _runtimeState.update {
            it.copy(
                messages = it.messages + assistantMessage,
                latestSpeech = text,
                isSpeaking = true
            )
        }

        // Send to glasses OLED if connected
        glassesGateway.sendCommand("TEXT_OLED:${text.take(64)}")

        // Speak response through TWS / Audio Output Router
        audioRouter.optimizeForVoicePlayback()
        textToSpeechManager.speak(text) {
            _runtimeState.update { it.copy(isSpeaking = false) }
            stateMachine.transitionTo(ConversationState.IDLE, "Response delivery completed")
        }
    }

    fun enableGlassesMode(enable: Boolean) {
        glassesGateway = if (enable && glassesGateway.isAvailable) {
            RealGlassesGateway(appContext)
        } else {
            NoGlassesGateway()
        }
    }
}
