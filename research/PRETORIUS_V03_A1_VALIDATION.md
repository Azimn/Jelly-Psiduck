# Pretorius v0.3.0a1 deterministic validation

## Scope

This record covers engineering validation of the Pretorius v0.3.0a1
autobiographical substrate. The branch begins exactly from Pretorius 0.2.0rc1
commit `510f87c514b8fe7aa683c86bb74d5eb5961dab96`. It does not alter the frozen
schema-4 Pretorius runtime, the `pretorius-live-v1` protocol, or accepted v0.2
evidence.

The validation is deterministic development evidence. No live language-model
trial is represented here, and no claim of consciousness, sentience, human
likeness, model-independent identity, or long-horizon developmental success is
made from these checks.

## Result

At v0.3 code head `0b0689937a8ea530ef0fa035ed29f37ea34987fa`, GitHub Actions
completed successfully on Python 3.11 and Python 3.12. The repository test suite
reported 109 passing tests on Python 3.11. The same workflow also completed the
existing inner-ear evaluation, endogenous evaluation, dry-run model-efficacy
harness, Pretorius history evaluation, and frozen Pretorius live dry-run on both
Python versions.

The frozen `pretorius-live-v1` dry-run remained mechanically valid. Its
`evidence_eligible` field remained false because the development package is
`0.3.0a1`, not the frozen `0.2.0rc1` release contract. This is intentional
scientific isolation.

## a1 properties exercised

The tests establish the implemented engineering contracts for this milestone:
fresh schema-5 initialization preserves the pinned typed prehistory; post-
instantiation messages append deterministic hash-chained `lived:v1` events;
speaker assertions are represented as assertions rather than promoted into
autobiographical fact; restart preserves the ledger; active-memory overflow
archives complete records rather than deleting them; identical consolidation
inputs produce canonical byte-equivalent persisted state; open continuity items
protect their supporting memory evidence transitively; schema-4 migration is
explicit, copy-only, fingerprinted, and lossless for the inherited subject
state; and schema-4 control stores are not silently seeded during migration.

The migration and replay checks also preserve the boundary between reconstructed
history and post-instantiation lived history. Migrated schema-4 state begins with
an empty `lived:v1` event ledger rather than retrospectively converting earlier
records into lived events.

## Remaining boundary

The reserved schema-5 stores for retrieval traces, learned associations, tensions,
self-model versions, reflection proposals, relationship episodes, prospective
items, diary entries, and scheduler state are intentionally inactive in a1.
Their causal mechanisms and the model-swap, post-instantiation fork,
false-memory, anchoring, and endurance protocols remain later versioned work.
