# MACLE Google Meet local connector

A single-device connector for Google Meet. It combines two explicitly separate inputs:

1. A user-initiated Chrome tab recorder for the visible Google Meet tab, recording the tab's rendered video and tab audio locally.
2. A local Python client for Google Meet REST API metadata and available post-meeting artifacts.

No companion device, meeting bot, hosted MACLE service, remote database, or third-party capture/transcription provider is used.

## Current capability boundary

The Chrome recorder captures the rendered tab as one composite video stream and the audio output of that tab. Recording chunks are written to the browser's local Origin Private File System before download, so the full meeting is not kept in extension memory. It does not expose individual participant media tracks. It can optionally mix this device's microphone into the recording, but only after explicit permission and a separate attestation that the source is synthetic test audio. The microphone is off by default and is not stored as a separate track. It cannot see content that is not rendered in the selected tab, and browser/OS behavior may constrain capture.

The Python client retrieves conference metadata, participants, participant sessions, recording/transcript/smart-note metadata, and structured transcript entries where Google makes them available. The general conference-list endpoint is organizer-scoped; a known conference record can be fetched directly if Google authorizes access.

This is a first working slice, not complete multimodal perception. In particular, it does not infer gestures, identify people in the rendered pixels, or guarantee complete event coverage.

## Synthetic-only validation boundary

The owner has approved local, synthetic-only testing. The extension therefore requires an explicit confirmation that the selected meeting is a synthetic test meeting before recording starts. This checkbox is an operator attestation, not an automated guarantee about the meeting's participants.

Do not use it to capture real meetings or real participant data until a separate authorization is explicitly granted.

## Chrome extension setup

1. Open Chrome and visit `chrome://extensions`.
2. Enable Developer mode.
3. Choose **Load unpacked** and select `connectors/google-meet/chrome-extension`.
4. Open a synthetic Google Meet test meeting in a Chrome tab.
5. Open the extension's settings page from Chrome's extension details and save the synthetic-only attestation.
6. Leave microphone capture off for the baseline test. If testing it, select the synthetic-input attestation, enable the microphone, and use **Authorize microphone**; the default is off.
7. Click the MACLE toolbar icon to start recording (the badge shows REC); click it again to stop. Chrome downloads a WebM recording and a JSON capture manifest.

The extension only starts on `https://meet.google.com/`. Capture is initiated by a visible toolbar click; a second click stops it. It also stops on tab navigation or closure. It records the tab's rendered output and tab audio. The local microphone is included only if explicitly enabled, authorized in Chrome, and separately attested as synthetic test audio. Never use a real person's voice under the current approval.

### Shared Rust/WASM contract runtime

The Chrome extension uses the same Rust contract validator as the Android native shell. Build the WebAssembly module before loading the extension:

```sh
sh scripts/build-wasm-core.sh
```

See [Chrome extension build instructions](chrome-extension/BUILD.md). The extension refuses to start a capture if the shared WASM runtime is missing. The generated `core-wasm/` files are build artifacts and are not committed.

The Chrome capture now emits a `macle.session-manifest/v1` manifest with separate source capability states and a SHA-256 digest for the WebM artifact. The recording and manifest are still downloaded as a pair, not yet as a single archive package.

## Python API/artifact client

From the repository root, the convenience installer creates a local virtual environment, installs the client, and prepares private configuration/data directories:

```sh
bash scripts/install-google-meet.sh
```

Manual installation is also possible:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[asr]'
```

Create a Google Cloud project, enable Google Meet REST API, configure OAuth consent for a Desktop app, add your account as a test user if the app is in Testing, and download the OAuth client JSON to:

```
~/.config/macle-meet/client_secret.json
```

Then:

```sh
macle-meet auth
macle-meet sync --synthetic-test-attested --days 30
```

To attach to the active conference from the same device, resolve its current meeting space using the meeting code. The connector uses the code for the lookup but removes `meetingCode` and `meetingUri` from the stored space snapshot, because Google says meeting codes should not be stored long term:

```sh
macle-meet sync --synthetic-test-attested --meeting-code abc-mnop-xyz
```

You can also pass a space resource directly with `--space spaces/RESOURCE_ID`. This calls `spaces.get`, reads `activeConference.conferenceRecord`, and then retrieves the conference and available participants/artifacts. It prints the stable `spaces/RESOURCE_ID` for later use with `--space`. It works only while that space has an active conference and Google authorizes access. Google advises against storing meeting codes long term; the connector redacts the code and meeting URI from its persisted space snapshot.

To retrieve a known past conference resource:

```sh
macle-meet sync --synthetic-test-attested --conference-record 'conferenceRecords/CONFERENCE_ID'
```

The local SQLite database is stored under `~/.local/share/macle-meet/`; the JSONL observation export is written to the current directory. The optional ASR model cache is stored under `~/.cache/macle-meet/models/`. OAuth credentials are stored under `~/.config/macle-meet/` with owner-only permissions; the directory is created with mode 0700 and the token with mode 0600.

## Watch participant state during a synthetic meeting

To collect a sampled timeline of participant and participant-device sessions while a synthetic meeting is active:

```sh
macle-meet watch --synthetic-test-attested --meeting-code abc-mnop-xyz --interval 15
```

The command polls the Meet REST API every 15 seconds by default, stores participant and participant-session resource revisions locally, and stops when Google reports that the conference has ended or when you press Ctrl+C. Use `--duration 3600` to set a maximum duration, or `--space spaces/RESOURCE_ID` if you already know the stable space resource. You can also use `--conference-record` for a known conference, but it cannot resolve an active meeting space by itself.

This is **sampled REST polling**, not a real-time Workspace Events subscription. A short-lived state transition can be missed between polls, and API visibility/quotas depend on the Google account and Workspace policy. The explicit `--synthetic-test-attested` flag is required for both sync and watch while the current project approval remains synthetic-only.

## Local speech transcription

The installer includes the optional `faster-whisper` backend. After capture, transcribe the local WebM file with:

```sh
macle-meet transcribe \\
  --media ./MACLE-Meet-....webm \\
  --manifest ./MACLE-Meet-....manifest.json \\
  --conference-record 'conferenceRecords/CONFERENCE_ID' \
  --language fr
