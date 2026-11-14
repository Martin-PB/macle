# Formal-method selection for MACLE capture

## Decision

Use a layered assurance strategy. No single formalism can establish the
correctness of the entire browser extension because Chrome, Google Meet,
operating-system media devices, and the download manager are external actors.

| Concern | Preferred method | Why it fits | What the result means |
|---|---|---|---|
| Asynchronous lifecycle and races | TLA+ / TLC | The extension is a transition system with nondeterministic event ordering, failure, retries, and stop/finalize paths | Exhaustive model-checking evidence for a finite abstraction |
| Larger or symbolic parameter spaces | Apalache | SMT-based symbolic checking complements TLC's explicit state enumeration | Bounded checking or inductiveness evidence under Apalache's supported fragment |
| Pure data and state invariants | Lean 4 | Useful for proving small propositions about typed session states, authorization tokens, artifact/manifest consistency, and state-transition preservation | Kernel-checked theorem about the formalized definitions |
| Static relations in session evidence | Alloy Analyzer | Useful for checking that session manifests, sources, artifacts, timestamps, hashes, and provenance links form structurally consistent finite instances | Counterexample or instance for the relational model; not a temporal proof |
| Event-sequence exploration against implementation | Stateful property-based testing | Generates interleavings and fault sequences that humans rarely write by hand | Executable test evidence, not proof |
| Browser API boundary | Playwright + Chromium synthetic media | Exercises real extension contexts, service worker, Offscreen document, permissions, downloads, and browser behavior | Integration-test evidence for the tested Chromium/OS configuration |
| Runtime fault detection | Explicit runtime assertions and structured lifecycle events | Detects divergence between expected and observed state in real sessions | Runtime evidence and diagnostics, not proof |

## Where Alloy may help

Use Alloy for the MACLE evidence graph rather than the recorder's asynchronous
lifecycle: session-to-source relations, artifact-to-manifest references,
provenance, modality availability, and consistency constraints across event
identifiers. Alloy is complementary to TLA+: it checks structural relations,
while TLA+ checks temporal behavior.

## What should be proved in Lean

Keep the theorem surface small and independent of Chrome internals.

1. A value representing a `Recording` state necessarily carries an explicit
   authorization witness and an Offscreen-ready witness.
2. A value representing a `Saved` session necessarily carries finalized media
   and manifest artifacts and successful completion evidence for both exports.
3. Every allowed abstract transition preserves the lifecycle invariants.
4. A manifest accepted by the shared Rust core satisfies the pure structural
   invariants encoded by the core's typed data model.

These theorems do not prove that JavaScript calls Chrome correctly. That
connection requires a refinement argument and adapter tests.

## What should be model-checked in TLA+

- No transition reaches Recording before authorization, Offscreen readiness,
  and a fresh stream identifier.
- The stream identifier is consumed at most once.
- The abstract single-session phase machine admits only one transition out of Idle. The JavaScript worker and Offscreen locks are separately checked by adapter case C-04; their refinement is not yet mechanically proved.
- Stop, tab closure, and navigation cannot skip finalization ordering.
- Saved is unreachable unless both finalized artifacts have completed downloads.
- A retained artifact is SHA-256 checked before any missing export is retried; hash mismatch blocks recovery without deleting the artifact.
- Under stated fairness assumptions, every accepted stop request reaches a
  terminal success or failure state.

TLC is the initial checker because the state space is finite and small.
Apalache is a complementary checker, not a replacement for understanding the
abstraction or its assumptions.

## Test strategy

Use stateful property-based tests to generate action sequences from the same
abstract transition vocabulary. Include:
- duplicate starts and starts while stopping;
- navigation or tab closure at every startup/finalization boundary;
- Offscreen creation delay and WASM initialization failure;
- expired stream IDs;
- recorder errors and rejected OPFS writes;
- user-cancelled, interrupted, delayed, and completed downloads;
- service-worker suspension/restart between every externally visible event.

Then replay failing sequences in Chromium and retain the trace as a regression
fixture. A trace is evidence of a counterexample in the implementation, not a
proof that all traces are safe.

## Assurance case

For each product claim, retain a linked record containing:
- claim identifier and precise statement;
- assumptions and environment scope;
- formal predicate or theorem;
- implementation mapping;
- checker/test identity and version;
- result, counterexample or test trace;
- known gaps and accepted risk.

Do not collapse tests, model checking, and theorem proving into one PASS label.
Report them as separate evidence classes.
