# MACLE — Observation envelope proposal

**Status:** PROPOSED conceptual envelope; not a JSON Schema, wire format, or accepted requirement.  
**Purpose:** define information that should travel with an observation so normalization does not discard source meaning, provenance, time, uncertainty, or derivation.

## 1. Design intent

An observation should be interpretable without guessing:
- what is being asserted or observed;
- which meeting occurrence and source it belongs to;
- when the described phenomenon occurred and when MACLE received it;
- whether it came from a platform, media, algorithm, human, or consumer;
- what processing produced it;
- which entities it refers to;
- what is unknown, uncertain, incomplete, or contradicted.

This envelope carries an observation or assertion. It is not the entire domain model and does not prescribe a storage record or transport format.

## 2. Candidate envelope sections

| Section | Candidate contents | Purpose |
|---|---|---|
| Identity | observation ID, type, schema/concept version | Stable identification and interpretation |
| Context | meeting ID, meeting occurrence ID, capture session ID | Situation and acquisition scope |
| Subject | entities and relations concerned | What the observation is about |
| Claim | predicate/type, value/payload, original source event type | What is being reported |
| Temporal | valid/event time, observation time, ingestion time, processing time | Preserve different clocks and temporal meanings |
| Origin | source kind, platform/provider, source resource ID, original payload reference | Preserve provenance |
| Derivation | direct report/media observation/extraction/annotation/interpretation, processor and version | Explain how the observation came to exist |
| Attribution | participant, endpoint, person hypothesis, speaker hypothesis references | Preserve identity distinctions |
| Evidence | evidence references, supporting and contradicting observations | Make claims auditable |
| Qualification | confidence/uncertainty, coverage, limitations, missing fields | Prevent false precision |
| Revision | correction, challenge, supersession, predecessor/successor links | Preserve change history |
| Governance | purpose/context label, access classification, retention/deletion state | Enable policy enforcement; semantics require separate decisions |

## 3. Orthogonal classification axes

Do not compress these into one type field.

### 3.1 Origin
- platform API or webhook;
- SDK callback;
- acquired media;
- imported artifact;
- user-provided metadata;
- human annotation;
- downstream consumer.

### 3.2 Derivation
- platform-reported assertion;
- direct media observation;
- algorithmic extraction;
- human annotation/correction;
- downstream interpretation.

### 3.3 Assertion status
- asserted;
- observed;
- hypothesized;
- challenged;
- contradicted;
- corrected;
- superseded;
- unknown.

### 3.4 Coverage
- complete for declared source and interval;
- partial;
- unavailable from this source;
- interrupted/gap;
- not tested;
- unknown.

### 3.5 Confidence and uncertainty
Confidence is producer-specific and must not be compared across models or sources unless calibrated. Preserve:
- value and scale, if numeric;
- producer and version;
- interpretation of the scale;
- uncertainty interval or qualitative category where appropriate;
- absence of a confidence estimate when none exists.

## 4. Time fields

A candidate time block should keep separate fields for:
- valid_time: time the claim says the phenomenon occurred;
- observed_time: time the source/capture component observed or reported it;
- ingested_time: time MACLE received and recorded it;
- processed_time: time an extraction/transform ran.

For interval-bearing observations, each relevant time dimension may need a start/end pair. Preserve source timestamp text, clock identity, timezone, precision, and estimated uncertainty.

Do not fill missing valid time with ingested time. Do not compare timestamps from different clocks as if they were perfectly synchronized.

## 5. Provenance and derivation

An observation should be traceable through a chain such as:

source platform event → capture adapter → normalized platform assertion → derived event

or:

audio source → media segment → speech activity extraction → diarization segment → speaker hypothesis → downstream interpretation

Each derivation step should identify input observations/artifacts/media intervals, processing activity, processor/model and version, material parameters/configuration reference, output observation identifiers, processing time, and known limitations/failure state.

Original source payloads should be retained or securely referenced where lawful and necessary. A normalized representation must not overwrite the original source event name or payload.

## 6. Identity and attribution

The envelope may reference:
- platform participant identity;
- participant session;
- endpoint;
- person hypothesis;
- speaker hypothesis;
- unresolved/unknown actor.

These references must remain distinct. An observation attributed to a platform participant must not automatically be attributed to a human Person. Any inferred association should identify its derivation, evidence, confidence, and validity interval.

## 7. Revision and conflict

A corrected observation should reference the prior observation and state whether it corrects a value, narrows/expands a validity interval, changes an attribution hypothesis, challenges an earlier assertion, supersedes an earlier view, or records an unresolved contradiction.

Do not erase conflicting evidence merely to produce one current value. A consumer may request a current projection, but the underlying assertion history should remain inspectable subject to the eventual retention/deletion policy.

## 8. Minimal illustrative example (not a schema)

A platform reports that participant P raised a hand at source time T. MACLE stores:
- the original platform event name and payload reference;
- platform participant P and meeting occurrence M;
- source event time T and ingestion time I separately;
- origin = platform event;
- derivation = platform-reported assertion;
- assertion status = asserted by platform;
- source and connector version;
- coverage and any missing timestamp precision.

A separate speech extraction may report a speech interval overlapping T. MACLE relates the two observations temporally; it does not invent a causal relation or claim that the hand raise was a response to the speech.

## 9. What this proposal does not decide

This proposal does not define normative field names, an encoding, JSON Schema, CloudEvents profile, RDF/OWL ontology, PROV serialization, database layout, or event transport. It does not select append-only storage or retention policy. Those decisions require further modeling, standards study, and explicit arbitration.
