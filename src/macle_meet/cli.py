"""Command-line interface for the local Google Meet connector."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from google.auth.transport.requests import AuthorizedSession, Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from . import __version__
from .client import MeetApiError, MeetClient
from .asr import transcribe_file
from .store import LocalStore
from .normalize import sanitize_space_resource

SCOPE = "https://www.googleapis.com/auth/meetings.space.readonly"


def config_dir() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "macle-meet"


def data_dir() -> Path:
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "macle-meet"


def cache_dir() -> Path:
    return Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "macle-meet"


def ensure_private_config_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if os.name == "posix":
        path.chmod(0o700)


def authenticate(client_secrets: Path, token_path: Path) -> Credentials:
    if not client_secrets.is_file():
        raise FileNotFoundError(
            f"OAuth client file not found: {client_secrets}\n"
            "Create a Desktop OAuth client in Google Cloud and save its JSON here."
        )
    if token_path.parent == config_dir():
        ensure_private_config_directory(token_path.parent)
    else:
        token_path.parent.mkdir(parents=True, exist_ok=True)
    flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets), [SCOPE])
    credentials = flow.run_local_server(host="127.0.0.1", port=0, open_browser=True)
    token_path.write_text(credentials.to_json(), encoding="utf-8")
    token_path.chmod(0o600)
    return credentials


def load_credentials(token_path: Path) -> Credentials:
    if token_path.parent == config_dir():
        ensure_private_config_directory(token_path.parent)
    if not token_path.exists():
        raise FileNotFoundError("Not authenticated. Run: macle-meet auth")
    credentials = Credentials.from_authorized_user_file(str(token_path), [SCOPE])
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        token_path.write_text(credentials.to_json(), encoding="utf-8")
        token_path.chmod(0o600)
    if not credentials.valid:
        raise RuntimeError("Google credentials are invalid. Run: macle-meet auth")
    return credentials


def run_sync(args: argparse.Namespace) -> int:
    credentials = load_credentials(args.token_file)
    client = MeetClient(AuthorizedSession(credentials))
    since = None
    if args.days is not None:
        since = (datetime.now(timezone.utc) - timedelta(days=args.days)).isoformat()
    space_resource = None
    if args.meeting_code or args.space:
        space_name = args.space or f"spaces/{args.meeting_code}"
        space_resource = client.get_space(space_name)
        active = space_resource.get("activeConference") or {}
        conference_name = active.get("conferenceRecord")
        if not conference_name:
            raise RuntimeError(
                f"No active conference was found in {space_name}. "
                "Use --conference-record with a known past conference resource."
            )
        conferences = [client.get(conference_name)]
    else:
        conferences = client.list_conferences(
            since=since, conference_name=args.conference_record
        )
    if space_resource and space_resource.get("name"):
        print(f"Resolved meeting space: {space_resource['name']}")
    store = LocalStore(args.database)
    total = 0
    try:
        for conference in conferences:
            name = conference["name"]
            resources = client.collect_conference(conference)
            if space_resource and space_resource.get("name"):
                resources.insert(0, sanitize_space_resource(space_resource))
            inserted = store.add(resources, conference_name=name)
            total += inserted
            print(f"{name}: {len(resources)} resources fetched, {inserted} new.")
        exported = store.export_jsonl(args.export)
    finally:
        store.close()
    print(
        f"Done: {len(conferences)} conferences, {total} new source revisions, "
        f"{exported} observations exported to {args.export}"
    )
    return 0


def run_index_capture(args: argparse.Namespace) -> int:
    if not args.manifest.is_file() or not args.media.is_file():
        raise FileNotFoundError("Both --manifest and --media files must exist.")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("schema") != "macle.capture-manifest/v0" or not manifest.get("captureId"):
        raise RuntimeError("Unsupported or incomplete MACLE capture manifest.")
    if manifest.get("syntheticTestAttested") is not True:
        raise RuntimeError("Refusing to index a capture without the synthetic-only attestation.")
    if manifest.get("microphoneCaptured") and manifest.get("microphoneSyntheticAttested") is not True:
        raise RuntimeError("Refusing to index microphone audio without a synthetic-input attestation.")
    digest = hashlib.sha256()
    with args.media.open("rb") as media_file:
        for chunk in iter(lambda: media_file.read(1024 * 1024), b""):
            digest.update(chunk)
    media_path = args.media.resolve()
    observation_payload = {
        "captureManifest": manifest,
        "media": {
            "path": str(media_path),
            "sha256": digest.hexdigest(),
            "sizeBytes": media_path.stat().st_size,
        },
    }
    canonical = json.dumps(
        observation_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    observation_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    conference_name = args.conference_record or ""
    observation = {
        "id": observation_id,
        "schema": "macle.observation/v0",
        "observedAt": manifest.get("startedAt"),
        "retrievedAt": datetime.now(timezone.utc).isoformat(),
        "source": {
            "platform": "google_meet",
            "resourceName": manifest.get("captureId"),
            "resourceType": "local_capture",
            "conferenceRecord": conference_name or None,
            "deviceBoundary": "single_local_device",
        },
        "modality": "audio_video_composite",
        "content": None,
        "payload": observation_payload,
        "limitations": [
            "Composite recording of the rendered Meet tab, not individual participant tracks.",
            (
                "Local microphone was mixed with tab audio."
                if manifest.get("microphoneCaptured")
                else "Local microphone was not captured."
            ),
            "Local media file remains outside the observation JSON; only path, hash, size and capture manifest are indexed.",
        ],
    }
    store = LocalStore(args.database)
    try:
        store.add_observation(observation, conference_name=conference_name)
        count = store.export_jsonl(args.export)
    finally:
        store.close()
    print(f"Indexed local capture {manifest.get('captureId')} ({digest.hexdigest()[:12]}…).")
    print(f"Exported {count} observations to {args.export}")
    return 0


def run_transcribe(args: argparse.Namespace) -> int:
    if not args.manifest.is_file():
        raise FileNotFoundError(f"Capture manifest not found: {args.manifest}")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("schema") != "macle.capture-manifest/v0" or not manifest.get("captureId"):
        raise RuntimeError("Unsupported or incomplete MACLE capture manifest.")
    if manifest.get("syntheticTestAttested") is not True:
        raise RuntimeError("Refusing to transcribe a capture without the synthetic-only attestation.")
    if manifest.get("microphoneCaptured") and manifest.get("microphoneSyntheticAttested") is not True:
        raise RuntimeError("Refusing to transcribe microphone audio without a synthetic-input attestation.")
    capture_args = argparse.Namespace(
        manifest=args.manifest,
        media=args.media,
        conference_record=args.conference_record,
        database=args.database,
        export=args.export,
    )
    run_index_capture(capture_args)
    observations, summary = transcribe_file(
        args.media,
        model_name=args.model,
        language=args.language,
        device=args.device,
        compute_type=args.compute_type,
        model_cache=args.model_cache,
        cpu_threads=args.cpu_threads,
        beam_size=args.beam_size,
        manifest=manifest,
        conference_name=args.conference_record,
    )
    store = LocalStore(args.database)
    try:
        for observation in observations:
            store.add_observation(observation, conference_name=args.conference_record or "")
        exported = store.export_jsonl(args.export)
    finally:
        store.close()
    print(
        f"Transcribed {summary['segments']} segments using {summary['model']} "
        f"({summary['device']}/{summary['computeType']}, "
        f"language={summary['language'] or 'unknown'})."
    )
    print(f"Media SHA-256: {summary['mediaSha256']}")
    print(f"Exported {exported} observations to {args.export}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="macle-meet",
        description="Local, single-device Google Meet connector for MACLE.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    auth = sub.add_parser("auth", help="Authorize this local installation with Google.")
    auth.add_argument("--client-secrets", type=Path, default=config_dir() / "client_secret.json")
    auth.add_argument("--token-file", type=Path, default=config_dir() / "token.json")

    sync = sub.add_parser("sync", help="Fetch conferences and available artifacts.")
    sync.add_argument("--days", type=int, default=30, help="Look back this many days (default: 30).")
    lookup = sync.add_mutually_exclusive_group()
    lookup.add_argument(
        "--conference-record",
        help="Fetch one known conference resource, including a past conference.",
    )
    lookup.add_argument(
        "--meeting-code",
        help="Resolve the active conference from a Google Meet code, e.g. abc-mnop-xyz.",
    )
    lookup.add_argument(
        "--space",
        help="Resolve the active conference from a space resource, e.g. spaces/RESOURCE_ID.",
    )
    sync.add_argument("--token-file", type=Path, default=config_dir() / "token.json")
    sync.add_argument("--database", type=Path, default=data_dir() / "macle.sqlite3")
    sync.add_argument("--export", type=Path, default=Path("macle-meet-observations.jsonl"))
    capture = sub.add_parser("index-capture", help="Index a local Chrome capture and its manifest.")
    capture.add_argument("--manifest", type=Path, required=True)
    capture.add_argument("--media", type=Path, required=True)
    capture.add_argument("--conference-record")
    capture.add_argument("--database", type=Path, default=data_dir() / "macle.sqlite3")
    capture.add_argument("--export", type=Path, default=Path("macle-meet-observations.jsonl"))

    transcribe = sub.add_parser("transcribe", help="Transcribe a local capture using local Whisper ASR.")
    transcribe.add_argument("--media", type=Path, required=True)
    transcribe.add_argument("--manifest", type=Path, required=True)
    transcribe.add_argument("--conference-record", help="Associate the capture and transcript with a Meet conference resource.")
    transcribe.add_argument("--model", default="small", choices=["tiny", "base", "small", "medium", "large-v3", "turbo"])
    transcribe.add_argument("--language", help="Language code such as fr; omit for automatic detection.")
    transcribe.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    transcribe.add_argument("--compute-type", help="Defaults to int8 on CPU and float16 on CUDA.")
    transcribe.add_argument("--cpu-threads", type=int, default=min(os.cpu_count() or 4, 8))
    transcribe.add_argument("--beam-size", type=int, default=5)
    transcribe.add_argument("--model-cache", type=Path, default=cache_dir() / "models")
    transcribe.add_argument("--database", type=Path, default=data_dir() / "macle.sqlite3")
    transcribe.add_argument("--export", type=Path, default=Path("macle-meet-observations.jsonl"))
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "auth":
            authenticate(args.client_secrets, args.token_file)
            print(f"Google authorization stored locally at {args.token_file}")
            return
        if args.command == "sync":
            raise SystemExit(run_sync(args))
        if args.command == "index-capture":
            raise SystemExit(run_index_capture(args))
        if args.command == "transcribe":
            raise SystemExit(run_transcribe(args))
    except (MeetApiError, FileNotFoundError, RuntimeError, requests.RequestException) as exc:
        print(f"macle-meet: error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
