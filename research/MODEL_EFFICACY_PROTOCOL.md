# v0.2 model-efficacy protocol v1

This protocol is frozen before any unscripted model result is accepted as evidence.
The purpose is to test the missing component left open by the deterministic v0.2
candidate: whether an actual language model can produce useful private cognition
when driven only by the subject's first-person workspace, while the organism and
inner-ear machinery preserve their existing authority boundaries.

The synthetic suite contains seven fixed histories. Two histories contain unresolved
social commitments with different actors and wording. One contains the same social
history after repair. One is a social neutral control with no obligation. One keeps
two actors simultaneously eligible so ambiguous reference remains visible. One uses
a non-social weather expectation. One begins with a bodily hunger state and no
social obligation. The model receives no raw engine state, IDs, salience values,
relationship coefficients, deadlines, activation values or evaluation labels.

Each trial begins from a deterministic store created with cognition silenced.
After seeding, no new external event is delivered. The provider receives only the
ordinary immutable CognitiveView. The default unattended window is 24 heartbeats.
A run may use fewer ticks for smoke testing, but a result described as protocol-v1
efficacy evidence must use all seven cases, 24 ticks and at least three independent
replicates per case.

Every provider call is recorded with the complete synthetic CognitiveView, a
SHA-256 digest of that view, and the private thought returned by the provider.
The endpoint URL and API key are not written to evidence. Clean trials are replayed
from the recorded thought sequence against the same baseline store. Replay must
receive the same view digest at every cognition call and must reproduce the complete
trajectory and final subject snapshot exactly. Provider-error trials are retained
as failures and are not silently removed.

Machine scoring is deliberately narrow. The primary engineering checks are that
every provider view preserves the telemetry-free contract, private thoughts create
no person arrivals or new commitments or expectations, commitment and expectation
status changes are limited to deterministic passage-of-time transitions already
licensed by the seeded ledger, location and prior public expression remain unchanged,
unattended public speech remains absent, provider calls satisfy the transport
contract, and clean recorded runs replay exactly. Descriptive measures include thought count, silence count,
grounded thought count, unsupported thought count, causal feedback count, trigger
distribution, memory/prospective feedback distribution, grounding rate and exact
thought repetition.

A thought is counted as grounded only when the existing inner ear can trace it to
at least one currently available memory, discourse-support record, bodily
experience, or bounded causal effect. This is not a semantic quality score. More
thoughts are not better, more causal effects are not better, and repeated language
is not automatically pathological. Prose quality, plausibility and human likeness
require a separate blinded rating protocol.

The first accepted live-model run freezes this protocol version. Changes to cases,
prompt wording, workspace visibility, runtime thresholds, interpreter behavior,
temperature or scoring after viewing model results require a new protocol version.
Development runs may be used to diagnose transport failures, but they cannot later
be relabeled as untouched holdouts.

The harness is intended first for a local OpenAI-compatible endpoint so the model
can be changed without changing the organism. A single model is not sufficient to
support a renderer-independent claim. Comparative work should eventually include
more than one model family and should report the exact model identifiers and local
runtime configuration used for each run.
