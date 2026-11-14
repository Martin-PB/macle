# Local speech transcription study

**Status:** implementation study for the first local ASR adapter; not a universal MACLE ASR decision.

## 1. Requirement context

The single-device Google Meet connector records the rendered tab and its audio output. To make the audio useful as MACLE observations, the first post-capture processing step is local speech recognition.

This must remain distinct from:
- Google-generated transcript artifacts returned by the Meet API;
- direct observations of audio/video;
- human-verified transcripts;
- speaker identity or diarization;
- semantic interpretation, summaries, action items or evaluation.

A machine-generated transcript is an algorithmic extraction with uncertainty, not a verbatim proof of what a person said.

## 2. First backend: faster-whisper

The first adapter uses [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper), a Python implementation of Whisper inference using CTranslate2.

Why it is a pragmatic first implementation:
- a direct Python API accepts media file paths and returns segments with start/end offsets;
- CPU int8 execution is supported;
- PyAV decodes audio, so a system FFmpeg installation is not required;
- integrated voice activity detection can suppress long non-speech intervals;
- the library is MIT-licensed;
- the backend can be kept behind a narrow MACLE adapter, without making it part of the conceptual observation model.

The project README documents CPU int8 mode, segment iteration, language detection and VAD. It also notes that model weights are downloaded from Hugging Face when loading a named model for the first time.

## 3. Runtime boundary

- Audio/video is read from a local WebM file.
- Inference runs in the local Python process.
- The audio and generated transcript are not sent to a hosted ASR provider.
- Model weights may be downloaded once from Hugging Face and cached locally.
- The default runtime is CPU with int8 quantization.
- CUDA is an explicit opt-in and requires a compatible local CUDA runtime.
- The initial implementation is post-capture, not streaming.

Model downloads are network access for software/model acquisition, not media-data egress. An offline installation can instead provide a compatible local model directory.

## 4. Observation semantics

Each non-empty ASR segment becomes one MACLE observation containing:
- source capture ID, where supplied by the capture manifest;
- SHA-256 and size of the source media file;
- segment index and offsets relative to the capture;
- recognized text;
- ASR engine and model identifier;
- detected language and language probability;
- available segment-level decoder confidence fields;
- an explicit statement that speaker attribution is not established from the composite recording.

The absolute observed timestamp is derived from the capture start time plus the segment offset only when the capture manifest provides a parseable start time. The relative offsets remain authoritative.

No speaker identity is inferred. A single composite audio stream may contain overlapping speech, remote audio, local playback, or other sources that cannot be disentangled reliably by this first backend.

## 5. Model-size policy

The CLI defaults to `small` to balance initial download size, CPU execution and multilingual recognition. Users can select `medium`, `large-v3`, or `turbo` where the available hardware and latency budget justify it.

Whisper model performance varies by language, audio quality, overlap, accents, microphone/speaker conditions and domain vocabulary. A selected model must be evaluated against a synthetic reference fixture before any quality claim is made.

## 6. Alternatives retained

### whisper.cpp

[ggml-org/whisper.cpp](https://github.com/ggml-org/whisper.cpp) provides a C/C++ inference implementation with CPU-only execution, AVX optimizations, quantization, GPU backends and VAD. Its release page listed v1.9.5 on 2026-10-06.

It remains a viable alternative if MACLE later needs a smaller native runtime, a standalone executable, or reduced Python/CTranslate2 coupling. The current Python CLI makes faster-whisper the simpler first adapter.

### Google-generated transcripts

Google Meet can generate transcript artifacts and timestamped transcript entries, but availability depends on Workspace settings and meeting configuration. These are a distinct source with Google provenance, not a replacement for local ASR and not guaranteed to be available.

## 7. License and provenance caution

The faster-whisper implementation repository declares MIT. OpenAI's Whisper repository says its code and weights are MIT, while the Hugging Face `openai/whisper-large-v3` model card declares Apache-2.0. Record the actual model repository and license metadata for each selected checkpoint; do not infer the weight license solely from the inference library's license. The initial connector downloads weights at runtime and does not redistribute them.

## 8. Explicit limitations

- Not streaming or real-time.
- No speaker diarization or identity recognition.
- No guaranteed separation of overlapping speakers.
- No semantic summarization or action-item inference.
- No transcript correctness guarantee.
- No hosted ASR or audio upload.
- Synthetic-only content remains the only authorized test input under the current demonstrator boundary.

## 9. References

- SYSTRAN faster-whisper repository and usage: https://github.com/SYSTRAN/faster-whisper — retrieved 2026-11-14.
- faster-whisper license: https://github.com/SYSTRAN/faster-whisper/blob/master/LICENSE — retrieved 2026-11-14.
- CTranslate2 repository and MIT license: https://github.com/OpenNMT/CTranslate2 — retrieved 2026-11-14.
- OpenAI Whisper repository, model capabilities and stated code/weight license: https://github.com/openai/whisper — retrieved 2026-11-14.
- Whisper large-v3 model card metadata: https://huggingface.co/openai/whisper-large-v3 — retrieved 2026-11-14.
- whisper.cpp repository: https://github.com/ggml-org/whisper.cpp — retrieved 2026-11-14.
- whisper.cpp releases: https://github.com/ggml-org/whisper.cpp/releases — retrieved 2026-11-14.
