# Study — Videoconferencing capture strategies

**Status:** options analysis; no strategy selected.

The capture mechanism is a separate decision from the platform and from the perception components. MACLE should not assume that a platform connector must be implemented as a bot, or that a bot is the only way to obtain meeting data.

## 1. Candidate strategies

### A. Native platform SDK or API

The integration uses the platform's own SDKs, REST APIs, event subscriptions, or webhooks.

**Potential strengths**
- Access to platform-native participant identities and lifecycle events.
- Potentially better semantic fidelity for mute, camera, roles, hand raise, chat, and screen-share lifecycle.
- Direct access to platform-specific media paths where supported.

**Potential limitations**
- Separate integration and permission model for every platform.
- Feature parity differs substantially between vendors and SDK variants.
- Some APIs expose only metadata or post-meeting artifacts, not live media.
- Host/tenant/admin consent and plan restrictions can limit access.

**Examples:** Zoom Meeting SDK and Video SDK; Google Meet REST API and Workspace Events; Teams Graph and Real-time Media; Webex Meetings APIs and webhooks.

### B. Bot participant

A service launches a bot that joins the meeting as a participant and captures the data available to it.

**Potential strengths**
- Cross-platform access through a single integration provider may reduce connector engineering.
- A bot can receive the same meeting experience as a participant, including media and sometimes chat or screen content.
- Real-time capture and post-meeting artifact workflows can be combined.

**Potential limitations**
- The bot is visible as a participant and may affect participant experience.
- It may be blocked by waiting rooms, host policies, tenant policies, or platform changes.
- Bot identity, consent, disclosure and permissions require careful design.
- The provider may normalize away platform-specific events or retain data in its own infrastructure.

**Candidate:** Recall.ai Meeting Bot API. Its documentation describes support for Zoom, Google Meet, Teams, Webex and other platforms, with platform-specific nuances.

### C. Desktop or browser capture

A local application/SDK captures the user's meeting experience, system audio, application windows, camera tiles, and screen content without joining as a separate meeting participant.

**Potential strengths**
- Avoids adding a visible bot participant.
- Can observe the actual rendered interface and content, including application/window changes that platform APIs may not expose.
- May work when native meeting APIs are unavailable or inaccessible.

**Potential limitations**
- Requires a local installation and operating-system permissions.
- UI changes, browser differences, scaling, multiple monitors, and audio routing create fragility.
- Distinguishing individual participant media from a composite gallery can be difficult.
- Local capture is not automatically equivalent to platform-native participant identity or event semantics.

**Candidate:** Recall.ai Desktop Recording SDK; other desktop capture products such as Granola and tl;dv provide useful reference patterns, but their output and capture coverage must be evaluated independently.

### D. Post-meeting artifact retrieval

The system retrieves platform-generated recordings, transcripts, attendance reports, and metadata after the meeting.

**Potential strengths**
- Often uses official platform artifacts and permission models.
- Avoids live media processing and may be simpler to operate.
- Useful for backfill, audit, reconciliation and enrichment.

**Potential limitations**
- Cannot provide live situation awareness.
- Artifacts may be absent if recording/transcription was not enabled.
- Granularity, timestamps, retention and availability differ by platform.
- A transcript cannot reconstruct visual events, screen changes, or all interaction events.

### E. User-provided recording or media import

A user uploads or references a recording for asynchronous processing.

**Potential strengths**
- Useful for offline evaluation, reproducible test fixtures and historical data.
- No need to join a live meeting.

**Potential limitations**
- No live events or interactions.
- Platform context and participant identity may be missing.
- Consent, rights and provenance still need to be established.

## 2. Comparative matrix

| Criterion | Native SDK/API | Bot participant | Desktop/browser | Post-meeting artifacts | User upload |
|---|---|---|---|---|---|
| Live operation | Depends on API | Often yes | Yes | No | No |
| Platform semantics | Potentially strong | Variable | UI-dependent | Artifact-dependent | Usually weak |
| Raw media | SDK-specific | Provider-specific | Capture-dependent | Recording-dependent | File-dependent |
| Screen sharing | SDK-specific | Provider-specific | Rendered view | Usually in recording | In recording |
| Chat/events | API-specific | Provider-specific | UI-visible only | Often incomplete | Usually absent |
| Visible meeting participant | No, normally | Yes | No | No | No |
| Local installation | Sometimes | No | Yes | No | No |
| Cross-platform reuse | Low to medium | Potentially high | Medium, OS-dependent | Medium | High file-level |
| Post-meeting data | Often | Often | Depends on product | Yes | Derived |
| Main risk | API fragmentation | Provider dependence and bot policy | OS/UI fragility | Loss of real-time context | Missing context |

This is a qualitative comparison, not a measured benchmark.

## 3. Important hybrid possibility

A future MACLE implementation could combine strategies:
- native platform events for identity and lifecycle;
- bot or desktop capture for live media;
- post-meeting artifacts for reconciliation and enrichment;
- local media processing for extraction and alignment.

This is a candidate architecture pattern only. It should not be adopted until the first platform and required event/media coverage are chosen.

## 4. Evaluation protocol

For each candidate strategy and platform, test the same scripted meeting:
1. two or more participants join and leave;
2. one participant reconnects from another device;
3. one endpoint is shared by multiple people;
4. camera and microphone are toggled;
5. speakers overlap and pause;
6. screen sharing starts, changes content, pauses and stops;
7. chat messages, reactions and hand raises occur;
8. participants enter/leave breakout rooms if supported;
9. recording/transcription permissions are varied;
10. network interruption and client restart are simulated.

Record missing events, timestamp quality, attribution, media continuity, latency, resource usage, consent UX and recovery behavior.

## 5. Current position

No strategy is selected. The purpose of this study is to prevent premature commitment to a bot, a desktop recorder, or a single platform API before their coverage has been compared against MACLE's actual requirements.
