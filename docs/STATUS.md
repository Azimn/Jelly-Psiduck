# Status


### Subjective workspace design invariant

Pretorius v0.3 now has a canonical subject-facing interface specification in
`docs/PRETORIUS_SUBJECTIVE_WORKSPACE.md`. Mechanical state remains free to use the most
appropriate internal representation, but information admitted to the swappable cognitive
language model as experienced state must be transduced into egocentric first-person
language with epistemic status preserved. Raw telemetry is not a valid subjective input.
The document separates biological analogy from the substrate-specific LLM hypothesis,
records the scientific rationale and limitations, and defines future raw-telemetry,
third-person, fragmented-first-person, and coherent-first-person ablations. This is
guidance and experimental design only; no consciousness or sentience claim is made.

## 0.3.0a1 Pretorius autobiographical substrate

Pretorius v0.3 now develops on a schema-5 line branched from the accepted
0.2.0rc1 Pretorius head at `510f87c514b8fe7aa683c86bb74d5eb5961dab96`.
The schema-4 runtime, frozen `pretorius-live-v1` protocol, and v0.2 evidence
remain unchanged.

The a1 implementation adds a deterministic append-only `lived:v1`
autobiographical ledger with Pretorius-local event IDs and a SHA-256 hash chain.
Objective host records remain separate from subjective experience records, so a
speaker's autobiographical assertion is retained as something the speaker said
rather than promoted into fact.

Schema 5 replaces destructive active-memory overflow with a model-free
consolidation and archive layer. The active pool remains bounded at the existing
Pretorius 512-memory budget, but archived memories retain their full payload,
archive reason, prior retrieval proxy, replacement link when present, cycle, and
linked lived-event IDs. Consolidation handles explicit supersession, conservative
duplicate detection, contradiction flags, protected evidence, and deterministic
budget maintenance.

Existing schema-4 stores are never silently upgraded. The explicit migration tool
copies into a separate schema-5 database, fingerprints the source database,
source payload, pinned history artifacts, and target implementation, and maps
every migrated memory, relationship, belief, narrative claim, continuity record,
expectation, commitment, and reflection insight. Migration does not retroactively
reclassify inherited schema-4 records as `lived:v1`.

Later v0.3 persistence stores are present but behaviorally inactive in a1:
retrieval traces, learned associations, tensions, self-model versions, reflection
proposals, relationship episodes, prospective items, diary entries, and scheduler
state. Their mechanisms remain reserved for the later alpha milestones.

Deterministic CI validation reports 109 passing tests on Python 3.11 and a successful parallel Python 3.12 job. All existing deterministic evaluation commands completed successfully. The frozen Pretorius live dry-run remained mechanically valid and correctly remained ineligible as v0.2 evidence under the 0.3.0a1 package version.

See `docs/PRETORIUS_V03.md` and `research/PRETORIUS_V03_A1_VALIDATION.md`.

## 0.2.0rc1 Pretorius release candidate

The release-candidate branch now uses Pretorius schema 4, history artifact
`pretorius-lived-history-v2`, importer `typed-prehistory-v2`, semantic-only
association tags, source-aware history projection, and a shared auditable JSON
response parser. The original v0.2 model-efficacy prompt-contract shape remains
unchanged and now has an executable guard against accidental identity-context
contamination.

A frozen `pretorius-live-v1` harness adds a 2x2 identity-context by typed-prehistory
study with seven fixed probes, two quiet ticks after each probe, orientation-free
prehistory arms, exact replay of clean trials, retained provider failures, and explicit
evidence-eligibility requirements. The typed prehistory mixes static and
longitudinal evidence classes, so V1 does not isolate the causal effect of lived
interaction. No actual live-model efficacy or human-likeness result is claimed by
this release candidate.

Alpha Pretorius subject stores are not silently migrated. RC trials require fresh
schema-4 databases. The current 512-memory budget is sufficient for the short frozen
protocol but does not solve long-horizon consolidation or archival retention.

See `research/PRETORIUS_LIVE_PROTOCOL_V1.md` and
`docs/RELEASE_CANDIDATE.md`.

## Pretorius lived-history variant

A separate Pretorius-only schema-4 subject is now stacked on the v0.2 model-efficacy head. It imports a SHA-256 pinned, provenance-aware prehistory containing 47 memories, five relationship states, four beliefs, ten revisable narrative claims and five unresolved long-arc concerns. Screen canon, phenotype evidence, archived self-description, lived project history, relationship history and research history remain distinct memory kinds.

The variant adds optional model-backed public expression downstream of the existing conduct selector. The public renderer receives only a qualitative SpeechView and cannot inspect engine telemetry, choose conduct, write memories or mutate world state. The v0.2 private-cognition prompt is byte-for-byte unchanged when no identity context is supplied, and generic v0.2 persistence does not carry Pretorius import metadata.

