package com.smartglasses.ai.core.bluetooth

import android.annotation.SuppressLint
import android.bluetooth.*
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanFilter
import android.bluetooth.le.ScanResult
import android.bluetooth.le.ScanSettings
import android.content.Context
import android.content.SharedPreferences
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

enum class SmartGlassesPairingState {
    UNPAIRED,
    DISCOVERING,
    PAIRING,
    PAIRED,
    CONNECTING,
    CONNECTED,
    DISCONNECTING,
    DISCONNECTED,
    ERROR
}

data class DiscoveredBleDevice(
    val name: String,
    val address: String,
    val rssi: Int,
    val isCompatible: Boolean = true
)

data class SmartGlassesState(
    val connectionState: DeviceConnectionState = DeviceConnectionState.CONNECTED_SIMULATED,
    val pairingState: SmartGlassesPairingState = SmartGlassesPairingState.PAIRED,
    val deviceName: String = "SmartGlasses-S3",
    val deviceId: String = "ESP32-S3-SENSE-01",
    val battery: Int = 85,
    val rssi: Int = -58,
    val cameraAvailable: Boolean = true,
    val microphoneAvailable: Boolean = true,
    val visionPipelineReady: Boolean = true,
    val firmwareVersion: String = "v0.3.0-phase3b16",
    val isScreenOffActive: Boolean = true
)

class BleManager(private val context: Context) {
    companion object {
        private const val TAG = "SmartGlasses.BLE"
        private const val SCAN_PERIOD_MS = 10000L
        private const val PREFS_NAME = "smart_glasses_ble_prefs"
        private const val KEY_PAIRED_ADDR = "paired_device_address"
        private const val KEY_PAIRED_NAME = "paired_device_name"

        @Volatile
        private var instance: BleManager? = null

        fun getInstance(context: Context): BleManager {
            return instance ?: synchronized(this) {
                instance ?: BleManager(context.applicationContext).also { instance = it }
            }
        }
    }

    private val prefs: SharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val bluetoothManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager
    private val bluetoothAdapter: BluetoothAdapter? = bluetoothManager?.adapter

    private val _connectionState = MutableStateFlow(DeviceConnectionState.CONNECTED_SIMULATED)
    val connectionState: StateFlow<DeviceConnectionState> = _connectionState.asStateFlow()

    private val _batteryLevel = MutableStateFlow(85)
    val batteryLevel: StateFlow<Int> = _batteryLevel.asStateFlow()

    private val _rssiLevel = MutableStateFlow(-58)
    val rssiLevel: StateFlow<Int> = _rssiLevel.asStateFlow()

    private val _isScanning = MutableStateFlow(false)
    val isScanningFlow: StateFlow<Boolean> = _isScanning.asStateFlow()

    private val _discoveredDevices = MutableStateFlow<List<DiscoveredBleDevice>>(emptyList())
    val discoveredDevices: StateFlow<List<DiscoveredBleDevice>> = _discoveredDevices.asStateFlow()

    private val _glassesState = MutableStateFlow(SmartGlassesState())
    val glassesState: StateFlow<SmartGlassesState> = _glassesState.asStateFlow()

    private val _talkEvents = MutableSharedFlow<BleTalkEvent>(extraBufferCapacity = 8)
    val talkEvents: SharedFlow<BleTalkEvent> = _talkEvents.asSharedFlow()

    // Backward-compatibility button press event
    private val _buttonPressEvents = MutableSharedFlow<Unit>(extraBufferCapacity = 1)
    val buttonPressEvents: SharedFlow<Unit> = _buttonPressEvents.asSharedFlow()

    private var bluetoothGatt: BluetoothGatt? = null
    private var commandCharacteristic: BluetoothGattCharacteristic? = null
    private val mainHandler = Handler(Looper.getMainLooper())

