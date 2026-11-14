# Cross-platform architecture feasibility: shared MACLE core

**Status:** study opened 2026-11-14. Candidate architecture only; no technology decision is baselined.

## Objective

Investigate one coherent MACLE product foundation for Android, iOS, Windows, Linux, macOS and browser/Chrome, maximizing shared code without pretending that operating systems expose identical capture capabilities.

**Proposed answer:** share the domain model, session engine, observation envelope, temporal/provenance logic, append-only storage, package format, integrity checks, capability reporting, conformance tests and agent-delivery protocol. Keep capture behind narrow native/browser adapters.

## 1. Shared core versus platform adapters

The shared core should own:
- Session lifecycle, stable identifiers and source registry.
- Canonical observation/event envelope and schema evolution.
- Clock domains, timestamp conversion, uncertainty and temporal alignment.
- Append-only observation log, media chunk indexing and integrity hashes.
- Durable local outbox, monotonic sequence numbers, idempotency, acknowledgements and replay.
- Portable package manifest, export/import and validation.
- Redaction/minimization policy hooks and audit records.
- Agent-neutral consumer API and transport abstraction.

Platform adapters should expose a capability contract: enumerate sources, request/observe permissions, start/stop/pause, emit timestamped chunks/events, report interruptions and clock discontinuities, and surface lifecycle/storage/thermal changes. Platform-specific types must not leak into the domain model.

A source unavailable on a platform is explicitly marked unavailable, not silently substituted by another modality. Microphone room audio must never be represented as equivalent to direct digital meeting playback.

## 2. Candidate implementation shape

### Preferred candidate to prototype: Rust shared core + native shells

Rust is a strong candidate for the shared engine: native compilation across targets, a WebAssembly target, mature serialization and cryptographic libraries, and C-compatible embedding. This is a prototype recommendation, not a language decision.

- **Android:** Kotlin shell and Android capture services; shared Rust core through JNI/generated bindings.
- **iOS/iPadOS:** Swift shell and ReplayKit/AVFoundation adapters; shared Rust core through a stable C ABI/generated bindings. Broadcast capture may require a ReplayKit Broadcast Upload Extension.
- **Windows:** native shell and Windows Graphics Capture plus supported audio loopback APIs; shared Rust library.
- **macOS:** native shell and ScreenCaptureKit/CoreAudio adapters subject to TCC permissions and entitlements.
- **Linux:** desktop shell and PipeWire/xdg-desktop-portal capture where available; compositor and audio-server differences remain visible.
- **Browser/Chrome:** TypeScript extension/web adapter using browser-mediated capture APIs; same schemas and package/stream protocol. WASM can host portable pure logic.

The current Python Google Meet connector remains a working reference/integration during migration. Do not rewrite it merely for language uniformity; first extract stable semantics and interfaces.

### Alternatives to compare

- **Kotlin Multiplatform:** promising shared Kotlin domain/application code for Android/iOS/desktop, but native capture adapters and Swift interop remain; assess exact browser/WASM and library maturity.
- **Flutter/Dart:** potentially broad shared UI, but capture plugins, extensions and lifecycle constraints remain platform-specific.
- **Tauri:** attractive Rust + web UI desktop shell; mobile support and capture plugin coverage require validation.
- **WebAssembly-first:** useful for portable logic, browser execution and sandboxing; not an operating-system capture API.

No UI framework should be selected before a capability prototype and a small end-to-end vertical slice.

## 3. Capture capability reality

