# Fixture — Ground-truth annotation dry run 01

**Status:** PROPOSED worked dry run using a simulated timeline; no real meeting or media recording was produced.  
**Related fixture:** REFERENCE-MEETING-01.md.  
**Purpose:** test whether the annotation fields and adjudication procedure can preserve identity ambiguity, shared endpoints, device changes, time uncertainty, and disagreements without silently overwriting evidence.

## 1. What this dry run is and is not

This is a desk-based exercise using a fictional event log and fictional actors. It tests the annotation procedure and record shape. It does not test capture software, diarization accuracy, annotator performance on real media, or legal compliance for a real deployment.

The identifiers and times are synthetic. The example is not a canonical serialization or a schema decision.

## 2. Synthetic run context

- Run ID: DRY-RUN-01
- Meeting occurrence: MEETING-DRY-01
- Platform participant for shared endpoint: PARTICIPANT-BC
- Shared endpoint: ENDPOINT-BC
- PERSON-B and PERSON-C are two distinct test actors behind ENDPOINT-BC.
- PERSON-D uses ENDPOINT-D1, then leaves and joins through ENDPOINT-D2.
- Platform account label for PERSON-D: ACCOUNT-D.
- Platform may expose one participant identity across both sessions or create a new participant object; this example does not assume either behavior.
- Timeline is relative to a test-run monotonic clock. An illustrative wall-clock mapping is recorded separately.

## 3. Scripted ground-truth facts

| Fact ID | Valid start | Valid end | Actor | Platform identity | Endpoint | Ground-truth action |
|---|---:|---:|---|---|---|---|
| GT-001 | 00:00.000 | 00:00.000 | PERSON-B and PERSON-C | PARTICIPANT-BC | ENDPOINT-BC | Two people join together through one shared endpoint |
| GT-002 | 00:20.000 | 00:28.000 | PERSON-B | PARTICIPANT-BC | ENDPOINT-BC | PERSON-B speaks alone |
| GT-003 | 00:31.000 | 00:37.000 | PERSON-C | PARTICIPANT-BC | ENDPOINT-BC | PERSON-C speaks alone |
| GT-004 | 00:40.000 | 00:45.000 | PERSON-B and PERSON-C | PARTICIPANT-BC | ENDPOINT-BC | Both speak simultaneously |
| GT-005 | 01:00.000 | 01:00.000 | PERSON-D | ACCOUNT-D / platform session as observed | ENDPOINT-D1 | PERSON-D leaves from phone |
| GT-006 | 01:16.000 | 01:16.000 | PERSON-D | ACCOUNT-D / platform session as observed | ENDPOINT-D2 | PERSON-D rejoins from laptop |
| GT-007 | 01:40.000 | 01:40.000 | PERSON-B | PARTICIPANT-BC | ENDPOINT-BC | PERSON-B raises hand |

The operator's scripted action log is the ground-truth evidence for who was instructed to perform each action. A platform event alone only supports attribution to the platform participant/session it reports.

## 4. Independent annotation passes

Two annotators independently receive the same synthetic source package:
- operator action log;
- platform event log;
- time synchronization note;
- a mock media description that identifies B and C for the isolated utterances but does not visually disambiguate the hand-raise action.

They do not see each other's annotations before submitting their first pass.

### Annotator A

| Annotation ID | Source fact | Actor label | Platform participant | Endpoint | Time | Status |
|---|---|---|---|---|---|---|
| A-001 | GT-002 | PERSON-B | PARTICIPANT-BC | ENDPOINT-BC | [00:20.000, 00:28.000] ± 50 ms | reviewed |
| A-002 | GT-003 | PERSON-C | PARTICIPANT-BC | ENDPOINT-BC | [00:31.000, 00:37.000] ± 50 ms | reviewed |
| A-003 | GT-004 | PERSON-B and PERSON-C | PARTICIPANT-BC | ENDPOINT-BC | [00:40.000, 00:45.000] ± 50 ms | reviewed |
| A-004 | GT-007 | PERSON-B | PARTICIPANT-BC | ENDPOINT-BC | point at 01:40.000 ± 100 ms | reviewed |

### Annotator B

