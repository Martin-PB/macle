"""Sparse local video-frame observations from a captured Meet tab."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sample_video_frames(
    media_path: Path,
    output_dir: Path,
    *,
    interval_seconds: float = 30.0,
    max_dimension: int = 1280,
    jpeg_quality: int = 85,
    manifest: dict[str, Any] | None = None,
    container_factory: Callable[..., Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Extract sparse local JPEG frames and return MACLE visual observations."""
    if not media_path.is_file():
        raise FileNotFoundError(f"Media file not found: {media_path}")
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be positive")
    if max_dimension < 64:
        raise ValueError("max_dimension must be at least 64")
    if not 1 <= jpeg_quality <= 100:
        raise ValueError("jpeg_quality must be between 1 and 100")

    if container_factory is None:
        try:
            import av
        except ImportError as exc:
            raise RuntimeError(
                "Local video frame extraction requires PyAV. "
                "Install the local media extra with: python -m pip install -e '.[asr]'"
            ) from exc
        container_factory = av.open

    output_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    media_hash = _sha256(media_path)
    capture_id = (manifest or {}).get("captureId")
    capture_started = (manifest or {}).get("startedAt")
    absolute_start = None
    if capture_started:
        try:
            absolute_start = datetime.fromisoformat(capture_started.replace("Z", "+00:00"))
        except ValueError:
            absolute_start = None

    container = container_factory(str(media_path))
    observations: list[dict[str, Any]] = []
    first_timestamp: float | None = None
    next_sample = 0.0
    try:
        for frame in container.decode(video=0):
            timestamp = getattr(frame, "time", None)
            if timestamp is None:
                pts = getattr(frame, "pts", None)
                time_base = getattr(frame, "time_base", None)
                if pts is None or time_base is None:
                    continue
                timestamp = float(pts * time_base)
            timestamp = float(timestamp)
            if first_timestamp is None:
                first_timestamp = timestamp
            relative_seconds = max(0.0, timestamp - first_timestamp)
            if relative_seconds + 1e-6 < next_sample:
                continue

            width = int(frame.width)
            height = int(frame.height)
            scale = min(1.0, max_dimension / max(width, height))
            if scale < 1.0:
                frame = frame.reformat(
                    width=max(1, round(width * scale)),
                    height=max(1, round(height * scale)),
                )
                width = int(frame.width)
                height = int(frame.height)

            frame_index = len(observations)
            filename = (
                f"{media_hash[:12]}-{frame_index:06d}-"
                f"{int(relative_seconds * 1000):012d}.jpg"
            )
            frame_path = output_dir / filename
            frame.save(str(frame_path), quality=jpeg_quality)
            frame_path.chmod(0o600)
            frame_hash = _sha256(frame_path)
            observed_at = None
            if absolute_start is not None:
                observed_at = (
                    absolute_start + timedelta(seconds=relative_seconds)
                ).isoformat()
            payload = {
                "captureId": capture_id,
                "media": {
                    "sha256": media_hash,
                    "sizeBytes": media_path.stat().st_size,
                },
                "frame": {
                    "path": str(frame_path.resolve()),
                    "sha256": frame_hash,
                    "sizeBytes": frame_path.stat().st_size,
                    "width": width,
                    "height": height,
                    "format": "image/jpeg",
                },
                "frameIndex": frame_index,
                "startSeconds": relative_seconds,
                "samplingIntervalSeconds": interval_seconds,
                "jpegQuality": jpeg_quality,
            }
            canonical = json.dumps(
                payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            )
            observation_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            observations.append({
                "id": observation_id,
                "schema": "macle.observation/v0",
                "observedAt": observed_at,
                "retrievedAt": datetime.now(timezone.utc).isoformat(),
                "source": {
                    "platform": "google_meet",
                    "resourceName": capture_id or media_path.name,
                    "resourceType": "video_frame_sample",
                    "captureId": capture_id,
                    "mediaSha256": media_hash,
                    "frameSha256": frame_hash,
                    "deviceBoundary": "single_local_device",
                },
                "modality": "video_frame",
                "subject": {
                    "participant": None,
                    "speakerAttribution": "not_established",
                },
                "content": None,
                "payload": payload,
                "limitations": [
                    "Sparse frame sample from the rendered tab, not continuous video evidence.",
                    "The frame is from a composite tab recording, not an individual participant track.",
                    "No face recognition, identity inference, emotion inference or semantic interpretation is performed.",
                ],
            })
            next_sample = relative_seconds + interval_seconds
    finally:
        container.close()

    return observations, {
        "mediaSha256": media_hash,
        "captureId": capture_id,
        "frames": len(observations),
        "intervalSeconds": interval_seconds,
        "outputDirectory": str(output_dir.resolve()),
    }
