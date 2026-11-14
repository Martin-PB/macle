"""Local SQLite store; no remote persistence or telemetry."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from .normalize import normalize_resource


class LocalStore:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.db = sqlite3.connect(path)
        path.chmod(0o600)
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS source_resources (
                resource_name TEXT NOT NULL,
                payload_sha256 TEXT NOT NULL,
                conference_name TEXT NOT NULL,
                retrieved_at TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                PRIMARY KEY(resource_name, payload_sha256)
            )"""
        )
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS observations (
                observation_id TEXT PRIMARY KEY,
                conference_name TEXT NOT NULL,
                observation_json TEXT NOT NULL
            )"""
        )
        self.db.commit()

    def add(self, resources: list[dict[str, Any]], *, conference_name: str) -> int:
        inserted = 0
        for resource in resources:
            name = resource.get("name", "")
            raw = json.dumps(resource, sort_keys=True, ensure_ascii=False)
            digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            observation = normalize_resource(resource, conference_name=conference_name)
            cursor = self.db.execute(
                """INSERT OR IGNORE INTO source_resources
                   (resource_name, payload_sha256, conference_name, retrieved_at, payload_json)
                   VALUES (?, ?, ?, ?, ?)""",
                (name, digest, conference_name, observation["retrievedAt"], raw),
            )
            if cursor.rowcount:
                inserted += 1
            self.db.execute(
                """INSERT OR IGNORE INTO observations
                   (observation_id, conference_name, observation_json)
                   VALUES (?, ?, ?)""",
                (
                    observation["id"],
                    conference_name,
                    json.dumps(observation, sort_keys=True, ensure_ascii=False),
                ),
            )
        self.db.commit()
        return inserted

    def add_observation(self, observation: dict[str, Any], *, conference_name: str = "") -> None:
        self.db.execute(
            """INSERT OR IGNORE INTO observations
               (observation_id, conference_name, observation_json)
               VALUES (?, ?, ?)""",
            (
                observation["id"],
                conference_name,
                json.dumps(observation, sort_keys=True, ensure_ascii=False),
            ),
        )
        self.db.commit()

    def export_jsonl(self, destination: Path) -> int:
        destination.parent.mkdir(parents=True, exist_ok=True)
        rows = self.db.execute(
            "SELECT observation_json FROM observations ORDER BY conference_name, observation_id"
        )
        count = 0
        with destination.open("w", encoding="utf-8") as output:
            for (payload,) in rows:
                output.write(payload + "\n")
                count += 1
        destination.chmod(0o600)
        return count

    def close(self) -> None:
        self.db.close()
