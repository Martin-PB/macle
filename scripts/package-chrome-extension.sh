#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
EXTENSION_DIR="$ROOT/connectors/google-meet/chrome-extension"
DIST_DIR="$ROOT/dist"
OUTPUT="$DIST_DIR/macle-chrome-extension.zip"

for command in cargo rustup wasm-pack node zip; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "Missing required command: $command" >&2
    exit 127
  }
done

NODE_MAJOR=$(node -p 'Number(process.versions.node.split(".")[0])')
if [ "$NODE_MAJOR" -lt 22 ]; then
  echo "Node.js 22 or newer is required for the WebAssembly smoke test." >&2
  exit 2
fi

# Build and exercise the exact WASM module that the extension loads.
sh "$ROOT/scripts/test-wasm-core.sh"

# Catch syntax errors in every hand-written extension JavaScript entry point.
node --check "$EXTENSION_DIR/service-worker.js"
node --check "$EXTENSION_DIR/offscreen.js"
node --check "$EXTENSION_DIR/options.js"

test -s "$EXTENSION_DIR/core-wasm/macle_core.js"
test -s "$EXTENSION_DIR/core-wasm/macle_core_bg.wasm"

mkdir -p "$DIST_DIR"
rm -f "$OUTPUT"
(
  cd "$EXTENSION_DIR"
  zip -qr "$OUTPUT" .
)

echo "Chrome extension package created: $OUTPUT"
echo "Load the unpacked directory at chrome://extensions, or extract the ZIP and load it."
