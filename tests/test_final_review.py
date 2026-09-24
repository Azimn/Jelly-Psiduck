import json
from dataclasses import replace

import pytest

from digital_subject.continuity import ContinuityState, SubjectContinuity
from digital_subject.host import PersistentOrganismHost
from digital_subject.enhanced_host import PersistentContinuityHost
from digital_subject.models import Event
from jelly_psiduck.cli import DEFAULT_CARTRIDGE
from digital_subject.cartridge import load_cartridge
from jelly_psiduck.workspace import SubjectiveWorkspace


@pytest.mark.parametrize("host_type", [PersistentOrganismHost, PersistentContinuityHost])
def test_legacy_host_rejects_changed_cartridge_content(tmp_path, host_type):
    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    path = tmp_path / "subject.json"
    host = host_type.open(cartridge, path, clock=lambda: 100, auto_catch_up=False)
    host.save()
    changed = replace(cartridge, need_rates={**cartridge.need_rates, "hunger": .1})
    with pytest.raises(ValueError, match="cartridge"):
        host_type.open(changed, path, clock=lambda: 100, auto_catch_up=False)
    assert host_type.open(cartridge, path, clock=lambda: 100, auto_catch_up=False).engine.state.tick == 0


def test_fingerprintless_snapshot_requires_explicit_migration(tmp_path):
    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    path = tmp_path / "subject.json"
    host = PersistentOrganismHost.open(cartridge, path, auto_catch_up=False)
    host.save()
    raw = json.loads(host.snapshot_path.read_text())
    raw.pop("cartridge_fingerprint")
    host.snapshot_path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="migration"):
        PersistentOrganismHost.open(cartridge, path, auto_catch_up=False)


def test_retained_continuity_support_and_revision_survive_trimming_restart():
    continuity = SubjectContinuity(record_limit=16)
    original = continuity.observe(Event("promise_made", "visitor", "I will return."), tick=1, interpretation="A promise.")
    continuity.create_expectation("A return.", tick=1, evidence_ids=(original.id,))
    revision = continuity.revise_record(original.id, interpretation="A later return.", evidence_id=original.id, confidence=.8, tick=2)
    for tick in range(3, 100):
        continuity.observe(Event("neutral", "world", str(tick)), tick=tick, interpretation="Time passed.")
    restored = SubjectContinuity(ContinuityState.from_dict(continuity.state.to_dict()), record_limit=16)
    assert restored._record(original.id).revised_by == revision.id
    assert restored._record(revision.id).evidence_ids
    assert len(restored.state.epistemic_records) == 18
    restored.revise_record(original.id, interpretation="Another correction.", evidence_id=revision.id, confidence=.9, tick=100)


def test_hidden_thoughts_do_not_shrink_eligible_window():
    workspace = SubjectiveWorkspace()
    for i in range(16):
        workspace.add(i, "social", f"Experience {i}")
        workspace.add(i, "thought", "Private unavailable thought", available_to_cognition=False)
    assert len(workspace.view().experiences) == 16
    assert workspace.view().experiences[0].first_person == "Experience 0"


def test_backward_legacy_clock_watermark_survives_restart(tmp_path):
    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    path = tmp_path / "subject.json"
    host = PersistentOrganismHost.open(cartridge, path, clock=lambda: 100, tick_seconds=10, auto_catch_up=False)
    assert host.catch_up(120).applied_ticks == 2
    assert host.catch_up(105).applied_ticks == 0
    reopened = PersistentOrganismHost.open(cartridge, path, clock=lambda: 120, auto_catch_up=False)
    assert reopened.catch_up(120).applied_ticks == 0
    assert reopened.catch_up(130).applied_ticks == 1


def test_capped_life_log_does_not_hide_new_experience(tmp_path):
    host = PersistentOrganismHost.open(load_cartridge(DEFAULT_CARTRIDGE), tmp_path / "s.json",
                                      clock=lambda: 100, tick_seconds=10, auto_catch_up=False)
    assert len(host.run_ticks(80)) == 80
    assert len(host.engine.state.life_log) == 64
    assert len(host.run_ticks(4)) == 4
    assert len(host.catch_up(130).experiences) == 3
