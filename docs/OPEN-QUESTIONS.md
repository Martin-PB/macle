# MACLE — Open questions

This is a working list. An open question is not a hidden decision.

## Product behavior
- Which competency questions should be baselined as initial consumer needs, and which are explicitly out of scope?
- Which conceptual entities and relations are essential, optional, or merely explanatory?
- What is the minimum observation envelope needed to preserve source identity, derivation, time, uncertainty, and provenance?
- Must MACLE expose observations while the meeting is still running, or is post-meeting processing sufficient for the first milestone?
- What is the minimum useful event set for a first demonstrator?
- Is full video capture required, or are selected frames and derived visual events sufficient?
- Must the system capture chat and shared documents, or only references/metadata?
- Should raw media be retained, transiently buffered, or discarded after extraction?

## Identity and attribution
- Should speaker labels be session-scoped hypotheses by default, with person resolution deferred unless justified by a concrete purpose and legal assessment?
- What rules govern identity hypotheses, competing candidates, confidence, correction, and supersession?
- How should a person be represented when they join from several devices?
- How should one device representing several people be modeled?
- Can voice/visual diarization be linked to platform identity, and under what confidence rules?
- How should anonymous, dial-in, room-device, guest, and bot participants be represented?

## Capture and platforms
- Which platform is the first reference integration?
- Is a visible bot acceptable?
- Is desktop/browser capture acceptable?
- Is a third-party capture provider acceptable for an initial version?
- Which platforms and client types must be supported at launch?
- Which self-hostable environment, if any, should be used only as a reproducible reference fixture (separate from production-platform selection)?
- Should the reference fixture prioritize a complete meeting UI (Jitsi), explicit track-level media primitives (LiveKit), or rich post-meeting replay (BigBlueButton)?
- What exact event/media coverage is needed for the first demonstrator, and which gaps are acceptable?
- Can the candidate capture path preserve the distinction between a person, a platform participant, an endpoint, and a participant session?
- Which platform permissions and tenant restrictions make a candidate route unavailable in realistic target environments?

## Data and governance
- What consent and disclosure behavior is required?
- What retention and deletion guarantees are required?
- Which deployment regions and data residency constraints apply?
- What data may leave the user's environment?
- What lawful basis, controller/processor roles, participant notice, objection/opt-out, and organizational policies apply to each deployment context? (Requires dedicated legal/privacy analysis; not answered by the platform API study.)
- What minimization rules apply separately to raw media, transcripts, extracted observations, and inferred attributes?
- How should deletion propagate to derived observations, backups, exports, and third-party processors?
- What access-control model applies to recordings, derived events, and meeting context?

## Interfaces and consumers
- Should provenance be represented natively in a MACLE model, mapped to W3C PROV, or both?
- Which interval relations and uncertainty semantics are needed for cross-modal temporal reasoning?
- Is CloudEvents useful as a transport envelope while retaining a MACLE-owned domain payload?
- Which query semantics are needed for as-of views, temporal overlap, provenance traversal, and contradiction discovery?
- Should the first consumer interface be an API, MCP server, event stream, SDK, or a combination?
- What does a consuming agent need to query: timeline, participants, current state, relations, source artifacts, or all of these?
- How should MACLE expose uncertainty and provenance without making downstream consumers depend on vendor-specific schemas?

## Engineering
- What latency and throughput targets are appropriate?
- Which media and event formats should be canonical?
- What storage/query model is needed for time-indexed linked events?
- Which components should be local, remote, or replaceable adapters?
