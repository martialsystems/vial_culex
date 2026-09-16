# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from vial_culex.config import RunConfig
from vial_culex.population import run_generations


def test_fruit_forever_no_mosquito_blood() -> None:
    cfg = RunConfig(
        n=60,
        generations=30,
        seed=1,
        fruit_forever=True,
        t_starve=5,
        kinship_cap=False,
    )
    run = run_generations(cfg)
    gens = run["generations"]
    assert max(float(g["share_stolen"]) for g in gens) < 0.05
    assert max(float(g["cargo"]) for g in gens) == 0.0
    last = gens[-1]
    assert float(last["mean_energy_fruit"]) > float(last["mean_usable_stolen"])
    assert float(last["mean_energy_bite_mammal"]) == 0.0
