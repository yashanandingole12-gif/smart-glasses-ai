package com.smartglasses.ai.core.network

data class NetworkDiagnostics(
    val backendUrl: String = "",
    val connectionState: ConnectionState = ConnectionState.CONNECTING,
    val lastSuccessfulRequestTime: String? = null,
    val lastFailureReason: String? = null,
    val lastLatencyMs: Double? = null,
    val averageLatencyMs: Double = 0.0,
    val p95LatencyMs: Double = 0.0,
    val minLatencyMs: Double = 0.0,
    val maxLatencyMs: Double = 0.0,
    val totalRequests: Int = 0,
    val failedRequests: Int = 0
)
