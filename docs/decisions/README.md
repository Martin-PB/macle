# MACLE — Decision register

This register contains explicit project decisions only. Studies and recommendations do not become decisions by implication.

## Status vocabulary

- **PROPOSED** — suggestion not yet accepted.
- **ACCEPTED** — explicitly agreed scope or decision.
- **DEFERRED** — deliberately postponed.
- **REJECTED** — considered and not selected.
- **SUPERSEDED** — replaced by a later decision.

## Current decisions

| ID | Decision | Status |
|---|---|---|
| ADR-0001 | Initial operational scope is videoconferencing meetings | ACCEPTED |

## Templates and proposed governance

- [ADR template](TEMPLATE.md) — proposed structure; not yet adopted.

## Open decision topics

- First platform(s) to support.
- Native platform integration versus cross-platform capture provider.
- Bot participant versus desktop/browser capture.
- Live processing versus post-meeting processing.
- Required modalities and minimum useful event set.
- Media storage versus derived observations/references.
- Identity model for people, platform accounts, devices and shared endpoints.
- Privacy, consent, retention, deletion, data residency and access control.
- API/MCP/service exposure and downstream integration model.

Each topic should receive its own decision record when evidence is sufficient. Do not bundle unrelated choices into one architecture decision.
