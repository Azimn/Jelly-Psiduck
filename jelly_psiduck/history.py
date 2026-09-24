"""Deterministic import of typed prehistory into a fresh persistent subject.

A history file is not replayed as current perception. It initializes durable memory,
relationships, self-model evidence, and unresolved concerns while preserving an audit
record of exactly which artifact, importer, and orientation policy produced the state.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from digital_subject.models import Belief, Concern, Memory, NarrativeClaim, Relationship

from .firewall import remembered


HISTORY_SCHEMA = 1
HISTORY_IMPORTER_VERSION = "typed-prehistory-v2"


def _clamp(value: Any, *, signed: bool = False) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("history numeric values must be finite")
    return max(-1.0 if signed else 0.0, min(1.0, number))


def _records(raw: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = raw.get(key, [])
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ValueError(f"{key} must be a list of mappings")
    return value


def _unique_key(records: list[dict[str, Any]], field: str, label: str) -> None:
    seen: set[str] = set()
    for item in records:
        value = str(item.get(field, "")).strip()
        if not value or value in seen:
            raise ValueError(f"{label} {field} values must be unique and nonempty")
        seen.add(value)


def load_history(path: str | Path) -> tuple[dict[str, Any], str]:
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or int(raw.get("schema", 0)) != HISTORY_SCHEMA:
        raise ValueError("unsupported history schema")
    if not str(raw.get("history_id", "")).strip():
        raise ValueError("history_id is required")
    _records(raw, "memories")
    canonical = json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return raw, hashlib.sha256(canonical).hexdigest()


def _memory_id(history_id: str, record_id: str) -> str:
    return f"{history_id}:{record_id}"


def seed_history(
    subject,
    path: str | Path,
    *,
    workspace_orientation: bool = True,
) -> dict[str, Any]:
    """Import typed prehistory once. A changed transform requires a new subject store."""
    if not hasattr(subject, "history_imports"):
        raise TypeError("subject must provide persistent history_imports metadata")
    raw, digest = load_history(path)
    history_id = str(raw["history_id"])
    path = Path(path)
    options = {"workspace_orientation": bool(workspace_orientation)}

    with subject._transaction():
        prior = subject.history_imports.get(history_id)
        if prior:
            if prior.get("sha256") != digest:
                raise ValueError("history artifact changed after import; use a new subject store")
            if prior.get("importer_version") != HISTORY_IMPORTER_VERSION:
                raise ValueError("history importer changed after import; use a new subject store")
            if prior.get("options") != options:
                raise ValueError("history import options changed; use a new subject store")
            return {**prior, "already_present": True}

        if (
            subject.engine.state.tick != 0
            or subject.pending
            or subject.continuity.state.epistemic_records
            or any(r.source != "memory" or r.generated_by != "cartridge" for r in subject.workspace.records)
        ):
            raise ValueError("history import requires a fresh subject before lived events")

        expected_subject = str(raw.get("subject", "")).strip()
        if expected_subject and expected_subject != subject.cartridge.display_name:
            raise ValueError("history subject does not match cartridge display name")

        state = subject.engine.state
        pressure_state = raw.get("state", {}).get("pressures", {})
        if not isinstance(pressure_state, dict):
            raise ValueError("state.pressures must be a mapping")
        for key, value in pressure_state.items():
            if key not in state.pressures:
                raise ValueError(f"unknown pressure in history: {key}")
            state.pressures[key] = _clamp(value)

        relationships = _records(raw, "relationships")
        _unique_key(relationships, "person_id", "relationship")
        for item in relationships:
            person_id = str(item["person_id"]).strip()
            values = dict(item.get("state", {}))
            allowed = {
                "trust", "comfort", "respect", "interest", "attachment", "affection",
                "safety", "familiarity", "obligation", "uncertainty",
            }
            unknown = set(values) - allowed
            if unknown:
                raise ValueError(f"unsupported relationship field: {sorted(unknown)[0]}")
            clean = {key: _clamp(value) for key, value in values.items()}
            age = max(0, int(item.get("last_contact_age_ticks", 0)))
            state.relationships[person_id] = Relationship(
                person_id,
                **clean,
                last_contact_tick=state.tick - age,
            )

        memory_records = _records(raw, "memories")
        _unique_key(memory_records, "id", "history memory")
        imported_memories: dict[str, Memory] = {}
        for item in memory_records:
            record_id = str(item["id"]).strip()
            evidence_class = str(item.get("evidence_class", "")).strip()
            if not evidence_class:
                raise ValueError(f"history memory {record_id} requires evidence_class")
            summary = str(item.get("summary", "")).strip()
            first_person = str(item.get("first_person", "")).strip()
            if not summary or not first_person:
                raise ValueError(f"history memory {record_id} requires summary and first_person")
            raw_tags = item.get("tags", [])
            if not isinstance(raw_tags, list):
                raise ValueError(f"history memory {record_id} tags must be a list")
            tags = tuple(dict.fromkeys(
                str(tag).strip() for tag in raw_tags if str(tag).strip()
            ))
            age = max(0, int(item.get("age_ticks", 0)))
            memory = Memory(
                id=_memory_id(history_id, record_id),
                summary=summary,
                meaning=first_person,
                tags=tags,
                strength=_clamp(item.get("strength", 0.7)),
                emotional_charge=_clamp(item.get("emotional_charge", 0.3)),
                created_tick=state.tick - age,
                last_recalled_tick=state.tick - age,
                kind=f"history:{evidence_class}",
            )
            subject.engine._store_memory(memory)
            subject.engine._update_associations(tags)
            imported_memories[record_id] = memory

        beliefs = _records(raw, "beliefs")
        _unique_key(beliefs, "key", "history belief")
        for item in beliefs:
            key = str(item["key"]).strip()
            proposition = str(item.get("proposition", "")).strip()
            if not proposition:
                raise ValueError("history beliefs require proposition")
            state.beliefs[key] = Belief(
                key,
                proposition,
                _clamp(item.get("confidence", 0.6)),
                _clamp(item.get("valence", 0.0), signed=True),
                state.tick - max(0, int(item.get("age_ticks", 0))),
            )

        claims = _records(raw, "narrative_claims")
        _unique_key(claims, "key", "history narrative claim")
        for item in claims:
            key = str(item["key"]).strip()
            proposition = str(item.get("proposition", "")).strip()
            if not proposition:
                raise ValueError("history narrative claims require proposition")
            evidence_ids = item.get("evidence", [])
            if not isinstance(evidence_ids, list):
                raise ValueError(f"history narrative claim {key} evidence must be a list")
            unknown = [str(record_id) for record_id in evidence_ids if str(record_id) not in imported_memories]
            if unknown:
                raise ValueError(f"history narrative claim {key} references unknown memory: {unknown[0]}")
            evidence = tuple(imported_memories[str(record_id)].id for record_id in evidence_ids)
            state.narrative[key] = NarrativeClaim(
                key,
                proposition,
                _clamp(item.get("confidence", 0.6)),
                _clamp(item.get("valence", 0.0), signed=True),
                evidence,
                state.tick - max(0, int(item.get("age_ticks", 0))),
            )

        open_loops = _records(raw, "open_loops")
        _unique_key(open_loops, "key", "history open loop")
        for item in open_loops:
            key = str(item["key"]).strip()
            description = str(item.get("description", "")).strip()
            if not description:
                raise ValueError("history open loops require description")
            state.concerns[key] = Concern(
                key,
                description,
                _clamp(item.get("urgency", 0.4)),
                _clamp(item.get("persistence", 0.985)),
                state.tick - max(0, int(item.get("age_ticks", 0))),
            )
            if description not in state.unresolved:
                state.unresolved.append(description)
        state.unresolved = state.unresolved[-24:]

        orientation_ids = raw.get("workspace_orientation", [])
        if not isinstance(orientation_ids, list):
            raise ValueError("workspace_orientation must be a list")
        normalized_orientation = [str(record_id) for record_id in orientation_ids]
        if len(normalized_orientation) != len(set(normalized_orientation)):
            raise ValueError("workspace_orientation ids must be unique")
        for record_id in normalized_orientation:
            if record_id not in imported_memories:
                raise ValueError(f"unknown workspace orientation memory: {record_id}")

        orientation = []
        if workspace_orientation:
            for record_id in normalized_orientation:
                memory = imported_memories[record_id]
                item = subject._add(
                    "memory",
                    subject._remember(memory) if hasattr(subject, "_remember") else remembered(memory),
                    memory_links=(memory.id,),
                    generated_by="history-import",
                )
                orientation.append(item.id)

        state.last_contact_tick = max(
            [state.last_contact_tick, *(r.last_contact_tick for r in state.relationships.values())]
        )
        report = {
            "history_id": history_id,
            "sha256": digest,
            "source_file": path.name,
            "importer_version": HISTORY_IMPORTER_VERSION,
            "options": options,
            "association_tag_policy": "semantic-only",
            "memory_count": len(imported_memories),
            "relationship_count": len(relationships),
            "belief_count": len(beliefs),
            "narrative_count": len(claims),
            "open_loop_count": len(open_loops),
            "orientation_count": len(orientation),
        }
        subject.history_imports[history_id] = report
        subject._trace({"kind": "history_import", **report})
        return {**report, "already_present": False}
