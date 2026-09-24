# v0.3 development protocol: idle reverie and balanced subjective workspace

Recorded on the v0.3 branch before implementing the candidate mechanisms.

This branch is intentionally separate from the lived-history/Pretorius experiment
in PR #4. It starts from the generic v0.2 model-efficacy head at `47b5b9e` and
must not import Pretorius history artifacts, schema-3 lived-history envelopes,
persona-specific memories, relationship seeds, autobiographical chronology, or
public-renderer behavior. The two experiments may later be compared, but they
must not share a treatment branch while either mechanism is being characterized.

## Question

When the organism has no external event, no body transition, no open concern
crossing its threshold, no deferred thought and no associative-drift trigger,
does a sparse idle cognition opportunity allow useful spontaneous thought without
turning the system into a forced continuous monologue?

A second question follows from the Muse pilot: can the cognitive view remain
balanced when a recurrent topic generates many thoughts, or does recency allow
one loop to evict identity, perception and unrelated state from working memory?

## Candidate mechanisms

### 1. Idle reverie

v0.3 may create an `idle_reverie` cognition opportunity after a configurable
number of otherwise quiet heartbeats. The trigger authorizes a provider call; it
does not manufacture a thought. The provider may return `null`.

Repeated idle silence increases the next idle interval up to a bounded maximum.
A produced thought resets the idle backoff. Any ordinary v0.2 cognition trigger
also resets the quiet interval. The trigger is measured in heartbeats rather than
wall-clock seconds; real cadence therefore remains host-controlled. At the default
5-second live heartbeat, two quiet ticks correspond to about ten seconds.

### 2. Balanced subjective view

The v0.2 workspace remains the archival short-term substrate. v0.3 may compose a
smaller provider view from that substrate instead of blindly taking the last
sixteen eligible records. Composition must remain telemetry-free.

The candidate view should preserve a self/identity anchor, recent external or
social perception, current interoception, active temporal/concern material,
autobiographical memory and a bounded number of recent private thoughts. Exact
duplicate source/text pairs should not consume multiple provider slots merely
because a loop repeated them.

Selection metadata remains engine-side. The provider still receives only
`{source, first_person}`.

### 3. Concern habituation

Repeated unresolved-concern returns without new evidence may receive an increasing
refractory interval. The underlying commitment, expectation, affect and concern
remain intact; habituation changes only how soon the same unresolved root can
again demand a cognition opportunity. New external input or a new temporal grade
may reset that refractory state.

This is an optional ablation, not a biological claim.

## Predeclared contrasts

1. Calm neutral history, v0.2 versus v0.3: v0.2 produces no cognition when no
   endogenous trigger exists; v0.3 eventually produces an `idle_reverie`
   opportunity.
2. Silent provider under idle reverie: cognition calls occur but no private thought
   is forced; repeated silence increases the next idle interval.
3. Thought-producing provider under idle reverie: a thought resets idle backoff;
   downstream authority remains identical to v0.2.
4. Saturation fixture with many repeated private thoughts: recency-only view versus
   balanced view. The balanced view must retain identity plus at least one
   non-thought source when such material exists, and cap thought occupancy.
5. Duplicate-memory fixture: exact repeated memory text should not consume several
   balanced-view slots.
6. Unresolved concern with no new evidence: habituation-on must space later concern
   recurrences farther apart than habituation-off.
7. New temporal evidence after habituation: a temporal-grade change is allowed to
   reset concern refractory state.
8. Restart split-run: idle schedule, silence backoff, habituation state and future
   provider views/trajectory must survive reopen exactly.
9. Compatibility: existing v0.1, v0.2 endogenous evaluation and model-efficacy
   dry-run must remain unchanged on their own architectures.

## Authority and interpretation limits

Idle reverie is a scheduling mechanism only. It grants no world authority and no
new action selector. A spontaneous thought remains private, cannot create arrivals,
commitments, expectations or consequences, and reaches state only through the same
bounded inner-ear paths already present in v0.2.

A balanced view is an attention policy, not a memory system. It does not claim a
psychological working-memory capacity or solve long-term archival recall.

Concern habituation is intended to reduce repeated attentional capture without
erasing unresolved state. It must not convert an open problem into a resolved one.

The deterministic tests characterize mechanisms only. Live-model language quality,
human likeness and phenomenology remain outside the claim.
