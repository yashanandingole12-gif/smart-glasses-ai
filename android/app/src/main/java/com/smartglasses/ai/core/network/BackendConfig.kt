package com.smartglasses.ai.core.network

import android.content.Context
import android.content.SharedPreferences
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

object BackendConfig {
    private const val PREFS_NAME = "smart_glasses_backend_config"
    private const val KEY_BASE_URL = "backend_base_url"

    const val DEFAULT_EMULATOR_URL = "http://10.0.2.2:8001/"
    const val DEFAULT_LAN_URL = "http://192.168.137.1:8001/"

    private var prefs: SharedPreferences? = null

    private val _baseUrlState = MutableStateFlow(DEFAULT_LAN_URL)
    val baseUrlState: StateFlow<String> = _baseUrlState.asStateFlow()

    fun init(context: Context) {
        prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val savedUrl = prefs?.getString(KEY_BASE_URL, DEFAULT_LAN_URL) ?: DEFAULT_LAN_URL
        _baseUrlState.value = normalizeUrl(savedUrl)
    }

    fun getBaseUrl(): String {
        return _baseUrlState.value
    }

    fun setBaseUrl(url: String) {
        val normalized = normalizeUrl(url)
        _baseUrlState.value = normalized
        prefs?.edit()?.putString(KEY_BASE_URL, normalized)?.apply()
    }

    fun normalizeUrl(raw: String): String {
        var clean = raw.trim()
        // Auto-fix common typo where dot between 168 and subnet is omitted (e.g. 192.168243. -> 192.168.243.)
        clean = clean.replace(Regex("""192\.168(\d{1,3})\."""), "192.168.$1.")

        if (!clean.startsWith("http://") && !clean.startsWith("https://")) {
            clean = "http://$clean"
        }
        if (!clean.endsWith("/")) {
            clean = "$clean/"
        }
        return clean
    }
}
