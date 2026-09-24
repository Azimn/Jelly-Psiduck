"""v0.3 candidate: sparse idle reverie plus a balanced subjective view.

This is a sibling experiment to the lived-history/Pretorius branch, not a merge of
it. The generic organism, v0.2 endogenous mechanisms and frozen model harness remain
the substrate. Schema 4 is intentionally distinct from both v0.2 schema 2 and the
separate lived-history schema 3 experiment.
"""
from __future__ import annotations

from dataclasses import dataclass

from .endogenous import EndogenousConfig, EndogenousSubject
from .workspace import CognitiveView, FeltExperience


@dataclass(frozen=True)
class ReverieConfig(EndogenousConfig):
    idle_reverie: bool = True
    idle_interval_ticks: int = 2
    idle_max_interval_ticks: int = 24
    balanced_workspace: bool = True
    concern_habituation: bool = True
    concern_refractory_ticks: int = 4
    concern_refractory_max_ticks: int = 24

    def __post_init__(self):
        super().__post_init__()
        for name in (
            "idle_interval_ticks",
            "idle_max_interval_ticks",
            "concern_refractory_ticks",
            "concern_refractory_max_ticks",
        ):
            value = getattr(self, name)
            if type(value) is not int or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.idle_max_interval_ticks < self.idle_interval_ticks:
            raise ValueError("idle_max_interval_ticks must be >= idle_interval_ticks")
        if self.concern_refractory_max_ticks < self.concern_refractory_ticks:
            raise ValueError("concern_refractory_max_ticks must be >= concern_refractory_ticks")


class ReverieSubject(EndogenousSubject):
    SCHEMA = 4
    CONFIG_TYPE = ReverieConfig

    def __init__(self, *args, **kwargs):
        self.v03 = {
            "last_warrant_tick": 0,
            "idle_interval": None,
            "idle_silence_streak": 0,
            "concern_exposures": {},
            "concern_next_tick": {},
        }
        super().__init__(*args, **kwargs)

    def _payload(self):
        return {**super()._payload(), "v03": self.v03}

    def _restore(self, raw):
        super()._restore(raw)
        self.v03 = raw["v03"]

    def _current_idle_interval(self):
        value = self.v03.get("idle_interval")
        return self.config.idle_interval_ticks if value is None else int(value)

    def _warrants_cognition(self, incoming, fresh_body, temporal):
        tick = self.engine.state.tick

        if incoming or temporal:
            self.v03["concern_exposures"].clear()
            self.v03["concern_next_tick"].clear()

        if self.config.concern_habituation:
            for key, next_tick in list(self.v03["concern_next_tick"].items()):
                if tick < int(next_tick):
                    self.endogenous["activation"][key] = 0
        else:
            self.v03["concern_exposures"].clear()
            self.v03["concern_next_tick"].clear()

        warranted = super()._warrants_cognition(incoming, fresh_body, temporal)
        if warranted:
            kind = self.trigger.get("kind")
            if kind == "unresolved_concern" and self.config.concern_habituation:
                parents = self.trigger.get("parents") or []
                if parents:
                    key = str(parents[0])
                    exposure = int(self.v03["concern_exposures"].get(key, 0)) + 1
                    self.v03["concern_exposures"][key] = exposure
                    delay = min(
                        self.config.concern_refractory_max_ticks,
                        self.config.concern_refractory_ticks * (2 ** (exposure - 1)),
                    )
                    self.v03["concern_next_tick"][key] = tick + delay
            self.v03["last_warrant_tick"] = tick
            self.v03["idle_interval"] = self.config.idle_interval_ticks
            self.v03["idle_silence_streak"] = 0
            return True

        if not self.config.idle_reverie or not self.config.autonomous_cognition:
            return False

        quiet_for = tick - int(self.v03.get("last_warrant_tick", 0))
        if quiet_for < self._current_idle_interval():
            return False

        self.trigger = {"kind": "idle_reverie", "parents": [], "depth": 0}
        self.v03["last_warrant_tick"] = tick
        self._trace({"kind": "cognition_trigger", "trigger": self.trigger})
        return True

    def _after_cognition_opportunity(self, warranted, thought_ids):
        if not warranted or self.trigger.get("kind") != "idle_reverie":
            return
        if thought_ids:
            self.v03["idle_silence_streak"] = 0
            self.v03["idle_interval"] = self.config.idle_interval_ticks
            return
        streak = int(self.v03.get("idle_silence_streak", 0)) + 1
        self.v03["idle_silence_streak"] = streak
        self.v03["idle_interval"] = min(
            self.config.idle_max_interval_ticks,
            self.config.idle_interval_ticks * (2 ** streak),
        )

    def _identity_text(self):
        summary = str(self.cartridge.identity.get("summary", "")).strip()
        return f"I know myself as {self.cartridge.display_name}." + (f" {summary}" if summary else "")

    @staticmethod
    def _view_category(source):
        if source == "thought":
            return "thought"
        if source == "memory":
            return "memory"
        if source == "interoception":
            return "body"
        if source == "temporal":
            return "temporal"
        if source in {"perception", "social", "action_consequence"}:
            return "external"
        return "imagination"

    def _cognitive_view(self):
        if not self.config.balanced_workspace:
            return super()._cognitive_view()

        eligible = [record for record in self.workspace.records if record.available_to_cognition]
        indexed = list(enumerate(eligible))
        limits = {
            "thought": 3,
            "memory": 3,
            "body": 2,
            "temporal": 3,
            "external": 3,
            "imagination": 1,
        }
        counts = {key: 0 for key in limits}
        selected = []
        selected_ids = set()
        signatures = {("memory", self._identity_text())}

        def admit(index, record):
            category = self._view_category(record.source)
            signature = (record.source, record.first_person)
            if record.id in selected_ids or signature in signatures:
                return False
            if counts[category] >= limits[category]:
                return False
            selected.append((index, FeltExperience(record.source, record.first_person)))
            selected_ids.add(record.id)
            signatures.add(signature)
            counts[category] += 1
            return True

        for category in ("external", "body", "temporal", "memory", "thought", "imagination"):
            wanted = limits[category]
            for index, record in reversed(indexed):
                if counts[category] >= wanted:
                    break
                if self._view_category(record.source) == category:
                    admit(index, record)

        for index, record in reversed(indexed):
            if len(selected) >= 15:
                break
            admit(index, record)

        selected.sort(key=lambda item: item[0])
        experiences = [FeltExperience("memory", self._identity_text())]
        experiences.extend(item for _, item in selected[-15:])
        return CognitiveView(tuple(experiences[:16]))
