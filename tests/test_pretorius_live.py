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
