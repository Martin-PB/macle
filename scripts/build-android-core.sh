#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
command -v cargo-ndk >/dev/null 2>&1 || {
  echo "cargo-ndk is required (install it separately with: cargo install cargo-ndk)." >&2
  exit 127
}
rustup target add aarch64-linux-android
cargo ndk -t arm64-v8a -o "$ROOT/apps/android/app/src/main/jniLibs" \
  build --release --manifest-path "$ROOT/core/macle-core/Cargo.toml"
