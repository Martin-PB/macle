#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/macle"
JAR="${TLA2TOOLS_JAR:-$CACHE_DIR/tla2tools-1.7.4.jar}"
EXPECTED_SHA1="bee4a54f3ee3d4afc347c3240ec2d9e93b075104"
EXPECTED_SHA256="936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88"
URL="https://github.com/tlaplus/tlaplus/releases/download/v1.7.4/tla2tools.jar"

mkdir -p "$(dirname "$JAR")"
if [[ ! -f "$JAR" ]]; then
  command -v curl >/dev/null || { echo "curl is required to bootstrap TLC." >&2; exit 2; }
  tmp="${JAR}.download"
  trap 'rm -f "$tmp"' EXIT
  curl --fail --location --retry 3 "$URL" --output "$tmp"
  echo "$EXPECTED_SHA1  $tmp" | sha1sum --check --status || {
    echo "TLC 1.7.4 SHA-1 mismatch; refusing to execute the downloaded verifier." >&2
    exit 3
  }
  echo "$EXPECTED_SHA256  $tmp" | sha256sum --check --status || {
    echo "TLC 1.7.4 SHA-256 mismatch; refusing to execute the downloaded verifier." >&2
    exit 4
  }
  mv "$tmp" "$JAR"
  trap - EXIT
fi

echo "$EXPECTED_SHA1  $JAR" | sha1sum --check
echo "$EXPECTED_SHA256  $JAR" | sha256sum --check
for model in CaptureLifecycle ExportRecovery; do
  echo "Checking $model with TLC 1.7.4..."
  java -XX:+UseParallelGC -Xmx2g -jar "$JAR" \
    -workers 1 \
    -config "$ROOT/formal/chrome-capture/$model.cfg" \
    "$ROOT/formal/chrome-capture/$model.tla"
done
