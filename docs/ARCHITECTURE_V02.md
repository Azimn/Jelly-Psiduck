# v0.2 candidate: endogenous cognitive opportunities

This opt-in candidate extends the feature-frozen v0.1 baseline at `9a7945c`.
`UnifiedSubject` remains the default. `EndogenousSubject` shares its transaction,
event intake, private/public boundary and sole conduct selector. Small projection,
recurrence and inner-ear hooks select the candidate behavior without replacing
the organism or duplicating the heartbeat implementation.

## State-driven recurrence

There is no fixed "call the model every sixth tick" rule in v0.2. A heartbeat
may create a cognitive opportunity for one of these recorded reasons:

| Cause | Grounding and consequence |
| --- | --- |
| External input | Existing host event becomes an owned experience |
| Body change | A need changes qualitative intensity or begins to ease |
| Temporal change | An unresolved deadline crosses an elapsed-wait grade |
| Unresolved concern | Attention accumulates to an open continuity root or unresolved event concern |
| Association | A recalled memory activates a different existing related memory |
| Prior thought | A grounded earlier thought returns after a bounded delay |

Triggers are opportunities, not guaranteed model calls or sentences. With
autonomous cognition disabled, the organism may still notice something; the
provider is not invoked without external input. A provider may always return
silence. Every admitted thought remains private; the host still resolves action
consequences and promises. No person name, scenario or ordered story lives in
the runtime's cognition rules.

## Mechanisms and limits

**Interoception.** Need urgency crosses mild/clear/strong bands at .45/.65/.85,
with .03 downward hysteresis. Recovery is itself experience. Cognition receives
phrases, not grades or numerical values. The binary v0.1 projection is an ablation.

**Concerns.** Open/overdue commitments, pending/expired expectations and event
concerns still present in `state.unresolved` accumulate attention. Urgency combines
importance, elapsed waiting, attachment and uncertainty. Readiness depends on focus.
Each heartbeat adds `urgency * readiness * .25`; an opportunity occurs at a
threshold of .8 and consumes that activation. Resolving the root removes it from
recurrence. Residual affect alone cannot falsely keep a fulfilled promise open.

**Associations.** One recollection is attended per thought. The donor's existing
retrieval/association mechanism supplies neighboring memories. Up to four pending
neighbors can receive bounded activation, with recent-memory exclusion and an
eight-tick exposure cooldown. A later heartbeat can admit one different memory,
retaining the originating thought and memory links. No new autobiographical event
is manufactured. Candidates whose source or target memory is absent are dropped.

**Thought recurrence.** A grounded thought can schedule one deferred private echo,
due after two ticks and expiring after six. Echo/drift chains have maximum depth
two. A new external/body/temporal/concern cause can initiate another episode;
repeating a thought alone cannot authorize an unbounded recursion. Echo state,
activation and all exposure records are persisted in the same subject transaction.

**Interpretation.** `semantics.interpret` is a bounded English discourse grammar.
It annotates inquiry/anticipation/concern/recall and uncertainty/negation, and can
resolve an explicit personal pronoun when exactly one actor is grounded in the
currently visible experience. Elliptical omitted subjects fail closed because an
instruction such as "I should check the stove" must not inherit the only visible
person merely from discourse position. Single-word actor names also require bounded
referential context, so an actor named Will is not activated by "I will check the
stove." Generic memory-tag matching excludes currently grounded actor names and
cannot bypass that rule. Ambiguous references fail closed. The literal-only
ablation cannot resolve the same pronoun thought. These annotations do not turn
"she returned" into observation or resolution. This is beyond literal name matching
for the demonstrated cases, but is not general semantic understanding or an LLM
semantic judge. Multilingual interpretation, complex negation, topic shifts and
multiple-person coreference need their own tests and model-backed proposals.

**Independent feedback.** `memory_feedback` controls recollection and its appraisal;
`prospective_feedback` separately controls appraisal of supported, unresolved
continuity. Lateness exposure rises from zero to one over twelve overdue ticks.
Only increases above the last encountered exposure add fear, bounded by importance
times .20 over that episode. This is a prototype discrepancy measure, not a
calibrated probability or evidence that harm occurred. Related uncertainty and
typed prospective concerns can change existing engine conduct. Prospective
concerns reuse the existing fear action channel; no second action selector exists.

The default `SituatedCognition` provider is a stateless template control that reacts
to the latest first-person experience. It has no actor names, story stages, time
counter or access to telemetry. Its generated language is still templated. Passing
these experiments demonstrates scheduling/feedback mechanisms, not unscripted
LLM thought, emergent understanding, or the exact Sarah narrative.

## Persistence and compatibility

v0.2 SQLite snapshots use schema 2 and require a separate database. v0.1 schema 1
stores are rejected by the v0.2 constructor, and vice versa. There is no automatic
migration or loss of a previous subject. Legacy JSON host schema numbers belong
to a different format and are unrelated to this SQLite schema number.

v0.1 code paths and evidence remain usable. The shared hook refactor reproduces
the complete frozen v1 evaluation JSON exactly. The new fields describe cognition
belonging to the existing subject, not a new identity or independent planner.

Persistent pending echoes/drift retain immediate support during their lifetime.
The bounded workspace and trace are not an archival record of every thought.
Existing limits and synchronous provider calls remain as documented for v0.1;
this phase does not claim an unbounded-lifetime storage or responsiveness policy.

## Run and evaluate

```bash
python -m jelly_psiduck --architecture v02 --db v02-demo.sqlite3 demo
python -m jelly_psiduck --architecture v02 --db v02-demo.sqlite3 tick 24
python -m jelly_psiduck --architecture v02 --db v02-demo.sqlite3 status
python -m jelly_psiduck --architecture v02 --db v02-demo.sqlite3 run
python -m jelly_psiduck.endogenous_evaluation --output evidence/local-v02.json
```

An explicitly configured model can replace the template provider using the existing
`--endpoint` and `--model` options. Such a run is not part of the current evidence.
The bounded inner-ear interpreter stays engine-side regardless of the provider.
