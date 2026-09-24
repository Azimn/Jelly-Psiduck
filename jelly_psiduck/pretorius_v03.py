"""Pretorius v0.3 alpha: historical continuity and self-consolidation substrate.

The v0.2 Pretorius release candidate remains frozen in jelly_psiduck.pretorius.
This module introduces schema 5 without silently opening or rewriting schema-4
stores. v0.3.0a1 adds the append-only lived-event ledger, active/archive memory
split, deterministic consolidation, and persistence scaffolding for later v0.3
milestones.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import threading
from pathlib import Path
from typing import Any

from digital_subject.cartridge import load_cartridge
from digital_subject.models import Consequence

from .autobiography import AutobiographyLedger, LIVED_PROVENANCE
from .cognition import OpenAICompatibleCognition
from .consolidation import make_archive_record, plan_consolidation
from .history import load_history, seed_history
from .pretorius import (
    DEFAULT_CARTRIDGE,
    DEFAULT_HISTORY,
    PretoriusOrganism,
    PretoriusSubject,
)
from .speech import OpenAICompatibleSpeechRenderer


SCHEMA5 = 5
V03_RELEASE = "0.3.0a1"

_REQUIRED_SCHEMA5_FIELDS = (
    "autobiography_meta",
    "autobiographical_events",
    "active_memory_index",
    "archive_records",
    "retrieval_traces",
    "learned_associations",
    "tensions",
    "self_model_versions",
    "reflection_proposals",
    "relationship_episodes",
    "prospective_items",
    "diary_entries",
    "scheduler_state",
    "consolidation_journal",
)


def schema5_extension(subject_id: str, active_memory_ids=()) -> dict[str, Any]:
    """Return the explicit schema-5 extension used by fresh stores and migration."""
    ledger = AutobiographyLedger(subject_id)
    ledger_state = ledger.to_state()
    events = ledger_state.pop("events")
    return {
        "autobiography_meta": ledger_state,
        "autobiographical_events": events,
        "active_memory_index": list(active_memory_ids),
        "archive_records": {},
        "retrieval_traces": [],
        "learned_associations": [],
        "tensions": {},
        "self_model_versions": {},
        "reflection_proposals": [],
        "relationship_episodes": [],
        "prospective_items": [],
        "diary_entries": [],
        "scheduler_state": {"schema": 1, "last_decision_tick": None},
        "consolidation_journal": [],
        "consolidation_cycle": 0,
        "protected_memory_ids": [],
        "migration_manifest": None,
        "derived_fields": {
            "active_memory_index": "ordered engine.memories ids; persisted audit cache and rebuildable",
        },
    }


class PretoriusV03Organism(PretoriusOrganism):
    """Pretorius engine variant that never destroys overflow inside _store_memory.

    Schema-5 subject orchestration performs the deterministic archive pass before
    the enclosing subject transaction commits.
    """

    def _store_memory(self, memory):
        if not memory.kind.startswith("history:"):
            self._memory_sequence += 1
            memory.id = f"{self._dynamic_memory_prefix()}{self._memory_sequence:08d}"
        self.state.memories.append(memory)


class PretoriusV03Subject(PretoriusSubject):
    """Schema-5 Pretorius subject with append-only lived history and archive."""

    SCHEMA = SCHEMA5
    ENGINE_TYPE = PretoriusV03Organism

    def __init__(self, *args, **kwargs):
        subject_id = str(kwargs.get("subject_id", "pretorius-001"))
        extension = schema5_extension(subject_id)
        self.autobiography = AutobiographyLedger(subject_id)
        self.archive_records = extension["archive_records"]
        self.retrieval_traces = extension["retrieval_traces"]
        self.learned_associations = extension["learned_associations"]
        self.tensions = extension["tensions"]
        self.self_model_versions = extension["self_model_versions"]
        self.reflection_proposals = extension["reflection_proposals"]
        self.relationship_episodes = extension["relationship_episodes"]
        self.prospective_items = extension["prospective_items"]
        self.diary_entries = extension["diary_entries"]
        self.scheduler_state = extension["scheduler_state"]
        self.consolidation_journal = extension["consolidation_journal"]
        self.consolidation_cycle = extension["consolidation_cycle"]
        self.protected_memory_ids = set(extension["protected_memory_ids"])
        self.migration_manifest = extension["migration_manifest"]
        self.derived_fields = extension["derived_fields"]
        super().__init__(*args, **kwargs)

    def _payload(self):
        raw = super()._payload()
        ledger = self.autobiography.to_state()
        events = ledger.pop("events")
        return {
            **raw,
            "autobiography_meta": ledger,
            "autobiographical_events": events,
            "active_memory_index": [memory.id for memory in self.engine.state.memories],
            "archive_records": self.archive_records,
            "retrieval_traces": self.retrieval_traces,
            "learned_associations": self.learned_associations,
            "tensions": self.tensions,
            "self_model_versions": self.self_model_versions,
            "reflection_proposals": self.reflection_proposals,
            "relationship_episodes": self.relationship_episodes,
            "prospective_items": self.prospective_items,
            "diary_entries": self.diary_entries,
            "scheduler_state": self.scheduler_state,
            "consolidation_journal": self.consolidation_journal,
            "consolidation_cycle": self.consolidation_cycle,
            "protected_memory_ids": sorted(self.protected_memory_ids),
            "migration_manifest": self.migration_manifest,
            "derived_fields": self.derived_fields,
        }

    def _restore(self, raw):
        missing = [key for key in _REQUIRED_SCHEMA5_FIELDS if key not in raw]
        if missing:
            raise ValueError(
                "schema-5 store is incomplete; explicit migration or a fresh store is required"
            )
        super()._restore(raw)
        ledger_state = {
            **dict(raw.get("autobiography_meta", {})),
            "events": list(raw["autobiographical_events"]),
        }
        self.autobiography = AutobiographyLedger.from_state(ledger_state)
        self.archive_records = dict(raw["archive_records"])
        self.retrieval_traces = list(raw["retrieval_traces"])
        self.learned_associations = list(raw["learned_associations"])
        self.tensions = dict(raw["tensions"])
        self.self_model_versions = dict(raw["self_model_versions"])
        self.reflection_proposals = list(raw["reflection_proposals"])
        self.relationship_episodes = list(raw["relationship_episodes"])
        self.prospective_items = list(raw["prospective_items"])
        self.diary_entries = list(raw["diary_entries"])
        self.scheduler_state = dict(raw["scheduler_state"])
        self.consolidation_journal = list(raw["consolidation_journal"])
        self.consolidation_cycle = int(raw.get("consolidation_cycle", 0))
        self.protected_memory_ids = set(raw.get("protected_memory_ids", ()))
        self.migration_manifest = raw.get("migration_manifest")
        self.derived_fields = dict(raw.get("derived_fields", {}))

        active_ids = [memory.id for memory in self.engine.state.memories]
        if list(raw["active_memory_index"]) != active_ids:
            raise ValueError("active memory index does not match persisted engine memories")
        overlap = set(active_ids).intersection(self.archive_records)
        if overlap:
            raise ValueError("a memory cannot be both active and archived")
        for memory_id, record in self.archive_records.items():
            if record.get("memory_id") != memory_id:
                raise ValueError("archive record key does not match memory id")

    def _new_workspace_records(self, prior_sequence: int):
        records = []
        for record in self.workspace.records:
            try:
                sequence = int(record.id.rsplit("-", 1)[1])
            except (IndexError, ValueError):
                continue
            if sequence > prior_sequence:
                records.append(record)
        return records

    def _affect_snapshot(self) -> dict[str, float]:
        return {
            key: float(value)
            for key, value in sorted(self.engine.state.pressures.items())
            if math.isfinite(float(value))
        }

    def _append_processed_events(
        self,
        raw_events: list[dict[str, Any]],
        *,
        prior_workspace_sequence: int,
        prior_memory_ids: set[str],
    ) -> None:
        if not raw_events:
            return
        new_records = self._new_workspace_records(prior_workspace_sequence)
        perceived = [
            record for record in new_records
            if record.source in {"social", "perception"}
        ]
        new_episodes = [
            memory
            for memory in self.engine.state.memories
            if (
                memory.id not in prior_memory_ids
                and memory.kind == "episode"
                and memory.created_tick == self.engine.state.tick
            )
        ]
        for index, raw in enumerate(raw_events):
            source = str(raw["source"])
            event_type = str(raw["kind"])
            description = str(raw["description"])
            subjective = (
                perceived[index].first_person
                if index < len(perceived)
                else self.engine.state.current_experience
            )
            objective = (
                f"{source} said: {description}"
                if event_type == "message"
                else description
            )
            participants = ()
            if source not in {"world", "environment", "system", "self"}:
                participants = (source,)
            metadata = raw.get("metadata") or {}
            person_id = str(metadata.get("person_id", "")).strip()
            if person_id and person_id not in participants:
                participants = (*participants, person_id)
            memory_links = ()
            if index < len(new_episodes):
                memory_links = (new_episodes[index].id,)
            self.autobiography.append(
                tick=self.engine.state.tick,
                source=source,
                event_type=event_type,
                objective_record=objective,
                subjective_record=subjective,
                provenance=LIVED_PROVENANCE,
                participants=participants,
                tags=tuple(raw.get("tags", ())),
                affect_snapshot=self._affect_snapshot(),
                relationship_links=tuple(
                    person for person in participants
                    if person in self.engine.state.relationships
                ),
                memory_links=memory_links,
            )

    def _superseded_memory_map(self) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for event in self.autobiography.events:
            if not event.supersedes_interpretation or not event.memory_links:
                continue
            earlier = self.autobiography.get(event.supersedes_interpretation)
            if earlier is None or not earlier.memory_links:
                continue
            replacement = event.memory_links[0]
            for memory_id in earlier.memory_links:
                mapping[memory_id] = replacement
        return mapping

    def _protected_ids(self) -> set[str]:
        protected = set(self.protected_memory_ids)
        for claim in self.engine.state.narrative.values():
            protected.update(claim.evidence_memory_ids)
        for record in self.workspace.records[-16:]:
            if record.concern_links or record.expectation_links:
                protected.update(record.memory_links)
        return protected

    def _source_event_ids(self, memory_id: str) -> tuple[str, ...]:
        return tuple(
            event.id
            for event in self.autobiography.events
            if memory_id in event.memory_links
        )

    def _run_consolidation(self, *, force: bool = False) -> dict[str, Any] | None:
        memories = list(self.engine.state.memories)
        actions = plan_consolidation(
            memories,
            budget=self.engine.memory_limit,
            tick=self.engine.state.tick,
            protected_ids=self._protected_ids(),
            superseded_by=self._superseded_memory_map(),
        )
        if not actions and not force:
            return None

        self.consolidation_cycle += 1
        active_before = len(memories)
        by_id = {memory.id: memory for memory in memories}
        archived_ids: set[str] = set()
        serialized_actions = []
        for action in actions:
            serialized_actions.append(action.to_dict())
            if action.action != "archive" or action.memory_id is None:
                continue
            memory = by_id.get(action.memory_id)
            if memory is None or memory.id in self.archive_records:
                continue
            archive = make_archive_record(
                memory,
                action,
                tick=self.engine.state.tick,
                cycle=self.consolidation_cycle,
                source_event_ids=self._source_event_ids(memory.id),
            )
            self.archive_records[memory.id] = archive.to_dict()
            archived_ids.add(memory.id)

        if archived_ids:
            self.engine.state.memories = [
                memory
                for memory in self.engine.state.memories
                if memory.id not in archived_ids
            ]

        report = {
            "cycle": self.consolidation_cycle,
            "tick": self.engine.state.tick,
            "active_before": active_before,
            "active_after": len(self.engine.state.memories),
            "archive_count": len(self.archive_records),
            "actions": serialized_actions,
        }
        self.consolidation_journal.append(report)
        return report

    def _tick(self):
        raw_events = [dict(item) for item in self.pending[:8]]
        prior_workspace_sequence = self.workspace.sequence
        prior_memory_ids = {memory.id for memory in self.engine.state.memories}
        result = super()._tick()
        self._append_processed_events(
            raw_events,
            prior_workspace_sequence=prior_workspace_sequence,
            prior_memory_ids=prior_memory_ids,
        )
        self._run_consolidation()
        return result

    def consequence(self, consequence: Consequence):
        """Persist an experienced action consequence and archive in one transaction."""
        with self._transaction():
            prior_memory_ids = {memory.id for memory in self.engine.state.memories}
            self.engine.apply_consequence(consequence)
            self.continuity.advance_deadlines(self.engine.state.tick)
            subjective = self.engine._consequence_meaning(consequence)
            item = self._add(
                "action_consequence",
                subjective,
                concepts=consequence.tags,
            )
            new_episodes = [
                memory for memory in self.engine.state.memories
                if memory.id not in prior_memory_ids and memory.kind == "episode"
            ]
            memory_links = (new_episodes[0].id,) if new_episodes else ()
            consequence_id = (
                f"{self.engine.state.subject_id}:consequence:"
                f"{self.engine.state.tick:08d}:{consequence.action.value}"
            )
            self.autobiography.append(
                tick=self.engine.state.tick,
                source="system",
                event_type="action_consequence",
                objective_record=consequence.description,
                subjective_record=item.first_person,
                provenance=LIVED_PROVENANCE,
                tags=consequence.tags,
                affect_snapshot=self._affect_snapshot(),
                consequence_links=(consequence_id,),
                memory_links=memory_links,
            )
            self._run_consolidation()

    def record_interpretation_correction(
        self,
        *,
        source: str,
        objective_record: str,
        subjective_record: str,
        supersedes_event_id: str,
        memory_links=(),
        tags=("correction",),
    ) -> dict[str, Any]:
        """Trusted host API for a correction, never a model-side memory write."""
        with self._transaction():
            event = self.autobiography.append(
                tick=self.engine.state.tick,
                source=source,
                event_type="correction",
                objective_record=objective_record,
                subjective_record=subjective_record,
                provenance=LIVED_PROVENANCE,
                participants=(source,),
                tags=tags,
                affect_snapshot=self._affect_snapshot(),
                memory_links=memory_links,
                supersedes_interpretation=supersedes_event_id,
            )
            self._run_consolidation()
            return event.to_dict()

    def consolidate(self) -> dict[str, Any]:
        with self._transaction():
            report = self._run_consolidation(force=True)
            return dict(report)

    def archive_lookup(self, memory_id: str) -> dict[str, Any] | None:
        snapshot = self.inspect()
        record = snapshot["archive_records"].get(str(memory_id))
        return None if record is None else dict(record)


def open_pretorius_v03(
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
        cognition = OpenAICompatibleCognition(
            endpoint,
            model,
            api_key,
            identity=cartridge.identity,
        )
        if model_speech:
            renderer = OpenAICompatibleSpeechRenderer(endpoint, model, api_key)
    host = PretoriusV03Subject(
        db,
        cartridge,
        cognition=cognition,
        renderer=renderer,
        subject_id="pretorius-001",
    )

    history_raw, history_digest = load_history(history_path)
    history_id = str(history_raw["history_id"])
    if host.history_imports:
        existing = host.history_imports.get(history_id)
        if existing is None or existing.get("sha256") != history_digest:
            raise ValueError("existing schema-5 subject is pinned to a different history artifact")
        report = {**existing, "already_present": True}
    else:
        report = seed_history(host, history_path)
    return host, report


def _print_turn(result):
    print(result.get("speech") or "[silent]", flush=True)


def main():
    parser = argparse.ArgumentParser(
        description="Pretorius v0.3 alpha historical continuity runtime"
    )
    parser.add_argument("--db", type=Path, default=Path("pretorius-v03.sqlite3"))
    parser.add_argument("--cartridge", type=Path, default=DEFAULT_CARTRIDGE)
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    parser.add_argument("--endpoint", help="OpenAI-compatible API base URL including /v1")
    parser.add_argument("--model", help="Model name; required with --endpoint")
    parser.add_argument("--speaker", default="Jay")
    parser.add_argument(
        "--template-speech",
        action="store_true",
        help="Use model private cognition with deterministic cartridge speech",
    )

    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    commands.add_parser("status")
    commands.add_parser("consolidate")
    archive = commands.add_parser("archive")
    archive.add_argument("memory_id")
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

    host, report = open_pretorius_v03(
        args.db,
        cartridge_path=args.cartridge,
        history_path=args.history,
        endpoint=args.endpoint,
        model=args.model,
        api_key=os.environ.get("JELLY_API_KEY", ""),
        model_speech=not args.template_speech,
    )

    if args.command == "init":
        print(json.dumps({
            "db": str(args.db),
            "version": V03_RELEASE,
            "schema": SCHEMA5,
            "history": report,
        }, indent=2))
    elif args.command == "status":
        print(json.dumps(host.inspect(), indent=2))
    elif args.command == "consolidate":
        print(json.dumps(host.consolidate(), indent=2))
    elif args.command == "archive":
        print(json.dumps(host.archive_lookup(args.memory_id), indent=2))
    elif args.command == "tick":
        for _ in range(args.count):
            print(json.dumps(host.heartbeat()))
    elif args.command == "say":
        host.message(args.speaker, args.text)
        _print_turn(host.heartbeat())
    elif args.command == "chat":
        print("Pretorius v0.3 alpha is active. Use /quit to end the foreground session.")
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
        print("Pretorius v0.3 heartbeat running. Ctrl+C stops the foreground process.")
        try:
            host.run(
                threading.Event(),
                tick_seconds=args.interval,
                on_result=lambda result: _print_turn(result)
                if result.get("speech")
                else None,
            )
        except KeyboardInterrupt:
            print("Stopped; the last completed heartbeat remains persisted.")


if __name__ == "__main__":
    main()
