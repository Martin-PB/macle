# Study — Videoconferencing platforms

**Status:** initial desk research; not a platform selection or implementation plan.  
**Scope:** Zoom, Microsoft Teams, Google Meet, Cisco Webex, with cross-platform capture providers as a separate category.

## 1. Why platform-specific study is necessary

A platform can expose meeting administration data without exposing live media. Conversely, a media SDK may provide raw audio/video while exposing a different set of meeting semantics. We must compare at least four layers independently:

1. **Control plane:** meeting lifecycle, participants, roles, presence, moderation and interaction events.
2. **Media plane:** audio, camera video, screen sharing, per-participant streams versus mixed/composited streams.
3. **Content plane:** chat, files, links, annotations, Q&A and shared documents.
4. **Post-meeting artifacts:** recordings, transcripts, attendance, summaries and metadata.

An API's existence does not imply universal availability. Account plan, tenant configuration, OAuth scopes, administrator consent, host privileges, participant consent, platform policy and meeting type can all restrict access.

## 2. Platform snapshots

### 2.1 Zoom

**Documented avenues**
- Meeting APIs expose meeting metadata and settings, including whether features such as hand raise, reactions, screen sharing, recording, and video were used.
- The Meeting SDK can expose raw audio and video through raw recording or raw streaming, subject to host permission and the relevant SDK/app setup.
- Zoom's Video SDK provides real-time raw audio, video, and share data for sessions built with that SDK. This is not equivalent to universal access to every ordinary Zoom meeting.
- Raw media callbacks can provide per-user audio and video/share frames; mixed audio is also available in documented SDK paths.

**Implications**
- Zoom appears to offer a relatively rich native media path, but distinguish Meeting SDK integration into an existing Zoom meeting from building a session with the Video SDK.
- Host permissions and visible recording/streaming consent are material constraints.
- Investigate platform event coverage and the exact distinction between meeting REST APIs, Meeting SDK, and Video SDK before designing an adapter.

**Sources**
- https://godevelopers.zoom.us/docs/api/meetings/ — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.
- https://developers.zoom.us/docs/meeting-sdk/windows/default-ui/advanced-features/raw-data/ — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.
- https://developers.zoom.us/docs/video-sdk/web/raw-data/ — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.

### 2.2 Microsoft Teams

**Documented avenues**
- Microsoft Graph can provide meeting transcripts and recordings after they become available, with change notifications.
- Access depends on Entra permissions, resource-specific consent or organization-wide permissions, and tenant administrator settings.
- Teams Real-time Media bots can access raw audio, multiple participant video streams, and screen-sharing media.
- The real-time media platform is a specialized route: Microsoft describes compliance recording and contact-center use cases, and explicitly does not recommend application-hosted real-time media bots as the default route for AI meeting agents.
- The application-hosted media path requires .NET/C# and Windows Server according to the current documentation.

**Implications**
- Separate Graph artifact retrieval from live media acquisition.
- The raw-media route may carry significant operational and platform constraints; do not assume it is a lightweight generic bot API.
- Tenant policy can disable Graph transcript access independently of app-level permissions.

**Sources**
- https://learn.microsoft.com/en-us/microsoftteams/platform/bots/calls-and-meetings/real-time-media-concepts — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.
- https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/meeting-transcripts/overview-transcripts — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.
- https://learn.microsoft.com/en-us/microsoftteams/meeting-transcript-api-access — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.

### 2.3 Google Meet

**Documented avenues**
- The Meet REST API manages meeting spaces and provides conference records, participants, participant sessions, recordings, transcripts, transcript entries, and smart notes.
- Google Workspace Events API subscriptions provide notifications about changes to meeting spaces and conference activity.
- The API supports pre-meeting configuration, participant/session information during conferences, and retrieval of artifacts after conferences.
- Transcript entries include participant identity, timestamps, text, and language code, with documented retention limits.