| Platform | Screen/window candidate | Meeting/system audio candidate | Microphone | Main constraints |
|---|---|---|---|---|
| Android | MediaProjection | AudioPlaybackCapture only if source app usage/policy permits | Android recording APIs | Runtime consent, foreground-service rules, source-app policy, OEM variance |
| iOS/iPadOS | ReplayKit; broadcast extension | ReplayKit broadcast audio in supported flows | ReplayKit/AVAudioSession | App sandbox, user-initiated system flow, extension lifecycle; no unrestricted app-to-app capture |
| Windows | Windows Graphics Capture / Desktop Duplication | WASAPI loopback | WASAPI capture | Consent indicators, protected content, endpoint/session mixing and version behavior |
| macOS | ScreenCaptureKit | ScreenCaptureKit audio where supported; CoreAudio as applicable | AVAudioEngine/CoreAudio | TCC permissions, entitlements, OS-version requirements |
| Linux | PipeWire via xdg-desktop-portal | PipeWire monitor/source nodes | PipeWire/ALSA/PulseAudio paths | Wayland portals, compositor and audio-server differences |
| Browser/Chrome | getDisplayMedia / extension tabCapture | Tab audio where explicitly exposed | getUserMedia | Browser permissions, user activation, tab/window scope, enterprise policy; no unrestricted global loopback |

This is a candidate matrix, not verified MACLE capability. Android Meet playback audio remains unestablished. iOS ReplayKit must be tested against the precise Meet app and broadcast flow; do not assume arbitrary capture of another app's audio.

## 4. What WebAssembly can and cannot do

**Good WASM candidates:** schema validation, canonical serialization, event normalization, temporal/provenance calculations, chunk indexing, deterministic package validation, hashing of host-supplied bytes, shared rules, browser-side portable logic.

**WASM does not provide:** MediaProjection, ReplayKit, Windows/macOS/Linux capture APIs, OS permission prompts, entitlements, background execution, device routing or unrestricted file-system access.

A WASM module embedded in a native app needs host imports/bridges for capture, files, permissions and lifecycle. Those bridges are the platform adapters. WASM can maximize reuse and sandbox portable logic; it cannot eliminate native code.

## 5. Illustrative repository boundaries

    core/model/       domain types and observation envelope
    core/session/     lifecycle, clocks, source registry
    core/store/       append-only log and durable outbox
    core/package/     manifest, export/import, integrity
    core/transport/   agent-neutral streaming protocol
    core/wasm/        optional WASM target
    adapters/android/
    adapters/ios/
    adapters/windows/
    adapters/macos/
    adapters/linux/
    adapters/browser/
    apps/android/
    apps/ios/
    apps/desktop/
    apps/chrome-extension/
    connectors/google-meet/  current Python/Chrome reference
    schemas/
    conformance/

This is a conceptual boundary, not a request to create empty directories now. Canonical schemas should remain consumable by other-language implementations.

## 6. Conformance before UI convergence

Build a platform-neutral synthetic conformance suite for session identity/lifecycle; sequence and duplicate behavior; source identity/capability states; clocks/timestamps/uncertainty; chunk metadata and hashes; explicit gaps/revocations/interruption; package round-trip equivalence; outbox retry/ack/replay/idempotency; offline finalization; and the current synthetic-only authorization gate.

Platform hardware reports remain separate. A common conformance pass does not prove equal capture coverage. Record exact OS build, device, meeting-client version, route, permissions and evidence for each capability.

## 7. Staged implementation proposal

1. Stabilize session, observation, source, capability, chunk, package and stream contracts independently of UI.
2. Extract a minimal shared core: session log, serialization, hashes, package validator, outbox and deterministic tests. Prototype Rust native and WASM builds.
3. Prove two contrasting hosts (browser/Chrome and one native desktop or Android host) to validate the boundary.
4. Add Android and iOS shells/adapters; test on physical devices.
5. Add Windows, macOS and Linux adapters with capability-specific evidence.
6. Only then converge UI, choosing a framework that does not compromise native capture, accessibility, permissions or lifecycle.

## 8. Status and non-decisions

This study recommends a **shared domain/session engine with native platform capture adapters**, and recommends evaluating **Rust as the shared-core language with an optional WASM target**.

It does not decide Rust, Kotlin Multiplatform, Flutter, Tauri, UI framework, minimum OS versions, detailed package schema or platform release order. It does not establish that every platform can capture Google Meet audio/video. It does not authorize real-meeting capture or agent egress.

Existing synthetic-only/local-only Stage A boundaries remain unchanged. Optional streaming remains disabled unless explicitly configured and separately authorized for the data being transmitted.