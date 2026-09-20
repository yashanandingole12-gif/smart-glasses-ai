package com.smartglasses.ai.core.audio

import android.util.Log
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentSkipListMap

data class AudioPacket(
    val sessionId: String,
    val streamId: Int,
    val sequenceNumber: Long,
    val timestampMs: Long,
    val payloadLength: Int,
    val payload: ByteArray
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false
        other as AudioPacket
        return sequenceNumber == other.sequenceNumber && sessionId == other.sessionId && streamId == other.streamId
    }

    override fun hashCode(): Int {
        var result = sessionId.hashCode()
        result = 31 * result + streamId
        result = 31 * result + sequenceNumber.hashCode()
        return result
    }
}

/**
 * High-performance, latency-resilient framed audio transport and bounded jitter buffer.
 * Re-orders packets, eliminates duplicates, and mitigates BLE/Wi-Fi packet jitter.
 */
class AudioTransport(
    private val maxBufferSize: Int = 32, // Bounded buffer (max ~1s of 32ms frames)
    private val onFrameReady: (AudioPacket) -> Unit
) {
    companion object {
        private const val TAG = "EVA.AudioTransport"
        const val FRAME_HEADER_SIZE = 24
        const val MAGIC_BYTE: Byte = 0xEA.toByte()
    }

    // Per-session ordered bounded jitter queues
    private val jitterBuffer = ConcurrentSkipListMap<Long, AudioPacket>()
    private var lastEmittedSequence = -1L
    private var droppedFramesCount = 0L

    fun ingestRawFrame(rawBytes: ByteArray, sessionId: String = "default_session", streamId: Int = 0) {
        if (rawBytes.isEmpty()) return

        // Check if frame has binary header or is raw PCM
        val packet = if (rawBytes.size >= FRAME_HEADER_SIZE && rawBytes[0] == MAGIC_BYTE) {
            parseFramedPacket(rawBytes)
        } else {
            // Unframed PCM wrap with monotonic sequence
            val seq = lastEmittedSequence + 1 + jitterBuffer.size
            AudioPacket(
                sessionId = sessionId,
                streamId = streamId,
                sequenceNumber = seq,
                timestampMs = System.currentTimeMillis(),
                payloadLength = rawBytes.size,
                payload = rawBytes
            )
        }

        if (packet == null) return

        // Duplicate rejection
        if (packet.sequenceNumber <= lastEmittedSequence) {
            Log.d(TAG, "Dropping stale/duplicate packet seq=${packet.sequenceNumber} (lastEmitted=$lastEmittedSequence)")
            return
        }

        // Bounded queue enforcement (backpressure & drop oldest if overflow)
        if (jitterBuffer.size >= maxBufferSize) {
            val oldestKey = jitterBuffer.firstKey()
            jitterBuffer.remove(oldestKey)
            droppedFramesCount++
            Log.w(TAG, "Jitter buffer overflow: dropped oldest frame seq=$oldestKey (total dropped=$droppedFramesCount)")
        }

        jitterBuffer[packet.sequenceNumber] = packet
        drainJitterBuffer()
    }

    private fun parseFramedPacket(bytes: ByteArray): AudioPacket? {
        try {
            val buffer = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN)
            val magic = buffer.get()
            val version = buffer.get()
            val streamId = buffer.short.toInt()
            val seq = buffer.long
            val ts = buffer.long
            val payloadLen = buffer.int

            if (payloadLen <= 0 || buffer.remaining() < payloadLen) return null

            val payload = ByteArray(payloadLen)
            buffer.get(payload)

            return AudioPacket(
                sessionId = "stream_$streamId",
                streamId = streamId,
                sequenceNumber = seq,
                timestampMs = ts,
                payloadLength = payloadLen,
                payload = payload
            )
        } catch (e: Exception) {
            Log.w(TAG, "Packet parse error: ${e.message}")
            return null
        }
    }

    private fun drainJitterBuffer() {
        while (jitterBuffer.isNotEmpty()) {
            val nextSeq = if (lastEmittedSequence == -1L) jitterBuffer.firstKey() else lastEmittedSequence + 1
            val packet = jitterBuffer.remove(nextSeq)

            if (packet != null) {
                lastEmittedSequence = packet.sequenceNumber
                onFrameReady(packet)
            } else {
                // If gap exists, wait unless jitter buffer has accumulated 3+ frames
                if (jitterBuffer.size > 3) {
                    val skippedKey = jitterBuffer.firstKey()
                    val skippedPacket = jitterBuffer.remove(skippedKey)
                    if (skippedPacket != null) {
                        lastEmittedSequence = skippedPacket.sequenceNumber
                        onFrameReady(skippedPacket)
                    }
                }
                break
            }
        }
    }

    fun resetSession() {
        jitterBuffer.clear()
        lastEmittedSequence = -1L
        droppedFramesCount = 0L
        Log.i(TAG, "Audio transport session reset.")
    }
}
