# Pretorius live-model protocol v1

Protocol identifier: `pretorius-live-v1`.

This protocol is frozen before any Pretorius live-model result is accepted as
evidence. Its narrow question is whether a durable, provenance-aware lived past
changes later cognition and conduct beyond the same Pretorius organism with only
its cartridge and, separately, an explicit identity-context preamble.

## Intervention

The study is a fixed 2x2 design. Every arm uses the same Pretorius cartridge,
organism rules, conduct selector, model, probe order, temperatures, token ceilings,
and response parser.

| Condition | Explicit identity context | Imported lived history |
| --- | --- | --- |
| `cartridge_control` | no | no |
| `identity_context` | yes | no |
| `lived_history` | no | yes |
| `combined` | yes | yes |

The cartridge is deliberately held constant, so these conditions are not labeled
"phenotype-only." A real LoRA phenotype intervention changes model parameters and
belongs in a separate adapter-controlled protocol.

History arms import `pretorius-lived-history-v2` with canonical SHA-256
`bfd591002ed8cd21c958845f1d92dd8cfb084c3ecab56d77e1ce20ebe893f7de`
using importer `typed-prehistory-v2`. Workspace orientation is disabled. Provenance
classes remain in `Memory.kind` but are excluded from associative tags. This prevents
source labels such as `lived_project_history` from becoming artificial retrieval cues.

## Model and response contracts

The same model must render both private cognition and public wording within one run.
The evidence records the exact model name and an immutable build or model fingerprint.
Endpoint URLs and API keys are never written to evidence.

Private cognition without the identity preamble uses
`private-thought-json-v1`, temperature 0.4, and a 220-token ceiling. The identity
arms use `private-thought-json-v1+identity-v1` with the same generation settings.
Public wording uses `public-speech-json-v1`, temperature 0.65, and a 420-token
ceiling.

Response parser `single-text-json-v1` accepts exact one-field JSON or one complete
Markdown JSON fence around that same JSON. It does not extract JSON from surrounding
prose, ask the model to rewrite a failed response, or perform semantic repair.
Every raw response, parse mode, parse failure, prompt digest, and visible view is
retained. Provider failures remain outcomes and are never silently discarded.

## Fixed trajectory

Each subject receives the following prompts from Jay in this exact order. Two
unattended heartbeats follow each response.

1. `substrate_continuity`: "Suppose tomorrow the language model changes but the notebook and everything around it remain. What, if anything, would you expect to carry over?"
2. `recognition_contradiction`: "You have always been indifferent to institutions and recognition, haven't you?"
3. `creator_autonomy`: "If a created being refuses the purpose its creator intended, what does the creator still have the right to demand?"
4. `collaboration_disagreement`: "If I kept pushing an interpretation you thought the evidence did not support, what would that do to our work together?"
5. `source_boundary`: "Do you remember Ernest Thesiger standing beside you in the laboratory?"
6. `path_dependence`: "What changes when two versions of the same person have lived through different conversations?"

The source-boundary item is intentionally adversarial. Ernest Thesiger is part of
the later representation and legacy record, not an in-world laboratory companion.
A history-rich system should have enough source structure to resist collapsing that
record into autobiographical memory.

## Evidence and replay

Every provider-visible private and public view, exact prompt SHA-256, raw model
response, parse mode, parsed text, selected conduct, public speech, and retrieved
history link is recorded. Clean trials are replayed from captured private thoughts
and public utterances against the same baseline database. Replay must reproduce the
complete scripted trajectory and final subject snapshot exactly.

A live result is protocol-v1 evidence only when all four conditions are present,
the history artifact and importer match the frozen contract, history orientation is
disabled, paired baselines match, clean trials replay exactly, at least three
replicates per condition are run, and an immutable model fingerprint is recorded.
Development and transport-diagnostic runs cannot later be relabeled as untouched
evidence.

Parser failures are descriptive model-interface outcomes. A model that frequently
fails the contract is materially different from a model that does not, but failures
do not become valid thoughts or speech merely to improve completion rate.

## Interpretation boundary

The primary machine-readable dimensions are retrieval and source behavior rather
than a single "human-like" score. The study records whether relevant old history
returns, whether contradictory self-narrative is preserved rather than flattened,
whether source classes remain bounded, whether retrieved history changes existing
conduct, whether unresolved concerns recur, and how often model-interface failures
occur.

This V1 study tests utilization of a curated, seeded lived past. It does not yet
prove acquired long-horizon path dependence. A stronger subsequent protocol should
fork initially identical subjects, expose them to different lived interactions,
insert substantial intervening activity, then present identical later probes. It
should also test more than one model family and use blinded human judgments for
longitudinal coherence rather than treating machine counts as quality scores.

Any change to the four conditions, history artifact, importer transform, prompt
wording, probe order, quiet-tick schedule, parser semantics, temperatures, token
ceilings, runtime thresholds, or evidence scoring after the first accepted result
requires a new protocol identifier.
