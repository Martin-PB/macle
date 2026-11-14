# Decision brief — Initial demonstrator data and deployment boundary

**Status:** OPEN — user arbitration required.  
**Related issue:** #8.  
**Related studies:** DATA-EGRESS-AND-PRIVACY-GATE.md, DATA-PROTECTION-AND-GOVERNANCE.md, REFERENCE-SPIKE-READINESS.md.  
**No ADR number assigned:** this is a decision brief, not an adopted decision.

## 1. Decision required

Before the reference-environment spike moves from documentation to real execution, MACLE needs an explicit boundary for:
1. whether the first demonstrator uses fully synthetic media/content or real human participants/media;
2. whether any data may leave the self-hosted test environment.

These are separate axes. “Synthetic data” does not automatically mean “no personal data” if actual testers' voices, faces, names, device identifiers, or network metadata are captured. “Local-only” reduces external disclosure but does not by itself establish compliance.

## 2. Staged options

| Stage | Test material | Processing boundary | What it can validate | What it does not validate |
|---|---|---|---|---|
| A — synthetic baseline | Generated/synthetic audio, video, chat, identities and event actions; no real participant media | Local self-hosted fixture | Event plumbing, track IDs, source timing, media continuity, observer restart, normalization, overlap handling | Human consent UX, real camera/microphone variation, actual multi-person capture behavior |
| B — controlled human test | Limited project/test volunteers, disclosed and governed; pseudonymous fixture IDs | Local self-hosted fixture; no third-party capture or speech provider | Real microphone/camera behavior, shared endpoint, real acoustic overlap, hand-raise and UI workflow | Production deployment, broad tenant/provider behavior |
| C — synthetic provider test | Synthetic media and identities sent through a third-party capture/service path | External provider under a documented test account and terms | Provider API behavior, bot/desktop capture, egress mapping, provider event fidelity | Lawfulness or suitability for real meeting content |
| D — real meeting/provider test | Real meeting participants and content | External provider and/or cloud services | Deployment-specific integration behavior | No general conclusion beyond the assessed controller, purpose, participants, provider terms and jurisdiction |

The stages are not mutually exclusive product architectures. A later project may use more than one, but each requires its own scope and evidence.

## 3. Main trade-offs

### Stage A — synthetic/local
**Advantages:** smallest data-protection surface; reproducible; avoids real participant data in the first media-plane test; allows the event/track/clock/recovery mechanics to be exercised.

**Limitations:** generated media cannot fully represent camera/microphone variability, real co-located speech, acoustic echo, real participant permissions, or user-facing disclosure.

### Stage B — controlled human/local
**Advantages:** validates the most important shared-endpoint and real-world media behavior.

**Limitations:** actual voices/images and associated metadata are personal data. Pseudonymous labels do not anonymize them. The test needs a defined controller, purpose, lawful basis, information, security, retention/deletion and rights-handling. If the context involves employees or other power imbalance, consent must not be assumed to be freely given.

### Stage C — synthetic/provider
**Advantages:** allows a provider's technical integration and data-flow behavior to be evaluated without using real meeting content, if the synthetic material truly contains no identifiable real-person data.

**Limitations:** introduces provider contracts, subprocessors, region, access, retention, model-use and deletion questions even for test content. It does not authorize real-data use.

### Stage D — real/provider
**Advantages:** closest to a production deployment.

**Limitations:** highest governance burden; requires deployment-specific legal/privacy/security approval and verifiable provider controls. It must not be inferred from a successful synthetic technical test.

## 4. Proposed progression for consideration (not adopted)

A conservative sequence would be:
1. Stage A first, to verify the technical event/media pipeline without real participant media.
2. Stage B only if actual human shared-endpoint behavior is necessary to answer an unresolved question and the test controller has approved the required privacy safeguards.
3. Stage C only after provider terms/data-flow are documented, using synthetic data.
4. Stage D only after a deployment-specific gate and qualified review.

This progression is a proposal for discussion, not an accepted MACLE policy.

## 5. Questions the decision owner must answer

1. Which stage is authorized for the first executable demonstrator: A, B, or A followed by B?
2. Is any third-party service permitted in the initial spike, even with synthetic content, or must both candidates be entirely self-hosted?
3. Who is the controller/decision authority for any human-participant pilot, and who will review the legal/privacy assessment?
4. What maximum retention and deletion evidence is required for any test artifacts?

No answer is assumed.

## 6. What can proceed before arbitration

- Prepare a self-hosted fixture and observer harness for synthetic media.
- Pin candidate Jitsi and LiveKit versions without selecting either for production.
- Test platform events, track subscription, timestamps, reconnect and recovery with synthetic participants.
- Keep third-party capture providers and real meeting content out of the spike until explicitly authorized.
- Keep human-participant testing as a separate gate.

This work can make progress without deciding whether MACLE's eventual product will be local, cloud, hybrid, or multi-deployment.

## 7. No decision made

This brief does not approve real participant capture, external data egress, a lawful basis, a consent model, a provider, a retention period, or a deployment architecture. The decision remains open for explicit user arbitration.
