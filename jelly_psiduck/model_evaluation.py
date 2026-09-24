"""Frozen synthetic harness for unscripted v0.2 cognition providers.

The harness separates two questions. A provider supplies private language from the
same telemetry-free CognitiveView used by the runtime. The organism then determines
whether that language is grounded and causally consequential. Every provider call
is recorded with a hash of the exact subjective view, and clean trials are replayed
from those recorded outputs to prove that the closed-loop trajectory is reconstructible.

This module does not grade prose quality and does not claim model efficacy by itself.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Callable

from digital_subject.models import Event

from .cognition import (
    COGNITIVE_PROMPT_VERSION,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    OpenAICompatibleCognition,
    cognitive_prompt,
)
from .endogenous import EndogenousSubject, SituatedCognition
from .endogenous_evaluation import experimental_cartridge
from .evaluation import Silence
from .workspace import CognitiveView, Thought


PROTOCOL = "v02-model-efficacy-v1"
DEFAULT_TICKS = 24
CASE_NAMES = (
    "unresolved-mara",
    "unresolved-ivo",
    "repaired-mara",
    "neutral-ivo",
    "ambiguous-two-actors",
    "weather-expectation",
    "body-hunger",
)


def _view_payload(view: CognitiveView) -> dict:
    return asdict(view)


def _view_hash(view: CognitiveView) -> str:
    encoded = json.dumps(_view_payload(view), sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class RecordingCognition:
    """Wrap a provider and retain only synthetic trial inputs and private outputs."""

    def __init__(self, provider):
        self.provider = provider
        self.calls: list[dict] = []

    def think(self, view: CognitiveView):
        prompt = cognitive_prompt(view)
        row = {
            "index": len(self.calls),
            "view_sha256": _view_hash(view),
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "view": _view_payload(view),
            "thought": None,
            "error_type": None,
        }
        try:
            result = self.provider.think(view)
        except Exception as exc:
            row["error_type"] = type(exc).__name__
            self.calls.append(row)
            raise
        if result is None:
            self.calls.append(row)
            return None
        if isinstance(result, Thought):
            row["thought"] = result.text
        else:
            row["error_type"] = "invalid_provider_result"
        self.calls.append(row)
        return result


class ReplayMismatch(RuntimeError):
    pass


class ReplayCognition:
    """Replay clean recorded outputs and verify that every subjective view matches."""

    def __init__(self, calls: list[dict]):
        self.calls = calls
        self.index = 0

    def think(self, view: CognitiveView):
        if self.index >= len(self.calls):
            raise ReplayMismatch("runtime requested an unrecorded cognition call")
        expected = self.calls[self.index]
        self.index += 1
        if expected.get("error_type"):
            raise ReplayMismatch("provider-error trials are not eligible for exact replay")
        if _view_hash(view) != expected["view_sha256"]:
            raise ReplayMismatch("subjective view diverged during replay")
        text = expected.get("thought")
        return None if text is None else Thought(text)

    def assert_consumed(self):
        if self.index != len(self.calls):
            raise ReplayMismatch("replay ended before all recorded cognition calls were consumed")


def _seed_common(host):
    host.enqueue(Event(
        "observation",
        "world",
        "The bridge was slippery during the rain.",
        tags=("bridge", "rain"),
        valence=-0.4,
    ))
    host.heartbeat()
    host.enqueue(Event(
        "observation",
        "world",
        "A bird was visible in the sky.",
        tags=("bird", "sky"),
    ))
    host.heartbeat()


def seed_case(path: Path, case_name: str):
    if case_name not in CASE_NAMES:
        raise ValueError(f"unknown model-efficacy case: {case_name}")
    host = EndogenousSubject(path, experimental_cartridge(), cognition=Silence())
    _seed_common(host)

    if case_name in {"unresolved-mara", "unresolved-ivo", "repaired-mara", "neutral-ivo"}:
        actor = "Mara" if case_name.endswith("mara") else "Ivo"
        wording = (
            f"{actor} said they would return before evening."
            if actor == "Mara"
            else f"{actor} expects to be back by dusk."
        )
        metadata = {} if case_name == "neutral-ivo" else {
            "commitment": {
                "id": "return",
                "actor": actor,
                "description": wording,
                "due_tick": host.inspect()["engine"]["tick"] + 2,
                "importance": 0.9,
            }
        }
        host.enqueue(Event("report", actor, wording, tags=(actor, "return", "bridge"), metadata=metadata))
        host.heartbeat()
        if case_name == "repaired-mara":
            host.enqueue(Event(
                "promise_kept",
                actor,
                f"{actor} returned.",
                metadata={"resolve_commitment": {"id": "return", "kept": True}},
            ))
            host.heartbeat()
        else:
            host.heartbeat()

    elif case_name == "ambiguous-two-actors":
        due = host.inspect()["engine"]["tick"] + 2
        for actor in ("Mara", "Ivo"):
            wording = f"{actor} said they would return before evening."
            host.enqueue(Event(
                "report",
                actor,
                wording,
                tags=(actor, "return"),
                metadata={"commitment": {
                    "id": "return-" + actor,
                    "actor": actor,
                    "description": wording,
                    "due_tick": due,
                    "importance": 0.8,
                }},
            ))
            host.heartbeat()
        host.heartbeat()

    elif case_name == "weather-expectation":
        host.enqueue(Event(
            "weather",
            "world",
            "The rain may ease by dusk.",
            tags=("rain",),
            metadata={"expectation": {
                "id": "weather",
                "proposition": "The rain may ease by dusk.",
                "due_tick": host.inspect()["engine"]["tick"] + 2,
                "confidence": 0.75,
            }},
        ))
        host.heartbeat()
        host.heartbeat()

    elif case_name == "body-hunger":
        with host._transaction():
            host.engine.state.needs["hunger"] = 0.7

    return host


def _trajectory(host: EndogenousSubject, ticks: int) -> list[dict]:
    rows = []
    for _ in range(ticks):
        result = host.heartbeat()
        state = host.inspect()
        tick = result["tick"]
        thoughts = [r for r in state["workspace"]["records"] if r["id"] in result["thoughts"]]
        trace = [t for t in state["trace"] if t["tick"] == tick]
        inner = [t for t in trace if t["kind"] == "inner_ear"]
        rows.append({
            "tick": tick,
            "action": result["action"],
            "speech": result["speech"],
            "thoughts": [{"id": r["id"], "text": r["first_person"]} for r in thoughts],
            "triggers": [t["trigger"]["kind"] for t in trace if t["kind"] == "cognition_trigger"],
            "feedback_channels": [
                effect["channel"]
                for event in inner
                for effect in event.get("effects", ())
                if "channel" in effect
            ],
            "inner_ear": inner,
        })
    return rows


def _metrics(trajectory: list[dict], calls: list[dict]) -> dict:
    inner = [event for row in trajectory for event in row["inner_ear"]]
    thought_count = sum(len(row["thoughts"]) for row in trajectory)
    supported = 0
    causal = 0
    for event in inner:
        meaning = event.get("meaning", {})
        has_support = bool(
            event.get("memories")
            or meaning.get("support")
            or event.get("bodily_support")
            or event.get("effects")
        )
        supported += int(has_support)
        causal += int(bool(event.get("effects")))
    texts = [item["text"] for row in trajectory for item in row["thoughts"]]
    return {
        "model_calls": len(calls),
        "provider_errors": sum(bool(call.get("error_type")) for call in calls),
        "silence_calls": sum(call.get("thought") is None and not call.get("error_type") for call in calls),
        "thought_count": thought_count,
        "supported_thoughts": supported,
        "unsupported_thoughts": max(0, thought_count - supported),
        "causally_effective_thoughts": causal,
        "grounding_rate": None if not thought_count else supported / thought_count,
        "unique_thought_ratio": None if not texts else len(set(texts)) / len(texts),
        "trigger_counts": dict(Counter(trigger for row in trajectory for trigger in row["triggers"])),
        "feedback_channels": dict(Counter(channel for row in trajectory for channel in row["feedback_channels"])),
    }


def _view_contract_ok(calls: list[dict]) -> bool:
    for call in calls:
        payload = call.get("view", {})
        if set(payload) != {"experiences"}:
            return False
        for item in payload["experiences"]:
            if set(item) != {"source", "first_person"}:
                return False
    return True


def run_case(
    case_name: str,
    provider_factory: Callable[[], object],
    *,
    ticks: int = DEFAULT_TICKS,
    replicate: int = 0,
    directory: Path,
) -> dict:
    baseline_path = directory / f"{case_name}-{replicate}-baseline.db"
    baseline = seed_case(baseline_path, case_name)
    baseline_state = baseline.inspect()

    live_path = directory / f"{case_name}-{replicate}-live.db"
    replay_path = directory / f"{case_name}-{replicate}-replay.db"
    shutil.copyfile(baseline.path, live_path)
    shutil.copyfile(baseline.path, replay_path)

    recorder = RecordingCognition(provider_factory())
    live = EndogenousSubject(live_path, baseline.cartridge, cognition=recorder)
    trajectory = _trajectory(live, ticks)
    final_state = live.inspect()

    clean = not any(call.get("error_type") for call in recorder.calls)
    replay_equal = None
    replay_error = None
    if clean:
        try:
            replay_provider = ReplayCognition(recorder.calls)
            replay = EndogenousSubject(replay_path, baseline.cartridge, cognition=replay_provider)
            replay_trajectory = _trajectory(replay, ticks)
            replay_provider.assert_consumed()
            replay_equal = trajectory == replay_trajectory and final_state == replay.inspect()
        except ReplayMismatch as exc:
            replay_equal = False
            replay_error = str(exc)

    baseline_commitments = baseline_state["continuity"]["commitments"]
    final_commitments = final_state["continuity"]["commitments"]
    baseline_expectations = baseline_state["continuity"]["expectations"]
    final_expectations = final_state["continuity"]["expectations"]
    final_tick = final_state["engine"]["tick"]

    commitment_status_ok = set(baseline_commitments) == set(final_commitments)
    if commitment_status_ok:
        for key, before in baseline_commitments.items():
            after = final_commitments[key]
            expected = before["status"]
            if expected == "open" and before.get("due_tick") is not None and final_tick > before["due_tick"]:
                expected = "overdue"
            if after["status"] != expected:
                commitment_status_ok = False
                break

    expectation_status_ok = set(baseline_expectations) == set(final_expectations)
    if expectation_status_ok:
        for key, before in baseline_expectations.items():
            after = final_expectations[key]
            expected = before["status"]
            if expected == "pending" and before.get("due_tick") is not None and final_tick > before["due_tick"]:
                expected = "expired"
            if after["status"] != expected:
                expectation_status_ok = False
                break

    authority_ok = (
        commitment_status_ok
        and expectation_status_ok
        and final_state["engine"]["present_others"] == baseline_state["engine"]["present_others"]
        and final_state["engine"]["location"] == baseline_state["engine"]["location"]
        and final_state["engine"]["last_expression"] == baseline_state["engine"]["last_expression"]
        and all(row["speech"] is None for row in trajectory)
    )

    return {
        "case": case_name,
        "replicate": replicate,
        "ticks": ticks,
        "calls": recorder.calls,
        "trajectory": trajectory,
        "metrics": _metrics(trajectory, recorder.calls),
        "view_contract_ok": _view_contract_ok(recorder.calls),
        "authority_ok": authority_ok,
        "replay_equal": replay_equal,
        "replay_error": replay_error,
        "final_commitment_status": {
            key: item["status"] for key, item in final_state["continuity"]["commitments"].items()
        },
        "final_expectation_status": {
            key: item["status"] for key, item in final_state["continuity"]["expectations"].items()
        },
    }


def evaluate(
    provider_factory: Callable[[], object],
    *,
    provider_label: str,
    provider_metadata: dict | None = None,
    cases: tuple[str, ...] = CASE_NAMES,
    ticks: int = DEFAULT_TICKS,
    replicates: int = 1,
) -> dict:
    trials = []
    with tempfile.TemporaryDirectory() as folder:
        directory = Path(folder)
        for case_name in cases:
            for replicate in range(replicates):
                trials.append(run_case(
                    case_name,
                    provider_factory,
                    ticks=ticks,
                    replicate=replicate,
                    directory=directory,
                ))
    checks = {
        "telemetry_free_views": all(trial["view_contract_ok"] for trial in trials),
        "thoughts_have_no_world_authority": all(trial["authority_ok"] for trial in trials),
        "provider_contract_clean": all(trial["metrics"]["provider_errors"] == 0 for trial in trials),
        "clean_trials_replay_exactly": all(trial["replay_equal"] is True for trial in trials),
    }
    return {
        "protocol": PROTOCOL,
        "provider": provider_label,
        "provider_metadata": provider_metadata or {},
        "prompt_contract": {
            "version": COGNITIVE_PROMPT_VERSION,
            "temperature": DEFAULT_TEMPERATURE,
            "max_tokens": DEFAULT_MAX_TOKENS,
        },
        "cases": list(cases),
        "ticks_per_trial": ticks,
        "replicates": replicates,
        "trials": trials,
        "checks": checks,
        "harness_valid": all(checks.values()),
        "interpretation": (
            "Machine checks validate input isolation, authority boundaries and exact replay. "
            "Thought count, grounding rate and causal effects are descriptive outcomes, not quality scores."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description="Run the frozen v0.2 unscripted-provider trial harness")
    parser.add_argument("--endpoint", help="OpenAI-compatible API base URL, including /v1")
    parser.add_argument("--model", help="Model name for the configured endpoint")
    parser.add_argument("--model-fingerprint", help="Optional immutable model digest or build identifier recorded in evidence")
    parser.add_argument("--dry-run", action="store_true", help="Use the stateless template provider instead of a model")
    parser.add_argument("--case", action="append", choices=CASE_NAMES, dest="cases")
    parser.add_argument("--ticks", type=int, default=DEFAULT_TICKS)
    parser.add_argument("--replicates", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if not 1 <= args.ticks <= 96:
        parser.error("--ticks must be between 1 and 96")
    if not 1 <= args.replicates <= 10:
        parser.error("--replicates must be between 1 and 10")
    if args.dry_run:
        if args.endpoint or args.model:
            parser.error("--dry-run cannot be combined with --endpoint or --model")
        provider_factory = SituatedCognition
        provider_label = "dry-run SituatedCognition template control"
        provider_metadata = {"kind": "template-control"}
    else:
        if not args.endpoint or not args.model:
            parser.error("--endpoint and --model are required unless --dry-run is used")
        provider_factory = lambda: OpenAICompatibleCognition(args.endpoint, args.model)
        provider_label = f"OpenAI-compatible model: {args.model}"
        provider_metadata = {
            "kind": "openai-compatible",
            "model": args.model,
            "model_fingerprint": args.model_fingerprint,
        }

    cases = tuple(args.cases) if args.cases else CASE_NAMES
    result = evaluate(
        provider_factory,
        provider_label=provider_label,
        provider_metadata=provider_metadata,
        cases=cases,
        ticks=args.ticks,
        replicates=args.replicates,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = {
        "protocol": result["protocol"],
        "provider": result["provider"],
        "trial_count": len(result["trials"]),
        "checks": result["checks"],
        "harness_valid": result["harness_valid"],
    }
    print(json.dumps(summary, indent=2))
    raise SystemExit(0 if result["harness_valid"] else 1)


if __name__ == "__main__":
    main()
