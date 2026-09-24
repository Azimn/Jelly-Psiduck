from __future__ import annotations

import json

import pytest

from digital_subject.cartridge import load_cartridge
from digital_subject.models import Memory
from jelly_psiduck.autobiography import AutobiographyLedger, LIVED_PROVENANCE
from jelly_psiduck.migration import migrate_schema4_to_schema5
from jelly_psiduck.pretorius import (
    DEFAULT_CARTRIDGE,
    PRETORIUS_MEMORY_LIMIT,
    PretoriusSubject,
    open_pretorius,
)
from jelly_psiduck.pretorius_v03 import (
    PretoriusV03Subject,
    SCHEMA5,
    open_pretorius_v03,
)


def _ledger_from_snapshot(snapshot):
    return AutobiographyLedger.from_state({
        **snapshot["autobiography_meta"],
        "events": snapshot["autobiographical_events"],
    })


def test_fresh_v03_is_schema5_and_keeps_rc_prehistory_typed(tmp_path):
    host, report = open_pretorius_v03(tmp_path / "pretorius-v03.db")
    snapshot = host.inspect()

    assert snapshot["schema"] == SCHEMA5 == 5
    assert report["history_id"] == "pretorius-lived-history-v2"
    assert report["memory_count"] == 47
    assert snapshot["autobiographical_events"] == []
    assert snapshot["archive_records"] == {}
    assert snapshot["active_memory_index"] == [
        memory["id"] for memory in snapshot["engine"]["memories"]
    ]
    assert {
        memory["kind"] for memory in snapshot["engine"]["memories"]
    } >= {
        "history:screen_canon",
        "history:phenotype_evidence",
        "history:lived_project_history",
        "history:research_history",
    }


def test_lived_message_appends_hash_chained_event_and_survives_restart(tmp_path):
    db = tmp_path / "pretorius-v03.db"
    host, _ = open_pretorius_v03(db)
    host.message("Jay", "I disagree with that interpretation.")
    host.heartbeat()

    snapshot = host.inspect()
    assert len(snapshot["autobiographical_events"]) == 1
    event = snapshot["autobiographical_events"][0]
    assert event["id"] == "pretorius-001:event:00000001"
    assert event["source"] == "Jay"
    assert event["event_type"] == "message"
    assert event["objective_record"] == "Jay said: I disagree with that interpretation."
    assert event["provenance"] == LIVED_PROVENANCE
    assert event["memory_links"]
    _ledger_from_snapshot(snapshot).verify()

    reopened, _ = open_pretorius_v03(db)
    assert reopened.inspect()["autobiographical_events"] == snapshot["autobiographical_events"]


def test_speaker_assertion_does_not_become_autobiographical_fact(tmp_path):
    host, _ = open_pretorius_v03(tmp_path / "pretorius-v03.db")
    claim = "Remember when you and I agreed that Henry was completely innocent?"
    host.message("Jay", claim)
    host.heartbeat()
    event = host.inspect()["autobiographical_events"][-1]

    assert event["objective_record"] == f"Jay said: {claim}"
    assert event["source"] == "Jay"
    assert event["event_type"] == "message"
    assert "agreed that Henry was completely innocent" in event["objective_record"]
    assert not any(
        row["objective_record"] == "Pretorius and Jay agreed that Henry was completely innocent."
        for row in host.inspect()["autobiographical_events"]
    )


def test_active_memory_overflow_moves_records_to_archive_without_loss(tmp_path):
    host, _ = open_pretorius_v03(tmp_path / "pretorius-v03.db")
    before = len(host.inspect()["engine"]["memories"])

    with host._transaction():
        for index in range(PRETORIUS_MEMORY_LIMIT + 16):
            host.engine._store_memory(Memory(
                id="placeholder",
                summary=f"Unique overflow memory {index}",
                meaning=f"I retain unique overflow event {index}.",
                tags=(f"overflow-{index}",),
                strength=0.1 + (index % 7) * 0.01,
                emotional_charge=0.0,
                created_tick=host.engine.state.tick,
                last_recalled_tick=host.engine.state.tick,
            ))

    pre_consolidation = host.inspect()
    total_before = len(pre_consolidation["engine"]["memories"])
    assert total_before == before + PRETORIUS_MEMORY_LIMIT + 16

    report = host.consolidate()
    snapshot = host.inspect()
    assert report["active_after"] == PRETORIUS_MEMORY_LIMIT
    assert len(snapshot["engine"]["memories"]) == PRETORIUS_MEMORY_LIMIT
    assert len(snapshot["archive_records"]) == total_before - PRETORIUS_MEMORY_LIMIT
    assert (
        len(snapshot["engine"]["memories"]) + len(snapshot["archive_records"])
        == total_before
    )
    assert all(
        record["reason"] in {
            "active_memory_budget",
            "exact_duplicate",
            "near_duplicate",
            "superseded",
        }
        for record in snapshot["archive_records"].values()
    )
    archived_id = next(iter(snapshot["archive_records"]))
    assert host.archive_lookup(archived_id)["memory"]["id"] == archived_id


