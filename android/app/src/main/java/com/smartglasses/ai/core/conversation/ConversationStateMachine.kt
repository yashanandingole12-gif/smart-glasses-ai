package com.smartglasses.ai.core.conversation

import android.util.Log
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

enum class ConversationState {
    IDLE,
    WAKE_DETECTED,
    LISTENING,
    CAPTURING,
    TRANSCRIBING,
    UNDERSTANDING,
    EXECUTING,
    RESPONDING,
    RECOVERABLE_ERROR
}

class ConversationStateMachine {
    companion object {
        private const val TAG = "EVA.StateMachine"
    }

    private val _state = MutableStateFlow(ConversationState.IDLE)
    val state: StateFlow<ConversationState> = _state.asStateFlow()

    private var previousSafeState: ConversationState = ConversationState.IDLE

    @Synchronized
    fun transitionTo(newState: ConversationState, reason: String = "") {
        val current = _state.value
        if (current == newState) return

        if (current != ConversationState.RECOVERABLE_ERROR) {
            previousSafeState = current
        }

        Log.i(TAG, "STATE_TRANSITION: $current -> $newState (Reason: '$reason')")
        _state.value = newState
    }

    @Synchronized
    fun handleError(errorMsg: String) {
        Log.w(TAG, "STATE_ERROR in ${_state.value}: '$errorMsg'")
        _state.value = ConversationState.RECOVERABLE_ERROR
        
        // Auto-recover to previous safe state or IDLE
        val target = if (previousSafeState != ConversationState.RECOVERABLE_ERROR) previousSafeState else ConversationState.IDLE
        Log.i(TAG, "STATE_RECOVERY: Recovering from error -> $target")
        _state.value = target
    }

    @Synchronized
    fun stopConversation(reason: String = "User stop") {
        Log.i(TAG, "STOP_CONVERSATION: Resetting to IDLE (Reason: '$reason')")
        previousSafeState = ConversationState.IDLE
        _state.value = ConversationState.IDLE
    }

    val isListening: Boolean
        get() = _state.value == ConversationState.LISTENING || _state.value == ConversationState.CAPTURING

    val isProcessing: Boolean
        get() = _state.value == ConversationState.TRANSCRIBING ||
                _state.value == ConversationState.UNDERSTANDING ||
                _state.value == ConversationState.EXECUTING

    val isResponding: Boolean
        get() = _state.value == ConversationState.RESPONDING
}
