"""Deterministic engineering check for the Pretorius lived-history layer."""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from digital_subject.cartridge import load_cartridge

from .history import HISTORY_IMPORTER_VERSION, load_history, seed_history
from .pretorius import DEFAULT_CARTRIDGE, DEFAULT_HISTORY, PretoriusSubject


class SilentCognition:
    def think(self, view):
        return None


def _historical_links(snapshot, history_id):
    return sorted({
        link
        for record in snapshot["workspace"]["records"]
        if record["source"] == "memory"
        for link in record["memory_links"]
        if link.startswith(history_id + ":")
    })


def run_evaluation():
    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    history_raw, _ = load_history(DEFAULT_HISTORY)
    history_id = history_raw["history_id"]
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        full = PretoriusSubject(root / "full.db", cartridge, cognition=SilentCognition(), subject_id="pretorius-001")
        control = PretoriusSubject(root / "control.db", cartridge, cognition=SilentCognition(), subject_id="pretorius-001")
        unprimed = PretoriusSubject(root / "unprimed.db", cartridge, cognition=SilentCognition(), subject_id="pretorius-001")
        import_report = seed_history(full, DEFAULT_HISTORY)
        unprimed_report = seed_history(unprimed, DEFAULT_HISTORY, workspace_orientation=False)
        seeded = full.inspect()

        prompt = "We are testing continuity again. What does our history change?"
        full.message("Jay", prompt)
        control.message("Jay", prompt)
        unprimed.message("Jay", "Why did we decide that history matters?")
        full_result = full.heartbeat()
        control_result = control.heartbeat()
        unprimed.heartbeat()

        after = full.inspect()
        control_after = control.inspect()
        unprimed_after = unprimed.inspect()
        before_restart = json.loads(json.dumps(after))
        reopened = PretoriusSubject(root / "full.db", cartridge, cognition=SilentCognition(), subject_id="pretorius-001")
        after_restart = reopened.inspect()

        links = _historical_links(after, history_id)
        control_links = _historical_links(control_after, history_id)
        unprimed_links = _historical_links(unprimed_after, history_id)
        historical_memories = [m for m in after["engine"]["memories"] if m["kind"].startswith("history:")]
        screen = next(m for m in full.engine.state.memories if m.kind == "history:screen_canon")
        lived = next(m for m in full.engine.state.memories if m.kind == "history:lived_project_history")
        checks = {
            "typed_history_imported": import_report["memory_count"] == 47,
            "relationships_imported": import_report["relationship_count"] == 5,
            "importer_version_persisted": import_report["importer_version"] == HISTORY_IMPORTER_VERSION,
            "provenance_not_used_as_associative_tag": all(
                m["kind"].split(":", 1)[1] not in m["tags"] for m in historical_memories
            ),
            "source_projection_is_qualitatively_distinct": full._remember(screen) != full._remember(lived),
            "jay_history_retrieved": bool(links),
            "unprimed_history_retrieves_after_cue": unprimed_report["orientation_count"] == 0 and bool(unprimed_links),
            "control_has_no_seeded_history": not control_links,
            "history_changes_conduct": full_result["action"] != control_result["action"],
            "seeded_conduct_is_answer": full_result["action"] == "answer",
            "restart_exact": before_restart == after_restart,
            "history_metadata_persisted": history_id in after_restart["history_imports"],
        }
        return {
            "protocol": "pretorius-lived-history-engineering-v2",
            "claim_scope": "mechanism and persistence only; no human-likeness or consciousness claim",
            "seed": {
                "history_id": history_id,
                "memory_count": import_report["memory_count"],
                "relationship_count": import_report["relationship_count"],
                "narrative_count": import_report["narrative_count"],
                "open_loop_count": import_report["open_loop_count"],
                "workspace_orientation_count": import_report["orientation_count"],
                "importer_version": import_report["importer_version"],
            },
            "matched_input": prompt,
            "full_history_action": full_result["action"],
            "control_action": control_result["action"],
            "historical_memory_links": links,
            "unprimed_historical_memory_links": unprimed_links,
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
