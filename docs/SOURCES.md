# Source provenance

The owner's Unified Subjective Organism Architecture specification is the design
contract for this repository. The following sources have different reuse roles.

## Imported foundation

[Azimn/Persona-and-Jelly-Sandwich-](https://github.com/Azimn/Persona-and-Jelly-Sandwich-)
at commit `f196ddef26ca755d814b5fb3e4ed41d1fead01a3`.

Imported `digital_subject/`, `cartridges/`, and the donor `tests/`. The bundled
default cartridge in `jelly_psiduck/cartridges/` is an unchanged packaging copy.
The Gelatinblob reservoir and its dependencies were not imported. All Jelly-Psiduck
changes are reviewable relative to that source; architecture documentation lists
the narrow modifications to the original engine. Upstream ownership and attribution
are retained; this import does not assert a new license over upstream material.

## Conceptual sources, no third-party code transplanted

- [Arianna-Pipitone/robot-inner-speech](https://github.com/Arianna-Pipitone/robot-inner-speech)
  and [Robot's inner speech and emotions](https://github.com/RoboticsLab-Unipa/Robot-s-inner-speech-and-emotions):
  recursive internal speech as cognitive input and its connection to appraisal.
  Jelly-Psiduck's bounded word-cue loop is an original narrow implementation, not
  a reproduction of the robotics experiments or their results.
- [huodebing-alt/anima](https://github.com/huodebing-alt/anima), including its
  [design paper](https://github.com/huodebing-alt/anima/blob/main/docs/ANIMA_PAPER.md):
  ongoing heartbeat, recent-thought context and lifecycle patterns. Sleep,
  self-model rewriting and dream consolidation are not imported.
- [laude-institute/headlong](https://github.com/laude-institute/headlong):
  persistent agency and communication within an ongoing process. No shell
  harness, autonomous tool authority or distributed messaging is imported.
- [Azimn/DUCK](https://github.com/Azimn/DUCK): first-person access boundary,
  subject/machine separation and evidence-gated donor reuse. The README and donor
  audit informed this design; this is not a port of DUCK v0.9's planning runtime.

These links document design provenance, not independent validation of this
synthesis. Source claims about consciousness are not adopted as established facts.
