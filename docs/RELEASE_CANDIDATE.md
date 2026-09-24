# Jelly-Psiduck 0.2.0rc1

This release candidate is the first Pretorius build intended for controlled
live-model trials rather than only deterministic mechanism checks.

## Release-candidate changes

The Pretorius persistence envelope is schema 4. The default prehistory is
`pretorius-lived-history-v2`, pinned by canonical SHA-256 and importer version.
Provenance remains explicit in memory kinds but no longer participates as an
associative tag. This removes a retrieval confound in which records could become
related merely because they shared an evidence class.

Pretorius now uses a subject-specific capacity of 512 memories and 2,048 semantic associations while retaining top-k 4 retrieval. The generic v0.2 organism remains unchanged. The old 32-association toy cap would have retained only a small fraction of the 532 distinct semantic tag-pairs present in the current history seed.

History can now be imported without workspace orientation. The frozen live-study
protocol uses that mode so the treatment is durable state rather than six relevant
records preloaded into working memory. Source classes also survive the subjective
firewall as qualitative distinctions, so screen canon, legacy representation,
archived self-report, phenotype evidence, and lived project history are not all
rendered as equivalent autobiographical recollection.

Private and public model responses use the auditable
`single-text-json-v1` parser. It accepts exact JSON or one complete JSON code
fence and performs no semantic repair. Raw output, parse mode, and failure type are
available to study recorders. Public speech no longer receives the internal subject
identifier.

The frozen v0.2 model-efficacy harness now rejects identity-bearing or otherwise
mutated prompts before provider invocation while preserving its original prompt
contract and evidence shape.

The new `pretorius-live-v1` harness records package and implementation fingerprints
and freezes a 2x2 study of explicit identity context and the full typed prehistory,
with the cartridge and model held constant. Prehistory arms disable workspace
orientation. Seven fixed probes test continuity, self-contradiction, creator autonomy, collaborator disagreement, source bounding, path-dependence reasoning, and the opposite risk of memory anchoring. Clean runs must exact-replay.

## Compatibility

Do not open an alpha Pretorius database as an RC subject. Schema 4 intentionally
requires a fresh store. The older history artifact remains in the repository for
provenance, but v2 is the RC default.

Generic v0.1 and v0.2 subject contracts remain separate. The frozen v0.2
model-efficacy prompt text, cases, temperature, token ceiling, and scoring are not
silently repurposed for Pretorius.

## Claim boundary

The deterministic engineering checks can establish causal use of stored history,
source separation, persistence, and replayability. They do not establish
human-likeness or consciousness. The live V1 study tests utilization of curated, provenance-rich seeded prehistory.
Because that artifact mixes static canon, autobiography, phenotype evidence and
longitudinal records, V1 cannot isolate the causal effect of lived interaction.
Acquired long-horizon path dependence still requires a later
forked-life experiment in which initially identical subjects accumulate different
experiences before receiving identical delayed probes.

No live-model Pretorius result has been accepted as evidence at the time this
release candidate is defined.

Stable Pretorius continuity IDs are generated at creation for records, expectations,
commitments and reflection insights. They are not rewritten after the turn. Generic
v0.2 continuity retains its UUID behavior.

## Known release-candidate limits

The 512-memory budget is sufficient for the frozen short live protocol but is not a
complete long-life memory system. When capacity is exceeded, the donor engine keeps
higher-scoring memories and discards lower-scoring ones. There is not yet a
consolidation layer, hierarchical autobiographical summary, or protected archive for
old but identity-defining events.

The live evidence manifest now fingerprints all Python implementation files in both
runtime packages, the Pretorius cartridge, the Python environment, the cartridge
payload, and provider-reported model metadata when available. The user-supplied model
fingerprint remains a provenance label rather than provider attestation.
