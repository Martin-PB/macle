# Fixture — Reference videoconference scenario 01

**Status:** PROPOSED test fixture specification; no execution has been performed.  
**Purpose:** define a reproducible meeting scenario and human-annotated ground-truth timeline for evaluating MACLE capture paths.  
**Platform independence:** the scenario is written in domain terms; a platform-specific execution mapping must be recorded for each run.

## 1. Objective

Exercise the central MACLE modeling and capture challenges in one small, repeatable meeting:

- multiple human beings behind one shared camera/microphone/endpoint;
- one person using more than one device over time;
- separate participant, endpoint, session, media-source, and person identities;
- overlapping speech and cross-modal temporal relations;
- screen-share changes, chat, hand raise, mute/camera changes;
- capture interruption and recovery;
- source provenance and missing-evidence reporting.

This fixture is intentionally not a test of high-level meeting understanding, intent, sentiment, emotion, productivity, or truth evaluation.

## 2. Test actors and topology

Use fictional labels in all fixture records. The names below are labels for the test, not real identities.

| Person label | Platform participant | Endpoint | Topology | Known ground truth |
|---|---|---|---|---|
| PERSON-A | PARTICIPANT-A | ENDPOINT-A | Individual laptop, camera and microphone | One tester |
| PERSON-B | PARTICIPANT-BC | ENDPOINT-BC | Shared laptop/camera/microphone in a room | One of two co-located testers |
| PERSON-C | PARTICIPANT-BC | ENDPOINT-BC | Same shared endpoint as PERSON-B | Second co-located tester |
| PERSON-D | PARTICIPANT-D | ENDPOINT-D1, then ENDPOINT-D2 | Phone, then laptop; same platform account where supported | One tester changes device |

Important expected topology:
- PERSON-B and PERSON-C are two distinct humans represented by one platform participant and one endpoint.
- PERSON-D is one human represented by two endpoints and possibly two participant sessions.
- The platform may report only PARTICIPANT-BC for the shared endpoint. It must not be expected to identify PERSON-B and PERSON-C separately.
- Human annotation supplies fixture ground truth; it must remain distinct from what the capture adapter actually observed.

## 3. Preparation

Before each run:

1. Select and record the reference platform and exact server/client versions.
2. Create the meeting and record its platform meeting/conference identifier.
3. Create test accounts/identities for the four platform participants.
4. Prepare ENDPOINT-BC with PERSON-B and PERSON-C visible in the same camera view where feasible, with one shared microphone.
5. Prepare the phone and laptop used by PERSON-D.
6. Prepare a short synthetic slide deck with three visibly distinct slides and no personal data.
7. Prepare a chat message with a unique fixture marker.
8. Synchronize test clocks as far as practical and record the clock source and measured offset.
9. Inform all testers of the recording/capture procedure, signals captured, test purpose, storage location, and deletion plan. Do not use unsuspecting participants or real meeting content.
10. Record the capture configuration and permissions before starting.

The fixture's controlled participation does not by itself establish legal compliance for other deployments. Use a separate privacy/security review for any non-test participant data.

## 4. Scripted timeline

Times are relative to the first participant joining. The operator should announce each step and record actual execution time in the run log. Target times are not a substitute for actual timestamps.

| Target time | Actor | Action | Expected domain observations |
|---|---|---|---|
| 00:00 | PERSON-A | Join from ENDPOINT-A and become host/moderator | Participant join; participant session; endpoint association |
| 00:20 | PERSON-B and PERSON-C | Join together through ENDPOINT-BC | One platform participant/session may represent two human-presence facts |
| 00:40 | PERSON-D | Join from phone ENDPOINT-D1 | Participant join and phone endpoint/session |
| 01:00 | PERSON-A | Speak alone for 15 seconds using a scripted sentence | Speech interval attributed to platform participant A; media-derived speaker label if available |
| 01:30 | PERSON-B | Speak alone for 12 seconds from the shared endpoint | Audio from PARTICIPANT-BC; human ground truth identifies PERSON-B |
| 01:55 | PERSON-C | Speak alone for 12 seconds from the same endpoint | Same platform participant/endpoint; human ground truth identifies PERSON-C |
| 02:20 | PERSON-B and PERSON-C | Speak simultaneously for 10 seconds | Overlapping speech; one endpoint/media source may contain both voices |
| 02:45 | PERSON-A | Mute and unmute microphone | Platform state event if exposed; media discontinuity/state evidence |
| 03:05 | PERSON-A | Start screen share on slide 1 | Screen-share start, owner, media source and slide observation |
| 03:35 | PERSON-D | Send fixture chat marker “FIXTURE-CHAT-01” | Chat message, sender, text, source timestamp |
| 03:55 | PERSON-B | Raise hand from the shared endpoint | Platform event attributed to PARTICIPANT-BC; human ground truth says PERSON-B performed the action |
| 04:15 | PERSON-A | Change shared content from slide 1 to slide 2 | Visual/content change within same share interval |
| 04:40 | PERSON-C | Speak while slide 2 is displayed | Speech interval temporally overlaps shared content |
| 05:05 | PERSON-A | Stop screen sharing | Screen-share stop event and end of media interval |
| 05:30 | PERSON-D | Leave the meeting from ENDPOINT-D1 | Participant/session leave or disconnect event |
| 05:50 | PERSON-D | Rejoin from ENDPOINT-D2 using the same account where supported | New endpoint/session association; same human ground truth |
| 06:15 | PERSON-A | Start sharing slide 3 | New share interval and content observation |
| 06:35 | PERSON-B and PERSON-C | Alternate short utterances, then overlap for 8 seconds | Multiple human speakers behind one participant and endpoint |
| 07:00 | PERSON-A | Stop sharing and end the meeting | Share stop; meeting end |
| 07:20 | Operator | Stop the MACLE capture process and export evidence | Capture-session end, final health state, artifact references |

