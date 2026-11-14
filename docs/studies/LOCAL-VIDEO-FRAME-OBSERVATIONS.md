# Local video frame observations

**Status:** first optional visual extraction from the single-device Google Meet capture; not a vision-understanding system.

## Purpose

The Chrome connector records the rendered Meet tab as a composite video. Sparse frame extraction makes selected visual states addressable by time and hash without retaining a second continuous video representation or pretending to expose participant-specific video tracks.

## Implementation

The `macle-meet transcribe` command also samples a frame every 30 seconds by default:
- PyAV decodes the local WebM video stream.
- A sampled frame is converted to JPEG and saved under the local MACLE data directory.
- The frame is resized to a maximum dimension of 1280 pixels by default.
- JPEG quality defaults to 85.
- Each frame is SHA-256 hashed and referenced by a `video_frame` MACLE observation.
- The observation retains the source media hash, capture ID, frame index, relative timestamp, derived absolute timestamp (when the capture manifest provides a valid start time), dimensions and local file path.
- Frame bytes are not embedded in SQLite/JSONL.
- File permissions are owner-only on POSIX systems.

Sampling can be disabled with `--frame-interval 0`, or adjusted with `--frame-interval`, `--max-frame-dimension`, `--jpeg-quality` and `--frames-dir`.

PyAV exposes frame decoding, timestamps and JPEG frame saving through its Python API. The local frame adapter uses these capabilities directly; it does not invoke a hosted vision service.

## Semantics and limits

A frame sample is a visual observation at a point in the composite tab recording. It is not:
- continuous video evidence;
- an individual participant camera stream;
- proof that every participant or event was visible;
- a semantic interpretation of what the frame depicts.

No face recognition, identity inference, emotion inference, object recognition or activity classification is performed. Future visual interpretation would need its own model provenance, confidence, uncertainty, validation and authorization boundary.

## References

- PyAV documentation, including frame decoding and saving: https://pyav.org/docs/stable/ — retrieved 2026-11-14.
- PyAV frame API: https://pyav.org/docs/stable/api/video.html — retrieved 2026-11-14.
- PyAV time and timestamp model: https://pyav.org/docs/stable/api/time.html — retrieved 2026-11-14.
