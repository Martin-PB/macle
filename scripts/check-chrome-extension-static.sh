#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXT="$ROOT/connectors/google-meet/chrome-extension"

node --check "$EXT/service-worker.js"
node --check "$EXT/offscreen.js"
node --check "$EXT/options.js"
node --test "$ROOT/tests/chrome-capture/offscreen-recovery.test.mjs"
python3 -m json.tool "$EXT/manifest.json" >/dev/null

grep -q 'response?.coreReady' "$EXT/service-worker.js"
grep -q 'message.type === "DOWNLOAD_STATUS"' "$EXT/service-worker.js"
grep -q 'if (starting || saving' "$EXT/offscreen.js"
grep -q 'status.state === "complete"' "$EXT/offscreen.js"
grep -q 'status.state === "interrupted"' "$EXT/offscreen.js"
grep -q 'pendingExport' "$EXT/offscreen.js"
grep -q 'actualSha256 !== pendingExport.sha256' "$EXT/offscreen.js"
grep -q 'if (temporaryFileName)' "$EXT/offscreen.js"
grep -q 'Fail closed: keep captureActive' "$ROOT/connectors/google-meet/chrome-extension/service-worker.js"
grep -q 'sender.url !== chrome.runtime.getURL("offscreen.html")' "$ROOT/connectors/google-meet/chrome-extension/service-worker.js"
grep -q 'async function removeRetainedArtifact' "$EXT/offscreen.js"
grep -q 'pendingExport.mediaComplete && pendingExport.manifestComplete' "$EXT/offscreen.js"
grep -q 'if (state.pendingExport)' "$EXT/service-worker.js"
PENDING_LINE="$(grep -n 'set({ pendingExport: pendingExportRecord })' "$EXT/offscreen.js" | head -n1 | cut -d: -f1)"
VALIDATE_LINE="$(grep -n 'validate_manifest_json(pendingExportRecord.manifestJson)' "$EXT/offscreen.js" | head -n1 | cut -d: -f1)"
[[ "$PENDING_LINE" -lt "$VALIDATE_LINE" ]]
grep -q 'RETRY_PENDING_EXPORT' "$EXT/offscreen.js"
grep -q 'RETRY_PENDING_EXPORT' "$EXT/service-worker.js"
grep -q 'pendingExport' "$EXT/options.js"
grep -q 'retryExport' "$EXT/options.html"

echo "Chrome extension static checks: PASS"
