# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _load(name: str) -> dict | None:
    path = REPO / "logs" / name
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def test_knn_origin_all_extinct_at_starve() -> None:
    found = [_load(f"knn_2500_s{s}.json") for s in (1, 2, 3)]
    if any(r is None for r in found):
        pytest.skip("origin knn JSON not generated")
    for run in found:
        assert run is not None
        assert run["config"]["m0"] == 200.0
        assert run["config"]["a0"] == 8.0
        assert run["extinct"] is True
        assert int(run["final_t"]) == 5
        assert run["pass_eval"]["pass"] is False
        g5 = next(g for g in run["generations"] if int(g["t"]) == 5)
        assert float(g5["cargo"]) == 200.0
        assert float(g5["share_stolen"]) == 0.0
        assert float(g5["mean_energy_bite_mammal"]) == 0.0
        assert int(run["n_cap_fallback_gens"]) == 0
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert "0 of 3" in readme
    assert "never found the mosquito" in readme
    assert "blank founders" in readme
    agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    assert "Do not bolt mosquitoes onto vial_morsus" in agents
    long_arm = (REPO / "LONG_ARM.md").read_text(encoding="utf-8")
    assert "new lock" in long_arm
    assert "Do not average" in long_arm or "do not average" in long_arm.lower()


def test_random_origin_all_extinct_at_starve() -> None:
    for seed in (1, 2, 3):
        run = _load(f"random_2500_s{seed}.json")
        if run is None:
            pytest.skip("origin random JSON not generated")
        assert run["extinct"] is True
        assert int(run["final_t"]) == 5


def test_fruit_forever_stolen_clean() -> None:
    run = _load("fruit_forever_400_s1.json")
    if run is None:
        pytest.skip("fruit-forever JSON not generated")
    last = run["generations"][-1]
    assert int(last["t"]) == 400
    assert float(last["share_stolen"]) < 0.05
    assert run["extinct"] is False
    assert float(last["mean_energy_bite_mammal"]) == 0.0