```

Omit `--language` for automatic language detection. The default model is `small`, running locally on CPU with int8 quantization. Use `--model medium` for a larger model, or `--device cuda` only when the required CUDA runtime is correctly installed. The model weights are downloaded from Hugging Face the first time a model is used and cached locally; the WebM audio and generated transcript are not sent to Hugging Face or any hosted ASR service. `faster-whisper` decodes media through PyAV, so a system FFmpeg installation is not required.

The command first indexes the capture manifest and media hash, then stores each generated segment as a separate MACLE observation with capture ID, optional conference resource, media SHA-256, relative start/end offsets, text, model identifier, detected language and confidence metadata. It also samples one video frame every 30 seconds by default, saves JPEG artifacts under `~/.local/share/macle-meet/frames/`, and creates `video_frame` observations with their own hashes and capture-relative timestamps. Use `--frame-interval 0` to disable frame sampling or adjust the interval and maximum dimension with `--frame-interval` and `--max-frame-dimension`. These are **machine-generated local ASR observations**, not Google-generated transcript entries. No speaker identity or diarization is inferred from the composite tab recording. Frame samples are sparse references to the composite video, not continuous or participant-specific streams. No face recognition, identity inference, emotion inference or semantic interpretation is performed. ASR output is not a verified verbatim transcript.

### One-command post-capture workflow

Instead of running the separate indexing, transcription, REST sync and report commands, use:

```sh
macle-meet process-capture --synthetic-test-attested \\
  --media ./MACLE-Meet-....webm \\
  --manifest ./MACLE-Meet-....manifest.json \\
  --conference-record 'conferenceRecords/CONFERENCE_ID' \\
  --language fr
```

The conference resource is optional. When supplied, MACLE synchronizes available Meet REST metadata/artifacts using the local OAuth token. If that sync fails, the local capture, ASR and frame observations are retained and the report is still generated with a warning. Without a conference resource, the command processes only the local capture.

### Local HTML report

Generate a local HTML report for inspection:

```sh
macle-meet report --synthetic-test-attested \\
  macle-meet-observations.jsonl \\
  ./macle-meet-report.html
```

The report includes capture provenance, participant/session resources, timestamped ASR segments and verified local frame thumbnails. It writes a sibling `macle-meet-report_assets/` directory for copied frame images. The HTML uses inline CSS only, no remote scripts or fonts, escapes transcript/resource text, and verifies frame hashes before copying. The report and assets are local files; no upload occurs.

## Local-only data handling

- The Chrome extension downloads files to the user's normal browser download location.
- The Python client stores source payloads and normalized observations in local SQLite; its dedicated data directory is created with owner-only permissions and the database/JSONL files are chmod 0600 where supported.
- There is no remote MACLE server or third-party processor in this implementation.
- Protect WebM recordings, transcripts, database files, OAuth tokens and exports as sensitive data.
- The extension's manifest records capture start/end times, source tab origin/title and MIME type. It deliberately does not persist the full Meet URL or meeting code. The Python client also redacts Google Meet's short-lived `meetingCode` and `meetingUri` fields before storing a space snapshot.
- Delete local downloads/database/token files when no longer needed. This does not delete source artifacts in Google Drive.

## Validation

Run the Python unit tests:

```sh
pytest
```

The Chrome extension requires a manual smoke test in Chrome against a synthetic meeting. The local ASR test requires a short synthetic audio/video fixture; the first use downloads the selected model weights. No real meeting capture is part of the approved validation scope.


## Index a local capture

After downloading a capture, index it alongside the API observations:

```sh
macle-meet index-capture --manifest ./MACLE-Meet-....manifest.json --media ./MACLE-Meet-....webm
```

If you have the matching Google conference resource name, add `--conference-record 'conferenceRecords/…'` to associate the local capture with that conference. The command records the media file's SHA-256, size and local path; it does not copy the media bytes into SQLite or upload them.
