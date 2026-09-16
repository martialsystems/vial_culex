# Copyright (c) 2026 Martial Systems LLC
"""Fruit, then two mosquito liquids: hemolymph vs stolen midgut blood."""

from __future__ import annotations

from vial_culex.config import RunConfig

HOST_CHANNELS = ("hemolymph", "stolen_blood")


def fruit_available(t: int, cfg: RunConfig) -> float:
    if cfg.fruit_forever:
        return 1.0
    return 1.0 if int(t) < int(cfg.t_starve) else 0.0


def mosquitoes_present(t: int, cfg: RunConfig) -> bool:
    if cfg.fruit_forever:
        return False
    return int(t) >= int(cfg.t_starve)


def cargo_frac(cargo: float, cfg: RunConfig) -> float:
    c = max(float(cargo), 0.0)
    return c / max(c + float(cfg.k_cargo), float(cfg.eps_cargo))


def survive_params(t: int, cfg: RunConfig) -> tuple[float, float]:
    if fruit_available(t, cfg) > 0.0:
        return float(cfg.survive_steep_fruit), float(cfg.survive_thresh_fruit)
    return float(cfg.survive_steep_host), float(cfg.survive_thresh_host)
