"""Local foreground host. Inspector output is explicitly distinct from speech."""
import argparse
import json
import os
import threading
from pathlib import Path

from digital_subject.cartridge import load_cartridge
from digital_subject.models import Event
from .cognition import OpenAICompatibleCognition
from .runtime import UnifiedSubject


DEFAULT_CARTRIDGE = Path(__file__).parent / "cartridges" / "seed_subject.toml"


def main():
    parser = argparse.ArgumentParser(description="Jelly-Psiduck: one continuing subjective organism")
    parser.add_argument("--db", type=Path, default=Path("jelly-subject.sqlite3"))
    parser.add_argument("--cartridge", type=Path, default=DEFAULT_CARTRIDGE)
    parser.add_argument("--endpoint", help="Optional OpenAI-compatible API base URL (including /v1)")
    parser.add_argument("--model", help="Model name; required with --endpoint")
    parser.add_argument("--architecture", choices=("v01", "v02", "v03"), default="v01",
                        help="v02/v03 are opt-in experiments and require separate subject stores")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    commands.add_parser("status", help="Read-only engine telemetry and private experience inspector")
    tick = commands.add_parser("tick")
    tick.add_argument("count", type=int, nargs="?", default=1)
    run = commands.add_parser("run", help="Live heartbeat until Ctrl+C")
    run.add_argument("--interval", type=float, default=5)
    message = commands.add_parser("message", help="Queue a percept for the next heartbeat")
    message.add_argument("speaker")
    message.add_argument("text")
    demo = commands.add_parser("demo", help="Seed a host-authored return expectation and run six ticks")
    demo.add_argument("--person", default="visitor")
    args = parser.parse_args()
    if bool(args.endpoint) != bool(args.model):
        parser.error("--endpoint and --model must be supplied together")
    if args.command == "tick" and not 1 <= args.count <= 10000:
        parser.error("count must be between 1 and 10000")
    provider = OpenAICompatibleCognition(args.endpoint, args.model, os.environ.get("JELLY_API_KEY", "")) if args.endpoint else None
    if args.architecture == "v03":
        from .v03 import ReverieSubject
        runtime_type = ReverieSubject
    elif args.architecture == "v02":
        from .endogenous import EndogenousSubject
        runtime_type = EndogenousSubject
    else:
        runtime_type = UnifiedSubject
    host = runtime_type(args.db, load_cartridge(args.cartridge), cognition=provider)
    if args.command == "status":
        print(json.dumps(host.inspect(), indent=2))
    elif args.command == "init":
        print(f"Subject ready in {args.db}")
    elif args.command == "message":
        host.message(args.speaker, args.text)
        print("Message queued as a social percept.")
    elif args.command == "tick":
        for _ in range(args.count):
            print(json.dumps(host.heartbeat()))
    elif args.command == "demo":
        tick = host.inspect()["engine"]["tick"]
        person = args.person
        host.enqueue(Event("promise", person, f"{person} said they would return soon.",
            tags=(person, "promise"), metadata={"commitment": {
                "actor": person, "description": f"{person} said they would return soon.",
                "due_tick": tick + 2, "importance": 0.9}}))
        for _ in range(6):
            print(json.dumps(host.heartbeat()))
        print("Inspect the persisted private trace with status.")
    elif args.command == "run":
        print("Heartbeat running. Queue messages from another terminal; Ctrl+C stops the host.")
        def display(result):
            if result["speech"]:
                print(result["speech"], flush=True)
        try:
            host.run(threading.Event(), tick_seconds=args.interval, on_result=display)
        except KeyboardInterrupt:
            print("Stopped; the last completed heartbeat remains persisted.")


if __name__ == "__main__":
    main()
