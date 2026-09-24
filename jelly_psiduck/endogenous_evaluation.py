"""Unattended matched-store development experiment for the v0.2 candidate."""
import argparse
import json
import shutil
import tempfile
from collections import Counter
from dataclasses import replace
from pathlib import Path

from digital_subject.cartridge import load_cartridge
from digital_subject.models import Event
from .cli import DEFAULT_CARTRIDGE
from .endogenous import EndogenousConfig, EndogenousSubject, SituatedCognition
from .evaluation import Silence


def experimental_cartridge():
    """Matched bodily baseline isolates recurrence from incidental need crossings."""
    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    lows = {"energy", "comfort", "warmth", "safety", "focus", "satisfaction"}
    return replace(cartridge, need_rates={}, activities=(), habits=(),
                   need_setpoints={key: .9 if key in lows else .1 for key in cartridge.need_setpoints})


def seed(root, case, actor):
    host = EndogenousSubject(root, experimental_cartridge(), cognition=Silence())
    host.enqueue(Event("observation", "world", "The bridge was slippery during the rain.",
                       tags=("bridge", "rain"), valence=-.4))
    host.heartbeat()
    text = f"{actor} said they would return before evening." if actor == "Mara" else f"{actor} expects to be back by dusk."
    metadata = {} if case == "neutral" else {"commitment": {
        "id": "return", "actor": actor, "description": text, "due_tick": 5, "importance": .9}}
    host.enqueue(Event("report", actor, text, tags=(actor, "return", "bridge"), metadata=metadata))
    host.heartbeat()
    host.enqueue(Event("observation", "world", "A bird was visible in the sky.", tags=("bird", "sky")))
    host.heartbeat()
    if case == "repaired":
        host.enqueue(Event("promise_kept", actor, f"{actor} returned.", metadata={
            "resolve_commitment": {"id": "return", "kept": True}}))
        host.heartbeat()
    else:
        host.heartbeat()
    return host


def trajectory(host, ticks):
    rows = []
    for _ in range(ticks):
        result = host.heartbeat()
        state = host.inspect()
        tick = result["tick"]
        thoughts = [r for r in state["workspace"]["records"] if r["id"] in result["thoughts"]]
        trace = [t for t in state["trace"] if t["tick"] == tick]
        triggers = [t["trigger"]["kind"] for t in trace if t["kind"] == "cognition_trigger"]
        channels = [e["channel"] for t in trace if t["kind"] == "inner_ear" for e in t["effects"]]
        rows.append({"tick": tick, "action": result["action"], "speech": result["speech"],
                     "thoughts": [r["first_person"] for r in thoughts], "triggers": triggers,
                     "feedback_channels": channels, "fear": state["engine"]["pressures"]["fear"],
                     "attention": state["attention"]})
    return rows


def evaluate():
    config = EndogenousConfig()
    arms = {"full": config, "no_concern_recurrence": replace(config, concern_recurrence=False),
            "no_thought_recurrence": replace(config, thought_recurrence=False),
            "no_associative_drift": replace(config, associative_drift=False),
            "no_memory_feedback": replace(config, memory_feedback=False),
            "no_prospective_feedback": replace(config, prospective_feedback=False),
            "transcript_only": replace(config, thought_effects=False),
            "no_autonomous_cognition": replace(config, autonomous_cognition=False)}
    cases = [("unresolved", "Mara"), ("unresolved", "Ivo"), ("repaired", "Mara"), ("neutral", "Ivo")]
    results = {}
    with tempfile.TemporaryDirectory() as folder:
        directory = Path(folder)
        for index, (case, actor) in enumerate(cases):
            baseline = seed(directory / f"base-{index}.db", case, actor)
            case_results = {}
            for arm, settings in arms.items():
                path = directory / f"{index}-{arm}.db"
                shutil.copyfile(baseline.path, path)
                host = EndogenousSubject(path, baseline.cartridge)
                with host._transaction():
                    host.config = settings
                first = trajectory(host, 8)
                fork_path = directory / f"{index}-{arm}-restart.db"
                shutil.copyfile(host.path, fork_path)
                restarted = EndogenousSubject(fork_path, baseline.cartridge)
                latter = trajectory(host, 16)
                resumed = trajectory(restarted, 16)
                rows = first + latter
                state = host.inspect()
                case_results[arm] = {"trajectory": rows,
                    "thought_count": sum(len(r["thoughts"]) for r in rows),
                    "trigger_counts": dict(Counter(t for r in rows for t in r["triggers"])),
                    "channel_counts": dict(Counter(c for r in rows for c in r["feedback_channels"])),
                    "restart_equal": latter == resumed and state == restarted.inspect(),
                    "commitments": {key: item["status"] for key, item in state["continuity"]["commitments"].items()},
                    "world_presence": state["engine"]["present_others"]}
            results[f"{case}-{actor}"] = case_results
    checks = {
        "all_restart_trajectories_match": all(r["restart_equal"] for case in results.values() for r in case.values()),
        "unresolved_attention_returns": all(results[f"unresolved-{actor}"]["full"]["trigger_counts"].get("unresolved_concern", 0) > 0 for actor in ("Mara", "Ivo")),
        "concern_recurrence_ablation_removes_its_triggers": all(not case["no_concern_recurrence"]["trigger_counts"].get("unresolved_concern", 0) for case in results.values()),
        "repaired_and_neutral_do_not_recur_as_unresolved": all(not results[name]["full"]["trigger_counts"].get("unresolved_concern", 0) for name in ("repaired-Mara", "neutral-Ivo")),
        "prior_thoughts_create_later_opportunities": any(case["full"]["trigger_counts"].get("prior_thought", 0) for case in results.values()),
        "thought_recurrence_ablation_removes_its_triggers": all(not case["no_thought_recurrence"]["trigger_counts"].get("prior_thought", 0) for case in results.values()),
        "association_ablation_removes_its_triggers": all(not case["no_associative_drift"]["trigger_counts"].get("association", 0) for case in results.values()),
        "associated_memories_create_later_opportunities": any(case["full"]["trigger_counts"].get("association", 0) for case in results.values()),
        "memory_off_retains_prospective_feedback": all(case["no_memory_feedback"]["channel_counts"].get("prospective", 0) and not case["no_memory_feedback"]["channel_counts"].get("memory", 0) for name, case in results.items() if name.startswith("unresolved")),
        "prospective_off_retains_memory_feedback": all(case["no_prospective_feedback"]["channel_counts"].get("memory", 0) and not case["no_prospective_feedback"]["channel_counts"].get("prospective", 0) for name, case in results.items() if name.startswith("unresolved")),
        "transcript_control_has_no_thought_feedback": all(not case["transcript_only"]["channel_counts"] for case in results.values()),
        "autonomy_off_has_no_unattended_thoughts": all(not case["no_autonomous_cognition"]["thought_count"] for case in results.values()),
        "no_thought_invents_arrival": all(not arm["world_presence"] for case in results.values() for arm in case.values()),
    }
    return {"protocol": "unattended-endogenous-v02-development", "baseline": "9a7945c",
            "provider": "stateless SituatedCognition templates; no model calls",
            "ticks_per_arm": 24, "scenarios": results, "checks": checks, "passed": all(checks.values()),
            "limitations": ["Development cases, not independent holdouts or real-model efficacy evidence.",
                            "Body setpoints, rates and activities are controlled to isolate recurrence; graded body dynamics are tested separately.",
                            "Discourse interpretation has a bounded English grammar, not general semantic understanding."]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate()
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(json.dumps({"checks": result["checks"], "passed": result["passed"]}, indent=2))
    else:
        print(text)
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
