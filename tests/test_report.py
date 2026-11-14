import hashlib
import json
from pathlib import Path

from macle_meet.report import generate_report


def _write_jsonl(path: Path, observations):
    path.write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in observations),
        encoding="utf-8",
    )


def test_report_escapes_untrusted_transcript_text_and_has_no_remote_dependencies(tmp_path):
    export = tmp_path / "observations.jsonl"
    output = tmp_path / "report.html"
    hostile = '<script>alert("xss")</script>'
    _write_jsonl(export, [{
        "id": "segment-1",
        "modality": "speech_transcription",
        "content": hostile,
        "observedAt": "2026-11-14T10:00:00Z",
        "source": {"resourceType": "local_asr_segment", "resourceName": "capture-1"},
        "payload": {
            "startSeconds": 0.0,
            "endSeconds": 1.0,
            "asr": {"model": "small", "language": "fr"},
        },
    }])

    summary = generate_report(export, output, frames_root=tmp_path / "frames")
    document = output.read_text(encoding="utf-8")
    assert summary["transcriptSegments"] == 1
    assert "&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;" in document
    assert "<script>alert(" not in document
    assert "https://" not in document
    assert output.stat().st_mode & 0o777 == 0o600


def test_report_copies_verified_frame_asset_under_relative_path(tmp_path):
    frames_root = tmp_path / "frames"
    frames_root.mkdir()
    frame_path = frames_root / "frame.jpg"
    frame_path.write_bytes(b"synthetic-jpeg")
    digest = hashlib.sha256(frame_path.read_bytes()).hexdigest()
    export = tmp_path / "observations.jsonl"
    output = tmp_path / "report.html"
    _write_jsonl(export, [{
        "id": "frame-1",
        "modality": "video_frame",
        "observedAt": "2026-11-14T10:00:00Z",
        "source": {"resourceType": "video_frame_sample", "resourceName": "capture-1"},
        "payload": {
            "startSeconds": 12.0,
            "frame": {
                "path": str(frame_path),
                "sha256": digest,
                "width": 1280,
                "height": 720,
            },
        },
    }])

    summary = generate_report(export, output, frames_root=frames_root)
    asset = tmp_path / "report_assets" / "frames" / f"{digest}.jpg"
    document = output.read_text(encoding="utf-8")
    assert summary["frames"] == 1
    assert asset.is_file()
    assert asset.read_bytes() == frame_path.read_bytes()
    assert f'report_assets/frames/{digest}.jpg' in document
    assert asset.stat().st_mode & 0o777 == 0o600


def test_report_refuses_frame_paths_outside_configured_root(tmp_path):
    frames_root = tmp_path / "approved-frames"
    frames_root.mkdir()
    outside = tmp_path / "outside.jpg"
    outside.write_bytes(b"not-approved")
    digest = hashlib.sha256(outside.read_bytes()).hexdigest()
    export = tmp_path / "observations.jsonl"
    output = tmp_path / "report.html"
    _write_jsonl(export, [{
        "id": "frame-outside",
        "modality": "video_frame",
        "source": {"resourceType": "video_frame_sample"},
        "payload": {"frame": {"path": str(outside), "sha256": digest}},
    }])

    generate_report(export, output, frames_root=frames_root)
    document = output.read_text(encoding="utf-8")
    assert "outside the configured frames root" in document
    assert not (tmp_path / "report_assets").exists()


def test_report_refuses_frame_hash_mismatch(tmp_path):
    frames_root = tmp_path / "frames"
    frames_root.mkdir()
    frame_path = frames_root / "frame.jpg"
    frame_path.write_bytes(b"actual")
    export = tmp_path / "observations.jsonl"
    output = tmp_path / "report.html"
    _write_jsonl(export, [{
        "id": "frame-mismatch",
        "modality": "video_frame",
        "source": {"resourceType": "video_frame_sample"},
        "payload": {"frame": {"path": str(frame_path), "sha256": "0" * 64}},
    }])

    generate_report(export, output, frames_root=frames_root)
    document = output.read_text(encoding="utf-8")
    assert "SHA-256 does not match" in document
    assert not (tmp_path / "report_assets").exists()
