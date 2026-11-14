# Study — Google Meet integration

**Status:** current desk research plus an initial single-device prototype; no production capture architecture, provider, add-on, or deployment has been selected.  
**Product priority:** first platform integration for a usable MACLE product. Discord is a likely later integration, explicitly deferred.  
**Research retrieved:** 2026-11-14.

## 1. Executive finding

Google Meet is a viable first product integration target, but no single supported Google interface provides the complete multimodal observation surface MACLE conceptually needs.

The integration must separate at least four surfaces:

1. **Control plane:** Meet REST API and Google Workspace Events expose meeting-space, conference, participant and participant-session information and lifecycle notifications.
2. **Post-meeting artifacts:** Meet REST API and Drive provide recordings, transcripts, transcript entries and smart notes when generated and accessible.
3. **In-meeting user experience:** Meet add-ons embed a collaborative application in Meet. They are a user-interface and collaboration surface, not a documented raw audio/video capture API.
4. **Live media observation:** requires a separate, sustainable acquisition route. The Meet Media API is being shut down and must not be used as the foundation of a new product.

A first useful integration can start with OAuth-authorized metadata, lifecycle events and post-meeting artifacts, while clearly identifying that it is not live multimodal situational awareness. Live observation remains a separate engineering and governance workstream.

## 2. Product priority and boundaries

The project owner clarified on 2026-11-14:
- Google Meet is the first target for a usable MACLE platform integration.
- Discord is a likely second platform, but deferred.
- Stage A is approved for the first technical demonstrator: synthetic identities and content only, locally self-hosted, with no third-party provider egress.

Stage A is limited to synthetic/local validation. It does not authorize real-meeting capture, processing real participant data, or sending any data to external capture, speech, transcription or AI providers.

The self-hosted Jitsi/LiveKit comparison remains useful as a generic reference fixture for media/event modeling. It is not a substitute for the first product integration with Google Meet, and it does not select either as a production platform.

## 3. Surface A — Meet REST API

The Meet REST API (v2) provides:
- meeting-space creation, retrieval and configuration;
- conference records;
- participant records;
- participant sessions;
- recordings;
- transcripts and transcript entries;
- smart notes;
- meeting-space members and roles.

It supports pre-meeting configuration, some operations and metadata during an active conference, and artifact retrieval after the conference. It is not a general raw live-media API.

Important identity distinctions:
- A **meeting space** is a persistent meeting container.
- A **conference record** identifies a particular conference occurrence in that space.
- A **participant** represents a person participating in the call (including relevant room-device and companion-mode cases).
- A **participant session** represents a participant/device pair's session; one participant may have multiple sessions.
- A **member** is a persistent space-level membership/role and is not synonymous with a participant in a particular conference.

MACLE must preserve Google's original resource names and not collapse these entities into one generic participant identifier.

Transcript entries are particularly useful for a first artifact integration: they provide discrete speech segments with participant association, timestamps, text and language code. Google documents a 30-day availability window for transcript entries after the conference. ConferenceRecord resources themselves also have an `expireTime` and are deleted 30 days after the conference ends. This is a time-bounded API evidence window, not a durable transcript or meeting-metadata archive guarantee; MACLE must sync eligible records promptly and preserve its own governed local copy.

Access is constrained by OAuth authorization/scopes, whether the authenticated user is a meeting owner or participant for the requested operation, Workspace configuration and policies, organizer/host settings, artifact generation and availability. A useful single-device route for a currently active meeting is to call `spaces.get` with the meeting code, read `activeConference.conferenceRecord`, and then retrieve the conference and participants; this avoids relying on organizer-only historical discovery for the active session. Domain-wide delegation is a distinct administrative authorization path, not a default assumption for a consumer application.

Google also explicitly states that the Meet REST API is not intended for performance tracking or user evaluation within an organization, and that Meet data should not be collected for that purpose. MACLE's initial integration must not be repurposed into employee-performance scoring or surveillance; any future use case in this area requires separate product and legal review.

## 4. Surface B — Google Workspace Events

Workspace Events subscriptions can notify an application about Meet space and conference changes. Documented event families include:
- conference started/ended;
- participant joined/left;
- recording lifecycle and file generation;
- transcript lifecycle and file generation;
- smart-note lifecycle.

Events are useful for orchestration and timely discovery, but must not be mistaken for a complete observation stream. The adapter must retain original event type, event payload, subscription/resource identity, event timestamp and receipt timestamp where available. Delivery/retry/expiration and reconciliation behavior must be tested; periodic REST reconciliation may be needed to recover missed notifications.

