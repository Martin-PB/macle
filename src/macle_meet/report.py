"""Local HTML report generation for MACLE observation JSONL exports."""

from __future__ import annotations

import hashlib
import html
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_observations(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Observation export not found: {path}")
    observations = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at line {line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"Observation at line {line_number} must be a JSON object.")
        observations.append(value)
    return observations


def _e(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _pretty(value: Any) -> str:
    return _e(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _relative_seconds(observation: dict[str, Any]) -> float | None:
    payload = observation.get("payload") or {}
    for key in ("startSeconds",):
        value = payload.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _format_seconds(value: float | None) -> str:
    if value is None:
        return "—"
    minutes, seconds = divmod(max(0, int(value * 1000)), 60_000)
    whole_seconds, millis = divmod(seconds, 1000)
    return f"{minutes:02d}:{whole_seconds:02d}.{millis:03d}"


def _copy_frame_asset(
    observation: dict[str, Any],
    *,
    frames_root: Path,
    assets_frames: Path,
) -> tuple[str | None, str]:
    frame = ((observation.get("payload") or {}).get("frame") or {})
    raw_path = frame.get("path")
    expected_hash = frame.get("sha256")
    if not raw_path or not expected_hash:
        return None, "Frame path or hash is missing."
    source = Path(raw_path).resolve()
    root = frames_root.resolve()
    try:
        source.relative_to(root)
    except ValueError:
        return None, "Frame path is outside the configured frames root."
    if not source.is_file() or source.suffix.lower() not in {".jpg", ".jpeg"}:
        return None, "Frame file is missing or is not a JPEG."
    actual_hash = _sha256(source)
    if actual_hash != expected_hash:
        return None, "Frame SHA-256 does not match its observation."
    assets_frames.mkdir(parents=True, exist_ok=True, mode=0o700)
    target = assets_frames / f"{actual_hash}.jpg"
    if not target.exists():
        shutil.copyfile(source, target)
        target.chmod(0o600)
    return f"{assets_frames.name}/{target.name}", "verified"


def generate_report(
    input_path: Path,
    output_path: Path,
    *,
    frames_root: Path,
) -> dict[str, Any]:
    observations = _read_observations(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    assets_dir = output_path.parent / f"{output_path.stem}_assets"
    assets_frames = assets_dir / "frames"
    frame_assets: dict[str, tuple[str | None, str]] = {}
    for observation in observations:
        if observation.get("modality") == "video_frame":
            frame_assets[observation.get("id", "")] = _copy_frame_asset(
                observation,
                frames_root=frames_root,
                assets_frames=assets_frames,
            )

    modalities = Counter(item.get("modality", "unknown") for item in observations)
    captures = [
        item for item in observations
        if (item.get("source") or {}).get("resourceType") == "local_capture"
    ]
    platform = [
        item for item in observations
        if (item.get("source") or {}).get("resourceType") in {
            "meeting_space", "conference", "participant", "participant_session",
            "recording", "transcript", "transcript_entry", "smart_notes",
        }
    ]
    transcripts = [
        item for item in observations if item.get("modality") == "speech_transcription"
    ]
    frames = [
        item for item in observations if item.get("modality") == "video_frame"
    ]

    def transcript_row(item: dict[str, Any]) -> str:
        payload = item.get("payload") or {}
        asr = payload.get("asr") or {}
        start = payload.get("startSeconds")
        end = payload.get("endSeconds")
        timing = f"{_format_seconds(start)} – {_format_seconds(end)}"
        model = f"{asr.get('model', 'unknown')} / {asr.get('language') or 'unknown'}"
        return (
            "<tr>"
            f"<td>{_e(timing)}</td>"
            f"<td>{_e(item.get('content'))}</td>"
            f"<td>{_e(model)}</td>"
            f"<td><details><summary>Provenance</summary><pre>{_pretty(item.get('source', {}))}</pre></details></td>"
            "</tr>"
        )

    transcript_html = "".join(transcript_row(item) for item in sorted(
        transcripts, key=lambda item: _relative_seconds(item) or 0.0
    )) or '<tr><td colspan="4">No local ASR segments.</td></tr>'

    frame_cards = []
    for item in sorted(frames, key=lambda item: _relative_seconds(item) or 0.0):
        asset, status = frame_assets.get(item.get("id", ""), (None, "not processed"))
        timestamp = _format_seconds(_relative_seconds(item))
        if asset:
            visual = f'<img src="{_e(asset)}" alt="Sampled frame at {_e(timestamp)}" loading="lazy">'
        else:
            visual = f'<p class="missing">{_e(status)}</p>'
        frame_cards.append(
            f'<article class="frame-card">{visual}'
            f'<p><strong>{_e(timestamp)}</strong> · {_e(status)}</p>'
            f'<details><summary>Frame provenance</summary><pre>{_pretty(item.get("payload", {}))}</pre></details>'
            "</article>"
        )
    frames_html = "".join(frame_cards) or "<p>No sampled video frames.</p>"

    def platform_row(item: dict[str, Any]) -> str:
        payload = item.get("payload") or {}
        source = item.get("source") or {}
        resource = source.get("resourceName") or source.get("resourceType") or "resource"
        time_value = item.get("observedAt") or payload.get("startTime") or payload.get("endTime") or "—"
        return (
            "<tr>"
            f"<td>{_e(source.get('resourceType'))}</td>"
            f"<td>{_e(resource)}</td>"
            f"<td>{_e(time_value)}</td>"
            f"<td><details><summary>Payload</summary><pre>{_pretty(payload)}</pre></details></td>"
            "</tr>"
        )

    platform_html = "".join(platform_row(item) for item in platform) or (
        '<tr><td colspan="4">No Meet platform resources.</td></tr>'
    )
    capture_html = "".join(
        f'<li><strong>{_e((item.get("source") or {}).get("resourceName"))}</strong>'
        f'<details><summary>Capture manifest and media hash</summary><pre>{_pretty(item.get("payload", {}))}</pre></details></li>'
        for item in captures
    ) or "<li>No local capture index.</li>"

    summary_items = "".join(
        f"<li><strong>{_e(modality)}</strong>: {_e(count)}</li>"
        for modality, count in sorted(modalities.items())
    )
    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MACLE — Local Google Meet observations</title>
<style>
:root {{ color-scheme: light dark; font-family: system-ui, sans-serif; }}
body {{ max-width: 1100px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }}
h1, h2 {{ line-height: 1.2; }}
.notice {{ border: 1px solid currentColor; border-radius: .5rem; padding: 1rem; }}
table {{ width: 100%; border-collapse: collapse; margin: 1rem 0 2rem; }}
th, td {{ text-align: left; vertical-align: top; border-bottom: 1px solid #8888; padding: .55rem; }}
pre {{ white-space: pre-wrap; overflow-wrap: anywhere; max-width: 100%; }}
.frame-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }}
.frame-card {{ border: 1px solid #8888; border-radius: .5rem; padding: .75rem; min-width: 0; }}
.frame-card img {{ display: block; width: 100%; height: auto; }}
.missing {{ color: #b66; }}
small {{ opacity: .8; }}
</style>
</head>
<body>
<h1>MACLE — Local Google Meet observations</h1>
<p>Generated from <code>{_e(input_path.name)}</code>. This report is local and has no remote scripts, styles, fonts or network dependencies.</p>
<div class="notice">
<strong>Interpretation limits</strong>
<ul>
<li>Local ASR is machine-generated and is not a verified verbatim transcript.</li>
<li>Audio and video come from a composite tab capture, not individual participant media tracks.</li>
<li>Participant resources and participant-session resources are distinct identities.</li>
<li>Frame samples are sparse visual references; no face, identity, emotion or semantic recognition was performed.</li>
<li>Source timestamps, retrieval timestamps and capture-relative offsets must not be conflated.</li>
</ul>
</div>
<h2>Observation inventory</h2>
<ul>{summary_items}</ul>
<h2>Local capture</h2>
<ul>{capture_html}</ul>
<h2>Speech segments</h2>
<table><thead><tr><th>Capture time</th><th>Machine-generated text</th><th>Model / language</th><th>Provenance</th></tr></thead>
<tbody>{transcript_html}</tbody></table>
<h2>Sampled video frames</h2>
<div class="frame-grid">{frames_html}</div>
<h2>Meet platform resources</h2>
<table><thead><tr><th>Resource type</th><th>Resource name</th><th>Source time</th><th>Details</th></tr></thead>
<tbody>{platform_html}</tbody></table>
<footer><small>MACLE local report · {len(observations)} observations · generated without network access.</small></footer>
</body>
</html>
"""
    output_path.write_text(document, encoding="utf-8")
    output_path.chmod(0o600)
    if assets_dir.exists():
        assets_dir.chmod(0o700)
    return {
        "observations": len(observations),
        "captures": len(captures),
        "transcriptSegments": len(transcripts),
        "frames": len(frames),
        "platformResources": len(platform),
        "report": str(output_path.resolve()),
        "assets": str(assets_dir.resolve()) if assets_dir.exists() else None,
    }
