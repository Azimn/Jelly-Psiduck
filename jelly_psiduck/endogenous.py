"""Opt-in v0.2 candidate. Endogenous activation is part of the same subject.

The core heartbeat, state transaction and action selector are inherited. These
hooks change which grounded experiences return to attention, not who owns action
or truth. Schema 2 prevents accidentally opening a v0.1 experimental apparatus.
"""
from dataclasses import asdict, dataclass

from digital_subject.models import Concern

from .firewall import LOW_IS_BAD, NEED_LANGUAGE, remembered
from .organism import Organism
from .runtime import ExperimentConfig, UnifiedSubject, concepts
from .semantics import interpret, ThoughtMeaning
from .workspace import Thought


@dataclass(frozen=True)
class EndogenousConfig(ExperimentConfig):
    graded_interoception: bool = True
    concern_recurrence: bool = True
    associative_drift: bool = True
    thought_recurrence: bool = True
    semantic_interpretation: bool = True
    prospective_feedback: bool = True
    activation_threshold: float = 0.8

    def __post_init__(self):
        super().__post_init__()
        if not .4 <= self.activation_threshold <= 2:
            raise ValueError("activation_threshold must be between .4 and 2")


class SituatedCognition:
    """Stateless engineering control: no scenario, actor names or sequence counter.

    This is deliberately a template provider. Its trajectories demonstrate causal
    scheduling and feedback, not unscripted natural-language intelligence.
    """
    def think(self, view):
        if not view.experiences:
            return None
        latest = view.experiences[-1]
        prefix = {"temporal": "I wonder what to expect now: ",
                  "memory": "This may matter to what I am considering: ",
                  "interoception": "I should attend to this feeling: ",
                  "thought": "I am not finished considering: "}.get(latest.source)
        return Thought(prefix + latest.first_person) if prefix else None


class EndogenousOrganism(Organism):
    def _triage_pressures(self):
        # Typed prospective concerns still flow through the existing fear options.
        return [("concern:fear" if key.startswith("concern:prospective:") else key, value)
                for key, value in super()._triage_pressures()]


