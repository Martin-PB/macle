# Study — Data protection and governance considerations

**Status:** preliminary research baseline, 13 November 2026.  
**Jurisdictional lens:** European Union / France, because this is a relevant initial operating context; this document does not establish a universal legal framework.  
**Decision status:** no legal basis, consent model, retention period, hosting region, or deployment model selected.  
**Important:** this is product research, not legal advice or a compliance assessment for a particular deployment.

## 1. Why this is a separate workstream

MACLE's first operational domain involves videoconference situations. Depending on the capture path and processing choices, the system may handle participant names and account identifiers, voice, image, chat, shared documents, attendance, behavioral events, transcripts, inferred speaker attribution, and contextual observations.

The technical ability to collect a signal does not establish that a particular organization may collect it for a particular purpose. Platform permission, participant notice, consent, GDPR lawful basis, organizational policy, and national employment/privacy rules are separate questions.

This study therefore identifies design questions and safeguards. It does not decide whether a given meeting may be captured.

## 2. Personal data and derived data

The CNIL describes personal data broadly: information relating to an identified or identifiable natural person, including voice, image, and identifiers. Data derived from a meeting may remain personal data even when the original audio/video is no longer retained.

For MACLE, the data inventory must cover more than source media:

- platform participant IDs, names, email addresses, and account attributes;
- endpoint, device, network, and session identifiers;
- voice and image recordings;
- transcripts, captions, and diarization outputs;
- speaker-to-person links and confidence values;
- chat messages, reactions, shared links, files, and screen contents;
- attendance, presence, interaction, and timing events;
- extracted topics, action items, decisions, sentiment-like labels, or other interpretations;
- user corrections, annotations, and provenance linking an assertion to its sources.

Pseudonymization does not automatically make data anonymous. A stable pseudonymous identifier or a rich combination of meeting observations may still permit identification or singling out.

## 3. Voice, image, and biometric distinction

The distinction between ordinary audio/video processing and biometric identification must be explicit.

- A voice recording or image can be personal data because it relates to an identifiable person.
- The CNIL explains that biometric data under the GDPR includes physical, physiological, or behavioral characteristics processed for the purpose of uniquely identifying a person.
- The CNIL's voice-assistant guidance describes voice templates used to recognize a person across interactions as biometric data.
- Therefore, speech-to-text, voice activity detection, or diarization must not automatically be labelled biometric identification. Conversely, a feature that builds or uses voiceprints to recognize a person uniquely requires a separate and much stricter assessment.
- Audio/video may also reveal or allow inferences about sensitive matters. The data inventory and risk analysis must consider the actual purpose and outputs, not just the file format.

**Design implication:** separate speaker segmentation from identity recognition. A diarization result such as “speaker 2” is not a verified human identity and must not silently become one.

## 4. Purpose and lawful basis

Under the GDPR, processing needs a lawful basis under Article 6, and purposes must be specified, explicit, and legitimate. The basis must be assessed for each actual purpose and deployment context.

Potential purposes that must not be conflated include:
- live accessibility or captioning;
- meeting notes and action-item extraction;
- search and retrieval of meeting records;
- organizational memory and continuity;
- compliance recording;
- performance monitoring or employee evaluation;
- product analytics;
- model evaluation or training;
- research and development.

A purpose that might justify one processing operation does not automatically justify another. Reusing meeting content for model training, employee evaluation, or unrelated analytics is not simply a technical extension of note-taking.

The CNIL explains that legitimate interest requires a balancing exercise and appropriate safeguards. Its guidance on AI and lawful basis highlights the particular difficulty of relying on employee consent where there is a power imbalance. The CNIL's HR reference framework also says employees are rarely able to give, refuse, or withdraw consent freely because of the dependency inherent in the employment relationship.

**Open issue:** MACLE cannot choose a single lawful basis for all users. The controller must determine the basis in the context of the purpose, people, and deployment.

## 5. Transparency, choice, and participant control

