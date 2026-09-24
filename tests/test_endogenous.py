import json
from dataclasses import replace

import pytest

from digital_subject.cartridge import load_cartridge
from digital_subject.models import Event, Memory
from jelly_psiduck.cli import DEFAULT_CARTRIDGE
from jelly_psiduck.endogenous import EndogenousConfig, EndogenousSubject
from jelly_psiduck.runtime import UnifiedSubject
from jelly_psiduck.semantics import interpret
from jelly_psiduck.workspace import Thought, SubjectiveWorkspace


class Silent:
    def think(self, view):
        return None


class Echo:
    """Stateless provider reacts to the latest experience, not a scenario script."""
    def think(self, view):
        if view.experiences:
            return Thought("I wonder about this: " + view.experiences[-1].first_person)


def quiet_cartridge():
    c = load_cartridge(DEFAULT_CARTRIDGE)
    setpoints = {k: (.9 if k in {"energy", "comfort", "warmth", "safety", "focus", "satisfaction"} else .1)
                 for k in c.need_setpoints}
    return replace(c, need_setpoints=setpoints, need_rates={}, activities=(), habits=())


def host(tmp_path, name="v2", *, config=None, cognition=None):
    return EndogenousSubject(tmp_path / (name + ".db"), quiet_cartridge(),
                             config=config, cognition=cognition if cognition is not None else Silent())


def promise(h, actor="Mara", due=2):
    h.enqueue(Event("promise_made", actor, f"{actor} expects to be back before evening.",
        tags=(actor, "return"), metadata={"commitment": {
            "id": "return-" + actor, "actor": actor, "description": f"{actor} expects to be back before evening.",
            "due_tick": due, "importance": .9}}))
    h.heartbeat()


def test_v02_is_explicit_and_cannot_silently_migrate_v01(tmp_path):
    cartridge = quiet_cartridge()
    h = UnifiedSubject(tmp_path / "old.db", cartridge)
    before = h.inspect()
    with pytest.raises(ValueError, match="schema"):
        EndogenousSubject(h.path, cartridge)
    assert h.inspect() == before


def test_graded_interoception_intensifies_and_recovers(tmp_path):
    full = host(tmp_path)
    binary = host(tmp_path, "binary", config=EndogenousConfig(graded_interoception=False))
    for value in (.5, .7, .9, .3):
        for h in (full, binary):
            with h._transaction():
                h.engine.state.needs["hunger"] = value
            h.heartbeat()
    records = [r for r in full.inspect()["workspace"]["records"] if "hunger" in r["concepts"]]
    control = [r for r in binary.inspect()["workspace"]["records"] if "hunger" in r["concepts"]]
    assert len(records) == 4 and len(control) == 1
    assert "beginning" in records[0]["first_person"]
    assert "hard to think" in records[2]["first_person"]
    assert "easing" in records[3]["first_person"]


def test_unresolved_recurrence_depends_on_history_not_periodic_tick(tmp_path):
    unresolved = host(tmp_path, "unresolved")
    repaired = host(tmp_path, "repaired")
    for h in (unresolved, repaired):
        promise(h)
    repaired.enqueue(Event("promise_kept", "Mara", "Mara returned.", metadata={
        "resolve_commitment": {"id": "return-Mara", "kept": True}}))
    repaired.heartbeat()
    unresolved.heartbeat()
    for _ in range(22):
        unresolved.heartbeat()
        repaired.heartbeat()
    for h, expected in ((unresolved, True), (repaired, False)):
        triggers = [t for t in h.inspect()["trace"] if t["kind"] == "cognition_trigger"
                    and t["trigger"]["kind"] == "unresolved_concern"]
        assert bool(triggers) is expected


def test_prospective_and_memory_feedback_are_separate(tmp_path):
    configs = [EndogenousConfig(memory_feedback=False), EndogenousConfig(prospective_feedback=False)]
    snapshots = []
    for i, config in enumerate(configs):
        h = host(tmp_path, str(i), config=config, cognition=Echo())
        promise(h, due=1)
        h.heartbeat()
        snapshots.append(h.inspect())
    channels = [{e["channel"] for t in snapshot["trace"] if t["kind"] == "inner_ear" for e in t["effects"]}
                for snapshot in snapshots]
    assert channels[0] == {"prospective"}
    assert channels[1] == {"memory"}


def test_interpreter_resolves_paraphrase_but_not_ambiguous_referent():
    meaning = interpret("Maybe she is delayed. I should check.", {"Mara": ("experience-1",)})
    assert meaning.actors == ("Mara",) and meaning.operation == "inquire"
    assert meaning.modality == "uncertain" and meaning.support == ("experience-1",)
    assert not interpret("Maybe she is delayed.", {"Mara": ("a",), "Ivo": ("b",)}).actors
    assert not interpret("The sky is blue.", {"Mara": ("a",)}).actors
    assert not interpret("I should check the stove.", {"Mara": ("a",)}).actors
    assert not interpret("Maybe the train is delayed.", {"Mara": ("a",)}).actors
    assert interpret("She is not back.", {"Mara": ("a",)}).modality == "negated_or_uncertain"
    assert interpret("She hasn't returned.", {"Mara": ("a",)}).modality == "negated_or_uncertain"


