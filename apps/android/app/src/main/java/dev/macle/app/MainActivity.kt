package dev.macle.app

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.Gravity
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import dev.macle.app.core.NativeCore

/**
 * First Android vertical slice: import and validate a MACLE session manifest
 * using the shared Rust core. MediaProjection capture is deliberately a
 * separate next step; this app does not yet record meetings.
 */
class MainActivity : Activity() {
    private lateinit var status: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(32, 32, 32, 32)
        }
        val heading = TextView(this).apply {
            text = "MACLE · Android core check"
            textSize = 22f
        }
        status = TextView(this).apply {
            text = "Import a synthetic MACLE session manifest to validate it with the shared Rust core."
            textSize = 16f
            setPadding(0, 24, 0, 24)
        }
        val button = Button(this).apply {
            text = "Import session manifest"
            setOnClickListener { openManifestPicker() }
        }
        layout.addView(heading)
        layout.addView(status)
        layout.addView(button)
        setContentView(layout)
    }

    private fun openManifestPicker() {
        val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "application/json"
        }
        startActivityForResult(intent, REQUEST_MANIFEST)
    }

    @Deprecated("Use Activity Result APIs in the next UI refinement.")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode != REQUEST_MANIFEST || resultCode != RESULT_OK) return
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

    companion object {
        private const val REQUEST_MANIFEST = 4101
    }
}
