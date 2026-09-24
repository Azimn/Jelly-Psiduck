"""Deterministic engineering evaluation for the v0.3 candidate."""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from dataclasses import replace
from pathlib import Path

from digital_subject.models import Event

from .endogenous_evaluation import experimental_cartridge
from .v03 import ReverieConfig, ReverieSubject


class CountingSilence:
    def __init__(self):
        self.calls = 0

    def think(self, view):
        self.calls += 1
        return None


def _promise(host):
    host.enqueue(Event(
        "promise_made",
        "Mara",
        "Mara expects to be back before evening.",
        tags=("Mara", "return"),
        metadata={"commitment": {
            "id": "return-Mara",
            "actor": "Mara",
            "description": "Mara expects to be back before evening.",
            "due_tick": 1,
            "importance": 0.9,
        }},
    ))
    host.heartbeat()


def _run(host, ticks):
    return [host.heartbeat() for _ in range(ticks)]


def evaluate():
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        cartridge = experimental_cartridge()

        silent = CountingSilence()
        idle = ReverieSubject(root / "idle.db", cartridge, cognition=silent)
        idle_results = _run(idle, 16)
        idle_state = idle.inspect()
        idle_triggers = [
            t["tick"] for t in idle_state["trace"]
            if t["kind"] == "cognition_trigger" and t["trigger"]["kind"] == "idle_reverie"
        ]

        no_idle_provider = CountingSilence()
        no_idle = ReverieSubject(
            root / "no-idle.db",
            cartridge,
            cognition=no_idle_provider,
            config=ReverieConfig(idle_reverie=False),
        )
        _run(no_idle, 16)
        no_idle_triggers = [
            t for t in no_idle.inspect()["trace"]
            if t["kind"] == "cognition_trigger" and t["trigger"]["kind"] == "idle_reverie"
        ]

        balanced = ReverieSubject(root / "balanced.db", cartridge, cognition=CountingSilence())
        with balanced._transaction():
            balanced._add("perception", "I can still see the bird near the window.")
            balanced._add("memory", "I remember the bridge.")
            for index in range(12):
                balanced._add("thought", f"I keep circling the same question, pass {index}.")
            for _ in range(3):
                balanced._add("memory", "I remember the bridge.")
        view = balanced._cognitive_view()
        thought_slots = sum(item.source == "thought" for item in view.experiences)
        bridge_slots = sum(item.first_person == "I remember the bridge." for item in view.experiences)

        base_config = ReverieConfig(
            idle_reverie=False,
            associative_drift=False,
            thought_recurrence=False,
        )
        habituated = ReverieSubject(
            root / "habituated.db", cartridge, cognition=CountingSilence(), config=base_config)
        unhabituated = ReverieSubject(
            root / "unhabituated.db", cartridge, cognition=CountingSilence(),
            config=replace(base_config, concern_habituation=False))
        for host in (habituated, unhabituated):
            _promise(host)
            _run(host, 60)

        def concern_ticks(host):
            return [
                t["tick"] for t in host.inspect()["trace"]
                if t["kind"] == "cognition_trigger"
                and t["trigger"]["kind"] == "unresolved_concern"
            ]

        hab_ticks = concern_ticks(habituated)
        raw_ticks = concern_ticks(unhabituated)

        restart = ReverieSubject(root / "restart.db", cartridge, cognition=CountingSilence())
        _run(restart, 3)
        fork_path = root / "restart-fork.db"
        shutil.copyfile(restart.path, fork_path)
        fork = ReverieSubject(fork_path, cartridge, cognition=CountingSilence())
        first = _run(restart, 12)
        second = _run(fork, 12)

        checks = {
            "idle_reverie_occurs_without_forced_thought": bool(idle_triggers)
                and not any(result["thoughts"] for result in idle_results),
            "idle_silence_backs_off": idle_triggers[:3] == [2, 6, 14],
            "idle_ablation_removes_idle_triggers": not no_idle_triggers and no_idle_provider.calls == 0,
            "balanced_view_keeps_identity": view.experiences[0].first_person.startswith("I know myself as "),
            "balanced_view_caps_thoughts": thought_slots <= 3,
            "balanced_view_deduplicates_memory_text": bridge_slots == 1,
            "balanced_view_retains_external_context": any(item.source == "perception" for item in view.experiences),
            "habituation_reduces_forced_concern_returns": len(hab_ticks) < len(raw_ticks) and bool(raw_ticks),
            "restart_future_trajectory_matches": first == second and restart.inspect() == fork.inspect(),
        }
        return {
            "protocol": "v03-idle-reverie-development",
            "checks": checks,
            "passed": all(checks.values()),
            "idle_trigger_ticks": idle_triggers,
            "concern_trigger_ticks": {"habituation_on": hab_ticks, "habituation_off": raw_ticks},
            "balanced_view": [
                {"source": item.source, "first_person": item.first_person}
                for item in view.experiences
            ],
            "limitations": [
                "Deterministic engineering characterization, not live-model efficacy evidence.",
                "Idle cadence is measured in heartbeats; wall-clock cadence is host controlled.",
                "Balanced-view quotas are experimental attention policy, not a biological capacity claim.",
                "This branch deliberately excludes the separate lived-history/Pretorius experiment.",
            ],
        }


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
