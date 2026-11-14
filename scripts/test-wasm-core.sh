#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
sh "$ROOT/scripts/build-wasm-core.sh"
node "$ROOT/scripts/test-wasm-core.mjs"
