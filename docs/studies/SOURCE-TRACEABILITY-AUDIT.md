# Study — External source and version traceability audit

**Status:** source-inventory audit, 14 November 2026.  
**Decision status:** no vendor or platform selected.  
**Scope:** external references in the current study catalogue. This audit records traceability coverage; it is not a claim that every product capability has been independently reproduced.

## 1. Audit method

For each study, identify external URLs, determine whether the source is primary/official or a foundational standard, record a retrieval/check date, and record a product/API/SDK/standard version when the source makes one explicit. Do not invent a version when a rolling documentation page does not publish a stable version identifier.

A source date and version answer different questions:
- retrieval date establishes when the source was consulted;
- product/API/SDK version identifies the interface or release described;
- a rolling documentation page may have a retrieval date but no stable version;
- a regulation or formal standard should be identified by instrument/recommendation/version rather than treated as software.

## 2. Inventory

The audit identified 92 external URL references across eight study documents. Three documents in the current study catalogue contain no external URL list because they are project-authored conceptual or procedural material, rather than comparative claims about a third-party interface.

| Study | External references | Traceability status |
|---|---:|---|
| ADJACENT-TOOLS.md | 12 | Retrieval date on each source; API/SDK versions not pinned where pages are rolling |
| DATA-EGRESS-AND-PRIVACY-GATE.md | 5 | Source section checked 14 Nov 2026; legal instrument numbers and EDPB guideline identifier recorded |
| DATA-PROTECTION-AND-GOVERNANCE.md | 12 | Retrieval date added; regulation identifiers and dated CNIL documents identified where stated |
| PLATFORM-CAPABILITY-MATRIX.md | 17 | All official platform links dated 14 Nov 2026; rolling API/SDK versions explicitly not pinned |
| PROVENANCE-TIME-EVENT-STANDARDS.md | 5 | W3C recommendation dates, Allen publication and CloudEvents 1.0.2 release line identified; working draft distinguished |
| REFERENCE-ENVIRONMENTS.md | 12 | Official project documentation checked 13 Nov 2026; rolling project docs/SDK versions not pinned |
| TEMPORAL-AND-REVISION-SEMANTICS.md | 5 | Sources checked 14 Nov 2026; foundational publication and W3C recommendation identities recorded |
| VIDEOCONFERENCING-PLATFORMS.md | 24 | Retrieval date on each volatile platform/provider reference; product/API versions not pinned where the source page does not state one |

The three documents without external URL lists are:
- CAPTURE-EVALUATION-PROTOCOL.md — MACLE's proposed comparative test protocol;
- CAPTURE-STRATEGIES.md — conceptual comparison; vendor examples now point to the official references in ADJACENT-TOOLS.md;
- MEETING-OBSERVATION-CATALOG.md — vendor-neutral observation-domain catalogue.

## 3. Corrections and traceability improvements

- Corrected an invalid Zoom webhook documentation hostname in VIDEOCONFERENCING-PLATFORMS.md to the official developers.zoom.us Meetings events page.
- Added retrieval dates to the official platform sources in PLATFORM-CAPABILITY-MATRIX.md.
- Added retrieval dates and document/instrument identifiers to DATA-PROTECTION-AND-GOVERNANCE.md.
- Confirmed the CNIL pages on personal data, sensitive data, legal basis, legitimate interest, employee activity monitoring and DPIA, plus the HR reference framework and voice-assistant white paper, resolve to official CNIL resources.
- Connected vendor examples in CAPTURE-STRATEGIES.md to the official source inventory in ADJACENT-TOOLS.md.
- Retained explicit version uncertainty for rolling vendor documentation rather than inferring SDK/API versions from a current web page.

## 4. Known limitations and remaining work

1. A retrieval date does not prove that every claim on a page is supported. Capability statements still need claim-to-source mapping and periodic review.
2. Many official vendor pages do not pin a release version in the page URL or content. Where the API has a versioned path (for example, Google Meet REST v2), record that path-level version; where not stated, keep “not pinned”.
3. Some documentation is mutable on branches such as GitHub main/master. For reproducible future comparisons, pin a commit or release tag when one exists and retain the retrieval date.
4. Product plan, tenant, account, host, regional and permission conditions can change independently of SDK versions. These must be recorded in a test environment, not inferred from documentation alone.
5. The source inventory does not replace a link checker or a claim-level review. A future automated audit should distinguish HTTP resolution, redirect destination, official-domain ownership, version pinning and claim coverage.

## 5. Review cadence proposal

Recheck volatile platform and provider references:
- before selecting a platform or capture provider;
- before a technical spike uses a documented API path;
- when a provider announces an API/SDK major version or permission-policy change;
- at least once per major research milestone.

This cadence is proposed, not adopted policy.

## 6. No decision made

This audit does not establish that a platform capability works in MACLE, select a provider, or adopt a release version. Empirical verification remains separate and is tracked by issue #5.
