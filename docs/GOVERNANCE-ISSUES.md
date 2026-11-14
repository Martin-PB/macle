# MACLE — Issue taxonomy and decomposition proposal

**Status:** PROPOSED workflow guidance; not adopted. This document does not create labels or change repository settings.

## Proposed labels

Work type:
- kind:question — evidence or arbitration required
- kind:study — research/comparison
- kind:decision — explicit decision preparation/review
- kind:model — conceptual/formal model
- kind:fixture — reproducible scenario/ground truth
- kind:implementation — executable code/integration
- kind:verification — test, model check, proof or empirical validation
- kind:documentation — docs and repository governance

State/gate:
- state:proposed
- state:blocked
- state:ready
- state:verified
- state:accepted

Domain:
- area:privacy
- area:identity
- area:temporal
- area:capture
- area:platforms
- area:provenance
- area:consumer-interface

Labels classify work; they do not replace issue state or an explicit decision record.

## Issue decomposition

Create a separate issue when a work item has a distinct deliverable, dependency, acceptance criterion or decision authority. Every actionable issue should state problem/why now, scope/non-goals, deliverable, evidence required, observable acceptance criteria, dependencies, decision authority, and what completion must not imply.

## Closure rules

- A draft document alone does not close an issue unless that is the stated deliverable.
- A study can be complete while its decision remains open.
- A decision issue closes only after the explicit decision is recorded in an ADR and its status updated.
- An implementation issue closes only after code is merged and stated verification evidence is available.
- “Verified” names environment, version, date and test evidence.
- Opening or merging a PR does not by itself make a proposal accepted.

## Suggested decomposition

1. Privacy/data-egress gate.
2. Temporal/revision semantics.
3. Jitsi and LiveKit reference-environment spike with synthetic participants.
4. Fixture ground-truth dry run and adjudication.
5. Source traceability audit for volatile API/SDK claims.
6. Issue taxonomy and label creation after project-owner approval.

No labels are created and no mandatory policy is adopted by this proposal.
