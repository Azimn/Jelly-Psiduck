from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

from .cartridge import Cartridge
from .engine import SubjectEngine
from .models import Event, Experience, ExpressionPacket
from .world import RoomState, RoomWorld


@dataclass(frozen=True, slots=True)
class CatchUpReport:
    elapsed_seconds: float
    requested_ticks: int
    applied_ticks: int
    compressed_ticks: int
    remainder_seconds: float
    start_tick: int
    end_tick: int
    memory_delta: int
    start_needs: dict[str, float]
    end_needs: dict[str, float]
    experiences: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RuntimeState:
    schema_version: int = 1
    last_wall_time: float = 0.0
    remainder_seconds: float = 0.0
    last_seen_tick: int = 0
    total_catchup_ticks: int = 0
    world: dict[str, Any] = field(default_factory=dict)
    last_catchup: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None, now: float) -> "RuntimeState":
        raw = raw or {}
        return cls(
            schema_version=int(raw.get("schema_version", 1)),
            last_wall_time=float(raw.get("last_wall_time", now)),
            remainder_seconds=max(0.0, float(raw.get("remainder_seconds", 0.0))),
            last_seen_tick=max(0, int(raw.get("last_seen_tick", 0))),
            total_catchup_ticks=max(0, int(raw.get("total_catchup_ticks", 0))),
            world=dict(raw.get("world", {})),
            last_catchup=dict(raw.get("last_catchup", {})),
        )


