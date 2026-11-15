const attest = document.getElementById("attest");
const includeMicrophone = document.getElementById("includeMicrophone");
const syntheticMicrophone = document.getElementById("syntheticMicrophone");
const monitorTabAudio = document.getElementById("monitorTabAudio");
const status = document.getElementById("status");
const pendingExportSection = document.getElementById("pendingExport");
const pendingExportStatus = document.getElementById("pendingExportStatus");
const retryExport = document.getElementById("retryExport");

chrome.storage.local.get([
  "syntheticTestAttested",
  "includeMicrophone",
  "syntheticMicrophoneAttested",
  "monitorTabAudio",
  "pendingExport"
]).then((value) => {
  attest.checked = Boolean(value.syntheticTestAttested);
  includeMicrophone.checked = Boolean(value.includeMicrophone);
  syntheticMicrophone.checked = Boolean(value.syntheticMicrophoneAttested);
  monitorTabAudio.checked = Boolean(value.monitorTabAudio);
  if (value.pendingExport) {
    pendingExportSection.hidden = false;
    pendingExportStatus.textContent =
      value.pendingExport.filename + " — media: " +
      (value.pendingExport.mediaComplete ? "exported" : "pending") +
      ", manifest: " + (value.pendingExport.manifestComplete ? "exported" : "pending") +
      ". The retained recording will be SHA-256 checked before retry.";
  }
});

document.getElementById("authorizeMic").addEventListener("click", async () => {
  if (!syntheticMicrophone.checked) {
    status.textContent = "First attest that the selected microphone input is synthetic test audio.";
    return;
  }
  try {
    const microphone = await navigator.mediaDevices.getUserMedia({ audio: true });
    microphone.getTracks().forEach((track) => track.stop());
    status.textContent = "Microphone permission granted by Chrome.";
  } catch (error) {
    status.textContent = "Microphone permission not granted: " + (error.message || String(error));
  }
});

document.getElementById("save").addEventListener("click", async () => {
  if (includeMicrophone.checked && !syntheticMicrophone.checked) {
    status.textContent = "Microphone capture is blocked unless its input is attested as synthetic test audio.";
    return;
  }
  await chrome.storage.local.set({
    syntheticTestAttested: attest.checked,
    includeMicrophone: includeMicrophone.checked,
    syntheticMicrophoneAttested: syntheticMicrophone.checked,
    monitorTabAudio: monitorTabAudio.checked
  });
  status.textContent = attest.checked
    ? "Synthetic-only attestation and capture settings saved on this device."
    : "Attestation disabled. Capture will not start.";
});


retryExport.addEventListener("click", async () => {
  retryExport.disabled = true;
  pendingExportStatus.textContent = "Checking the retained recording and retrying the missing exports…";
  try {
    const result = await chrome.runtime.sendMessage({ type: "RETRY_PENDING_EXPORT" });
    if (!result?.ok) throw new Error(result?.error || "Export recovery failed.");
    pendingExportSection.hidden = true;
    status.textContent = "Recording export recovered: " + result.filename;
  } catch (error) {
    pendingExportStatus.textContent = "Export recovery failed: " + (error.message || String(error));
  } finally {
    retryExport.disabled = false;
  }
});
