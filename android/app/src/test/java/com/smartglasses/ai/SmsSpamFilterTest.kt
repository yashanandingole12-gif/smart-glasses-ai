package com.smartglasses.ai

import com.smartglasses.ai.core.sms.SmsCategory
import com.smartglasses.ai.core.sms.SmsItem
import com.smartglasses.ai.core.sms.SmsSpamFilter
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class SmsSpamFilterTest {

    @Test
    fun testPersonalContactClassification() {
        val res = SmsSpamFilter.classify(
            senderAddress = "+919876543210",
            body = "Hey, are we still meeting for lunch today?",
            contactName = "Rahul Sharma"
        )
        assertEquals(SmsCategory.PERSONAL, res.category)
        assertFalse(res.isSpamOrPromo)
        assertFalse(res.isScamOrSuspicious)
        assertEquals("LOW", res.urgency)
    }

    @Test
    fun testScamElectricityThreatClassification() {
        val res = SmsSpamFilter.classify(
            senderAddress = "9876543210",
            body = "Dear customer, your electricity power will be disconnected tonight at 9:30 PM due to unpaid bill. Call 9876543210 immediately.",
            contactName = null
        )
        assertEquals(SmsCategory.SCAM, res.category)
        assertTrue(res.isSpamOrPromo)
        assertTrue(res.isScamOrSuspicious)
        assertEquals("HIGH", res.urgency)
    }

    @Test
    fun testScamLotteryPrizeClassification() {
        val res = SmsSpamFilter.classify(
            senderAddress = "VM-WINNER",
            body = "Congratulations! You won Rs 25,00,000 in KBC Jackpot lucky draw. Claim your prize now!",
            contactName = null
        )
        assertEquals(SmsCategory.SCAM, res.category)
        assertTrue(res.isSpamOrPromo)
        assertTrue(res.isScamOrSuspicious)
    }

    @Test
    fun testSuspiciousShortlinkClassification() {
        val res = SmsSpamFilter.classify(
            senderAddress = "AD-UNKNOWN",
            body = "Urgent: Click here to verify your account credentials bit.ly/verify3918 immediately.",
            contactName = null
        )
        assertEquals(SmsCategory.SUSPICIOUS, res.category)
        assertTrue(res.isSpamOrPromo)
        assertTrue(res.isScamOrSuspicious)
        assertEquals("HIGH", res.urgency)
    }

    @Test
    fun testImportantOtpClassification() {
        val res = SmsSpamFilter.classify(
            senderAddress = "VM-HDFCBK",
            body = "Your OTP is 482910 for transaction of Rs 1,500.00 at Amazon. Do not share with anyone.",
            contactName = null
        )
        assertEquals(SmsCategory.IMPORTANT, res.category)
        assertFalse(res.isSpamOrPromo)
        assertFalse(res.isScamOrSuspicious)
        assertEquals("HIGH", res.urgency)
    }

    @Test
    fun testImportantTravelDeliveryClassification() {
        val res = SmsSpamFilter.classify(
            senderAddress = "AX-BLRDEL",
            body = "Your courier package is out for delivery today. Track with tracking id 83910283.",
            contactName = null
        )
        assertEquals(SmsCategory.IMPORTANT, res.category)
        assertFalse(res.isSpamOrPromo)
        assertFalse(res.isScamOrSuspicious)
        assertEquals("MEDIUM", res.urgency)
    }

    @Test
    fun testSystemTelecomClassification() {
        val res = SmsSpamFilter.classify(
            senderAddress = "JD-JIOINF",
            body = "You have consumed 100% daily data limit. Your validity expires on 24-Oct-2026.",
            contactName = null
        )
        assertEquals(SmsCategory.SYSTEM, res.category)
        assertFalse(res.isSpamOrPromo)
        assertFalse(res.isScamOrSuspicious)
    }

    @Test
    fun testPromotionalAdClassification() {
        val res = SmsSpamFilter.classify(
            senderAddress = "BP-MYNTRA",
            body = "Mega Sale! Flat 50% off on all sneakers today only. Use coupon code SNEAK50. Shop now!",
            contactName = null
        )
        assertEquals(SmsCategory.PROMOTIONAL, res.category)
        assertTrue(res.isSpamOrPromo)
        assertFalse(res.isScamOrSuspicious)
    }

    @Test
    fun testFilterRelevantMessagesFiltersOutSpamAndPromo() {
        val messages = listOf(
            SmsItem("1", "+919876543210", "Are you home?", 1000L, "10:00 AM", "Papa"),
            SmsItem("2", "BP-MYNTRA", "Flat 40% discount on clothing today!", 2000L, "10:05 AM", null),
            SmsItem("3", "9876543210", "Electricity power cut tonight! Pay immediately.", 3000L, "10:10 AM", null),
            SmsItem("4", "VM-HDFCBK", "Your OTP is 829103 for login.", 4000L, "10:15 AM", null)
        )

        val (relevant, filteredCount) = SmsSpamFilter.filterRelevantMessages(messages, includePromotions = false)
        assertEquals(2, relevant.size)
        assertEquals(2, filteredCount)
        assertEquals("1", relevant[0].id)
        assertEquals("4", relevant[1].id)
    }
}
