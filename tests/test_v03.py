import shutil
from dataclasses import replace

import pytest

from digital_subject.models import Event
from jelly_psiduck.endogenous import EndogenousSubject
from jelly_psiduck.endogenous_evaluation import experimental_cartridge
from jelly_psiduck.v03 import ReverieConfig, ReverieSubject
from jelly_psiduck.workspace import Thought


class Silent:
    def __init__(self):
        self.calls = 0

    def think(self, view):
        self.calls += 1
        return None


class Thinker:
    def __init__(self):
        self.calls = 0
        self.views = []

    def think(self, view):
        self.calls += 1
        self.views.append(view)
        return Thought("I wonder what else is here.")


def make(tmp_path, name="v03", *, config=None, cognition=None):
    return ReverieSubject(
        tmp_path / f"{name}.db",
        experimental_cartridge(),
        config=config,
        cognition=cognition if cognition is not None else Silent(),
    )


def promise(host, due=1):
    host.enqueue(Event(
        "promise_made",
        "Mara",
        "Mara expects to be back before evening.",
        tags=("Mara", "return"),
        metadata={"commitment": {
            "id": "return-Mara",
            "actor": "Mara",
            "description": "Mara expects to be back before evening.",
            "due_tick": due,
            "importance": .9,
        }},
    ))
    host.heartbeat()


def test_v03_is_separate_schema_and_does_not_open_v02_store(tmp_path):
    cartridge = experimental_cartridge()
    old = EndogenousSubject(tmp_path / "v02.db", cartridge, cognition=Silent())
    before = old.inspect()
    with pytest.raises(ValueError, match="schema"):
        ReverieSubject(old.path, cartridge, cognition=Silent())
    assert old.inspect() == before

    new = ReverieSubject(tmp_path / "v03.db", cartridge, cognition=Silent())
    with pytest.raises(ValueError, match="schema"):
        EndogenousSubject(new.path, cartridge, cognition=Silent())


def test_idle_reverie_calls_provider_without_forcing_thought(tmp_path):
    provider = Silent()
    host = make(tmp_path, cognition=provider)
    for _ in range(3):
        host.heartbeat()
    data = host.inspect()
    triggers = [t for t in data["trace"] if t["kind"] == "cognition_trigger"
                and t["trigger"]["kind"] == "idle_reverie"]
    assert triggers
    assert provider.calls == len(triggers)
    assert not any(r["source"] == "thought" for r in data["workspace"]["records"])


def test_idle_silence_uses_exponential_bounded_backoff(tmp_path):
    provider = Silent()
    host = make(tmp_path, cognition=provider)
    for _ in range(20):
        host.heartbeat()
    ticks = [t["tick"] for t in host.inspect()["trace"] if t["kind"] == "cognition_trigger"
             and t["trigger"]["kind"] == "idle_reverie"]
    assert ticks[:3] == [2, 6, 14]
    assert host.inspect()["v03"]["idle_interval"] <= host.config.idle_max_interval_ticks


def test_idle_thought_resets_backoff(tmp_path):
    class Alternate:
        def __init__(self):
            self.calls = 0
        def think(self, view):
            self.calls += 1
            return None if self.calls == 1 else Thought("I remember that I am still here.")

    provider = Alternate()
    host = make(tmp_path, cognition=provider)
    for _ in range(7):
        host.heartbeat()
    assert host.inspect()["v03"]["idle_interval"] == host.config.idle_interval_ticks
    assert host.inspect()["v03"]["idle_silence_streak"] == 0


def test_balanced_view_preserves_identity_and_caps_thought_occupancy(tmp_path):
    host = make(tmp_path)
    with host._transaction():
        host._add("perception", "I notice a bird outside.")
        host._add("interoception", "I am hungry.")
        host._add("temporal", "Time is passing.")
        host._add("memory", "I remember the bridge.")
        for index in range(14):
            host._add("thought", f"I keep thinking about the same thing {index}.")
    view = host._cognitive_view()
    assert len(view.experiences) <= 16
    assert view.experiences[0].source == "memory"
    assert view.experiences[0].first_person.startswith("I know myself as ")
    assert sum(e.source == "thought" for e in view.experiences) <= 3
    assert any(e.source == "perception" for e in view.experiences)
    assert any(e.source == "interoception" for e in view.experiences)
    assert any(e.source == "temporal" for e in view.experiences)


def test_balanced_view_deduplicates_exact_repeated_memory_text(tmp_path):
    host = make(tmp_path)
    with host._transaction():
        for _ in range(6):
            host._add("memory", "I remember the same bird.")
    view = host._cognitive_view()
    assert sum(e.first_person == "I remember the same bird." for e in view.experiences) == 1


def test_provider_view_remains_telemetry_free_under_composition(tmp_path):
    provider = Thinker()
    host = make(tmp_path, cognition=provider)
    for _ in range(3):
        host.heartbeat()
    assert provider.views
    for view in provider.views:
        for item in view.experiences:
            assert set(item.__dataclass_fields__) == {"source", "first_person"}
            assert "activation_threshold" not in item.first_person
            assert "idle_interval" not in item.first_person


def test_concern_habituation_reduces_forced_recurrence_without_resolving(tmp_path):
    base = ReverieConfig(idle_reverie=False, associative_drift=False, thought_recurrence=False)
    full = make(tmp_path, "full", config=base)
    control = make(tmp_path, "control", config=replace(base, concern_habituation=False))
    for host in (full, control):
        promise(host)
        for _ in range(60):
            host.heartbeat()

    def ticks(host):
        return [t["tick"] for t in host.inspect()["trace"] if t["kind"] == "cognition_trigger"
                and t["trigger"]["kind"] == "unresolved_concern"]

    assert len(ticks(full)) < len(ticks(control))
    assert full.inspect()["continuity"]["commitments"]["return-Mara"]["status"] == "overdue"


def test_restart_preserves_idle_backoff_and_future_views(tmp_path):
    host = make(tmp_path, cognition=Silent())
    for _ in range(3):
        host.heartbeat()
    before = host.inspect()
    fork_path = tmp_path / "fork.db"
    shutil.copyfile(host.path, fork_path)
    reopened = ReverieSubject(fork_path, host.cartridge, cognition=Silent())
    assert reopened.inspect() == before
    for _ in range(12):
        assert host.heartbeat() == reopened.heartbeat()
    assert host.inspect() == reopened.inspect()
