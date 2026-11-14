# Study — Temporal and revision semantics

**Status:** PROPOSED conceptual study, 14 November 2026. No timestamp encoding, temporal database, interval algebra, event store or revision strategy adopted.

## 1. Two different questions

MACLE must distinguish: (1) when an assertion says a phenomenon happened; and (2) when MACLE learned, recorded, revised or withdrew that assertion. A transcript correction recorded tomorrow may describe speech from yesterday. A webhook may arrive late. One timestamp cannot express these facts.

## 2. Candidate temporal dimensions

| Dimension | Meaning |
|---|---|
| Valid/event time | Time or interval in the modeled situation |
| Source assertion time | Time the source says it emitted or recorded the assertion |
| Observation time | Time the adapter observed the payload or media |
| Ingestion/record time | Time MACLE durably accepted the observation |
| Processing time | Time an extraction/transformation ran |
| Revision/system time | Time a correction, challenge, supersession or withdrawal entered the record |

Not every record has every value. Preserve original source timestamps and local receipt timestamps even if a normalized UTC value is also generated.

## 3. Bitemporal view, precision and uncertainty

Bitemporal systems distinguish valid time (when a fact applies in the modeled world) from transaction/system time (when the system recorded that version). This is relevant to “what did MACLE have evidence for as of T?”. MACLE may need additional source, observation, ingestion and processing times; bitemporality is a conceptual minimum, not a complete design.

A temporal value may need original lexical form, normalized form, clock identifier/domain, timezone/offset, precision, estimated offset/drift, uncertainty bounds, and point/interval/unknown-boundary kind. Do not fabricate precision. A whole-second source timestamp does not become microsecond-accurate by storing extra decimals. Point events must not silently become non-zero intervals.

## 4. Multiple clock domains

A meeting may combine platform server time, device wall clocks, media presentation timestamps, audio sample counters, observer wall/monotonic clocks, annotator clocks and artifact times. These clocks can drift, reset or use different epochs.

Candidate requirements:
- preserve raw source time and clock identity;
- record local receipt wall time and monotonic time where useful;
- record synchronization method and estimated offset/uncertainty in fixture runs;
- distinguish source sequence order from cross-source chronological order;
- avoid strict ordering when uncertainty intervals overlap;
- make alignment a derived, versioned activity with provenance.

## 5. Temporal relations

Allen's interval algebra (before, meets, overlaps, during, starts, finishes, equals) can support cross-modal questions. Uncertain boundaries may leave multiple relations possible. The model must permit unknown, ambiguous or a set of possible relations rather than forcing one answer. Retain whether a relation is direct (same source clock) or derived (cross-source alignment).

## 6. Revision and correction

Candidate assertion states include asserted, challenged, corrected, superseded, withdrawn and retracted. These are not a finalized enum and must not be conflated with source health, processing status or legal deletion.

A correction should identify earlier assertion(s), the new assertion, who/what made it, when and why, supporting evidence, valid-time interval, and whether it replaces or only qualifies the earlier assertion. Do not mutate a source payload to match a normalized interpretation.

## 7. Append-only history versus privacy

Append-only history can support auditability and as-of queries, but it is not automatically right or lawful for all meeting data:
- assertion history is not the same as retaining raw audio/video forever;
- immutable audit metadata is not necessarily exempt from deletion;
- a tombstone does not justify retaining personal data that should be erased;
- backups, caches, derivatives, exports and third-party copies need lifecycle handling;
- provenance must not become an indefinite shadow archive of deleted personal information.

A revisioned assertion ledger, mutable projections, bounded retention and deletion propagation are options to investigate, not adopted architecture.

## 8. Query patterns and candidate tests

Evaluate current preferred view, as-of system time, valid-time view, correction history, cross-modal overlap, uncertain ordering, provenance traversal, deletion impact and coverage-aware absence.

Candidate tests:
- late platform events retain event time and later observation/ingestion time;
- uncertain speech boundaries do not become falsely precise;
- supported overlapping speech remains overlapping;
- cross-clock ordering remains ambiguous when uncertainty prevents a conclusion;
- corrected transcript is queryable as currently preferred and as originally recorded;
- challenged attribution remains visible as challenged;
- deleted artifacts are not retrievable through ungoverned derived references;
- capture outage is a coverage gap, not a silent interval.

## Sources checked 14 November 2026

- James F. Allen, “Maintaining Knowledge about Temporal Intervals”, CACM 26(11), 832–843 (1983): https://doi.org/10.1145/182.358434
- W3C PROV-DM: https://www.w3.org/TR/prov-dm/
- W3C PROV-O: https://www.w3.org/TR/prov-o/
- PostgreSQL date/time types (implementation example only): https://www.postgresql.org/docs/current/datatype-datetime.html
- Martin Fowler, “Bitemporal History”: https://martinfowler.com/articles/bitemporal-history.html

No timestamp encoding, synchronization protocol, interval algebra, database, event store, append-only policy, retention rule or deletion mechanism is adopted.
