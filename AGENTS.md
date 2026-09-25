# Jelly-Psiduck agent instructions

Read README.md, docs/ARCHITECTURE.md, docs/STATUS.md, docs/SOURCES.md and
research/PROTOCOL.md before substantive changes.

For v0.2 also read docs/ARCHITECTURE_V02.md, research/V02_PROTOCOL.md and
research/V02_RESULTS.md. v0.1 remains a frozen comparison apparatus. New behavior
uses the explicit v0.2 runtime and separate schema-2 SQLite stores; never silently
migrate the default v0.1 runtime or overwrite its frozen experimental evidence.

For unscripted-provider trials also read research/MODEL_EFFICACY_PROTOCOL.md before
changing the harness. After the first accepted live-model result, do not change the
case set, prompt contract or scoring under the same protocol identifier. Increment
the protocol version instead. Never persist API keys or endpoint URLs in evidence.

For Pretorius live-model trials also read research/PRETORIUS_LIVE_PROTOCOL_V1.md.
Protocol-v1 evidence must use history v2 with the pinned digest and importer,
workspace orientation disabled, all four fixed 2x2 conditions, the fixed probe
order, at least three replicates per condition, and an immutable model fingerprint.
Do not relabel development or transport-diagnostic runs as evidence.


For any Pretorius v0.3 or later work, read `docs/PRETORIUS_V03.md` and
`docs/PRETORIUS_SUBJECTIVE_WORKSPACE.md` before changing architecture, prompts,
workspace projection, cognition, memory, body/interoception, appraisal, relationships,
or model-provider boundaries. The Subjective Workspace Invariant is a core experimental
constraint: mechanical state may use any appropriate representation, but state admitted
to the cognitive language model as Pretorius's experienced state must first be rendered
as an egocentric first-person linguistic representation with epistemic status preserved.
Never expose engine telemetry or raw mechanical control values to the cognitive model as
experienced state. The first-person stream must be causally upstream of cognition, not
decorative post-hoc narration. Do not silently remove or weaken this invariant; changes
require a versioned ablation or protocol that directly tests the alternative.

- Persona-and-Jelly remains the organism foundation and sole conduct authority.
- The engine simulates the organism; the subject experiences the consequences.
- Cognition receives only immutable subjective views, never engine telemetry.
- Thoughts are private cognitive occurrences, not observations, promises or actions.
- Preserve source distinctions, support traces, atomic persistence and restart identity.
- Use the trusted host API for world facts; natural-language messages are percepts.
- Keep character content in cartridges and model selection in host configuration.
- No mandatory network/model dependency for deterministic tests.
- Use the existing engine selector; no parallel planner or independent subject.
- Test consequences in later state and after restart, with negative ablations.
- Update docs/STATUS.md and research evidence in the same substantive phase.
- Preserve donor provenance and distinguish engineering tests from independent evidence.

Verification: `python -m pytest -q` and
`python -m jelly_psiduck.evaluation --output evidence/local-inner-ear.json`.
For v0.2 also run `python -m jelly_psiduck.endogenous_evaluation --output evidence/local-v02.json`.

For the stacked efficacy harness also run `python -m jelly_psiduck.model_evaluation --dry-run --case unresolved-mara --case body-hunger --ticks 8 --output evidence/local-model-harness.json`.

For the Pretorius release-candidate harness also run:
`python -m jelly_psiduck.pretorius_live --dry-run --replicates 1 --output evidence/local-pretorius-live.json`.
