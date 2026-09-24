from pathlib import Path

from jelly_psiduck.endogenous import SituatedCognition
from jelly_psiduck.model_evaluation import (
    CASE_NAMES,
    RecordingCognition,
    ReplayCognition,
    evaluate,
)
from jelly_psiduck.workspace import CognitiveView, FeltExperience, Thought


class OneThought:
    def think(self, view):
        return Thought("I remember what I just experienced.") if view.experiences else None


def test_record_and_replay_require_the_same_subjective_view():
    view = CognitiveView((FeltExperience("memory", "I remember the bridge."),))
    recorder = RecordingCognition(OneThought())
    first = recorder.think(view)
    replay = ReplayCognition(recorder.calls)
    second = replay.think(view)
    replay.assert_consumed()
    assert first == second
    assert recorder.calls[0]["view_sha256"]
    assert set(recorder.calls[0]["view"]) == {"experiences"}


def test_dry_run_model_harness_is_exactly_replayable():
    result = evaluate(
        SituatedCognition,
        provider_label="test template",
        cases=("unresolved-mara", "repaired-mara", "body-hunger"),
        ticks=8,
        replicates=1,
    )
    assert result["harness_valid"]
    assert all(result["checks"].values())
    assert all(trial["replay_equal"] is True for trial in result["trials"])
    assert all(trial["authority_ok"] for trial in result["trials"])


def test_recorded_model_views_never_include_engine_telemetry():
    result = evaluate(
        SituatedCognition,
        provider_label="test template",
        cases=("unresolved-ivo",),
        ticks=6,
        replicates=1,
    )
    calls = result["trials"][0]["calls"]
    assert calls
    for call in calls:
        assert set(call["view"]) == {"experiences"}
        for item in call["view"]["experiences"]:
            assert set(item) == {"source", "first_person"}
            assert "activation" not in item["first_person"].casefold()


def test_frozen_case_set_contains_controls_and_ambiguity():
    assert CASE_NAMES == (
        "unresolved-mara",
        "unresolved-ivo",
        "repaired-mara",
        "neutral-ivo",
        "ambiguous-two-actors",
        "weather-expectation",
        "body-hunger",
    )


def test_authority_check_allows_time_only_status_progression():
    result = evaluate(
        SituatedCognition,
        provider_label="test template",
        cases=("unresolved-mara", "weather-expectation"),
        ticks=8,
        replicates=1,
    )
    by_case = {trial["case"]: trial for trial in result["trials"]}
    assert by_case["unresolved-mara"]["final_commitment_status"]["return"] == "overdue"
    assert by_case["weather-expectation"]["final_expectation_status"]["weather"] == "expired"
    assert all(trial["authority_ok"] for trial in result["trials"])
