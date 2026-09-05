package com.smartglasses.ai

import com.smartglasses.ai.core.network.BackendConfig
import org.junit.Assert.assertEquals
import org.junit.Test

class BackendConfigTest {

    @Test
    fun testNormalizeUrlStandard() {
        assertEquals("http://192.168.1.100:8001/", BackendConfig.normalizeUrl("http://192.168.1.100:8001"))
        assertEquals("http://192.168.1.100:8001/", BackendConfig.normalizeUrl("192.168.1.100:8001"))
    }

    @Test
    fun testNormalizeUrlWithTrailingZeroOrDigitsAfterPort() {
        assertEquals("http://10.252.162.120:8001/", BackendConfig.normalizeUrl("http://10.252.162.120:8001/0"))
        assertEquals("http://10.252.162.120:8001/", BackendConfig.normalizeUrl("http://10.252.162.120:8001/0/"))
    }

    @Test
    fun testNormalizeUrlSubnetTypo() {
        assertEquals("http://192.168.137.1:8001/", BackendConfig.normalizeUrl("192.168137.1:8001"))
    }
}
