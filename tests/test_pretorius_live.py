from jelly_psiduck.pretorius_live import CONDITIONS, PROTOCOL, evaluate


def test_pretorius_live_dry_run_is_replayable_and_not_evidence():
    report = evaluate(dry_run=True, replicates=1)

    assert report["protocol"] == PROTOCOL
    assert {trial["condition"] for trial in report["trials"]} == {
        condition["name"] for condition in CONDITIONS
    }
    assert report["checks"]["paired_baselines_match"]
    assert report["checks"]["history_contract_pinned"]
    assert report["checks"]["history_arms_have_no_workspace_orientation"]
    assert report["checks"]["public_views_exclude_subject_id"]
    assert report["checks"]["clean_trials_replay_exactly"]
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
