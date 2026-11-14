# MACLE — Project map

This document separates the project's conceptual foundation, initial product scope, platform integrations, candidate tools, and unresolved decisions. It is a navigation document, not an implementation specification.

## 1. Conceptual foundation

**MACLE — Multimodal Articulation through Concrescence of Linked Events**

MACLE is conceived as a perception and articulation layer: it captures, extracts, normalizes, structures, correlates, and exposes observations about a situation. Its value lies in preserving relations between signals, participants, events, time, and context—not merely collecting independent media streams.

The consuming system (an agent, an LLM, or another application) remains responsible for interpretation, reasoning, projection, and action. MACLE does not require a proprietary LLM or a specific agent architecture.

This conceptual foundation is deliberately broader than the first product.

## 2. First application domain: meetings

The focus is the meeting, not only what is said but the wider situation in which the meeting unfolds.

The meeting is treated as a temporally evolving situation involving people, interactions, media, shared content, and technical events. Speech is only one observable dimension.

## 3. Initial operational scope: videoconferencing

**Confirmed scope:** the first operational target is a meeting mediated by videoconferencing software.

This includes meetings where:
- one person participates from one computer;
- several people share one computer, camera, or room endpoint;
- participants join from multiple devices;
- audio, camera video, screen sharing, chat, and platform events coexist.

A shared camera or endpoint does not turn this initial use case into an in-person meeting. Dedicated in-person and room-sensing scenarios are outside the initial operational scope.

## 4. Separate workstreams

| Workstream | Purpose | Status |
|---|---|---|
| Conceptual foundation | Situation, events, relations, time, concrescence | Established as framing |
| Meeting domain model | Describe what can happen in a meeting independently of vendors | PROPOSED conceptual draft added; review and validation pending |
| Videoconferencing platforms | Study platform APIs, SDKs, permissions, limitations | Google Meet is the first product integration priority; Discord is deferred; comparative research remains |
| Capture mechanisms | Native SDK, bot participant, desktop capture, post-meeting artifacts | Candidate strategies documented; repeatable evaluation protocol added |
| Adjacent tools | Transcription, diarization, recording, calendar, chat, documents, workflow tools | Study candidates |
| MACLE product requirements | Decide what MACLE itself must provide | Not yet baselined; competency questions drafted as proposals |
| Architecture and implementation | Select interfaces, storage, runtime, languages, deployment | Android-native offline-first capture with optional agent streaming is the preferred user-facing direction under feasibility study; remote Meet audio capture is not yet established. Existing Chrome connector retained as fallback/reference. Synthetic-only/local-only validation boundary remains in force. |

## 5. Document governance

Keep these categories distinct:

- **Concept:** explanatory or philosophical framing; not automatically a software requirement.
- **Scope:** an explicitly accepted boundary of the product.
- **Requirement:** a capability MACLE is expected to provide.
- **Study:** research into an external technology, product, standard, or approach.
- **Decision:** an explicit choice with rationale and consequences.
- **Open question:** an unresolved issue requiring evidence or user arbitration.
- **Implementation:** work actually present in the repository.
- **Verified:** behavior actually tested in a stated environment.

A study recommendation is not a decision. A vendor feature is not automatically a MACLE requirement. An API capability is not proof that access is available to every tenant, account, participant, or meeting.

## 6. Current documents

- [Initial scope](01-SCOPE.md)
- [Initial conceptual domain model](02-DOMAIN-MODEL.md) (PROPOSED)
- [Competency questions](03-COMPETENCY-QUESTIONS.md) (PROPOSED)
- [Observation envelope](04-OBSERVATION-ENVELOPE.md) (PROPOSED)
- [Meeting observation catalogue](studies/MEETING-OBSERVATION-CATALOG.md)
- [Videoconferencing platform study](studies/VIDEOCONFERENCING-PLATFORMS.md)
- [Google Meet first-integration study](studies/GOOGLE-MEET-INTEGRATION.md) (invitee-side participation; REST/OAuth optional enrichment)
- [Android capture feasibility and product direction](studies/ANDROID-CAPTURE-FEASIBILITY.md) (Android-first investigation; MediaProjection, playback-audio eligibility, offline package and optional agent streaming)
- [Capture strategy study](studies/CAPTURE-STRATEGIES.md)
- [Platform capability and evidence matrix](studies/PLATFORM-CAPABILITY-MATRIX.md)
- [Capture evaluation protocol](studies/CAPTURE-EVALUATION-PROTOCOL.md)
- [Data protection and governance study](studies/DATA-PROTECTION-AND-GOVERNANCE.md)
- [Adjacent tools and components study](studies/ADJACENT-TOOLS.md)
- [Provenance, temporal relations, and event-envelope standards study](studies/PROVENANCE-TIME-EVENT-STANDARDS.md)
- [Open reference environments study](studies/REFERENCE-ENVIRONMENTS.md)
- [Data egress and privacy gate](studies/DATA-EGRESS-AND-PRIVACY-GATE.md) (PROPOSED)
- [Temporal and revision semantics](studies/TEMPORAL-AND-REVISION-SEMANTICS.md) (PROPOSED)
- [Architecture decision template](decisions/TEMPLATE.md) (PROPOSED)
- [Issue taxonomy and decomposition proposal](GOVERNANCE-ISSUES.md) (PROPOSED)
- [Reference meeting fixture 01](fixtures/REFERENCE-MEETING-01.md) (PROPOSED; not yet executed)
- [Open questions](OPEN-QUESTIONS.md)
- [Google Meet local connector](../connectors/google-meet/README.md) (desktop/browser fallback and reference prototype; synthetic-only validation)
- [Google Meet single-device smoke test](studies/GOOGLE-MEET-SINGLE-DEVICE-SMOKE-TEST.md) (manual validation pending; includes one-command post-capture workflow)
- [Local speech transcription study](studies/LOCAL-SPEECH-TRANSCRIPTION.md) (first optional local ASR backend)
- [Local video frame observations](studies/LOCAL-VIDEO-FRAME-OBSERVATIONS.md) (sparse local visual references)
- [Local HTML report generation](../connectors/google-meet/README.md#local-html-report) (offline inspection of observation exports)
- [Google Meet single-device participant watch](../connectors/google-meet/README.md#watch-participant-state-during-a-synthetic-meeting) (sampled REST polling; implementation in progress)
- [Decision register](decisions/README.md)
- [ADR 0001 — Initial scope](decisions/ADR-0001-INITIAL-SCOPE.md)

- [Cross-platform architecture feasibility](studies/CROSS-PLATFORM-ARCHITECTURE.md) (shared core, native capture adapters, WASM assessment; candidate architecture only)

- [Cross-platform architecture feasibility](studies/CROSS-PLATFORM-ARCHITECTURE.md) (shared core, native capture adapters, WASM assessment; candidate architecture only)
- [Shared Rust core](../core/macle-core/README.md) (session/observation contracts, JSONL log, SHA-256; first implementation slice)
- [Android native core check](../apps/android/README.md) (imports and validates a session manifest through the shared Rust JNI library; capture not yet implemented)
- [Chrome extension build](../connectors/google-meet/chrome-extension/BUILD.md) (WASM core build prerequisite)

## 7. Important restraint

The README remains the concise public introduction. These working documents carry the detailed distinctions and may evolve without forcing premature technical commitments into the README.
