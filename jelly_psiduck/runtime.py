"""One local, transactionally persisted subject; time and input share one loop.

SQLite serializes local writers. The entire subject, workspace, continuity,
inbox and feedback cooldowns commit together. A failed turn rolls back. Each
operation refreshes the latest snapshot, so a separate CLI can enqueue messages
while the heartbeat process lives. No process or model owns a second subject.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import threading
import time
from contextlib import contextmanager
from contextlib import closing
from dataclasses import asdict, dataclass
from pathlib import Path

from digital_subject.cartridge import Cartridge
from digital_subject.continuity import ContinuityState, SubjectContinuity
from digital_subject.continuity_influence import derive_continuity_influence, apply_continuity_influence
from digital_subject.models import Action, Consequence, Event

from .cognition import ReflectiveCognition
from .firewall import body_experiences, remembered
from .organism import Organism
from .workspace import SubjectiveWorkspace, Thought


@dataclass(frozen=True)
class ExperimentConfig:
    inner_ear: bool = True
    thought_effects: bool = True
    memory_feedback: bool = True
    autonomous_cognition: bool = True
    max_thoughts: int = 2

    def __post_init__(self):
        if type(self.max_thoughts) is not int or not 0 <= self.max_thoughts <= 4:
            raise ValueError("max_thoughts must be an integer from zero through four")


def concepts(text):
    return set(re.findall(r"[^\W_]+", text.casefold()))


class UnifiedSubject:
    SCHEMA = 1
    CONFIG_TYPE = ExperimentConfig
    ENGINE_TYPE = Organism

    def __init__(self, path: str | Path, cartridge: Cartridge, *, cognition=None,
                 config: ExperimentConfig | None = None, subject_id="subject-001"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.cartridge = cartridge
        self.cognition = cognition if cognition is not None else ReflectiveCognition()
        self.config = config or self.CONFIG_TYPE()
        self.fingerprint = hashlib.sha256(json.dumps(asdict(cartridge), sort_keys=True).encode()).hexdigest()
        self._lock = threading.RLock()
        self.engine = self.ENGINE_TYPE.from_cartridge(cartridge, subject_id)
        self.continuity = SubjectContinuity()
        self.workspace = SubjectiveWorkspace()
        self.workspace.add(0, "memory", f"I know myself as {cartridge.display_name}. "
                           + str(cartridge.identity.get("summary", "")), generated_by="cartridge")
        self.pending = []
        self.cooldowns = {}
        self.noticed = {}
        self.trace = []
        self.attention = ()
        self.last_clock = None
        self.clock_remainder = 0.0
        with closing(self._connect()) as db:
            db.execute("CREATE TABLE IF NOT EXISTS subject (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL)")
            db.commit()
        with self._transaction():
            if config is not None and self.config != config:
                raise ValueError("experiment configuration belongs to the persisted run; use a new store")

    def _connect(self):
        return sqlite3.connect(self.path, timeout=60)

    def _payload(self):
        return {"schema": self.SCHEMA, "cartridge": self.fingerprint,
                "config": asdict(self.config), "engine": self.engine.state.to_dict(),
                "continuity": self.continuity.state.to_dict(), "workspace": self.workspace.to_dict(),
                "pending": self.pending, "cooldowns": self.cooldowns, "noticed": self.noticed,
                "trace": self.trace, "attention": self.attention,
                "last_clock": self.last_clock, "clock_remainder": self.clock_remainder}

    def _restore(self, raw):
        if raw["schema"] != self.SCHEMA or raw["cartridge"] != self.fingerprint:
            raise ValueError("unsupported schema or changed cartridge; explicit migration required")
        self.config = self.CONFIG_TYPE(**raw["config"])
        self.engine = self.ENGINE_TYPE.from_dict(raw["engine"], self.cartridge)
        self.continuity = SubjectContinuity(ContinuityState.from_dict(raw["continuity"]))
        self.workspace = SubjectiveWorkspace.from_dict(raw["workspace"])
        self.pending = raw["pending"]
        self.cooldowns = raw["cooldowns"]
        self.noticed = raw["noticed"]
        self.trace = raw["trace"]
        self.attention = tuple(raw["attention"])
        self.last_clock = raw["last_clock"]
        self.clock_remainder = raw["clock_remainder"]

    @contextmanager
    def _transaction(self):
        with self._lock:
            db = self._connect()
            before = None
            try:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute("SELECT payload FROM subject WHERE id=1").fetchone()
                if row:
                    self._restore(json.loads(row[0]))
                before = json.loads(json.dumps(self._payload()))
                yield
                payload = json.dumps(self._payload(), allow_nan=False)
                db.execute("INSERT OR REPLACE INTO subject VALUES (1, ?)", (payload,))
                db.commit()
            except BaseException:
                db.rollback()
                if before is not None:
                    self._restore(before)
                raise
            finally:
                db.close()

    def inspect(self):
        """Read-only host telemetry; never passed to cognition or public expression."""
        with self._lock, closing(self._connect()) as db:
            return json.loads(db.execute("SELECT payload FROM subject WHERE id=1").fetchone()[0])

    def enqueue(self, event: Event):
        """Trusted host/sensor ingress. Chat text must use message(), not metadata."""
        if not event.description.strip() or len(event.description) > 4000:
            raise ValueError("event description must contain 1..4000 characters")
        if any(not math.isfinite(v) for v in (event.intensity, event.valence)):
            raise ValueError("event values must be finite")
        with self._transaction():
            if len(self.pending) >= 64:
                raise ValueError("inbox full")
            self.pending.append(asdict(event))

    def message(self, speaker: str, text: str):
        if not speaker.strip() or len(speaker) > 80 or speaker in {"self", "world", "system", "environment"}:
            raise ValueError("message requires a named external speaker")
        self.enqueue(Event("message", speaker, text, tags=(speaker, "communication")))

    def heartbeat(self):
        with self._transaction():
            return self._tick()

    def _add(self, source, text, **metadata):
        return self.workspace.add(self.engine.state.tick, source, text, **metadata)

    def _cognitive_view(self):
        """Detached provider view; subclasses may change selection, never contents."""
        return self.workspace.view()

    def _after_cognition_opportunity(self, warranted, thought_ids):
        """Optional lifecycle hook. Base architectures deliberately do nothing."""
        return None

    def _tick(self):
        state = self.engine.state
        self.engine.advance_body()
        self.continuity.advance_deadlines(state.tick)
        start = self.workspace.sequence
        fresh_body = self._project_body()

        last_event = None
        incoming, self.pending = self.pending[:8], self.pending[8:]
        for raw in incoming:
            event = Event(**{**raw, "tags": tuple(raw["tags"])})
            last_event = event
            influence = derive_continuity_influence(self.continuity, event, tick=state.tick)
            apply_continuity_influence(state, influence, tick=state.tick)
            packet = self.engine.step(event, advance_time=False, choose_conduct=False)
            links = packet.private_content["matched_memory_ids"]
            social = event.source not in {"world", "environment", "system", "self"}
            text = (f"I hear {event.source} say: {event.description}" if event.kind == "message"
                    else state.current_experience)
            item = self._add("social" if social else "perception", text,
                             concepts=event.tags, memory_links=links)
            self.continuity.observe(event, tick=state.tick, interpretation=text, evidence_ids=links)
            for memory in self.engine._memories_by_ids(links):
                self._add("memory", remembered(memory), memory_links=(memory.id,), generated_by=item.id)

        temporal = self._project_temporal()

        warranted = self._warrants_cognition(incoming, fresh_body, temporal)
        thought_ids = []
        if warranted and (incoming or self.config.autonomous_cognition):
            for _ in range(self.config.max_thoughts):
                try:
                    thought = self.cognition.think(self._cognitive_view())
                except Exception as exc:
                    self._trace({"kind": "cognition_error", "error_type": type(exc).__name__})
                    break
                if thought is None:
                    break
                if not isinstance(thought, Thought) or not isinstance(thought.text, str) or not 0 < len(thought.text.strip()) <= 600:
                    self._trace({"kind": "rejected_thought", "reason": "invalid_shape"})
                    break
                text = thought.text.strip()
                if any(r.source == "thought" and r.first_person == text and state.tick - r.tick < 6
                       for r in self.workspace.records):
                    break
                item = self._add("thought", text, concepts=tuple(sorted(concepts(text))),
                                 generated_by="cognition", available_to_cognition=self.config.inner_ear)
                thought_ids.append(item.id)
                if not self.config.inner_ear:
                    break
                self._hear(item)

        self._after_cognition_opportunity(warranted, tuple(thought_ids))
        action = self.engine.select_conduct(last_event)
        speech = None
        # Only explicitly selected communicative conduct can be rendered. A thought
        # is never copied into public speech, including conceal/deflect cases.
        if incoming and action in {Action.ANSWER, Action.ASK, Action.REPAIR, Action.CHALLENGE,
                                   Action.DEFLECT, Action.APPROACH}:
            options = self.cartridge.dialogue.get(action.value, ())
            if options:
                speech = options[0].format(name=state.display_name, topic="what I heard",
                    memory="what I remember", experience="what I experienced",
                    relationship="how I feel about this", need="what I need", activity=action.value)
                self.engine.record_expression(speech)
        if not incoming:
            activity = self.engine.finish_silent_activity(action)
            # Persist nonverbal life without forcing it into the language context.
            self._trace({"kind": "activity", "action": state.current_activity.value,
                         "experience": activity.first_person})
        self._trace({"kind": "heartbeat", "action": action.value, "thoughts": thought_ids,
                     "experience_count": self.workspace.sequence - start, "speech": speech})
        return {"tick": state.tick, "action": action.value, "speech": speech, "thoughts": thought_ids}

    def _project_body(self):
        state = self.engine.state
        fresh_body = False
        for key, text, urgency in body_experiences(state):
            if self.noticed.get(key) != text:
                self._add("interoception", text, salience=urgency, intensity=urgency, concepts=(key,))
                fresh_body = True
            self.noticed[key] = text
        active = {key for key, _, _ in body_experiences(state)}
        self.noticed = {k: v for k, v in self.noticed.items() if k in active}

        return fresh_body

    def _project_temporal(self):
        state = self.engine.state
        temporal = False
        for commitment in self.continuity.state.commitments.values():
            if commitment.status != "overdue":
                continue
            key = f"deadline:{commitment.id}"
            if key in self.cooldowns:
                continue
            self.cooldowns[key] = state.tick
            self._add("temporal", f"The time I expected has passed: {commitment.description}",
                      concepts=(commitment.actor,), concern_links=(commitment.id,))
            temporal = True
        for expectation in self.continuity.state.expectations.values():
            key = f"expectation:{expectation.id}"
            if expectation.status == "expired" and key not in self.cooldowns:
                self.cooldowns[key] = state.tick
                self._add("temporal", f"I still have no confirmation of what I expected: {expectation.proposition}",
                          expectation_links=(expectation.id,))
                temporal = True

        return temporal

    def _warrants_cognition(self, incoming, fresh_body, temporal):
        state = self.engine.state
        # Salient transitions and sparse revisits warrant cognition; quiet body
        # evolution does not require a sentence or a model call on every tick.
        revisit = state.tick % 6 == 0 and (bool(self.attention) or any(
            c.status == "overdue" for c in self.continuity.state.commitments.values()))
        if revisit and self.attention and self.config.memory_feedback:
            for memory in self.engine.recall(self.attention):
                self._add("memory", remembered(memory), memory_links=(memory.id,), generated_by="attention")
        warranted = bool(incoming) or fresh_body or temporal or revisit
        return warranted

    def _hear(self, thought):
        tokens = concepts(thought.first_person)
        # Concepts are grounded against existing tags/actors, never model-authored
        # numeric deltas, synthetic world events, or executable commitments.
        vocabulary = {tag for m in self.engine.state.memories for tag in m.tags}
        vocabulary.update(c.actor for c in self.continuity.state.commitments.values())
        cues = tuple(sorted(tag for tag in vocabulary if concepts(tag) <= tokens))
        if self.config.thought_effects:
            self.attention = cues
        if not self.config.memory_feedback:
            return
        memories = self.engine.recall(cues)
        effects = []
        for memory in memories:
            self._add("memory", remembered(memory), memory_links=(memory.id,), generated_by=thought.id)
            key = f"recall:{memory.id}"
            if self.config.thought_effects and self._ready(key):
                pressure, delta = self.engine.appraise_recollection(memory)
                effects.append({"memory": memory.id, "pressure": pressure, "delta": delta})
                self._add("interoception", "Remembering that leaves me uneasy." if pressure == "fear"
                          else "That memory changes how I feel right now.", memory_links=(memory.id,),
                          generated_by=thought.id)
        for actor in cues:
            if not any(c.actor == actor for c in self.continuity.state.commitments.values()):
                continue
            if self.config.thought_effects and self._ready(f"continuity:{actor}"):
                influence = derive_continuity_influence(self.continuity,
                    Event("recollection", actor, "I reconsider what I expected."), tick=self.engine.state.tick)
                apply_continuity_influence(self.engine.state, influence, tick=self.engine.state.tick)
                effects.append({"actor": actor, "pressure_deltas": influence.pressure_deltas,
                                "reasons": influence.reasons})
                if influence.concern_description:
                    self._add("interoception", f"I am concerned: {influence.concern_description}",
                              concern_links=(influence.concern_key,), generated_by=thought.id)
        self._trace({"kind": "inner_ear", "thought": thought.id, "concepts": cues,
                     "memories": [m.id for m in memories], "effects": effects})

    def _ready(self, key):
        tick = self.engine.state.tick
        if tick - self.cooldowns.get(key, -100) < 6:
            return False
        self.cooldowns[key] = tick
        return True

    def _trace(self, record):
        self.trace.append({"tick": self.engine.state.tick, **record})
        self.trace = self.trace[-256:]

    def consequence(self, consequence: Consequence):
        with self._transaction():
            self.engine.apply_consequence(consequence)
            self.continuity.advance_deadlines(self.engine.state.tick)
            self._add("action_consequence", self.engine._consequence_meaning(consequence),
                      concepts=consequence.tags)

    def catch_up(self, now: float, *, tick_seconds=5.0, max_ticks=12):
        if not math.isfinite(now) or not math.isfinite(tick_seconds) or tick_seconds <= 0 or max_ticks < 1:
            raise ValueError("invalid clock parameters")
        with self._transaction():
            if self.last_clock is None:
                self.last_clock = now
                return {"applied": 0, "skipped": 0, "results": []}
            elapsed = max(0, now - self.last_clock) + self.clock_remainder
            requested = int(elapsed // tick_seconds)
            self.clock_remainder = elapsed - requested * tick_seconds
            self.last_clock = max(now, self.last_clock)
            results = [self._tick() for _ in range(min(requested, max_ticks))]
            report = {"applied": len(results), "skipped": max(0, requested - max_ticks), "results": results}
            if report["skipped"]:
                self._trace({"kind": "clock_gap", "skipped_ticks": report["skipped"]})
            return report

    def run(self, stop: threading.Event, *, tick_seconds=5.0, on_result=None):
        """Foreground lifecycle; stop is interruptible, no hidden service install."""
        report = self.catch_up(time.time(), tick_seconds=tick_seconds)
        if on_result:
            for result in report["results"]:
                on_result(result)
        while not stop.wait(min(tick_seconds, 0.25)):
            report = self.catch_up(time.time(), tick_seconds=tick_seconds)
            if on_result:
                for result in report["results"]:
                    on_result(result)
