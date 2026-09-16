# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from vial_culex.cargo import consume_and_arrive
from vial_culex.config import RunConfig
from vial_culex.population import run_generations


def test_consume_cannot_invent_cargo() -> None:
    cfg = RunConfig(a0=0.0, k_cargo=80.0)
    left, taken, arr = consume_and_arrive(10.0, 1000.0, cfg)
    assert taken <= 10.0
    assert left == 10.0 - taken
    assert arr == 0.0


def test_arrivals_are_mosquitoes() -> None:
    cfg = RunConfig(
        n=80,
        generations=20,
        seed=1,
        t_starve=3,
        m0=30.0,
        a0=4.0,
        kinship_cap=False,
        fail_n_min=1,
        fail_viability=0.0,
    )
    run = run_generations(cfg)
    host = [g for g in run["generations"] if int(g["t"]) >= 3]
    assert host
    assert float(host[0]["cargo"]) <= 30.0 + 4.0 + 1e-6
    for g in host:
        assert float(g["arrivals"]) in (0.0, 4.0) or abs(float(g["arrivals"]) - 4.0) < 1e-9
