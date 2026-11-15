# Chrome capture adapter test plan

These tests validate the boundary between the abstract lifecycle model and
real Chromium APIs. They are separate from TLC model checking.

## Deterministic synthetic cases

| ID | Setup / event sequence | Expected observation |
|---|---|---|
| C-01 | No Offscreen document; click capture | Create document, wait for PONG with coreReady, then request stream ID |
| C-02 | Existing Offscreen document still initializing | No early return; PING retries until coreReady |
| C-03 | WASM import rejects | No stream ID requested; toolbar reports ERR |
| C-04 | Two START_CAPTURE messages arrive concurrently | Exactly one start passes the synchronous Offscreen lock |
| C-05 | Stream ID is stale/expired | getUserMedia fails closed; all acquired resources are released |
| C-06 | Stop while recording | Recorder stops; queued chunk writes drain; OPFS writable closes before export |
| C-07 | Media download completes; manifest download completes | CAPTURE_SAVED is sent only after both states are complete |
| C-08 | Either download is interrupted or cancelled | CAPTURE_ERROR is sent; CAPTURE_SAVED is never sent |
| C-09 | Download remains in progress for 30 minutes | Timeout is reported as failure, never success |
| C-10 | Tab navigates or closes while recording | Stop/finalization path is invoked |
| C-11 | Optional microphone enabled | Microphone tracks are stopped on success and failure |
| C-12 | Tab audio monitoring disabled | Captured tab audio remains in recording mix but is not routed to local speakers |
| C-13 | Cancel or interrupt the media download after finalization | OPFS artifact and pending-export metadata remain; no CAPTURE_SAVED; settings exposes retry |
| C-14 | Media download completes but manifest download is interrupted | Recovery skips the completed media download and retries only the manifest |
| C-15 | Modify/corrupt the retained OPFS artifact before retry | SHA-256 mismatch blocks export recovery and never reports success |
| C-16 | Click the toolbar while a pending export exists | No new stream ID is requested; settings opens directly on the recovery control |
| C-17 | Retry export of a large retained recording | SHA-256 is recomputed incrementally from the Blob stream, without reading the whole recording into one ArrayBuffer |
| C-18 | Shared manifest validation rejects an otherwise finalized artifact | The OPFS file and pending-export pointer are retained; no CAPTURE_SAVED is emitted |
| C-19 | Browser restarts while a pending export is being retried | Recovery metadata and OPFS file survive; next retry recomputes SHA-256 and resumes only incomplete downloads |
| C-20 | Both downloads completed but the browser stopped before clearing recovery metadata | Retry performs cleanup without downloading either file again; it may tolerate an already-removed OPFS file |
| C-21 | MediaRecorder construction fails after the OPFS file and writable handle are created | Partial file is removed, writable handle is aborted, and acquired media tracks are stopped; error is not masked by cleanup |
| C-22 | STOP_CAPTURE acknowledgement fails or Offscreen is temporarily unavailable | Service worker retains captureActive and capturedTabId, clears only captureStopping, and a later toolbar click retries stop instead of starting a second recorder |
| C-23 | Source tab navigates or closes while MediaRecorder is active | Capture leaves the Recording phase immediately; the recorder reaches Stopped before media finalization begins; source tracks are released during final cleanup |

## Required real-browser acceptance test

Use a dedicated synthetic Google Meet session and a controlled audio/video
source. Record the browser version, OS, selected tab, track counts, WebM
duration, WebM readability, manifest schema validation, and SHA-256 recompute.

Acceptance requires:
- video is present and decodable;
- tab audio is present when Chrome exposes a tab audio track;
- local monitoring remains disabled by default;
- the manifest accurately reports unavailable sources;
- both downloads reach Chrome state `complete`;
- no media track remains live after finalization.

A passing static test or TLC run does not replace this acceptance test.
