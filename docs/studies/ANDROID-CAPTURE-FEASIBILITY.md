# Android capture feasibility and product direction

**Status:** feasibility study opened 2026-11-14. Android is the owner's preferred user-facing form factor to investigate; this is not yet a verified capture capability or a final architecture decision.

**Product scenario:** an ordinary invitee receives a Google Meet invitation, joins through the normal Google Meet Android app or browser flow, and uses MACLE on the same Android device to capture what the OS and meeting client actually expose. MACLE produces a local, portable session package for a downstream agent. An optional, user-configured stream can send observations/chunks to an agent while the local recording remains authoritative.

## 1. Product shape

The Android app should be a **capture instrument and hand-off surface**, not the meeting host, a Workspace administration client, or necessarily the interpreter.

Two outputs are first-class:

1. **Offline-first package (required):** self-contained session manifest, append-only observations, source media/chunks where available, transcripts/derived artifacts, hashes, timestamps, provenance, permission/capability record, and explicit capture gaps. The user can share/export it to any compatible downstream agent.
2. **Optional live stream:** a user-selected agent endpoint receives bounded, ordered chunks and observations during the meeting. A durable local outbox, acknowledgements, idempotency and replay ensure network failure never interrupts capture. The stream is a separate data-egress decision and must not be silently enabled.

The agent is downstream and replaceable. MACLE's session format must not encode one vendor's agent API as its canonical model.

## 2. User flow

1. User opens the MACLE Android app and supplies/pastes the Meet invitation URL, or chooses the invitation in the normal Android share/open flow.
2. MACLE hands the URL to the installed Google Meet app or browser. The user signs in, chooses guest access if offered, and completes all pre-join and host-admission steps normally.
3. Once in the meeting, the user returns to MACLE or starts the already-authorized capture notification/control, grants Android's screen-capture consent, and explicitly starts the session.
4. MACLE shows a persistent capture notification and separate status for screen, playback audio, microphone and any other source. A source that is unavailable is marked unavailable; it is never silently inferred from another source.
5. User stops capture. MACLE finalizes hashes/indexes and exports a session package. Optionally, the user selects a compatible agent to receive the package or enables live streaming to a configured endpoint.
6. The agent interprets the package/stream. MACLE preserves raw observations, provenance and uncertainty separately from agent interpretations.

MACLE does not bypass Google sign-in, guest restrictions, waiting rooms, host admission, Android permissions, secure-window policy, or any capture policy of the meeting app.

## 3. Android platform capabilities and constraints

### 3.1 Screen capture — MediaProjection

Android's MediaProjection API can provide user-approved screen/display capture. The user must approve the OS capture request; the OS exposes active projection in system UI and allows the user to revoke it. On revocation, associated streams stop; the app must detect this and record a capture gap rather than continue as if capture were healthy.

For apps targeting Android 14/API 34 and later, MediaProjection foreground-service type and permission requirements apply. The screen-capture consent flow must occur before starting the relevant foreground service.

