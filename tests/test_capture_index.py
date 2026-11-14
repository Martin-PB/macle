import json
from argparse import Namespace

import pytest

from macle_meet.cli import run_index_capture


def test_index_capture_requires_synthetic_attestation(tmp_path):
    manifest = tmp_path / "capture.json"
    media = tmp_path / "capture.webm"
    manifest.write_text(json.dumps({
        "schema": "macle.capture-manifest/v0",
        "captureId": "synthetic-capture",
        "syntheticTestAttested": False,
    }))
    media.write_bytes(b"synthetic-media")
    args = Namespace(
        manifest=manifest,
        media=media,
        conference_record=None,
        database=tmp_path / "macle.sqlite3",
        export=tmp_path / "observations.jsonl",
    )
    with pytest.raises(RuntimeError, match="synthetic-only attestation"):
        run_index_capture(args)


def test_index_capture_records_optional_microphone_and_conference(tmp_path):
    manifest = tmp_path / "capture.manifest.json"
    media = tmp_path / "capture.webm"
    manifest.write_text(json.dumps({
        "schema": "macle.capture-manifest/v0",
        "captureId": "synthetic-capture-with-mic",
        "startedAt": "2026-11-14T10:00:00Z",
        "endedAt": "2026-11-14T10:05:00Z",
        "syntheticTestAttested": True,
        "microphoneCaptured": True,
        "microphoneSyntheticAttested": True,
    }))
    media.write_bytes(b"synthetic-media")
    export = tmp_path / "observations.jsonl"
    args = Namespace(
        manifest=manifest,
        media=media,
        conference_record="conferenceRecords/c1",
        database=tmp_path / "macle.sqlite3",
        export=export,
    )
    assert run_index_capture(args) == 0
    row = json.loads(export.read_text().splitlines()[0])
    assert row["source"]["conferenceRecord"] == "conferenceRecords/c1"
    assert "Local microphone was mixed with tab audio." in row["limitations"]
    assert row["payload"]["media"]["sha256"]


def test_index_capture_rejects_unattested_microphone_audio(tmp_path):
    manifest = tmp_path / "capture.manifest.json"
    media = tmp_path / "capture.webm"
    manifest.write_text(json.dumps({
        "schema": "macle.capture-manifest/v0",
        "captureId": "capture-with-unattested-mic",
        "syntheticTestAttested": True,
        "microphoneCaptured": True,
        "microphoneSyntheticAttested": False,
    }))
    media.write_bytes(b"synthetic-media")
    args = Namespace(
        manifest=manifest,
        media=media,
        conference_record=None,
        database=tmp_path / "macle.sqlite3",
        export=tmp_path / "observations.jsonl",
    )
    with pytest.raises(RuntimeError, match="microphone audio"):
        run_index_capture(args)