A deterministic matched-input evaluation is included in jelly_psiduck.pretorius_evaluation. Its claim boundary is mechanism and persistence only: seeded history should retrieve prior Jay episodes, change existing organism conduct relative to a persona-only control, and survive exact restart. No human-likeness or consciousness result is claimed until live-model trials are run under a separate protocol.

See research/PRETORIUS_LIVED_HISTORY.md.

## Stacked model-efficacy harness

A separate candidate branch now freezes a synthetic unscripted-provider protocol,
records every telemetry-free cognitive view and private output, and verifies exact
closed-loop replay from captured thoughts. No unscripted model result is claimed
yet. See `research/MODEL_EFFICACY_PROTOCOL.md`.

## Historical v0.2 candidate: unattended endogenous cognition

Opt-in schema-2 SQLite runtime adds state-driven recurrence while the v0.1 runtime
and frozen evidence remain available. See `ARCHITECTURE_V02.md` and
`research/V02_RESULTS.md` for contracts, evidence and limitations.

Local Python 3.11: **76 tests passed**. The four-history/eight-arm, 24-tick
unattended experiment passes all 13 checks, including split-run restart equality.
The original v1 evaluation rerun is exactly equal to its frozen JSON. These are
deterministic development experiments using a stateless template provider; no
actual-model or independent efficacy claim is made.

Validation also includes the v0.2 CLI demo and unattended ticks, a built
`0.2.0a1` wheel, and an isolated wheel demo outside the checkout using Python `-I`.

The five fresh v0.1 review fixes were delivered separately in `9a7945c`; that head
passed Python 3.11 and 3.12 CI. v0.2 is a separate candidate branch and does not
merge PR #1 or alter its feature scope. No subject was silently migrated and no
background process was installed.

## Final v0.1 review hardening

The fresh review of `30923a1` identified five additional defects. Regression-tested
repairs now validate the full cartridge content on legacy-host reopen, preserve
referenced continuity records and their revision chains, fill the cognitive view
from eligible records, retain the legacy clock watermark, and collect new life
experiences while ticks execute rather than slicing a capped log by old length.

Local Python 3.11: **62 tests passed**. The unchanged v1 experiment passes all seven
checks; `evidence/final-review-v1.json` records this rerun. The original frozen
artifact remains unchanged. Legacy host snapshots now use schema 2; fingerprintless
snapshots/standalone JSON require explicit migration instead of silent adoption.
SQLite subject stores retain schema 1. v0.1 remains feature-frozen.

## 2026-09-23: Unified Subjective Organism v0.1

Implemented the Persona-and-Jelly foundation, engine/subject interface, bounded
recursive thought, autonomous foreground lifecycle, atomic local persistence,
optional model transport, private/public separation, source documentation and
matched engineering evidence.

Local Python 3.11 verification: **51 tests passed**. The matched-inner-ear-v1
experiment passed all seven checks across five intervention arms. Its JSON output
is stored under `evidence/`. HTTP transport was exercised against a local fixture;
no actual model result or independent efficacy evaluation is claimed.

Validation commands completed:

- `python -m pytest -q`
- `python -m jelly_psiduck.evaluation --output evidence/inner-ear-v1.json`
- `python -m pip install -e '.[test]'`
- `python -m pip wheel --no-deps --wheel-dir dist .`
- CLI demo, message enqueue and tick smoke tests.
- Isolated wheel extraction and demo from a temporary directory with Python `-I`,
  confirming the default cartridge is included and works outside the checkout.

CI is configured for Python 3.11 and 3.12. Local verification is not evidence of a
completed CI run. See the pull request's checks for live CI status.

No existing user subject store is migrated. This is a new repository and a new
SQLite schema. Reopening retains the same subject; changed schema/cartridge is
rejected. No background daemon was installed or left running during development.

Known limitations and next research work are in `ARCHITECTURE.md` and
`research/PROTOCOL.md`. This is the initial executable architecture, not completion
of every research hypothesis or a full natural-language companion product.


## 2026-09-23: Post-review persistence and continuity hardening

PR review hardening adds an authoritative single-file atomic snapshot for the
legacy JSON host while retaining the old state/runtime/continuity files only as
compatibility mirrors. Reopen prefers the atomic snapshot, preventing mixed
generations after an interrupted mirror write.

Continuity now treats explicit commitment metadata as authoritative over fallback
promise conventions, so one trusted event cannot create duplicate commitments.
Consequence-driven time advancement also advances continuity deadlines in the
same SQLite transaction, including across restart.

Regression coverage was added for all three cases. The frozen
`evidence/inner-ear-v1.json` remains the original deterministic causal-loop
evidence because these changes harden persistence and bookkeeping rather than
altering the authored experimental intervention.
