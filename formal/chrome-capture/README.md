# Formal assurance: Chrome capture lifecycle

## Purpose

This model specifies the abstract lifecycle of a user-authorized, local-only
Chrome tab capture. It is intended to find ordering, race, and failure-handling
defects before relying on browser integration tests.

It is not a proof of Chrome's implementation, Google Meet behavior, media
codec correctness, file-system durability, or JavaScript refinement.

## Model files

- `CaptureLifecycle.tla`: finite-state capture lifecycle transition system.
- `CaptureLifecycle.cfg`: lifecycle invariants and stop-liveness property.
- `ExportRecovery.tla`: integrity-gated recovery of a retained recording after partial export.
- `ExportRecovery.cfg`: recovery safety invariants checked by TLC.

## Claims specified for TLC checking

| Claim | Formal predicate |
|---|---|
| Capture cannot start without explicit authorization | `AuthorizationSafety` |
| A recording requires a ready Offscreen document | `RecorderRequiresReadyOffscreen` |
| A recording consumes one fresh stream identifier exactly once | `RecorderRequiresConsumedStream`; `StreamConsumedAtMostOnce` |
| A setup failure after stream issuance still consumes no more than one identifier and ends in failure | `StartRecorderFailure`; `StreamConsumedAtMostOnce` |
| A session is not called Saved until both artifacts are finalized and both downloads complete | `SavedMeansBothDownloadsComplete` |
| A download cannot begin before its artifact is finalized | `DownloadRequiresFinalizedArtifact` |
| A retry cannot start until the retained artifact passes its SHA-256 check | `DownloadRequiresVerifiedArtifact`; `ExportingRequiresVerifiedHash` |
| A hash mismatch blocks recovery without deleting the retained artifact | `BlockedMeansNoFalseSuccess`; `MetadataRequiresRetainedArtifact` |
| Recovery is successful only after both exports are complete, then the local recovery record and artifact may be removed | `RecoveredMeansTruthfulSuccess`; `OnlyRecoveryRemovesArtifact`; `OnlyRecoveryRemovesMetadata` |
| If both exports were already complete before a cleanup crash, recovery removes stale local metadata without re-exporting or re-hashing the artifact | `CleanupAlreadyExported` |
| Browser restart during recovery forces re-verification and converts in-progress exports to retryable interruptions | `BrowserRestart` |
| A new capture cannot start while a retained export is pending | `PendingRecoveryBlocksNewCapture` |
| The recording phase ends when its source tab closes, and the recorder then eventually stops | `NoRecordingAfterTabClosure`; `TabClosureEventuallyStopsRecorder` |
| A terminal session has no active recorder | `TerminalRecorderQuiescent` |
| A stop request eventually reaches Saved or Failed under the stated fairness assumptions | `StopEventuallyTerminates` |
| A recorder active at tab closure eventually becomes quiescent under recorder-stop fairness | `TabClosureEventuallyStopsRecorder` |

## Important semantic correction

The current Chrome implementation's `chrome.downloads.download()` callback
returns a download identifier when Chrome accepts the request. Acceptance is
not the same as completion. The implementation must query the download item (or observe
`chrome.downloads.onChanged`) and distinguish `in_progress`, `complete`,
and `interrupted` before it can truthfully report that the files were saved.

The model therefore treats successful download completion—not merely obtaining
a download ID—as the terminal success condition.

## Assumptions and abstraction boundary

1. User authorization is represented by one Boolean. UI correctness and the
   provenance of the user's gesture are outside this model.
2. The initial Offscreen state is nondeterministically absent, loading, or
   already ready, covering both new and pre-existing documents. The browser
   supplies a fresh stream identifier only after readiness. Its real expiry
   window and API errors are tested at the adapter boundary.
3. The Offscreen recorder and browser download manager are abstract actors.
   Their internal implementations are not proven by this state machine.
4. The model has one tab, one capture session, and one media artifact plus one
   manifest. Multi-tab concurrency and multiple sessions are out of scope.
