# Study — Adjacent tools and reusable components

**Status:** initial landscape; candidates only.  
**Purpose:** identify existing capabilities that MACLE may consume, integrate, compare, or deliberately avoid duplicating.

## 1. Keep capture, perception, and downstream productivity separate

Many meeting products combine recording, transcription, summaries, action items, CRM updates, and AI chat. MACLE's intended role is different: it should expose structured observations and relationships, leaving interpretation and action to downstream consumers.

A tool that generates excellent summaries may still be a poor source for MACLE if it hides raw signals, event provenance, timing, uncertainty, or modality-level data.

## 2. Capture and meeting-data platforms

### Recall.ai
A cross-platform capture infrastructure candidate. Offers meeting bots and a desktop recording SDK, with access to meeting media and metadata. Particularly relevant for comparing bot-based and bot-free acquisition.

Study: https://docs.recall.ai/docs/getting-started — retrieved_on: 2026-11-13; version: not stated in the cited source.

### Fireflies.ai
A meeting assistant that joins supported video meetings, records/transcribes, and provides a GraphQL API, webhooks, transcripts, summaries and action items. It can also ingest uploaded media. This appears oriented toward meeting intelligence and productivity rather than a neutral multimodal event substrate.

Study:
- https://fireflies.ai/api — retrieved_on: 2026-11-13; version: not stated in the cited source.
- https://guide.fireflies.ai/articles/5365127863-web-conference-platforms-supported — retrieved_on: 2026-11-13; version: not stated in the cited source.

### Otter.ai
A meeting assistant supporting automatic joining of Zoom, Google Meet and Teams, transcription, notes, and slide capture. Its product surface is useful as a benchmark for meeting capture and transcription workflows; raw multimodal/event export needs separate verification.

Study: https://otter.ai/apps — retrieved_on: 2026-11-13; version: not stated in the cited source.

### Fathom
A meeting recording/transcription product with a public API for summaries, transcripts and action items, plus integrations and an MCP route to meeting context. The API is oriented toward already processed meeting insights.

Study:
- https://help.fathom.video/en/articles/8368641 — retrieved_on: 2026-11-13; version: not stated in the cited source.
- https://help.fathom.video/en/articles/11497793 — retrieved_on: 2026-11-13; version: not stated in the cited source.

### tl;dv
A recorder and meeting-notes product for Meet, Teams and Zoom, with API access to meeting data, transcripts and notes. Its API is documented as alpha and access is plan-dependent. It also offers bot-free recording for some workflows, which is worth examining as a capture pattern.

Study:
- https://intercom.help/tldv/en/articles/11583137-api — retrieved_on: 2026-11-13; version: not stated in the cited source.
- https://intercom.help/tldv/en/ — retrieved_on: 2026-11-13; version: not stated in the cited source.

### Granola
A desktop AI notepad that integrates with calendars and connects notes to CRM, project management, document, messaging and AI tools. Its “no meeting bot” approach is an interesting alternative capture model. Its public product emphasis is notes and workflow integration rather than full raw multimodal capture.

Study:
- https://docs.granola.ai/help-center/getting-started/granola-101 — retrieved_on: 2026-11-13; version: not stated in the cited source.
- https://www.granola.ai/integrations — retrieved_on: 2026-11-13; version: not stated in the cited source.

## 3. Speech and diarization components

### Deepgram
Documents streaming and batch speech recognition with speaker diarization. Diarization assigns speaker labels to words; streaming and batch models have different capabilities. Speaker labels must not be treated as verified human identities.

Study: https://developers.deepgram.com/docs/diarization — retrieved_on: 2026-11-13; version: not stated in the cited source.

### Speechmatics
Documents real-time transcription over WebSocket with continuously returned transcript results. Evaluate latency, language coverage, punctuation, timestamps, speaker attribution, overlap handling, and data-processing terms.

Study: https://docs.speechmatics.com/speech-to-text/realtime/quickstart — retrieved_on: 2026-11-13; version: not stated in the cited source.

### Further candidates to investigate
- AssemblyAI
- pyannote.audio
- NVIDIA Riva
- Whisper / faster-whisper
- Vosk and other offline speech-recognition engines

These are research leads, not evaluated recommendations. Their diarization, streaming, language, hardware, licensing and deployment characteristics must be checked before inclusion in a comparison.

## 4. Tool families beyond transcription

These families may supply signals or context around a meeting. They are not all necessarily MACLE integrations.

| Family | Examples / candidates | Potential contribution |
|---|---|---|
| Calendar and scheduling | Google Calendar, Outlook Calendar | Meeting identity, schedule, invitees, organizer, expected context |
| Messaging | Teams chat, Webex messaging, Slack | Messages, reactions, links, follow-up context |
| Documents and storage | Google Drive/Docs, OneDrive/SharePoint, Notion | Shared artifacts and post-meeting references |
| Collaboration boards | Miro, FigJam, Mural | Shared visual artifacts, edits, cursors, comments |
| Project/issue tracking | Jira, Linear, GitHub, Asana, Trello | External work items associated with discussion |
| CRM | Salesforce, HubSpot, Attio, Affinity | Relationship context and meeting-linked records |
| Automation | Zapier, Make, n8n | Workflow orchestration; likely downstream rather than perception core |
| Media processing | FFmpeg, GStreamer | Media ingestion, conversion, segmentation and synchronization |
| Computer vision | OpenCV and specialist vision models | Frame-level visual observations, screen/layout analysis |
| Audio processing | WebRTC audio processing, VAD, sound-event detection | Voice activity, segmentation, acoustic events |

The examples are a landscape to examine, not a committed dependency list.

## 5. Evaluation criteria

For every candidate, record:

1. What source does it observe: platform API, bot media, local desktop, uploaded file, or user-authored data?
2. Which modalities are available: audio, video, screen, chat, events, documents?
3. Is access live, delayed, or post-meeting?
4. Are outputs raw, extracted, summarized, or interpreted?
5. Are timestamps and participant attribution available?
6. Can raw source segments and provenance be retained?
7. What are the latency, completeness and failure modes?
8. Can it operate with multiple people behind one endpoint?
9. What permissions, consent and organizational controls are required?
10. What are the licensing, cost, deployment, residency and retention constraints?
11. Can the component be replaced without changing MACLE's internal model?
12. Does it duplicate a capability that MACLE should own?

## 6. Preliminary principle

Prefer replaceable adapters around external tools. Preserve the distinction between a source observation, a tool-produced extraction, and an interpretation. Do not make a downstream meeting-summary product the canonical source of MACLE's situation model without an explicit decision.
