# Study — Data egress and privacy gate

**Status:** PROPOSED study, 14 November 2026. No deployment policy or legal conclusion adopted. Not legal advice.

## Purpose

Before selecting or evaluating a capture path for real meetings, MACLE needs a deployment-specific data-flow and privacy assessment. API capability alone is insufficient. Local processing may reduce exposure but does not itself establish a lawful basis, necessity, transparency, purpose compatibility, or compliance.

## Regulatory anchors (EU / France)

- GDPR Article 5: lawfulness, fairness, transparency, purpose limitation, minimisation, accuracy, storage limitation, security, accountability.
- GDPR Article 6: a lawful basis is needed for each purpose; consent is not automatically the appropriate basis in every employment or meeting context.
- GDPR Article 9: biometric data are special-category data when processed for the purpose of uniquely identifying a natural person. A voice recording may be personal data, but is not automatically Article 9 biometric data merely because it contains a voice; purpose and technical processing matter.
- GDPR Articles 13–14: information duties; Article 17: erasure subject to conditions/exceptions; Article 28: processor terms; Articles 32–35: security, breach and DPIA obligations; Chapter V: third-country transfers.
- AI Act Article 5(1)(f): prohibits AI systems used to infer emotions of natural persons in workplace and education institutions, except for medical or safety reasons. This is not a general prohibition on all audio/video analysis.
- CNIL and French labour/privacy rules may add requirements for employee monitoring, recording, transparency, proportionality, consultation and access. The actual deployment needs qualified legal/DPO review.

A supplier's contractual label does not settle whether it is a processor, joint controller, or independent controller. Assess actual purposes, means and roles.

## Data classes

Assess each separately:
- raw audio (individual tracks, mixed audio, snippets);
- raw video (individual tracks, gallery, selected frames);
- screen/shared content and documents;
- platform/control events, chat and metadata;
- transcripts, captions and diarization;
- identity, endpoint and attribution hypotheses;
- derived features (embeddings, voiceprints, face descriptors, OCR, acoustic features);
- human annotations and ground truth;
- operational logs, timestamps and trace IDs;
- downstream summaries, action items and interpretations.

Derived data are not automatically anonymous. Pseudonymisation, hashing, embeddings or removing names do not by themselves establish anonymity.

## Required data-flow inventory

For every adapter, SDK, bot, desktop capture process, speech provider, storage service and consumer, record:
1. origin and collection mechanism;
2. processing location and countries (including backups and support access);
3. every recipient, subprocessor and role;
4. data classes, fields, modalities and purpose per operation;
5. transfer mechanism for third-country access/transfers;
6. active, transient, cache, backup, log and provider retention;
7. deletion propagation to derivatives, exports and backups, and evidence of deletion;
8. human/machine access, encryption, key ownership, isolation, audit and incident handling;
9. model training, evaluation, service-improvement and other secondary uses;
10. information, objection, access, correction, erasure, restriction and complaint handling;
11. contract, DPA, security, location, retention and tested-deletion evidence.

Unknown values remain unknown, not “no”.

## Candidate deployment profiles (not selected)

| Profile | Boundary | Main unresolved questions |
|---|---|---|
| Local-only | User-controlled device/environment | Local security, permissions, backups, device capability |
| Customer-controlled | Organization-administered infrastructure | Admin access, hoster, region, operations, backups |
| Contracted cloud | Provider processes under contract | Subprocessors, transfers, retention, model use, deletion |
| Third-party capture | Separate service joins/captures and returns data | Additional recipient, bot visibility, egress, retention, lock-in |
| Hybrid | Different data classes cross different boundaries | Re-identification, hidden metadata, policy/provenance complexity |

Describe the boundary per data class and processing activity, not only by naming a hosting provider.

## Gate before third-party provider selection

For the intended deployment, document:
- controller/processor roles, purposes and lawful bases;
- participant notice, refusal, objection and withdrawal behavior;
- employment/customer/student power imbalance;
- Article 9 and biometric-identification assessment;
- exclusion of workplace/education emotion inference;
- DPIA determination and accountable decision-maker;
- data egress, recipients, countries, transfer mechanisms and subprocessors;
- retention/deletion for raw data, derivatives, backups and exports;
- model training and secondary-use controls;
- rights handling and security evidence.

Candidate workflow states: not assessed, blocked, conditionally acceptable for synthetic-data evaluation, approved for a defined deployment. These are not legal conclusions. Record approver, scope, evidence, date, review trigger and residual risk.

## Proposed research constraints (not accepted policy)

1. Use synthetic or project-controlled participants for fixtures.
2. Do not send real meeting audio/video to third parties during an unapproved spike.
3. Do not create voiceprints, face templates or cross-meeting biometric identity links in baseline work.
4. Do not infer emotions, attention, engagement, productivity, agreement or performance as baseline observations.
5. Keep raw media, transcripts, platform assertions, human annotations and downstream interpretations distinct.
6. Do not select a provider or architecture until the deployment profile and controls are sufficiently specified.

## Open questions

Which deployment profile is intended initially? Is the first demonstrator synthetic-only? Which data classes are transient, retained, exportable or deletable? Who can approve a deployment-specific gate? How does deletion propagate through provenance-linked derivatives?

## Sources checked 14 November 2026

- GDPR: https://eur-lex.europa.eu/eli/reg/2016/679/oj
- AI Act: https://eur-lex.europa.eu/eli/reg/2024/1689
- EDPB Guidelines 05/2020 on consent: https://www.edpb.europa.eu/documents/guideline/guidelines-052020-on-consent-under-regulation-2016679_en
- CNIL, telework security and communication tools: https://www.cnil.fr/fr/les-conseils-de-la-cnil-pour-mettre-en-place-du-teletravail
- CNIL, workplace screen capture/video coupled with call recording: https://www.cnil.fr/fr/lenregistrement-video-ou-la-capture-decran-couple-lenregistrement-des-conversations-telephoniques

No lawful basis, consent model, controller/processor allocation, deployment profile, region, provider, retention period or production architecture is selected.