## 5. Surface C — Meet add-ons SDK

The Meet add-ons SDK lets a web application appear inside Meet and supports collaborative/shared experiences. This may eventually provide MACLE's in-meeting user interface.

The reviewed documentation does not establish that add-ons can access raw participant audio/video, individual media tracks, or the full meeting UI state. Do not infer media access from the ability to embed an application in Meet. Treat add-ons as a UI integration candidate only until a specific documented capability is verified.

## 5.1 Surface C2 — Companion mode as a secondary observation surface

Google Meet Companion mode must not be confused with a media-capture SDK.

Google documents Companion mode as a second-screen experience. Its microphone and meeting audio are disabled to avoid echo, and its camera is off by default. The user may enable a personal video tile in supported contexts, but that is the user's own camera feed; it does not expose the remote participants' individual video tracks to the companion client. The documented use cases focus on viewing presentations, sharing a screen, chat, polls, Q&A and host controls. The participant grid/video tiles are not available in the same way as a full audio/video join.

Consequently:
- Companion mode is **not** a route to obtain the meeting's audio.
- It is **not established** as a route to acquire remote participant camera streams.
- It may provide a secondary interaction/presentation surface, and potentially the user's own camera as an explicit personal-video feature; these are distinct observations.
- A presentation visible in Companion mode is not equivalent to the original presenter's camera or a separate media track.
- Do not assume that a second device running Companion mode can act as a camera-only observer for all participants.

### Multi-device identity and temporal correlation

Google's API model offers an important partial aid: a participant represents a person, while participant sessions are created per participant-device pair. The same person's full-audio/video connection and Companion-mode connection may therefore be represented as separate device sessions associated with participant identity, where Google resolves them to the same signed-in participant. This is useful for provenance and association, but it does not synchronize the devices' observations or guarantee that two independent capture clocks are aligned.

If MACLE ever combines observations from a primary device and a Companion device, it must preserve:
- the Google participant resource and each distinct participant-session resource;
- the source device and capture process identity;
- source timestamps, local monotonic timestamps, ingestion/receipt timestamps and any estimated clock offset separately;
- uncertainty bounds for temporal alignment;
- the observation modality and surface (e.g. presentation view, user camera, chat event, REST event);
- explicit association confidence and the evidence used to associate observations across devices.

Potential correlation signals include the shared conference record, participant identity where available, participant-session start/end times, event timestamps, and explicit user pairing between the two local MACLE clients. These signals can support a best-effort temporal association; they do not justify silently merging the streams into one synchronized media timeline.

A separate-device approach therefore has a significant coordination cost. It should be evaluated only if Companion mode provides a genuinely useful observation that cannot be obtained more simply on the primary device. It is not a prerequisite for the first Google Meet connector.

**Sources**
- Google Meet Companion mode help: https://support.google.com/meet/answer/11295507?hl=en — retrieved 2026-11-14.
- Google Meet Companion mode feature comparison: https://support.google.com/a/users/answer/11418474?hl=en — retrieved 2026-11-14.
- Meet participant and participant-session model: https://developers.google.com/workspace/meet/api/guides/participants — retrieved 2026-11-14.

## 6. Surface D — Meet Media API: not a sustainable path

Google's developer documentation states that the Meet Media API Developer Preview will not proceed to general availability and that its endpoints will be permanently shut down on **2027-01-15**. New signups are closed; existing approved preview participants retain access only until shutdown.

Consequences:
- Do not build a production adapter or long-lived architecture around Meet Media API.
- Do not treat preview access as a generally available capability.
- If historical preview behavior is useful for research, record it as temporary/deprecated evidence only.
- Re-check Google's official release notes before any implementation that could be affected by API lifecycle changes.

## 7. Live observation alternatives — research only

The absence of a sustainable documented raw-media API in the reviewed Meet REST/add-on interfaces does not prove that no other acquisition path exists. The following are candidates for study, not decisions:

### 7.1 User-controlled browser or desktop capture
Potentially allows local acquisition of the user's rendered meeting experience and selected system/tab audio, subject to browser/OS permissions and limitations.

Questions:
- Can capture be initiated transparently by the user and visibly indicated?
- Which browser/OS combinations expose tab audio, microphone, camera or rendered video?
- Can individual remote participant streams be separated, or is the result mixed/composited?
- How are screen sharing, layout changes, browser permissions, hardware acceleration, reconnects and multiple tabs handled?
- Does capture rely on unsupported/private Meet internals or DOM selectors that can break without notice?
- Can the application operate without collecting unrelated browser content?
- What do Google's terms and policies permit?

