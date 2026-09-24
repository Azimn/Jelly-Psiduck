# v0.3 development results

Protocol: [V03_PROTOCOL.md](V03_PROTOCOL.md)

Branch: `feat/v03-idle-reverie`, intentionally separate from the
lived-history/Pretorius experiment in PR #4.

## Validation

GitHub Actions completed successfully on Python 3.11 and 3.12 for the v0.3
candidate. The workflow reruns the frozen v0.1 evaluation, the v0.2 endogenous
evaluation, the frozen model-efficacy dry-run, the complete unit-test suite and
the new deterministic v0.3 evaluation.

The v0.3 evaluation exited successfully with all declared checks passing. It
covers the following mechanism-level claims:

- a calm generic subject eventually receives an `idle_reverie` cognition
  opportunity without the runtime manufacturing a private thought;
- a provider that returns silence causes bounded exponential idle backoff;
- disabling idle reverie removes those idle cognition calls;
- the balanced provider view keeps a first-person identity anchor, retains
  available external context, caps private-thought occupancy and collapses exact
  repeated memory text;
- concern habituation reduces repeated *forced* unresolved-concern returns while
  leaving the underlying commitment unresolved;
- idle scheduling and habituation state survive restart with identical future
  deterministic trajectory.

## Scope

These are deterministic engineering checks. No live-model v0.3 run is included
here, and the result does not establish that periodic reverie improves cognition.
The existing v0.2 live-model harness remains the appropriate apparatus for model
efficacy work.

The longer-history Pretorius experiment is not part of this result. No Pretorius
history artifact, chronology, relationship seed, public renderer or schema-3
lived-history state is present on this branch. A future study that combines
lived history with idle reverie should be designed as an explicit factorial
experiment rather than created by merging the treatments during development.
