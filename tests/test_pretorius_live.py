from digital_subject.models import Event
from jelly_psiduck.pretorius_live import CONDITIONS, PROTOCOL, evaluate


def test_pretorius_live_dry_run_is_replayable_and_not_evidence():
    report = evaluate(dry_run=True, replicates=1)

    assert report["protocol"] == PROTOCOL
    assert {trial["condition"] for trial in report["trials"]} == {
        condition["name"] for condition in CONDITIONS
    }
    assert report["checks"]["paired_baselines_match"]
    assert report["checks"]["history_contract_pinned"]
    assert report["checks"]["prehistory_arms_have_no_workspace_orientation"]
    assert report["checks"]["public_views_exclude_subject_id"]
    assert report["checks"]["clean_trials_replay_exactly"], [
        {
            "condition": trial["condition"],
            "error": trial["replay_error"],
            "diagnostics": trial["replay_diagnostics"],
        }
        for trial in report["trials"]
        if trial["clean"] and trial["replay_equal"] is not True
    ]
    assert report["harness_valid"]
    assert report["evidence_eligible"] is False


def test_pretorius_dynamic_memory_ids_are_deterministic(tmp_path):
    from digital_subject.cartridge import load_cartridge
    from jelly_psiduck.pretorius import DEFAULT_CARTRIDGE, PretoriusSubject

    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    ids = []
    for name in ("a.db", "b.db"):
        host = PretoriusSubject(
            tmp_path / name,
            cartridge,
            subject_id="pretorius-001",
        )
        host.message("Jay", "A deterministic replay probe.")
        host.heartbeat()
        ids.append([
            memory["id"]
            for memory in host.inspect()["engine"]["memories"]
            if not memory["kind"].startswith("history:")
        ])

    assert ids[0] == ids[1]
    assert ids[0]
    assert all(item.startswith("pretorius-001:memory:") for item in ids[0])


def test_pretorius_full_turn_state_is_deterministic(tmp_path):
    from digital_subject.cartridge import load_cartridge
    from jelly_psiduck.pretorius import DEFAULT_CARTRIDGE, PretoriusSubject

    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    snapshots = []
    for name in ("first.db", "second.db"):
        host = PretoriusSubject(
            tmp_path / name,
            cartridge,
            subject_id="pretorius-001",
        )
        for text in (
            "A deterministic continuity probe.",
            "A second deterministic continuity probe.",
            "A third deterministic continuity probe.",
        ):
            host.message("Jay", text)
            host.heartbeat()
        snapshots.append(host.inspect())

    assert snapshots[0] == snapshots[1]
    assert all(
        record["id"].startswith("pretorius-001:record:")
        for record in snapshots[0]["continuity"]["epistemic_records"]
    )
    assert all(
        insight["id"].startswith("pretorius-001:insight:")
        for insight in snapshots[0]["continuity"]["insights"]
    )


def test_pretorius_continuity_ids_are_stable_at_creation_and_restart(tmp_path):
    from digital_subject.cartridge import load_cartridge
    from jelly_psiduck.pretorius import DEFAULT_CARTRIDGE, PretoriusSubject

    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    db = tmp_path / "continuity.db"
    host = PretoriusSubject(db, cartridge, subject_id="pretorius-001")
    with host._transaction():
        record = host.continuity.observe(
            Event("message", "Jay", "A continuity ID probe.", tags=("Jay", "communication")),
            tick=host.engine.state.tick,
            interpretation="I hear Jay.",
        )
        expectation = host.continuity.create_expectation(
            "A later check will occur.",
            tick=host.engine.state.tick,
            evidence_ids=(record.id,),
        )
        commitment = host.continuity.create_commitment(
            "Jay",
            "Return to the probe.",
            tick=host.engine.state.tick,
            evidence_ids=(record.id,),
        )

    assert record.id == "pretorius-001:record:00000001"
    assert expectation.id == "pretorius-001:expectation:00000001"
    assert commitment.id == "pretorius-001:commitment:00000001"

    reopened = PretoriusSubject(db, cartridge, subject_id="pretorius-001")
    with reopened._transaction():
        next_record = reopened.continuity.observe(
            Event("message", "Jay", "A second probe.", tags=("Jay", "communication")),
            tick=reopened.engine.state.tick,
            interpretation="I hear Jay again.",
        )
    assert next_record.id == "pretorius-001:record:00000002"