| Annotation ID | Source fact | Actor label | Platform participant | Endpoint | Time | Status |
|---|---|---|---|---|---|---|
| B-001 | GT-002 | PERSON-B | PARTICIPANT-BC | ENDPOINT-BC | [00:20.030, 00:28.040] ± 80 ms | reviewed |
| B-002 | GT-003 | PERSON-C | PARTICIPANT-BC | ENDPOINT-BC | [00:31.020, 00:37.030] ± 80 ms | reviewed |
| B-003 | GT-004 | PERSON-B and PERSON-C | PARTICIPANT-BC | ENDPOINT-BC | [00:40.020, 00:45.010] ± 80 ms | reviewed |
| B-004 | GT-007 | PERSON-C | PARTICIPANT-BC | ENDPOINT-BC | point at 01:40.090 ± 120 ms | disputed |

## 5. Disagreement and adjudication

A-004 and B-004 disagree about the person who raised the hand. Both agree on:
- platform participant: PARTICIPANT-BC;
- endpoint: ENDPOINT-BC;
- approximate event time;
- event type: hand raise.

The mock media description does not distinguish which co-located person performed the action. The operator's scripted action log says PERSON-B was instructed to raise the hand.

Adjudicated record:

| Field | Value |
|---|---|
| Adjudication ID | ADJ-001 |
| Supersedes neither original annotation | Both A-004 and B-004 remain preserved |
| Adjudicated actor | PERSON-B |
| Platform participant | PARTICIPANT-BC |
| Endpoint | ENDPOINT-BC |
| Valid time | point at 01:40.000, uncertainty ± 120 ms |
| Evidence | operator action log entry GT-007 |
| Rationale | controlled script identifies PERSON-B as the actor; the platform event alone does not |
| Status | adjudicated for this synthetic fixture |
| Reviewers | ANNOTATOR-A and ANNOTATOR-B |
| Caveat | without the operator action log, actor attribution would remain unknown |

The adjudicated record is not a reason to rewrite either annotator's original claim. It is a separate assertion linked to both annotations and the supporting action log.

## 6. Device-change example

The platform event log may show:
- participant/session departure at 01:00;
- new participant/session join at 01:16;
- account label ACCOUNT-D on both sides, if the platform exposes it.

The ground-truth log says one human, PERSON-D, changed from ENDPOINT-D1 to ENDPOINT-D2. The MACLE observation should preserve the platform evidence and the human ground-truth association separately.

Do not conclude that the same platform participant ID persisted unless the source actually reports that. Do not conclude that the same human is present from an account identifier alone.

## 7. Temporal and provenance example

For GT-002, a future annotation record could carry:
- run and annotation identifiers;
- valid interval and uncertainty;
- annotator clock ID;
- source/operator log reference;
- platform participant and endpoint labels;
- derivation type HUMAN_ANNOTATED;
- annotation status reviewed;
- recorded/ingestion time distinct from valid time.

For A-004/B-004/ADJ-001, it must additionally carry:
- the original annotation IDs;
- disagreement/adjudication relation;
- adjudicator identity or role;
- reason and supporting evidence;
- revision/system time.

This is a conceptual field inventory, not a JSON/YAML schema decision.

## 8. Findings from the dry run

The procedure can express the important distinctions, provided it retains separate records for independent annotations and adjudication.

Issues to address before a real annotation trial:
1. Define the exact convention for point-event uncertainty and interval endpoint inclusivity.
2. Define whether annotator identity is a person, role, or pseudonymous evaluator identifier in stored records.
3. Define how evidence references are protected and later deleted if they contain personal data.
4. Define the minimum evidence required for adjudication; the operator script is authoritative for this controlled fixture but would not be an authoritative source in a real meeting.
5. Add explicit fields for annotator clock uncertainty and source-package version.
6. Define how an annotation can be corrected after adjudication without erasing the earlier adjudication.

## 9. What this dry run does not verify

- No live Jitsi/LiveKit/BigBlueButton run was performed.
- No audio/video was captured or processed.
- No real human annotators participated.
- No diarization or person-recognition algorithm was evaluated.
- No numeric scoring thresholds were set.
- No canonical serialization or annotation database was selected.

The next empirical step is to have two human annotators perform this protocol on an actual synthetic fixture recording once issue #5 has produced a reproducible capture environment.
