package dev.macle.app.core

/**
 * Thin JNI facade over the same Rust core used by the browser's WASM build.
 * The Android capture adapter must remain responsible for OS permissions and media acquisition.
 */
object NativeCore {
    init {
        System.loadLibrary("macle_core")
    }

    /** Returns an empty string when valid, otherwise a human-readable validation error. */
    external fun validateManifestJson(json: String): String

    /** Returns an empty string when valid, otherwise a human-readable validation error. */
    external fun validateObservationJson(json: String): String
}
