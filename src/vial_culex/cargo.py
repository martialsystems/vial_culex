# Copyright (c) 2026 Martial Systems LLC
"""Finite mosquito midgut cargo. Arrivals are mosquitoes, not flies."""

from __future__ import annotations

from vial_culex.config import RunConfig
from vial_culex.diet import mosquitoes_present


def arm_cargo(t: int, cargo: float, armed: bool, cfg: RunConfig) -> tuple[float, bool]:
    if not mosquitoes_present(t, cfg):
        return 0.0, False
    if not armed:
        return float(cfg.m0), True
    return float(cargo), True


def consume_and_arrive(cargo: float, demand: float, cfg: RunConfig) -> tuple[float, float, float]:
    """demand is sum of trait products. Take min(cargo, demand * cargo_frac)."""
    from vial_culex.diet import cargo_frac as frac

    c = max(float(cargo), 0.0)
    f = frac(c, cfg)
    taken = min(c, max(float(demand), 0.0) * f)
    left = c - taken
    arrivals = float(cfg.a0)
    return left + arrivals, taken, arrivals
