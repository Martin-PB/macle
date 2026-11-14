# Study — Reference-environment spike readiness

**Status:** PROPOSED versioned technical readiness study, 14 November 2026.  
**Decision status:** neither Jitsi nor LiveKit selected; no spike executed.

## 1. Candidate version snapshot

These versions were observed on 14 November 2026 and are candidate pins for a controlled test, not adopted dependencies.

| Candidate | Component | Observed version/reference | Meaning |
|---|---|---|---|
| Jitsi | Docker deployment bundle | docker-jitsi-meet stable-11248-3 (released 2 Nov 2026) | Pins deployment bundle; inspect resolved image tags/digests |
| Jitsi | Web client | 2.0.11248 release line | Web frontend release line |
| Jitsi | lib-jitsi-meet | Generated API docs / master source | Documentation snapshot only; not a reproducible source pin |
| LiveKit | Server | v1.13.11 (released 25 Oct 2026) | Server release |
| LiveKit | JavaScript client SDK | v2.24.0 documentation | JS SDK reference version |

For an actual run, record container image digests, package lockfile versions, browser versions, OS/kernel, Docker/Compose versions, and the exact lib-jitsi-meet source bundled by the Jitsi release. A page or branch named master is not a version pin.

## 2. Jitsi: remote track access is documented

Official lib-jitsi-meet documentation describes:
- conference events for track added/removed, track mute, audio-level changes, dominant-speaker changes, and participant join/leave;
- participant objects exposing their media tracks;
- JitsiRemoteTrack objects carrying owner endpoint ID, source name, SSRC, media type and video type;
- inherited track APIs exposing the underlying WebRTC MediaStreamTrack and MediaStream.

This is stronger evidence than a participant-metadata-only interface: a connected lib-jitsi-meet client has documented access to remote media track objects.

It does **not** prove that a dedicated MACLE observer can obtain every desired stream in a stable, supported, non-intrusive way. The spike must determine:
- whether the observer must join as an ordinary participant and what that means for visibility and permissions;
- whether remote tracks are available under LastN, P2P, bandwidth and bridge conditions;
- whether camera and desktop-share tracks are reliably distinguishable;
- how endpoint IDs and track owner IDs behave across reconnects and source replacement;
- whether browser APIs can consume MediaStreamTrack without loss or timing distortion;
- how interrupted/restoring states and track removal map to capture gaps;
- what media is available with end-to-end encryption enabled.

### Jitsi evidence status

| Capability | Status |
|---|---|
| Participant lifecycle and dominant speaker | Documented client API |
| Remote track add/remove and mute events | Documented client API |
| Remote participant track collection | Documented client API |
| Underlying WebRTC media track | Documented API |
| Complete track coverage for observer | Not empirically tested |
| Screen-share source fidelity | Not empirically tested |
| Recovery after observer interruption | Not empirically tested |
| Server-side event feed independent of client | Not established by this evidence |

The correct characterization is: client-side track access is documented; observer coverage and operational behavior remain to be measured.

## 3. LiveKit: explicit track and frame primitives

Official documentation describes:
- participant and track publication/subscription events;
- separate TrackPublication metadata and Track media objects;
- raw participant track subscriptions;
- JavaScript SDK track access through subscribed remote tracks;
- server-side AudioStream and VideoStream frame iteration;
- C++ SDK callbacks for decoded audio/video frames;
- self-hosted local development and production deployment options.

Webhook delivery is push-based and not guaranteed. LiveKit retries transient failures several times, then abandons delivery. Consumers must use event IDs, idempotent processing, state refresh and reconciliation rather than assume complete delivery.

### LiveKit evidence status

| Capability | Status |
|---|---|
| Participant lifecycle and track events | Documented SDK/server events |
| Per-participant published tracks | Documented |
| Track subscription with participant/publication context | Documented |
| Decoded audio/video frame access | Documented for relevant server/C++ SDK paths |
| Screen-share source mapping | Track source model documented; fixture-specific behavior to test |
| Webhook delivery completeness | Explicitly not guaranteed |
| Recovery/reconciliation | Not empirically tested |
| Full meeting UI/chat/hand raise | Application must implement or integrate these semantics |

LiveKit is media infrastructure, not a complete meeting application. A fixture needs a minimal meeting client, participant identity mapping, screen-share and interaction controls, and the scripted scenario. This harness work is part of the comparison.

