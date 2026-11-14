# MACLE — Initial conceptual domain model

**Status:** PROPOSED conceptual model for discussion; not an accepted schema, requirement baseline, or implementation design.  
**Scope:** initial operational domain of videoconferencing meetings.

## 1. Modeling principles

1. **Situation before inventory.** A meeting is a temporally evolving situation, not merely independent streams or transcript lines.
2. **Relations are first-class.** Participants, endpoints, sessions, media, observations, events, and artifacts are explicitly linked.
3. **Identity is not assumed.** A platform participant is not necessarily one human; one human may use multiple endpoints; one endpoint may represent several humans.
4. **Observation is not interpretation.** Observable/extracted material remains distinct from downstream conclusions.
5. **Evidence is qualified.** Assertions retain source, derivation, time, uncertainty, and coverage limitations.
6. **Time is multi-dimensional.** Event time, observation time, ingestion time, and processing time are not interchangeable.
7. **Corrections are traceable.** A correction does not silently erase what was previously observed or believed.
8. **Vendor semantics are preserved.** Normalization must not destroy original platform identifiers, event names, payloads, or modality distinctions.

## 2. Candidate conceptual entities

These types do not prescribe table names, programming-language classes, serialization, or storage.

### 2.1 Situation and lifecycle
- **Meeting:** conceptual meeting as a planned or recognized social/organizational event.
- **Meeting occurrence:** one concrete execution, with its own start/end and platform conference/session identifiers.
- **Capture session:** MACLE's acquisition lifecycle for a meeting occurrence. It may start late, stop early, restart, or operate alongside another capture path.
- **Meeting event:** an occurrence or state transition in the meeting domain, such as start/end, join/leave, mute change, hand raise, or share lifecycle.
- **Capture event:** an occurrence in MACLE's own capture process, such as source connected, permission lost, media gap detected, or capture restarted.

Meeting occurrence and capture session are distinct. A meeting can continue while MACLE capture is interrupted.

### 2.2 Human, platform identity, endpoint, and session
- **Person:** a real human being, whether identified, partially identified, or unknown.
- **Platform participant identity:** an identity/account/participant object represented by a conferencing platform.
- **Endpoint:** a device or client, such as desktop, phone, browser client, or room system.
- **Participant session:** one connection/session of a platform participant through an endpoint during a meeting occurrence.
- **Person hypothesis:** a provisional claim that an observation or set of observations may correspond to a person.
- **Attribution assertion:** a sourced or inferred relation between a person hypothesis, platform participant, endpoint, speaker segment, or other entity.

Do not require a Person record for every platform participant. A participant may remain unidentified. Do not require a one-to-one relation between Person, platform participant, Endpoint, or Participant session.

### 2.3 Media and shared content
- **Media source:** a source of acquired audio, video, screen-share, or other media.
- **Media segment:** a time-bounded portion or reference into a media source.
- **Shared-content source:** the platform/application/window/document/board being shared, when identity is exposed.
- **Content artifact:** a file, document, slide deck, image, link, or other artifact associated with the meeting.
- **Media observation:** a direct observation of acquired media, such as a received frame or audio interval.
- **Content observation:** an observation about what was visible or shared, without assuming access to the underlying semantic document.

A screen capture is not automatically the underlying document. A composite gallery is not automatically a set of individual camera streams.

### 2.4 Observation, event, assertion, and interpretation
- **Observation:** a recorded claim about something observed or reported by a source, with provenance and temporal scope.
- **Event:** a modeled occurrence or state change in the meeting situation. It may be directly reported by a platform or derived from observations.
- **State observation:** a time-scoped observation of a condition, such as a microphone indicator being muted or a camera stream being available.
- **Extraction:** a derived result produced by a processing component, such as speech recognition, diarization, OCR, or visual-change detection.
- **Human annotation:** a label or correction supplied by a human evaluator or authorized user.
- **Interpretation:** a higher-level meaning or conclusion produced by a downstream consumer.
- **Claim/assertion:** a proposition made by a source, extraction process, human, or consumer, with explicit epistemic/provenance status.

An Event is not synonymous with an Observation. An observation is evidence-bearing information; an event is a domain-level occurrence that may be supported by multiple observations. A platform-reported event can be stored as an observation of a platform assertion and mapped to a normalized event without discarding its original form.

### 2.5 Provenance and processing
- **Source:** platform API, SDK, media stream, uploaded artifact, human annotation, or other origin.
- **Capture adapter:** component that acquires source data and preserves source identity.
- **Processor:** component that transforms or extracts observations.
- **Processing activity:** one execution of capture, extraction, alignment, or transformation.
- **Model/tool version:** versioned identity of software/model used.
- **Evidence item:** source material or reference supporting an observation or assertion.
- **Derivation relation:** relation from an output observation to input observations, media segments, artifacts, or processing activities.

## 3. Candidate relations

This is an initial starter set, not a closed ontology.