**Implications**
- The documented REST API is strong for meeting metadata, lifecycle events, and post-meeting artifacts.
- Do not mistake this for a general-purpose raw live audio/video API. A separate capture route (for example, a supported SDK, browser/desktop capture, or a bot provider) would need investigation.
- Distinguish persistent meeting-space members from participants and participant-device sessions.

**Sources**
- https://developers.google.com/workspace/meet/api/guides/overview — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.
- https://developers.google.com/workspace/meet/api/reference/rest/v2 — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.

### 2.4 Cisco Webex

**Documented avenues**
- Webex Meetings REST APIs cover scheduling, invitees, participant information, meeting controls, recordings, transcripts, summaries, and other meeting resources, subject to scopes.
- Webhooks are available for selected Webex activities, but resource availability differs by product and event type.
- The meeting resource guide says recording must be enabled and Webex Assistant must be enabled for transcripts; the latter cannot be turned on programmatically through the documented route and must be enabled by a host/participant or set as a default by an administrator.

**Implications**
- The control and post-meeting artifact APIs are useful, but the currently reviewed documentation does not establish a general raw live-media capture API for ordinary meetings.
- Transcript availability has an explicit configuration dependency.
- Further investigation is needed for Webex media SDKs and any supported live capture path.

**Sources**
- https://developer.webex.com/meeting/docs/meetings — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.
- https://developer.webex.com/meeting/docs/api/guides/webhooks — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.
- https://developer.webex.com/meeting/docs/access-meeting-resources-guide — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.

## 3. Cross-platform capture providers

### Recall.ai — candidate for evaluation, not selected

Recall.ai documents:
- a Meeting Bot API supporting Zoom, Google Meet, Microsoft Teams, Webex and other platforms;
- bot-based access to audio, video, transcripts, participant data and metadata, during and after meetings;
- a Desktop Recording SDK supporting several desktop/browser combinations;
- real-time media streaming and post-meeting recordings.

This is particularly relevant because it offers two distinct acquisition models:
- a bot that joins the meeting as a participant;
- desktop capture without relying on a meeting bot.

**Questions to investigate**
- exact per-platform parity and event fidelity;
- whether video is individual participant streams, composite output, or both;
- screen-share capture and attribution;
- latency, dropped frames, reconnect behavior and concurrency;
- data retention, residency, subprocessors, encryption and deletion;
- pricing, quotas, plan restrictions and lock-in;
- ability to export raw observations and provenance without using the vendor's interpretation layer;
- behavior when multiple people share one endpoint.

Sources:
- https://docs.recall.ai/docs/meeting-platforms — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.
- https://docs.recall.ai/docs/bot-overview — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.
- https://docs.recall.ai/docs/getting-started — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.
- https://www.recall.ai/product/meeting-bot-api — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.

## 4. Preliminary comparison

| Platform | Control/events | Live raw media | Post-meeting artifacts | Main caveat |
|---|---|---|---|---|
| Zoom | Meeting APIs and SDK callbacks | Yes, via specific SDK paths | Recording and related APIs | Permission/consent; Meeting SDK vs Video SDK distinction |
| Teams | Graph and bot APIs | Yes, specialized real-time media bot | Graph transcripts and recordings | Tenant policy; specialized .NET/Windows media path |
| Google Meet | REST + Workspace Events | Not established by reviewed REST API | Rich conference artifacts | Separate live media acquisition route needed |
| Webex | REST + selected webhooks | Not established by reviewed docs | Recordings, transcripts, summaries, participants | Transcript setup and API scope constraints |
| Recall.ai | Unified provider layer | Yes, bot/desktop capture products | Recordings, transcripts, metadata | Vendor dependency; verify per-platform fidelity |

This table is a research snapshot, not a scorecard. “Not established” means the reviewed sources do not prove the capability; it does not assert that no such capability exists.

## 5. Research gaps