The design should be capable of supporting clear information before capture, including:
- who operates the processing and who is responsible for it;
- the purpose(s) and categories of data;
- whether capture is live, recorded, or post-meeting;
- which processors/providers receive data;
- whether raw media, transcripts, and derived observations are retained;
- retention periods or criteria;
- how people can exercise applicable rights and contact the responsible organization;
- whether any automated inference or profiling is performed.

The system should also investigate controls for:
- visible capture state;
- pausing and stopping capture;
- participant or host opt-out where applicable;
- excluding particular content or participants where technically feasible;
- recording a refusal or withdrawal without turning it into a hidden failure;
- avoiding capture by default when the configured purpose does not require it.

These are design capabilities to investigate, not a claim that one universal consent button makes a deployment lawful. Consent is only one possible lawful basis and must be freely given, specific, informed, and unambiguous where relied upon.

## 6. Necessity, proportionality, and minimization

The GDPR's principles include purpose limitation, data minimization, accuracy, storage limitation, integrity/confidentiality, and accountability. Article 25 requires data protection by design and by default.

For each purpose, ask:
1. What exact output is needed?
2. Which input signals are strictly necessary?
3. Can a less intrusive signal or lower fidelity satisfy the purpose?
4. Is raw media needed at all after extraction?
5. Can processing occur locally or transiently?
6. Can the system avoid collecting unrelated windows, notifications, or background audio?
7. Can access be restricted by meeting, role, purpose, and time?
8. How can a person challenge an incorrect attribution or derived assertion?

A transcript use case may not need continuous video retention. A screen-change observation may not need a permanent copy of the entire desktop. These are examples for necessity analysis, not predetermined product rules.

## 7. Retention, deletion, and derived-data lineage

The GDPR's storage-limitation principle means retention must be tied to purpose; a universal indefinite event history is not a safe default.

MACLE should distinguish lifecycle policies for:
- raw audio/video;
- transient media buffers;
- platform recordings;
- transcripts and captions;
- extracted events and features;
- identity mappings and speaker attribution;
- user annotations and corrections;
- backups, exports, caches, and provider-side copies.

A deletion workflow must be evaluated end-to-end. Deleting a recording while retaining transcript segments, speaker embeddings, extracted personal attributes, or copied exports may leave substantial personal data behind.

**Architecture questions:**
- Can every derived observation refer to its source artifacts and processing run?
- Can the system enumerate descendants of a source item?
- Can deletion, restriction, or correction propagate through derived artifacts and external processors?
- Can a legally required hold or preservation exception be represented without silently defeating normal deletion?
- Can the system prove what was deleted, retained, or made inaccessible, and when?

The system should not promise perfect erasure from backups or third-party systems until the lifecycle and provider contracts are verified.

## 8. Roles, processors, and third-party providers

The controller/processor relationship depends on who determines the purposes and essential means of a particular processing operation. It cannot be inferred solely from whether a component is called a SaaS provider, connector, or SDK.

For every external service, establish:
- whether it acts as processor, independent controller, or another role for each operation;
- whether it reuses data for its own purposes;
- data categories and purposes;
- subprocessors and onward transfers;
- processing locations and transfer safeguards;
- security measures and incident obligations;
- assistance with data-subject rights;
- deletion/return at end of service;
- audit and evidence rights.

A provider's claim that it is “GDPR compliant” is not a substitute for reviewing the actual data flows, contractual terms, subprocessors, and configuration.

## 9. Security and impact assessment

Security controls should be proportionate to the sensitivity, volume, and consequences of the data. Candidate controls include:
- encryption in transit and at rest;
- scoped and short-lived credentials;
- least-privilege access to meetings and artifacts;
- tenant and meeting isolation;
- explicit separation of raw media from derived observations;
- audit trails for access, export, correction, and deletion;
- secure secret handling and key management;
- retention enforcement and backup lifecycle controls;
- protection against accidental capture of unrelated content;
- incident response and provider breach notification processes.

The CNIL explains that a data protection impact assessment (DPIA/AIPD) is required when processing is likely to result in high risk to individuals' rights and freedoms. It should be assessed before processing begins, based on the actual nature, scope, context, purposes, and risks. The product should make it possible for a deploying organization to understand its data flows and supply evidence for its own assessment; a vendor-level assessment does not automatically replace the controller's assessment.