class EndogenousSubject(UnifiedSubject):
    SCHEMA = 2
    CONFIG_TYPE = EndogenousConfig
    ENGINE_TYPE = EndogenousOrganism

    def __init__(self, *args, cognition=None, **kwargs):
        self.endogenous = {"body_levels": {}, "temporal_levels": {}, "activation": {},
                           "echoes": [], "drift": {}, "prospective_levels": {}}
        self.trigger = {"kind": "none", "parents": [], "depth": 0}
        super().__init__(*args, cognition=cognition if cognition is not None else SituatedCognition(), **kwargs)

    def _payload(self):
        return {**super()._payload(), "endogenous": self.endogenous}

    def _restore(self, raw):
        super()._restore(raw)
        self.endogenous = raw["endogenous"]
        self.trigger = {"kind": "none", "parents": [], "depth": 0}

    def _project_body(self):
        self.trigger = {"kind": "none", "parents": [], "depth": 0}
        if not self.config.graded_interoception:
            return super()._project_body()
        changed = False
        for key, description in NEED_LANGUAGE.items():
            value = self.engine.state.needs.get(key, .5)
            urgency = 1 - value if key in LOW_IS_BAD else value
            previous = self.endogenous["body_levels"].get(key, 0)
            level = sum(urgency >= threshold for threshold in (.45, .65, .85))
            # Downward hysteresis prevents numerical flutter becoming inner speech.
            if level < previous and urgency > (.45, .65, .85)[previous - 1] - .03:
                level = previous
            if level != previous:
                if level < previous:
                    text = "That feeling is easing." if level == 0 else f"It is easing: {description}"
                else:
                    text = ("I am beginning to notice this: " if level == 1 else
                            "It is hard to think past this: " if level == 3 else "") + description
                self._add("interoception", text, intensity=urgency, salience=urgency,
                          concepts=(key,), generated_by="body_change")
                changed = True
            self.endogenous["body_levels"][key] = level
        return changed

    def _open_records(self):
        """Typed continuity roots; evidence and status come only from the ledger."""
        for c in self.continuity.state.commitments.values():
            if c.status in {"open", "overdue"}:
                yield "commitment:" + c.id, c.description, c.due_tick, c.importance, c.actor, c.id
        for e in self.continuity.state.expectations.values():
            if e.status in {"pending", "expired"}:
                yield "expectation:" + e.id, e.proposition, e.due_tick, e.confidence, None, e.id

    def _urgency(self, due, importance, actor):
        age = max(0, self.engine.state.tick - due) if due is not None else 0
        relationship = self.engine.state.relationships.get(actor)
        attachment = relationship.attachment if relationship else 0
        uncertainty = relationship.uncertainty if relationship else .5
        return min(1, importance * (.25 + .45 * age / (age + 6)) + .2 * attachment + .1 * uncertainty)

    def _project_temporal(self):
        changed = False
        live = set()
        for key, description, due, importance, actor, record_id in self._open_records():
            live.add(key)
            if due is None:
                continue
            age = self.engine.state.tick - due
            # Grades express elapsed uncertainty; no invented external failure.
            level = 0 if age <= 0 else 1 if age <= 4 else 2 if age <= 12 else 3
            prior = self.endogenous["temporal_levels"].get(key, 0)
            if level != prior:
                prefix = {1: "The time I expected has passed: ",
                          2: "I have been waiting and still have no confirmation: ",
                          3: "The wait is becoming prolonged, and I still do not know: ",
                          0: "I am still anticipating: "}[level]
                self._add("temporal", prefix + description, generated_by=key,
                          concern_links=(key,), expectation_links=(record_id,) if key.startswith("expectation:") else (),
                          concepts=(actor,) if actor else (), salience=self._urgency(due, importance, actor))
                changed = True
            self.endogenous["temporal_levels"][key] = level
        for field in ("temporal_levels", "prospective_levels"):
            self.endogenous[field] = {k: v for k, v in self.endogenous[field].items() if k in live}
        for key in list(self.engine.state.concerns):
            if key.startswith("prospective:") and key.removeprefix("prospective:") not in live:
                del self.engine.state.concerns[key]
        return changed

    def _warrants_cognition(self, incoming, fresh_body, temporal):
        tick = self.engine.state.tick
        candidates = []
        for key, text, due, importance, actor, record_id in self._open_records():
            candidates.append((key, text, self._urgency(due, importance, actor), (actor,) if actor else (), record_id))
        for concern in self.engine.state.concerns.values():
            # Generic residual pressures are not proof of an unfinished matter.
            # Event concerns must still be in the organism's unresolved history;
            # prospective recurrence comes from open ledger roots above.
            if not concern.key.startswith("prospective:") and concern.description in self.engine.state.unresolved:
                candidates.append(("concern:" + concern.key, concern.description, concern.urgency, (), None))
        active_keys = {c[0] for c in candidates}
        readiness = .5 + .5 * self.engine.state.needs.get("focus", .5)
        self.endogenous["activation"] = {key: value for key, value in self.endogenous["activation"].items() if key in active_keys}
        if self.config.concern_recurrence:
            for key, _, urgency, _, _ in candidates:
                self.endogenous["activation"][key] = min(2.0, self.endogenous["activation"].get(key, 0) + urgency * readiness * .25)
        else:
            self.endogenous["activation"].clear()
        self.endogenous["echoes"] = [e for e in self.endogenous["echoes"] if tick <= e["expires"]]
        live_memories = {m.id: m for m in self.engine.state.memories}
        self.endogenous["drift"] = {key: item for key, item in self.endogenous["drift"].items()
                                   if key in live_memories and item["from_memory"] in live_memories and tick <= item["expires"]}

        if incoming or fresh_body or temporal:
            kind = "external" if incoming else "body_change" if fresh_body else "temporal_change"
            parents = [r.id for r in self.workspace.records if r.tick == tick and r.source != "thought"]
            self.trigger = {"kind": kind, "parents": parents, "depth": 0}
            self._trace({"kind": "cognition_trigger", **{"trigger": self.trigger}})
            return True

        if self.config.associative_drift and self.config.memory_feedback and self.endogenous["drift"]:
            key, item = max(self.endogenous["drift"].items(), key=lambda pair: (pair[1]["activation"], pair[0]))
            del self.endogenous["drift"][key]
            if item["activation"] >= .2:
                memory = live_memories[key]
                self._add("memory", remembered(memory), memory_links=(key, item["from_memory"]),
                          generated_by=item["thought"])
                self.trigger = {"kind": "association", "parents": [item["thought"], item["from_memory"], key], "depth": item["depth"]}
                self._trace({"kind": "cognition_trigger", "trigger": self.trigger})
                return True
        if self.config.thought_recurrence and self.endogenous["echoes"]:
            echo = self.endogenous["echoes"][0]
            if echo["due"] <= tick:
                self.endogenous["echoes"].pop(0)
                self._add("thought", echo["text"], generated_by=echo["parent"])
                self.trigger = {"kind": "prior_thought", "parents": [echo["parent"]], "depth": echo["depth"]}
                self._trace({"kind": "cognition_trigger", "trigger": self.trigger})
                return True
        eligible = [c for c in candidates if self.endogenous["activation"].get(c[0], 0) >= self.config.activation_threshold]
        if eligible:
            key, text, urgency, cues, record_id = max(eligible, key=lambda c: (self.endogenous["activation"][c[0]], c[0]))
            self.endogenous["activation"][key] = 0
            self._add("temporal", f"This unfinished matter returns to my attention: {text}",
                      salience=urgency, concern_links=(key,), concepts=cues, generated_by=key,
                      expectation_links=(record_id,) if key.startswith("expectation:") else ())
            self.trigger = {"kind": "unresolved_concern", "parents": [key], "depth": 0}
            self._trace({"kind": "cognition_trigger", "trigger": self.trigger})
            return True
        return False

    def _anchors(self):
        actors = {c.actor for c in self.continuity.state.commitments.values()}
        actors.update(self.engine.state.relationships)
        eligible = [r for r in self.workspace.records if r.available_to_cognition][-16:]
        return {actor: tuple(r.id for r in eligible if r.source != "thought" and concepts(actor) <= concepts(r.first_person))
                for actor in sorted(actors)
                if any(r.source != "thought" and concepts(actor) <= concepts(r.first_person) for r in eligible)}

    def _hear(self, thought):
        anchors = self._anchors()
        if self.config.semantic_interpretation:
            meaning = interpret(thought.first_person, anchors)
        else:
            actors = tuple(actor for actor in anchors if concepts(actor) <= concepts(thought.first_person))
            meaning = ThoughtMeaning(actors, "recall", "uninterpreted", ())
        vocabulary = {tag for m in self.engine.state.memories for tag in m.tags}
        tokens = concepts(thought.first_person)
        actor_terms = {actor.casefold() for actor in anchors}
        lexical = {
            tag for tag in vocabulary
            if tag.casefold() not in actor_terms and concepts(tag) <= tokens
        }
        cues = tuple(sorted(set(meaning.actors) | lexical))
        if self.config.thought_effects:
            self.attention = cues
        # One attended recollection per thought leaves related candidates available
        # to drift later, instead of flooding the same linguistic moment.
        memories = self.engine.recall(cues)[:1] if self.config.memory_feedback else []
        effects = []
        for memory in memories:
            self._add("memory", remembered(memory), memory_links=(memory.id,), generated_by=thought.id)
            if self.config.thought_effects and self._ready("recall:" + memory.id):
                key, delta = self.engine.appraise_recollection(memory)
                effects.append({"channel": "memory", "memory": memory.id, "pressure": key, "delta": delta})
            if self.config.thought_effects and self.config.associative_drift:
                self._spread(memory, thought.id)
        if self.config.thought_effects and self.config.prospective_feedback:
            effects.extend(self._prospective(meaning, thought))
        bodily_support = tuple(r.id for r in self.workspace.records[-16:]
                               if r.source == "interoception" and r.first_person in thought.first_person)
        grounded = bool(memories or meaning.support or bodily_support or effects)
        if grounded and self.config.thought_effects and self.config.thought_recurrence and self.trigger["depth"] < 2:
            self.endogenous["echoes"] = [{"text": thought.first_person, "parent": thought.id,
                "due": self.engine.state.tick + 2, "expires": self.engine.state.tick + 6,
                "depth": self.trigger["depth"] + 1}]
        self._trace({"kind": "inner_ear", "thought": thought.id, "meaning": asdict(meaning),
                     "concepts": cues, "memories": [m.id for m in memories], "effects": effects,
                     "bodily_support": bodily_support, "trigger": self.trigger})

    def _spread(self, memory, thought_id):
        if self.trigger["depth"] >= 2:
            return
        tick = self.engine.state.tick
        recent = {r.memory_links[0] for r in self.workspace.records[-8:] if r.source == "memory" and r.memory_links}
        for other in self.engine.recall(memory.tags):
            if other.id == memory.id or other.id in recent or tick - self.cooldowns.get("drift:" + other.id, -100) < 8:
                continue
            self.cooldowns["drift:" + other.id] = tick
            self.endogenous["drift"][other.id] = {"activation": min(1, other.strength * .6 + other.emotional_charge * .4),
                "thought": thought_id, "from_memory": memory.id, "expires": tick + 6,
                "depth": self.trigger["depth"] + 1}
        self.endogenous["drift"] = dict(sorted(self.endogenous["drift"].items(),
            key=lambda item: item[1]["activation"], reverse=True)[:4])

    def _prospective(self, meaning, thought):
        effects = []
        for key, text, due, importance, actor, record_id in self._open_records():
            supported = actor in meaning.actors if actor else any(
                concepts(a) <= concepts(text) for a in meaning.actors)
            if not actor and text.casefold() in thought.first_person.casefold():
                # Non-social expectations need no invented actor. Require the
                # proposition to have actually crossed the subjective boundary.
                supported = any(record_id in r.expectation_links and r.available_to_cognition
                                for r in self.workspace.records[-16:])
            if not supported or due is None or self.engine.state.tick <= due:
                continue
            age = self.engine.state.tick - due
            error = min(1, age / 12)
            previous = self.endogenous["prospective_levels"].get(key, 0)
            # Charge only newly encountered lateness, not every wording of it.
            delta = max(0, error - previous) * importance * .20
            self.endogenous["prospective_levels"][key] = max(previous, error)
            if delta <= 0:
                continue
            self.engine._adjust_pressure("fear", delta)
            urgency = self._urgency(due, importance, actor)
            concern_key = "prospective:" + key
            self.engine.state.concerns[concern_key] = Concern(concern_key,
                f"I still do not know what followed: {text}", urgency, .985, self.engine.state.tick)
            relationship = self.engine.state.relationships.get(actor)
            if relationship:
                relationship.uncertainty = min(1, relationship.uncertainty + delta)
            self._add("interoception", f"The uncertainty matters to me: {text}",
                      concern_links=(key,), generated_by=thought.id, intensity=urgency)
            effects.append({"channel": "prospective", "support": key, "prediction_error": error,
                            "pressure": "fear", "delta": delta})
        return effects
