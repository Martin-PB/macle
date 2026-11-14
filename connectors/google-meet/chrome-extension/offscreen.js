let recorder = null;
let stream = null;
let microphoneStream = null;
let recorderStream = null;
let audioContext = null;
let fileHandle = null;
let writable = null;
let temporaryFileName = null;
let writeChain = Promise.resolve();
let captureMetadata = null;
let saving = false;
let captureFailure = null;

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
    captureMetadata = {
      schema: "macle.capture-manifest/v0",
      captureId: crypto.randomUUID(),
      platform: "google_meet",
      captureMode: "single_device_visible_tab",
      startedAt: new Date().toISOString(),
      endedAt: null,
      tabOrigin: new URL(tab.url).origin,
      tabTitle: tab.title,
      mimeType: recorder.mimeType || mimeType || "browser-default",
      audioSource: [
        tabAudioTracks.length ? "google_meet_tab_audio_output" : null,
        microphoneStream ? "local_microphone" : null
      ].filter(Boolean),
      videoSource: "rendered_google_meet_tab",
      microphoneCaptured: Boolean(microphoneStream),
      microphoneSyntheticAttested: Boolean(microphoneStream && syntheticMicrophoneAttested),
      individualParticipantTracks: false,
      syntheticTestAttested: true,
      egress: "local_browser_download_only"
    };

    recorder.ondataavailable = (event) => {
      if (event.data && event.data.size) {
        writeChain = writeChain.then(() => writable.write(event.data));
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
    captureMetadata = null;
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
    captureMetadata.endedAt = new Date().toISOString();
    if (captureFailure) throw new Error(captureFailure);
    await writeChain;
    await writable.close();
    writable = null;
    const blob = await fileHandle.getFile();
    if (!blob.size) throw new Error("The capture produced an empty recording.");
    const stamp = captureMetadata.startedAt.replace(/[:.]/g, "-");
    const filename = "MACLE-Meet-" + stamp + ".webm";
    await requestDownload(blob, filename);
    const manifest = new Blob(
      [JSON.stringify(captureMetadata, null, 2)],
      { type: "application/json" }
    );
    await requestDownload(
      manifest,
      filename.replace(/\\.webm$/, ".manifest.json")
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
    send("CAPTURE_ERROR", { error: error.message || String(error) });
  } finally {
    if (stream) stream.getTracks().forEach((track) => track.stop());
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
    captureMetadata = null;
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
      sendResponse({ ok: false, error: "No active capture." });
      return;
    }
    saving = true;
    recorder.stop();
    sendResponse({ ok: true });
    return true;
  }
});