    private val scanCallback = object : ScanCallback() {
        @SuppressLint("MissingPermission")
        override fun onScanResult(callbackType: Int, result: ScanResult?) {
            val device = result?.device ?: return
            val name = result.scanRecord?.deviceName ?: device.name ?: "Unknown BLE Device"
            val rssi = result.rssi

            val isCompatible = name.contains(BleProtocol.DEVICE_NAME_PREFIX, ignoreCase = true) ||
                    name.contains("ESP32", ignoreCase = true) ||
                    name.contains("Glasses", ignoreCase = true)

            val currentList = _discoveredDevices.value.toMutableList()
            val existingIndex = currentList.indexOfFirst { it.address == device.address }
            val item = DiscoveredBleDevice(name = name, address = device.address, rssi = rssi, isCompatible = isCompatible)

            if (existingIndex >= 0) {
                currentList[existingIndex] = item
            } else {
                currentList.add(item)
            }
            _discoveredDevices.value = currentList

            // Auto-connect if matches saved paired device or default prefix
            val pairedAddr = prefs.getString(KEY_PAIRED_ADDR, null)
            if (pairedAddr != null && device.address.equals(pairedAddr, ignoreCase = true)) {
                Log.i(TAG, "Found paired SmartGlasses device ($pairedAddr). Auto-connecting...")
                stopScan()
                connectToDevice(device)
            } else if (pairedAddr == null && name.contains(BleProtocol.DEVICE_NAME_PREFIX, ignoreCase = true)) {
                Log.i(TAG, "Found SmartGlasses device: $name (${device.address})")
                stopScan()
                connectToDevice(device)
            }
        }

        override fun onScanFailed(errorCode: Int) {
            Log.e(TAG, "BLE scan failed with error: $errorCode")
            _connectionState.value = DeviceConnectionState.DISCONNECTED
            _isScanning.value = false
            syncGlassesState()
        }
    }

    private val gattCallback = object : BluetoothGattCallback() {
        @SuppressLint("MissingPermission")
        override fun onConnectionStateChange(gatt: BluetoothGatt?, status: Int, newState: Int) {
            if (newState == BluetoothProfile.STATE_CONNECTED) {
                Log.i(TAG, "Connected to Smart Glasses GATT server. Requesting 512 MTU & discovering services...")
                _connectionState.value = DeviceConnectionState.CONNECTED_ESP32
                syncGlassesState()
                // Request higher MTU for rich payloads
                gatt?.requestMtu(512)
                gatt?.discoverServices()
                gatt?.readRemoteRssi()
            } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                Log.w(TAG, "Disconnected from Smart Glasses GATT server.")
                _connectionState.value = DeviceConnectionState.DISCONNECTED
                bluetoothGatt?.close()
                bluetoothGatt = null
                commandCharacteristic = null
                syncGlassesState()
            }
        }

        @SuppressLint("MissingPermission")
        override fun onMtuChanged(gatt: BluetoothGatt?, mtu: Int, status: Int) {
            Log.i(TAG, "BLE MTU updated to: $mtu (status=$status)")
            gatt?.discoverServices()
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

        override fun onReadRemoteRssi(gatt: BluetoothGatt?, rssi: Int, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                _rssiLevel.value = rssi
                syncGlassesState()
            }
        }