## 4. Comparable spike design

Separate:
1. platform fixture UX: join/leave, mute, hand raise, chat and screen-share actions;
2. control/event acquisition: SDK events and server webhooks;
3. media acquisition: individual audio/video tracks and screen-share media;
4. observer recovery: reconnect, replay/reconciliation, event gaps;
5. normalization: same MACLE observation envelope while preserving source identifiers.

For Jitsi, use the self-hosted Docker bundle and an observer client built with the matching lib-jitsi-meet version. For LiveKit, use the pinned server, a small browser meeting client and a separate observer subscriber. Both paths must produce the same fixture timeline and ground-truth comparison.

## 5. Candidate version pins

### Jitsi
- docker-jitsi-meet stable-11248-3;
- inspect and record every resolved container image tag and digest;
- use the lib-jitsi-meet version bundled with that release, not an independently fetched master branch;
- record the running web client build identifier.

### LiveKit
- server v1.13.11;
- JavaScript client SDK v2.24.0;
- pin package lockfile and container image digest;
- record any server-side SDK used for frame extraction separately.

Do not silently upgrade either candidate mid-run. A later release is a separate test configuration.

## 6. Environment prerequisites

- Dedicated self-hosted test environment, not a production meeting tenant.
- Synthetic test identities and content only.
- Known browser/OS versions and separate client profiles.
- Network path capable of WebRTC UDP or documented TURN fallback; record firewall and relay behavior.
- Trusted HTTPS/TLS where required by the chosen browser/SDK.
- Synchronized wall clocks plus monotonic receipt clocks; record clock offset and uncertainty.
- CPU, memory, bandwidth, packet loss and dropped-frame monitoring.
- No external speech or AI provider in the initial media-plane spike.
- Preserve logs/media only as long as the controlled test requires; exclude secrets and real identities.

A successful single-machine call is not evidence of multi-network connectivity. Include distinct endpoint environments if infrastructure permits.

## 7. Required outputs

For each candidate/run:
- exact version manifest and image/package digests;
- environment/network configuration;
- participant/endpoint/session topology;
- raw event log and media-track inventory;
- event/media source identifiers;
- source timestamps, receipt timestamps and clock mapping;
- observer health and capture-gap timeline;
- reconnect/reconciliation results;
- normalized observation timeline;
- comparison against synthetic ground truth;
- documented, observed, unavailable and untested capability matrix.

No numeric acceptance threshold is set here. Establish thresholds only after measurement behavior and the fixture are stable.

## 8. Sources checked 14 November 2026

### Jitsi
- Docker release inventory: https://github.com/jitsi/docker-jitsi-meet/releases — stable-11248-3 observed as latest.
- Official Docker self-hosting guide: https://jitsi.github.io/handbook/docs/devops-guide/devops-guide-docker/
- Web release notes: https://jitsi.github.io/handbook/docs/releases/ — 2.0.11248 line.
- Conference event API: https://jitsi.github.io/lib-jitsi-meet/enums/JitsiConferenceEvents.JitsiConferenceEvents.html
- Remote track API: https://jitsi.github.io/lib-jitsi-meet/classes/JitsiConference._internal_.JitsiRemoteTrack.html
- Participant API: https://jitsi.github.io/lib-jitsi-meet/classes/JitsiParticipant.JitsiParticipant.html

### LiveKit
- Server release inventory: https://github.com/livekit/livekit/releases — v1.13.11 observed as latest.
- JavaScript client SDK reference: https://docs.livekit.io/reference/client-sdk-js/ — v2.24.0.
- Raw media tracks: https://docs.livekit.io/transport/media/raw-tracks/
- Track subscription: https://docs.livekit.io/transport/media/subscribe/
- Self-hosting overview: https://docs.livekit.io/transport/self-hosting/
- Local server: https://docs.livekit.io/transport/self-hosting/local/
- Deployment/network requirements: https://docs.livekit.io/transport/self-hosting/deployment/
- Webhook delivery/retry: https://docs.livekit.io/intro/basics/rooms-participants-tracks/webhooks-events/

## 9. No decision or verification claim

This study does not select Jitsi or LiveKit and does not claim either has passed the spike. It pins candidate versions and sharpens test questions. Empirical validation remains open under issue #5.
