import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const offscreenPath = resolve(
  repoRoot,
  "connectors/google-meet/chrome-extension/offscreen.js"
);
const originalSource = readFileSync(offscreenPath, "utf8");
const importExpression = 'import(chrome.runtime.getURL("core-wasm/macle_core.js"))';
const serviceWorkerPath = resolve(
  repoRoot,
  "connectors/google-meet/chrome-extension/service-worker.js"
);
const serviceWorkerSource = readFileSync(serviceWorkerPath, "utf8");

class FakeBlob {
  constructor(parts, options = {}) {
    this.parts = parts;
    this.type = options.type || "";
    this.size = parts.reduce(
      (size, part) => size + (typeof part === "string" ? part.length : (part.size ?? part.byteLength ?? 0)),
      0
    );
  }
}

async function runRecovery({
  expectedHash = "sha-ok",
  actualHash = "sha-ok",
  mediaComplete = false,
  manifestComplete = false,
  downloadState = "complete",
  fileMissing = false
} = {}) {
  const downloads = [];
  const events = [];
  const pending = {
    temporaryFileName: "retained.webm",
    filename: "meeting.webm",
    manifestFilename: "meeting.manifest.json",
    manifestJson: JSON.stringify({
      schema: "macle.session-manifest/v1",
      artifacts: [],
      limitations: []
    }),
    sha256: expectedHash,
    sizeBytes: 4,
    mediaComplete,
    manifestComplete,
    createdAt: "2026-11-15T00:00:00Z"
  };

  let stored = pending;
  let removed = false;
  let listener;
  const reader = {
    index: 0,
    async read() {
      if (this.index++ === 0) {
        return { done: false, value: new Uint8Array([1, 2, 3, 4]) };
      }
      return { done: true };
    },
    releaseLock() {}
  };
  const retainedBlob = {
    size: 4,
    stream: () => ({ getReader: () => reader })
  };
  const root = {
    async getFileHandle() {
      return { async getFile() { return retainedBlob; } };
    },
    async removeEntry() {
      removed = true;
      if (fileMissing) {
        const error = new Error("File was already removed.");
        error.name = "NotFoundError";
        throw error;
      }
    }
  };

  const chrome = {
    runtime: {
      getURL: () => "chrome-extension://test/core-wasm/macle_core.js",
      onMessage: {
        addListener(callback) { listener = callback; }
      },
      async sendMessage(message) {
        if (message.type === "DOWNLOAD_BLOB") {
          downloads.push(message.filename);
          return { ok: true, downloadId: downloads.length };
        }
        if (message.type === "DOWNLOAD_STATUS") {
          return {
            ok: true,
            state: downloadState,
            error: downloadState === "interrupted" ? "USER_CANCELED" : null
          };
        }
        events.push(message);
        return { ok: true };
      }
    },
    storage: {
      local: {
        async get() { return { pendingExport: stored }; },
        async set(value) { stored = value.pendingExport; },
        async remove() { stored = null; }
      }
    }
  };

  const source = originalSource.replace(
    importExpression,
    'Promise.resolve({ default: async () => {}, ' +
      'WasmSha256Accumulator: class { ' +
      'update(bytes) { globalThis.__hashBytes = (globalThis.__hashBytes || 0) + bytes.length; } ' +
      'finalize_hex() { return globalThis.__actualHash; } }, ' +
      'validate_manifest_json: (json) => JSON.parse(json) })'
  );
  assert.notEqual(source, originalSource, "WASM import seam must be present");

  const context = {
    chrome,
    navigator: { storage: { async getDirectory() { return root; } } },
    URL: { createObjectURL: () => "blob:test", revokeObjectURL() {} },
    Blob: FakeBlob,
    setTimeout: () => 1,
    console: { error() {} },
    MediaRecorder: function MediaRecorder() {},
    MediaStream: function MediaStream() {},
    AudioContext: function AudioContext() {},
    crypto: { randomUUID: () => "test-id" },
    Date,
    Promise,
    Uint8Array,
    JSON,
    Error,
    __actualHash: actualHash,
    __hashBytes: 0
  };
  context.globalThis = context;
  vm.runInNewContext(source, context, { filename: "offscreen.js" });

  const result = await new Promise((resolveResponse) => {
    listener(
      { target: "macle-offscreen", type: "RETRY_PENDING_EXPORT" },
      {},
      resolveResponse
    );
  });

  return {
    result,
    downloads,
    stored,
    removed,
    events,
    hashBytes: context.__hashBytes
  };
}