Official sources:
- Android: [Capture video and audio playback](https://developer.android.com/media/platform/av-capture)
- Android: [Media projection](https://developer.android.com/media/grow/media-projection)
- Android: [Foreground service types are required](https://developer.android.com/about/versions/14/changes/fgs-types-required)

**Not established:** whether all relevant Google Meet screens/video tiles/presentations are capturable on every supported device and app version. Secure surfaces, device policy, OS version, vendor behavior, app switching and projection revocation must be tested.

### 3.2 Remote meeting playback audio — AudioPlaybackCapture

Android 10/API 29 introduced AudioPlaybackCapture, which can capture audio played by another app only when the relevant requirements are met. Among them, the source app's audio usage must be UNKNOWN, GAME or MEDIA and its effective capture policy must permit capture. A source using voice-communication audio, or a source that disallows capture, is not made capturable by requesting MediaProjection.

Therefore **do not assume that Google Meet's remote audio can be captured by a third-party Android app**. Screen recording working does not prove audio capture works. The actual Google Meet Android app, exact version, call mode, audio route and device must be tested. Record a positive or negative result with a reproducible test and source audio fingerprint.

Official sources:
- Android: [Capture video and audio playback](https://developer.android.com/media/platform/av-capture)
- Android API: [AudioPlaybackCaptureConfiguration](https://developer.android.com/reference/android/media/AudioPlaybackCaptureConfiguration)

### 3.3 Microphone audio

Microphone capture is a distinct source. Android requires runtime microphone permission and, for background continuation, a correctly declared foreground service type and compliance with while-in-use restrictions. Simultaneous use of the microphone by Meet and MACLE, routing, speakerphone echo, Bluetooth/headset behavior, audio focus and device-vendor behavior need physical-device tests.

If MACLE captures room acoustics through its microphone, the source must be labelled as **device microphone / acoustic room capture**, not as direct digital remote-participant audio. The system must not merge it invisibly with playback audio.

Official source:
- Android: [Foreground service types are required](https://developer.android.com/about/versions/14/changes/fgs-types-required)

### 3.4 Foreground lifecycle and user control

Long-running capture must use the appropriate foreground service(s), visible notification and explicit user controls. Handle screen lock, app switching, calls/interruptions, battery saver, process death, storage exhaustion, thermal throttling, permission revocation and device restart. Do not claim a capture continues unless the media pipeline confirms it.

### 3.5 Meet Media API is not the fallback

Google's Meet Media API Developer Preview has been discontinued and Google says existing access ends on **2027-01-15**. Its restricted scopes and preview eligibility do not fit the ordinary invitee/no-Workspace-prerequisite core workflow. Do not build the Android app on it.

Official source:
- Google Meet developer documentation: [Google Meet](https://developers.google.com/workspace/meet)

## 4. Required capability matrix

Keep each source independent; update this matrix only with evidence.

| Source | Candidate Android mechanism | What it could provide | Critical limitation / test |
|---|---|---|---|
| Screen pixels | MediaProjection | Composite display/video of what is rendered | OS consent/revocation, secure surfaces, black frames, lifecycle; test Meet app and browser |
| Remote Meet audio | AudioPlaybackCapture | Digital playback mix if Meet permits capture | App usage and capture policy must allow it; do not assume voice-communication audio is eligible |
| Local room audio | RECORD_AUDIO + foreground microphone service | Acoustic mixture from the device microphone | Not equivalent to remote digital audio; Meet/MACLE mic arbitration, routing and echo |
| Meet participant metadata | No required API in core path | Potential optional enrichment only | REST/OAuth has separate account/permission constraints; not needed to capture |
| Transcript | Local ASR on captured audio or downstream agent | Timestamped speech hypotheses | Only as complete as the audio source; preserve confidence and gaps |
| Live agent | User-configured network transport | Incremental observations/media chunks | Egress approval, encryption, endpoint trust, durable queue and replay |
| Offline hand-off | Local package + Android Sharesheet/Storage Access Framework | Portable data for any downstream app | Package integrity, size, resumability and export/import tests |

Evidence status vocabulary:
- **Documented:** supported by current primary documentation.
- **Observed:** seen in a specific experiment, not yet repeatably tested.
- **Verified:** reproducible test with exact device/OS/app versions and evidence.
- **Not established:** insufficient evidence; do not claim capability.
- **Unavailable:** tested and unavailable under the stated configuration.

## 5. Portable session package and streaming semantics

The package must follow the MACLE observation envelope and preserve source distinctions. A proposed physical layout:

```text
macle-session-<session-id>/
  manifest.json
  observations.jsonl
  media/
    screen/
    playback-audio/
    microphone/
  transcripts/
  metadata/
  report/
```

The manifest should include:
- session ID and schema version;
- start/end times, wall-clock source and monotonic clock identity;
- device model, Android build, Meet app/browser version and capture implementation version;
- per-source capture configuration, permission state and actual active intervals;
- per-source clock precision/offset/uncertainty where measurable;
- media chunk names, MIME/codec, time interval, byte length and SHA-256;
- observation log identity and sequence range;
- capture interruptions, missing intervals, permission revocations and recovery events;
- optional agent destination and transfer receipt metadata, without storing secrets in the package.

For streaming, each bounded chunk/observation should have a stable session ID, source ID, monotonic sequence, source time interval, content hash and idempotency key. A durable local outbox retains unacknowledged data. The receiver acknowledges committed sequence/hash; retries must be idempotent. A stream outage changes delivery latency, not capture continuity. Local package and stream must derive from the same append-only session log.

## 6. Validation plan

Use only synthetic/project-controlled identities and content during the existing Stage A approval.

1. Build a test meeting and synthetic audio/video stimulus with known timestamps and signal markers.
2. Test screen-only MediaProjection and verify frame continuity, timestamps, revocation and black-frame detection.
3. Test AudioPlaybackCapture independently with known remote test audio; determine whether Meet playback is eligible on the exact device/version.
4. Test microphone independently and during Meet, across speakerphone, wired headset and Bluetooth where available.
5. Verify screen, playback audio and microphone are never confused or silently fused.
6. Exercise app switching, screen lock, incoming-call interruption, battery saver, low storage, process death, permission revocation and long-duration capture.
7. Export/import the session package and verify every hash, sequence, timestamp and gap.
8. Simulate network loss, receiver crash, duplicate delivery, reordered acknowledgements and replay; verify no data loss or double application.
9. Record exact device model, OS build, security patch, Meet version, capture settings and test evidence for every result.

A physical Android device is required for meaningful capture validation; emulator-only results are insufficient for the final capability claim.

## 7. Product and authorization boundaries

- No Google Workspace subscription, Workspace administrator role, Calendar, OAuth client, Meet REST API or Workspace Events subscription is required for the core Android local-capture workflow.
- The user participates through the normal Meet app/browser flow. MACLE is not a meeting bot and does not create or host the meeting.
- Local recording is not automatically legally or organizationally authorized. Applicable participant notice, permissions, legal basis and organizational policy must be assessed for the actual context.
- Existing Stage A approval remains synthetic-only and local-only. It does not authorize recording real people or streaming real meeting data to an agent, including an agent the user operates.
- Any later real-meeting or external-agent use requires a separate explicit deployment/data-egress approval.
- The existing desktop/browser connector remains a fallback and reference until Android capture capability is demonstrated.

## 8. Decision status

This study supports an **Android-first product investigation**, not yet an unconditional decision that Android can capture every required modality. The key gating evidence is whether the actual Meet client exposes remote playback audio to AudioPlaybackCapture while the user participates normally on the same device. If it does not, the product must make the limitation explicit and assess whether a different, user-authorized capture topology is acceptable; it must not disguise microphone room audio as equivalent.

No Android architecture, language, minimum Android version, device list, agent transport, or real-meeting authorization is baselined by this study.
