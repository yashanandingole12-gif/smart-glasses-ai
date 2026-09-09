package com.smartglasses.ai.core.bluetooth

import android.annotation.SuppressLint
import android.bluetooth.*
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanFilter
import android.bluetooth.le.ScanResult
import android.bluetooth.le.ScanSettings
import android.content.Context
import android.os.Handler
import android.os.Looper
import android.os.ParcelUuid
import android.util.Log
import com.smartglasses.ai.core.permissions.PermissionManager
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import org.json.JSONObject
import java.util.UUID

enum class DeviceConnectionState {
    DISCONNECTED,
    CONNECTING,
    CONNECTED_SIMULATED,
    CONNECTED_ESP32
}

enum class BleTalkEvent {
    TALK_START,
    TALK_STOP,
    BUTTON_SHORT_PRESS,
    BUTTON_LONG_PRESS
}

class BleManager(private val context: Context) {
    companion object {
        private const val TAG = "SmartGlasses.BLE"
        private const val SCAN_PERIOD_MS = 10000L
    }

    private val bluetoothManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager
    private val bluetoothAdapter: BluetoothAdapter? = bluetoothManager?.adapter

    private val _connectionState = MutableStateFlow(DeviceConnectionState.CONNECTED_SIMULATED)
    val connectionState: StateFlow<DeviceConnectionState> = _connectionState.asStateFlow()

    private val _batteryLevel = MutableStateFlow(85)
    val batteryLevel: StateFlow<Int> = _batteryLevel.asStateFlow()

    private val _talkEvents = MutableSharedFlow<BleTalkEvent>(extraBufferCapacity = 8)
    val talkEvents: SharedFlow<BleTalkEvent> = _talkEvents.asSharedFlow()

    // Backward-compatibility button press event
    private val _buttonPressEvents = MutableSharedFlow<Unit>(extraBufferCapacity = 1)
    val buttonPressEvents: SharedFlow<Unit> = _buttonPressEvents.asSharedFlow()

    private var bluetoothGatt: BluetoothGatt? = null
    private var commandCharacteristic: BluetoothGattCharacteristic? = null
    private val mainHandler = Handler(Looper.getMainLooper())
    private var isScanning = false

    private val scanCallback = object : ScanCallback() {
        @SuppressLint("MissingPermission")
        override fun onScanResult(callbackType: Int, result: ScanResult?) {
            val device = result?.device ?: return
            val name = result.scanRecord?.deviceName ?: device.name ?: ""
            if (name.contains(BleProtocol.DEVICE_NAME_PREFIX, ignoreCase = true)) {
                Log.i(TAG, "Found SmartGlasses device: $name (${device.address})")
                stopScan()
                connectToDevice(device)
            }
        }

        override fun onScanFailed(errorCode: Int) {
            Log.e(TAG, "BLE scan failed with error: $errorCode")
            _connectionState.value = DeviceConnectionState.DISCONNECTED
            isScanning = false
        }
    }

    private val gattCallback = object : BluetoothGattCallback() {
        @SuppressLint("MissingPermission")
        override fun onConnectionStateChange(gatt: BluetoothGatt?, status: Int, newState: Int) {
            if (newState == BluetoothProfile.STATE_CONNECTED) {
                Log.i(TAG, "Connected to Smart Glasses GATT server. Discovering services...")
                _connectionState.value = DeviceConnectionState.CONNECTED_ESP32
                gatt?.discoverServices()
            } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                Log.w(TAG, "Disconnected from Smart Glasses GATT server.")
                _connectionState.value = DeviceConnectionState.DISCONNECTED
                bluetoothGatt?.close()
                bluetoothGatt = null
                commandCharacteristic = null
            }
        }

