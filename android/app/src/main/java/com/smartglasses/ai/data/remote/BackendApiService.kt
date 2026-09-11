package com.smartglasses.ai.data.remote

import com.smartglasses.ai.data.models.AgentMessageRequestDto
import com.smartglasses.ai.data.models.AgentMessageResponseDto
import com.smartglasses.ai.data.models.FullContextPayloadDto
import com.smartglasses.ai.data.models.GoogleAuthStatusDto
import com.smartglasses.ai.data.models.HealthResponseDto
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.Multipart
import retrofit2.http.Part

interface BackendApiService {
    @GET("api/v1/health")
    suspend fun checkHealth(): HealthResponseDto

    @GET("api/v1/context")
    suspend fun getContext(): FullContextPayloadDto

    @GET("api/v1/auth/google/status")
    suspend fun getGoogleStatus(): GoogleAuthStatusDto

    @POST("api/v1/agent/message")
    suspend fun sendMessage(@Body request: AgentMessageRequestDto): AgentMessageResponseDto

    @Multipart
    @POST("api/v1/files/upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("source") source: RequestBody
    ): Map<String, Any>

    @Multipart
    @POST("api/v1/images/upload")
    suspend fun uploadImage(
        @Part file: MultipartBody.Part,
        @Part("source") source: RequestBody
    ): Map<String, Any>
}

