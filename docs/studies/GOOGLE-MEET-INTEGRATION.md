# Study — Google Meet integration

**Status:** current desk research and integration planning; no capture architecture, provider, add-on, or production deployment has been selected.  
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

Transcript entries are particularly useful for a first artifact integration: they provide discrete speech segments with participant association, timestamps, text and language code. Google documents a 30-day availability window for transcript entries after the conference. This is a time-bounded artifact interface, not a durable transcript archive guarantee.

Access is constrained by OAuth authorization/scopes, whether the authenticated user is a meeting owner or participant for the requested operation, Workspace configuration and policies, organizer/host settings, artifact generation and availability. Domain-wide delegation is a distinct administrative authorization path, not a default assumption for a consumer application.

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

## 8. First useful product slice — proposal, not a decision

A pragmatic first slice to validate with product requirements:
1. User-authorized Google OAuth connection with least-privilege scopes.
2. Discover eligible Meet spaces/conference records for the authorized principal.
3. Subscribe to relevant Workspace Events and persist source event provenance.
4. Reconcile events against Meet REST resources.
5. Retrieve available conference participants and participant sessions.
6. Retrieve transcripts, transcript entries, recordings metadata and smart notes when authorized and available.
7. Normalize these into MACLE observations while preserving original Google resource identifiers, source payloads, timestamps, uncertainty, retrieval time and artifact references.
8. Expose explicit coverage gaps: no raw live media, no guaranteed live transcript, missing/disabled artifacts, event delivery gaps, access denial and retention expiry.

This slice can provide useful post-meeting articulation and lifecycle context. It must not be marketed or specified as full live multimodal observation.

## 9. Minimum adapter mapping requirements

The future adapter should preserve at least:
- Google meeting-space resource name;
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
- Are visible bot-based routes acceptable for the intended product experience?
- What level of live multimodal fidelity is actually required by the initial competency questions?
- Which gaps are acceptable in the first usable product?

## 12. Official sources

- Google Meet REST API overview: https://developers.google.com/workspace/meet/api/guides/overview — retrieved 2026-11-14.
- Google Meet REST API v2 reference: https://developers.google.com/workspace/meet/api/reference/rest/v2 — retrieved 2026-11-14.
- Meet conference records: https://developers.google.com/workspace/meet/api/guides/conferences — retrieved 2026-11-14.
- Meet participants and participant sessions: https://developers.google.com/workspace/meet/api/guides/participants — retrieved 2026-11-14.
- Google Workspace Events for Meet: https://developers.google.com/workspace/events/guides/events-meet — retrieved 2026-11-14.
- Google Meet SDK/API overview (including add-ons and Media API lifecycle notice): https://developers.google.com/workspace/meet/overview — retrieved 2026-11-14.
- Google Meet API release notes (Media API shutdown announcement dated 2026-10-28): https://developers.google.com/workspace/meet/release-notes — retrieved 2026-11-14.
- Meet Media API overview (historical preview documentation): https://developers.google.com/workspace/meet/media-api/guides/overview — retrieved 2026-11-14.

---

This study records evidence and candidate paths. It does not select an implementation, provider, browser extension, bot, deployment model, retention policy, or legal basis.
