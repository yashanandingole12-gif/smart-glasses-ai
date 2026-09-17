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
import com.smartglasses.ai.core.media.GalleryMediaHelper
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
    private var serviceDiscoveryRunnable: Runnable? = null

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

            // Auto-connect if matches saved paired device or default prefix and not already connecting/connected
            val isAlreadyConnectingOrConnected = _connectionState.value == DeviceConnectionState.CONNECTING ||
                    _connectionState.value == DeviceConnectionState.CONNECTED_ESP32

            if (!isAlreadyConnectingOrConnected) {
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
            Log.i(TAG, "onConnectionStateChange status=$status, newState=$newState")
            if (status != BluetoothGatt.GATT_SUCCESS) {
                Log.w(TAG, "GATT connection status error ($status). Cleaning up connection...")
                mainHandler.post {
                    serviceDiscoveryRunnable?.let { mainHandler.removeCallbacks(it) }
                    serviceDiscoveryRunnable = null
                    try {
                        gatt?.disconnect()
                        gatt?.close()
                    } catch (e: Exception) {
                        Log.e(TAG, "Error closing gatt on failure: ${e.message}")
                    }
                    if (bluetoothGatt == gatt) {
                        bluetoothGatt = null
                        commandCharacteristic = null
                    }
                    _connectionState.value = DeviceConnectionState.DISCONNECTED
                    syncGlassesState()
                }
                return
            }

            if (newState == BluetoothProfile.STATE_CONNECTED) {
                Log.i(TAG, "Successfully connected to Smart Glasses GATT server. Requesting MTU 512 & High Priority...")
                mainHandler.post {
                    _connectionState.value = DeviceConnectionState.CONNECTED_ESP32
                    syncGlassesState()
                }

                // Sequence GATT operations: Request high priority (11.25ms interval) and 512 MTU
                gatt?.requestConnectionPriority(BluetoothGatt.CONNECTION_PRIORITY_HIGH)
                val mtuOk = gatt?.requestMtu(512) ?: false
                Log.d(TAG, "requestMtu(512) returned: $mtuOk")

                // Fallback timeout in case onMtuChanged is never triggered by the OS
                serviceDiscoveryRunnable?.let { mainHandler.removeCallbacks(it) }
                val fallback = Runnable {
                    Log.i(TAG, "MTU callback fallback; initiating service discovery...")
                    gatt?.discoverServices()
                }
                serviceDiscoveryRunnable = fallback
                mainHandler.postDelayed(fallback, 1000L)

            } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                Log.w(TAG, "Disconnected from Smart Glasses GATT server.")
                mainHandler.post {
                    serviceDiscoveryRunnable?.let { mainHandler.removeCallbacks(it) }
                    serviceDiscoveryRunnable = null
                    try {
                        gatt?.disconnect()
                        gatt?.close()
                    } catch (e: Exception) {
                        Log.e(TAG, "Error closing gatt on disconnect: ${e.message}")
                    }
                    if (bluetoothGatt == gatt) {
                        bluetoothGatt = null
                        commandCharacteristic = null
                    }
                    _connectionState.value = DeviceConnectionState.DISCONNECTED
                    syncGlassesState()
                }
            }
        }

        @SuppressLint("MissingPermission")
        override fun onMtuChanged(gatt: BluetoothGatt?, mtu: Int, status: Int) {
            Log.i(TAG, "BLE MTU negotiated: $mtu (status=$status)")
            serviceDiscoveryRunnable?.let { mainHandler.removeCallbacks(it) }
            serviceDiscoveryRunnable = null
            // Ensure high connection priority is enforced with new MTU
            gatt?.requestConnectionPriority(BluetoothGatt.CONNECTION_PRIORITY_HIGH)
            // Slight delay before service discovery to avoid GATT busy collision
            mainHandler.postDelayed({
                val discovering = gatt?.discoverServices() ?: false
                Log.i(TAG, "discoverServices initiated: $discovering")
            }, 100L)
        }

        @SuppressLint("MissingPermission")
        override fun onServicesDiscovered(gatt: BluetoothGatt?, status: Int) {
            Log.i(TAG, "onServicesDiscovered status=$status")
            if (status == BluetoothGatt.GATT_SUCCESS && gatt != null) {
                val service = gatt.getService(BleProtocol.SERVICE_UUID)
                if (service != null) {
                    commandCharacteristic = service.getCharacteristic(BleProtocol.COMMAND_CHAR_UUID)

                    // Subscribe to Event notifications
                    val eventChar = service.getCharacteristic(BleProtocol.EVENT_CHAR_UUID)
                    if (eventChar != null) {
                        val setNotification = gatt.setCharacteristicNotification(eventChar, true)
                        Log.d(TAG, "setCharacteristicNotification on EVENT_CHAR returned $setNotification")
                        val descriptor = eventChar.getDescriptor(UUID.fromString("00002902-0000-1000-8000-00805f9b34fb"))
                        if (descriptor != null) {
                            descriptor.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
                            mainHandler.postDelayed({
                                val writeSuccess = gatt.writeDescriptor(descriptor)
                                Log.i(TAG, "writeDescriptor 2902 on EVENT_CHAR returned $writeSuccess")
                            }, 100L)
                        }
                    }

                    // Subscribe to Battery notifications
                    val batteryChar = service.getCharacteristic(BleProtocol.BATTERY_CHAR_UUID)
                    if (batteryChar != null) {
                        gatt.setCharacteristicNotification(batteryChar, true)
                    }

                    Log.i(TAG, "Smart Glasses GATT services and notifications configured successfully.")
                } else {
                    Log.w(TAG, "Smart Glasses service ${BleProtocol.SERVICE_UUID} not found on device.")
                }
            } else {
                Log.e(TAG, "Service discovery failed with status: $status")
            }
        }

        @SuppressLint("MissingPermission")
        override fun onDescriptorWrite(gatt: BluetoothGatt?, descriptor: BluetoothGattDescriptor?, status: Int) {
            Log.i(TAG, "onDescriptorWrite uuid=${descriptor?.uuid} status=$status")
            if (status == BluetoothGatt.GATT_SUCCESS) {
                mainHandler.postDelayed({
                    gatt?.readRemoteRssi()
                    sendCommand(BleProtocol.CMD_STATUS_REQUEST)
                }, 200L)
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
            .setMatchMode(ScanSettings.MATCH_MODE_AGGRESSIVE)
            .setCallbackType(ScanSettings.CALLBACK_TYPE_ALL_MATCHES)
            .setNumOfMatches(ScanSettings.MATCH_NUM_MAX_ADVERTISEMENT)
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
        // Clean up previous GATT instance first
        serviceDiscoveryRunnable?.let { mainHandler.removeCallbacks(it) }
        serviceDiscoveryRunnable = null
        try {
            bluetoothGatt?.disconnect()
            bluetoothGatt?.close()
        } catch (e: Exception) {
            Log.e(TAG, "Error cleaning up previous GATT instance: ${e.message}")
        }
        bluetoothGatt = null
        commandCharacteristic = null

        _connectionState.value = DeviceConnectionState.CONNECTING
        syncGlassesState()

        val devName = try { device.name ?: "SmartGlasses" } catch (e: Exception) { "SmartGlasses" }
        Log.i(TAG, "Initiating GATT connection to $devName (${device.address})...")
        mainHandler.postDelayed({
            try {
                bluetoothGatt = device.connectGatt(context, false, gattCallback, BluetoothDevice.TRANSPORT_LE)
            } catch (e: Exception) {
                Log.e(TAG, "Failed to connectGatt: ${e.message}")
                _connectionState.value = DeviceConnectionState.DISCONNECTED
                syncGlassesState()
            }
        }, 100L)
    }

    fun sendCommand(command: String): Boolean {
        val gatt = bluetoothGatt ?: return false
        val char = commandCharacteristic ?: return false
        return try {
            char.value = command.toByteArray(Charsets.UTF_8)
            char.writeType = if ((char.properties and BluetoothGattCharacteristic.PROPERTY_WRITE_NO_RESPONSE) != 0) {
                BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE
            } else {
                BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT
            }
            val success = gatt.writeCharacteristic(char)
            Log.i(TAG, "Sent BLE command '$command' -> success=$success")
            success
        } catch (e: Exception) {
            Log.e(TAG, "Error writing BLE command '$command': ${e.message}")
            false
        }
    }

    fun sendWifiCredentials(ssid: String, pass: String): Boolean {
        val payload = "CMD_WIFI_PROVISION:{\"ssid\":\"$ssid\",\"password\":\"$pass\"}"
        return sendCommand(payload)
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
        serviceDiscoveryRunnable?.let { mainHandler.removeCallbacks(it) }
        serviceDiscoveryRunnable = null
        try {
            bluetoothGatt?.disconnect()
            bluetoothGatt?.close()
        } catch (e: Exception) {
            Log.e(TAG, "Error during disconnect: ${e.message}")
        }
        bluetoothGatt = null
        commandCharacteristic = null
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

    fun requestPhotoCapture(): Boolean {
        Log.i(TAG, "Triggering photo capture from smart glasses camera...")
        val sent = sendCommand("{\"action\":\"CAPTURE_IMAGE\"}")
        GalleryMediaHelper.saveSamplePhoto(context, "LARA Smart Glasses Photo")
        return sent || _connectionState.value == DeviceConnectionState.CONNECTED_SIMULATED
    }
}
