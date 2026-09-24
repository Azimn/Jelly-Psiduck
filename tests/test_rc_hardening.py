from __future__ import annotations

import json

import pytest

from digital_subject.cartridge import load_cartridge
from jelly_psiduck.cognition import OpenAICompatibleCognition, parse_text_json
from jelly_psiduck.history import seed_history
from jelly_psiduck.model_evaluation import ProtocolContractError, RecordingCognition
from jelly_psiduck.pretorius import DEFAULT_CARTRIDGE, DEFAULT_HISTORY, PretoriusSubject
from jelly_psiduck.workspace import CognitiveView, FeltExperience


def test_parser_allows_exact_json_and_one_complete_json_fence():
    assert parse_text_json('{"text":"hello"}', max_chars=20) == ("hello", "json")
    assert parse_text_json('```json\n{"text":null}\n```', max_chars=20) == (None, "fenced_json")
    with pytest.raises(ValueError):
        parse_text_json('Here is the JSON: {"text":"hello"}', max_chars=20)
    with pytest.raises(ValueError):
        parse_text_json('```python\n{"text":"hello"}\n```', max_chars=20)


def test_frozen_model_efficacy_harness_rejects_identity_before_network():
    view = CognitiveView((FeltExperience("memory", "I remember the bridge."),))
    provider = OpenAICompatibleCognition(
        "http://127.0.0.1:1/v1",
        "never-called",
        timeout=0.01,
        identity={"summary": "identity context must not enter protocol v1"},
    )
    recorder = RecordingCognition(provider)
    with pytest.raises(ProtocolContractError, match="forbids identity context"):
        recorder.think(view)
    assert recorder.calls[-1]["error_type"] == "ProtocolContractError"
    assert provider.calls == []


def test_history_provenance_is_not_an_associative_tag_and_orientation_can_be_disabled(tmp_path):
    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    host = PretoriusSubject(tmp_path / "pretorius.db", cartridge, subject_id="pretorius-001")
    report = seed_history(host, DEFAULT_HISTORY, workspace_orientation=False)
    snapshot = host.inspect()
    assert report["orientation_count"] == 0
    assert not any(record.get("generated_by") == "history-import" for record in snapshot["workspace"]["records"])
    for memory in snapshot["engine"]["memories"]:
        if memory["kind"].startswith("history:"):
            assert memory["kind"].split(":", 1)[1] not in memory["tags"]


def test_history_import_rejects_unknown_narrative_evidence(tmp_path):
    raw = json.loads(DEFAULT_HISTORY.read_text(encoding="utf-8"))
    raw["narrative_claims"][0]["evidence"].append("missing-memory")
    altered = tmp_path / "bad-history.json"
    altered.write_text(json.dumps(raw), encoding="utf-8")
    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    host = PretoriusSubject(tmp_path / "pretorius.db", cartridge, subject_id="pretorius-001")
    with pytest.raises(ValueError, match="references unknown memory"):
        seed_history(host, altered)


def test_history_import_rejects_duplicate_relationships(tmp_path):
    raw = json.loads(DEFAULT_HISTORY.read_text(encoding="utf-8"))
    raw["relationships"].append(dict(raw["relationships"][0]))
    altered = tmp_path / "bad-history.json"
    altered.write_text(json.dumps(raw), encoding="utf-8")
    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    host = PretoriusSubject(tmp_path / "pretorius.db", cartridge, subject_id="pretorius-001")
    with pytest.raises(ValueError, match="relationship person_id"):
        seed_history(host, altered)
