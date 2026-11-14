# Google Meet single-device prototype — manual smoke test

**Status:** prepared; not yet executed.  
**Approved data boundary:** synthetic test identities/content, one local computer, no third-party egress.  
**Implementation:** [local connector guide](../../connectors/google-meet/README.md).

This runbook validates the first Google Meet integration without using real meeting content or a second device. It is a manual browser/API test, not an automated CI test.

## 1. Preconditions

- Chrome 116 or newer.
- Python 3.11 or newer.
- A Google Cloud project with Google Meet REST API enabled.
- A Desktop OAuth client JSON configured for the Google account used in the synthetic test.
- A Google Meet test space and meeting containing only synthetic identities and synthetic content.
- If testing the optional microphone path, a virtual microphone whose input is generated synthetic audio. Do not use a physical microphone carrying a real person's voice under the current approval.

## 2. Install the Python client

From the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev,asr]'
pytest -q
macle-meet --version
```

Expected:
- Unit tests pass.
- CLI prints version `0.1.0`.

## 3. Configure Google OAuth

1. Enable Google Meet REST API in the selected Google Cloud project.
2. Configure the OAuth consent screen; add the test account as a test user if the app is in Testing.
3. Create and download a Desktop OAuth client JSON.
4. Save it as `~/.config/macle-meet/client_secret.json` and restrict it to your user (`chmod 600 ~/.config/macle-meet/client_secret.json`).
5. Run:

```sh
macle-meet auth
```

Expected:
- Browser opens Google's consent page.
- User authorizes the read-only Meet scope.
- Local token is stored at `~/.config/macle-meet/token.json` with mode 0600.
- No token or client secret is committed to the repository.

## 4. Install the Chrome extension

1. Open `chrome://extensions`.
2. Enable Developer mode.
3. Select **Load unpacked** and choose `connectors/google-meet/chrome-extension`.
4. Open the extension's options page.
5. Check the synthetic-only attestation.
6. Leave microphone capture disabled for the baseline test.
7. Save settings.

Expected:
- Extension loads without manifest errors.
- Toolbar icon is present.
- Capture does not start unless the synthetic-only attestation is saved.

## 5. Test active conference lookup

1. Open the synthetic Google Meet meeting in the same Chrome profile.
2. Copy the meeting code from its URL.
3. Run:

```sh
macle-meet sync --synthetic-test-attested --meeting-code abc-mnop-xyz
```

Replace the example with the actual synthetic test meeting code.

Expected:
- The client calls `spaces.get` using the meeting-code alias.
- It resolves `activeConference.conferenceRecord` and prints the stable space resource name.
- It fetches the conference record, participants and participant sessions.
- The persisted space snapshot omits `meetingCode` and `meetingUri`.
- It fetches any available recording/transcript/smart-note metadata and transcript entries.
- It prints the conference resource name, which can be used for a later post-meeting sync.
- The local SQLite database and JSONL export are created.
- No data is sent to a MACLE server or a third-party provider.

If there is no active conference, the command should explain that a known past `conferenceRecords/…` resource is required.

## 5b. Watch participant sessions during the synthetic meeting

In a second terminal, start the local participant-state poller:

```sh
macle-meet watch --synthetic-test-attested --meeting-code abc-mnop-xyz --interval 15 --duration 600
```

Expected:
- The command resolves the same active conference record.
- It polls participants and participant-device sessions every 15 seconds.
- New or changed source resource revisions are added to SQLite/JSONL; unchanged resources are not duplicated.
- It stops when the conference ends, the duration elapses, or Ctrl+C is pressed.
- The resulting records preserve participant and participant-session resource identities and source times.
- This is sampled polling, not guaranteed real-time event delivery.

## 6. Test local tab capture

1. Keep the synthetic Meet tab active.
2. Click the MACLE toolbar icon.
3. Confirm that the badge displays `REC`.
4. Confirm that Meet tab audio continues to play through the normal output device.
5. Allow a short synthetic test segment to play.
6. Click the toolbar icon again to stop.

Expected:
- Chrome downloads one `.webm` file and one `.manifest.json` file.
- The manifest identifies the capture mode as `single_device_visible_tab`.
- It records start/end times, tab origin/title, MIME type, audio source, microphone state and synthetic attestation.
- The video is a composite of the rendered tab, not individual participant tracks.
- Capture stops if the tab navigates or closes.

## 7. Optional synthetic microphone path

Only run this section with a virtual microphone fed by generated synthetic audio.

1. Open extension settings.
2. Check the synthetic microphone-input attestation.
3. Check **Include this device's microphone**.
4. Select **Authorize microphone** and grant Chrome permission.
5. Save settings.
6. Repeat the short capture test.

Expected:
- The manifest reports `microphoneCaptured=true` and `microphoneSyntheticAttested=true`.
- The microphone is mixed with tab audio; it is not stored as a separate track.
- A manifest without the synthetic microphone attestation is rejected by `index-capture`.

Do not use a real person's voice or physical microphone under the current Stage A approval.

## 8. Index the local capture

Use the conference resource name printed in step 5:

```sh
macle-meet index-capture \
  --manifest ./MACLE-Meet-....manifest.json \
  --media ./MACLE-Meet-....webm \
  --conference-record 'conferenceRecords/CONFERENCE_ID'
```

Expected:
- The local media file is hashed with SHA-256.
- The JSONL observation includes the capture manifest, file path, file size and hash.
- The media bytes are not copied into SQLite or uploaded.
- The capture observation is associated with the supplied conference resource.

## 8b. Local speech transcription

Run local ASR on the captured WebM:

```sh
macle-meet transcribe \\
  --media ./MACLE-Meet-....webm \\
  --manifest ./MACLE-Meet-....manifest.json \\
  --conference-record 'conferenceRecords/CONFERENCE_ID' \
  --language fr
```

Expected:
- The first run downloads the selected Whisper model weights to the local cache.
- Audio is decoded and transcribed locally; only model weights are downloaded, never the recording.
- The command indexes the capture and outputs timestamped speech-segment observations with capture, optional conference and model provenance.
- No participant identity or speaker attribution is fabricated.
- The machine-generated transcript is distinct from any Google-generated transcript artifact.

## 9. Post-meeting artifact sync

After the synthetic meeting ends and Google has generated any configured artifacts, run:

```sh
macle-meet sync --synthetic-test-attested --conference-record 'conferenceRecords/CONFERENCE_ID'
```

Expected:
- Available transcript entries and artifact metadata are added to the local store.
- Missing/not-yet-generated artifacts do not imply an empty meeting.
- The REST API's 30-day conference/transcript-entry expiry window is respected; sync promptly.

## 10. Negative checks

- With synthetic-only attestation disabled, toolbar click must open settings and must not start capture.
- With microphone enabled but synthetic-microphone attestation absent, settings must refuse to save that configuration.
- A microphone capture manifest without synthetic microphone attestation must be rejected by `index-capture`.
- A non-Meet tab must not start capture.
- Tab navigation or closure must stop capture.
- A conference resource inaccessible to the OAuth principal must produce an API error, not a fabricated empty result.
- No external provider, cloud upload, real participant or real voice is used.

## 11. Record the test result

When executed, append:
- Date/time and operator.
- OS and Chrome versions.
- Python version.
- Google Workspace account type and relevant test policy settings (no account identifiers or tokens).
- Extension load result.
- OAuth result.
- Active conference lookup result.
- Capture start/stop and playback result.
- Manifest fields and file hash.
- Python test/CI status.
- Deviations, errors, and unresolved limitations.

Until this runbook is executed in Chrome with a configured Google test account, the prototype is **implemented but not operationally verified**.
