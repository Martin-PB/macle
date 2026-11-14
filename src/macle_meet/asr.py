"""Local speech transcription adapter; audio never leaves this process/device."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def transcribe_file(
    media_path: Path,
    *,
    model_name: str = "small",
    language: str | None = None,
    device: str = "cpu",
    compute_type: str | None = None,
    model_cache: Path | None = None,
    cpu_threads: int = 8,
    beam_size: int = 5,
    manifest: dict[str, Any] | None = None,
    model_factory: Callable[..., Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Transcribe a local audio/video file and return MACLE segment observations.

    The injected model_factory is for deterministic tests. Production use lazily
    imports faster-whisper and downloads model weights only when first required.
    """
    if not media_path.is_file():
        raise FileNotFoundError(f"Media file not found: {media_path}")
    if device not in {"cpu", "cuda"}:
        raise ValueError("device must be 'cpu' or 'cuda'")
    effective_compute = compute_type or ("int8" if device == "cpu" else "float16")

    if model_factory is None:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(
                "Local ASR is not installed. Reinstall MACLE with: "
                "python -m pip install -e '.[asr]'"
            ) from exc
        model_factory = WhisperModel

    model_kwargs: dict[str, Any] = {
        "device": device,
        "compute_type": effective_compute,
    }
    if device == "cpu":
        model_kwargs["cpu_threads"] = max(1, cpu_threads)
    if model_cache is not None:
        model_cache.mkdir(parents=True, exist_ok=True, mode=0o700)
        model_kwargs["download_root"] = str(model_cache)

    model = model_factory(model_name, **model_kwargs)
    segments, info = model.transcribe(
        str(media_path),
        language=language,
        beam_size=beam_size,
        vad_filter=True,
    )

    media_hash = _sha256(media_path)
    capture_id = (manifest or {}).get("captureId")
    capture_started = (manifest or {}).get("startedAt")
    observations: list[dict[str, Any]] = []
    absolute_start = None
    if capture_started:
        try:
            absolute_start = datetime.fromisoformat(capture_started.replace("Z", "+00:00"))
        except ValueError:
            absolute_start = None

    detected_language = getattr(info, "language", None)
    language_probability = getattr(info, "language_probability", None)
    for index, segment in enumerate(segments):
        text = str(getattr(segment, "text", "")).strip()
        if not text:
            continue
        start = float(segment.start)
        end = float(segment.end)
        observed_at = None
        if absolute_start is not None:
            observed_at = (absolute_start + timedelta(seconds=start)).isoformat()
        payload = {
            "captureId": capture_id,
            "media": {
                "sha256": media_hash,
                "sizeBytes": media_path.stat().st_size,
            },
            "segmentIndex": index,
            "startSeconds": start,
            "endSeconds": end,
            "text": text,
            "asr": {
                "engine": "faster-whisper",
                "model": model_name,
                "device": device,
                "computeType": effective_compute,
                "language": detected_language,
                "languageProbability": language_probability,
                "averageLogProbability": getattr(segment, "avg_logprob", None),
                "noSpeechProbability": getattr(segment, "no_speech_prob", None),
            },
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        observation_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        observations.append({
            "id": observation_id,
            "schema": "macle.observation/v0",
            "observedAt": observed_at,
            "retrievedAt": datetime.now().astimezone().isoformat(),
            "source": {
                "platform": "google_meet",
                "resourceName": capture_id or media_path.name,
                "resourceType": "local_asr_segment",
                "captureId": capture_id,
                "mediaSha256": media_hash,
                "deviceBoundary": "single_local_device",
            },
            "modality": "speech_transcription",
            "subject": {
                "participant": None,
                "participantSession": None,
                "speakerAttribution": "not_established_from_composite_audio",
            },
            "content": text,
            "payload": payload,
            "limitations": [
                "Machine-generated local ASR; not a verbatim or independently verified transcript.",
                "Segment offsets are relative to the local capture file.",
                "Composite tab audio does not support reliable participant identity attribution.",
                "No audio or transcript content is sent to a hosted transcription service.",
            ],
        })

    summary = {
        "mediaSha256": media_hash,
        "captureId": capture_id,
        "model": model_name,
        "device": device,
        "computeType": effective_compute,
        "language": detected_language,
        "languageProbability": language_probability,
        "segments": len(observations),
    }
    return observations, summary
