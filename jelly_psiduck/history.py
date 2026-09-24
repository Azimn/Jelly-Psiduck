"""Deterministic import of typed prehistory into a fresh persistent subject.

A history file is not replayed as current perception. It initializes durable memory,
relationships, self-model evidence, and unresolved concerns while preserving an audit
record of exactly which history artifact was imported.
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


def _clamp(value: Any, *, signed: bool = False) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("history numeric values must be finite")
    return max(-1.0 if signed else 0.0, min(1.0, number))


def load_history(path: str | Path) -> tuple[dict[str, Any], str]:
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or int(raw.get("schema", 0)) != HISTORY_SCHEMA:
        raise ValueError("unsupported history schema")
    if not str(raw.get("history_id", "")).strip():
        raise ValueError("history_id is required")
    if not isinstance(raw.get("memories", []), list):
        raise ValueError("history memories must be a list")
    canonical = json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return raw, hashlib.sha256(canonical).hexdigest()


def _memory_id(history_id: str, record_id: str) -> str:
    return f"{history_id}:{record_id}"


def seed_history(subject, path: str | Path) -> dict[str, Any]:
    """Import typed prehistory once. A changed artifact requires a new subject store."""
    raw, digest = load_history(path)
    history_id = str(raw["history_id"])
    path = Path(path)

    with subject._transaction():
        prior = subject.history_imports.get(history_id)
        if prior:
            if prior.get("sha256") != digest:
                raise ValueError("history artifact changed after import; use a new subject store")
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

        relationships = raw.get("relationships", [])
        if not isinstance(relationships, list):
            raise ValueError("relationships must be a list")
        for item in relationships:
            person_id = str(item.get("person_id", "")).strip()
            if not person_id:
                raise ValueError("relationship person_id is required")
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

        imported_memories: dict[str, Memory] = {}
        seen_record_ids: set[str] = set()
        for item in raw.get("memories", []):
            record_id = str(item.get("id", "")).strip()
            if not record_id or record_id in seen_record_ids:
                raise ValueError("history memory ids must be unique and nonempty")
            seen_record_ids.add(record_id)
            evidence_class = str(item.get("evidence_class", "archive")).strip() or "archive"
            summary = str(item.get("summary", "")).strip()
            first_person = str(item.get("first_person", "")).strip()
            if not summary or not first_person:
                raise ValueError(f"history memory {record_id} requires summary and first_person")
            age = max(0, int(item.get("age_ticks", 0)))
            tags = tuple(dict.fromkeys((
                "history",
                evidence_class,
                *(str(tag) for tag in item.get("tags", []) if str(tag).strip()),
            )))
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

        beliefs = raw.get("beliefs", [])
        if not isinstance(beliefs, list):
            raise ValueError("beliefs must be a list")
        for item in beliefs:
            key = str(item.get("key", "")).strip()
            proposition = str(item.get("proposition", "")).strip()
            if not key or not proposition:
                raise ValueError("history beliefs require key and proposition")
            state.beliefs[key] = Belief(
                key,
                proposition,
                _clamp(item.get("confidence", 0.6)),
                _clamp(item.get("valence", 0.0), signed=True),
                state.tick - max(0, int(item.get("age_ticks", 0))),
            )

        claims = raw.get("narrative_claims", [])
        if not isinstance(claims, list):
            raise ValueError("narrative_claims must be a list")
        for item in claims:
            key = str(item.get("key", "")).strip()
            proposition = str(item.get("proposition", "")).strip()
            if not key or not proposition:
                raise ValueError("history narrative claims require key and proposition")
            evidence = tuple(
                imported_memories[record_id].id
                for record_id in item.get("evidence", [])
                if record_id in imported_memories
            )
            state.narrative[key] = NarrativeClaim(
                key,
                proposition,
                _clamp(item.get("confidence", 0.6)),
                _clamp(item.get("valence", 0.0), signed=True),
                evidence,
                state.tick - max(0, int(item.get("age_ticks", 0))),
            )

        open_loops = raw.get("open_loops", [])
        if not isinstance(open_loops, list):
            raise ValueError("open_loops must be a list")
        for item in open_loops:
            key = str(item.get("key", "")).strip()
            description = str(item.get("description", "")).strip()
            if not key or not description:
                raise ValueError("history open loops require key and description")
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

        orientation = []
        for record_id in raw.get("workspace_orientation", []):
            memory = imported_memories.get(str(record_id))
            if memory is None:
                raise ValueError(f"unknown workspace orientation memory: {record_id}")
            item = subject._add(
                "memory",
                remembered(memory),
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