async function runConcurrentStart() {
  let releaseMedia;
  const mediaGate = new Promise((resolveMedia) => { releaseMedia = resolveMedia; });
  let listener;
  let recorderStarts = 0;
  const videoTrack = { kind: "video", stop() {} };
  const mediaStream = {
    getAudioTracks: () => [],
    getVideoTracks: () => [videoTrack],
    getTracks: () => [videoTrack]
  };
  const writable = {
    async write() {},
    async close() {},
    async abort() {}
  };
  const root = {
    async getFileHandle() {
      return { async createWritable() { return writable; } };
    }
  };
  class FakeMediaStream {
    constructor(tracks) { this.tracks = tracks; }
    getTracks() { return this.tracks; }
  }
  class FakeMediaRecorder {
    static isTypeSupported() { return false; }
    constructor() { this.state = "inactive"; }
    start() { recorderStarts += 1; this.state = "recording"; }
  }

  const chrome = {
    runtime: {
      getURL: () => "chrome-extension://test/core-wasm/macle_core.js",
      onMessage: { addListener(callback) { listener = callback; } },
      async sendMessage() { return { ok: true }; }
    },
    storage: { local: { async get() { return {}; } } }
  };
  const navigator = {
    mediaDevices: { async getUserMedia() { return mediaGate; } },
    storage: { async getDirectory() { return root; } }
  };
  const source = originalSource.replace(
    importExpression,
    'Promise.resolve({ default: async () => {}, ' +
      'WasmSha256Accumulator: class { update() {} finalize_hex() { return "unused"; } }, ' +
      'validate_manifest_json: (json) => JSON.parse(json) })'
  );
  const context = {
    chrome,
    navigator,
    URL: { createObjectURL: () => "blob:test", revokeObjectURL() {} },
    Blob: FakeBlob,
    setTimeout: (callback) => { callback(); return 1; },
    console: { error() {} },
    MediaRecorder: FakeMediaRecorder,
    MediaStream: FakeMediaStream,
    AudioContext: function AudioContext() {},
    crypto: { randomUUID: () => "test-id" },
    Date,
    Promise,
    Uint8Array,
    JSON,
    Error
  };
  context.globalThis = context;
  vm.runInNewContext(source, context, { filename: "offscreen.js" });

  const request = {
    target: "macle-offscreen",
    type: "START_CAPTURE",
    streamId: "fresh-stream",
    tab: { id: 7, url: "https://meet.google.com/test" }
  };
  const firstResponse = new Promise((resolveResponse) => listener(request, {}, resolveResponse));
  const secondResponse = await new Promise((resolveResponse) => listener(request, {}, resolveResponse));
  releaseMedia(mediaStream);
  const first = await firstResponse;
  return { first, second: secondResponse, recorderStarts };
}

async function runManifestValidationFailureRetention() {
  let listener;
  let lastRecorder;
  let stored = null;
  let removed = false;
  const events = [];
  const writable = {
    async write() {},
    async close() {},
    async abort() {}
  };
  const fileBlob = new FakeBlob([new Uint8Array([1, 2, 3, 4])], { type: "video/webm" });
  const handle = {
    async createWritable() { return writable; },
    async getFile() { return fileBlob; }
  };
  const root = {
    async getFileHandle() { return handle; },
    async removeEntry() { removed = true; }
  };
  const stream = {
    getAudioTracks: () => [],
    getVideoTracks: () => [{ kind: "video", stop() {} }],
    getTracks: () => [{ kind: "video", stop() {} }]
  };
  class FakeMediaStream {
    constructor(tracks) { this.tracks = tracks; }
  }
  class FakeMediaRecorder {
    static isTypeSupported() { return false; }
    constructor() {
      this.state = "inactive";
      lastRecorder = this;
    }
    start() { this.state = "recording"; }
  }

  const chrome = {
    runtime: {
      getURL: () => "chrome-extension://test/core-wasm/macle_core.js",
      onMessage: { addListener(callback) { listener = callback; } },
      async sendMessage(message) { events.push(message); return { ok: true }; }
    },
    storage: {
      local: {
        async get() { return { pendingExport: stored }; },
        async set(value) { stored = value.pendingExport; },
        async remove() { stored = null; }
      }
    }
  };
  const navigator = {
    mediaDevices: { async getUserMedia() { return stream; } },
    storage: { async getDirectory() { return root; } }
  };
  const source = originalSource.replace(
    importExpression,
    'Promise.resolve({ default: async () => {}, ' +
      'WasmSha256Accumulator: class { update() {} finalize_hex() { return "sha256-test"; } }, ' +
      'validate_manifest_json: () => { throw new Error("synthetic schema rejection"); } })'
  );
  const context = {
    chrome,
    navigator,
    URL: { createObjectURL: () => "blob:test", revokeObjectURL() {} },
    Blob: FakeBlob,
    setTimeout: () => 1,
    console: { error() {} },
    MediaRecorder: FakeMediaRecorder,
    MediaStream: FakeMediaStream,
    AudioContext: function AudioContext() {},
    crypto: { randomUUID: () => "test-id" },
    Date,
    Promise,
    Uint8Array,
    JSON,
    Error
  };
  context.globalThis = context;
  vm.runInNewContext(source, context, { filename: "offscreen.js" });

  const started = await new Promise((resolveResponse) => {
    listener({
      target: "macle-offscreen",
      type: "START_CAPTURE",
      streamId: "fresh-stream",
      tab: { id: 7, url: "https://meet.google.com/test" }
    }, {}, resolveResponse);
  });
  assert.equal(started.ok, true);
  await lastRecorder.onstop();
  return { stored, removed, events };
}

