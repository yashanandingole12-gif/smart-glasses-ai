package com.smartglasses.ai.core.network

import com.smartglasses.ai.data.remote.BackendApiService
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object NetworkClient {
    private var cachedBaseUrl: String? = null
    private var cachedApiService: BackendApiService? = null

    private val okHttpClient: OkHttpClient by lazy {
        val logging = HttpLoggingInterceptor { message ->
            // Centralized token/credential redaction in Android logs
            val redacted = message
                .replace(Regex("(?i)Bearer\\s+[a-zA-Z0-9_\\-\\.]+"), "Bearer [REDACTED]")
                .replace(Regex("(?i)api[_-]?key=[\"']?[^\"'&\\s]+"), "api_key=[REDACTED]")
                .replace(Regex("(?i)refresh_token=[\"']?[^\"'&\\s]+"), "refresh_token=[REDACTED]")
            android.util.Log.d("SmartGlasses.Network", redacted)
        }.apply {
            level = HttpLoggingInterceptor.Level.BASIC
        }

        OkHttpClient.Builder()
            .addInterceptor(logging)
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(15, TimeUnit.SECONDS)
            .build()
    }

    @Synchronized
    fun getApiService(): BackendApiService {
        val currentBaseUrl = BackendConfig.getBaseUrl()
        if (cachedApiService == null || cachedBaseUrl != currentBaseUrl) {
            cachedBaseUrl = currentBaseUrl
            val retrofit = Retrofit.Builder()
                .baseUrl(currentBaseUrl)
                .client(okHttpClient)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
            cachedApiService = retrofit.create(BackendApiService::class.java)
        }
        return cachedApiService!!
    }
}