A browser extension must not be assumed to have privileged access to Meet internals. A general-purpose covert or background capture mechanism is out of scope.

### 7.2 Explicitly participating meeting bot
A bot may join as a visible participant and acquire media through a supported integration/provider. This changes meeting membership and participant experience and may be blocked by host/tenant policy.

Assess:
- visibility, disclosure and host admission;
- media granularity and screen-share fidelity;
- guest and authenticated meeting behavior;
- participant/session mapping;
- data processing, retention, residency, subprocessors and deletion;
- reliability, latency, cost and provider lock-in.

### 7.3 Third-party capture provider
A provider may offer a Meet-specific bot or desktop SDK. No provider is selected. Any provider evaluation must inspect exact Meet parity, media granularity, event semantics, provenance export, terms, security, privacy, retention, residency and operational constraints.

**Stage A does not authorize sending synthetic or real data to such a provider.** A later provider trial requires a separate explicit data-egress decision; real-meeting use requires a separate deployment-specific approval.

## 7.4 Initial single-device implementation

Following the project owner's instruction on 2026-11-14, the first executable prototype uses one computer and deliberately avoids Companion mode and inter-device synchronization.

The current implementation branch contains two local components:

1. **Chrome tab recorder:** a Manifest V3 extension restricted to `meet.google.com`. The user explicitly attests to synthetic-only testing in the extension settings, then starts/stops capture by clicking the toolbar icon. It records the rendered Meet tab as one composite video and the tab's audio output. The WebM and a provenance manifest are downloaded locally.
2. **Python REST/artifact client:** a desktop OAuth flow with the read-only Meet scope; organizer-scoped conference discovery or explicit retrieval of a known conference resource; participant and participant-session listing; recording/transcript/smart-note metadata; transcript entries; local SQLite revision storage; JSONL observation export.

The browser recorder is intentionally limited:
- It captures the visible tab rendering, not individual participant camera tracks.
- It captures audio output from the tab. The local microphone can be explicitly enabled and authorized; it is then mixed with tab audio, not kept as a separate track.
- It does not inspect private Meet internals or inject scripts into Meet.
- It records a composite presentation/layout, so layout changes and hidden participants cannot be reconstructed as independent source tracks.
- It stops when the selected tab begins any navigation or closes.
- It writes recording chunks to the browser's local Origin Private File System before download, avoiding full-recording buffering in extension memory.
- It does not send media to any server or third-party provider.

The Python client is complementary, not a substitute for live capture. Google REST resources preserve participant/session identities and transcript timestamps, but the local composite recording is not automatically diarized or frame-aligned with those resources. A later correlation step can use the conference resource and overlapping timestamps, but it must preserve uncertainty.

The extension's synthetic-only checkbox is an operator attestation, not proof that all participants/media are synthetic. The implementation must be used only with synthetic test meetings under the current approval. No real-meeting capture is authorized.

This is an initial working implementation contract. The first browser smoke test and live Google OAuth/API test still need to be performed in the user's Chrome/Google Cloud environment; code being present is not verification.

## 8. First useful product slice — implementation baseline for the prototype

A pragmatic first slice to validate with product requirements:
1. User-authorized Google OAuth connection with least-privilege scopes.
2. For the current meeting, resolve the active conference through `spaces.get` using the meeting code or space resource; for history, discover organizer-visible conference records or fetch a known conference resource.
3. Subscribe to relevant Workspace Events and persist source event provenance.
4. Reconcile events against Meet REST resources.
5. Retrieve available conference participants and participant sessions.
6. Retrieve transcripts, transcript entries, recordings metadata and smart notes when authorized and available.
7. Normalize these into MACLE observations while preserving original Google resource identifiers, source payloads, timestamps, uncertainty, retrieval time and artifact references.
8. Expose explicit coverage gaps: no raw live media, no guaranteed live transcript, missing/disabled artifacts, event delivery gaps, access denial and retention expiry.

This slice can provide useful post-meeting articulation and lifecycle context. It must not be marketed or specified as full live multimodal observation.

## 9. Minimum adapter mapping requirements