async function runSuccessfulCaptureSave() {
  let listener;
  let lastRecorder;
  let stored = null;
  let removed = false;
  const downloads = [];
  const events = [];
  const downloadStates = ["in_progress", "complete", "complete"];
  let statusQueries = 0;
  const writable = {
    async write() {},
    async close() {},
    async abort() {}
  };
  const fileBlob = new FakeBlob([new Uint8Array([1, 2, 3, 4])], { type: "video/webm" });
  const handle = {
    async createWritable() { return writable; },
    async getFile() { return fileBlob; }
  };
  const root = {
    async getFileHandle() { return handle; },
    async removeEntry() { removed = true; }
  };
  const stream = {
    getAudioTracks: () => [],
    getVideoTracks: () => [{ kind: "video", stop() {} }],
    getTracks: () => [{ kind: "video", stop() {} }]
  };
  class FakeMediaStream {
    constructor(tracks) { this.tracks = tracks; }
    getTracks() { return this.tracks; }
  }
  class FakeMediaRecorder {
    static isTypeSupported() { return false; }
    constructor() {
      this.state = "inactive";
      lastRecorder = this;
    }
    start() { this.state = "recording"; }
  }

  const chrome = {
    runtime: {
      getURL: () => "chrome-extension://test/core-wasm/macle_core.js",
      onMessage: { addListener(callback) { listener = callback; } },
      async sendMessage(message) {
        if (message.type === "DOWNLOAD_BLOB") {
          downloads.push(message.filename);
          return { ok: true, downloadId: downloads.length };
        }
        if (message.type === "DOWNLOAD_STATUS") {
          const state = downloadStates[Math.min(statusQueries, downloadStates.length - 1)];
          statusQueries += 1;
          return { ok: true, state };
        }
        events.push(message);
        return { ok: true };
      }
    },
    storage: {
      local: {
        async get() { return { pendingExport: stored }; },
        async set(value) { stored = value.pendingExport; },
        async remove() { stored = null; }
      }
    }
  };
  const navigator = {
    mediaDevices: { async getUserMedia() { return stream; } },
    storage: { async getDirectory() { return root; } }
  };
  const source = originalSource.replace(
    importExpression,
    'Promise.resolve({ default: async () => {}, ' +
      'WasmSha256Accumulator: class { update() {} finalize_hex() { return "sha256-success"; } }, ' +
      'validate_manifest_json: (json) => JSON.parse(json) })'
  );
  const context = {
    chrome,
    navigator,
    URL: { createObjectURL: () => "blob:test", revokeObjectURL() {} },
    Blob: FakeBlob,
    setTimeout: (callback) => { callback(); return 1; },
    console: { error() {} },
    MediaRecorder: FakeMediaRecorder,
    MediaStream: FakeMediaStream,
    AudioContext: function AudioContext() {},
    crypto: { randomUUID: () => "success-id" },
    Date,
    Promise,
    Uint8Array,
    JSON,
    Error
  };
  context.globalThis = context;
  vm.runInNewContext(source, context, { filename: "offscreen.js" });

  const started = await new Promise((resolveResponse) => {
    listener({
      target: "macle-offscreen",
      type: "START_CAPTURE",
      streamId: "fresh-stream",
      tab: { id: 7, url: "https://meet.google.com/test" }
    }, {}, resolveResponse);
  });
  assert.equal(started.ok, true);
  await lastRecorder.onstop();
  return { stored, removed, downloads, events, statusQueries };
}

