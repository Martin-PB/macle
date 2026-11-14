let creatingOffscreen;
let startingCapture = false;

async function ensureOffscreenDocument() {
  const url = chrome.runtime.getURL("offscreen.html");
  const contexts = await chrome.runtime.getContexts({
    contextTypes: ["OFFSCREEN_DOCUMENT"],
    documentUrls: [url]
  });
  if (!contexts.length) {
    if (!creatingOffscreen) {
      creatingOffscreen = chrome.offscreen.createDocument({
        url: "offscreen.html",
        reasons: ["USER_MEDIA"],
        justification: "Record the user-selected Google Meet tab locally for a synthetic test."
      });
    }
    try {
      await creatingOffscreen;
    } finally {
      creatingOffscreen = null;
    }
  }

  // Always perform the handshake, including when the document already
  // exists. PONG means both the listener and the shared WASM core are ready.
  let lastError = "The offscreen recorder did not become ready.";
  for (let attempt = 0; attempt < 50; attempt += 1) {
    try {
      const response = await chrome.runtime.sendMessage({
        target: "macle-offscreen",
        type: "PING"
      });
      if (response?.ok && response?.type === "PONG" && response?.coreReady) return;
      lastError = response?.error || lastError;
    } catch (error) {
      lastError = error.message || String(error);
    }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error("MACLE offscreen recorder startup timed out: " + lastError);
}

async function stopCapture() {
  const state = await chrome.storage.local.get(["captureActive", "captureStopping"]);
  if (!state.captureActive || state.captureStopping) return;

  // Keep the active state until the offscreen recorder has finalized and
  // exported both files. This prevents a second start racing the save.
  await chrome.storage.local.set({ captureStopping: true });
  const result = await chrome.runtime.sendMessage({
    target: "macle-offscreen",
    type: "STOP_CAPTURE"
  }).catch((error) => ({ ok: false, error: error.message || String(error) }));

  if (!result?.ok) {
    const error = result?.error || "The recorder could not be stopped.";
    // Fail closed: keep captureActive and capturedTabId so a later toolbar
    // click can retry STOP_CAPTURE instead of allowing a second recorder while
    // the original recorder may still be alive.
    await chrome.storage.local.set({ captureStopping: false });
    await chrome.action.setBadgeText({ text: "ERR" });
    await chrome.action.setTitle({ title: "MACLE capture stop error: " + error });
    return;
  }

  await chrome.action.setBadgeText({ text: "..." });
  await chrome.action.setTitle({ title: "MACLE is finalizing the recording and exporting its files" });
}

chrome.action.onClicked.addListener(async (tab) => {
  if (startingCapture) return;
  startingCapture = true;
  try {
    const state = await chrome.storage.local.get([
      "syntheticTestAttested",
      "captureActive",
      "pendingExport",
      "includeMicrophone",
      "syntheticMicrophoneAttested",
      "monitorTabAudio"
    ]);
    if (state.captureActive) {
      await stopCapture();
      return;
    }
    if (state.pendingExport) {
      await chrome.runtime.openOptionsPage();
      return;
    }
    if (!state.syntheticTestAttested) {
      await chrome.runtime.openOptionsPage();
      return;
    }
    if (!tab?.id || !tab.url?.startsWith("https://meet.google.com/")) {
      await chrome.action.setTitle({ title: "Open a Google Meet tab before starting capture" });
      return;
    }

    await ensureOffscreenDocument();
    // Called from the toolbar-click handler as documented by Chrome; the
    // stream ID is created immediately before it is passed to the offscreen consumer.
    const streamId = await chrome.tabCapture.getMediaStreamId({ targetTabId: tab.id });
    const result = await chrome.runtime.sendMessage({
      target: "macle-offscreen",
      type: "START_CAPTURE",
      streamId,
      tab: { id: tab.id, title: tab.title || "", url: tab.url },
      includeMicrophone: Boolean(state.includeMicrophone && state.syntheticMicrophoneAttested),
      syntheticMicrophoneAttested: Boolean(state.syntheticMicrophoneAttested),
      monitorTabAudio: Boolean(state.monitorTabAudio)
    });
    if (!result?.ok) throw new Error(result?.error || "Recorder did not start.");
    await chrome.storage.local.set({ captureActive: true, captureStopping: false, capturedTabId: tab.id });

    // Close the race where navigation or tab closure happens after the
    // capture starts but before capturedTabId is persisted and the tab event
    // listener can observe it.
    const currentTab = await chrome.tabs.get(tab.id).catch(() => null);
    if (!currentTab || currentTab.url !== tab.url) {
      await stopCapture();
      throw new Error("The Meet tab navigated or closed while capture was starting.");
    }

    await chrome.action.setBadgeText({ text: "REC" });
    await chrome.action.setBadgeBackgroundColor({ color: "#b3261e" });
    await chrome.action.setTitle({ title: "MACLE is recording this Meet tab — click to stop" });
  } catch (error) {
    await chrome.action.setBadgeText({ text: "ERR" });
    await chrome.action.setTitle({ title: error.message || String(error) });
    console.error("MACLE Meet capture:", error);
  } finally {
    startingCapture = false;
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "RETRY_PENDING_EXPORT") {
    if (sender.url !== chrome.runtime.getURL("options.html")) return;
    ensureOffscreenDocument()
      .then(() => chrome.runtime.sendMessage({
        target: "macle-offscreen",
        type: "RETRY_PENDING_EXPORT"
      }))
      .then(sendResponse)
      .catch((error) => sendResponse({ ok: false, error: error.message || String(error) }));
    return true;
  }

  if (message.type === "DOWNLOAD_BLOB" || message.type === "DOWNLOAD_STATUS") {
    if (sender.url !== chrome.runtime.getURL("offscreen.html")) return;
  }

  if (message.type === "DOWNLOAD_BLOB") {
    chrome.downloads.download({
      url: message.url,
      filename: message.filename,
      saveAs: true
    }, (downloadId) => {
      if (chrome.runtime.lastError) {
        sendResponse({ ok: false, error: chrome.runtime.lastError.message });
      } else {
        sendResponse({ ok: true, downloadId });
      }
    });
    return true;
  }

  if (message.type === "DOWNLOAD_STATUS") {
    chrome.downloads.search({ id: message.downloadId }, (items) => {
      if (chrome.runtime.lastError) {
        sendResponse({ ok: false, error: chrome.runtime.lastError.message });
        return;
      }
      const item = items && items[0];
      if (!item) {
        sendResponse({ ok: false, error: "Chrome no longer reports download " + message.downloadId });
        return;
      }
      sendResponse({
        ok: true,
        state: item.state,
        error: item.error || null,
        filename: item.filename || null
      });
    });
    return true;
  }

  if (message.type === "CAPTURE_SAVED" || message.type === "CAPTURE_ERROR") {
    if (sender.url !== chrome.runtime.getURL("offscreen.html")) return;
    chrome.storage.local.set({ captureActive: false, captureStopping: false, capturedTabId: null });
    chrome.action.setBadgeText({ text: message.type === "CAPTURE_SAVED" ? "OK" : "ERR" });
    chrome.action.setTitle({
      title: message.type === "CAPTURE_SAVED"
        ? "MACLE capture saved: " + message.filename
        : "MACLE capture error: " + message.error +
          (message.pendingExport ? " — open extension settings to retry the retained export" : "")
    });
  }
});

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo) => {
  // Stop on any navigation: tabCapture otherwise survives page navigations.
  if (changeInfo.status !== "loading") return;
  const state = await chrome.storage.local.get("capturedTabId");
  if (state.capturedTabId === tabId) await stopCapture();
});

chrome.tabs.onRemoved.addListener(async (tabId) => {
  const state = await chrome.storage.local.get("capturedTabId");
  if (state.capturedTabId === tabId) await stopCapture();
});


chrome.runtime.onStartup.addListener(async () => {
  // A browser restart ends all media tracks; clear any stale toolbar state.
  await chrome.storage.local.set({ captureActive: false, captureStopping: false, capturedTabId: null });
  await chrome.action.setBadgeText({ text: "" });
});
