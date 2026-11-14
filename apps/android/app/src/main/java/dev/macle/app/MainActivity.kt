package dev.macle.app

import android.app.Activity
import android.content.Intent
import android.media.projection.MediaProjectionManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.view.Gravity
import android.widget.Button
import android.widget.CheckBox
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.content.FileProvider
import androidx.core.content.ContextCompat
import dev.macle.app.capture.ScreenCaptureService
import dev.macle.app.core.NativeCore
import java.io.File

/**
 * Android vertical slice: synthetic-only MediaProjection screen capture,
 * portable manifest validation through the shared Rust core, and file hand-off.
 * Playback audio and microphone are deliberately not captured.
 */
class MainActivity : Activity() {
    private lateinit var status: TextView
    private lateinit var syntheticAttestation: CheckBox

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(32, 32, 32, 32)
        }
        val heading = TextView(this).apply {
            text = "MACLE · Android capture prototype"
            textSize = 22f
        }
        status = TextView(this).apply {
            text = "Screen-only capture. Playback audio and microphone are not captured."
            textSize = 16f
            setPadding(0, 24, 0, 24)
        }
        syntheticAttestation = CheckBox(this).apply {
            text = "I confirm this is a synthetic test meeting with no real participant data."
        }
        val start = Button(this).apply {
            text = "Authorize and start screen capture"
            setOnClickListener { requestScreenCapture() }
        }
        val stop = Button(this).apply {
            text = "Stop capture"
            setOnClickListener { stopScreenCapture() }
        }
        val export = Button(this).apply {
            text = "Export last session"
            setOnClickListener { exportLastSession() }
        }
        val import = Button(this).apply {
            text = "Import and validate session manifest"
            setOnClickListener { openManifestPicker() }
        }

        layout.addView(heading)
        layout.addView(status)
        layout.addView(syntheticAttestation)
        layout.addView(start)
        layout.addView(stop)
        layout.addView(export)
        layout.addView(import)
        setContentView(layout)
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS) != android.content.pm.PackageManager.PERMISSION_GRANTED) {
            requestPermissions(arrayOf(android.Manifest.permission.POST_NOTIFICATIONS), REQUEST_NOTIFICATIONS)
        }
    }

    private fun requestScreenCapture() {
        if (!syntheticAttestation.isChecked) {
            status.text = "Capture blocked: confirm the synthetic-only test boundary first."
            return
        }
        val manager = getSystemService(MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        startActivityForResult(manager.createScreenCaptureIntent(), REQUEST_PROJECTION)
    }

    private fun stopScreenCapture() {
        startService(Intent(this, ScreenCaptureService::class.java).apply {
            action = ScreenCaptureService.ACTION_STOP
        })
        status.text = "Stopping capture and finalizing the local session."
    }

    private fun exportLastSession() {
        val directoryPath = getSharedPreferences(
            ScreenCaptureService.PREFERENCES,
            MODE_PRIVATE
        ).getString(ScreenCaptureService.LAST_SESSION_DIRECTORY, null)
        if (directoryPath == null) {
            status.text = "No completed session is available to export."
            return
        }
        val directory = File(directoryPath)
        val manifest = File(directory, "manifest.json")
        val media = File(directory, "media/screen/capture.mp4")
        if (!manifest.isFile) {
            status.text = "The session manifest is missing."
            return
        }
        try {
            val authority = "$packageName.fileprovider"
            val uris = arrayListOf<Uri>(
                FileProvider.getUriForFile(this, authority, manifest)
            )
            if (media.isFile && media.length() > 0L) {
                uris.add(FileProvider.getUriForFile(this, authority, media))
            }
            val share = Intent(Intent.ACTION_SEND_MULTIPLE).apply {
                type = "*/*"
                putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            startActivity(Intent.createChooser(share, "Export MACLE session files"))
        } catch (failure: Exception) {
            status.text = "Export failed: ${failure.message ?: failure.javaClass.simpleName}"
        }
    }

    private fun openManifestPicker() {
        val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "application/json"
        }
        startActivityForResult(intent, REQUEST_MANIFEST)
    }

    @Deprecated("Kept minimal for this first prototype; migrate to Activity Result APIs during UI refinement.")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_PROJECTION) {
            if (resultCode != RESULT_OK || data == null) {
                status.text = "Screen capture was not authorized."
                return
            }
            val serviceIntent = Intent(this, ScreenCaptureService::class.java).apply {
                action = ScreenCaptureService.ACTION_START
                putExtra(ScreenCaptureService.EXTRA_RESULT_CODE, resultCode)
                putExtra(ScreenCaptureService.EXTRA_PROJECTION_DATA, data)
            }
            ContextCompat.startForegroundService(this, serviceIntent)
            status.text = "Screen capture started. Use Stop capture to finalize the session."
            return
        }

        if (requestCode == REQUEST_MANIFEST && resultCode == RESULT_OK) {
            val uri: Uri = data?.data ?: return
            try {
                val json = contentResolver.openInputStream(uri)?.bufferedReader()?.use { it.readText() }
                    ?: error("Could not read the selected manifest.")
                val error = NativeCore.validateManifestJson(json)
                status.text = if (error.isEmpty()) {
                    "Valid MACLE session manifest. Shared Rust core executed successfully on Android."
                } else {
                    "Manifest rejected: $error"
                }
            } catch (failure: Exception) {
                status.text = "Import failed: ${failure.message ?: failure.javaClass.simpleName}"
            } catch (failure: UnsatisfiedLinkError) {
                status.text = "Shared core library is missing. Build the Android Rust library first."
            }
        }
    }

    companion object {
        private const val REQUEST_PROJECTION = 4102
        private const val REQUEST_MANIFEST = 4101
        private const val REQUEST_NOTIFICATIONS = 4103
    }
}