test("recovery skips media already exported and downloads only the manifest", async () => {
  const result = await runRecovery({
    mediaComplete: true,
    manifestComplete: false
  });

  assert.equal(result.result.ok, true);
  assert.deepEqual(result.downloads, ["meeting.manifest.json"]);
  assert.equal(result.stored, null);
  assert.equal(result.removed, true);
  assert.equal(result.hashBytes, 4);
  assert.ok(result.events.some((event) => event.type === "CAPTURE_SAVED"));
});

test("recovery exports both artifacts when neither has completed", async () => {
  const result = await runRecovery();

  assert.equal(result.result.ok, true);
  assert.deepEqual(result.downloads, ["meeting.webm", "meeting.manifest.json"]);
  assert.equal(result.stored, null);
  assert.equal(result.removed, true);
  assert.equal(result.hashBytes, 4);
});

test("SHA-256 mismatch blocks downloads and preserves the pending artifact", async () => {
  const result = await runRecovery({ expectedHash: "expected", actualHash: "corrupt" });

  assert.equal(result.result.ok, false);
  assert.match(result.result.error, /SHA-256 integrity check/);
  assert.deepEqual(result.downloads, []);
  assert.notEqual(result.stored, null);
  assert.equal(result.removed, false);
  assert.ok(!result.events.some((event) => event.type === "CAPTURE_SAVED"));
  assert.equal(result.hashBytes, 4);
});


test("interrupted download keeps the artifact and never reports capture saved", async () => {
  const result = await runRecovery({ downloadState: "interrupted" });

  assert.equal(result.result.ok, false);
  assert.match(result.result.error, /interrupted/);
  assert.deepEqual(result.downloads, ["meeting.webm"]);
  assert.notEqual(result.stored, null);
  assert.equal(result.removed, false);
  assert.ok(!result.events.some((event) => event.type === "CAPTURE_SAVED"));
});


async function runToolbarClickWithPendingExport() {
  let onClicked;
  let streamRequests = 0;
  let offscreenMessages = 0;
  let optionsOpened = 0;

  const chrome = {
    runtime: {
      async openOptionsPage() { optionsOpened += 1; },
      async sendMessage() { offscreenMessages += 1; return { ok: true }; },
      onMessage: { addListener() {} },
      onStartup: { addListener() {} }
    },
    action: {
      onClicked: { addListener(callback) { onClicked = callback; } },
      async setBadgeText() {},
      async setBadgeBackgroundColor() {},
      async setTitle() {}
    },
    storage: {
      local: {
        async get() {
          return {
            pendingExport: { filename: "retained.webm" },
            syntheticTestAttested: true,
            captureActive: true,
            capturedTabId: 7,
            includeMicrophone: false,
            syntheticMicrophoneAttested: false,
            monitorTabAudio: false
          };
        },
        async set() {}
      }
    },
    tabs: {
      onUpdated: { addListener() {} },
      onRemoved: { addListener() {} },
      async get() { return { url: "https://meet.google.com/test" }; }
    },
    tabCapture: {
      async getMediaStreamId() { streamRequests += 1; return "must-not-be-requested"; }
    },
    offscreen: { async createDocument() {} }
  };

  vm.runInNewContext(serviceWorkerSource, {
    chrome,
    console: { error() {} },
    Promise,
    setTimeout
  }, { filename: "service-worker.js" });

  await onClicked({
    id: 7,
    title: "Synthetic Meet",
    url: "https://meet.google.com/test"
  });
  return { streamRequests, offscreenMessages, optionsOpened };
}

