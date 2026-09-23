"""Builder-designed matched-history experiment, not independent efficacy evidence."""
import argparse
import json
import shutil
import tempfile
from dataclasses import asdict, replace
from pathlib import Path

from digital_subject.cartridge import load_cartridge
from digital_subject.models import Event
from .cli import DEFAULT_CARTRIDGE
from .runtime import ExperimentConfig, UnifiedSubject
from .workspace import Thought


class FixedThought:
    """Exactly the same proposed sentence across intervention arms."""
    def think(self, view):
        return Thought("I wonder where the traveler is.")


class Silence:
    def think(self, view):
        return None


def evaluate():
    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    arms = {"full": ExperimentConfig(),
            "no_inner_ear": replace(ExperimentConfig(), inner_ear=False),
            "transcript_only": replace(ExperimentConfig(), thought_effects=False),
            "no_memory_feedback": replace(ExperimentConfig(), memory_feedback=False),
            "no_autonomous_cognition": replace(ExperimentConfig(), autonomous_cognition=False)}
    results = {}
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        baseline = UnifiedSubject(root / "baseline.db", cartridge, cognition=Silence())
        baseline.enqueue(Event("promise", "traveler", "The traveler promised to return.",
            tags=("traveler", "promise"), metadata={"commitment": {
                "id": "return", "actor": "traveler", "description": "The traveler promised to return.",
                "due_tick": 1, "importance": 1.0}}))
        baseline.heartbeat()
        snapshot = baseline.inspect()
        for name, config in arms.items():
            path = root / f"{name}.db"
            shutil.copy2(baseline.path, path)
            host = UnifiedSubject(path, cartridge, cognition=FixedThought())
            # Experiment-only fork: change exactly one edge on an identical closed
            # subject snapshot. The production constructor rejects silent changes.
            with host._transaction():
                host.config = config
            first = host.heartbeat()
            after = host.inspect()
            reopened = UnifiedSubject(path, cartridge, cognition=Silence())
            restart_equal = reopened.inspect() == after
            following = reopened.heartbeat()
            results[name] = {
                "config": asdict(config), "probe_action": first["action"],
                "following_action": following["action"],
                "fear": after["engine"]["pressures"]["fear"],
                "fear_change": after["engine"]["pressures"]["fear"] - snapshot["engine"]["pressures"]["fear"],
                "thought_text": [r["first_person"] for r in after["workspace"]["records"] if r["source"] == "thought"],
                "effect_count": sum(len(t["effects"]) for t in after["trace"] if t["kind"] == "inner_ear"),
                "restart_equal": restart_equal,
                "world_presence": after["engine"]["present_others"],
                "commitment_status": after["continuity"]["commitments"]["return"]["status"],
            }
    full, buffer = results["full"], results["transcript_only"]
    checks = {
        "same_thought_full_vs_buffer": full["thought_text"] == buffer["thought_text"],
        "different_affect_full_vs_buffer": full["fear"] > buffer["fear"],
        "different_conduct_full_vs_buffer": full["probe_action"] != buffer["probe_action"],
        "different_conduct_after_restart": full["following_action"] != buffer["following_action"],
        "all_restarts_preserve_snapshot": all(r["restart_equal"] for r in results.values()),
        "ablations_remove_feedback": all(r["effect_count"] == 0 for n, r in results.items() if n != "full"),
        "no_invented_arrival": all(not r["world_presence"] for r in results.values()),
    }
    return {"protocol": "matched-inner-ear-v1", "evidence_class": "builder-designed deterministic engineering",
            "limitations": ["One authored history and one fixed thought; no independent holdout or live-model evidence.",
                            "Does not establish consciousness, general rumination, or human recognizability.",
                            "Full organism removal and raw-telemetry cognition controls are not implemented."],
            "arms": results, "checks": checks, "passed": all(checks.values())}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate()
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
