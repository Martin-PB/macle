"""Loss-preserving mapping from Google resources to MACLE observations."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


def _stable_id(value: dict[str, Any]) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def sanitize_space_resource(resource: dict[str, Any]) -> dict[str, Any]:
    """Drop short-lived meeting codes and URIs before persisting a space snapshot."""
    return {
        key: value
        for key, value in resource.items()
        if key not in {"meetingCode", "meetingUri"}
    }


def normalize_resource(
    resource: dict[str, Any],
    *,
    conference_name: str,
    retrieved_at: str | None = None,
) -> dict[str, Any]:
    name = resource.get("name", "")
    leaf = name.rsplit("/", 1)[-1] if name else "unknown"
    if name.startswith("spaces/"):
        kind, modality = "meeting_space", "metadata"
    elif "/transcripts/" in name and "/entries/" in name:
        kind, modality = "transcript_entry", "text"
    elif "/participantSessions/" in name:
        kind, modality = "participant_session", "metadata"
    elif "/participants/" in name:
        kind, modality = "participant", "metadata"
    elif "/recordings/" in name:
        kind, modality = "recording", "media_artifact_reference"
    elif "/transcripts/" in name:
        kind, modality = "transcript", "text_artifact_reference"
    elif "/smartNotes/" in name:
        kind, modality = "smart_notes", "text_artifact_reference"
    else:
        kind, modality = "conference", "metadata"

    now = retrieved_at or datetime.now(timezone.utc).isoformat()
    source_time = (
        resource.get("startTime")
        or resource.get("earliestStartTime")
        or resource.get("createTime")
        or resource.get("endTime")
    )
    observation = {
        "id": _stable_id(resource),
        "schema": "macle.observation/v0",
        "observedAt": source_time,
        "retrievedAt": now,
        "source": {
            "platform": "google_meet",
            "resourceName": name,
            "resourceType": kind,
            "conferenceRecord": conference_name,
            "deviceBoundary": "single_local_device",
        },
        "modality": modality,
        "subject": {
            "participant": resource.get("participant"),
            "participantSession": name if kind == "participant_session" else None,
        },
        "content": resource.get("text") if kind == "transcript_entry" else None,
        "payload": resource,
        "limitations": [
            "Google Meet REST resource; not a raw audio/video observation.",
            "Source timestamps are preserved as supplied and are not inferred to be local capture-clock timestamps.",
        ],
    }
    return observation


def normalize_resources(
    resources: list[dict[str, Any]], *, conference_name: str
) -> list[dict[str, Any]]:
    return [
        normalize_resource(resource, conference_name=conference_name)
        for resource in resources
    ]
