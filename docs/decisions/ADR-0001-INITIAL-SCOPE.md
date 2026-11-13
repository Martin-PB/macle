# ADR-0001 — Initial operational scope

- **Status:** ACCEPTED
- **Date:** 2026-11-13
- **Decision owners:** Project owner

## Context

MACLE has a broad conceptual foundation: articulating multimodal observations and linked events to expose the evolving structure of a situation.

The first application domain is the meeting, understood as more than spoken conversation. The first practical scope must nevertheless be bounded so that platform research and implementation can be concrete.

## Decision

The initial operational scope is **meetings mediated by videoconferencing platforms**.

This includes situations where multiple people may share one computer, camera, room endpoint or other device. Such a configuration remains within the videoconferencing scope; it is not reclassified as an in-person meeting merely because several people are physically co-located behind one endpoint.

Dedicated in-person meeting capture and room-sensing are outside the initial operational scope.

The public README remains unchanged for now. It may retain the broader conceptual framing and meeting focus; the detailed videoconferencing boundary is maintained in project documentation.

## Consequences

- Platform-specific capabilities and restrictions must be studied separately.
- The domain model must distinguish human participants from devices/endpoints.
- Capture options must include the possibility that several people share one endpoint.
- In-person-only sensors and room deployments are not first-release requirements.
- No platform, capture provider, SDK, bot strategy, language, runtime, or architecture is selected by this decision.

## Alternatives considered

1. **Start with in-person meetings:** not selected for the initial operational scope.
2. **Treat all meeting contexts as first-release targets:** too broad for an initial implementation.
3. **Focus only on speech/transcription:** rejected as a scope definition because the meeting situation includes more than what is said.

## Review triggers

Revisit this decision only if the project owner explicitly expands the initial operational scope or new evidence reveals that the videoconferencing boundary is impractical.
