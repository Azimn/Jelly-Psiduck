# Architecture v0.1

## Authority and representation

`digital_subject.SubjectState` remains the organism. `SubjectContinuity` owns
existing epistemic, expectation and commitment records. They are components of
one persisted subject, not competing agents. `jelly_psiduck.Organism` extends the
existing engine with narrow heartbeat, recollection and conduct entry points.

`SubjectiveExperience` is an engine-owned record of having experienced something.
Its contents do not thereby become objective truth. Source, intensity, salience,
concepts, affect, memory/concern/expectation links, generator and privacy flags are
available to the operator. `CognitiveView` contains only immutable source-labelled
first-person text. Knowing that something was remembered or imagined is necessary
for source discrimination; persistence IDs and scores are not subjective access.

The firewall is an allowlisted data interface, not a prompt asking a model to
ignore numbers it has already received. Numbers quoted by an external speaker can
still appear as communication content; they are not privileged engine telemetry.
In-process plugins are trusted code: immutable views are not an OS sandbox against
a malicious callback that deliberately accesses globals or files.

## One heartbeat

1. Acquire the process reentrant lock and SQLite `BEGIN IMMEDIATE`; refresh the
   latest complete snapshot, including messages queued by another local client.
2. Advance the organism once, including homeostasis, sensory influence and decay.
3. Advance deadlines, admit up to eight queued host events, project newly salient
   body experiences, external perception, remembered events and temporal awareness.
4. If there is meaningful input, a body transition, a deadline transition or a
   sparse attention revisit, run at most two private-language calls by default.
5. Validate each thought's shape and length. Store it as a private thought. The
   inner ear extracts word cues against existing memory tags and commitment actors.
6. Retrieve existing memories, project them subjectively, and apply bounded
   recollection/continuity effects through existing pressure and concern channels.
   Project resulting feelings back into the workspace before another thought.
7. Invoke the existing conduct selector once. Apply a matching internal regulation
   activity or render permitted public expression from cartridge templates.
8. Commit the entire state atomically. Failure rolls back the turn and its inbox
   consumption. A cognition failure is recorded and the organism still advances.

Thought text cannot supply numbers, event kinds, metadata, successful outcomes,
commitment adoption or belief revisions. "The visitor returned" in a thought is
not a `person_arrived` event. The thought is not inserted into autobiographical
event memory. Proposing an action in prose is not authority to execute it.

Attention is a persisted set of grounded cues. Sparse later revisits use those
cues for memory retrieval. Thought effects can therefore outlast the language
call without continual narration. Memory valence reuses the donor's tag-based
rule; this is a deliberately narrow mechanism, not general semantic understanding.

## Bounds and persistence

- Workspace: most recent 64 records; cognitive view: most recent 16 eligible records.
- Trace: most recent 256 operator records; thought text: at most 600 characters.
- Inbox: 64 events, with at most eight consumed per heartbeat.
- Cognition: default two calls per tick, configurable from zero to four.
- Exact repeated thoughts suppressed for six ticks; each recalled memory and
  continuity actor can affect state at most once per six ticks.
- Recollection changes one pressure by at most 0.08. Existing continuity deltas
  remain individually bounded to 0.20. All existing pressure clamps still apply.
- Default catch-up: at most twelve ticks; skipped time is recorded explicitly,
  not represented as lived experience. Fractional elapsed time survives restart;
  backward clock jumps do not create duplicate elapsed time.

These are prototype execution bounds, not experimentally optimal cognitive
capacities. The imported memory limit and continuity retention remain donor
policies. Long-term recoverability after eviction has not been established here.
Open commitment/expectation and cooldown collections are not a demonstrated
bounded long-life storage policy. Persistent unbounded unattended deployment is
therefore not claimed on the strength of the bounded workspace alone.

One SQLite row contains the complete subject snapshot. Subject identity,
cartridge fingerprint, schema and experiment flags are validated on reopen.
Changing a cartridge or schema requires an explicit migration. Experiment flags
cannot silently change an existing run; the evaluation harness forks a closed
snapshot to make interventions. Replacing the cognition provider does not replace
the subject. SQLite handles local serialization, not distributed custody or merging.

Model calls are synchronous inside a transaction (30-second transport timeout).
This preserves atomicity but can delay queued messages and graceful shutdown.
Asynchronous model proposals with revision checks are a future operational step.

## Public and private

The host sees telemetry. Cognition sees the subjective workspace. Public speech
is optional, gated by selected conduct, and never obtained by copying a thought.
Nonverbal acts and concealment may yield `speech: null`. External actions are
proposals until the host calls `consequence`; there are no automatic shell,
browser, file-writing or messaging tools in the organism.

`enqueue(Event(...))` is trusted host ingress, including typed observation
metadata. `message(speaker, text)` is the untrusted natural-language ingress and
does not parse that text as metadata. An operator who calls the trusted API is
responsible for sensor accuracy and authority. Imagining has a source type but
no separate imagination generator in this release.

## Foundation changes

The donor's `_choose_intention` allowed a habit belonging to a weaker need to
override stronger incompatible fear. Its own paired-history test failed at the
imported commit. This fork constrains the habit to the dominant channel's options.
`step` also supports ingesting events without an additional clock step or early
conduct selection, so one heartbeat has one final action decision.

`from_dict` restores engine state from the atomic host snapshot. Expression packets
now expose matched-memory provenance to the host; the legacy text handoff projects
qualitative needs instead of numeric needs. The supported unified entry point is
`python -m jelly_psiduck`; imported `digital_subject` hosts and sidecar helpers are
compatibility/research APIs and are not the new cognition boundary.

## Not yet demonstrated

General natural-language appraisal, multi-history relationship development,
thought-derived prospective commitment proposals with adoption gates, richer
imagination, independent recognizability evaluation, full organism removal and
raw-telemetry control arms, long-duration stability and real-model robustness
remain research work. No claim of felt consciousness follows from this machinery.
