# MACLE — Initial scope

**Status:** accepted product boundary; detailed requirements remain open.

## 1. Product framing

MACLE's general purpose is to articulate multimodal observations into a structured representation of linked events and relations.

Its first application domain is the meeting:

> The focus is the meeting, not only what is said but the wider situation in which the meeting unfolds.

The first operational scope is narrower: **videoconferencing meetings**.

## 2. In scope

A meeting mediated by a videoconferencing platform, including:

- participants and participant identities as exposed or inferable through permitted sources;
- audio, speech, speakers, pauses, overlaps, prosody, and relevant non-speech sounds;
- camera video and observable visual activity;
- screen sharing, shared windows, applications, slides, documents, and changes to shared content;
- in-meeting chat, reactions, annotations, questions, and messages where accessible;
- meeting lifecycle and interaction events: join, leave, reconnect, mute/unmute, camera on/off, hand raise/lower, reactions, role changes, screen-share start/stop, and similar events where exposed;
- timestamps, ordering, overlap, simultaneity, source identity, provenance, and uncertainty;
- multiple people sharing one camera, room device, computer, or endpoint.

A single endpoint may represent several human participants. Endpoint identity and human identity must therefore not be conflated.

## 3. Out of initial operational scope

- Dedicated capture of ordinary in-person meetings without a videoconferencing platform.
- Room-wide ambient sensing and independent arrays of microphones/cameras.
- A physical meeting-room product or hardware appliance.
- General-purpose surveillance or continuous monitoring outside a meeting session.

These exclusions do not deny that such situations could be relevant to a broader future MACLE concept. They are simply not part of the first operational target.

## 4. Functional boundary

MACLE is expected to investigate and potentially provide:

1. acquisition from permitted sources;
2. extraction of observable signals and events;
3. normalization across modalities and vendors;
4. temporal alignment and correlation;
5. explicit relations between events, participants, endpoints, media, and shared artifacts;
6. provenance, confidence, and uncertainty;
7. a queryable/exposable representation for consuming systems.

The following remain outside the assumed responsibility of the perception layer:

- deciding what participants really intend;
- deciding whether a statement is true;
- evaluating the strategic meaning of the meeting;
- deciding what action should be taken;
- acting autonomously on behalf of participants.

Those may be performed by a downstream consumer.

## 5. Important modeling distinctions

- **Person vs endpoint:** one endpoint can represent multiple people; one person can use multiple endpoints.
- **Participant vs speaker:** a platform participant may be present without speaking; a speaker label from diarization is not automatically a verified identity.
- **Media stream vs event:** a stream is a source of observations; an event is a time-bounded occurrence or state change derived from one or more observations.
- **Platform event vs inferred event:** preserve whether an event came directly from a platform API or was inferred from media.
- **Shared content vs screen pixels:** a screen capture may reveal content, but it does not necessarily identify the underlying document, application object, or semantic change.
- **Observed vs interpreted:** store observations and their provenance separately from downstream interpretations.

## 6. Requirements not yet decided

No commitment has yet been made about:
- real-time operation versus post-meeting processing, or the balance between them;
- whether a MACLE bot may join meetings as a visible participant;
- whether desktop capture is acceptable or preferred;
- whether native platform integrations are required for the first release;
- which platforms must be supported first;
- which media must be captured by default;
- retention, deletion, consent, access-control, and data-residency policies;
- whether MACLE stores media, derived artifacts, or only references and structured observations;
- whether transcription and diarization are built in, integrated, or optional.

These questions belong in studies and decision records before they become requirements.
