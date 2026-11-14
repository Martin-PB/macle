# MACLE

**Multimodal Articulation through Concrescence of Linked Events**

MACLE is an open-source project exploring how multimodal observations of a situation can be articulated into a coherent, structured representation.

Its initial area of focus is the meeting: not only what is said, but the wider situation in which a meeting unfolds.

That situation can include:

- spoken audio, speakers, silences, intonation and other sounds;
- video, people, gestures, expressions and movement;
- shared screens, windows, applications and changes to displayed content;
- chat messages, annotations and documents;
- interaction and platform events, such as presence changes, reactions, raised hands, joins and departures;
- temporal relations, simultaneity, sequences and evolving context.

The central challenge is not merely to collect these streams. It is to preserve and expose the relations between observations, participants, events and context.

## Project boundary

MACLE aims to observe, capture, extract, normalize, structure, correlate and expose information about a situation.

Its outputs may include observations, events, relationships, timestamps, provenance, confidence and state/history.

Interpretation, reasoning, projection and action remain the responsibility of the system or agent consuming MACLE's outputs. MACLE is not tied to a particular LLM, agent framework or model provider.

## Concept

The name expresses the project's guiding idea:

- **Multimodal** — a situation is perceived through multiple modalities.
- **Articulation** — observations are related and organized, rather than merely juxtaposed.
- **through Concrescence** — a multiplicity of relations comes to form a concrete, coherent whole.
- **of Linked Events** — people, interactions, perceptions and changes are represented through the events by which they become observable in a situation.

The project takes inspiration from process philosophy and the philosophy of situation. These inspirations guide its conceptual framing; they are not software specifications.

## Status

MACLE remains an exploratory product, but its first cross-platform implementation slice is now underway: a shared Rust session core with a Chrome WebAssembly host and an Android native/JNI host. The Android app contains a synthetic-only, screen-only MediaProjection prototype; Chrome continues to provide the existing local tab recorder. Neither platform's capture behavior has yet been validated across a physical-device/browser compatibility matrix. The current Stage A boundary remains synthetic-only and local-only.

## License

MACLE is distributed under the [Apache License, Version 2.0](LICENSE).
