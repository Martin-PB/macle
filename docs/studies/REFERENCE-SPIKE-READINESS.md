# Study — Reference-environment spike readiness

**Status:** versioned technical readiness study, 14 November 2026.  
**Decision status:** neither Jitsi nor LiveKit is selected. No test has been executed.  
**Purpose:** turn issue #5 into a reproducible, version-pinned comparison while distinguishing what the official APIs document from what the spike must verify.

## 1. Snapshot of candidate versions

The following are current version references observed on 14 November 2026. They are candidate pins for a controlled spike, not an adoption decision.

| Candidate | Component | Version/reference observed | Source date | What this pins |
|---|---|---|---|---|
| Jitsi Meet | Docker deployment bundle | docker-jitsi-meet tag stable-11248-3 | 2 Nov 2026 release | The deployment bundle and its compose/environment files; inspect actual image tags in the release |
| Jitsi Meet | Web client | 2.0.11248 release line | 14 Sep 2026 | Web frontend release line; not a separate lib-jitsi-meet package pin |
| Jitsi Meet | lib-jitsi-meet API docs | current generated API docs / master source | retrieved 14 Nov 2026 | Documentation snapshot only; not a reproducible source commit |
| LiveKit | Server | v1.13.11 | 25 Oct 2026 | Server release |
| LiveKit | JavaScript client SDK | v2.24.0 documentation | retrieved 14 Nov 2026 | JS client SDK reference version |
| LiveKit | Self-hosting docs | rolling documentation | retrieved 14 Nov 2026 | Deployment guidance only; server release is separately pinned |

For an actual run, record container image digests, package lockfile versions, browser versions, OS/kernel, Docker/Compose versions, and the exact lib-jitsi-meet source bundled by the chosen Jitsi release. A documentation page or branch named master is not a version pin.

## 2. Jitsi: stronger evidence for remote track access than the initial study established

The official lib-jitsi-meet API documents:
- conference events for track added/removed, track mute, audio-level changes, dominant-speaker changes, and participant join/leave;
- remote participant objects exposing their media tracks;
- JitsiRemoteTrack objects carrying owner endpoint ID, SSRC, source name, media type and video type;
- inherited track methods exposing the underlying WebRTC MediaStreamTrack and MediaStream.

This is meaningful evidence that a connected lib-jitsi-meet client can observe remote media tracks, not merely participant-level metadata. It refines the earlier statement that the observer-side raw-media path was wholly unestablished.

It does **not** yet prove that a dedicated MACLE observer can obtain every desired stream in a stable, supported, non-intrusive way. The spike must still determine:
- whether the observer must join as an ordinary participant and what that means for visibility, permissions and user experience;
- whether remote audio and video tracks are available for all participants under LastN, P2P, bandwidth and bridge conditions;
- whether camera and desktop-share tracks are reliably distinguishable by source name/video type;
- how participant endpoint IDs and track owner IDs behave across reconnects, source replacement and endpoint changes;
- whether browser APIs can consume the raw MediaStreamTrack in the target browsers without loss or timing distortion;
- how track mute, interrupted/restoring states and track removal map to capture gaps;
- what media can be captured when end-to-end encryption is enabled.

### Jitsi preliminary status

| Capability | Evidence status |
|---|---|
| Participant lifecycle and dominant speaker | Documented client API |
| Remote track add/remove and mute events | Documented client API |
| Remote participant track collection | Documented client API |
| Underlying WebRTC media track | Documented API inheritance |
| Stable full-track coverage for an observer | Not empirically tested |
| Screen-share source fidelity across supported clients | Not empirically tested |
| Recovery/reconciliation after observer interruption | Not empirically tested |
| Server-side event feed independent of a client | Not established by this evidence |

Jitsi therefore merits a focused observer-client spike. The correct characterization is “client-side track access is documented; coverage and operational behavior remain to be measured”, not “Jitsi has no raw media API”.

## 3. LiveKit: explicit track and frame primitives

Official LiveKit documentation describes:
- participant and track publication/subscription events;
- separate TrackPublication metadata and Track media objects;
- raw participant track subscriptions;
- JavaScript SDK track access through the subscribed remote track;
- server-side AudioStream and VideoStream frame iteration in media-processing workflows;
- C++ SDK callbacks for decoded audio/video frames;
- self-hosted local development mode and production deployment requirements.

Webhook delivery is push-based and not guaranteed. LiveKit retries transient failures several times, then abandons delivery. A consumer must therefore use event IDs, idempotent processing, reconciliation, and state refresh rather than assume complete webhook delivery.

### LiveKit preliminary status

| Capability | Evidence status |
|---|---|
| Participant lifecycle and track events | Documented SDK/server events |
| Per-participant published tracks | Documented |
| Track subscription with participant/publication context | Documented |
| Decoded audio/video frame access | Documented for relevant server/C++ SDK paths |
| Screen-share source track | Documented track source model; fixture-specific mapping still needs test |
| Webhook delivery completeness | Explicitly not guaranteed |
| Recovery/reconciliation after observer interruption | Must be measured |
| Complete meeting UI/chat/hand-raise workflow | Application must implement or integrate these semantics |

