# Jelly-Psiduck

## Unified Subjective Organism Architecture

**The engine simulates the organism. The subject experiences the consequences.**

Jelly-Psiduck builds on Persona-and-Jelly's persistent organism. Body, needs,
relationships, memory, expectations and commitments evolve in engine-owned state.
A subjective workspace translates that state into first-person experiences.
Private thoughts can re-enter that workspace, retrieve existing autobiography,
change bounded appraisal and attention, and alter the same engine's next action.

This is an executable research prototype, not evidence of phenomenal consciousness.
The first release demonstrates a narrow causal loop; the broader hypothesis still
requires independent experiments and richer histories.

An opt-in [v0.2 endogenous-cognition candidate](docs/ARCHITECTURE_V02.md) now adds
graded interoception, unresolved-concern recurrence, associative memory drift,
deferred thought input, bounded discourse interpretation, and independent memory
versus prospective feedback. Use `--architecture v02` with a **new database**;
the default v0.1 apparatus remains available. See the [development results](research/V02_RESULTS.md)
for the four-history/eight-arm unattended experiment and its limitations.

```text
world / messages / time
          |
          v
Persona-and-Jelly organism <---- governed memory / continuity effects
          |                                  ^
          v                                  |
experiential firewall -> subjective workspace -> private cognition
                               ^                    |
                               +----- inner ear <---+
                                                    |
                              existing action selector
                                     |            |
                              internal action  optional public speech
                                     |            |
                                  consequences from the host
```

### Run locally

Python 3.11 or newer; no model, network, GPU, or third-party runtime dependency is required.

```bash
python -m pip install -e '.[test]'
python -m jelly_psiduck init
python -m jelly_psiduck --db demo.sqlite3 demo
python -m jelly_psiduck --db demo.sqlite3 status
python -m jelly_psiduck run --interval 5
```

In a second terminal, deliver a message to the running organism:

```bash
python -m jelly_psiduck message Jay "I'm back."
```

Messages enter an inbox and become social experiences on the next heartbeat.
`run` stays in the foreground until Ctrl+C. `tick 12` advances twelve explicit
steps. `status` is an operator inspector: it includes private thoughts and engine
telemetry and is **not** the subject's cognition interface or public speech.
The host can select silence or nonverbal conduct in response to a message.

The deterministic private-language provider is intentionally simple. To use a
configured OpenAI-compatible model server instead:

```bash
python -m jelly_psiduck --endpoint http://localhost:11434/v1 --model YOUR_MODEL run
```

Set `JELLY_API_KEY` if the chosen provider requires authentication. Only detached
subjective experience text is sent. Body simulation and persistence remain local.
The integration is tested with a local HTTP fixture; actual model behavior has
not yet been evaluated. Public expression currently uses cartridge templates.

### What is implemented

- First-person workspace for perception, body experience, social input, memories,
  temporal expectations, private thought and action consequences.
- Immutable cognition views with no meters, salience scores, persistence IDs,
  retrieval scores or support metadata. The engine retains that provenance.
- Thought -> grounded concepts -> memory -> bounded appraisal -> subsequent
  experience and conduct, with persistent evidence cooldowns.
- Intermittent cognition during an autonomous heartbeat; quiet periods still
  update the organism. Recent thoughts persist without becoming observed facts.
- One SQLite snapshot transaction for organism, continuity, workspace, queued
  input, clock and feedback state. Restart retains the same subject.
- Separate public speech, private thought, selected conduct and host-reported
  consequences. Model prose cannot fabricate arrivals or fulfill promises.
- Matched-history ablations for the inner ear, thought effects, memory feedback
  and autonomous cognition.

### Verify

```bash
python -m pytest -q
python -m jelly_psiduck.evaluation --output evidence/local-inner-ear.json
```

The frozen [initial evidence](evidence/inner-ear-v1.json) compares five arms
forked from the same pre-probe snapshot. The complete loop selects withdrawal;
the four ablations select exploration. The distinction survives restart.
This is an authored engineering scenario, not independent efficacy evidence.

See [architecture](docs/ARCHITECTURE.md), [source provenance](docs/SOURCES.md),
[research protocol](research/PROTOCOL.md), and [status](docs/STATUS.md).
