package com.smartglasses.ai.core.bluetooth

import java.util.UUID

object BleProtocol {
    // Standard Custom Smart Glasses GATT Service & Characteristic UUIDs
    val SERVICE_UUID: UUID = UUID.fromString("6e400001-b5a3-f393-e0a9-e50e24dcca9e")
    val COMMAND_CHAR_UUID: UUID = UUID.fromString("6e400002-b5a3-f393-e0a9-e50e24dcca9e")
    val EVENT_CHAR_UUID: UUID = UUID.fromString("6e400003-b5a3-f393-e0a9-e50e24dcca9e")
    val STATUS_CHAR_UUID: UUID = UUID.fromString("6e400004-b5a3-f393-e0a9-e50e24dcca9e")
    val BATTERY_CHAR_UUID: UUID = UUID.fromString("6e400005-b5a3-f393-e0a9-e50e24dcca9e")
    val AUDIO_RX_CHAR_UUID: UUID = UUID.fromString("6e400006-b5a3-f393-e0a9-e50e24dcca9e")

    const val DEVICE_NAME_PREFIX = "SmartGlasses"

    // Standard BLE Event Names
    const val EVENT_TALK_START = "TALK_START"
    const val EVENT_TALK_STOP = "TALK_STOP"
    const val EVENT_BUTTON_PRESSED = "BUTTON_PRESSED"
    const val EVENT_BUTTON_LONG_PRESSED = "BUTTON_LONG_PRESSED"
    const val EVENT_BATTERY_CHANGED = "BATTERY_CHANGED"
    const val EVENT_DEVICE_CONNECTED = "DEVICE_CONNECTED"
    const val EVENT_DEVICE_DISCONNECTED = "DEVICE_DISCONNECTED"
    const val EVENT_CAMERA_READY = "CAMERA_READY"

    // Standard BLE Commands
    const val CMD_START_LISTENING = "START_LISTENING"
    const val CMD_STOP_LISTENING = "STOP_LISTENING"
    const val CMD_CAPTURE_IMAGE = "CAPTURE_IMAGE"
    const val CMD_STATUS_REQUEST = "STATUS_REQUEST"
    const val CMD_PLAY_MESSAGE_ALERT = "PLAY_MESSAGE_ALERT"
    const val CMD_PLAY_AI_RESPONSE = "PLAY_AI_RESPONSE"
    const val CMD_CALL_INCOMING = "CALL_INCOMING"
    const val CMD_SPEAKER_TEST = "SPEAKER_TEST"
}

