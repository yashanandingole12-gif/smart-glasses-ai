package com.smartglasses.ai.core.bluetooth

import java.util.UUID

object BleProtocol {
    val SERVICE_UUID: UUID = UUID.fromString("4fafc201-1fb5-459e-8fcc-c5c9c331914b")
    val EVENT_CHAR_UUID: UUID = UUID.fromString("beb5483e-36e1-4688-b7f5-ea07361b26a8")
    val COMMAND_CHAR_UUID: UUID = UUID.fromString("beb5483f-36e1-4688-b7f5-ea07361b26a8")
    val AUDIO_CHAR_UUID: UUID = UUID.fromString("beb54840-36e1-4688-b7f5-ea07361b26a8")

    const val DEVICE_NAME_PREFIX = "SmartGlasses"
}
