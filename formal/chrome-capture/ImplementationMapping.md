# Implementation-to-model mapping

This mapping is deliberately explicit: a model predicate is only useful when
there is a corresponding implementation mechanism and an executable test.

| Model concern | Current implementation mechanism | Required adapter evidence |
|---|---|---|
| Offscreen readiness | `ensureOffscreenDocument` always performs PING; Offscreen PING waits for `macleCoreReady` | Existing and newly-created Offscreen contexts both answer PONG only after WASM initialization |
| Fresh stream consumption | `getMediaStreamId` is called only after readiness and immediately before START_CAPTURE | Synthetic capture proves one stream ID is consumed once; delayed/stale IDs fail closed |
| Single startup | Service-worker operation guard plus synchronous Offscreen `starting` lock | Two simultaneous START_CAPTURE messages yield exactly one recorder |
| Stop/finalize ordering | STOP_CAPTURE -> MediaRecorder stop -> serialized chunk writes -> close OPFS file | Stop during recording drains all queued writes before file close |
| Artifact integrity | Incremental SHA-256 while chunks are written; manifest validation via shared core | Recompute SHA-256 from exported WebM and compare with manifest |
| Download completion | Service worker exposes `DOWNLOAD_STATUS`; Offscreen waits for Chrome state `complete` | Completed state produces CAPTURE_SAVED; interrupted/cancelled/timed-out state produces CAPTURE_ERROR |
| Resource release | `saveCapture` finally stops tab/microphone tracks and closes AudioContext; `startCapture` setup failure aborts the partial writable and removes its temporary OPFS entry | C-11 and C-21 verify cleanup after normal finalization and MediaRecorder construction failure |
| Stop acknowledgement failure | Service worker keeps `captureActive` and `capturedTabId` when STOP_CAPTURE fails; only `captureStopping` is reset | C-22 verifies a later toolbar click retries stop and cannot issue a new stream ID |
| Interrupted export recovery | Persist `pendingExport` metadata in extension storage; retain finalized OPFS artifact; settings page retries only incomplete downloads after SHA-256 verification | Cancel media or manifest export, reopen settings, retry; verify integrity check and no false `CAPTURE_SAVED` |
| Pending-recovery capture gate | Service worker checks `pendingExport` before creating a stream ID and opens settings instead | C-16 proves no new stream ID or Offscreen start is requested while recovery is pending; `PendingRecoveryBlocksNewCapture` specifies the state invariant |

## Known refinement gaps

- The TLA+ model is an abstract lifecycle contract, not a mechanically checked
  refinement proof from JavaScript to TLA+.
- The model's single-session abstraction does not yet model simultaneous tabs.
- The download completion poll is bounded to 30 minutes. Timeout is a failure,
  not success.
- The current extension still requires a real Chromium synthetic-media test to
  establish the browser API adapter behavior.
- A browser crash can leave an incomplete temporary OPFS file; crash recovery
  and orphan cleanup are separate work.
- The model does not prove audio/video codec interoperability or that Meet
  exposes a usable tab audio track in every environment.
