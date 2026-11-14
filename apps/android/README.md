# MACLE Android — first native capture prototype

The Android shell contains a deliberately limited, synthetic-only screen-capture vertical slice. It calls the same Rust core as the Chrome WebAssembly build.

## Build and install

See [the shared installation guide](../../docs/INSTALLATION.md#android) for prerequisites and the reproducible APK build:

~~~sh
sh scripts/build-android-apk.sh
adb install -r dist/MACLE-android-debug.apk
~~~

The build script compiles the Rust JNI library for arm64-v8a, builds the Android debug APK, and copies it to dist/. Android Studio can also open this directory as a Gradle project after the JNI library has been built.

## What works in this prototype

- Native Android application shell (minimum Android 10 / API 29).
- Explicit checkbox attestation for synthetic test content.
- Android MediaProjection consent flow initiated by the user.
- Foreground service with a persistent capture notification.
- Local screen-only MP4 recording using MediaProjection + MediaRecorder.
- Session manifest generation with separate source states, capture limitations, timestamps and a streamed SHA-256 file digest.
- Manifest validation through the shared Rust core over JNI.
- Export of the manifest and media file through Android's Sharesheet / FileProvider.
- Import and validation of an existing manifest, including the shared Chrome fixture.

## Explicitly not implemented

- Remote Meet playback audio capture (AudioPlaybackCapture is not implemented or verified).
- Microphone capture.
- Participant-specific media tracks, transcription, or semantic interpretation.
- Agent streaming, network permissions, or any hosted MACLE service.
- A single ZIP package; this prototype exports the manifest and media as two files.
- Production lifecycle recovery, exhaustive device/OS compatibility, or long-duration reliability.

The manifest records playback audio and microphone as not_requested, not as successfully captured sources. If screen recording fails or produces an empty file, the screen source is marked interrupted.

## Synthetic smoke test

1. Install and launch MACLE.
2. Check the synthetic-only attestation. Do not use real meeting participants or voices.
3. Tap **Authorize and start screen capture** and approve Android's system capture dialog.
4. Display a project-controlled synthetic test screen/stimulus; the app records the display locally.
5. Tap **Stop capture**. The service finalizes the MP4 and validates the session manifest with the Rust core.
6. Tap **Export last session** and send both files to a local test consumer.
7. Optionally use **Import and validate session manifest** to validate a Chrome-generated fixture or the exported manifest.

## Platform and safety boundary

- Screen capture is user-authorized through MediaProjection; the operating system can revoke it.
- A visible foreground service is used while recording.
- The capture may include all visible content on the selected display; use only controlled synthetic material under the current Stage A approval.
- The first adapter records video only. It must not imply that Android Meet playback audio can be captured.
- Physical-device tests are still required for orientation changes, display/app-window selection, lock, interruption, revocation, low storage, process death and long-duration behavior.
