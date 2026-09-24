# v0.2 development results

Protocol: [V02_PROTOCOL.md](V02_PROTOCOL.md), recorded before implementation.
Evidence: [complete trajectories](../evidence/endogenous-v02.json).
Comparator: v0.1 at `9a7945c`; the frozen v1 evidence remains unchanged and its
rerun is exactly equal in `evidence/v02-v01-regression.json`.

## What was measured

Four seeded histories (two unresolved actors/wordings, a repaired history and a
neutral history), each forked into eight intervention arms. Each arm runs for 24
ticks with no new external event. After eight ticks the store is forked again;
the remaining sixteen ticks are compared to a reopened continuation.

All 13 declared harness checks pass. Every restart trajectory and final snapshot
matches its uninterrupted counterpart. Unit tests additionally cover graded body
intensity/recovery, pronoun resolution versus ambiguous reference, isolated
associative drift, isolated finite thought recurrence, relationship sensitivity,
activation-threshold sensitivity and telemetry/authority boundaries.

For each unresolved history, the full arm produced 16 admitted provider thoughts,
with opportunities caused by three temporal changes, six prior thoughts, two
associations and three returns of an unresolved concern. The full repaired and
neutral histories produced no unattended provider thoughts under the controlled
body baseline. Opportunities and thoughts are different measures: a provider can
return silence, a thought may be duplicate-suppressed, and one opportunity allows
at most two admitted thoughts.

Memory-off arms still produced prospective feedback, and prospective-off arms
still produced memory feedback. The transcript-only arm produced no thought-to-state
effects. The autonomy-off arm produced no unattended provider thoughts. Thought
and association ablations remove their corresponding recurrence causes.

## Negative result and repair

The first repair-history test failed: a generic `arousal` concern, inherited from
anticipation before promise resolution, continued to trigger as if still unfinished.
The corrected recurrence path requires open canonical continuity roots or an event
concern that is still in the organism's unresolved history. Residual affect can
continue decaying; it does not masquerade as an outstanding commitment.

## Limits on interpretation

These are builder-designed development cases with a deterministic template provider.
They are neither independent holdouts nor real-model evidence. They establish
mechanism-level causal opportunities and state changes; they do not establish
the quality of spontaneous language, general rumination, or a human-like subject.

Body rates, activities and initial setpoints are controlled in the longitudinal
harness to isolate recurrence. Separate tests exercise graded body changes. The
no-obligation and repaired runs therefore do not imply a normal organism should
never think after repair. More thoughts also do not imply better cognition:
the memory-off arms can produce more wording while having less autobiographical
grounding. Read the full trajectories instead of selecting attractive quotations.

The recurrence threshold is an experimental parameter, not a fitted cognitive
constant. Tests demonstrate monotonic opportunity-count changes at .4/.8/1.6 and
earlier recurrence with greater attachment in a matched fixture. No biological
claim or optimal parameter estimate follows.

The next efficacy experiment should freeze broader histories and distractors,
use actual model providers, score grounding and causal relevance independently
of prose quality, and include more than one linguistic interpreter. Do not tune
on these cases and later describe them as untouched holdouts.


## Post-candidate semantic hardening

A manual review found that the first bounded interpreter treated any non-recall
utterance as an omitted-subject reference when exactly one actor was visible.
That could incorrectly ground unrelated language such as "I should check the
stove" onto that actor. The candidate now fails closed for elliptical omitted
subjects and inherits a sole discourse actor only from an explicit personal
pronoun. Negation detection also covers ordinary English contractions such as
"hasn't" without treating the affirmative word "can" as negation.

This narrows the demonstrated reference mechanism rather than expanding the
claim. The existing pronoun case remains supported; general ellipsis and
coreference remain future work.
