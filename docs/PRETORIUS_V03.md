# Pretorius v0.3: Historical Continuity and Self-Consolidation

## Release boundary

Pretorius v0.3 is a new experimental line beginning from the accepted Pretorius 0.2.0rc1 head at commit `510f87c514b8fe7aa683c86bb74d5eb5961dab96`. The schema-4 runtime, `pretorius-live-v1` protocol, and v0.2 evidence remain frozen. Schema 5 is opened only by the new v0.3 runtime. Existing schema-4 databases require the explicit migration command and are never rewritten in place.

The research boundary remains strict. Reconstructed history is the initial condition. Events that occur after schema-5 instantiation are lived system history. Migration preserves existing schema-4 state but does not retroactively label it as `lived:v1`.

Pretorius and the blank developmental-subject experiment remain separate tracks. Pretorius tests preservation, continuation, and historically traceable divergence of an inherited character. It does not simulate childhood development or attempt to explain the developmental origin of the phenotype.

## v0.3.0a1 scope

This alpha implements the autobiographical substrate only. It adds an append-only lived-event ledger, a non-destructive archive layer, deterministic model-free consolidation, schema-5 persistence scaffolding, and provenance-preserving schema-4 migration. Reflection proposals, learned retrieval usefulness, experienced association learning, tensions, relationship episodes, diary behavior, and adaptive scheduling have reserved persisted stores but are not behaviorally activated in this milestone.

Every lived event receives a deterministic Pretorius-local identifier and participates in a SHA-256 hash chain. The ledger stores an objective host record separately from the subject's experienced representation. A conversational assertion such as "remember when..." is therefore recorded as a statement made by the speaker, not promoted into autobiographical fact.

The current ledger provenance for post-instantiation events is `lived:v1`. Reconstructed prehistory remains in its existing typed `history:<evidence_class>` records. The two provenance families are not interchangeable.

## Active memory and archive

The schema-4 donor engine enforced its memory limit by sorting and destructively dropping lower-ranked records. The schema-5 Pretorius organism removes that deletion point. Memory growth is allowed inside the transaction, then the schema-5 subject runs a deterministic consolidation pass before commit.

The active pool remains bounded by the Pretorius 512-memory contract. Records that leave active retrieval are copied in full into `archive_records`, including the original memory payload, archive tick, consolidation cycle, prior retrieval proxy, archive reason, replacement link when applicable, and any linked lived-event IDs. Archived records are excluded from ordinary engine retrieval but remain recoverable by identifier.

Consolidation recognizes explicit supersession, structurally exact duplicates, and deliberately conservative near duplicates. Near-duplicate detection requires the same memory kind, creation tick, tags, and very high token overlap. Repeated experiences at different times are therefore retained as separate historical events. Structured contradiction tags are flagged for audit rather than automatically resolved.

Budget maintenance protects explicit protected IDs, narrative evidence, and memory links supporting currently active concern or expectation workspace records. Remaining candidates are archived using a deterministic retention ordering. No language model participates in consolidation.

## Schema 5 persistence contract

Schema 5 persists the autobiography metadata and event list, active memory index, archive records, consolidation journal and cycle, protected memory IDs, and the later-milestone stores for retrieval traces, learned associations, tensions, self-model versions, reflection proposals, relationship episodes, prospective items, diary entries, and scheduler state.

The active memory index is an auditable derived cache. On restore it must exactly match the ordered engine memory IDs. A memory ID may not exist simultaneously in the active pool and archive. The autobiographical hash chain is verified on every restore.

## Explicit migration

The migration command is:

```bash
jelly-pretorius-migrate-v03 schema4.sqlite3 schema5.sqlite3
```

Migration requires a distinct target path and refuses to overwrite an existing database. It fingerprints the source database bytes, canonical source payload, pinned history artifacts, and target implementation. The manifest contains identity mappings for every migrated memory, relationship, belief, narrative claim, continuity record, expectation, commitment, and reflection insight.

Migration copies the schema-4 engine, continuity state, workspace, import metadata, pending state, and other persisted subject state unchanged. The archive begins empty with the migrated active set intact. The lived-event ledger begins empty because schema-4 records are not retroactively reclassified as post-instantiation `lived:v1` events.

A migrated target is reopened through the schema-5 runtime and checked against the source engine, continuity state, and history-import metadata before migration succeeds.

## Runtime

The v0.3 entry point is:

```bash
jelly-pretorius-v03 init
jelly-pretorius-v03 status
jelly-pretorius-v03 say "Hello."
jelly-pretorius-v03 consolidate
jelly-pretorius-v03 archive MEMORY_ID
```

The existing `jelly-pretorius` command remains the schema-4 RC runtime. The existing `jelly-pretorius-study` command remains the frozen `pretorius-live-v1` study harness. Because the development package version is now `0.3.0a1`, the frozen v0.2 study harness cannot classify runs from this branch as release-matched v0.2 evidence.


## Subjective workspace invariant

The canonical guidance for Pretorius's subject-facing cognitive interface is
[`docs/PRETORIUS_SUBJECTIVE_WORKSPACE.md`](PRETORIUS_SUBJECTIVE_WORKSPACE.md).

Beginning with v0.3, this is a core experimental constraint rather than a style preference.
Underlying systems may use numerical, graph, symbolic, learned, procedural, or other
machine-efficient representations. Those representations are not Pretorius's experienced
state. Any information admitted to the cognitive language model as current subjective
content must first pass through a subjective-transduction boundary and arrive as an
egocentric first-person linguistic representation appropriate to its provenance,
uncertainty, temporality, and ownership.

The cognitive model must not receive engine telemetry or raw internal control values as
if those values were experiences. First-person workspace content must be causally upstream
of model cognition and may affect later retrieval, appraisal, association, memory,
intention, conduct, and inner-ear recurrence. Objective events, subjective renderings,
and later interpretations remain distinct records.

This rule is explicitly substrate-specific. The project does not claim that biological
human consciousness requires verbal first-person narration. Pretorius uses a language
model as a swappable cognitive organ, so the research question is whether a stable
first-person linguistic interface is a useful integration surface for this different
substrate. The invariant remains in force until a versioned ablation directly compares
it against alternatives such as raw telemetry, third-person prose, and fragmented
first-person representations.

## Determinism and claim boundary

Given identical persisted state, identical incoming events, and identical captured model outputs, schema-5 state is intended to replay exactly. Autobiographical IDs, hashes, archive choices, consolidation actions, and migration mappings are deterministic.

The a1 test suite covers typed-prehistory preservation, hash-chained lived events, false-memory assertion containment, archive preservation under overflow, exact consolidation replay across identical subjects, lossless explicit schema migration, restart persistence, and exact deterministic multi-turn state.

These are architecture and replayability claims only. This milestone does not establish consciousness, sentience, human likeness, model-swap continuity, long-horizon path dependence, learned retrieval usefulness, self-model development, or relationship development. Those require later versioned mechanisms and protocols.
