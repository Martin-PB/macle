let recorder = null;
let stream = null;
let microphoneStream = null;
let recorderStream = null;
let audioContext = null;
let fileHandle = null;
let writable = null;
let temporaryFileName = null;
let writeChain = Promise.resolve();
let sessionManifest = null;
let artifactHasher = null;
let saving = false;
let captureFailure = null;
const macleCoreReady = import(chrome.runtime.getURL("core-wasm/macle_core.js")).then(async (core) => {
  await core.default();
  return core;
});

function send(type, details = {}) {
  chrome.runtime.sendMessage({ type, ...details }).catch(() => {});
}

function chooseMimeType() {
  const candidates = [
    "video/webm;codecs=vp9,opus",
    "video/webm;codecs=vp8,opus",
    "video/webm"
  ];
  return candidates.find((type) => MediaRecorder.isTypeSupported(type)) || "";
}

async function startCapture(
  streamId,
  tab,
  includeMicrophone = false,
  syntheticMicrophoneAttested = false
) {
  if (saving || (recorder && recorder.state !== "inactive")) {
    throw new Error("A capture is already running or the previous file is still being saved.");
  }
  try {
    // Fail before recording starts if the shared contract runtime was not built.
    const core = await macleCoreReady;
    artifactHasher = new core.WasmSha256Accumulator();
    const constraints = {
      audio: { mandatory: {
        chromeMediaSource: "tab",
        chromeMediaSourceId: streamId
      }},
      video: { mandatory: {
        chromeMediaSource: "tab",
        chromeMediaSourceId: streamId
      }}
    };
    stream = await navigator.mediaDevices.getUserMedia(constraints);

    // Optional microphone capture is separately authorized by the user in
    // the extension settings. It is mixed with tab audio; neither source is
    // sent anywhere except the local recording.
    if (includeMicrophone) {
      microphoneStream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
      });
    }
    const tabAudioTracks = stream.getAudioTracks();
    const audioSourcesPresent = tabAudioTracks.length > 0 || Boolean(microphoneStream);
    let recordingAudioTracks = [];
    if (audioSourcesPresent) {
      audioContext = new AudioContext();
      await audioContext.resume();
      const mixedAudio = audioContext.createMediaStreamDestination();
      if (tabAudioTracks.length) {
        const tabAudio = audioContext.createMediaStreamSource(new MediaStream(tabAudioTracks));
        tabAudio.connect(audioContext.destination);
        tabAudio.connect(mixedAudio);
      }
      if (microphoneStream) {
        const microphone = audioContext.createMediaStreamSource(microphoneStream);
        microphone.connect(mixedAudio);
      }
      recordingAudioTracks = mixedAudio.stream.getAudioTracks();
    }
    recorderStream = new MediaStream([
      ...stream.getVideoTracks(),
      ...recordingAudioTracks
    ]);

    // Write chunks to the local Origin Private File System rather than
    // retaining an entire meeting recording in extension memory.
    const root = await navigator.storage.getDirectory();
    temporaryFileName = "macle-" + crypto.randomUUID() + ".webm";
    fileHandle = await root.getFileHandle(temporaryFileName, { create: true });
    writable = await fileHandle.createWritable();
    writeChain = Promise.resolve();

    const mimeType = chooseMimeType();
    recorder = new MediaRecorder(recorderStream, mimeType ? { mimeType } : undefined);
    captureFailure = null;
    sessionManifest = {
      schema: "macle.session-manifest/v1",
      session_id: crypto.randomUUID(),
      platform: "chrome",
      started_at: new Date().toISOString(),
      ended_at: null,
      sources: [
        { source_id: "meet-tab-video", kind: "tab_video", status: "available", detail: "Composite rendered Meet tab video; not participant-specific tracks." },
        { source_id: "meet-tab-audio", kind: "tab_audio", status: tabAudioTracks.length ? "available" : "unavailable", detail: tabAudioTracks.length ? "Browser-exposed tab playback audio." : "No tab audio track was exposed by the browser." },
        { source_id: "device-microphone", kind: "microphone", status: microphoneStream ? "available" : "not_requested", detail: microphoneStream ? (syntheticMicrophoneAttested ? "Synthetic microphone input explicitly attested." : "Microphone input.") : "Microphone capture was not requested." }
      ],
      artifacts: [],
      limitations: [
        "Captures only the selected rendered Google Meet tab.",
        "Does not expose individual participant media tracks.",
        "Microphone input, when enabled, is a distinct source mixed into the recording container."
      ],
      authorization: { test_scope: "synthetic_only", egress: "local_only" }
    };

    recorder.ondataavailable = (event) => {
      if (event.data && event.data.size) {
        const chunk = event.data;
        writeChain = writeChain.then(async () => {
          // Hash each bounded recorder chunk as it is written; never load the
          // complete meeting recording into memory merely to compute its digest.
          const bytes = await chunk.arrayBuffer();
          artifactHasher.update(new Uint8Array(bytes));
          await writable.write(chunk);
        });
      }
    };
    recorder.onerror = (event) => {
      captureFailure = event.error?.message || "MediaRecorder failed.";
      if (recorder && recorder.state !== "inactive") {
        saving = true;
        recorder.stop();
      }
    };
    recorder.onstop = saveCapture;
    recorder.start(1000);
    return { ok: true };
  } catch (error) {
    if (stream) stream.getTracks().forEach((track) => track.stop());
    if (microphoneStream) microphoneStream.getTracks().forEach((track) => track.stop());
    if (recorderStream) recorderStream.getTracks().forEach((track) => track.stop());
    if (audioContext) await audioContext.close().catch(() => {});
    if (writable) await writable.abort().catch(() => {});
    if (temporaryFileName) {
      const root = await navigator.storage.getDirectory().catch(() => null);
      if (root) await root.removeEntry(temporaryFileName).catch(() => {});
    }
    stream = null;
    microphoneStream = null;
    recorderStream = null;
    audioContext = null;
    fileHandle = null;
    writable = null;
    temporaryFileName = null;
    recorder = null;
    sessionManifest = null;
    artifactHasher = null;
    captureFailure = null;
    throw error;
  }
}

