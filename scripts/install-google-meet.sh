#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required (Python 3.11 or newer)." >&2
  exit 1
fi

python3 - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11 or newer is required.")
print(f"Using Python {sys.version.split()[0]}")
PY

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .

install -d -m 700 "${XDG_CONFIG_HOME:-$HOME/.config}/macle-meet"
install -d -m 700 "${XDG_DATA_HOME:-$HOME/.local/share}/macle-meet"

echo
echo "MACLE Google Meet local client installed in: $ROOT_DIR/.venv"
echo
echo "Next steps:"
echo "  1. Create a Google Cloud OAuth Desktop client and enable the Google Meet REST API."
echo "  2. Save its client JSON to:"
echo "     ${XDG_CONFIG_HOME:-$HOME/.config}/macle-meet/client_secret.json"
echo "  3. Restrict that file: chmod 600 \"${XDG_CONFIG_HOME:-$HOME/.config}/macle-meet/client_secret.json\""
echo "  4. Authenticate: .venv/bin/macle-meet auth"
echo "  5. Load the unpacked Chrome extension from:"
echo "     $ROOT_DIR/connectors/google-meet/chrome-extension"
echo
echo "The current approval permits synthetic test meetings only."
