# Status

## 2026-09-23: Unified Subjective Organism v0.1

Implemented the Persona-and-Jelly foundation, engine/subject interface, bounded
recursive thought, autonomous foreground lifecycle, atomic local persistence,
optional model transport, private/public separation, source documentation and
matched engineering evidence.

Local Python 3.11 verification: **51 tests passed**. The matched-inner-ear-v1
experiment passed all seven checks across five intervention arms. Its JSON output
is stored under `evidence/`. HTTP transport was exercised against a local fixture;
no actual model result or independent efficacy evaluation is claimed.

Validation commands completed:

- `python -m pytest -q`
- `python -m jelly_psiduck.evaluation --output evidence/inner-ear-v1.json`
- `python -m pip install -e '.[test]'`
- `python -m pip wheel --no-deps --wheel-dir dist .`
- CLI demo, message enqueue and tick smoke tests.
- Isolated wheel extraction and demo from a temporary directory with Python `-I`,
  confirming the default cartridge is included and works outside the checkout.

CI is configured for Python 3.11 and 3.12. Local verification is not evidence of a
completed CI run. See the pull request's checks for live CI status.

No existing user subject store is migrated. This is a new repository and a new
SQLite schema. Reopening retains the same subject; changed schema/cartridge is
rejected. No background daemon was installed or left running during development.

Known limitations and next research work are in `ARCHITECTURE.md` and
`research/PROTOCOL.md`. This is the initial executable architecture, not completion
of every research hypothesis or a full natural-language companion product.
