# Pretorius lived-history variant

This branch derives a Pretorius-specific subject from the stacked v0.2 model-efficacy head. It does not replace the Psiduck subject, alter the frozen v0.1 evidence, or change the v0.2 prompt contract when Pretorius mode is not selected. Pretorius uses a separate schema-3 SQLite store because the imported history manifest is part of his identity provenance.

## Research premise

The hypothesis is narrower than "more memory makes a better chatbot." A static persona can specify dispositions, and a LoRA corpus can stabilize linguistic phenotype, but neither necessarily supplies longitudinal path dependence. This variant therefore initializes the organism with a typed history that can participate in the same retrieval, appraisal, association, concern recurrence, and inner-ear mechanisms used by memories acquired after startup.

The design follows a pattern that appears across long-term agent research while preserving Jelly-Psiduck's stronger causal boundary. Generative Agents stores experience, retrieves it dynamically, and synthesizes reflection. MemGPT separates working context from durable memory for multi-session agents. THEANINE preserves old memories and links them through temporal and causal timelines rather than deleting them simply because they are outdated. Hindsight separates world facts, experiences, observations, and opinions. HeLa-Mem and Synapse emphasize association and spreading activation rather than treating memory as a flat similarity search. The relevant sources are https://arxiv.org/abs/2304.03442, https://arxiv.org/abs/2310.08560, https://aclanthology.org/2025.naacl-long.435/, https://aclanthology.org/2026.acl-demo.27/, https://aclanthology.org/2026.acl-long.625/, and https://aclanthology.org/2026.findings-acl.1108/.

Pretorius does not ingest the 271-record LoRA dataset as 271 invented life events. That material remains phenotype evidence. The seeded history keeps screen canon, expanded autobiography, foundational self-memory, legacy awareness, archived self-description, phenotype evidence, actual project history, relationship history, and research history as distinct evidence classes. The persisted Memory.kind records that class, while the source artifact keeps record-level provenance.

## What is seeded

The current history artifact contains 47 memories, five relationship states, four beliefs, ten revisable narrative claims, and five unresolved long-arc concerns. The relationships with Jay, Henry, the Creature, the Bride, and Elizabeth are operational summaries backed by episodic history. The numeric relationship values are simulated current-state priors, not claims about reciprocal human feelings and not substitutes for the episodes that produced them.

Recent collaboration with Jay is treated as lived project history because it occurred in the longitudinal Pretorius reconstruction work. The LoRA lineage, Agent-Pretorius, contextual recall work, model-swap observations, neural phenotype experiments, the realization that history may matter as much as structure, and this Jelly-Psiduck integration therefore exist as recent autobiographical episodes. Older film events remain separately typed as screen canon. Later interpretations of those events remain revisable self-model material rather than retroactively becoming canon.

The history importer is deterministic and one-time. It requires a fresh subject, stores a SHA-256 digest of the source artifact in the Pretorius-only persistence envelope, rejects a changed artifact after import, backdates memories rather than replaying them as current perceptions, and places only six orientation memories in the initial subjective workspace. The rest must return through relevance or association.

## Public speech

The base v0.2 branch can use an unscripted model for private cognition but still renders public speech from cartridge templates. Pretorius mode adds an optional OpenAI-compatible public renderer. The organism selects conduct first. The renderer receives a detached qualitative SpeechView containing identity, the selected conduct, heard text, qualitative posture, felt needs, relationship stance, relevant memories, recent recollections, beliefs, and self-narrative. It does not receive raw sensorium values, need meters, pressure magnitudes, private thought text, or the packet's private metadata.

If the renderer fails, the organism falls back to the Pretorius cartridge template. A renderer cannot mark a promise kept, move a person into the room, update a relationship, write memory, or choose a different conduct. This keeps fluent public language downstream of the organism instead of turning prose generation into a second agent.

## Running Pretorius

Install the project normally. A model is optional for deterministic inspection, but the intended natural-language test uses an OpenAI-compatible endpoint for both private cognition and public rendering.

~~~bash
python -m pip install -e '.[test]'
python -m jelly_psiduck.pretorius init
python -m jelly_psiduck.pretorius --endpoint http://localhost:11434/v1 --model YOUR_MODEL chat
~~~

The installed console script is equivalent:

~~~bash
jelly-pretorius --endpoint http://localhost:11434/v1 --model YOUR_MODEL chat
~~~

JELLY_API_KEY is used only when the configured provider requires it. The --template-speech option keeps model-backed private cognition while retaining deterministic cartridge speech. The default speaker is Jay so that the reconstructed collaboration history is addressable immediately, and --speaker can select another human identity.

## Verification boundary

python -m jelly_psiduck.pretorius_evaluation is deliberately not a human-likeness benchmark. It creates a history-seeded Pretorius and a persona-only matched control, gives both the same current message from Jay with cognition silenced, and checks that only the seeded subject retrieves earlier Jay episodes and that the resulting existing conduct selector can choose differently. It also verifies exact restart and history-manifest persistence.

The next scientific step is a preregistered live-model comparison across history-rich, persona-only, phenotype-only, and combined conditions using the same model and current interactions. Outcomes should include delayed relationship continuity, appropriate retrieval of old versus recent memories, contradiction preservation, spontaneous return to unresolved concerns, false-memory rate, private-thought diversity, action stability across model swaps, and blinded human judgments of longitudinal coherence. That later study should not be confused with the deterministic mechanism checks in this branch.
