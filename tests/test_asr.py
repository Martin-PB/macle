from pathlib import Path
from types import SimpleNamespace

import pytest

from macle_meet.asr import transcribe_file


class FakeModel:
    def __init__(self, model_name, **kwargs):
        self.model_name = model_name
        self.kwargs = kwargs
        self.transcribe_args = None

    def transcribe(self, media_path, **kwargs):
        self.transcribe_args = kwargs
        segments = [
            SimpleNamespace(
                start=1.25,
                end=3.75,
                text=" Bonjour tout le monde. ",
                avg_logprob=-0.2,
                no_speech_prob=0.01,
            ),
            SimpleNamespace(start=4.0, end=4.5, text="  ", avg_logprob=-0.1, no_speech_prob=0.9),
        ]
        info = SimpleNamespace(language="fr", language_probability=0.98)
        return segments, info


def test_transcribe_file_creates_time_aligned_local_observations(tmp_path):
    media = tmp_path / "capture.webm"
    media.write_bytes(b"synthetic-webm")
    manifest = {
        "captureId": "capture-001",
        "startedAt": "2026-11-14T10:00:00.000Z",
    }
    created = {}

    def factory(model_name, **kwargs):
        model = FakeModel(model_name, **kwargs)
        created["model"] = model
        return model

    observations, summary = transcribe_file(
        media,
        model_name="small",
        language=None,
        device="cpu",
        model_cache=tmp_path / "models",
        manifest=manifest,
        model_factory=factory,
    )

    assert summary["segments"] == 1
    assert summary["language"] == "fr"
    assert created["model"].kwargs["compute_type"] == "int8"
    assert created["model"].transcribe_args["vad_filter"] is True
    observation = observations[0]
    assert observation["content"] == "Bonjour tout le monde."
    assert observation["observedAt"] == "2026-11-14T10:00:01.250000+00:00"
    assert observation["payload"]["startSeconds"] == 1.25
    assert observation["payload"]["endSeconds"] == 3.75
    assert observation["source"]["captureId"] == "capture-001"
    assert observation["subject"]["speakerAttribution"] == "not_established_from_composite_audio"
    assert observation["payload"]["asr"]["languageProbability"] == 0.98


def test_transcribe_file_rejects_missing_media(tmp_path):
    with pytest.raises(FileNotFoundError):
        transcribe_file(tmp_path / "missing.webm", model_factory=FakeModel)


def test_transcribe_file_rejects_unknown_device(tmp_path):
    media = tmp_path / "capture.webm"
    media.write_bytes(b"synthetic")
    with pytest.raises(ValueError, match="device"):
        transcribe_file(media, device="tpu", model_factory=FakeModel)
