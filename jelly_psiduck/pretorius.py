"""Dedicated history-rich Pretorius entry point built on v0.2 endogenous cognition."""
from __future__ import annotations

import argparse
import json
import os
import threading
from pathlib import Path

from digital_subject.cartridge import load_cartridge

from .cognition import OpenAICompatibleCognition
from .endogenous import EndogenousOrganism, EndogenousSubject
from .firewall import remembered
from .history import seed_history
from .speech import OpenAICompatibleSpeechRenderer


ROOT = Path(__file__).resolve().parent
DEFAULT_CARTRIDGE = ROOT / "cartridges" / "pretorius.toml"
DEFAULT_HISTORY = ROOT / "histories" / "pretorius_v2.json"
PRETORIUS_MEMORY_LIMIT = 512
PRETORIUS_ASSOCIATION_LIMIT = 2048
PRETORIUS_TOP_K = 4

_HISTORY_PROJECTIONS = {
    "screen_canon": "The screen canon records this about my earlier story:",
    "expanded_autobiography": "My reconstructed autobiography says:",
    "foundational_self_memory": "A foundational self-memory returns:",
    "legacy_awareness": "A later cultural record tells me:",
    "archive_self_report": "An archived self-report attributed to me says:",
    "phenotype_evidence": "A phenotype record suggests this recurring pattern:",
    "lived_project_history": "I remember this from my recent reconstruction work:",
    "relationship_history": "I remember this relationship episode:",
    "research_history": "I remember this from research in which I participated:",
}


def _project_history_memory(memory) -> str:
    if not memory.kind.startswith("history:"):
        return remembered(memory)
    evidence_class = memory.kind.split(":", 1)[1]
    lead = _HISTORY_PROJECTIONS.get(evidence_class, "A provenance-marked record returns to mind:")
    detail = f"{memory.summary} {memory.meaning}".strip()
    if memory.strength < 0.2:
        return f"{lead} The details are too weak for me to recover confidently."
    if memory.strength < 0.5:
        return f"{lead} I recover it only vaguely: {detail}"
    return f"{lead} {detail}"


class PretoriusOrganism(EndogenousOrganism):
    """History-rich capacity without changing the frozen generic v0.2 organism."""

    def __init__(
        self,
        state,
        cartridge,
        *,
        memory_limit: int = PRETORIUS_MEMORY_LIMIT,
        association_limit: int = PRETORIUS_ASSOCIATION_LIMIT,
        top_k: int = PRETORIUS_TOP_K,
    ):
        super().__init__(
            state,
            cartridge,
            memory_limit=memory_limit,
            association_limit=association_limit,
            top_k=top_k,
        )


class PretoriusSubject(EndogenousSubject):
    """Pretorius-only persistence envelope around the frozen v0.2 organism."""

    SCHEMA = 4
    ENGINE_TYPE = PretoriusOrganism

    def __init__(self, *args, **kwargs):
        self.history_imports = {}
        super().__init__(*args, **kwargs)

    def _payload(self):
        return {**super()._payload(), "history_imports": self.history_imports}

    def _restore(self, raw):
        super()._restore(raw)
        self.history_imports = dict(raw.get("history_imports", {}))

    def _remember(self, memory):
        return _project_history_memory(memory)

    def _public_memory(self, memory):
        return _project_history_memory(memory)


def open_pretorius(
    db: str | Path,
    *,
    cartridge_path: str | Path = DEFAULT_CARTRIDGE,
    history_path: str | Path = DEFAULT_HISTORY,
    endpoint: str | None = None,
    model: str | None = None,
    api_key: str = "",
    model_speech: bool = True,
):
    cartridge = load_cartridge(cartridge_path)
    cognition = None
    renderer = None
    if endpoint and model:
        cognition = OpenAICompatibleCognition(endpoint, model, api_key, identity=cartridge.identity)
        if model_speech:
            renderer = OpenAICompatibleSpeechRenderer(endpoint, model, api_key)
    host = PretoriusSubject(
        db,
        cartridge,
        cognition=cognition,
        renderer=renderer,
        subject_id="pretorius-001",
    )
    report = seed_history(host, history_path)
    return host, report


def _print_turn(result):
    if result.get("speech"):
        print(result["speech"], flush=True)
    else:
        print("[silent]", flush=True)


def main():
    parser = argparse.ArgumentParser(
        description="Pretorius on Jelly-Psiduck v0.2 with seeded longitudinal history"
    )
    parser.add_argument("--db", type=Path, default=Path("pretorius-jelly.sqlite3"))
    parser.add_argument("--cartridge", type=Path, default=DEFAULT_CARTRIDGE)
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    parser.add_argument("--endpoint", help="OpenAI-compatible API base URL including /v1")
    parser.add_argument("--model", help="Model name; required with --endpoint")
    parser.add_argument("--speaker", default="Jay")
    parser.add_argument(
        "--template-speech",
        action="store_true",
        help="Use the model for private cognition but retain deterministic cartridge speech",
    )

    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    commands.add_parser("status")
    tick = commands.add_parser("tick")
    tick.add_argument("count", nargs="?", type=int, default=1)
    say = commands.add_parser("say")
    say.add_argument("text")
    commands.add_parser("chat")
    run = commands.add_parser("run")
    run.add_argument("--interval", type=float, default=5.0)
    args = parser.parse_args()

    if bool(args.endpoint) != bool(args.model):
        parser.error("--endpoint and --model must be supplied together")
    if args.command == "tick" and not 1 <= args.count <= 10000:
        parser.error("count must be between 1 and 10000")

    host, report = open_pretorius(
        args.db,
        cartridge_path=args.cartridge,
        history_path=args.history,
        endpoint=args.endpoint,
        model=args.model,
        api_key=os.environ.get("JELLY_API_KEY", ""),
        model_speech=not args.template_speech,
    )

    if args.command == "init":
        print(json.dumps({"db": str(args.db), "history": report}, indent=2))
    elif args.command == "status":
        print(json.dumps(host.inspect(), indent=2))
    elif args.command == "tick":
        for _ in range(args.count):
            print(json.dumps(host.heartbeat()))
    elif args.command == "say":
        host.message(args.speaker, args.text)
        _print_turn(host.heartbeat())
    elif args.command == "chat":
        print("Pretorius is active. Use /quit to end the foreground session.")
        while True:
            try:
                text = input(f"{args.speaker}> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not text:
                continue
            if text.casefold() in {"/quit", "/exit"}:
                break
            host.message(args.speaker, text)
            _print_turn(host.heartbeat())
    elif args.command == "run":
        print("Pretorius heartbeat running. Ctrl+C stops the foreground process.")
        try:
            host.run(
                threading.Event(),
                tick_seconds=args.interval,
                on_result=lambda result: _print_turn(result) if result.get("speech") else None,
            )
        except KeyboardInterrupt:
            print("Stopped; the last completed heartbeat remains persisted.")


if __name__ == "__main__":
    main()
