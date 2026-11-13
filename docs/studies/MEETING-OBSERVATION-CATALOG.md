# Study — Meeting observation catalogue

**Status:** domain inventory for discussion; not a committed feature list.  
**Independence:** this catalogue describes the videoconference meeting domain without assuming a particular vendor or capture mechanism.

## 1. Purpose

Describe what may be observable in a videoconference meeting before deciding which observations MACLE must capture, how they are acquired, or which should be implemented first.

The catalogue deliberately distinguishes:
- a **domain phenomenon** (what happens in the meeting);
- an **observation** (what a source makes available);
- an **extraction** (what a processing component derives from media);
- an **interpretation** (what a downstream consumer concludes).

## 2. Participants, identities and endpoints

Potential observations:
- participant joins, leaves, reconnects, is admitted, is removed, or changes role;
- display name, platform user ID, account identity, guest/anonymous status, dial-in identity;
- device or endpoint joins, leaves, changes, or reconnects;
- participant uses several devices;
- several people share one camera, room device, microphone, or computer;
- participant is present but not visibly or audibly active.

Modeling cautions:
- a platform participant ID is not necessarily a durable human identity;
- a device session is not the same thing as a person;
- a camera tile or audio channel is not necessarily one person;
- a speaker label inferred from audio is not a verified identity.

## 3. Audio and speech

Potential observations:
- mixed meeting audio;
- individual participant audio streams, when available;
- speech segments and timestamps;
- speaker changes and overlap;
- pauses, silence, interruptions and turn-taking;
- loudness, pitch, prosody and other acoustic features;
- non-speech sounds such as laughter, applause, alarms, music or environmental noise;
- audio quality, clipping, packet loss, mute state and discontinuities;
- language and language changes.

Derived outputs may include voice activity, transcription, diarization, emotion-like acoustic descriptors, sound-event labels and alignment. These are extractions with model-specific uncertainty, not ground truth.

## 4. Camera video and visual activity

Potential observations:
- camera on/off and stream availability;
- individual camera streams or composite gallery output;
- visible people, faces, body posture, gestures and movement;
- changes in participant tile layout;
- visual reactions or visible attention cues;
- camera quality, frame loss, frozen frames and transitions.

Cautions:
- visual presence does not prove attention or comprehension;
- expressions and gestures should not be assigned psychological meaning automatically;
- a composite gallery can obscure which pixels correspond to which participant;
- the same participant may change camera or device.

## 5. Screen sharing and shared visual content

Potential observations:
- screen-share start, stop, pause, resume and ownership changes;
- shared screen/window/application identity, when exposed;
- screen frames, slides, cursor movement and visible changes;
- multiple concurrent shares or transitions between shared sources;
- remote control events, if supported and exposed;
- changes to a shared document, dashboard, IDE, browser, presentation or whiteboard.

Cautions:
- screen pixels are not equivalent to the underlying document or application data;
- a change in pixels may be a scroll, animation, cursor movement, edit, or window transition;
- attribution of a visual change to a person may be uncertain;
- a shared screen may contain information unrelated to the meeting.

## 6. Chat and platform-native interactions

Potential observations:
- chat messages, edits, deletions, replies, reactions and timestamps;
- sender and recipient/channel scope;
- links, attachments, polls, Q&A and annotations;
- hand raise/lower;
- mute/unmute, camera state, role changes and waiting-room transitions;
- reactions and platform-specific interaction events;
- breakout-room creation, assignment, join/leave and return to main room.

Availability varies widely by platform, SDK, permissions and meeting type. A missing event in one connector must not be interpreted as proof that it did not happen.

## 7. Meeting lifecycle and technical state

Potential observations:
- scheduled meeting identity and actual conference/session identity;
- meeting started/ended;
- participant and endpoint sessions;
- recording/transcription started, stopped or became available;
- network interruption, reconnect, client restart and media discontinuity;
- platform service or capture-bot connection state;
- capture source health and gaps.

Keep the lifecycle of the meeting separate from the lifecycle of MACLE's own capture session.

## 8. Temporal and relational dimensions

The meeting is not a list of isolated records. Relevant relations may include:
- event A occurred before, after, during, or overlapping event B;
- speech segment belongs to a media stream and is attributed to a speaker hypothesis;
- a participant session is associated with a platform identity and endpoint;
- a screen share was initiated by a participant and displayed a particular visual source;
- a chat message refers to a shared artifact or a prior spoken segment;
- a reaction occurred during a speech segment or after a visible change;
- an observation was extracted from a specific media interval or platform event.

Time should preserve:
- source timestamp;
- ingestion/receipt timestamp;
- processing timestamp;
- clock basis and synchronization uncertainty;
- interval start/end where an event has duration;
- ordering uncertainty when clocks or streams are not synchronized.

## 9. Evidence and provenance levels

Every observation should retain, where available:
- source platform, API, SDK, device or media artifact;
- original event type and source identifier;
- capture method and connector version;
- source timestamps and ingestion timestamps;
- raw reference or media interval;
- extraction component/model and version;
- confidence and known limitations;
- whether the content is direct platform telemetry, media-derived extraction, or later interpretation.

Suggested evidence labels (terminology to be reviewed):
- **PLATFORM_REPORTED** — explicitly reported by a platform API or event.
- **MEDIA_OBSERVED** — directly observed in an acquired media stream.
- **MODEL_EXTRACTED** — derived by an automated perception component.
- **HUMAN_ANNOTATED** — manually supplied or corrected.
- **CONSUMER_INTERPRETED** — conclusion made by a downstream application or agent.

These labels are proposed for discussion, not a final schema.

## 10. Candidate minimum demonstrator scenario

A deliberately small scenario that tests the central premise:
1. Two remote participants join from separate endpoints.
2. One participant speaks while the other shares a screen.
3. A third person joins through a shared room endpoint with multiple people behind one camera.
4. A chat message arrives and a participant raises a hand.
5. The shared content changes while speech continues.
6. One participant disconnects and rejoins from another device.

The demonstrator should show that MACLE can preserve the timeline, source, participant/endpoint distinction, overlapping events, and uncertainty. It need not attempt high-level meeting understanding.

## 11. What this catalogue does not decide

It does not establish that every listed signal must be captured, that all platforms expose it, that all observations must be real-time, or that MACLE must store raw media. Prioritization and implementation belong in requirements and decision records.
