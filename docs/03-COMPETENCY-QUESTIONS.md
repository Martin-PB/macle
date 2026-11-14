# MACLE — Competency questions

**Status:** PROPOSED working draft. These questions are not requirements and establish no feature commitment.  
**Scope:** initial operational domain of videoconferencing meetings, as accepted in ADR-0001.

## 1. Purpose

Competency questions (CQs) describe what a consumer may need to ask of MACLE's structured observations. They test whether a candidate domain model is expressive enough. A CQ is not a promise that MACLE can answer it in every capture configuration. Every answer must be qualified by source availability, capture coverage, temporal precision, attribution uncertainty, and provenance.

## 2. Candidate competency questions

| ID | Question | Candidate information needed | Important qualification |
|---|---|---|---|
| CQ-01 | Which platform participants and endpoints were present during interval T? | Meeting occurrence, participant identities, endpoints, sessions, validity intervals | Platform presence is not proof of a particular human's physical presence |
| CQ-02 | Which person or people may have been behind endpoint E during interval T, and what supports each hypothesis? | Person hypotheses, endpoint relations, evidence, confidence, validity interval | Must support unknown and multiple people; never infer one person per endpoint |
| CQ-03 | Who was speaking during interval T, according to each available source? | Speech segments, platform speaker signals, diarization outputs, attribution hypotheses | Platform attribution and media-derived diarization remain distinct |
| CQ-04 | What speech segments overlapped, and what was their temporal relationship? | Speech intervals, time bases, uncertainty, interval relations | Clock uncertainty may prevent definitive ordering |
| CQ-05 | What was being shared on screen during speech segment S? | Share lifecycle, media source, screen observations, time alignment | Screen pixels are not necessarily the underlying document or semantic content |
| CQ-06 | Which participant or endpoint initiated, held, paused, resumed, or stopped a screen share? | Platform events, share source, participant/session links | Attribution depends on platform support and provenance |
| CQ-07 | Which chat messages, reactions, or hand-raise events occurred during interval T? | Interaction observations, sender references, timestamps | Absence from a connector is not proof that an interaction did not occur |
| CQ-08 | What changed in shared visual content between T1 and T2? | Screen observations, extracted visual-change events, source intervals | Pixel differences may be scrolling, animation, cursor movement, or an edit |
| CQ-09 | What was the meeting's observable lifecycle and who/what changed state? | Meeting events, participant sessions, capture events, state transitions | Meeting lifecycle and MACLE capture lifecycle are distinct |
| CQ-10 | Where are the gaps or blind spots in the captured timeline? | Capture health, source availability, dropped media, permission failures | A gap must not be interpreted as evidence that nothing happened |
| CQ-11 | What is the provenance chain for observation O? | Source, source ID, media interval, capture path, processor/model/version, derivation links | Incomplete provenance must be explicit |
| CQ-12 | What did MACLE have evidence for as of time T, and what is the current corrected view? | Revision history, valid time, recorded time, correction and supersession links | Historical views must not be silently rewritten |
| CQ-13 | Which observations or assertions were corrected, challenged, or superseded, and by what evidence? | Assertion history, challenge/correction relations, evidence links | Supersession is not necessarily deletion |
| CQ-14 | Which observations depend on a source artifact, and what would be affected if it were withdrawn or deleted? | Provenance graph, derivation dependencies, deletion/retention state | Needed for lifecycle propagation |
| CQ-15 | Which facts are platform-reported, directly media-observed, algorithmically extracted, human-annotated, or interpreted downstream? | Evidence/derivation axes, agent and source metadata | These classifications are orthogonal |
| CQ-16 | What is known about a participant's media state during interval T? | Platform state events, media availability, source health | A mute indicator, missing audio, and absence of speech are different observations |
| CQ-17 | Which participant sessions belong to the same platform participant, and which endpoints did they use? | Platform identity, session IDs, endpoint IDs, time intervals | Preserve platform identity semantics and stability |
| CQ-18 | Which claims are uncertain, conflicting, or unsupported by available evidence? | Confidence/uncertainty, contradiction relations, coverage and provenance | Do not force a single resolved answer when evidence conflicts |

## 3. Candidate negative / boundary questions

| ID | Question | Boundary |
|---|---|---|
| NQ-01 | What did a participant really intend? | Intent is downstream interpretation, not a directly observed event |
| NQ-02 | Was a statement true? | Truth evaluation is outside the perception layer |
| NQ-03 | Did a participant understand or agree? | Presence, silence, facial expression, or reaction does not establish understanding or agreement |
| NQ-04 | What emotion was a participant experiencing? | Not a baseline observation; workplace/education emotion inference has specific AI Act restrictions |
| NQ-05 | What action should the organization take? | Action selection belongs to a downstream consumer or human |
| NQ-06 | Was a person attentive, engaged, productive, or performing well? | Evaluative interpretations must not be smuggled in as neutral observations |

## 4. Coverage and answerability

Every answer should state:
- which meeting occurrence and interval it concerns;
- which source(s) were available;
- which capture path and version supplied them;
- whether the result is a platform assertion, direct media observation, extraction, annotation, or interpretation;
- whether it is complete, partial, uncertain, contradictory, or unavailable;
- the timestamp basis and uncertainty;
- whether it depends on a human-identity hypothesis.

“Unknown”, “not observed”, “not available from this source”, and “capture gap” are valid answers. Missing evidence must not become a negative fact.

## 5. Relationship to the domain model

The candidate entities and relations are described in DOMAIN-MODEL.md. The observation envelope is described in OBSERVATION-ENVELOPE.md. Revise the model when a CQ cannot be represented without inventing facts, losing provenance, collapsing distinct identities, or overstating certainty.

## 6. What this draft does not decide

This draft does not baseline the CQs as product requirements, select a demonstrator, define a canonical event taxonomy or query API, or require every question to be answerable in the first release.