| Relation | From → To | Meaning |
|---|---|---|
| hasOccurrence | Meeting → Meeting occurrence | A meeting can have one or more concrete occurrences |
| hasCaptureSession | Meeting occurrence → Capture session | An occurrence can have multiple capture sessions |
| representedBy | Person hypothesis → Person | A hypothesis may refer to an identified person |
| usesPlatformIdentity | Person hypothesis / Participant → Platform participant identity | Sourced or inferred association, not an identity axiom |
| connectedThrough | Platform participant identity → Participant session | A platform participant connects through one or more sessions |
| usesEndpoint | Participant session → Endpoint | Session is associated with an endpoint |
| produces | Media source → Media segment | Source yields segments or intervals |
| observes | Source / Processor / Human → Observation | Agent/source produces an observation |
| reports | Observation → Source assertion | Observation preserves a source's reported assertion |
| supports | Evidence item → Claim/assertion | Evidence supports a claim with qualification |
| derivedFrom | Observation → Observation / Media segment / Artifact | Output depends on prior source material |
| about | Observation / Event → Entity | Observation/event concerns an entity |
| occursDuring | Event / Observation → Meeting occurrence | Temporal containment in an occurrence |
| attributedTo | Speech segment / Event → Participant / Person hypothesis / Endpoint | Sourced or inferred attribution |
| overlaps | Temporal entity ↔ Temporal entity | Intervals overlap |
| precedes | Temporal entity → Temporal entity | One event/interval precedes another when supported by time evidence |
| supersedes | Assertion / Observation → Earlier assertion / observation | A later version replaces an earlier view without erasing history |
| challenges | Claim → Claim | Evidence or actor contests a claim |
| contradicts | Claim / Observation ↔ Claim / Observation | Claims cannot all be accepted together under a given interpretation |
| hasGap | Capture session → Time interval / Source | Coverage is missing or degraded during an interval |

Relations asserting identity, attribution, or causality should themselves be qualified by source, derivation, temporal scope, and uncertainty.

## 4. Identity as qualified hypotheses

The model should not force early entity resolution. A person hypothesis may have no resolved Person target; link to one or more candidate Persons; be supported by voice, video, user annotation, platform metadata, or a combination; apply only for a bounded interval; be challenged or contradicted; and be superseded without deleting history.

The model must support:
- one Endpoint associated with several Person hypotheses;
- one Person associated with multiple Endpoints over time;
- one Platform participant identity with several Participant sessions;
- several Platform identities associated with one Person hypothesis, if evidence supports it;
- no identity conclusion at all.

A diarization label such as “speaker 2” is a session-scoped speaker hypothesis, not a Person identifier. A platform account is a platform identity, not proof of the human operating the endpoint.

## 5. Time model

At least four temporal dimensions should be preserved where available:

1. **Valid/event time:** when the meeting phenomenon is said to have occurred.
2. **Observation time:** when the source or capture component observed/reported it.
3. **Ingestion time:** when MACLE received and recorded it.
4. **Processing time:** when a transformation or extraction was performed.

Each time value should preserve original source representation, normalized representation if available, clock source or time basis, timezone/UTC conversion, precision and uncertainty, interval start/end where relevant, and ordering uncertainty across clocks or streams.

A missing event time must not be silently replaced with ingestion time. If only receipt time is known, state that it is receipt time.

The choice of interval algebra, point-event semantics, and canonical timestamp representation remains a study item. Allen interval relations are a candidate reference, not yet adopted.

## 6. Evidence and epistemic dimensions

Avoid one overloaded field called “confidence” or one mutually exclusive evidence enum.

Candidate orthogonal dimensions:
- **Origin:** platform, media, user, human evaluator, external artifact, downstream consumer.
- **Derivation:** direct report, direct media observation, algorithmic extraction, human annotation, interpretation.
- **Assertion status:** asserted, observed, hypothesized, challenged, contradicted, corrected, superseded, unknown.
- **Confidence/uncertainty:** numeric, categorical, interval, or unavailable; semantics defined per producer.
- **Coverage:** complete for stated source/window, partial, unavailable, interrupted, not tested.
- **Verification:** not tested, tested with environment/date, independently reviewed, or another explicitly defined state.

These dimensions describe different things. A platform-reported event can be directly observed as an API payload while the underlying real-world claim remains an assertion by that platform. An algorithmic extraction can be human-reviewed without becoming a direct platform report.

## 7. Revision, correction, and historical views

A candidate model should preserve both what was recorded at a given system time and what time interval the observation claims to describe.

A correction should normally create a new assertion/observation linked to the earlier one, rather than silently mutate history. This supports “what did the system believe at time T?” and “what is the current corrected view?”

This is a proposed direction only. Append-only storage, mutable projections, tombstones, and retention/deletion behavior require a separate decision. Privacy deletion requirements may constrain historical availability.

## 8. Capture coverage and absence

The model must distinguish:
- an observed event;
- an event not observed despite a healthy and sufficiently complete source;
- an event unavailable from the chosen platform/API;
- an interval where capture was interrupted;
- an event not tested;
- an event known not to have occurred from an authoritative source.

“Not observed” is not equivalent to “did not happen”. Capture gaps and source limitations must be representable as first-class evidence.

## 9. Relationship to other drafts

The candidate envelope in OBSERVATION-ENVELOPE.md is intended to carry one observation or assertion and its provenance/temporal qualification.

The competency questions in 03-COMPETENCY-QUESTIONS.md test whether this model is expressive enough. If an answer requires an entity or relation not represented here, revise the conceptual model before defining serialization or database schema.

## 10. What this draft does not decide

This document does not adopt a formal ontology, serialization, database, event bus, append-only architecture, identity-resolution algorithm, AI model, capture platform, or API. It does not make every candidate entity or relation a product requirement.
