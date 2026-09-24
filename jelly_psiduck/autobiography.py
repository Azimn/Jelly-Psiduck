"""Append-only autobiographical substrate for Pretorius v0.3.

This module records post-instantiation lived events separately from reconstructed
prehistory. The ledger is deterministic, hash chained, and append-only through its
public API. Model-generated prose is never accepted as an objective event source.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from typing import Any, Iterable


AUTOBIOGRAPHY_SCHEMA = 1
LIVED_PROVENANCE = "lived:v1"


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _clean_strings(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(
        str(value).strip() for value in values if str(value).strip()
    ))


def _clean_affect(values: dict[str, float] | Iterable[tuple[str, float]]) -> tuple[tuple[str, float], ...]:
    items = values.items() if isinstance(values, dict) else values
    cleaned = []
    for key, value in items:
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("affect values must be finite")
        cleaned.append((str(key), number))
    return tuple(sorted(cleaned))


@dataclass(frozen=True, slots=True)
class AutobiographicalEvent:
    id: str
    tick: int
    source: str
    event_type: str
    objective_record: str
    subjective_record: str
    provenance: str
    participants: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    affect_snapshot: tuple[tuple[str, float], ...] = ()
    concern_links: tuple[str, ...] = ()
    relationship_links: tuple[str, ...] = ()
    consequence_links: tuple[str, ...] = ()
    memory_links: tuple[str, ...] = ()
    supersedes_interpretation: str | None = None
    previous_hash: str | None = None
    event_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "AutobiographicalEvent":
        data = dict(raw)
        for key in (
            "participants",
            "tags",
            "affect_snapshot",
            "concern_links",
            "relationship_links",
            "consequence_links",
            "memory_links",
        ):
            data[key] = tuple(data.get(key, ()))
        data["affect_snapshot"] = tuple(
            (str(key), float(value)) for key, value in data["affect_snapshot"]
        )
        return cls(**data)

    def unhashed_payload(self) -> dict[str, Any]:
        payload = self.to_dict()
        payload.pop("event_hash", None)
        return payload


class AutobiographyLedger:
    """Deterministic Pretorius-local append-only event ledger."""

    def __init__(
        self,
        subject_id: str,
        events: Iterable[AutobiographicalEvent] = (),
        sequence: int = 0,
    ):
        subject_id = str(subject_id).strip()
        if not subject_id:
            raise ValueError("subject_id is required")
        self.subject_id = subject_id
        self.events = list(events)
        self.sequence = int(sequence)
        self.verify()

    def _next_id(self) -> str:
        self.sequence += 1
        return f"{self.subject_id}:event:{self.sequence:08d}"

    def append(
        self,
        *,
        tick: int,
        source: str,
        event_type: str,
        objective_record: str,
        subjective_record: str,
        provenance: str = LIVED_PROVENANCE,
        participants: Iterable[str] = (),
        tags: Iterable[str] = (),
        affect_snapshot: dict[str, float] | Iterable[tuple[str, float]] = (),
        concern_links: Iterable[str] = (),
        relationship_links: Iterable[str] = (),
        consequence_links: Iterable[str] = (),
        memory_links: Iterable[str] = (),
        supersedes_interpretation: str | None = None,
    ) -> AutobiographicalEvent:
        if provenance != LIVED_PROVENANCE:
            raise ValueError("new autobiographical events must use lived:v1 provenance")
        if int(tick) < 0:
            raise ValueError("event tick must be nonnegative")
        source = str(source).strip()
        event_type = str(event_type).strip()
        objective_record = str(objective_record).strip()
        subjective_record = str(subjective_record).strip()
        if not source or not event_type or not objective_record or not subjective_record:
            raise ValueError("event source, type, objective record and subjective record are required")
        if supersedes_interpretation is not None:
            supersedes_interpretation = str(supersedes_interpretation)
            if not any(item.id == supersedes_interpretation for item in self.events):
                raise ValueError("superseded interpretation must reference an existing event")

        event_id = self._next_id()
        previous_hash = self.events[-1].event_hash if self.events else None
        provisional = AutobiographicalEvent(
            id=event_id,
            tick=int(tick),
            source=source,
            event_type=event_type,
            objective_record=objective_record,
            subjective_record=subjective_record,
            provenance=provenance,
            participants=_clean_strings(participants),
            tags=_clean_strings(tags),
            affect_snapshot=_clean_affect(affect_snapshot),
            concern_links=_clean_strings(concern_links),
            relationship_links=_clean_strings(relationship_links),
            consequence_links=_clean_strings(consequence_links),
            memory_links=_clean_strings(memory_links),
            supersedes_interpretation=supersedes_interpretation,
            previous_hash=previous_hash,
        )
        event = AutobiographicalEvent(
            **{
                **provisional.to_dict(),
                "event_hash": _hash(provisional.unhashed_payload()),
            }
        )
        self.events.append(event)
        return event

    def get(self, event_id: str) -> AutobiographicalEvent | None:
        return next((item for item in self.events if item.id == event_id), None)

    @property
    def chain_head(self) -> str | None:
        return self.events[-1].event_hash if self.events else None

    def verify(self) -> None:
        expected_sequence = 0
        previous_hash = None
        seen: set[str] = set()
        prefix = f"{self.subject_id}:event:"
        for event in self.events:
            if event.id in seen:
                raise ValueError("duplicate autobiographical event id")
            seen.add(event.id)
            if not event.id.startswith(prefix) or not event.id[len(prefix):].isdigit():
                raise ValueError("invalid autobiographical event id")
            sequence = int(event.id[len(prefix):])
            if sequence != expected_sequence + 1:
                raise ValueError("autobiographical event sequence is not contiguous")
            expected_sequence = sequence
            if event.provenance != LIVED_PROVENANCE:
                raise ValueError("autobiographical event has unsupported provenance")
            if event.previous_hash != previous_hash:
                raise ValueError("autobiographical hash chain is broken")
            if _hash(event.unhashed_payload()) != event.event_hash:
                raise ValueError("autobiographical event hash mismatch")
            if event.supersedes_interpretation is not None and event.supersedes_interpretation not in seen:
                raise ValueError("event supersedes an unknown or later interpretation")
            previous_hash = event.event_hash
        if self.sequence != expected_sequence:
            raise ValueError("autobiographical sequence metadata does not match ledger")

    def to_state(self) -> dict[str, Any]:
        return {
            "schema": AUTOBIOGRAPHY_SCHEMA,
            "subject_id": self.subject_id,
            "sequence": self.sequence,
            "chain_head": self.chain_head,
            "events": [event.to_dict() for event in self.events],
        }

    @classmethod
    def from_state(cls, raw: dict[str, Any]) -> "AutobiographyLedger":
        if int(raw.get("schema", 0)) != AUTOBIOGRAPHY_SCHEMA:
            raise ValueError("unsupported autobiography schema")
        events = [
            AutobiographicalEvent.from_dict(item)
            for item in raw.get("events", [])
        ]
        ledger = cls(
            str(raw.get("subject_id", "")),
            events,
            int(raw.get("sequence", 0)),
        )
        if raw.get("chain_head") != ledger.chain_head:
            raise ValueError("autobiographical chain head does not match events")
        return ledger