5. `StopEventuallyTerminates` assumes weak fairness for recorder stop,
   finalization, and download progress. It does not claim progress if Chrome,
   the operating system, or the user indefinitely prevents those operations.
6. Browser restart is modeled as a failure of an in-flight session, not as
   successful recovery of a partial recording.
7. In `ExportRecovery.tla`, the hash-valid flag abstracts the immutable Blob
   snapshot obtained from OPFS. The implementation hashes that Blob stream and
   passes the same Blob object to Chrome for download; it does not re-open a
   potentially different file between verification and export.
8. Browser restart during export recovery returns the state to Pending,
   invalidates the previous hash-verification witness, and records in-progress
   downloads as interrupted; the OPFS artifact and recovery metadata remain.
9. If both downloads were already complete before a cleanup crash, recovery
   may remove stale metadata and the retained file without re-hashing it: no
   further export is performed in that path.
10. Export recovery is safety-checked only. The model deliberately makes no
   liveness claim because a user can repeatedly cancel or interrupt downloads.

## Verification status

The specification and TLC configuration are committed, but TLC has **not yet
been executed** in the authoring environment. Do not call the model checked
until the local command completes successfully and its state count is recorded.

Run:

```bash
bash scripts/check-chrome-capture-formal.sh
```

The script bootstraps the official stable TLC 1.7.4 command-line JAR into the user's
local cache, checks the SHA-1 published by the official release and a
cross-pinned SHA-256 published for the same 1.7.4 JAR by the
[SourceForge mirror](https://sourceforge.net/projects/tlaplus.mirror/files/v1.7.4/tla2tools.jar/),
and runs both models with one worker on Java 11+. The one-worker setting is intentional: the 1.7.4 release
notes document a liveness-checking unsoundness with multiple workers. Version
1.8.0 is currently marked pre-release on the official
[TLA+ releases page](https://github.com/tlaplus/tlaplus/releases), so the
script pins the latest stable release rather than a pre-release.
No GitHub Actions workflow is required. Record the TLC version, Java version,
exact command, explored state count, and result after execution.

Do not describe bounded exploration as an unbounded theorem. TLC exhaustively
checks the finite state space of this abstraction; it does not prove that the
JavaScript implementation refines the model.

## Current implementation changes

The implementation branch corresponding to this model now:
- performs the Offscreen PING handshake even when the document already exists;
- waits for the shared WebAssembly core to initialize before declaring readiness;
- serializes concurrent start attempts with a service-worker operation guard
  and an Offscreen lock set before the first asynchronous yield;
- aborts and removes a partial OPFS artifact if MediaRecorder setup fails;
- retains the active-capture marker when STOP_CAPTURE cannot be acknowledged,
  so a later toolbar click retries stopping instead of starting a second recorder;
- accepts CAPTURE_SAVED and CAPTURE_ERROR state transitions only from the
  Offscreen document, preventing another extension page from spoofing recorder completion;
- queries Chrome's download manager until each file reaches `complete` or
  `interrupted`, rather than treating a returned download ID as saved;
- persists a recovery record before manifest validation or export, retains a
  finalized OPFS artifact if validation or either export fails, and exposes a
  settings-page retry that verifies SHA-256 before
  re-exporting only the missing files. Recovery recomputes SHA-256 incrementally
  from the retained file stream, avoiding a second full-recording memory copy.
  If both downloads completed before a crash, cleanup is idempotent and does
  not download either artifact again.

JavaScript syntax, manifest JSON, and static assertions have been checked. A
small set of targeted Offscreen/service-worker scenarios has also been exercised
manually in isolated mocks; this is not the same as running the committed Node
test suite. The suite currently contains thirteen regression cases. Run
`bash scripts/check-chrome-extension-static.sh` in a local checkout to execute
the full suite and reproduce the static checks. TLC and real Chromium/Meet
capture tests have not yet passed because they have not yet been run.

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
