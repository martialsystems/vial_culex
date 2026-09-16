# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from pathlib import Path

import numpy as np

from vial_culex.config import RunConfig
from vial_culex.diet import HOST_CHANNELS
from vial_culex.fitness import energy_channels
from vial_culex.genome import QTL_AUTO, S_POST_STARVE
from vial_culex.mating import mating_indices
from vial_culex.population import run_generations

REPO = Path(__file__).resolve().parents[1]


def test_five_laws_defaults() -> None:
    cfg = RunConfig()
    assert cfg.n == 1000
    assert cfg.generations == 2500
    assert cfg.t_starve == 5
    assert cfg.m0 == 200.0
    assert cfg.a0 == 8.0
    assert cfg.z_max == 3.0
    assert not hasattr(cfg, "bite_weight")
    assert QTL_AUTO == (
        "fruit_use",
        "find_mosquito",
        "cuticle_rasp",
        "gut_probe",
        "digest",
        "heme_safe",
    )
    names = " ".join(QTL_AUTO)
    assert "pierce" not in names
    assert "sweat" not in names
    assert "wound" not in names
    assert HOST_CHANNELS == ("hemolymph", "stolen_blood")
    assert S_POST_STARVE == (1, 2, 3)
    assert mating_indices(cfg.t_starve, cfg) == S_POST_STARVE


def test_law1_never_invents_flies() -> None:
    cfg = RunConfig(
        n=40,
        generations=8,
        seed=7,
        t_starve=2,
        n_ceiling=4000,
        kinship_cap=False,
        fail_n_min=1,
        fail_viability=0.0,
    )
    result = run_generations(cfg)
    for g in result["generations"]:
        if g["t"] > 0:
            assert g["n"] <= g["n_viable"]
            assert g["n_viable"] <= g["n_eggs"]


def test_no_graphforge() -> None:
    assert not (REPO / "engine_pin.json").exists()
    assert not (REPO / "product_laws.py").exists()
    agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    assert "Do not pin GraphForge" in agents
    long_arm = (REPO / "LONG_ARM.md").read_text(encoding="utf-8")
    assert "Curiosity is not a transition." in long_arm
    assert "next legal node" in long_arm.lower()


def test_no_connectome_files() -> None:
    for path in REPO.rglob("*"):
        if any(part in {".venv", "__pycache__", ".git"} for part in path.parts):
            continue
        name = path.name.lower()
        assert "flywire" not in name
        assert "malecns" not in name
        if path.suffix.lower() in {".h5", ".hdf5"}:
            raise AssertionError(path)


def test_hemolymph_is_not_stolen_blood() -> None:
    cfg = RunConfig()
    z = np.zeros((2, 6), dtype=np.float64)
    z[:, 1] = 1.0
    z[:, 2] = 1.0
    z[1, 3] = 2.0
    low = energy_channels(z[:1], 0.0, 200.0, cfg)
    high = energy_channels(z[1:2], 0.0, 200.0, cfg)
    assert float(high.stolen[0]) > float(low.stolen[0])
    assert abs(float(high.hemolymph[0]) - float(low.hemolymph[0])) < 1e-12
    assert float(low.bite_mammal[0]) == 0.0
    assert float(high.bite_mammal[0]) == 0.0


def test_empty_cargo_zeros_stolen() -> None:
    cfg = RunConfig()
    z = np.ones((1, 6), dtype=np.float64)
    e = energy_channels(z, 0.0, 0.0, cfg)
    assert float(e.stolen[0]) == 0.0
    assert float(e.hemolymph[0]) > 0.0
