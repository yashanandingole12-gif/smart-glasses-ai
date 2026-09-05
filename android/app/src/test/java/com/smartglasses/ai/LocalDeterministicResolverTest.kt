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
    fun testMathArithmeticResolvesLocally() {
        val resp = resolver.resolve("What is 15 * 8?", telemetry, "sess_m1")
        assertNotNull(resp)
        assertEquals(ResponseSource.LOCAL_DETERMINISTIC, resp?.source)
        assertTrue(resp?.text?.contains("120") == true)
    }

    @Test
    fun testMathTableResolvesLocally() {
        val resp = resolver.resolve("Table of 7", telemetry, "sess_m2")
        assertNotNull(resp)
        assertEquals(ResponseSource.LOCAL_DETERMINISTIC, resp?.source)
        assertTrue(resp?.text?.contains("7") == true && resp?.text?.contains("70") == true)
    }

    @Test
    fun testMathPercentageResolvesLocally() {
        val resp = resolver.resolve("20% of 150", telemetry, "sess_m3")
        assertNotNull(resp)
        assertEquals(ResponseSource.LOCAL_DETERMINISTIC, resp?.source)
        assertTrue(resp?.text?.contains("30") == true)
    }

    @Test
    fun testMathPowerAndRootResolvesLocally() {
        val respPow = resolver.resolve("2^8", telemetry, "sess_m4")
        assertNotNull(respPow)
        assertTrue(respPow?.text?.contains("256") == true)

        val respSqrt = resolver.resolve("square root of 144", telemetry, "sess_m5")
        assertNotNull(respSqrt)
        assertTrue(respSqrt?.text?.contains("12") == true)
    }

    @Test
    fun testMathReciprocalResolvesLocally() {
        val resp = resolver.resolve("reciprocal of 4", telemetry, "sess_m6")
        assertNotNull(resp)
        assertTrue(resp?.text?.contains("0.25") == true)
    }

    @Test
    fun testMathHinglishResolvesLocally() {
        val resp = resolver.resolve("25 aur 15 kitna hota hai", telemetry, "sess_m7")
        assertNotNull(resp)
        assertTrue(resp?.text?.contains("40") == true)
    }

    @Test
    fun testNonDeterministicReturnsNull() {
        val resp = resolver.resolve("Check my email", telemetry, "sess_7")
        assertNull(resp)
    }
}
