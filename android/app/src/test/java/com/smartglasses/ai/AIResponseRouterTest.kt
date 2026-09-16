package com.smartglasses.ai

import com.smartglasses.ai.core.ai.LocalAiEngine
import com.smartglasses.ai.core.network.ConnectionState
import com.smartglasses.ai.domain.models.AiAvailabilityState
import com.smartglasses.ai.domain.models.FailureCategory
import com.smartglasses.ai.domain.models.ResponseSource
import com.smartglasses.ai.domain.models.WearableResponse
import com.smartglasses.ai.domain.models.WearableTelemetry
import com.smartglasses.ai.domain.repositories.AssistantRepository
import com.smartglasses.ai.domain.usecases.AIResponseRouter
import com.smartglasses.ai.domain.usecases.LocalDeterministicResolver
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import java.io.File

class FakeAssistantRepository : AssistantRepository {
    var shouldTimeout = false
    var shouldFail = false
    var returnMessage = "Cloud Gemini Response"

    override suspend fun sendMessage(
        sessionId: String,
        userMessage: String,
        telemetry: WearableTelemetry,
        confirmedAction: Boolean?,
        confirmedActionId: String?,
        language: String?,
        locale: String?
    ): Result<WearableResponse> {
        if (shouldTimeout) {
            delay(4000)
        }
        if (shouldFail) {
            return Result.failure(Exception("Cloud unavailable"))
        }
        return Result.success(
            WearableResponse(
                text = returnMessage,
                sessionId = sessionId,
                source = ResponseSource.CLOUD_GEMINI,
                latencyMs = 250.0
            )
        )
    }

    override suspend fun checkHealth(): Result<Boolean> = Result.success(true)
    override suspend fun checkGoogleAuthStatus(): Result<Pair<Boolean, String?>> = Result.success(Pair(true, "user@gmail.com"))
}

class FakeContext(private val filesDirFile: File) : android.content.ContextWrapper(null) {
    override fun getFilesDir(): File = filesDirFile
}

class AIResponseRouterTest {

    private lateinit var fakeRepo: FakeAssistantRepository
    private lateinit var router: AIResponseRouter
    private val telemetry = WearableTelemetry(batteryPercentage = 84, timeFormatted = "12:42 PM", period = "afternoon", locationName = "Nagpur")

    @Before
    fun setup() {
        val tempDir = File(System.getProperty("java.io.tmpdir"), "glasses_test_${System.currentTimeMillis()}")
        tempDir.mkdirs()
        val fakeCtx = FakeContext(tempDir)
        fakeRepo = FakeAssistantRepository()
        val detResolver = LocalDeterministicResolver()
        val localAi = LocalAiEngine(fakeCtx)
        router = AIResponseRouter(fakeRepo, detResolver, localAi)
        router.conversationalCloudTimeoutMs = 500L
    }

    @Test
    fun testDeterministicQueryRoutesToLocal() = runBlocking {
        val resp = router.routeQuery("sess_1", "What time is it?", telemetry, ConnectionState.CONNECTED)
        assertEquals(ResponseSource.LOCAL_DETERMINISTIC, resp.source)
        assertTrue(resp.text.contains("12:42 PM"))
    }

    @Test
    fun testCloudRequiredOnlineRoutesToCloud() = runBlocking {
        fakeRepo.returnMessage = "You have 2 unread emails."
        val resp = router.routeQuery("sess_2", "Check my email", telemetry, ConnectionState.CONNECTED)
        assertEquals(ResponseSource.CLOUD_GEMINI, resp.source)
        assertEquals("You have 2 unread emails.", resp.text)
    }

    @Test
    fun testCloudRequiredOfflineDoesNotHallucinate() = runBlocking {
        val resp = router.routeQuery("sess_3", "Check my email", telemetry, ConnectionState.DISCONNECTED)
        assertTrue(resp.text.contains("can't access your email"))
        assertEquals(FailureCategory.NETWORK_FAILURE, resp.failureCategory)
    }