class PersistentOrganismHost:
    """Owns clock, files, and objective room state for one organism."""

    def __init__(
        self,
        engine: SubjectEngine,
        cartridge: Cartridge,
        state_path: str | Path,
        runtime_path: str | Path,
        *,
        world: RoomWorld | None = None,
        runtime: RuntimeState | None = None,
        clock: Callable[[], float] = time.time,
        tick_seconds: float = 300.0,
        max_catchup_ticks: int = 288,
    ) -> None:
        if tick_seconds <= 0:
            raise ValueError("tick_seconds must be positive")
        if max_catchup_ticks < 1:
            raise ValueError("max_catchup_ticks must be at least 1")
        self.engine = engine
        self.cartridge = cartridge
        self.state_path = Path(state_path)
        self.runtime_path = Path(runtime_path)
        self.snapshot_path = Path(str(self.state_path) + ".snapshot.json")
        self.clock = clock
        self.tick_seconds = float(tick_seconds)
        self.max_catchup_ticks = int(max_catchup_ticks)
        now = float(clock())
        self.runtime = runtime or RuntimeState(last_wall_time=now)
        self.world = world or RoomWorld(RoomState.from_dict(self.runtime.world))
        self._lock = threading.RLock()
        self.world.apply_to(self.engine)

    @classmethod
    def open(
        cls,
        cartridge: Cartridge,
        state_path: str | Path,
        *,
        runtime_path: str | Path | None = None,
        subject_id: str = "subject-001",
        clock: Callable[[], float] = time.time,
        tick_seconds: float | None = None,
        max_catchup_ticks: int | None = None,
        auto_catch_up: bool = True,
    ) -> "PersistentOrganismHost":
        state_path = Path(state_path)
        runtime_path = Path(runtime_path) if runtime_path is not None else state_path.with_suffix(".runtime.json")
        now = float(clock())

        snapshot_path = Path(str(state_path) + ".snapshot.json")
        raw_runtime: dict[str, Any] = {}
        if snapshot_path.exists():
            snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
            if int(snapshot.get("schema_version", 0)) != 1:
                raise ValueError("unsupported persistent host snapshot schema")
            engine = SubjectEngine.from_dict(dict(snapshot["engine"]), cartridge)
            raw_runtime = dict(snapshot.get("runtime", {}))
        else:
            if state_path.exists():
                try:
                    engine = SubjectEngine.load(state_path, cartridge)
                except TypeError:
                    engine = SubjectEngine.load(state_path)
            else:
                engine = SubjectEngine.from_cartridge(cartridge, subject_id)
            if runtime_path.exists():
                raw_runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        runtime = RuntimeState.from_dict(raw_runtime, now)
        resolved_tick_seconds = float(tick_seconds if tick_seconds is not None else raw_runtime.get("tick_seconds", 300.0))
        resolved_max_catchup = int(max_catchup_ticks if max_catchup_ticks is not None else raw_runtime.get("max_catchup_ticks", 288))
        host = cls(
            engine,
            cartridge,
            state_path,
            runtime_path,
            world=RoomWorld(RoomState.from_dict(runtime.world)),
            runtime=runtime,
            clock=clock,
            tick_seconds=resolved_tick_seconds,
            max_catchup_ticks=resolved_max_catchup,
        )
        if auto_catch_up:
            host.catch_up(now)
        return host

    def catch_up(self, now: float | None = None) -> CatchUpReport:
        with self._lock:
            now = float(self.clock() if now is None else now)
            elapsed = max(0.0, now - self.runtime.last_wall_time) + self.runtime.remainder_seconds
            requested = int(elapsed // self.tick_seconds)
            applied = min(requested, self.max_catchup_ticks)
            compressed = max(0, requested - applied)
            remainder = elapsed - requested * self.tick_seconds

            start_tick = int(self.engine.state.tick)
            start_needs = dict(getattr(self.engine.state, "needs", {}))
            start_memories = len(getattr(self.engine.state, "memories", []))
            start_log = len(getattr(self.engine.state, "life_log", []))

            if applied:
                first_tick_time = now - max(0, applied - 1) * self.tick_seconds
                for index in range(applied):
                    self.world.advance_to(first_tick_time + index * self.tick_seconds)
                    self.world.apply_to(self.engine)
                    self._live_one_tick()

            new_log = getattr(self.engine.state, "life_log", [])[start_log:]
            report = CatchUpReport(
                elapsed_seconds=elapsed,
                requested_ticks=requested,
                applied_ticks=applied,
                compressed_ticks=compressed,
                remainder_seconds=remainder,
                start_tick=start_tick,
                end_tick=int(self.engine.state.tick),
                memory_delta=len(getattr(self.engine.state, "memories", [])) - start_memories,
                start_needs=start_needs,
                end_needs=dict(getattr(self.engine.state, "needs", {})),
                experiences=tuple(str(getattr(item, "first_person", item)) for item in new_log[-12:]),
            )
            self.runtime.last_wall_time = now
            self.runtime.remainder_seconds = remainder
            self.runtime.total_catchup_ticks += applied
            self.runtime.world = self.world.state.to_dict()
            self.runtime.last_catchup = report.to_dict()
            self.save()
            return report

    def run_ticks(self, ticks: int) -> tuple[Experience, ...]:
        with self._lock:
            count = max(0, int(ticks))
            start_log = len(getattr(self.engine.state, "life_log", []))
            timestamp = max(float(self.clock()), self.world.state.last_updated_at)
            for _ in range(count):
                timestamp += self.tick_seconds
                self.world.advance_to(timestamp)
                self.world.apply_to(self.engine)
                self._live_one_tick()
            self.runtime.last_wall_time = float(self.clock())
            self.runtime.world = self.world.state.to_dict()
            self.save()
            return tuple(getattr(self.engine.state, "life_log", [])[start_log:])

    def observe(self, event: Event) -> ExpressionPacket:
        with self._lock:
            self._before_observe(event)
            self.world.apply_to(self.engine)
            packet = self.engine.step(event)
            self._after_observe(event, packet)
            self.runtime.world = self.world.state.to_dict()
            self.runtime.last_wall_time = float(self.clock())
            self.save()
            return packet

    def set_room(self, **conditions: Any) -> ExpressionPacket:
        event = self.world.set_conditions(timestamp=float(self.clock()), **conditions)
        return self.observe(event)

    def arrive(self, person_id: str, display_name: str | None = None) -> ExpressionPacket:
        return self.observe(self.world.person_arrived(person_id, display_name))

    def leave(self, person_id: str, display_name: str | None = None) -> ExpressionPacket:
        return self.observe(self.world.person_left(person_id, display_name))

    def mark_seen(self) -> None:
        with self._lock:
            self.runtime.last_seen_tick = int(self.engine.state.tick)
            self.save_runtime()

    def save(self) -> None:
        with self._lock:
            self._before_save()
            snapshot = self._snapshot_payload()
            # This single file is authoritative. The historical JSON files below
            # remain compatibility mirrors only, so a crash cannot pair generations.
            self._atomic_write_json(self.snapshot_path, snapshot)
            try:
                self._atomic_write_json(self.state_path, snapshot["engine"])
                self._atomic_write_json(self.runtime_path, snapshot["runtime"])
            except OSError:
                # Recovery always prefers the already-committed authoritative snapshot.
                pass

    def save_runtime(self) -> None:
        self.save()

    def _snapshot_payload(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "engine": self.engine.state.to_dict(),
            "runtime": self._runtime_payload(),
            "extra": self._snapshot_extra(),
        }

    def _snapshot_extra(self) -> dict[str, Any]:
        return {}

    def _before_observe(self, event: Event) -> None:
        return None

    def _after_observe(self, event: Event, packet: ExpressionPacket) -> None:
        return None

    def _before_save(self) -> None:
        return None

    @staticmethod
    def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = Path(str(path) + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temporary.replace(path)

    def _runtime_payload(self) -> dict[str, Any]:
        self.runtime.world = self.world.state.to_dict()
        payload = self.runtime.to_dict()
        payload["tick_seconds"] = self.tick_seconds
        payload["max_catchup_ticks"] = self.max_catchup_ticks
        return payload

    def _live_one_tick(self) -> None:
        live = getattr(self.engine, "live", None)
        if callable(live):
            live(1)
        else:
            self.engine.idle_tick(1)
