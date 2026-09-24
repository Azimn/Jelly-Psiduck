# Status

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
