#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
command -v wasm-pack >/dev/null 2>&1 || {
  echo "wasm-pack is required (install it separately)." >&2
  exit 127
}
rustup target add wasm32-unknown-unknown
wasm-pack build "$ROOT/core/macle-core" --target web --out-dir "$ROOT/connectors/google-meet/chrome-extension/core-wasm"