        @SuppressLint("MissingPermission")
        override fun onServicesDiscovered(gatt: BluetoothGatt?, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                val service = gatt?.getService(BleProtocol.SERVICE_UUID)
                if (service != null) {
                    commandCharacteristic = service.getCharacteristic(BleProtocol.COMMAND_CHAR_UUID)

                    // Subscribe to Event notifications
                    val eventChar = service.getCharacteristic(BleProtocol.EVENT_CHAR_UUID)
                    if (eventChar != null) {
                        gatt.setCharacteristicNotification(eventChar, true)
                        val descriptor = eventChar.getDescriptor(UUID.fromString("00002902-0000-1000-8000-00805f9b34fb"))
                        if (descriptor != null) {
                            descriptor.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
                            gatt.writeDescriptor(descriptor)
                        }
                    }

                    // Subscribe to Battery notifications
                    val batteryChar = service.getCharacteristic(BleProtocol.BATTERY_CHAR_UUID)
                    if (batteryChar != null) {
                        gatt.setCharacteristicNotification(batteryChar, true)
                    }

                    Log.i(TAG, "Smart Glasses GATT services and notifications configured.")
                } else {
                    Log.w(TAG, "Smart Glasses service not found on device.")
                }
            }
        }

        override fun onCharacteristicChanged(gatt: BluetoothGatt?, characteristic: BluetoothGattCharacteristic?) {
            val uuid = characteristic?.uuid ?: return
            val data = characteristic.value ?: return

            if (uuid == BleProtocol.EVENT_CHAR_UUID) {
                val jsonStr = String(data, Charsets.UTF_8)
                parseEventJson(jsonStr)
            } else if (uuid == BleProtocol.BATTERY_CHAR_UUID && data.isNotEmpty()) {
                val batt = data[0].toInt() and 0xFF
                _batteryLevel.value = batt.coerceIn(0, 100)
                Log.i(TAG, "Battery updated from ESP32: $batt%")
            }
        }
    }

    private fun parseEventJson(jsonStr: String) {
        try {
            val json = JSONObject(jsonStr)
            val event = json.optString("event", "")
            Log.i(TAG, "Received BLE Event: $event ($jsonStr)")

            when (event) {
                BleProtocol.EVENT_TALK_START -> {
                    _talkEvents.tryEmit(BleTalkEvent.TALK_START)
                    _buttonPressEvents.tryEmit(Unit)
                }
                BleProtocol.EVENT_TALK_STOP -> {
                    _talkEvents.tryEmit(BleTalkEvent.TALK_STOP)
                }
                BleProtocol.EVENT_BUTTON_PRESSED -> {
                    _talkEvents.tryEmit(BleTalkEvent.BUTTON_SHORT_PRESS)
                    _buttonPressEvents.tryEmit(Unit)
                }
                BleProtocol.EVENT_BUTTON_LONG_PRESSED -> {
                    _talkEvents.tryEmit(BleTalkEvent.BUTTON_LONG_PRESS)
                }
                BleProtocol.EVENT_BATTERY_CHANGED -> {
                    val payload = json.optJSONObject("payload")
                    val batt = payload?.optInt("battery", -1) ?: -1
                    if (batt in 0..100) {
                        _batteryLevel.value = batt
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to parse event JSON: ${e.message}")
        }
    }

    @SuppressLint("MissingPermission")
    fun startScan() {
        if (!isBleHardwareAvailable()) {
            Log.w(TAG, "Bluetooth permission or adapter not ready.")
            return
        }
        val scanner = bluetoothAdapter?.bluetoothLeScanner ?: return
        if (isScanning) return

        _connectionState.value = DeviceConnectionState.CONNECTING
        isScanning = true

        val filter = ScanFilter.Builder()
            .setServiceUuid(ParcelUuid(BleProtocol.SERVICE_UUID))
            .build()
        val settings = ScanSettings.Builder()
            .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
            .build()

        mainHandler.postDelayed({
            if (isScanning) {
                stopScan()
            }
        }, SCAN_PERIOD_MS)

        scanner.startScan(listOf(filter), settings, scanCallback)
        Log.i(TAG, "BLE Scan started for SmartGlasses.")
    }

    @SuppressLint("MissingPermission")
    fun stopScan() {
        if (!isScanning) return
        val scanner = bluetoothAdapter?.bluetoothLeScanner
        try {
            scanner?.stopScan(scanCallback)
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping scan: ${e.message}")
        }
        isScanning = false
    }

    @SuppressLint("MissingPermission")
    private fun connectToDevice(device: BluetoothDevice) {
        bluetoothGatt = device.connectGatt(context, false, gattCallback, BluetoothDevice.TRANSPORT_LE)
    }

    fun toggleConnectionMode() {
        _connectionState.value = when (_connectionState.value) {
            DeviceConnectionState.DISCONNECTED -> {
                if (isBleHardwareAvailable()) {
                    startScan()
                    DeviceConnectionState.CONNECTING
                } else {
                    DeviceConnectionState.CONNECTED_SIMULATED
                }
            }
            DeviceConnectionState.CONNECTING -> {
                stopScan()
                DeviceConnectionState.DISCONNECTED
            }
            DeviceConnectionState.CONNECTED_SIMULATED -> {
                if (isBleHardwareAvailable()) {
                    startScan()
                    DeviceConnectionState.CONNECTING
                } else {
                    DeviceConnectionState.DISCONNECTED
                }
            }
            DeviceConnectionState.CONNECTED_ESP32 -> {
                disconnect()
                DeviceConnectionState.DISCONNECTED
            }
        }
    }

    @SuppressLint("MissingPermission")
    fun disconnect() {
        stopScan()
        bluetoothGatt?.disconnect()
        bluetoothGatt?.close()
        bluetoothGatt = null
        _connectionState.value = DeviceConnectionState.DISCONNECTED
    }

    fun isBleHardwareAvailable(): Boolean {
        return bluetoothAdapter != null && bluetoothAdapter.isEnabled && PermissionManager.hasBluetoothPermission(context)
    }

    fun simulateButtonPressed() {
        _talkEvents.tryEmit(BleTalkEvent.TALK_START)
        _buttonPressEvents.tryEmit(Unit)
    }

    fun simulateButtonReleased() {
        _talkEvents.tryEmit(BleTalkEvent.TALK_STOP)
    }

    fun setBatteryLevel(level: Int) {
        _batteryLevel.value = level.coerceIn(0, 100)
    }
}

