# Study — Capture evaluation protocol

**Status:** proposed research and test protocol; not a product requirement baseline.  
**Applies to:** platform adapters, bot participants, desktop/browser capture, and post-meeting artifact importers.

## 1. Objective

Evaluate whether a capture path preserves enough of a videoconference's observable situation for MACLE without conflating people and platform accounts, people and endpoints, participants and sessions, media streams and inferred speakers, direct observations and algorithmic interpretations, or event occurrence time and receipt/processing time.

This is a repeatable experiment, not a claim that every candidate must expose every signal.

## 2. Test environment record

Every run must record:

| Field | Required content |
|---|---|
| Run ID | Stable unique identifier |
| Date/time | Start/end in UTC and local time zone |
| Platform | Product, edition, tenant type, meeting type |
| Client | Browser/app version, OS, architecture |
| Acquisition path | Native SDK/API, bot, desktop/browser, artifacts, import |
| SDK/API | Exact product and version |
| Permissions | OAuth scopes, host/tenant grants, participant role |
| Consent/disclosure | Visible notice, host action, participant action, opt-out |
| Network | Connection type and induced impairments |
| Topology | Participants, devices, shared endpoints, room devices |
| Capture configuration | Enabled signals, stream selection, sampling and encoding |
| Retention | Where raw and derived data are stored and for how long |
| Operator | Test operator and configuration owner |

Do not compare runs if relevant configuration differs without recording the difference.

## 3. Scripted meeting scenario

### 3.1 Participants and endpoints
- A joins from one computer with camera and microphone.
- B and C are physically co-located and share one computer/camera/microphone endpoint.
- D joins from a phone and later joins from a second device.
- One participant leaves and rejoins.
- A guest or anonymous participant joins if supported.
- A room device or dial-in participant is added where supported.

### 3.2 Media and interaction
- A speaks alone for a known interval.
- B and C speak separately while using the shared endpoint.
- B and C speak simultaneously.
- A and D speak with overlapping audio.
- Cameras are enabled, disabled, and re-enabled.
- Microphones are muted and unmuted.
- Screen sharing starts, changes content, pauses, resumes, and stops.
- A participant raises and lowers a hand.
- Chat messages, edits/deletions, reactions, links, and file-sharing actions occur where available.

### 3.3 Discontinuities and permissions
- A network interruption is introduced for one participant.
- The capture process is restarted while the meeting continues.
- A participant reconnects from another device.
- Host/administrator permission is denied, granted, and (where possible) revoked.
- Recording/transcription is disabled for one run and enabled for another.
- A participant declines or opts out where the platform supports this flow.

### 3.4 Post-meeting
- The meeting ends normally.
- Recording/transcript artifacts are generated where enabled.
- The importer retrieves artifacts immediately and again after a delay.
- One artifact is modified or deleted in the source platform where supported.
- Retrieval is retried after a transient failure.

## 4. Expected observation inventory

The evaluator marks each item as observed, inferred, unavailable, or not tested.

| Observation | Ground truth available to evaluator | Capture result |
|---|---|---|
| Meeting started/ended | Script/operator log | |
| Participant joined/left | Script and platform roster | |
| Endpoint/device changed | Script and client logs | |
| Participant session/reconnect | Script and platform session records | |
| Shared endpoint used by B and C | Script | |
| Number of distinct speakers | Script and audio recording | |
| Speaker-to-person attribution | Script; distinguish capture from inference | |
| Mute/camera state changes | Script and platform UI | |
| Active speaker | Script and audio | |
| Screen-share start/stop | Script and platform UI | |
| Screen content changes | Known test content | |
| Chat/reaction/hand raise | Script and platform UI | |
| Recording/transcript generation | Platform artifact state | |
| Permission denied/granted/revoked | Script and platform response | |
| Network interruption/recovery | Induced fault log | |

The ground-truth log is an evaluation aid. It must not be copied into capture output as if the capture system had observed it.

## 5. Measurements

For every signal/event class, measure:

1. **Coverage:** expected observations received / expected observations.
2. **Attribution:** correct source participant, endpoint, stream, or unknown.
3. **Temporal quality:** event time, receipt time, clock source, precision, skew.
4. **Latency:** event occurrence to MACLE availability; report median and tail percentiles.
5. **Continuity:** missing media intervals, frame/audio loss, reconnect gaps.
6. **Ordering:** out-of-order events, duplicates, missing sequence information.
7. **Recovery:** ability to resume after network, process, or permission interruption.
8. **Resource use:** CPU, memory, network bandwidth, storage, local disk pressure.
9. **Operational friction:** installation, permissions, host actions, admin intervention.
10. **Disclosure and control:** visibility of capture, consent, opt-out, stop behavior.
11. **Portability:** OS/client/meeting-type constraints.
12. **Data handling:** retention, deletion, export, residency, provider processing.

Report distributions and failure examples, not only averages.

## 6. Evidence classification

Classify every output as one or more of:

- **Platform assertion:** a platform API/event says something happened.
- **Direct media observation:** audio/video/screen bytes or frames were received.
- **Algorithmic extraction:** speech recognition, diarization, OCR, visual detection, etc.
- **Human annotation:** a test operator or participant supplied a label.
- **Interpretation:** a higher-level claim inferred from observations.

Do not elevate algorithmic extraction to platform assertion. Do not treat diarization as identity proof. Do not treat a transcript as equivalent to source audio.

## 7. Result record

For each platform × acquisition path × scenario, produce:
- configuration record;
- event/capability coverage table;
- raw observation sample or secure reference;
- known missing observations;
- timing and resource measurements;
- failure/recovery log;
- permission and disclosure record;
- data lifecycle record;
- limitations and uncertainty;
- reproducibility instructions;
- reviewer and review date.

Every claim must point to supporting evidence. A result may be PASS, PARTIAL, FAIL, or NOT TESTED, but the criterion and evidence must accompany the label.

## 8. Shared-endpoint acceptance checks

This is a critical differentiator for MACLE.

- Do not silently assert that one platform participant is exactly one human.
- Represent endpoint separately from platform participant.
- Allow several human-presence or speaker observations to relate to one endpoint.
- Allow one person to relate to multiple endpoints/sessions over time.
- Retain uncertainty when speaker-to-person mapping is unknown.
- Do not manufacture separate platform identities for co-located people.
- Preserve original platform attribution alongside any inferred attribution.
- Keep contradictory evidence inspectable instead of overwriting it with one resolved identity.

These are evaluation criteria for the observation model, not a claim that a capture adapter can identify co-located people.

## 9. Fair comparison of strategies

- Use the same scripted scenario and ground-truth log.
- Keep meeting configuration and account entitlements equivalent where possible.
- Record unavoidable differences rather than normalizing them away.
- Compare native SDK, bot, desktop/browser, and artifact paths separately before hybrid combinations.
- Preserve original platform payloads and vendor-normalized outputs separately.
- Repeat runs to expose nondeterminism and transient failures.
- Test least-privilege configuration and the configuration required for richest documented capture.
- Include a negative test where access is refused or withdrawn.

## 10. Decision boundary

The protocol can produce evidence and comparative findings. It cannot decide which platform MACLE should support first, whether raw media is necessary, whether a bot or local desktop component is acceptable, what disclosure/consent policy is required, what data should be retained, or whether a vendor is acceptable.

Those remain separate product, governance, legal, and architecture decisions.
