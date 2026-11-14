from pathlib import Path
import stat

import pytest

from macle_meet.frames import sample_video_frames


class FakeFrame:
    def __init__(self, timestamp, width=1920, height=1080):
        self.time = timestamp
        self.width = width
        self.height = height

    def reformat(self, width, height):
        return FakeFrame(self.time, width, height)

    def save(self, path, quality=85):
        Path(path).write_bytes(f"jpeg:{self.time}:{quality}".encode())


class FakeContainer:
    def __init__(self, frames):
        self.frames = frames
        self.closed = False

    def decode(self, video=0):
        assert video == 0
        return iter(self.frames)

    def close(self):
        self.closed = True


def test_sample_video_frames_creates_sparse_time_aligned_observations(tmp_path):
    media = tmp_path / "capture.webm"
    media.write_bytes(b"synthetic-video")
    container = FakeContainer([
        FakeFrame(10.0),
        FakeFrame(10.5),
        FakeFrame(11.0),
        FakeFrame(12.0),
        FakeFrame(13.0),
    ])

    observations, summary = sample_video_frames(
        media,
        tmp_path / "frames",
        interval_seconds=1.0,
        max_dimension=1280,
        manifest={
            "captureId": "capture-frames-1",
            "startedAt": "2026-11-14T10:00:00.000Z",
        },
        container_factory=lambda path: container,
    )

    assert summary["frames"] == 4
    assert len(observations) == 4
    assert container.closed is True
    first = observations[0]
    assert first["modality"] == "video_frame"
    assert first["observedAt"] == "2026-11-14T10:00:00+00:00"
    assert first["payload"]["startSeconds"] == 0.0
    assert first["payload"]["frame"]["width"] == 1280
    assert first["payload"]["frame"]["height"] == 720
    assert first["source"]["captureId"] == "capture-frames-1"
    assert first["payload"]["frame"]["sha256"]
    frame_path = Path(first["payload"]["frame"]["path"])
    assert frame_path.is_file()
    assert stat.S_IMODE(frame_path.stat().st_mode) == 0o600


def test_sample_video_frames_rejects_invalid_interval(tmp_path):
    media = tmp_path / "capture.webm"
    media.write_bytes(b"synthetic")
    with pytest.raises(ValueError, match="interval_seconds"):
        sample_video_frames(
            media,
            tmp_path / "frames",
            interval_seconds=0,
            container_factory=lambda path: FakeContainer([]),
        )
