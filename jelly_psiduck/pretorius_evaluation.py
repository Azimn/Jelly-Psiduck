"""Deterministic engineering check for the Pretorius lived-history layer.

This does not evaluate human likeness. It verifies that typed history enters the
same organism, changes recall and conduct under matched current input, and survives
restart without a second subject or hidden model dependency.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from digital_subject.cartridge import load_cartridge

from .history import seed_history
from .pretorius import DEFAULT_CARTRIDGE, DEFAULT_HISTORY, PretoriusSubject


class SilentCognition:
    def think(self, view):
        return None


def _historical_links(snapshot):
    return sorted({
        link
        for record in snapshot["workspace"]["records"]
        if record["source"] == "memory"
        for link in record["memory_links"]
        if link.startswith("pretorius-lived-history-v1:")
    })


def run_evaluation():
    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        full = PretoriusSubject(
            root / "full.db",
            cartridge,
            cognition=SilentCognition(),
            subject_id="pretorius-001",
        )
        control = PretoriusSubject(
            root / "control.db",
            cartridge,
            cognition=SilentCognition(),
            subject_id="pretorius-001",
        )
        import_report = seed_history(full, DEFAULT_HISTORY)
        seeded = full.inspect()

        prompt = "We are testing continuity again. What does our history change?"
        full.message("Jay", prompt)
        control.message("Jay", prompt)
        full_result = full.heartbeat()
        control_result = control.heartbeat()

        after = full.inspect()
        control_after = control.inspect()
        before_restart = json.loads(json.dumps(after))
        reopened = PretoriusSubject(
            root / "full.db",
            cartridge,
            cognition=SilentCognition(),
            subject_id="pretorius-001",
        )
        after_restart = reopened.inspect()

        links = _historical_links(after)
        control_links = _historical_links(control_after)
        checks = {
            "typed_history_imported": import_report["memory_count"] == 57,
            "relationships_imported": import_report["relationship_count"] == 5,
            "jay_history_retrieved": bool(links),
            "control_has_no_seeded_history": not control_links,
            "history_changes_conduct": full_result["action"] != control_result["action"],
            "seeded_conduct_is_answer": full_result["action"] == "answer",
            "restart_exact": before_restart == after_restart,
            "history_metadata_persisted": "pretorius-lived-history-v1" in after_restart["history_imports"],
        }
        return {
            "protocol": "pretorius-lived-history-engineering-v1",
            "claim_scope": "mechanism and persistence only; no human-likeness or consciousness claim",
            "seed": {
                "memory_count": import_report["memory_count"],
                "relationship_count": import_report["relationship_count"],
                "narrative_count": import_report["narrative_count"],
                "open_loop_count": import_report["open_loop_count"],
                "workspace_orientation_count": import_report["orientation_count"],
            },
            "matched_input": prompt,
            "full_history_action": full_result["action"],
            "control_action": control_result["action"],
            "historical_memory_links": links,
            "control_historical_memory_links": control_links,
            "checks": checks,
            "passed": all(checks.values()),
            "seeded_state_before_probe": {
                "memory_count": len(seeded["engine"]["memories"]),
                "relationship_count": len(seeded["engine"]["relationships"]),
                "history_import_count": len(seeded["history_imports"]),
            },
        }


def main():
    parser = argparse.ArgumentParser(description="Run deterministic Pretorius history checks")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run_evaluation()
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