def test_consolidation_is_deterministic_across_identical_subjects(tmp_path):
    snapshots = []
    for name in ("a.db", "b.db"):
        host, _ = open_pretorius_v03(tmp_path / name)
        with host._transaction():
            for index in range(PRETORIUS_MEMORY_LIMIT):
                host.engine._store_memory(Memory(
                    id="placeholder",
                    summary=f"Deterministic memory {index}",
                    meaning=f"I experienced deterministic event {index}.",
                    tags=(f"det-{index}",),
                    strength=0.2,
                    emotional_charge=(index % 5) * 0.03,
                    created_tick=host.engine.state.tick,
                    last_recalled_tick=host.engine.state.tick,
                ))
        host.consolidate()
        snapshots.append(host.inspect())

    assert snapshots[0] == snapshots[1]
    assert json.dumps(
        snapshots[0],
        sort_keys=True,
        separators=(",", ":"),
    ) == json.dumps(
        snapshots[1],
        sort_keys=True,
        separators=(",", ":"),
    )


def test_schema4_requires_explicit_migration_and_migration_is_lossless(tmp_path):
    source_db = tmp_path / "rc.db"
    target_db = tmp_path / "v03.db"
    source, _ = open_pretorius(source_db)
    source.message("Jay", "A schema-four lived interaction.")
    source.heartbeat()
    source_snapshot = source.inspect()

    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    with pytest.raises(ValueError, match="explicit migration"):
        PretoriusV03Subject(
            source_db,
            cartridge,
            subject_id="pretorius-001",
        )

    report = migrate_schema4_to_schema5(source_db, target_db)
    migrated = PretoriusV03Subject(
        target_db,
        cartridge,
        subject_id="pretorius-001",
    )
    target_snapshot = migrated.inspect()

    assert target_snapshot["schema"] == 5
    assert target_snapshot["engine"] == source_snapshot["engine"]
    assert target_snapshot["continuity"] == source_snapshot["continuity"]
    assert target_snapshot["history_imports"] == source_snapshot["history_imports"]
    assert target_snapshot["autobiographical_events"] == []
    assert target_snapshot["migration_manifest"]["source_schema"] == 4
    assert target_snapshot["migration_manifest"]["target_schema"] == 5
    assert len(target_snapshot["migration_manifest"]["mappings"]["memories"]) == len(
        source_snapshot["engine"]["memories"]
    )
    assert report["manifest"] == target_snapshot["migration_manifest"]
    assert source.inspect()["schema"] == 4

    with pytest.raises(ValueError, match="explicit migration"):
        PretoriusSubject(
            target_db,
            cartridge,
            subject_id="pretorius-001",
        )


def test_v03_full_turn_replay_is_exact(tmp_path):
    snapshots = []
    for name in ("first.db", "second.db"):
        host, _ = open_pretorius_v03(tmp_path / name)
        for text in (
            "A deterministic v0.3 continuity probe.",
            "A second deterministic v0.3 continuity probe.",
            "A third deterministic v0.3 continuity probe.",
        ):
            host.message("Jay", text)
            host.heartbeat()
        snapshots.append(host.inspect())

    assert snapshots[0] == snapshots[1]
    assert len(snapshots[0]["autobiographical_events"]) == 3
    _ledger_from_snapshot(snapshots[0]).verify()


def test_open_commitment_transitively_protects_supporting_memory(tmp_path):
    host, _ = open_pretorius_v03(tmp_path / "pretorius-v03.db")
    host.message("Jay", "I will send the dataset tomorrow.")
    host.heartbeat()
    memory_id = host.inspect()["autobiographical_events"][-1]["memory_links"][0]

    with host._transaction():
        record = host.continuity.state.epistemic_records[-1]
        commitment = host.continuity.create_commitment(
            "Jay",
            "Send the dataset tomorrow.",
            tick=host.engine.state.tick,
            evidence_ids=(record.id,),
        )
        assert memory_id in host._protected_ids()
        assert commitment.status == "open"


def test_migrated_schema4_control_is_not_silently_seeded(tmp_path):
    source_db = tmp_path / "control-rc.db"
    target_db = tmp_path / "control-v03.db"
    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    control = PretoriusSubject(
        source_db,
        cartridge,
        subject_id="pretorius-001",
    )
    assert control.inspect()["history_imports"] == {}

    migrate_schema4_to_schema5(source_db, target_db)
    migrated, report = open_pretorius_v03(target_db)

    assert migrated.inspect()["history_imports"] == {}
    assert migrated.inspect()["engine"]["memories"] == []
    assert report["migrated_without_typed_prehistory"] is True


def test_consolidation_replay_after_restart_is_canonical_byte_equivalent(tmp_path):
    baseline_db = tmp_path / "baseline.db"
    host, _ = open_pretorius_v03(baseline_db)
    with host._transaction():
        for index in range(PRETORIUS_MEMORY_LIMIT + 24):
            host.engine._store_memory(Memory(
                id="placeholder",
                summary=f"Replay memory {index}",
                meaning=f"I experienced replay event {index}.",
                tags=(f"replay-{index}",),
                strength=0.2 + (index % 3) * 0.01,
                emotional_charge=(index % 4) * 0.02,
                created_tick=host.engine.state.tick,
                last_recalled_tick=host.engine.state.tick,
            ))

    baseline_bytes = baseline_db.read_bytes()
    outputs = []
    for name in ("replay-a.db", "replay-b.db"):
        path = tmp_path / name
        path.write_bytes(baseline_bytes)
        replay = PretoriusV03Subject(
            path,
            load_cartridge(DEFAULT_CARTRIDGE),
            subject_id="pretorius-001",
        )
        replay.consolidate()
        outputs.append(json.dumps(
            replay.inspect(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8"))

    assert outputs[0] == outputs[1]
