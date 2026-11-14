# MACLE Android — first native core integration

This is the first Android vertical slice. It is intentionally small: the app imports a MACLE session manifest and validates it by calling the same Rust core compiled as a native Android library. It does **not** yet capture a meeting or request MediaProjection.

## Build the shared Rust library

Prerequisites: Rust, Android SDK/NDK, Android Studio/Gradle, and cargo-ndk.

From the repository root:

```sh
cargo install cargo-ndk
./scripts/build-android-core.sh
```

Then open `apps/android` in Android Studio and run the `app` configuration on an Android 10+ device/emulator.

The Rust library is built for `arm64-v8a` by the script. Add other ABI targets only when needed.

## Smoke test

1. Build and launch MACLE.
2. Select **Import session manifest**.
3. Choose `tests/fixtures/session-manifest-v1.json`.
4. The app should report that the manifest is valid.

## Boundary

- This app is a native integration proof, not yet the Android capture MVP.
- No network permission or agent streaming is present.
- The shared core validates the contract; it does not acquire media.
- The next Android implementation step is an explicit, user-authorized MediaProjection screen-capture adapter with visible foreground-service lifecycle and synthetic-only test gating.
- AudioPlaybackCapture remains a separate unverified capability and must not be inferred from screen capture.