## 10. Emotion inference in workplace and education contexts

The EU Artificial Intelligence Act (Regulation (EU) 2024/1689), Article 5(1)(f), prohibits the placing on the market, putting into service for that specific purpose, or use of AI systems to infer emotions of natural persons in workplace and education contexts, except where the system is intended for medical or safety reasons.

This is a distinct issue from ordinary meeting transcription, diarization, or event detection. It is also not a blanket prohibition on every analysis of audio or video: whether a feature is an emotion-inference system depends on its purpose and operation and requires legal assessment. The Act's recitals explain concerns about scientific basis, reliability, generalisability, discrimination, and the power imbalance in work and education settings.

**Conservative product hypothesis to assess:** do not include emotion or intention inference in the initial operational feature set for workplace or education meetings. Do not relabel emotion inference as an “acoustic descriptor” or “engagement signal” to avoid the issue. Keep neutral, observable event descriptions (for example, speech interval, overlap, pause, volume level) conceptually distinct from claims about a person's emotional state or intention.

This is a research finding and a proposed restriction for legal review, not an adopted MACLE requirement or a substitute for counsel's assessment of a concrete feature and context.

## 11. Product-neutral design questions

These questions should be answered before an operational deployment is approved:

| Area | Question |
|---|---|
| Purpose | Which exact purpose is enabled for this meeting and who authorized it? |
| Role | Who is controller, processor, and subprocessor for each operation? |
| Legal basis | What basis applies to each purpose and category of person? |
| Transparency | What information is provided, when, and through which interface? |
| Capture | Which signals are necessary; which are explicitly disabled? |
| Control | Who can start, pause, stop, or object to capture? |
| Identity | Are people, platform accounts, endpoints, sessions, and speaker labels kept distinct? |
| Inference | Which outputs are algorithmic, and how can they be challenged? |
| Retention | What policy applies independently to raw and derived data? |
| Deletion | How are descendants, exports, backups, and providers handled? |
| Security | Who can access which data, for what purpose, and with what audit evidence? |
| Transfers | Where is data processed and which providers/subprocessors receive it? |
| Impact | Is an AIPD/DPIA required for this deployment? |

## 12. Official references

### European Union
- [Regulation (EU) 2016/679 — GDPR, especially Articles 5, 6, 9, 25, 28, 32 and 35](https://eur-lex.europa.eu/eli/reg/2016/679/oj)
- [Regulation (EU) 2024/1689 — Artificial Intelligence Act, Article 5(1)(f) and recitals 44–45](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
- [GDPR consolidated text — EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02016R0679)

### CNIL
- [Personal data: definition](https://www.cnil.fr/fr/definition/donnee-personnelle)
- [Sensitive data: definition](https://www.cnil.fr/fr/definition/donnee-sensible)
- [Lawfulness and legal bases](https://www.cnil.fr/fr/assurer-que-le-traitement-est-licite)
- [Legitimate interest](https://www.cnil.fr/fr/les-bases-legales/interet-legitime)
- [Employee activity monitoring and proportionality](https://www.cnil.fr/fr/controle-de-lactivite-des-personnes-employees)
- [HR data processing reference framework](https://www.cnil.fr/sites/default/files/atoms/files/referentiel_grh_novembre_2019_0.pdf)
- [DPIA/AIPD: what to know](https://www.cnil.fr/fr/ce-quil-faut-savoir-sur-lanalyse-dimpact-relative-a-la-protection-des-donnees-aipd)
- [Risk management and DPIA](https://www.cnil.fr/fr/gerer-les-risques)
- [Voice assistants and biometric voice identification](https://www.cnil.fr/sites/default/files/atoms/files/cnil_livre-blanc-assistants-vocaux.pdf)

## 13. No decision made

This study does not select a lawful basis, consent mechanism, retention period, hosting location, capture default, or provider. It does not conclude that MACLE may record a particular meeting. Those matters depend on the actual controller, purpose, participants, deployment context, and applicable law, and require appropriate legal/privacy review.
