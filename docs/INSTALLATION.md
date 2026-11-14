# Build and install the first MACLE capture prototypes

This guide builds the current Stage A prototypes from source. Both paths remain **synthetic-test-only and local-only**. Do not capture real participants, real meeting audio, or real meeting content. Neither build sends data to a MACLE server or third-party processing service.

The two adapters have different capabilities:

| Host | Current capture | Output |
|---|---|---|
| Chrome | Selected rendered Google Meet tab and browser-exposed tab audio; optional microphone is separately gated to synthetic test audio | WebM recording and JSON session manifest |
| Android | User-authorized display capture only; no playback audio or microphone | MP4 recording and JSON session manifest |

## Chrome

### Install the prebuilt extension (recommended)

A versioned, prebuilt extension ZIP is published on the repository's GitHub Releases page:

- [MACLE Chrome releases](https://github.com/Martin-PB/macle/releases)

No Rust, Cargo, wasm-pack, Node.js, ZIP utility, or local compilation is needed to install a published release.

1. Download the asset named `macle-chrome-extension.zip` from the selected release.
2. Extract the ZIP into a permanent folder. Do not delete or move that folder while the extension is installed.
3. Open `chrome://extensions`.
4. Enable **Developer mode**.
5. Select **Load unpacked** and choose the extracted folder containing `manifest.json`.
6. Pin MACLE to the toolbar if desired.
7. Open the extension's options and explicitly attest to synthetic-only testing.
8. Open a synthetic Google Meet test session.
9. Click the MACLE toolbar icon to start. Click it again to stop and save the WebM and manifest separately.

Chrome will load the extension from the extracted folder. This is a developer-mode installation, not a Chrome Web Store installation; Chrome may display a developer-mode notice. To update, download and extract the newer release, then use **Reload** on the extension card or remove the old unpacked folder and load the new one.

Check the release's `SHA256SUMS.txt` before installation if you want to verify the downloaded ZIP. The release also includes `BUILD-PROVENANCE.txt`, identifying the source commit and build tool versions.

The release ZIP contains the compiled shared Rust/WASM runtime. Installing it does not require building that runtime locally.

### Build from source (maintainers and contributors)


### Prerequisites

- Rust toolchain and rustup
- wasm-pack
- Node.js 22 or newer
- zip

Install the WebAssembly packager if it is not already present:

~~~sh
cargo install wasm-pack
~~~

From the repository root:

~~~sh
sh scripts/package-chrome-extension.sh
~~~

The script builds the shared Rust core for WebAssembly, validates both shared JSON fixtures, checks the incremental SHA-256 implementation against a known vector, syntax-checks the extension JavaScript, and creates:

    dist/macle-chrome-extension.zip

To load directly from the source tree instead of the ZIP:

1. Open chrome://extensions.
2. Enable **Developer mode**.
3. Select **Load unpacked**.
4. Choose connectors/google-meet/chrome-extension.
5. Open the extension's options and explicitly attest to synthetic-only testing.
6. Open a synthetic Google Meet test session.
7. Click the MACLE toolbar icon to start. Click it again to stop and save the WebM and manifest separately.

The generated core-wasm directory is intentionally ignored by Git; the packaging script creates it before producing the ZIP. A missing or invalid WASM runtime blocks capture rather than falling back to a weaker validator.

The extension records the rendered tab, not individual participant tracks. Tab audio availability depends on what Chrome exposes for that tab. Microphone capture is off by default and must remain disabled unless the input is synthetic test audio.

## Android

### Prerequisites

- Rust toolchain and rustup
- cargo-ndk
- JDK 17 or newer
- Android SDK and NDK
- Gradle 8.9 or newer (the project uses Android Gradle Plugin 8.7.3)
- A physical Android 10+ device for the MediaProjection smoke test

Install the Rust Android build helper if needed:

~~~sh
cargo install cargo-ndk
~~~

Set ANDROID_HOME or ANDROID_SDK_ROOT to the Android SDK location. Ensure the NDK is installed through SDK Manager and discoverable by cargo-ndk.

From the repository root:

~~~sh
sh scripts/build-android-apk.sh
~~~

The script builds the shared Rust JNI library for arm64-v8a, assembles the debug APK, and copies it to:

    dist/MACLE-android-debug.apk

Install it on a connected device with:

~~~sh
adb install -r dist/MACLE-android-debug.apk
~~~

Then:

1. Launch MACLE.
2. Confirm the synthetic-only test attestation.
3. Start screen capture and accept Android's system MediaProjection prompt.
4. Switch to a controlled synthetic test screen or synthetic Meet session.
5. Return to MACLE or use the persistent notification to stop capture.
6. Export the MP4 and manifest using the app's export action.

Android captures the display only. It does not capture Google Meet playback audio or microphone input. MediaProjection can be revoked by Android at any time. The current prototype does not yet promise recovery after process death, orientation changes, storage exhaustion, or long-duration recording.

## Download prebuilt artifacts from GitHub Actions

The MACLE prototype build workflow builds both targets on pull requests and pushes to main. When both jobs pass, it publishes two temporary artifacts for 14 days:

- macle-chrome-extension — the packaged Chrome extension ZIP.
- macle-android-debug — the unsigned debug APK for arm64-v8a Android devices.

To retrieve them, open the successful **MACLE prototype builds** run in the repository's Actions tab and download the artifacts shown at the bottom of the run summary.

For Chrome, extract the ZIP and load the extracted directory from chrome://extensions using Developer mode and **Load unpacked**.

For Android, install the debug APK on a connected device with adb install -r MACLE-android-debug.apk. It is a development build, not a Play Store-signed release.

## Validation boundary

The scripts validate the shared Rust/WASM contract path and build artifacts. They do not prove that Chrome can capture every Meet configuration or that Android can capture Meet playback audio. A physical-device/browser smoke test remains necessary before treating either adapter as operationally validated.

No CI or physical-device test result is implied by a successful local build.
