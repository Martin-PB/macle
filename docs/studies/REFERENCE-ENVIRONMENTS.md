# Study — Open reference environments for reproducible fixtures

**Status:** comparative feasibility study, 13 November 2026.  
**Decision status:** no reference environment selected.  
**Purpose:** assess whether a self-hostable open platform could provide a controllable reference environment for scripted meetings and ground-truth capture experiments. This is separate from choosing MACLE's first production platform.

## 1. Why use a reference environment?

A reference environment can make the first end-to-end experiment reproducible:
- controlled participant and endpoint identities;
- scripted join/leave/reconnect and media publication;
- known speech, screen, chat, and interaction actions;
- access to event and media streams;
- repeatable recording and replay;
- no dependence on a third-party enterprise tenant or commercial capture provider.

The fixture platform is a test instrument. Choosing it would not imply that MACLE should support it first in production, nor that its event model represents every commercial platform.

## 2. Candidates

Three candidates were investigated because they represent different kinds of open reference environment:

- **Jitsi Meet:** a complete videoconferencing application and self-hostable deployment, with a documented IFrame integration API and lower-level lib-jitsi-meet client library.
- **LiveKit:** a real-time media server and SDK platform, with track-level media and event APIs and self-hosted server support. It is a building block for a meeting application rather than a ready-made meeting product in the same sense as Jitsi.
- **BigBlueButton:** a complete web conferencing system oriented toward online learning, with rich interaction features, server-side event/media recording, and post-meeting playback.

## 3. Capability comparison

| Criterion | Jitsi Meet | LiveKit | BigBlueButton |
|---|---|---|---|
| Complete meeting application | Yes | No; SDK/server platform from which an app is built | Yes |
| Self-hosted deployment | Documented | Documented | Documented |
| Participant lifecycle events | IFrame API and lib-jitsi-meet events | SDK events and server webhooks | Event recording and optional webhooks |
| Participant state | Mute, role, hand raise and other IFrame/client events | Track mute/unmute, participant metadata/permissions | Participant status, mute, talking, raise-hand and interaction events in recording/event surfaces |
| Active speaker | Dominant-speaker event | ActiveSpeakersChanged and IsSpeakingChanged | Focused camera/layout and voice/talking events in recorded event stream |
| Individual media tracks | Lower-level SDK exposes track events; observer-side access and exact raw-frame path need a spike | Track publications and subscribed raw media tracks are first-class | Webcam/voice recordings exist; live per-participant raw track access not established by reviewed stable integration API |
| Screen sharing | Sharing participant events and screen-share support | Screen-share tracks; participant egress can include screen-share audio | Screen-share/deskshare events and media recording |
| Chat | IFrame events for incoming/outgoing messages | Data messages can be sent through room data channels; no built-in meeting chat product semantics | Public chat and recorded chat events |
| Whiteboard/shared artifacts | Whiteboard status and shared document integrations; event granularity needs study | Application-defined; no built-in whiteboard semantics | Presentation, annotations, shared notes, whiteboard, polls, breakout rooms |
| Post-meeting event/media archive | Depends on Jibri/recording configuration and deployment | Egress recording and application-defined event storage | Rich raw events and media archive with replay workflows |
| Webhook caveats | IFrame/client events require an embedded client; server-side event subscription not established here | Webhooks are push-based; delivery is not guaranteed, retries are bounded | Optional bbb-webhooks package; integration and recording APIs have different stability boundaries |
| Main limitation as fixture | Need a custom observer/client spike for track-level media capture | Requires building enough meeting UX and controls for the test scenario | Education-oriented semantics; raw event/media is strong but much is post-meeting |

## 4. Jitsi Meet

### Documented strengths
- Self-hosted deployments can load the IFrame API from their own domain.
- The IFrame API exposes participant join/leave, participant mute state, dominant speaker changes, screen-sharing participant changes, hand raise, chat messages, recording status, transcription status/chunks, breakout-room-related data, and other events.
- The lower-level lib-jitsi-meet client library exposes conference events including participant join/leave, dominant speaker changes, track added/removed, track mute changes, and audio-level changes.
- The generated API documents JitsiRemoteTrack objects with owner endpoint ID, source name, SSRC, media/video type, and access to the underlying WebRTC media track through the inherited JitsiTrack API. Thus, client-side remote track access is documented; full observer coverage and stability remain empirical questions.
- The IFrame API provides meeting session and participant metadata functions.

