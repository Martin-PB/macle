package dev.macle.app.capture

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.MediaRecorder
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.util.DisplayMetrics
import android.view.WindowManager
import android.content.Context
import android.content.pm.ServiceInfo
import dev.macle.app.core.NativeCore
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.security.MessageDigest
import java.time.Instant
import java.util.UUID

/**
 * Synthetic-only, user-authorized screen capture prototype.
 * It intentionally records no system playback audio or microphone input.
 */
class ScreenCaptureService : Service() {
    private var projection: MediaProjection? = null
    private var recorder: MediaRecorder? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var sessionDirectory: File? = null
    private var mediaFile: File? = null
    private var sessionId: String? = null
    private var startedAt: String? = null
    private var finishing = false
    private var recorderFinalized = false

    private val projectionCallback = object : MediaProjection.Callback() {
        override fun onStop() {
            finishCapture(stopProjection = false)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_STOP -> finishCapture(stopProjection = true)
            ACTION_START -> {
                val resultCode = intent.getIntExtra(EXTRA_RESULT_CODE, 0)
                val data = if (Build.VERSION.SDK_INT >= 33) {
                    intent.getParcelableExtra(EXTRA_PROJECTION_DATA, Intent::class.java)
                } else {
                    @Suppress("DEPRECATION")
                    intent.getParcelableExtra(EXTRA_PROJECTION_DATA)
                }
                if (data == null) {
                    stopSelf()
                    return START_NOT_STICKY
                }
                startCapture(resultCode, data)
            }
        }
        return START_NOT_STICKY
    }

    private fun startCapture(resultCode: Int, data: Intent) {
        if (projection != null || finishing) return
        try {
            val notification = buildNotification("Recording the device screen locally")
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                startForeground(
                    NOTIFICATION_ID,
                    notification,
                    ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION
                )
            } else {
                startForeground(NOTIFICATION_ID, notification)
            }

            val manager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
            projection = manager.getMediaProjection(resultCode, data)
            projection?.registerCallback(projectionCallback, Handler(Looper.getMainLooper()))

            sessionId = UUID.randomUUID().toString()
            startedAt = Instant.now().toString()
            sessionDirectory = File(filesDir, "sessions/$sessionId").apply { mkdirs() }
            val mediaDirectory = File(sessionDirectory, "media/screen").apply { mkdirs() }
            mediaFile = File(mediaDirectory, "capture.mp4")

            val metrics = DisplayMetrics()
            @Suppress("DEPRECATION")
            (getSystemService(Context.WINDOW_SERVICE) as WindowManager).defaultDisplay.getRealMetrics(metrics)
            val scale = minOf(1f, 1920f / metrics.widthPixels, 1080f / metrics.heightPixels)
            val width = ((metrics.widthPixels * scale).toInt() / 2) * 2
            val height = ((metrics.heightPixels * scale).toInt() / 2) * 2
            val density = metrics.densityDpi

            val mediaRecorder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                MediaRecorder(this)
            } else {
                @Suppress("DEPRECATION")
                MediaRecorder()
            }
            recorder = mediaRecorder
            mediaRecorder.setVideoSource(MediaRecorder.VideoSource.SURFACE)
            mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            mediaRecorder.setVideoEncoder(MediaRecorder.VideoEncoder.H264)
            mediaRecorder.setVideoSize(width, height)
            mediaRecorder.setVideoFrameRate(30)
            mediaRecorder.setVideoEncodingBitRate(4_000_000)
            mediaRecorder.setOutputFile(mediaFile!!.absolutePath)
            mediaRecorder.prepare()

