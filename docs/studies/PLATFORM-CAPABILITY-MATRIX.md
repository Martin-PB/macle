# Study — Platform capability and evidence matrix

**Status:** comparative research baseline, 13 November 2026.  
**Decision status:** no platform, provider, or capture strategy selected.

## 1. Reading rules

- **Documented:** official documentation explicitly describes the capability.
- **Conditional:** documented, but dependent on permission, plan, host, tenant, or deployment.
- **Not established:** reviewed sources do not establish the capability; this is not proof of absence.
- **Artifact-only:** available only after the meeting or artifact generation.
- **Provider-dependent:** a third party claims the capability; native-platform equivalence is not established.

A platform capability is not automatically a MACLE requirement. An API's existence does not prove effective access in every tenant, account, meeting, or client.

## 2. Capability matrix

| Capability | Zoom | Microsoft Teams | Google Meet | Cisco Webex |
|---|---|---|---|---|
| Participant join/leave | Documented in Meeting SDK events | Documented in Graph/bot event surfaces; exact set depends on API | Documented through Workspace Events and participant sessions | Documented for selected webhook/event surfaces |
| Participant state (mute, camera, role, hand raise) | Documented in Meeting SDK participant updates | Some state/media metadata available through specialized APIs; full parity not established | Participant/session records available; full live-state parity not established | Meeting controls/resources exist; complete state-event coverage not established |
| Active speaker | Documented in Meeting SDK Web events | Media-level access exists; normalized active-speaker parity not established | Speaker attribution in transcript artifacts; live active-speaker signal not established | Not established by sources reviewed |
| Per-participant audio | Documented in selected raw-data SDK paths | Documented for Real-time Media bots | Not established by reviewed REST/Events API | Not established by sources reviewed |
| Mixed audio | Documented in selected raw-data SDK paths | Exact mixed-stream contract not established here | Not established | Not established |
| Individual participant video | Documented in selected raw-data SDK paths | Documented for Real-time Media bots, with stream-selection constraints | Not established by reviewed REST/Events API | Not established |
| Screen-share media | Documented in selected raw-data SDK paths | Documented for Real-time Media bots | Live raw share media not established | Raw live share media not established |
| Screen-share lifecycle | Selected webhook/SDK surfaces documented | Event coverage depends on API path; full taxonomy not established | Full lifecycle taxonomy not established | Not established in reviewed sources |
| Chat/messages | SDK callbacks documented for selected SDKs | Graph/chat APIs exist; meeting-chat scope needs study | Meeting chat coverage not established by current source set | Messaging APIs/webhooks exist; meeting-specific coverage needs study |
| Recording artifact | Documented; host/account settings apply | Graph retrieval documented, subject to permission/tenant | Documented; MP4 saved in organizer Drive | Documented; configuration/product conditions apply |
| Transcript artifact | Product/feature-specific; exact API parity needs study | Graph retrieval documented; tenant policy can disable access | Documented, including granular entries | Documented when relevant configuration permits |
| Granular transcript entries | Further product/API study required | Further Graph API study required | Documented with participant, timestamps, text, language | Further API study required |
| Real-time event subscription | SDK callbacks and selected webhooks | Graph notifications and bot-specific events | Workspace Events subscriptions | Selected Webex webhooks |
| Raw live media | Specific Meeting SDK paths; distinct from Video SDK | Documented but specialized Real-time Media bot route | Not established by reviewed REST/Events APIs | Not established by reviewed sources |
| Main deployment constraint | SDK variants; host privilege and consent | Specialized media bots; C#/.NET and Windows Server/Azure requirements for app-hosted media | Workspace identity, OAuth and artifact access | API scopes, product/site configuration, artifact availability |

## 3. Platform evidence and caveats

### 3.1 Zoom

