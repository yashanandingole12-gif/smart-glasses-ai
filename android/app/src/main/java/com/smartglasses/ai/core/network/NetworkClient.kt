package com.smartglasses.ai.core.network

import com.smartglasses.ai.data.remote.BackendApiService
import okhttp3.ConnectionPool
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.Response
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.io.IOException
import java.util.concurrent.TimeUnit

object NetworkClient {
    private var cachedBaseUrl: String? = null
    private var cachedApiService: BackendApiService? = null

    // Safe Retry Interceptor: Retries GET requests on transient network failures up to 2 times.
    // NEVER retries POST/PUT/DELETE requests to avoid unintended side effects.
    private class SafeRetryInterceptor(private val maxRetries: Int = 2) : Interceptor {
        override fun intercept(chain: Interceptor.Chain): Response {
            val request = chain.request().newBuilder()
                .header("Connection", "keep-alive")
                .build()

            var response: Response? = null
            var exception: IOException? = null
            var attempt = 0

            val isGet = request.method.equals("GET", ignoreCase = true)
            val allowedAttempts = if (isGet) maxRetries + 1 else 1

            while (attempt < allowedAttempts) {
                try {
                    response = chain.proceed(request)
                    if (response.isSuccessful || !isGet) {
                        return response
                    }
                    // For transient server errors on GET, close and retry
                    if (response.code in 502..504 && attempt < maxRetries) {
                        response.close()
                        Thread.sleep(150L * (attempt + 1))
                    } else {
                        return response
                    }
                } catch (e: IOException) {
                    exception = e
                    if (!isGet || attempt >= maxRetries) {
                        throw e
                    }
                    try {
                        Thread.sleep(150L * (attempt + 1))
                    } catch (_: InterruptedException) {
                        Thread.currentThread().interrupt()
                        throw e
                    }
                }
                attempt++
            }

            throw exception ?: IOException("Request failed after $attempt attempts")
        }
    }

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
            // Connection Pooling & HTTP Keep-Alive
            .connectionPool(ConnectionPool(5, 5, TimeUnit.MINUTES))
            // Sensible timeouts as per Phase 3B.5 specifications
            .connectTimeout(3, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .writeTimeout(10, TimeUnit.SECONDS)
            .retryOnConnectionFailure(false)
            .addInterceptor(SafeRetryInterceptor(maxRetries = 2))
            .addInterceptor(logging)
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
