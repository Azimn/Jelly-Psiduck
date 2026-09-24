"""Deterministic, model-free memory consolidation for Pretorius v0.3."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Iterable, Sequence


_WORD = re.compile(r"[^\W_]+", re.UNICODE)


def _normalize(text: str) -> str:
    return " ".join(_WORD.findall(str(text).casefold()))


def _tokens(text: str) -> frozenset[str]:
    return frozenset(_WORD.findall(str(text).casefold()))


def _memory_snapshot(memory: Any) -> dict[str, Any]:
    raw = asdict(memory)
    raw["tags"] = list(raw.get("tags", ()))
    return raw


def retrieval_proxy(memory: Any, tick: int) -> float:
    recency = 1.0 / (1.0 + max(0, int(tick) - int(memory.last_recalled_tick)))
    return (
        float(memory.strength)
        + float(memory.emotional_charge) * 0.25
        + min(20, int(memory.recall_count)) * 0.01
        + recency * 0.02
    )


@dataclass(frozen=True, slots=True)
class ConsolidationAction:
    action: str
    memory_id: str | None
    reason: str
    replacement: str | None = None
    previous_retrieval_score: float | None = None
    related_memory_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ArchiveRecord:
    memory_id: str
    archive_tick: int
    reason: str
    previous_retrieval_score: float
    replacement: str | None
    cycle: int
    memory: dict[str, Any]
    source_event_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _retention_key(memory: Any, tick: int, protected: set[str]) -> tuple:
    return (
        memory.id in protected,
        memory.kind == "narrative",
        round(retrieval_proxy(memory, tick), 12),
        int(memory.last_recalled_tick),
        int(memory.created_tick),
        str(memory.id),
    )


def _exact_key(memory: Any) -> tuple:
    return (
        str(memory.kind),
        int(memory.created_tick),
        _normalize(memory.summary),
        _normalize(memory.meaning),
        tuple(sorted(str(tag) for tag in memory.tags)),
    )


def _near_duplicate(left: Any, right: Any) -> bool:
    if left.kind != right.kind or left.created_tick != right.created_tick:
        return False
    if tuple(sorted(left.tags)) != tuple(sorted(right.tags)):
        return False
    left_tokens = _tokens(f"{left.summary} {left.meaning}")
    right_tokens = _tokens(f"{right.summary} {right.meaning}")
    if len(left_tokens) < 6 or len(right_tokens) < 6:
        return False
    overlap = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    return union > 0 and overlap / union >= 0.96


def _contradiction_keys(memory: Any) -> tuple[str, ...]:
    prefix = "contradiction:"
    return tuple(sorted(
        str(tag)[len(prefix):]
        for tag in memory.tags
        if str(tag).startswith(prefix) and str(tag)[len(prefix):]
    ))


def plan_consolidation(
    memories: Sequence[Any],
    *,
    budget: int,
    tick: int,
    protected_ids: Iterable[str] = (),
    superseded_by: dict[str, str] | None = None,
) -> list[ConsolidationAction]:
    """Return an auditable deterministic plan without mutating memories."""
    if budget < 1:
        raise ValueError("memory budget must be positive")
    protected = set(protected_ids)
    superseded_by = dict(superseded_by or {})
    by_id = {memory.id: memory for memory in memories}
    if len(by_id) != len(memories):
        raise ValueError("active memory ids must be unique")

    actions: list[ConsolidationAction] = []
    archived: set[str] = set()

    for old_id, new_id in sorted(superseded_by.items()):
        if old_id in by_id and new_id in by_id and old_id != new_id and old_id not in protected:
            memory = by_id[old_id]
            actions.append(ConsolidationAction(
                "archive",
                old_id,
                "superseded",
                replacement=new_id,
                previous_retrieval_score=retrieval_proxy(memory, tick),
            ))
            archived.add(old_id)

    exact_groups: dict[tuple, list[Any]] = {}
    for memory in memories:
        if memory.id not in archived:
            exact_groups.setdefault(_exact_key(memory), []).append(memory)
    for group in sorted(exact_groups.values(), key=lambda group: tuple(sorted(item.id for item in group))):
        if len(group) < 2:
            continue
        keeper = max(group, key=lambda item: _retention_key(item, tick, protected))
        for memory in sorted(group, key=lambda item: item.id):
            if memory.id == keeper.id or memory.id in protected or memory.id in archived:
                continue
            actions.append(ConsolidationAction(
                "archive",
                memory.id,
                "exact_duplicate",
                replacement=keeper.id,
                previous_retrieval_score=retrieval_proxy(memory, tick),
            ))
            archived.add(memory.id)

    remaining = [memory for memory in memories if memory.id not in archived]
    ordered = sorted(remaining, key=lambda item: item.id)
    for index, left in enumerate(ordered):
        if left.id in archived:
            continue
        for right in ordered[index + 1:]:
            if right.id in archived or not _near_duplicate(left, right):
                continue
            pair = [left, right]
            keeper = max(pair, key=lambda item: _retention_key(item, tick, protected))
            candidate = right if keeper.id == left.id else left
            if candidate.id in protected:
                continue
            actions.append(ConsolidationAction(
                "archive",
                candidate.id,
                "near_duplicate",
                replacement=keeper.id,
                previous_retrieval_score=retrieval_proxy(candidate, tick),
            ))
            archived.add(candidate.id)
            if candidate.id == left.id:
                break

    contradiction_groups: dict[str, list[str]] = {}
    for memory in memories:
        if memory.id in archived:
            continue
        for key in _contradiction_keys(memory):
            contradiction_groups.setdefault(key, []).append(memory.id)
    for key, ids in sorted(contradiction_groups.items()):
        unique_ids = tuple(sorted(set(ids)))
        if len(unique_ids) >= 2:
            actions.append(ConsolidationAction(
                "flag",
                None,
                f"contradiction:{key}",
                related_memory_ids=unique_ids,
            ))

    active = [memory for memory in memories if memory.id not in archived]
    overflow = max(0, len(active) - budget)
    if overflow:
        eligible = [
            memory for memory in active
            if memory.id not in protected
        ]
        eligible.sort(key=lambda memory: _retention_key(memory, tick, protected))
        for memory in eligible[:overflow]:
            actions.append(ConsolidationAction(
                "archive",
                memory.id,
                "active_memory_budget",
                previous_retrieval_score=retrieval_proxy(memory, tick),
            ))
            archived.add(memory.id)

    return actions


def make_archive_record(
    memory: Any,
    action: ConsolidationAction,
    *,
    tick: int,
    cycle: int,
    source_event_ids: Iterable[str] = (),
) -> ArchiveRecord:
    if action.action != "archive" or action.memory_id != memory.id:
        raise ValueError("archive action does not match memory")
    return ArchiveRecord(
        memory_id=memory.id,
        archive_tick=int(tick),
        reason=action.reason,
        previous_retrieval_score=float(
            action.previous_retrieval_score
            if action.previous_retrieval_score is not None
            else retrieval_proxy(memory, tick)
        ),
        replacement=action.replacement,
        cycle=int(cycle),
        memory=_memory_snapshot(memory),
        source_event_ids=tuple(dict.fromkeys(str(item) for item in source_event_ids)),
    )
