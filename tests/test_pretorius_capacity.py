from digital_subject.cartridge import load_cartridge

from jelly_psiduck.history import seed_history
from jelly_psiduck.pretorius import (
    DEFAULT_CARTRIDGE,
    DEFAULT_HISTORY,
    PRETORIUS_ASSOCIATION_LIMIT,
    PRETORIUS_MEMORY_LIMIT,
    PRETORIUS_TOP_K,
    PretoriusSubject,
)


def test_pretorius_has_history_sized_capacity_without_changing_generic_defaults(tmp_path):
    cartridge = load_cartridge(DEFAULT_CARTRIDGE)
    host = PretoriusSubject(tmp_path / "pretorius.db", cartridge, subject_id="pretorius-001")
    seed_history(host, DEFAULT_HISTORY, workspace_orientation=False)

    assert host.engine.memory_limit == PRETORIUS_MEMORY_LIMIT == 512
    assert host.engine.association_limit == PRETORIUS_ASSOCIATION_LIMIT == 2048
    assert host.engine.top_k == PRETORIUS_TOP_K == 4
    assert len(host.engine.state.associations) > 32
    assert len(host.engine.state.associations) < PRETORIUS_ASSOCIATION_LIMIT

    reopened = PretoriusSubject(
        tmp_path / "pretorius.db",
        cartridge,
        subject_id="pretorius-001",
    )
    assert reopened.engine.memory_limit == PRETORIUS_MEMORY_LIMIT
    assert reopened.engine.association_limit == PRETORIUS_ASSOCIATION_LIMIT
    assert reopened.engine.top_k == PRETORIUS_TOP_K
