# v0.3 candidate: idle reverie and balanced working attention

v0.3 is a sibling of the lived-history/Pretorius experiment, not its successor or
dependency. Both branches start from the generic v0.2 model-efficacy apparatus.
PR #4 asks what a much richer lived history does to the organism. This v0.3 branch
asks what happens when the same generic organism is allowed sparse cognition during
otherwise quiet time and when its provider view resists single-topic saturation.

No Pretorius history, chronology, relationship seed or persona-specific state is
included here. v0.3 uses SQLite schema 4 specifically to avoid colliding with the
separate lived-history schema 3 experiment.

## Idle reverie

After two otherwise quiet heartbeats by default, v0.3 records an
`idle_reverie` cognition trigger. The provider gets an ordinary first-person view
and may produce one private thought or return silence. The timer never manufactures
language itself.

If an idle call returns silence, the next idle interval doubles, bounded by 24
heartbeats. If it produces a thought, the interval returns to the base value.
Any ordinary v0.2 trigger also restarts the quiet interval. The unit is heartbeat,
not seconds: with the default five-second live heartbeat the initial two-tick
interval is approximately ten seconds; hosts can choose another heartbeat cadence.

## Balanced subjective view

v0.2 exposes the last sixteen eligible experiences by recency. Pilot runs showed
a predictable failure mode: a strong recursive topic can fill nearly the entire
view with its own thoughts and repeated recollections.

v0.3 keeps the underlying 64-record workspace unchanged but composes the provider
view across source classes. It reserves a persistent first-person identity memory,
then admits bounded amounts of external/social perception, interoception, temporal
material, autobiographical memory, private thought and imagination. Exact duplicate
source/text pairs are collapsed in the provider view.

Private thought is capped at three slots. Selection uses engine metadata, but the
provider still sees only `source` and `first_person`; no score, ID, salience,
relationship coefficient or other telemetry crosses the experiential firewall.

## Concern habituation

v0.2 unresolved concerns accumulate activation until they return to attention.
v0.3 optionally gives repeated returns of the same unresolved root a growing
refractory interval. The underlying commitment, expectation, affect and concern
remain intact; the mechanism limits repeated forced attentional capture.

New external input or a new elapsed-time grade clears the refractory history so
genuinely new evidence can make the matter salient again. Idle reverie can still
occur during that refractory period; habituation prevents forced recurrence, not
voluntary thought.

## Separation from the longer-history experiment

The lived-history/Pretorius work remains on PR #4. It has its own history artifacts,
provenance rules, schema-3 envelope and research question. v0.3 contains none of
those materials. Both experiments can later be applied to a common frozen baseline
only through an explicitly designed factorial study.

## Run

Use a new database:

```bash
python -m jelly_psiduck --architecture v03 --db v03-demo.sqlite3 init
python -m jelly_psiduck --architecture v03 --db v03-demo.sqlite3 run --interval 5
python -m jelly_psiduck.v03_evaluation --output evidence/local-v03.json
```