    @Test
    fun testCalendarRequiredOfflineDoesNotHallucinate() = runBlocking {
        val resp = router.routeQuery("sess_4", "What is on my calendar for tomorrow?", telemetry, ConnectionState.DISCONNECTED)
        assertTrue(resp.text.contains("can't access your calendar"))
        assertEquals(FailureCategory.NETWORK_FAILURE, resp.failureCategory)
    }

    @Test
    fun testConversationalCloudTimeoutFallsBackToLocalAi() = runBlocking {
        fakeRepo.shouldTimeout = true
        var changedState: AiAvailabilityState? = null
        val resp = router.routeQuery(
            sessionId = "sess_5",
            query = "Tell me a joke",
            telemetry = telemetry,
            connectionState = ConnectionState.CONNECTED,
            onAiStateChanged = { changedState = it }
        )
        assertEquals(ResponseSource.LOCAL_AI, resp.source)
        assertEquals(AiAvailabilityState.USING_LOCAL_AI, changedState)
        assertTrue(resp.text.isNotBlank())
    }

    @Test
    fun testConversationalOfflineRoutesToLocalAi() = runBlocking {
        var changedState: AiAvailabilityState? = null
        val resp = router.routeQuery(
            sessionId = "sess_6",
            query = "Tell me a joke",
            telemetry = telemetry,
            connectionState = ConnectionState.DISCONNECTED,
            onAiStateChanged = { changedState = it }
        )
        assertEquals(ResponseSource.LOCAL_AI, resp.source)
        assertEquals(AiAvailabilityState.LOCAL_ONLY, changedState)
        assertTrue(resp.text.isNotBlank())
    }

    @Test
    fun testHeyLaraLifecycleGreeting() = runBlocking {
        val resp = router.routeQuery(
            sessionId = "sess_7",
            query = "Hey LARA",
            telemetry = telemetry,
            connectionState = ConnectionState.CONNECTED
        )
        assertEquals(ResponseSource.LOCAL_DETERMINISTIC, resp.source)
        assertTrue(resp.text.contains("LARA is active"))
        assertTrue(resp.text.contains("84%"))
    }

    @Test
    fun testGoodbyeLaraLifecycleCleanup() = runBlocking {
        val resp = router.routeQuery(
            sessionId = "sess_8",
            query = "Goodbye LARA",
            telemetry = telemetry,
            connectionState = ConnectionState.CONNECTED
        )
        assertEquals(ResponseSource.LOCAL_DETERMINISTIC, resp.source)
        assertTrue(resp.text.contains("Goodbye! Putting LARA to sleep"))
    }

    @Test
    fun testTenDigitPhoneSafetyRuleEnforcement() = runBlocking {
        // 9-digit number should NOT dial automatically; must require confirmation
        val respShort = router.routeQuery(
            sessionId = "sess_call1",
            query = "call 98765-4321",
            telemetry = telemetry,
            connectionState = ConnectionState.CONNECTED
        )
        assertTrue(respShort.requiresConfirmation)
        assertTrue(respShort.text.contains("less than the standard 10-digit format"))

        // Standard 10-digit number dials directly
        val respValid = router.routeQuery(
            sessionId = "sess_call2",
            query = "call 9876543210",
            telemetry = telemetry,
            connectionState = ConnectionState.CONNECTED
        )
        assertFalse(respValid.requiresConfirmation)
        assertTrue(respValid.text.contains("Calling 9876543210"))
    }

    @Test
    fun testOfflineLocalAiProgrammingKnowledge() = runBlocking {
        val respArray = router.routeQuery(
            sessionId = "sess_slm1",
            query = "what is an array",
            telemetry = telemetry,
            connectionState = ConnectionState.DISCONNECTED
        )
        assertTrue(respArray.text.contains("data structure"))

        val respTuple = router.routeQuery(
            sessionId = "sess_slm2",
            query = "what is a tuple",
            telemetry = telemetry,
            connectionState = ConnectionState.DISCONNECTED
        )
        assertTrue(respTuple.text.contains("immutable"))

        val respUnit = router.routeQuery(
            sessionId = "sess_slm3",
            query = "10 km to miles",
            telemetry = telemetry,
            connectionState = ConnectionState.DISCONNECTED
        )
        assertTrue(respUnit.text.contains("6.21 miles"))
    }
}