LiveKit is a media infrastructure, not a complete videoconferencing application. A fixture needs a minimal meeting client, participant identity mapping, screen-share and interaction controls, and a scripted scenario. This extra harness work is part of the comparison, not an invisible prerequisite.

## 4. Comparable spike design

Do not compare a fully featured Jitsi client against an incomplete LiveKit room without recording the asymmetry. The spike should separate:
1. **Platform fixture UX:** join/leave, mute, hand raise, chat and screen-share actions.
2. **Control/event acquisition:** platform/SDK events and server webhooks.
3. **Media acquisition:** individual audio/video tracks and screen-share media.
4. **Observer recovery:** reconnect, replay/reconciliation, event gaps.
5. **Normalization:** mapping into the same MACLE observation envelope without discarding source identifiers.

For Jitsi, use the self-hosted Docker bundle and a dedicated observer client built with the matching lib-jitsi-meet version. For LiveKit, use the pinned server plus a small browser meeting client and a separate observer subscriber. Both paths must produce the same fixture timeline and ground-truth comparison.

## 5. Candidate version pins for a first run

Subject to environment availability and a later decision to execute:

### Jitsi candidate
- docker-jitsi-meet: stable-11248-3;
- inspect and record every resolved container image tag and digest;
- use the lib-jitsi-meet version bundled with that release, not an independently fetched master branch;
- record the web client build identifier exposed by the running service.

### LiveKit candidate
- server: v1.13.11;
- JavaScript client SDK: v2.24.0;
- pin package lockfile and container image digest;
- record any server-side SDK used for frame extraction separately.

Do not silently upgrade either candidate mid-run. A second release should be a separate test configuration.

## 6. Environment prerequisites and test hygiene

- Dedicated self-hosted test environment, not a production meeting tenant.
- Synthetic test identities and content only.
- Known browser/OS versions and separate client profiles for participant endpoints.
- Network path capable of WebRTC UDP or documented TURN fallback; record firewall and relay behavior.
- Trusted HTTPS/TLS where the selected browser/SDK requires it.
- Synchronized wall clocks plus monotonic receipt clocks; record clock offset and uncertainty.
- Resource monitoring for CPU, memory, bandwidth, packet loss and dropped frames.
- No external speech or AI provider in the initial media-plane spike.
- Preserve logs and media only as long as the controlled test requires; do not include secrets or real identities in artifacts.

A successful local single-machine call is not evidence of multi-network connectivity. At least one test should involve distinct endpoint environments if the infrastructure allows it.

## 7. Required outputs

For each candidate and each run:
- exact version manifest and image/package digests;
- environment/network configuration;
- participant/endpoint/session topology;
- raw event log and media-track inventory;
- event and media source identifiers;
- source timestamps, receipt timestamps and clock mapping;
- observer health and capture-gap timeline;
- reconnect/reconciliation results;
- normalized observation timeline;
- comparison against the synthetic ground-truth fixture;
- list of documented, observed, unavailable and untested capabilities.

No numeric acceptance threshold is set in this study. Establish thresholds only after measurement behavior and the fixture are stable.

## 8. Sources checked 14 November 2026

### Jitsi
- Docker deployment release inventory: https://github.com/jitsi/docker-jitsi-meet/releases — stable-11248-3 observed as latest on 14 Nov 2026.
- Official Docker self-hosting guide: https://jitsi.github.io/handbook/docs/devops-guide/devops-guide-docker/
- Jitsi web release notes: https://jitsi.github.io/handbook/docs/releases/ — web release line 2.0.11248.
- lib-jitsi-meet conference event API: https://jitsi.github.io/lib-jitsi-meet/enums/JitsiConferenceEvents.JitsiConferenceEvents.html
- lib-jitsi-meet remote track API: https://jitsi.github.io/lib-jitsi-meet/classes/JitsiConference._internal_.JitsiRemoteTrack.html
- lib-jitsi-meet participant API: https://jitsi.github.io/lib-jitsi-meet/classes/JitsiParticipant.JitsiParticipant.html

### LiveKit
- Server release inventory: https://github.com/livekit/livekit/releases — v1.13.11 observed as latest on 14 Nov 2026.
- JavaScript client SDK reference: https://docs.livekit.io/reference/client-sdk-js/ — v2.24.0.
- Raw media tracks: https://docs.livekit.io/transport/media/raw-tracks/
- Track subscription: https://docs.livekit.io/transport/media/subscribe/
- Self-hosting overview: https://docs.livekit.io/transport/self-hosting/
- Local self-hosted server: https://docs.livekit.io/transport/self-hosting/local/
- Deployment and network requirements: https://docs.livekit.io/transport/self-hosting/deployment/
- Webhooks and delivery/retry caveats: https://docs.livekit.io/intro/basics/rooms-participants-tracks/webhooks-events/

## 9. No decision or verification claim

This document does not select Jitsi or LiveKit, and does not claim that either has passed the spike. It pins candidate versions and sharpens the test questions. Empirical validation remains open under issue #5.