- Meeting SDK Web documents participant join, leave, state updates, waiting-room changes, and active-speaker changes.
- State updates include mute, video, host/co-host role, and raised hand.
- SDK guidance recommends treating events as signals to refresh participant state, rather than assuming the event payload is a complete durable state record.
- Raw audio/video/screen access exists in selected Meeting SDK platform paths. Documented native paths distinguish per-user audio from mixed meeting audio.
- Raw streaming requires live-streaming privilege. Documentation describes host permission or an appropriately installed OAuth app and scopes.
- Meeting SDK and Video SDK are not interchangeable: Video SDK is for sessions built with it, not a universal adapter to ordinary Zoom meetings.
- Heavy processing inside raw-data callbacks can delay callbacks and cause data loss; callbacks should hand off promptly to bounded processing queues.

**MACLE implications:** preserve SDK variant and privilege mechanism as provenance; test whether event and media callbacks share stable participant identifiers; test reconnect, rename, waiting-room transitions, and privilege revocation.

### 3.2 Microsoft Teams

- Microsoft Graph supports retrieval of meeting transcripts and recordings after they become available.
- Access depends on application/user permissions and tenant policy. A tenant administrator can restrict transcript access independently of application configuration.
- Graph artifact notifications must not be conflated with a complete real-time event stream.
- Real-time Media bots can access raw audio, selected participant video streams, and screen-sharing media.
- Microsoft describes this as a specialized platform for compliance recording, contact centers, and Cloud Video Interop, and does not recommend it as the default route for AI meeting agents.
- App-hosted media bots have significant constraints: C#/.NET and Windows Server in the documented production model, with Azure deployment requirements.

**MACLE implications:** keep Graph artifact ingestion and Real-time Media capture as separate adapters and evidence classes. Investigate whether a supported non-raw-media route satisfies an initial scenario before considering the specialized route.

### 3.3 Google Meet

- Meet REST API and Workspace Events expose conference records, participant records, participant sessions, and meeting lifecycle notifications.
- Google distinguishes a participant (a person, including a room device) from a participant session (a particular participant-device pair). One participant can have multiple device sessions.
- Workspace Events notify subscribers about conference and participant activity; event access is affected by subscription and participant-role limitations.
- Recordings, transcripts, transcript entries, and smart notes are documented.
- Transcript entries carry participant reference, start/end timestamps, text, and language code.
- Transcript entries are available for 30 days after the conference ends. This differs from Drive/Vault retention of generated artifacts.
- API transcript entries may differ from the generated Docs transcript if that file is modified after generation.
- Reviewed REST and Workspace Events documentation does not establish generic access to raw live audio/video or individual live screen-share streams.

**MACLE implications:** model person/participant separately from device/session; record artifact generation and retrieval times, source resource ID, and retention deadline; treat transcript entries as platform-derived observations, not substitutes for source audio.

### 3.4 Cisco Webex

- Webex provides meeting APIs and selected webhooks. Webhooks are notifications that generally trigger a follow-up API call for details.
- Event registration, permissions, and delivery rules vary by product and event type.
- Current API support documentation notes that some resource types (including meetings, recordings, meeting participants, and meeting transcripts in the referenced support matrix) are not available as webhook resource types. REST-resource existence therefore does not imply webhook parity.
- Meeting recordings and transcripts depend on product/site configuration and relevant recording/Assistant settings.
- Sources reviewed do not establish a general raw live-media route for ordinary Webex Meetings.

**MACLE implications:** build a resource-by-resource matrix from Webex API support documentation; verify target product, site, account type, and transcript configuration; keep live-media feasibility open.

## 4. Shared-endpoint and identity implications

A meeting participant identity is not necessarily a human identity. At minimum, MACLE's observation model must distinguish:

1. Human/person, possibly unidentified.
2. Platform participant/account object.
3. Endpoint/device: computer, phone, room system, browser session, or shared terminal.
4. Participant session: a particular connection through an endpoint.
5. Media source: camera, microphone, screen-share stream, or mixed stream.
6. Speaker attribution: an observation or inference linking speech to a person or participant.
7. Presence evidence: what supports a claim that a person was present.

Do not infer that one platform participant equals one human. A shared endpoint may represent several people, and one person may create several sessions. Voice diarization or visual detection may suggest multiple speakers/people, but those are derived observations with uncertainty, not authoritative identity facts.