The future adapter should preserve at least:
- Google meeting-space resource name (but not the short-lived meeting code or meeting URI; Google advises against storing meeting codes long term);
- conference-record resource name;
- participant resource name;
- participant-session resource name;
- membership resource and role where relevant;
- original Workspace Event type and event resource;
- source event time, observation/receipt time and ingestion time as separate temporal facts;
- original transcript-entry resource, text, language, participant reference and timestamps;
- recording/transcript/smart-note resource identity and Drive artifact reference;
- OAuth principal and authorization context at a non-secret, auditable level;
- API version, retrieval time, pagination state and errors;
- explicit unavailable/not-authorized/not-generated/expired states.

Do not conflate a missing artifact with an empty meeting, a participant with a device session, or a transcript with raw audio evidence.

## 10. Validation plan

Under approved Stage A only:
- use synthetic fixtures and mocked Google API responses for deterministic domain/adapter tests;
- test pagination, duplicate events, delayed artifacts, missing artifacts, expired transcript-entry access, permission errors, subscription renewal and REST reconciliation;
- test mapping of one participant with multiple participant sessions and room-device representations;
- test source-time versus receipt-time preservation and out-of-order event handling;
- do not connect to real meetings or send data to external capture/transcription providers as part of this stage.

A later authorized integration test may use a controlled Google Workspace test environment. It must have a separate scope, identity, participant notice/consent assessment, data-retention plan and explicit approval.

## 11. Open research questions

- What is the minimum useful Meet product experience: post-meeting artifact ingestion, near-real-time lifecycle awareness, or both?
- Which OAuth scopes are truly required for the selected first slice, and which operations require organizer/participant roles or admin configuration?
- Which Workspace editions and admin policies affect artifact generation and API access?
- What are the exact Workspace Events subscription lifetimes, event delivery guarantees, retry behavior and reconciliation requirements?
- Can user-controlled browser/desktop capture provide sufficient local live observations without relying on unsupported Meet internals?
- Does Companion mode provide any observation surface that is genuinely additive to primary-device capture, and is its value worth the separate-device correlation cost?
- Can two MACLE clients on one conference reliably associate participant identity and calibrate clock offsets without treating participant-session identity as a media synchronization guarantee?
- Are visible bot-based routes acceptable for the intended product experience?
- What level of live multimodal fidelity is actually required by the initial competency questions?
- Which gaps are acceptable in the first usable product?

## 12. Official sources

- Google Meet REST API overview: https://developers.google.com/workspace/meet/api/guides/overview — retrieved 2026-11-14.
- Google Meet REST API v2 reference: https://developers.google.com/workspace/meet/api/reference/rest/v2 — retrieved 2026-11-14.
- Google Meet Space resource and `activeConference` field: https://developers.google.com/workspace/meet/api/reference/rest/v2/spaces — retrieved 2026-11-14.
- Google Meet meeting-space lifecycle and active conference lookup: https://developers.google.com/workspace/meet/api/guides/meeting-spaces-overview — retrieved 2026-11-14.
- Meet conference records and organizer-filtered discovery: https://developers.google.com/workspace/meet/api/guides/conferences — retrieved 2026-11-14.
- ConferenceRecord resource, including its 30-day `expireTime`: https://developers.google.com/workspace/meet/api/reference/rest/v2/conferenceRecords — retrieved 2026-11-14.
- Meet participants and participant sessions: https://developers.google.com/workspace/meet/api/guides/participants — retrieved 2026-11-14.
- Google Workspace Events for Meet: https://developers.google.com/workspace/events/guides/events-meet — retrieved 2026-11-14.
- Google Meet SDK/API overview (including add-ons and Media API lifecycle notice): https://developers.google.com/workspace/meet/overview — retrieved 2026-11-14.
- Google Meet API release notes (Media API shutdown announcement dated 2026-10-28): https://developers.google.com/workspace/meet/release-notes — retrieved 2026-11-14.
- Meet Media API overview (historical preview documentation): https://developers.google.com/workspace/meet/media-api/guides/overview — retrieved 2026-11-14.
- Chrome Extensions `tabCapture` API: https://developer.chrome.com/docs/extensions/reference/api/tabCapture — retrieved 2026-11-14.
- Chrome Extensions Offscreen API: https://developer.chrome.com/docs/extensions/reference/api/offscreen — retrieved 2026-11-14.
- Chrome Extensions Downloads API: https://developer.chrome.com/docs/extensions/reference/api/downloads — retrieved 2026-11-14.

---

This study records evidence and candidate paths. It does not select an implementation, provider, browser extension, bot, deployment model, retention policy, or legal basis.