- Full event catalogs for each platform, including hand raise, mute, camera, reactions, chat, screen-share lifecycle, breakout rooms and participant identity.
- Whether and how each platform exposes individual participant audio/video versus mixed or composited streams.
- Native SDK support matrix by operating system and client type.
- Browser-based capture feasibility and restrictions.
- Guest, external participant, anonymous and dial-in behavior.
- Multi-device identity resolution and room-device semantics.
- Permission and consent flows, including organizational policy.
- Platform terms and technical restrictions on recording, bot participation and automated capture.

## 6. No decisions made

No platform has been selected as the first integration. No capture provider has been selected. No assumption is made that all four platforms must be supported in the first release.


## 7. Event-level findings (additional research)

The platform APIs expose different granularities of events. Examples found in current official documentation:

- **Zoom Meeting SDK (web):** participant joined/left, participant state updates (including mute, video, roles and raised hand), waiting-room state, and active-speaker changes. Zoom also documents a webhook for screen-sharing started, and Meeting SDK chat callbacks for message received, edited, deleted, and chat status changes.
- **Google Meet:** Workspace Events subscriptions cover conference start/end, participant join/leave, recording start/end/file generation, transcript start/end/file generation, and smart-note lifecycle. The participant model explicitly distinguishes a person from a participant-device session; a room device can appear as a signed-in user/robot account.
- **Webex:** webhook event references include meeting participant joined/left and transcript-created events. The Meetings API also exposes meeting controls and participant resources, subject to scopes and product availability.
- **Teams:** real-time media bots can subscribe to selected participant video streams and screen-sharing content; Graph artifact notifications concern recordings and transcripts becoming available, not a complete live event stream.

These are examples, not a normalized cross-platform event taxonomy. MACLE will need to preserve the original platform event type and payload provenance before mapping it into any common event model.

**Sources**
- https://developers.zoom.us/docs/meeting-sdk/web/client-view/participant-events/ — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.
- https://developers.zoom.us/docs/api/meetings/events/ — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.
- https://developers.zoom.us/docs/meeting-sdk/linux/default-ui/basic-features/in-meeting-chat/ — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.
- https://developers.google.com/workspace/events/guides/events-meet — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.
- https://developers.google.com/workspace/meet/api/guides/participants — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.
- https://developer.webex.com/admin/docs/webhook-event-reference — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.
- https://learn.microsoft.com/en-us/microsoftteams/platform/bots/calls-and-meetings/real-time-media-concepts — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.

## 8. Secondary platforms and environments

The initial comparison should not imply that the four major enterprise platforms are the entire videoconferencing ecosystem.

- **GoTo Meeting:** official REST API documentation describes meeting creation and management, recordings, transcripts (when enabled for the account), and reporting. Recall.ai lists GoTo Meeting as beta support for its bot API.
- **Jitsi Meet:** worth a separate investigation because its open-source deployment model may offer a different integration and self-hosting profile. The current platform comparison has not yet validated its event/media interfaces or operational limitations.
- **Slack Huddles:** relevant because it is a meeting-like environment embedded in a collaboration platform. Recall.ai lists bot support and desktop SDK support with platform/OS limitations; native capture options need further study.
- **Other services:** Whereby, Discord voice/video, Amazon Chime SDK, and Zoom Rooms / Teams Rooms may be worth considering depending on product priorities. They are not part of the current baseline comparison.

Sources:
- https://developer.goto.com/GoToMeetingV1/ — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.
- https://docs.recall.ai/docs/meeting-platforms — retrieved_on: 2026-11-13; version: not pinned in this study; consult the cited page for its current API/SDK version.

## 9. Revised research priority

The next useful platform work is not to add every vendor indiscriminately. It is to complete a capability matrix for the likely first candidates (Zoom, Teams, Meet, Webex), then decide whether one or more secondary platforms merit inclusion. The matrix should distinguish:
- lifecycle and participant events;
- live media access and stream granularity;
- screen-share lifecycle and content;
- chat and reactions;
- post-meeting artifacts;
- permissions and tenant/host dependencies;
- client/OS coverage and deployment constraints.
