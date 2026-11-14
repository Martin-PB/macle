let creatingOffscreen;

async function ensureOffscreenDocument() {
  const url = chrome.runtime.getURL("offscreen.html");
  const contexts = await chrome.runtime.getContexts({
    contextTypes: ["OFFSCREEN_DOCUMENT"],
    documentUrls: [url]
  });
  if (contexts.length) return;
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

async function stopCapture() {
  await chrome.runtime.sendMessage({ target: "macle-offscreen", type: "STOP_CAPTURE" }).catch(() => {});
  await chrome.storage.local.set({ captureActive: false, capturedTabId: null });
  await chrome.action.setBadgeText({ text: "" });
  await chrome.action.setTitle({ title: "MACLE Meet capture — click to start" });
}

chrome.action.onClicked.addListener(async (tab) => {
  try {
    const state = await chrome.storage.local.get([
      "syntheticTestAttested",
      "captureActive",
      "includeMicrophone",
      "syntheticMicrophoneAttested"
    ]);
    if (state.captureActive) {
      await stopCapture();
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
      syntheticMicrophoneAttested: Boolean(state.syntheticMicrophoneAttested)
    });
    if (!result?.ok) throw new Error(result?.error || "Recorder did not start.");
    await chrome.storage.local.set({ captureActive: true, capturedTabId: tab.id });
    await chrome.action.setBadgeText({ text: "REC" });
    await chrome.action.setBadgeBackgroundColor({ color: "#b3261e" });
    await chrome.action.setTitle({ title: "MACLE is recording this Meet tab — click to stop" });
  } catch (error) {
    await chrome.action.setBadgeText({ text: "ERR" });
    await chrome.action.setTitle({ title: error.message || String(error) });
    console.error("MACLE Meet capture:", error);
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
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

  if (message.type === "CAPTURE_SAVED" || message.type === "CAPTURE_ERROR") {
    chrome.storage.local.set({ captureActive: false, capturedTabId: null });
    chrome.action.setBadgeText({ text: message.type === "CAPTURE_SAVED" ? "OK" : "ERR" });
    chrome.action.setTitle({
      title: message.type === "CAPTURE_SAVED"
        ? "MACLE capture saved: " + message.filename
        : "MACLE capture error: " + message.error
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
  await chrome.storage.local.set({ captureActive: false, capturedTabId: null });
  await chrome.action.setBadgeText({ text: "" });
});