            virtualDisplay = projection!!.createVirtualDisplay(
                "MACLE-screen-capture",
                width,
                height,
                density,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                mediaRecorder.surface,
                null,
                null
            )
            mediaRecorder.start()
            recorderFinalized = false
        } catch (failure: Exception) {
            finishCapture(stopProjection = true)
        }
    }

    private fun finishCapture(stopProjection: Boolean) {
        if (finishing) return
        finishing = true

        try {
            val activeRecorder = recorder
            if (activeRecorder != null) {
                try {
                    activeRecorder.stop()
                    recorderFinalized = true
                } catch (_: RuntimeException) {
                    // MediaRecorder can reject a very short/empty recording.
                    recorderFinalized = false
                }
                runCatching { activeRecorder.reset() }
                runCatching { activeRecorder.release() }
            }
            recorder = null
            virtualDisplay?.release()
            virtualDisplay = null

            val currentProjection = projection
            projection = null
            if (currentProjection != null) {
                if (stopProjection) {
                    runCatching { currentProjection.unregisterCallback(projectionCallback) }
                    currentProjection.stop()
                }
            }
            writeSessionManifest()
        } finally {
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
        }
    }

    private fun writeSessionManifest() {
        val directory = sessionDirectory ?: return
        val started = startedAt ?: Instant.now().toString()
        val ended = Instant.now().toString()
        val artifactFile = mediaFile
        val artifactExists = recorderFinalized && artifactFile != null && artifactFile.isFile && artifactFile.length() > 0L
        val sources = JSONArray()
            .put(source("android-screen", "screen", if (artifactExists) "available" else "interrupted",
                "User-approved MediaProjection screen recording."))
            .put(source("android-playback-audio", "playback_audio", "not_requested",
                "AudioPlaybackCapture is not implemented or verified in this prototype."))
            .put(source("android-microphone", "microphone", "not_requested",
                "Microphone capture is deliberately disabled in this prototype."))

        val artifacts = JSONArray()
        if (artifactExists && artifactFile != null) {
            artifacts.put(JSONObject()
                .put("path", "media/screen/capture.mp4")
                .put("media_type", "video/mp4")
                .put("size_bytes", artifactFile.length())
                .put("sha256", sha256File(artifactFile))
                .put("started_at", started)
                .put("ended_at", ended))
        }

        val manifest = JSONObject()
            .put("schema", "macle.session-manifest/v1")
            .put("session_id", sessionId ?: UUID.randomUUID().toString())
            .put("platform", "android")
            .put("started_at", started)
            .put("ended_at", ended)
            .put("sources", sources)
            .put("artifacts", artifacts)
            .put("limitations", JSONArray()
                .put("Screen-only prototype; no meeting playback audio or microphone is captured.")
                .put("MediaProjection captures the device display as rendered and may include unrelated visible content.")
                .put("Capture gaps, revocation or recorder failure are represented as an interrupted screen source."))
            .put("authorization", JSONObject()
                .put("test_scope", "synthetic_only")
                .put("egress", "local_only"))

        val validationError = NativeCore.validateManifestJson(manifest.toString())
        check(validationError.isEmpty()) { "Shared MACLE core rejected Android manifest: $validationError" }
        FileOutputStream(File(directory, "manifest.json")).use {
            it.write(manifest.toString(2).toByteArray(Charsets.UTF_8))
        }
        getSharedPreferences(PREFERENCES, MODE_PRIVATE).edit()
            .putString(LAST_SESSION_DIRECTORY, directory.absolutePath)
            .apply()
    }

    private fun source(id: String, kind: String, status: String, detail: String): JSONObject =
        JSONObject().put("source_id", id).put("kind", kind).put("status", status).put("detail", detail)

    private fun sha256File(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        FileInputStream(file).use { input ->
            val buffer = ByteArray(64 * 1024)
            while (true) {
                val count = input.read(buffer)
                if (count < 0) break
                digest.update(buffer, 0, count)
            }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "MACLE screen capture",
                NotificationManager.IMPORTANCE_LOW
            )
            getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
        }
    }

    private fun buildNotification(message: String): Notification {
        val builder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            Notification.Builder(this, CHANNEL_ID)
        } else {
            @Suppress("DEPRECATION")
            Notification.Builder(this)
        }
        return builder
            .setContentTitle("MACLE capture active")
            .setContentText(message)
            .setSmallIcon(android.R.drawable.ic_menu_camera)
            .setOngoing(true)
            .build()
    }

    override fun onDestroy() {
        if (!finishing && projection != null) finishCapture(stopProjection = true)
        super.onDestroy()
    }

    companion object {
        const val ACTION_START = "dev.macle.app.capture.START"
        const val ACTION_STOP = "dev.macle.app.capture.STOP"
        const val EXTRA_RESULT_CODE = "projection_result_code"
        const val EXTRA_PROJECTION_DATA = "projection_data"
        const val PREFERENCES = "macle_capture"
        const val LAST_SESSION_DIRECTORY = "last_session_directory"
        private const val CHANNEL_ID = "macle-capture"
        private const val NOTIFICATION_ID = 4102
    }
}