async function requestDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  try {
    const result = await chrome.runtime.sendMessage({
      type: "DOWNLOAD_BLOB",
      url,
      filename
    });
    if (!result?.ok) throw new Error(result?.error || "Browser download failed.");
    setTimeout(() => URL.revokeObjectURL(url), 60000);
  } catch (error) {
    URL.revokeObjectURL(url);
    throw error;
  }
}

async function saveCapture() {
  saving = true;
  try {
    sessionManifest.ended_at = new Date().toISOString();
    if (captureFailure) throw new Error(captureFailure);
    await writeChain;
    await writable.close();
    writable = null;
    const blob = await fileHandle.getFile();
    if (!blob.size) throw new Error("The capture produced an empty recording.");
    const stamp = sessionManifest.started_at.replace(/[:.]/g, "-");
    const filename = "MACLE-Meet-" + stamp + ".webm";
    const sha256 = artifactHasher.finalize_hex();
    artifactHasher = null;
    sessionManifest.artifacts.push({
      path: filename,
      media_type: blob.type || "video/webm",
      size_bytes: blob.size,
      sha256,
      started_at: sessionManifest.started_at,
      ended_at: sessionManifest.ended_at
    });
    const core = await macleCoreReady;
    core.validate_manifest_json(JSON.stringify(sessionManifest));
    const manifest = new Blob(
      [JSON.stringify(sessionManifest, null, 2)],
      { type: "application/json" }
    );
    await requestDownload(blob, filename);
    await requestDownload(
      manifest,
      filename.replace(/\.webm$/, ".manifest.json")
    );
    if (temporaryFileName) {
      const fileToRemove = temporaryFileName;
      setTimeout(async () => {
        const root = await navigator.storage.getDirectory().catch(() => null);
        if (root) await root.removeEntry(fileToRemove).catch(() => {});
      }, 65000);
      temporaryFileName = null;
    }
    send("CAPTURE_SAVED", { filename });
  } catch (error) {
    let failureMessage = error.message || String(error);
    if (sessionManifest) {
      sessionManifest.ended_at = sessionManifest.ended_at || new Date().toISOString();
      const hasFinalizedArtifact = sessionManifest.artifacts.length > 0;
      if (!hasFinalizedArtifact) {
        for (const source of sessionManifest.sources) {
          if (source.status === "available") {
            source.status = "interrupted";
            source.detail = (source.detail ? source.detail + " " : "") +
              "Capture ended before a complete artifact could be finalized.";
          }
        }
      }
      sessionManifest.limitations.push(
        (hasFinalizedArtifact ? "Capture artifact was finalized, but export failed: " :
          "Capture was interrupted before an artifact could be finalized: ") + failureMessage
      );
      try {
        const core = await macleCoreReady;
        core.validate_manifest_json(JSON.stringify(sessionManifest));
        const manifest = new Blob(
          [JSON.stringify(sessionManifest, null, 2)],
          { type: "application/json" }
        );
        const stamp = sessionManifest.started_at.replace(/[:.]/g, "-");
        await requestDownload(manifest, "MACLE-Meet-" + stamp + ".manifest.json");
      } catch (manifestError) {
        failureMessage += "; interruption manifest export also failed: " +
          (manifestError.message || String(manifestError));
      }
    }
    send("CAPTURE_ERROR", { error: failureMessage });
  } finally {
    // Stop every acquired source explicitly. Closing AudioContext does not
    // release the microphone MediaStream tracks created by getUserMedia().
    if (stream) stream.getTracks().forEach((track) => track.stop());
    if (microphoneStream) microphoneStream.getTracks().forEach((track) => track.stop());
    if (recorderStream) recorderStream.getTracks().forEach((track) => track.stop());
    if (audioContext) await audioContext.close().catch(() => {});
    if (writable) await writable.abort().catch(() => {});
    if (temporaryFileName) {
      const root = await navigator.storage.getDirectory().catch(() => null);
      if (root) await root.removeEntry(temporaryFileName).catch(() => {});
    }
    stream = null;
    microphoneStream = null;
    recorderStream = null;
    audioContext = null;
    recorder = null;
    fileHandle = null;
    writable = null;
    temporaryFileName = null;
    sessionManifest = null;
    artifactHasher = null;
    captureFailure = null;
    saving = false;
  }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.target !== "macle-offscreen") return;
  if (message.type === "START_CAPTURE") {
    startCapture(
      message.streamId,
      message.tab,
      Boolean(message.includeMicrophone),
      Boolean(message.syntheticMicrophoneAttested)
    )
      .then(sendResponse)
      .catch((error) => sendResponse({ ok: false, error: error.message || String(error) }));
    return true;
  }
  if (message.type === "STOP_CAPTURE") {
    if (!recorder || recorder.state === "inactive") {
      sendResponse(saving
        ? { ok: true, finalizing: true }
        : { ok: false, error: "No active capture." });
      return;
    }
    saving = true;
    recorder.stop();
    sendResponse({ ok: true, finalizing: true });
    return;
  }
});
