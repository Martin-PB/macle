const attest = document.getElementById("attest");
const includeMicrophone = document.getElementById("includeMicrophone");
const syntheticMicrophone = document.getElementById("syntheticMicrophone");
const status = document.getElementById("status");

chrome.storage.local.get([
  "syntheticTestAttested",
  "includeMicrophone",
  "syntheticMicrophoneAttested"
]).then((value) => {
  attest.checked = Boolean(value.syntheticTestAttested);
  includeMicrophone.checked = Boolean(value.includeMicrophone);
  syntheticMicrophone.checked = Boolean(value.syntheticMicrophoneAttested);
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
    syntheticMicrophoneAttested: syntheticMicrophone.checked
  });
  status.textContent = attest.checked
    ? "Synthetic-only attestation and capture settings saved on this device."
    : "Attestation disabled. Capture will not start.";
});