async function runRecorderConstructionFailure() {
  let listener;
  let removed = false;
  let aborted = false;
  let trackStops = 0;
  const track = { kind: "video", stop() { trackStops += 1; } };
  const mediaStream = {
    getAudioTracks: () => [],
    getVideoTracks: () => [track],
    getTracks: () => [track]
  };
  const writable = {
    async write() {},
    async close() {},
    async abort() { aborted = true; }
  };
  const root = {
    async getFileHandle() {
      return { async createWritable() { return writable; } };
    },
    async removeEntry() { removed = true; }
  };
  class FakeMediaStream {
    constructor(tracks) { this.tracks = tracks; }
    getTracks() { return this.tracks; }
  }
  class FailingMediaRecorder {
    static isTypeSupported() { return false; }
    constructor() { throw new Error("synthetic MediaRecorder constructor failure"); }
  }

  const chrome = {
    runtime: {
      getURL: () => "chrome-extension://test/core-wasm/macle_core.js",
      onMessage: { addListener(callback) { listener = callback; } },
      async sendMessage() { return { ok: true }; }
    },
    storage: { local: { async get() { return {}; } } }
  };
  const navigator = {
    mediaDevices: { async getUserMedia() { return mediaStream; } },
    storage: { async getDirectory() { return root; } }
  };
  const source = originalSource.replace(
    importExpression,
    'Promise.resolve({ default: async () => {}, ' +
      'WasmSha256Accumulator: class { update() {} finalize_hex() { return "unused"; } }, ' +
      'validate_manifest_json: (json) => JSON.parse(json) })'
  );
  const context = {
    chrome,
    navigator,
    URL: { createObjectURL: () => "blob:test", revokeObjectURL() {} },
    Blob: FakeBlob,
    setTimeout: (callback) => { callback(); return 1; },
    console: { error() {} },
    MediaRecorder: FailingMediaRecorder,
    MediaStream: FakeMediaStream,
    AudioContext: function AudioContext() {},
    crypto: { randomUUID: () => "failed-start-id" },
    Date,
    Promise,
    Uint8Array,
    JSON,
    Error
  };
  context.globalThis = context;
  vm.runInNewContext(source, context, { filename: "offscreen.js" });

  const result = await new Promise((resolveResponse) => {
    listener({
      target: "macle-offscreen",
      type: "START_CAPTURE",
      streamId: "fresh-stream",
      tab: { id: 7, url: "https://meet.google.com/test" }
    }, {}, resolveResponse);
  });
  return { result, removed, aborted, trackStops };
}

test("concurrent START_CAPTURE messages admit only one Offscreen start", async () => {
  const result = await runConcurrentStart();

  assert.equal(result.first.ok, true);
  assert.equal(result.second.ok, false);
  assert.match(result.second.error, /already starting/);
  assert.equal(result.recorderStarts, 1);
});


async function runStopFailure() {
  let onClicked;
  const state = {
    captureActive: true,
    captureStopping: false,
    capturedTabId: 7
  };
  const chrome = {
    runtime: {
      async sendMessage() { return { ok: false, error: "offscreen unavailable" }; },
      async openOptionsPage() {},
      onMessage: { addListener() {} },
      onStartup: { addListener() {} }
    },
    action: {
      onClicked: { addListener(callback) { onClicked = callback; } },
      async setBadgeText() {},
      async setBadgeBackgroundColor() {},
      async setTitle() {}
    },
    storage: {
      local: {
        async get() { return { ...state }; },
        async set(value) { Object.assign(state, value); }
      }
    },
    tabs: {
      onUpdated: { addListener() {} },
      onRemoved: { addListener() {} }
    },
    tabCapture: {
      async getMediaStreamId() { throw new Error("must not start another capture"); }
    }
  };
  vm.runInNewContext(serviceWorkerSource, {
    chrome,
    console: { error() {} },
    Promise,
    setTimeout
  }, { filename: "service-worker.js" });
  await onClicked({ id: 7, url: "https://meet.google.com/test" });
  return state;
}

test("toolbar opens recovery settings without issuing a new stream ID", async () => {
  const result = await runToolbarClickWithPendingExport();

  assert.equal(result.optionsOpened, 1);
  assert.equal(result.streamRequests, 0);
  assert.equal(result.offscreenMessages, 0);
});


test("finalized OPFS artifact is retained if manifest validation fails", async () => {
  const result = await runManifestValidationFailureRetention();

  assert.notEqual(result.stored, null);
  assert.equal(result.stored.temporaryFileName, "macle-test-id.webm");
  assert.equal(result.stored.sha256, "sha256-test");
  assert.equal(result.removed, false);
  assert.ok(result.events.some((event) =>
    event.type === "CAPTURE_ERROR" && event.pendingExport === true
  ));
  assert.ok(!result.events.some((event) => event.type === "CAPTURE_SAVED"));
});


