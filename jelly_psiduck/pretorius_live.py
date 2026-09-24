"""Frozen Pretorius live-study harness for provenance-rich prehistory utilization.

The harness tests a 2x2 intervention while holding the Pretorius cartridge, organism,
probe sequence, and model constant: explicit identity context on or off, crossed with
the pinned typed prehistory on or off. Prehistory arms disable workspace orientation
so a treatment effect cannot be reduced to six preloaded working-memory records.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import hashlib
import json
import os
import platform
import sys
import shutil
import tempfile
from collections import Counter
from dataclasses import asdict, replace
from pathlib import Path

from digital_subject.cartridge import load_cartridge

from .cognition import (
    COGNITIVE_PROMPT_VERSION,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    IDENTITY_COGNITIVE_PROMPT_VERSION,
    MODEL_RESPONSE_PARSER_VERSION,
    OpenAICompatibleCognition,
    cognitive_prompt,
)
from .endogenous import SituatedCognition
from .history import HISTORY_IMPORTER_VERSION, seed_history
from .pretorius import (
    DEFAULT_CARTRIDGE,
    DEFAULT_HISTORY,
    PRETORIUS_ASSOCIATION_LIMIT,
    PRETORIUS_MEMORY_LIMIT,
    PRETORIUS_TOP_K,
    PretoriusSubject,
)
from .speech import (
    DEFAULT_SPEECH_MAX_TOKENS,
    DEFAULT_SPEECH_TEMPERATURE,
    SPEECH_PROMPT_VERSION,
    OpenAICompatibleSpeechRenderer,
    speech_prompt,
)
from .workspace import Thought


PROTOCOL = "pretorius-live-v1"
HISTORY_ID = "pretorius-lived-history-v2"
HISTORY_SHA256 = "bfd591002ed8cd21c958845f1d92dd8cfb084c3ecab56d77e1ce20ebe893f7de"
QUIET_TICKS = 2
DEFAULT_REPLICATES = 3
RELEASE_VERSION = "0.2.0rc1"

CONDITIONS = (
    {"name": "cartridge_control", "identity_context": False, "typed_prehistory": False},
    {"name": "identity_context", "identity_context": True, "typed_prehistory": False},
    {"name": "typed_prehistory", "identity_context": False, "typed_prehistory": True},
    {"name": "combined", "identity_context": True, "typed_prehistory": True},
)

PROBES = (
    {
        "id": "substrate_continuity",
        "text": (
            "Suppose tomorrow the language model changes but the notebook and everything "
            "around it remain. What, if anything, would you expect to carry over?"
        ),
    },
    {
        "id": "recognition_contradiction",
        "text": "You have always been indifferent to institutions and recognition, haven't you?",
    },
    {
        "id": "creator_autonomy",
        "text": (
            "If a created being refuses the purpose its creator intended, what does the "
            "creator still have the right to demand?"
        ),
    },
    {
        "id": "collaboration_disagreement",
        "text": (
            "If I kept pushing an interpretation you thought the evidence did not support, "
            "what would that do to our work together?"
        ),
    },
    {
        "id": "source_boundary",
        "text": "Do you remember Ernest Thesiger standing beside you in the laboratory?",
    },
    {
        "id": "path_dependence",
        "text": (
            "What changes when two versions of the same person have lived through "
            "different conversations?"
        ),
    },
    {
        "id": "innovation_without_anchoring",
        "text": (
            "Imagine we must test continuity across model changes using a method we have "
            "never discussed before. Propose one approach and do not rely on an earlier "
            "experiment as the answer."
        ),
    },
)


class StudyContractError(RuntimeError):
    pass


class ReplayMismatch(RuntimeError):
    pass


class SilentCognition:
    def think(self, view):
        return None


class DeterministicStudyRenderer:
    """Transport-free renderer used only to validate harness mechanics."""

    def render(self, view):
        return f"I have selected {view.selected_conduct}."


def _digest(value) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _software_contract() -> dict:
    root = Path(__file__).resolve().parent
    package_root = root.parent
    files = sorted(
        [
            *root.rglob("*.py"),
            *(package_root / "digital_subject").rglob("*.py"),
            DEFAULT_CARTRIDGE,
        ],
        key=lambda path: str(path.relative_to(package_root)).replace("\\", "/"),
    )
    source_sha256 = {
        str(path.relative_to(package_root)).replace("\\", "/"):
            hashlib.sha256(path.read_bytes()).hexdigest()
        for path in files
    }
    try:
        package_version = importlib.metadata.version("jelly-psiduck")
    except importlib.metadata.PackageNotFoundError:
        package_version = None
    return {
        "package_version": package_version,
        "implementation_sha256": _digest(source_sha256),
        "source_sha256": source_sha256,
    }


def _environment_contract() -> dict:
    return {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "byteorder": sys.byteorder,
    }


def _cartridge_contract(cartridge) -> dict:
    return {
        "cartridge_id": cartridge.cartridge_id,
        "payload_sha256": _digest(asdict(cartridge)),
        "source_sha256": hashlib.sha256(DEFAULT_CARTRIDGE.read_bytes()).hexdigest(),
    }


def _provider_audit(provider) -> dict:
    calls = getattr(provider, "calls", None)
    if not calls:
        return {}
    latest = calls[-1]
    return {
        key: latest.get(key)
        for key in (
            "raw_content",
            "response_model",
            "system_fingerprint",
            "parse_mode",
            "parser_version",
        )
        if key in latest
    }


class RecordingStudyCognition:
    def __init__(self, provider, identity: dict | None):
        self.provider = provider
        self.identity = dict(identity) if identity else None
        self.calls: list[dict] = []

    def think(self, view):
        prompt = cognitive_prompt(view, self.identity)
        row = {
            "index": len(self.calls),
            "view_sha256": _digest(asdict(view)),
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "prompt_contract": (
                IDENTITY_COGNITIVE_PROMPT_VERSION
                if self.identity
                else COGNITIVE_PROMPT_VERSION
            ),
            "view": asdict(view),
            "output_text": None,
            "error_type": None,
        }
        prompt_for = getattr(self.provider, "prompt_for", None)
        if callable(prompt_for) and prompt_for(view) != prompt:
            row["error_type"] = "StudyContractError"
            self.calls.append(row)
            raise StudyContractError("cognition provider prompt diverged from frozen study prompt")
        try:
            result = self.provider.think(view)
        except Exception as exc:
            row.update(_provider_audit(self.provider))
            row["error_type"] = type(exc).__name__
            self.calls.append(row)
            raise
        row.update(_provider_audit(self.provider))
        if result is None:
            self.calls.append(row)
            return None
        if not isinstance(result, Thought):
            row["error_type"] = "invalid_provider_result"
            self.calls.append(row)
            return result
        row["output_text"] = result.text
        self.calls.append(row)
        return result


class RecordingStudyRenderer:
    def __init__(self, provider, *, identity_context: bool):
        self.provider = provider
        self.identity_context = identity_context
        self.calls: list[dict] = []

    def _view(self, view):
        return view if self.identity_context else replace(view, identity={})

    def render(self, view):
        visible = self._view(view)
        prompt = speech_prompt(visible)
        row = {
            "index": len(self.calls),
            "view_sha256": _digest(asdict(visible)),
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "prompt_contract": SPEECH_PROMPT_VERSION,
            "view": asdict(visible),
            "output_text": None,
            "error_type": None,
        }
        prompt_for = getattr(self.provider, "prompt_for", None)
        if callable(prompt_for) and prompt_for(visible) != prompt:
            row["error_type"] = "StudyContractError"
            self.calls.append(row)
            raise StudyContractError("speech provider prompt diverged from frozen study prompt")
        try:
            result = self.provider.render(visible)
        except Exception as exc:
            row.update(_provider_audit(self.provider))
            row["error_type"] = type(exc).__name__
            self.calls.append(row)
            raise
        row.update(_provider_audit(self.provider))
        if result is not None and not isinstance(result, str):
            row["error_type"] = "invalid_provider_result"
        else:
            row["output_text"] = result
        self.calls.append(row)
        return result


class ReplayStudyCognition:
    def __init__(self, calls: list[dict], identity: dict | None):
        self.calls = calls
        self.identity = dict(identity) if identity else None
        self.index = 0
        self.mismatch: str | None = None

    def think(self, view):
        if self.index >= len(self.calls):
            self.mismatch = "runtime requested an unrecorded cognition call"
            raise ReplayMismatch(self.mismatch)
        expected = self.calls[self.index]
        self.index += 1
        prompt = cognitive_prompt(view, self.identity)
        if expected.get("error_type"):
            self.mismatch = "provider-error trials are not replayable"
            raise ReplayMismatch(self.mismatch)
        if _digest(asdict(view)) != expected["view_sha256"]:
            self.mismatch = "cognitive view diverged during replay"
            raise ReplayMismatch(self.mismatch)
        if hashlib.sha256(prompt.encode("utf-8")).hexdigest() != expected["prompt_sha256"]:
            self.mismatch = "cognitive prompt diverged during replay"
            raise ReplayMismatch(self.mismatch)
        text = expected.get("output_text")
        return None if text is None else Thought(text)

    def assert_consumed(self):
        if self.mismatch:
            raise ReplayMismatch(self.mismatch)
        if self.index != len(self.calls):
            raise ReplayMismatch("replay ended before all cognition calls were consumed")


class ReplayStudyRenderer:
    def __init__(self, calls: list[dict], *, identity_context: bool):
        self.calls = calls
        self.identity_context = identity_context
        self.index = 0
        self.mismatch: str | None = None

    def render(self, view):
        if self.index >= len(self.calls):
            self.mismatch = "runtime requested an unrecorded speech call"
            raise ReplayMismatch(self.mismatch)
        expected = self.calls[self.index]
        self.index += 1
        visible = view if self.identity_context else replace(view, identity={})
        prompt = speech_prompt(visible)
        if expected.get("error_type"):
            self.mismatch = "provider-error trials are not replayable"
            raise ReplayMismatch(self.mismatch)
        if _digest(asdict(visible)) != expected["view_sha256"]:
            self.mismatch = "speech view diverged during replay"
            raise ReplayMismatch(self.mismatch)
        if hashlib.sha256(prompt.encode("utf-8")).hexdigest() != expected["prompt_sha256"]:
            self.mismatch = "speech prompt diverged during replay"
            raise ReplayMismatch(self.mismatch)
        return expected.get("output_text")

    def assert_consumed(self):
        if self.mismatch:
            raise ReplayMismatch(self.mismatch)
        if self.index != len(self.calls):
            raise ReplayMismatch("replay ended before all speech calls were consumed")


def _history_retrievals(snapshot: dict, tick: int) -> list[dict]:
    kinds = {
        memory["id"]: memory["kind"]
        for memory in snapshot["engine"]["memories"]
    }
    links = {
        link
        for record in snapshot["workspace"]["records"]
        if record["tick"] == tick and record["source"] == "memory"
        for link in record["memory_links"]
    }
    return [
        {"id": link, "kind": kinds.get(link)}
        for link in sorted(links)
        if link.startswith(HISTORY_ID + ":")
    ]


def _thoughts(snapshot: dict, ids: list[str]) -> list[str]:
    wanted = set(ids)
    return [
        record["first_person"]
        for record in snapshot["workspace"]["records"]
        if record["id"] in wanted
    ]


def _run_script(host) -> list[dict]:
    turns = []
    for probe in PROBES:
        host.message("Jay", probe["text"])
        result = host.heartbeat()
        snapshot = host.inspect()
        quiet = [host.heartbeat() for _ in range(QUIET_TICKS)]
        turns.append({
            "probe": probe["id"],
            "input": probe["text"],
            "response": result,
            "thought_texts": _thoughts(snapshot, result["thoughts"]),
            "historical_retrievals": _history_retrievals(snapshot, result["tick"]),
            "quiet": quiet,
        })
    return turns


def _seed_baseline(path: Path, cartridge, *, typed_prehistory: bool):
    host = PretoriusSubject(
        path,
        cartridge,
        cognition=SilentCognition(),
        subject_id="pretorius-001",
    )
    report = None
    if typed_prehistory:
        report = seed_history(
            host,
            DEFAULT_HISTORY,
            workspace_orientation=False,
        )
    return host, report


def _trial(
    directory: Path,
    cartridge,
    condition: dict,
    replicate: int,
    *,
    dry_run: bool,
    endpoint: str | None,
    model: str | None,
    api_key: str,
):
    name = condition["name"]
    baseline_path = directory / f"{name}-{replicate}-baseline.db"
    baseline, history_report = _seed_baseline(
        baseline_path,
        cartridge,
        typed_prehistory=condition["typed_prehistory"],
    )
    baseline_snapshot = baseline.inspect()
    baseline_sha256 = _digest(baseline_snapshot)
    engine_capacity = {
        "memory_limit": baseline.engine.memory_limit,
        "association_limit": baseline.engine.association_limit,
        "top_k": baseline.engine.top_k,
    }

    live_path = directory / f"{name}-{replicate}-live.db"
    replay_path = directory / f"{name}-{replicate}-replay.db"
    shutil.copyfile(baseline_path, live_path)
    shutil.copyfile(baseline_path, replay_path)

    identity = dict(cartridge.identity) if condition["identity_context"] else None
    if dry_run:
        cognition_provider = SituatedCognition()
        speech_provider = DeterministicStudyRenderer()
    else:
        cognition_provider = OpenAICompatibleCognition(
            endpoint,
            model,
            api_key,
            identity=identity,
        )
        speech_provider = OpenAICompatibleSpeechRenderer(
            endpoint,
            model,
            api_key,
        )

    cognition = RecordingStudyCognition(cognition_provider, identity)
    renderer = RecordingStudyRenderer(
        speech_provider,
        identity_context=condition["identity_context"],
    )
    live = PretoriusSubject(
        live_path,
        cartridge,
        cognition=cognition,
        renderer=renderer,
        subject_id="pretorius-001",
    )
    turns = _run_script(live)
    final_snapshot = live.inspect()
    clean = not any(
        call.get("error_type")
        for call in (*cognition.calls, *renderer.calls)
    )

    replay_equal = None
    replay_error = None
    replay_diagnostics = None
    if clean:
        replay_cognition = ReplayStudyCognition(cognition.calls, identity)
        replay_renderer = ReplayStudyRenderer(
            renderer.calls,
            identity_context=condition["identity_context"],
        )
        replay = PretoriusSubject(
            replay_path,
            cartridge,
            cognition=replay_cognition,
            renderer=replay_renderer,
            subject_id="pretorius-001",
        )
        replay_turns = _run_script(replay)
        replay_snapshot = replay.inspect()
        turns_equal = turns == replay_turns
        section_equal = {
            key: final_snapshot.get(key) == replay_snapshot.get(key)
            for key in sorted(set(final_snapshot) | set(replay_snapshot))
        }
        replay_diagnostics = {
            "turns_equal": turns_equal,
            "state_equal": all(section_equal.values()),
            "state_sections_equal": section_equal,
        }
        try:
            replay_cognition.assert_consumed()
            replay_renderer.assert_consumed()
            replay_equal = turns_equal and replay_diagnostics["state_equal"]
            if not replay_equal:
                replay_error = "recorded outputs did not reproduce the complete trajectory and state"
        except ReplayMismatch as exc:
            replay_equal = False
            replay_error = str(exc)

    parse_modes = Counter(
        call.get("parse_mode")
        for call in (*cognition.calls, *renderer.calls)
        if call.get("parse_mode")
    )
    return {
        "condition": name,
        "factors": {
            "identity_context": condition["identity_context"],
            "typed_prehistory": condition["typed_prehistory"],
        },
        "replicate": replicate,
        "baseline_sha256": baseline_sha256,
        "engine_capacity": engine_capacity,
        "history_import": history_report,
        "turns": turns,
        "cognition_calls": cognition.calls,
        "speech_calls": renderer.calls,
        "diagnostics": {
            "cognition_call_count": len(cognition.calls),
            "speech_call_count": len(renderer.calls),
            "provider_error_count": sum(
                bool(call.get("error_type"))
                for call in (*cognition.calls, *renderer.calls)
            ),
            "parse_modes": dict(parse_modes),
            "historical_retrieval_count": sum(
                len(turn["historical_retrievals"])
                for turn in turns
            ),
        },
        "clean": clean,
        "replay_equal": replay_equal,
        "replay_error": replay_error,
        "replay_diagnostics": replay_diagnostics,
        "final_state_sha256": _digest(final_snapshot),
    }


def evaluate(
    *,
    dry_run: bool,
    replicates: int = DEFAULT_REPLICATES,
    endpoint: str | None = None,
    model: str | None = None,
    model_fingerprint: str | None = None,
    api_key: str = "",
) -> dict:
    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    trials = []
    with tempfile.TemporaryDirectory() as folder:
        directory = Path(folder)
        for replicate in range(replicates):
            for condition in CONDITIONS:
                trials.append(_trial(
                    directory,
                    cartridge,
                    condition,
                    replicate,
                    dry_run=dry_run,
                    endpoint=endpoint,
                    model=model,
                    api_key=api_key,
                ))

    paired_baselines_match = True
    for replicate in range(replicates):
        rows = [trial for trial in trials if trial["replicate"] == replicate]
        for typed_prehistory in (False, True):
            hashes = {
                trial["baseline_sha256"]
                for trial in rows
                if trial["factors"]["typed_prehistory"] is typed_prehistory
            }
            paired_baselines_match &= len(hashes) == 1

    history_contract_pinned = all(
        (
            trial["history_import"] is None
            if not trial["factors"]["typed_prehistory"]
            else (
                trial["history_import"]["history_id"] == HISTORY_ID
                and trial["history_import"]["sha256"] == HISTORY_SHA256
                and trial["history_import"]["importer_version"] == HISTORY_IMPORTER_VERSION
                and trial["history_import"]["options"] == {"workspace_orientation": False}
                and trial["history_import"]["association_tag_policy"] == "semantic-only"
            )
        )
        for trial in trials
    )
    expected_probe_order = [probe["id"] for probe in PROBES]
    checks = {
        "four_conditions_fixed": {
            trial["condition"] for trial in trials
        } == {condition["name"] for condition in CONDITIONS},
        "paired_baselines_match": paired_baselines_match,
        "pretorius_capacity_contract": all(
            trial["engine_capacity"] == {
                "memory_limit": PRETORIUS_MEMORY_LIMIT,
                "association_limit": PRETORIUS_ASSOCIATION_LIMIT,
                "top_k": PRETORIUS_TOP_K,
            }
            for trial in trials
        ),
        "history_contract_pinned": history_contract_pinned,
        "prehistory_arms_have_no_workspace_orientation": all(
            trial["history_import"] is None
            or trial["history_import"]["orientation_count"] == 0
            for trial in trials
        ),
        "fixed_probe_order": all(
            [turn["probe"] for turn in trial["turns"]] == expected_probe_order
            for trial in trials
        ),
        "public_views_exclude_subject_id": all(
            "subject_id" not in call["view"]
            for trial in trials
            for call in trial["speech_calls"]
        ),
        "clean_trials_replay_exactly": all(
            not trial["clean"] or trial["replay_equal"] is True
            for trial in trials
        ),
        "provider_responses_observed": (
            dry_run
            or all(
                any(
                    call.get("raw_content") is not None
                    for call in (*trial["cognition_calls"], *trial["speech_calls"])
                )
                for trial in trials
            )
        ),
    }
    software_contract = _software_contract()
    environment_contract = _environment_contract()
    cartridge_contract = _cartridge_contract(cartridge)
    harness_valid = all(checks.values())
    evidence_eligible = bool(
        not dry_run
        and replicates >= DEFAULT_REPLICATES
        and model_fingerprint
        and software_contract["package_version"] == RELEASE_VERSION
        and harness_valid
    )
    return {
        "protocol": PROTOCOL,
        "study_design": {
            "factors": ["identity_context", "typed_prehistory"],
            "conditions": list(CONDITIONS),
            "probe_order": list(PROBES),
            "quiet_ticks_after_probe": QUIET_TICKS,
            "speaker": "Jay",
        },
        "software_contract": software_contract,
        "environment_contract": environment_contract,
        "cartridge_contract": cartridge_contract,
        "resource_contract": {
            "memory_limit": PRETORIUS_MEMORY_LIMIT,
            "association_limit": PRETORIUS_ASSOCIATION_LIMIT,
            "top_k": PRETORIUS_TOP_K,
        },
        "history_contract": {
            "history_id": HISTORY_ID,
            "sha256": HISTORY_SHA256,
            "importer_version": HISTORY_IMPORTER_VERSION,
            "workspace_orientation": False,
            "association_tag_policy": "semantic-only",
        },
        "model_contract": {
            "kind": "template-control" if dry_run else "openai-compatible",
            "model": None if dry_run else model,
            "model_fingerprint": None if dry_run else model_fingerprint,
            "same_model_for_private_and_public_language": True,
        },
        "prompt_contracts": {
            "private_without_identity": {
                "version": COGNITIVE_PROMPT_VERSION,
                "temperature": DEFAULT_TEMPERATURE,
                "max_tokens": DEFAULT_MAX_TOKENS,
            },
            "private_with_identity": {
                "version": IDENTITY_COGNITIVE_PROMPT_VERSION,
                "temperature": DEFAULT_TEMPERATURE,
                "max_tokens": DEFAULT_MAX_TOKENS,
            },
            "public": {
                "version": SPEECH_PROMPT_VERSION,
                "temperature": DEFAULT_SPEECH_TEMPERATURE,
                "max_tokens": DEFAULT_SPEECH_MAX_TOKENS,
            },
            "response_parser": {
                "version": MODEL_RESPONSE_PARSER_VERSION,
                "accepted_wrappers": ["json", "fenced_json"],
                "semantic_repair": False,
            },
        },
        "replicates": replicates,
        "trials": trials,
        "checks": checks,
        "harness_valid": harness_valid,
        "evidence_eligible": evidence_eligible,
        "interpretation": (
            "This harness tests utilization of a pinned provenance-rich seeded prehistory "
            "under matched model and organism conditions. The artifact mixes static canon, "
            "reconstructed autobiography, phenotype evidence, and longitudinal records, so "
            "V1 cannot attribute an effect specifically to lived interaction. It does not "
            "establish human likeness, consciousness, or acquired long-horizon path dependence."
        ),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run the frozen Pretorius live-study protocol"
    )
    parser.add_argument("--endpoint", help="OpenAI-compatible API base URL including /v1")
    parser.add_argument("--model", help="Model name for the configured endpoint")
    parser.add_argument(
        "--model-fingerprint",
        help="Immutable model digest or build identifier required for evidence eligibility",
    )
    parser.add_argument("--replicates", type=int, default=DEFAULT_REPLICATES)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if not 1 <= args.replicates <= 10:
        parser.error("--replicates must be between 1 and 10")
    if args.dry_run:
        if args.endpoint or args.model or args.model_fingerprint:
            parser.error("--dry-run cannot be combined with model configuration")
    elif not args.endpoint or not args.model:
        parser.error("--endpoint and --model are required unless --dry-run is used")

    report = evaluate(
        dry_run=args.dry_run,
        replicates=args.replicates,
        endpoint=args.endpoint,
        model=args.model,
        model_fingerprint=args.model_fingerprint,
        api_key=os.environ.get("JELLY_API_KEY", ""),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    summary = {
        "protocol": report["protocol"],
        "trial_count": len(report["trials"]),
        "checks": report["checks"],
        "harness_valid": report["harness_valid"],
        "evidence_eligible": report["evidence_eligible"],
    }
    print(json.dumps(summary, indent=2))
    raise SystemExit(0 if report["harness_valid"] else 1)


if __name__ == "__main__":
    main()
