package com.smartglasses.ai.core.audio

import android.util.Log
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.UUID

enum class AudioSessionState {
    IDLE,
    STREAM_STARTING,
    ACTIVE_INPUT_STREAMING,
    PROCESSING_SPEECH,
    DELIVERING_AUDIO_OUTPUT,
    RECOVERING,
    ERROR
}

/**
 * Manages audio stream sessions, lifecycle transitions, cancellation, and recovery.
 */
class AudioSessionManager {
    companion object {
        private const val TAG = "EVA.AudioSessionManager"
    }

    private val _sessionState = MutableStateFlow(AudioSessionState.IDLE)
    val sessionState: StateFlow<AudioSessionState> = _sessionState.asStateFlow()

    private var activeSessionId: String = UUID.randomUUID().toString()
    private var activeStreamId: Int = 1
    private var sessionStartTimeMs: Long = 0L

    fun startNewSession(): String {
        activeSessionId = UUID.randomUUID().toString()
        activeStreamId++
        sessionStartTimeMs = System.currentTimeMillis()
        _sessionState.value = AudioSessionState.STREAM_STARTING
        Log.i(TAG, "New audio session established: $activeSessionId (streamId=$activeStreamId)")
        return activeSessionId
    }

    fun transitionTo(newState: AudioSessionState, reason: String = "") {
        if (_sessionState.value != newState) {
            Log.d(TAG, "Session state transition: ${_sessionState.value} -> $newState ($reason)")
            _sessionState.value = newState
        }
    }

    fun endSession(reason: String = "") {
        _sessionState.value = AudioSessionState.IDLE
        Log.i(TAG, "Audio session $activeSessionId ended: $reason")
    }

    fun getCurrentSessionId(): String = activeSessionId
    fun getCurrentStreamId(): Int = activeStreamId
}