### Optional fault-injection run

Run separately from the baseline:
- interrupt the observer's network for 10 seconds while the meeting continues;
- restart the observer process;
- reconnect and reconcile participant/session/track state;
- record any lost events/media and whether the system reports a capture gap.

Do not mix fault-injection results into the baseline run without clearly marking the changed conditions.

## 5. Human-annotated ground truth

The ground-truth timeline must be produced from the test script and direct human observation by the test team. It is not the MACLE output and must not be injected into the capture result.

Each annotation should contain:

| Field | Meaning |
|---|---|
| annotation_id | Stable identifier for the annotation |
| run_id | Run to which the annotation belongs |
| actor_person_id | Test-only person label, or unknown |
| platform_participant_id | Platform participant label, if known |
| endpoint_id | Endpoint label, if known |
| action_or_observation | Controlled action or directly observed test fact |
| valid_start / valid_end | Actual time interval, where applicable |
| clock_source | Clock used by the annotator |
| evidence_reference | Reference to operator log, fixture recording, or other ground-truth evidence |
| annotator_id | Test annotator identity or role |
| annotation_status | Draft, reviewed, adjudicated, or disputed |
| notes | Ambiguity, deviation from script, or uncertainty |

Use the proposed HUMAN_ANNOTATED derivation/evidence label for these records, subject to later terminology review. An annotation must not claim more than the annotator actually observed.

### Annotation procedure

- One annotator records the actual action times and actor labels during the run.
- A second annotator independently reviews the reference recording and the operator log.
- Disagreements are retained and adjudicated explicitly; do not silently overwrite the first annotation.
- If an action did not occur as scripted, annotate what actually happened.
- If the actor is uncertain, use unknown rather than guessing.
- Preserve the difference between person ground truth and platform participant/endpoint attribution.

## 6. Evaluation outputs and metrics

For each acquisition path, produce a separate capture timeline and compare it with the human-annotated ground truth.

Candidate metrics:
- **Event precision/recall:** correct event detection within a stated time tolerance.
- **Temporal error:** difference between captured and annotated start/end times.
- **Attribution accuracy:** measured separately at platform-participant, endpoint, and person-hypothesis levels.
- **Overlap correctness:** whether simultaneous speech intervals and overlapping cross-modal events are preserved.
- **Capture-gap detection:** whether induced or observed blind spots are represented.
- **Provenance completeness:** proportion of observations with a resolvable source and derivation chain.
- **Revision traceability:** whether corrections and adjudications preserve prior assertions.
- **Recovery completeness:** whether events/tracks missed during interruption are reconciled or reported as unavailable.

No numeric acceptance thresholds are set in this fixture draft. Thresholds must be defined only after the measurement method and test environment are validated.

## 7. Expected result format

Each run should produce:
- run configuration and environment record;
- scripted timeline with actual execution times;
- human-annotated ground-truth timeline;
- raw capture references where authorized;
- normalized observation timeline;
- platform event and media coverage matrix;
- per-metric results and time tolerances;
- failure, gap, and recovery report;
- unresolved annotation disagreements;
- reviewer and review date.

## 8. Pass/fail boundary

A successful fixture run does not mean that MACLE understands the meeting. It means only that the tested acquisition/model path preserved the defined observations and relations to the measured degree.

The most important shared-endpoint check is not whether MACLE guesses PERSON-B or PERSON-C correctly. It is whether MACLE preserves:
- one platform participant and endpoint;
- two distinct human ground-truth actors;
- speech/media observations that may support speaker hypotheses;
- uncertainty where the capture path cannot distinguish the two people;
- the evidence and limits behind any proposed attribution.

## 9. What this fixture does not decide

This fixture does not select Jitsi, LiveKit, BigBlueButton, a production platform, a capture provider, a retention policy, a legal basis, a canonical serialization, or a metric threshold. It is a proposed reproducibility artifact to validate and revise before implementation.
