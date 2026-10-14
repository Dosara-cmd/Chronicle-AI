package com.chronicleai.chronicle_ai

import android.content.ContentValues
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.io.File
import java.io.FileInputStream

class MainActivity : FlutterActivity() {
    private val channelName =
        "com.chronicleai.chronicle_ai/video_library"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            channelName
        ).setMethodCallHandler { call, result ->
            when (call.method) {
                "saveVideo" -> {
                    val sourcePath = call.argument<String>("sourcePath")
                    val displayName = call.argument<String>("displayName")

                    if (sourcePath.isNullOrBlank() ||
                        displayName.isNullOrBlank()
                    ) {
                        result.error(
                            "INVALID_ARGUMENT",
                            "A video path and file name are required.",
                            null
                        )
                        return@setMethodCallHandler
                    }

                    try {
                        val uri = saveVideoToMediaStore(
                            sourcePath,
                            displayName
                        )
                        result.success(uri.toString())
                    } catch (error: Exception) {
                        result.error(
                            "SAVE_FAILED",
                            error.message ?: "Could not save the MP4 video.",
                            null
                        )
                    }
                }

                else -> result.notImplemented()
            }
        }
    }

    private fun saveVideoToMediaStore(
        sourcePath: String,
        displayName: String
    ): android.net.Uri {
        val source = File(sourcePath)

        if (!source.exists() || !source.isFile || source.length() == 0L) {
            throw IllegalArgumentException(
                "The generated MP4 does not exist or is empty."
            )
        }

        val resolver = applicationContext.contentResolver
        val collection =
            MediaStore.Video.Media.EXTERNAL_CONTENT_URI

        val values = ContentValues().apply {
            put(MediaStore.MediaColumns.DISPLAY_NAME, displayName)
            put(MediaStore.MediaColumns.MIME_TYPE, "video/mp4")

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                put(
                    MediaStore.MediaColumns.RELATIVE_PATH,
                    "${Environment.DIRECTORY_MOVIES}/Chronicle AI"
                )
                put(MediaStore.MediaColumns.IS_PENDING, 1)
            } else {
                @Suppress("DEPRECATION")
                put(
                    MediaStore.MediaColumns.DATA,
                    File(
                        Environment.getExternalStoragePublicDirectory(
                            Environment.DIRECTORY_MOVIES
                        ),
                        "Chronicle AI/$displayName"
                    ).absolutePath
                )
            }
        }

        val destination = resolver.insert(collection, values)
            ?: throw IllegalStateException(
                "Android could not create a video-library entry."
            )

        try {
            val output = resolver.openOutputStream(destination, "w")
                ?: throw IllegalStateException(
                    "Android could not open the destination video."
                )

            FileInputStream(source).use { input ->
                output.use { target ->
                    input.copyTo(target)
                    target.flush()
                }
            }

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                val readyValues = ContentValues().apply {
                    put(MediaStore.MediaColumns.IS_PENDING, 0)
                }
                resolver.update(destination, readyValues, null, null)
            }

            return destination
        } catch (error: Exception) {
            resolver.delete(destination, null, null)
            throw error
        }
    }
}