### Open questions
- Does a dedicated observer client receive all required remote tracks under LastN, P2P, bandwidth, encryption, and participant-permission conditions, and what user-visible participant role does it require?
- Can individual audio and video frames be obtained with reliable participant/source attribution?
- What media is available for screen sharing, and how are source changes represented?
- Which events are available from the server independently of a client connection?
- How do recording/Jibri deployment and consent controls affect the fixture?

### Preliminary assessment
Jitsi is the strongest candidate among these three for a fixture that should resemble a complete, ordinary videoconference. The event API looks rich. The main unresolved issue is the precise observer-side raw-media path and its stability; the IFrame API event surface alone is not proof of raw media access.

## 5. LiveKit

### Documented strengths
- The server can be self-hosted; webhook configuration is available in self-hosted deployments.
- Server webhooks cover room start/finish, participant join/leave/connection-aborted, track publish/unpublish, and egress lifecycle.
- SDK events cover participant connection/reconnection, track publication/subscription/mute, active speakers, speaking state, connection quality, metadata, and stream-state changes.
- A TrackPublication describes track metadata; a subscribed Track is the raw media stream available to the client.
- Clients can selectively subscribe to tracks, and the documentation shows access to individual participant audio/video tracks. C++ SDK examples expose decoded audio frames and video frames directly.
- Participant egress can record one participant's audio/video tracks and optionally their screen-share track/audio.

### Open questions
- A fixture requires a minimal meeting application, UI, identity model, chat and screen-share controls. This adds test-harness work.
- Determine which media track naming/source conventions to use for camera, microphone, and screen share.
- Measure event/webhook delivery, retry, duplicate, and recovery behavior. The documentation explicitly says webhook delivery is not guaranteed.
- Decide whether the test observer should subscribe as a participant or use server-side egress/recording; compare their timing and attribution.
- Confirm that the self-hosted server and required media services can be run reproducibly on the intended test infrastructure.

### Preliminary assessment
LiveKit is the strongest candidate for a controlled media-plane fixture because participant tracks and decoded media are explicit abstractions. It is not a ready-made meeting product: the fixture must supply a small meeting application and user interactions. Its event and media surfaces are promising for repeatable tests, but delivery and recovery behavior must be measured.

## 6. BigBlueButton

### Documented strengths
- BigBlueButton is a complete self-hostable web conferencing application.
- The integration API supports creating/joining/ending meetings, document insertion, public chat, recording retrieval and deletion, and meeting monitoring.
- The recording system stores raw event and media data for later playback, including chat, participant events, presentation/whiteboard, voice, deskshare, webcam, polls, shared notes, and captions.
- The raw recording archive can contain media and event material from the meeting, with a processing pipeline for playback.
- The optional bbb-webhooks package can publish meeting/user events to external URLs.
- The product has rich features such as presentation, shared notes, polls, breakout rooms, screen sharing, and hand raise.

### Open questions and caveats
- The stable integration API and the internal browser-client APIs are different. The documentation explicitly describes internal APIs as not part of the stable third-party integration contract.
- Much of the richest event/media evidence is in the recording pipeline and therefore post-meeting, not necessarily available as a clean live observation feed.
- Raw recording retention and cleanup require careful configuration. The privacy documentation describes raw recording data remaining on disk after processing until cleanup, and transcription may send audio to a third-party speech provider depending on configuration.
- Its education-oriented feature set may bias the fixture toward classroom workflows rather than a generic business meeting.

### Preliminary assessment
BigBlueButton is a strong candidate for testing rich post-meeting event/media reconstruction and complex shared-content interactions. It is less obviously the simplest fixture for a minimal generic live multimodal observer.

## 7. Version snapshot and research recommendation