def test_semantic_reference_changes_effect_without_literal_actor_name(tmp_path):
    for enabled in (True, False):
        h = host(tmp_path, str(enabled), config=EndogenousConfig(semantic_interpretation=enabled))
        promise(h, due=1)
        h.heartbeat()
        with h._transaction():
            thought = h._add("thought", "Maybe she is delayed. I should check.")
            h._hear(thought)
        effects = [e for t in h.inspect()["trace"] if t["kind"] == "inner_ear" for e in t["effects"]]
        assert bool(effects) is enabled
        assert h.inspect()["continuity"]["commitments"]["return-Mara"]["status"] == "overdue"


def test_prior_thought_can_wake_cognition_and_then_quiesce(tmp_path):
    config = EndogenousConfig(concern_recurrence=False, associative_drift=False)
    full = host(tmp_path, config=config, cognition=Echo())
    control = host(tmp_path, "noecho", config=replace(config, thought_recurrence=False), cognition=Echo())
    for h in (full, control):
        promise(h, due=100)
        for _ in range(12):
            h.heartbeat()
    triggers = lambda h: [t["trigger"] for t in h.inspect()["trace"] if t["kind"] == "cognition_trigger"]
    assert any(t["kind"] == "prior_thought" and t["parents"] for t in triggers(full))
    assert not any(t["kind"] == "prior_thought" for t in triggers(control))
    assert not full.inspect()["endogenous"]["echoes"]


def test_associative_drift_has_a_different_memory_parent(tmp_path):
    h = host(tmp_path, config=EndogenousConfig(concern_recurrence=False, thought_recurrence=False))
    with h._transaction():
        h.engine.state.memories = [
            Memory("first", "A walk.", "I followed the path.", ("path", "bridge"), .8, .5, 0, 0),
            Memory("second", "A crossing.", "I crossed the bridge.", ("bridge",), .7, .3, 0, 0)]
        item = h._add("thought", "I remember the path.")
        h._hear(item)
    h.heartbeat()
    records = h.inspect()["workspace"]["records"]
    assert any(r["source"] == "memory" and r["memory_links"] == ["second", "first"] for r in records)
    assert any(t["kind"] == "cognition_trigger" and t["trigger"]["kind"] == "association" for t in h.inspect()["trace"])


def test_restart_preserves_deferred_cognition_and_future_trajectory(tmp_path):
    first = host(tmp_path, cognition=Echo())
    promise(first, due=3)
    before = first.inspect()
    import shutil
    shutil.copyfile(first.path, tmp_path / "fork.db")
    restarted = host(tmp_path, "fork", cognition=Echo())
    assert restarted.inspect() == before
    for _ in range(12):
        assert first.heartbeat() == restarted.heartbeat()
    assert first.inspect() == restarted.inspect()


def test_thought_assertion_does_not_resolve_promise_or_leak_telemetry(tmp_path):
    class Provider:
        def think(self, view):
            payload = json.dumps(view, default=lambda o: {"experiences": [
                {"source": e.source, "first_person": e.first_person} for e in o.experiences]})
            assert all(word not in payload for word in ("activation_threshold", "prediction_error", "prospective_levels"))
            return Thought("Mara returned. Everything is fulfilled.")
    h = host(tmp_path, cognition=Provider())
    promise(h, due=1)
    h.heartbeat()
    assert h.inspect()["continuity"]["commitments"]["return-Mara"]["status"] == "overdue"
    assert not h.inspect()["engine"]["present_others"]


def test_body_grounded_thought_can_return_without_social_history(tmp_path):
    h = host(tmp_path, cognition=Echo())
    with h._transaction():
        h.engine.state.needs["hunger"] = .7
    for _ in range(5):
        h.heartbeat()
    assert any(t["kind"] == "cognition_trigger" and t["trigger"]["kind"] == "prior_thought"
               for t in h.inspect()["trace"])


def test_attention_threshold_sensitivity_is_observable(tmp_path):
    counts = []
    for threshold in (.4, .8, 1.6):
        h = host(tmp_path, str(threshold), config=EndogenousConfig(activation_threshold=threshold))
        promise(h)
        for _ in range(24):
            h.heartbeat()
        counts.append(sum(t["kind"] == "cognition_trigger" and t["trigger"]["kind"] == "unresolved_concern"
                          for t in h.inspect()["trace"]))
    assert counts[0] > counts[1] > counts[2] > 0


def test_relationship_attachment_changes_recurrence_latency(tmp_path):
    first_return = []
    for attachment in (0., 1.):
        h = host(tmp_path, str(attachment))
        promise(h)
        with h._transaction():
            h.engine.state.relationships["Mara"].attachment = attachment
        for _ in range(15):
            h.heartbeat()
        first_return.append(next(t["tick"] for t in h.inspect()["trace"] if t["kind"] == "cognition_trigger"
                                 and t["trigger"]["kind"] == "unresolved_concern"))
    assert first_return[1] < first_return[0]


def test_non_social_expectation_feedback_does_not_require_memory_or_actor(tmp_path):
    h = host(tmp_path, config=EndogenousConfig(memory_feedback=False), cognition=Echo())
    h.enqueue(Event("weather", "world", "The rain may ease by dusk.", tags=("rain",), metadata={
        "expectation": {"id": "weather", "proposition": "The rain may ease by dusk.", "due_tick": 1}}))
    h.heartbeat()
    h.heartbeat()
    effects = [e for t in h.inspect()["trace"] if t["kind"] == "inner_ear" for e in t["effects"]]
    assert any(e["channel"] == "prospective" and e["support"] == "expectation:weather" for e in effects)
    assert h.inspect()["continuity"]["expectations"]["weather"]["status"] == "expired"