Every mapping should preserve source namespace and identifier, observed identifier and scope, time interval and clock source, whether the relation is platform-asserted/user-supplied/algorithmically inferred, confidence where applicable, and contradictory observations rather than silently overwriting them.

## 5. Cross-cutting constraints to verify

For every platform and acquisition path, record:

- account edition, licensing, and feature entitlement;
- organizer/host role and whether the operator is host, co-host, attendee, or guest;
- tenant and administrator policies;
- OAuth scopes, consent mode, token lifetime, and revocation behavior;
- meeting type (scheduled, ad hoc, webinar, town hall, breakout room, room device);
- participant type (authenticated, guest, anonymous, dial-in, room system);
- supported client, SDK, OS, architecture, and deployment environment;
- media granularity (individual, mixed, composite, selected streams);
- event ordering, duplication, delivery guarantees, replay and recovery;
- timestamp semantics, clock skew, and time-zone representation;
- retention, deletion, data residency, subprocessors, and exportability;
- visible disclosure, participant notification, consent and opt-out behavior;
- provider-specific terms and restrictions.

These are test dimensions, not legal conclusions. Legal and organizational requirements need a separate data-governance study.

## 6. Official sources reviewed

### Zoom
- [Meeting SDK Web participant events](https://developers.zoom.us/docs/meeting-sdk/web/client-view/participant-events/)
- [Meeting SDK Windows raw data](https://developers.zoom.us/docs/meeting-sdk/windows/default-ui/advanced-features/raw-data/)
- [Meeting SDK macOS raw data](https://developers.zoom.us/docs/meeting-sdk/macos/custom-ui/advanced-features/raw-data/)
- [Meeting SDK iOS raw-data privilege flow](https://developers.zoom.us/docs/meeting-sdk/ios/custom-ui/advanced-features/raw-data/)

### Microsoft Teams
- [Real-time Media for calls and meetings bots](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/calls-and-meetings/real-time-media-concepts)
- [Application-hosted media bot requirements](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/calls-and-meetings/requirements-considerations-application-hosted-media-bots)
- [Meeting transcripts overview](https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/meeting-transcripts/overview-transcripts)
- [Transcript API access and tenant policy](https://learn.microsoft.com/en-us/microsoftteams/meeting-transcript-api-access)

### Google Meet
- [Meet REST API overview](https://developers.google.com/workspace/meet/api/guides/overview)
- [Work with participants and participant sessions](https://developers.google.com/workspace/meet/api/guides/participants)
- [Respond to Meet events](https://developers.google.com/workspace/meet/api/guides/events-overview)
- [Work with artifacts and retention](https://developers.google.com/workspace/meet/api/guides/artifacts)
- [Transcript entry resource](https://developers.google.com/workspace/meet/api/reference/rest/v2/conferenceRecords.transcripts.entries)

### Cisco Webex
- [Webex Meetings webhooks](https://developer.webex.com/meeting/docs/api/guides/webhooks)
- [Webex API support matrix](https://developer.webex.com/docs/api-support)
- [Meeting resources](https://developer.webex.com/meeting/docs/meetings)
- [Access meeting resources](https://developer.webex.com/meeting/docs/access-meeting-resources-guide)

## 7. Research gaps and next steps

1. Verify the full Teams Graph event and transcript permission matrix, including delegated vs application permissions and tenant policy.
2. Establish whether Webex offers a supported raw-media path for ordinary meetings, and identify SDK/product boundaries.
3. Complete platform-specific chat, reactions, Q&A, breakout-room, whiteboard, and shared-file coverage.
4. Test provider claims (especially bot and desktop capture) against native platform semantics.
5. Run the common evaluation protocol in CAPTURE-EVALUATION-PROTOCOL.md.
6. Perform a separate data-governance and privacy study before any real participant capture.

## 8. No decision made

This study does not select Zoom, Teams, Meet, Webex, Recall.ai, a bot, a desktop recorder, or any other implementation route. It records what reviewed official sources establish and where further evidence is required.