On 14 November 2026, the Jitsi Docker release inventory showed stable-11248-3 as the latest release; the Jitsi web release notes showed the 2.0.11248 line. LiveKit's official server release inventory showed v1.13.11, and the JavaScript client SDK reference showed v2.24.0. These are candidate test pins, not selected production dependencies. See [reference spike readiness](REFERENCE-SPIKE-READINESS.md) for the detailed pinning and test plan.

The Jitsi and LiveKit documentation sources below establish API surfaces, not empirical behavior in the MACLE fixture.

## 8. Preliminary comparison and research recommendation

If the immediate goal is **controlled access to individual media tracks and live event semantics**, LiveKit appears to offer the clearest documented primitives, at the cost of building a small meeting application.

If the immediate goal is **a complete meeting experience with a realistic user interface**, Jitsi appears closer to the intended scenario, but its observer-side raw-media access needs a targeted spike.

If the immediate goal is **rich post-meeting replay of multiple modalities and interactions**, BigBlueButton provides a strong event/media recording architecture, with a classroom-oriented domain and important retention/configuration caveats.

These are conditional research findings, not a selection. A reasonable next experiment is a short technical spike on Jitsi and LiveKit, using the same two-participant-plus-shared-endpoint scenario, before selecting one reference fixture. BigBlueButton can remain a candidate for a later post-meeting replay fixture.

## 9. Required spike and pass criteria

For each candidate, demonstrate:

1. create and run a self-hosted meeting/session;
2. create at least three platform participants, with two human testers sharing one endpoint;
3. capture participant join/leave and reconnect events;
4. capture microphone/camera mute changes and active-speaker events;
5. receive separate audio and video tracks with stable source IDs;
6. capture screen-share start/stop and media;
7. capture chat and hand raise where supported;
8. record source time, receipt time, and capture gaps;
9. stop/restart the observer without losing the ability to rejoin and reconcile state;
10. export the same normalized observation timeline and compare it with the human-annotated fixture ground truth.

The spike must report which capabilities are server-side, client-side, live, post-meeting, or inferred. It must not treat the fixture platform's internal event taxonomy as MACLE's canonical ontology.

## 10. Sources and retrieval record

Official project documentation checked on 13 November 2026:

### Jitsi
- [IFrame API overview](https://jitsi.github.io/handbook/docs/dev-guide/dev-guide-iframe/)
- [IFrame API events](https://jitsi.github.io/handbook/docs/dev-guide/dev-guide-iframe-events/)
- [IFrame API functions](https://jitsi.github.io/handbook/docs/dev-guide/dev-guide-iframe-functions/)
- [lib-jitsi-meet conference event API](https://jitsi.github.io/lib-jitsi-meet/enums/JitsiConferenceEvents.JitsiConferenceEvents.html)
- [lib-jitsi-meet remote track API](https://jitsi.github.io/lib-jitsi-meet/classes/JitsiConference._internal_.JitsiRemoteTrack.html)

### LiveKit
- [Webhooks and SDK events](https://docs.livekit.io/intro/basics/rooms-participants-tracks/webhooks-events/)
- [Subscribing to tracks](https://docs.livekit.io/transport/media/subscribe/)
- [Participant and track-composite egress](https://docs.livekit.io/transport/media/ingress-egress/egress/participant/)
- [Webhook API reference](https://docs.livekit.io/reference/api/projects/webhooks/)
- [Self-hosted local server](https://docs.livekit.io/transport/self-hosting/local/)
- [Server deployment requirements](https://docs.livekit.io/transport/self-hosting/deployment/)

### BigBlueButton
- [API reference](https://docs.bigbluebutton.org/dev/api/)
- [Recording and raw event/media archive](https://docs.bigbluebutton.org/development/recording/)
- [Webhooks](https://docs.bigbluebutton.org/4.0/development/webhooks/)
- [Privacy and raw recording/transcription behavior](https://docs.bigbluebutton.org/administration/privacy/)

## 11. No decision made

No candidate is selected as MACLE's reference environment. No conclusion is made about the production platform. The next step is a narrow technical spike and a repeatable fixture, not a platform commitment.
