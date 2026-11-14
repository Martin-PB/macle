# Formal assurance: Chrome capture lifecycle

## Purpose

This model specifies the abstract lifecycle of a user-authorized, local-only
Chrome tab capture. It is intended to find ordering, race, and failure-handling
defects before relying on browser integration tests.

It is not a proof of Chrome's implementation, Google Meet behavior, media
codec correctness, file-system durability, or JavaScript refinement.

## Model files

- `CaptureLifecycle.tla`: finite-state transition system.
- `CaptureLifecycle.cfg`: TLC invariants and temporal property.

## Claims checked by the model

| Claim | Formal predicate |
|---|---|
| Capture cannot start without explicit authorization | `AuthorizationSafety` |
| A recording requires a ready Offscreen document | `RecorderRequiresReadyOffscreen` |
| A recording consumes one fresh stream identifier exactly once | `RecorderRequiresConsumedStream` |
| A session is not called Saved until both artifacts are finalized and both downloads complete | `SavedMeansBothDownloadsComplete` |
| A download cannot begin before its artifact is finalized | `DownloadRequiresFinalizedArtifact` |
| A stop request eventually reaches Saved or Failed under the stated fairness assumptions | `StopEventuallyTerminates` |

## Important semantic correction

The current Chrome implementation's `chrome.downloads.download()` callback
returns a download identifier when Chrome accepts the request. Acceptance is
not the same as completion. The implementation must observe
`chrome.downloads.onChanged` and distinguish `in_progress`, `complete`,
and `interrupted` before it can truthfully report that the files were saved.

The model therefore treats successful download completion—not merely obtaining
a download ID—as the terminal success condition.

## Assumptions and abstraction boundary

1. User authorization is represented by one Boolean. UI correctness and the
   provenance of the user's gesture are outside this model.
2. The browser supplies a fresh stream identifier after Offscreen readiness.
   Its real expiry window and API errors are tested at the adapter boundary.
3. The Offscreen recorder and browser download manager are abstract actors.
   Their internal implementations are not proven by this state machine.
4. The model has one tab, one capture session, and one media artifact plus one
   manifest. Multi-tab concurrency and multiple sessions are out of scope.
5. `StopEventuallyTerminates` assumes weak fairness for recorder stop,
   finalization, and download progress. It does not claim progress if Chrome,
   the operating system, or the user indefinitely prevents those operations.
6. Browser restart is modeled as a failure of an in-flight session, not as
   successful recovery of a partial recording.

## Verification status

A model is not evidence until a named model checker has actually run it.
Record the TLC version, Java version, exact command, explored state count,
and result here when verification is executed. Do not describe bounded
exploration as an unbounded theorem.

## Refinement plan

1. Extract the state machine into a small implementation-facing controller.
2. Add deterministic tests that map each implementation event to a model
   transition.
3. Add adversarial event-sequence tests for concurrent start, navigation
   during startup, stop during startup, worker suspension, recorder errors,
   and interrupted downloads.
4. Run Chromium extension integration tests with synthetic media.
5. Keep a separate manual Google Meet smoke test for real browser/audio
   behavior, because a model and synthetic tests cannot establish that
   Meet's actual tab audio/video is exposed as expected.