test("completed downloads clear stale recovery metadata after a cleanup crash", async () => {
  const result = await runRecovery({
    mediaComplete: true,
    manifestComplete: true,
    fileMissing: true
  });

  assert.equal(result.result.ok, true);
  assert.deepEqual(result.downloads, []);
  assert.equal(result.stored, null);
  assert.equal(result.removed, true);
  assert.equal(result.hashBytes, 0);
  assert.ok(result.events.some((event) => event.type === "CAPTURE_SAVED"));
});


test("successful capture reports saved only after both downloads and local cleanup", async () => {
  const result = await runSuccessfulCaptureSave();

  const saved = result.events.find((event) => event.type === "CAPTURE_SAVED");
  assert.ok(saved);
  assert.equal(result.downloads[0], saved.filename);
  assert.equal(result.downloads[1], saved.filename.replace(/\\.webm$/, ".manifest.json"));
  assert.equal(result.downloads.length, 2);
  assert.equal(result.statusQueries, 3);
  assert.equal(result.stored, null);
  assert.equal(result.removed, true);
  assert.ok(result.events.some((event) => event.type === "CAPTURE_SAVED"));
  assert.ok(!result.events.some((event) => event.type === "CAPTURE_ERROR"));
});


test("manifest interruption preserves the completed media export for retry", async () => {
  const result = await runRecovery({
    mediaComplete: true,
    manifestComplete: false,
    downloadState: "interrupted"
  });

  assert.equal(result.result.ok, false);
  assert.deepEqual(result.downloads, ["meeting.manifest.json"]);
  assert.equal(result.stored.mediaComplete, true);
  assert.equal(result.stored.manifestComplete, false);
  assert.equal(result.removed, false);
  assert.ok(!result.events.some((event) => event.type === "CAPTURE_SAVED"));
});


test("MediaRecorder setup failure removes partial OPFS file and releases resources", async () => {
  const result = await runRecorderConstructionFailure();

  assert.equal(result.result.ok, false);
  assert.match(result.result.error, /synthetic MediaRecorder constructor failure/);
  assert.equal(result.removed, true);
  assert.equal(result.aborted, true);
  assert.ok(result.trackStops > 0);
  assert.doesNotMatch(result.result.error, /pendingExportRecord is not defined/);
});


async function runCaptureStatusSenderCheck() {
  let onMessage;
  const state = {
    captureActive: true,
    captureStopping: false,
    capturedTabId: 7
  };
  const chrome = {
    runtime: {
      getURL: (path) => "chrome-extension://test/" + path,
      onMessage: { addListener(callback) { onMessage = callback; } },
      onStartup: { addListener() {} },
      async sendMessage() { return { ok: true }; },
      async openOptionsPage() {}
    },
    action: {
      onClicked: { addListener() {} },
      async setBadgeText() {},
      async setTitle() {}
    },
    storage: {
      local: {
        async get() { return { ...state }; },
        async set(value) { Object.assign(state, value); }
      }
    },
    tabs: {
      onUpdated: { addListener() {} },
      onRemoved: { addListener() {} }
    }
  };
  vm.runInNewContext(serviceWorkerSource, {
    chrome,
    console: { error() {} },
    Promise,
    setTimeout
  }, { filename: "service-worker.js" });
  onMessage(
    { type: "CAPTURE_SAVED", filename: "spoofed.webm" },
    { url: "chrome-extension://test/options.html" },
    () => {}
  );
  const afterSpoof = { ...state };
  onMessage(
    { type: "CAPTURE_SAVED", filename: "real.webm" },
    { url: "chrome-extension://test/offscreen.html" },
    () => {}
  );
  await Promise.resolve();
  return { afterSpoof, final: state };
}

test("failed stop acknowledgement keeps capture active and blocks a new start", async () => {
  const state = await runStopFailure();

  assert.equal(state.captureActive, true);
  assert.equal(state.captureStopping, false);
  assert.equal(state.capturedTabId, 7);
});


test("only the Offscreen document may clear active capture state", async () => {
  const result = await runCaptureStatusSenderCheck();

  assert.equal(result.afterSpoof.captureActive, true);
  assert.equal(result.afterSpoof.capturedTabId, 7);
  assert.equal(result.final.captureActive, false);
  assert.equal(result.final.capturedTabId, null);
});
