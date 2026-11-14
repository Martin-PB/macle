# MACLE shared core (first implementation slice)

This crate is the platform-independent contract implementation. It deliberately does not acquire screen, audio, microphone, or meeting-platform data.

## Current scope

- Typed session manifest and observation envelope.
- Contract validation.
- SHA-256 helper.
- Append-only JSONL observation writer with per-source monotonic sequence enforcement.
- Native Rust library plus a WebAssembly-bindgen API for browser hosts.

## Build and test

From the repository root:

```sh
cargo test --workspace
cargo check --manifest-path core/macle-core/Cargo.toml
```

To build and test the browser module (requires Rust's `wasm32-unknown-unknown` target, `wasm-pack` and Node.js):

```sh
rustup target add wasm32-unknown-unknown
sh scripts/test-wasm-core.sh
```

The generated WASM package is a build artifact, not checked in. A Chrome extension build should bundle the generated JS/WASM pair and load it from its extension origin. Do not silently fall back to a different validation implementation if the module is missing in a production build.

## Android integration

Android should call the same Rust crate through JNI or a generated binding layer. The Kotlin adapter owns MediaProjection, AudioPlaybackCapture, microphone permissions, foreground services and lifecycle. It must pass only normalized session/observation data to this core; this crate does not imply that Meet playback audio is capturable.

## Contract ownership

The JSON Schemas in `/schemas` are the language-neutral wire contracts. Rust types are one implementation, not the sole authority. Other clients must pass the same fixtures and preserve source/status distinctions.
