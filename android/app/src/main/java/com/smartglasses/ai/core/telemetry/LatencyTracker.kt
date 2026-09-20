package com.smartglasses.ai.core.telemetry

import android.os.SystemClock
import android.util.Log

data class StageLatency(
    val stage: String,
    val durationMs: Double,
    val success: Boolean = true,
    val failureReason: String? = null
)

class LatencyTracker(
    val requestId: String,
    val sessionId: String,
    val deviceId: String = "EVA-Android"
) {
    companion object {
        private const val TAG = "EVA.Latency"
    }

    private val startTime = SystemClock.elapsedRealtime()
    private val stageTimers = mutableMapOf<String, Long>()
    private val recordedStages = mutableListOf<StageLatency>()

    fun startStage(stageName: String) {
        stageTimers[stageName] = SystemClock.elapsedRealtime()
    }

    fun endStage(stageName: String, success: Boolean = true, failureReason: String? = null): Double {
        val start = stageTimers[stageName] ?: return 0.0
        val dur = (SystemClock.elapsedRealtime() - start).toDouble().coerceAtLeast(0.1)
        val metric = StageLatency(stageName, dur, success, failureReason)
        recordedStages.add(metric)
        Log.d(TAG, "STAGE_LATENCY [$requestId] $stageName: ${dur}ms (success=$success)")
        return dur
    }

    fun getEndToEndLatency(): Double {
        return (SystemClock.elapsedRealtime() - startTime).toDouble()
    }

    fun logSummary() {
        val total = getEndToEndLatency()
        Log.i(TAG, "LATENCY_SUMMARY req=$requestId total=${total}ms breakdown=${recordedStages.map { "${it.stage}:${it.durationMs}ms" }}")
    }
}
