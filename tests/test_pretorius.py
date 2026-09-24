from __future__ import annotations

from dataclasses import asdict

import pytest

from digital_subject.cartridge import load_cartridge
from jelly_psiduck.endogenous import EndogenousSubject
from jelly_psiduck.history import seed_history
from jelly_psiduck.pretorius import DEFAULT_CARTRIDGE, DEFAULT_HISTORY, PretoriusSubject, open_pretorius


class CapturingRenderer:
    def __init__(self):
        self.views = []

    def render(self, view):
        self.views.append(view)
        return "A rendered Pretorius response."


def test_history_import_is_persisted_and_idempotent(tmp_path):
    host, first = open_pretorius(tmp_path / "pretorius.db")

    assert first["already_present"] is False
    assert first["memory_count"] == 34
    assert first["relationship_count"] == 4
    snapshot = host.inspect()
    assert "pretorius-lived-history-v1" in snapshot["history_imports"]
    assert snapshot["engine"]["relationships"]["Jay"]["familiarity"] == pytest.approx(.95)
    assert len(snapshot["engine"]["memories"]) == 34

    reopened, second = open_pretorius(tmp_path / "pretorius.db")
    assert second["already_present"] is True
    assert reopened.inspect()["history_imports"] == snapshot["history_imports"]
    assert len(reopened.inspect()["engine"]["memories"]) == 34


def test_jay_message_retrieves_actual_shared_history(tmp_path):
    host, _ = open_pretorius(tmp_path / "pretorius.db")

    host.message("Jay", "Why did we decide that history matters?")
    host.heartbeat()

    memories = [
        record
        for record in host.inspect()["workspace"]["records"]
        if record["source"] == "memory"
    ]
    linked = {link for record in memories for link in record["memory_links"]}
    assert any(link.startswith("pretorius-lived-history-v1:jay-") for link in linked)


def test_history_keeps_source_classes_distinct(tmp_path):
    host, _ = open_pretorius(tmp_path / "pretorius.db")
    kinds = {memory["kind"] for memory in host.inspect()["engine"]["memories"]}

    assert "history:screen_canon" in kinds
    assert "history:phenotype_evidence" in kinds
    assert "history:lived_project_history" in kinds
    assert "history:relationship_history" in kinds
    assert "history:research_history" in kinds


def test_model_renderer_receives_no_engine_telemetry_and_cannot_choose_conduct(tmp_path):
    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    renderer = CapturingRenderer()
    host = PretoriusSubject(
        tmp_path / "pretorius.db",
        cartridge,
        renderer=renderer,
        subject_id="pretorius-001",
    )
    seed_history(host, DEFAULT_HISTORY)

    host.message("Jay", "What do you make of this experiment?")
    result = host.heartbeat()

    assert result["action"] == "answer"
    assert result["speech"] == "A rendered Pretorius response."
    assert len(renderer.views) == 1
    view = renderer.views[0]
    assert view.selected_conduct == "answer"
    assert view.heard == "What do you make of this experiment?"
    serialized = asdict(view)
    assert "active_needs" not in serialized
    assert "private_content" not in serialized
    assert "sensorium" not in serialized
    assert all(isinstance(item, str) for item in view.felt_needs)


def test_history_import_rejects_changed_artifact_after_seed(tmp_path):
    host, _ = open_pretorius(tmp_path / "pretorius.db")
    altered = tmp_path / "altered.json"
    text = DEFAULT_HISTORY.read_text(encoding="utf-8")
    altered.write_text(text.replace(
        '"description": "A typed reconstruction history',
        '"description": "A changed reconstruction history'
    ), encoding="utf-8")

    with pytest.raises(ValueError, match="changed after import"):
        seed_history(host, altered)


def test_history_import_requires_fresh_subject(tmp_path):
    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    host = PretoriusSubject(tmp_path / "pretorius.db", cartridge, subject_id="pretorius-001")
    host.message("Jay", "Hello.")
    host.heartbeat()

    with pytest.raises(ValueError, match="fresh subject"):
        seed_history(host, DEFAULT_HISTORY)
