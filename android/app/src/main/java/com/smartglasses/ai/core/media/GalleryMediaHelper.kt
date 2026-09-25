package com.smartglasses.ai.core.media

import android.content.ContentValues
import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.net.Uri
import android.os.Build
import android.provider.MediaStore
import android.util.Log
import java.io.ByteArrayOutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

object GalleryMediaHelper {
    private const val TAG = "SmartGlasses.Gallery"

    fun saveJpegBytes(
        context: Context,
        jpegBytes: ByteArray,
        titlePrefix: String = "EVA_Capture"
    ): Uri? {
        if (jpegBytes.isEmpty()) return null
        return try {
            val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())
            val filename = "${titlePrefix}_$timestamp.jpg"

            val values = ContentValues().apply {
                put(MediaStore.Images.Media.DISPLAY_NAME, filename)
                put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
                put(MediaStore.Images.Media.DATE_ADDED, System.currentTimeMillis() / 1000)
                put(MediaStore.Images.Media.DATE_TAKEN, System.currentTimeMillis())
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    put(MediaStore.Images.Media.RELATIVE_PATH, "Pictures/EVA_SmartGlasses")
                    put(MediaStore.Images.Media.IS_PENDING, 1)
                }
            }

            val resolver = context.contentResolver
            val uri = resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
            if (uri != null) {
                resolver.openOutputStream(uri)?.use { out ->
                    out.write(jpegBytes)
                    out.flush()
                }

                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    values.clear()
                    values.put(MediaStore.Images.Media.IS_PENDING, 0)
                    resolver.update(uri, values, null, null)
                }
                Log.i(TAG, "Successfully saved photo to Gallery: $uri ($filename)")
                uri
            } else {
                Log.e(TAG, "Failed to create MediaStore entry for $filename")
                null
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error saving photo to Gallery: ${e.message}", e)
            null
        }
    }

    fun saveSamplePhoto(context: Context, label: String = "EVA Smart Glasses Photo"): Uri? {
        val width = 640
        val height = 480
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        canvas.drawColor(Color.rgb(24, 28, 36))

        val paint = Paint().apply {
            color = Color.WHITE
            textSize = 28f
            isAntiAlias = true
            textAlign = Paint.Align.CENTER
        }
        val subPaint = Paint().apply {
            color = Color.rgb(230, 126, 34)
            textSize = 20f
            isAntiAlias = true
            textAlign = Paint.Align.CENTER
        }

        canvas.drawText(label, width / 2f, height / 2f - 20, paint)
        canvas.drawText("XIAO ESP32-S3 Sense  OV2640", width / 2f, height / 2f + 25, subPaint)

        val stream = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.JPEG, 92, stream)
        val bytes = stream.toByteArray()
        return saveJpegBytes(context, bytes, "EVA_Photo")
    }
}