        override fun onCharacteristicChanged(gatt: BluetoothGatt?, characteristic: BluetoothGattCharacteristic?) {
            val uuid = characteristic?.uuid ?: return
            val data = characteristic.value ?: return

            if (uuid == BleProtocol.EVENT_CHAR_UUID) {
                val rawStr = String(data, Charsets.UTF_8)
                parseEventJson(rawStr)
            } else if (uuid == BleProtocol.BATTERY_CHAR_UUID && data.isNotEmpty()) {
                val batt = data[0].toInt() and 0xFF
                _batteryLevel.value = batt.coerceIn(0, 100)
                syncGlassesState()
                Log.i(TAG, "Battery updated from ESP32: $batt%")
            }
        }
    }

    private fun parseEventJson(rawStr: String) {
        val trimmed = rawStr.trim()
        Log.i(TAG, "Received BLE Event Raw: $trimmed")

        // 1. Robust pattern / token matching (immune to 20-byte packet truncation)
        if (trimmed.contains("TALK_START", ignoreCase = true)) {
            Log.i(TAG, "-> Triggering TALK_START voice capture on phone!")
            _talkEvents.tryEmit(BleTalkEvent.TALK_START)
            _buttonPressEvents.tryEmit(Unit)
            return
        }
        if (trimmed.contains("TALK_STOP", ignoreCase = true)) {
            Log.i(TAG, "-> Triggering TALK_STOP voice capture end on phone!")
            _talkEvents.tryEmit(BleTalkEvent.TALK_STOP)
            return
        }
        if (trimmed.contains("BUTTON_LONG", ignoreCase = true)) {
            Log.i(TAG, "-> Triggering BUTTON_LONG_PRESS")
            _talkEvents.tryEmit(BleTalkEvent.BUTTON_LONG_PRESS)
            return
        }
        if (trimmed.contains("BUTTON_PRESSED", ignoreCase = true) || trimmed.contains("BUTTON_CLICK", ignoreCase = true)) {
            Log.i(TAG, "-> Triggering BUTTON_SHORT_PRESS")
            _talkEvents.tryEmit(BleTalkEvent.BUTTON_SHORT_PRESS)
            _buttonPressEvents.tryEmit(Unit)
            return
        }

        // 2. Structured JSON parsing for battery and other telemetry
        try {
            val json = JSONObject(trimmed)
            val event = json.optString("event", "")
            when (event) {
                BleProtocol.EVENT_BATTERY_CHANGED -> {
                    val payload = json.optJSONObject("payload")
                    val batt = payload?.optInt("battery", -1) ?: -1
                    if (batt in 0..100) {
                        _batteryLevel.value = batt
                        syncGlassesState()
                    }
                }
            }
        } catch (e: Exception) {
            Log.d(TAG, "Raw event token processed (${trimmed}): ${e.message}")
        }
    }

    private fun syncGlassesState() {
        val pairedName = prefs.getString(KEY_PAIRED_NAME, "SmartGlasses-S3") ?: "SmartGlasses-S3"
        val pairingState = when (_connectionState.value) {
            DeviceConnectionState.CONNECTED_ESP32 -> SmartGlassesPairingState.CONNECTED
            DeviceConnectionState.CONNECTED_SIMULATED -> SmartGlassesPairingState.CONNECTED
            DeviceConnectionState.CONNECTING -> SmartGlassesPairingState.CONNECTING
            DeviceConnectionState.DISCONNECTED -> SmartGlassesPairingState.DISCONNECTED
        }

        _glassesState.value = SmartGlassesState(
            connectionState = _connectionState.value,
            pairingState = pairingState,
            deviceName = pairedName,
            battery = _batteryLevel.value,
            rssi = _rssiLevel.value,
            cameraAvailable = true,
            microphoneAvailable = true,
            visionPipelineReady = true,
            firmwareVersion = "v0.3.0-phase3b16",
            isScreenOffActive = true
        )
    }

    @SuppressLint("MissingPermission")
    fun startScan() {
        if (!isBleHardwareAvailable()) {
            Log.w(TAG, "Bluetooth permission or adapter not ready.")
            return
        }
        val scanner = bluetoothAdapter?.bluetoothLeScanner ?: return
        if (_isScanning.value) return

        _connectionState.value = DeviceConnectionState.CONNECTING
        _isScanning.value = true
        syncGlassesState()

        val filter = ScanFilter.Builder()
            .build()
        val settings = ScanSettings.Builder()
            .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
            .build()

        mainHandler.postDelayed({
            if (_isScanning.value) {
                stopScan()
            }
        }, SCAN_PERIOD_MS)

        scanner.startScan(listOf(filter), settings, scanCallback)
        Log.i(TAG, "BLE Scan started for SmartGlasses.")
    }

    @SuppressLint("MissingPermission")
    fun stopScan() {
        if (!_isScanning.value) return
        val scanner = bluetoothAdapter?.bluetoothLeScanner
        try {
            scanner?.stopScan(scanCallback)
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping scan: ${e.message}")
        }
        _isScanning.value = false
    }

    @SuppressLint("MissingPermission")
    private fun connectToDevice(device: BluetoothDevice) {
        bluetoothGatt = device.connectGatt(context, false, gattCallback, BluetoothDevice.TRANSPORT_LE)
    }

    fun pairDevice(address: String, name: String) {
        prefs.edit()
            .putString(KEY_PAIRED_ADDR, address)
            .putString(KEY_PAIRED_NAME, name)
            .apply()
        Log.i(TAG, "Device paired successfully: $name ($address)")
        connectToDiscoveredDevice(address)
    }

    @SuppressLint("MissingPermission")
    fun connectToDiscoveredDevice(address: String) {
        if (!isBleHardwareAvailable()) return
        stopScan()
        try {
            val device = bluetoothAdapter?.getRemoteDevice(address)
            if (device != null) {
                _connectionState.value = DeviceConnectionState.CONNECTING
                syncGlassesState()
                connectToDevice(device)
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error connecting to device $address: ${e.message}")
        }
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
        syncGlassesState()
    }

    @SuppressLint("MissingPermission")
    fun disconnect() {
        stopScan()
        bluetoothGatt?.disconnect()
        bluetoothGatt?.close()
        bluetoothGatt = null
        _connectionState.value = DeviceConnectionState.DISCONNECTED
        syncGlassesState()
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
        syncGlassesState()
    }
}
