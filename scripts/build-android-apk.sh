#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DIST_DIR="$ROOT/dist"
APK_SOURCE="$ROOT/apps/android/app/build/outputs/apk/debug/app-debug.apk"
APK_OUTPUT="$DIST_DIR/MACLE-android-debug.apk"

for command in cargo rustup cargo-ndk gradle java; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "Missing required command: $command" >&2
    exit 127
  }
done

JAVA_VERSION=$(java -version 2>&1 | awk -F '"' 'NR == 1 { print $2 }')
JAVA_MAJOR=${JAVA_VERSION%%.*}
if [ -z "$JAVA_MAJOR" ] || [ "$JAVA_MAJOR" -lt 17 ]; then
  echo "JDK 17 or newer is required by Android Gradle Plugin 8.7.3." >&2
  exit 2
fi

if [ -z "${ANDROID_HOME:-}${ANDROID_SDK_ROOT:-}" ]; then
  echo "Set ANDROID_HOME or ANDROID_SDK_ROOT to an installed Android SDK." >&2
  exit 2
fi

# Produces the arm64-v8a JNI library consumed by the Android application.
sh "$ROOT/scripts/build-android-core.sh"

# AGP 8.7.3 requires a compatible Gradle 8.9+ installation.
gradle --no-daemon -p "$ROOT/apps/android" :app:assembleDebug

test -s "$APK_SOURCE" || {
  echo "Gradle completed but the expected debug APK was not found: $APK_SOURCE" >&2
  exit 1
}

mkdir -p "$DIST_DIR"
cp "$APK_SOURCE" "$APK_OUTPUT"
echo "Android debug APK created: $APK_OUTPUT"
