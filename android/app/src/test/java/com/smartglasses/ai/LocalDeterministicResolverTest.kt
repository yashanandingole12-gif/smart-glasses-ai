package com.smartglasses.ai

import com.smartglasses.ai.domain.models.ResponseSource
import com.smartglasses.ai.domain.models.WearableTelemetry
import com.smartglasses.ai.domain.usecases.LocalDeterministicResolver
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class LocalDeterministicResolverTest {

    private val resolver = LocalDeterministicResolver()
    private val telemetry = WearableTelemetry(
        batteryPercentage = 84,
        timeFormatted = "12:42 PM",
        period = "afternoon",
        locationName = "Nagpur",
        locationAvailable = true
    )

    @Test
    fun testTimeQueryResolvesLocally() {
        val resp = resolver.resolve("What time is it?", telemetry, "sess_1")
        assertNotNull(resp)
        assertEquals(ResponseSource.LOCAL_DETERMINISTIC, resp?.source)
        assertTrue(resp?.text?.contains("12:42 PM") == true)
        assertTrue((resp?.latencyMs ?: 999.0) < 500.0)
    }

    @Test
    fun testBatteryQueryResolvesLocally() {
        val resp = resolver.resolve("What's my battery?", telemetry, "sess_2")
        assertNotNull(resp)
        assertEquals(ResponseSource.LOCAL_DETERMINISTIC, resp?.source)
        assertEquals("Battery is 84 percent.", resp?.text)
    }

    @Test
    fun testLocationQueryResolvesLocally() {
        val resp = resolver.resolve("Where am I?", telemetry, "sess_3")
        assertNotNull(resp)
        assertEquals(ResponseSource.LOCAL_DETERMINISTIC, resp?.source)
        assertTrue(resp?.text?.contains("Nagpur") == true)
    }

    @Test
    fun testGreetingResolvesLocally() {
        val resp = resolver.resolve("Good afternoon", telemetry, "sess_4")
        assertNotNull(resp)
        assertEquals(ResponseSource.LOCAL_DETERMINISTIC, resp?.source)
        assertTrue(resp?.text?.contains("Good afternoon") == true)
    }

    @Test
    fun testDateQueryResolvesLocally() {
        val resp = resolver.resolve("What is today's date?", telemetry, "sess_5")
        assertNotNull(resp)
        assertEquals(ResponseSource.LOCAL_DETERMINISTIC, resp?.source)
        assertTrue(resp?.text?.startsWith("Today is") == true)
    }

    @Test
    fun testAcknowledgementResolvesLocally() {
        val resp = resolver.resolve("Thank you", telemetry, "sess_6")
        assertNotNull(resp)
        assertEquals("You're welcome.", resp?.text)
    }

    @Test
    fun testNonDeterministicReturnsNull() {
        val resp = resolver.resolve("Check my email", telemetry, "sess_7")
        assertNull(resp)
    }
}
