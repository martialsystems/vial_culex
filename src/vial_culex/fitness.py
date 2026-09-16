# Copyright (c) 2026 Martial Systems LLC
"""Stolen midgut blood vs hemolymph. Mammal bite energy is always 0."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from vial_culex.config import RunConfig
from vial_culex.diet import cargo_frac, fruit_available, mosquitoes_present, survive_params
from vial_culex.genome import (
    I_DIGEST,
    I_FIND,
    I_FRUIT,
    I_HEME,
    I_PROBE,
    I_RASP,
    Pop,
    additive_z,
)


def pos(x: np.ndarray) -> np.ndarray:
    return np.clip(x, 0.0, np.inf)


def logistic(energy: np.ndarray, thresh: float, steep: float) -> np.ndarray:
    x = np.clip(steep * (energy - thresh), -60.0, 60.0)
    return 1.0 / (1.0 + np.exp(-x))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -60.0, 60.0)))


def load_weights(load: np.ndarray, cfg: RunConfig) -> np.ndarray:
    if load.size == 0:
        return np.ones((0, load.shape[1] if load.ndim == 3 else 0), dtype=np.float64)
    hom = (load[:, :, 0] == 1) & (load[:, :, 1] == 1)
    w = np.ones(load.shape[:2], dtype=np.float64)
    n_let = int(cfg.n_lethal)
    w[:, :n_let] = np.where(hom[:, :n_let], 1.0 - cfg.s_let, 1.0)
    w[:, n_let:] = np.where(hom[:, n_let:], 1.0 - cfg.s_sub, 1.0)
    return w


@dataclass
class Energy:
    fruit: np.ndarray
    hemolymph: np.ndarray
    stolen: np.ndarray
    usable_stolen: np.ndarray
    bite_mammal: np.ndarray
    host: np.ndarray
    total: np.ndarray
    heme_load: np.ndarray
    demand: np.ndarray
    cargo: float
    frac: float


@dataclass
class Phenotype:
    z: np.ndarray
    energy_fruit: np.ndarray
    energy_hemolymph: np.ndarray
    energy_stolen: np.ndarray
    usable_stolen: np.ndarray
    energy_bite_mammal: np.ndarray
    energy_host: np.ndarray
    energy: np.ndarray
    heme_load: np.ndarray
    v_iron: np.ndarray
    cost: np.ndarray
    v_load: np.ndarray
    survive: np.ndarray
    fertility: np.ndarray
    w: np.ndarray
    thief: np.ndarray
    cargo: float
    cargo_frac: float
    demand: float
    share_fruit: np.ndarray
    share_hemolymph: np.ndarray
    share_stolen: np.ndarray


def energy_channels(z: np.ndarray, fruit_avail: float, cargo: float, cfg: RunConfig) -> Energy:
    n = int(z.shape[0])
    fruit = pos(z[:, I_FRUIT]) * float(fruit_avail)
    find = pos(z[:, I_FIND])
    rasp = pos(z[:, I_RASP])
    probe = pos(z[:, I_PROBE])
    demand = rasp * find * probe
    if fruit_avail > 0.0:
        hemo = np.zeros(n, dtype=np.float64)
        stolen = np.zeros(n, dtype=np.float64)
        frac = 0.0
    else:
        frac = cargo_frac(cargo, cfg)
        hemo = rasp * find * float(cfg.h0)
        stolen = demand * frac * float(cfg.s0)
    usable = stolen * sigmoid(z[:, I_DIGEST])
    host = usable + hemo
    heme_load = float(cfg.c_heme_in) * stolen
    zero = np.zeros(n, dtype=np.float64)
    return Energy(
        fruit=fruit,
        hemolymph=hemo,
        stolen=stolen,
        usable_stolen=usable,
        bite_mammal=zero,
        host=host,
        total=fruit + host,
        heme_load=heme_load,
        demand=demand,
        cargo=float(cargo),
        frac=float(frac),
    )


def _shares(fruit: np.ndarray, hemo: np.ndarray, usable: np.ndarray) -> tuple[np.ndarray, ...]:
    total = fruit + hemo + usable
    den = np.maximum(total, 1e-12)
    return fruit / den, hemo / den, usable / den


def trait_cost(z: np.ndarray, stolen: np.ndarray, cargo: float, cfg: RunConfig) -> np.ndarray:
    quad = cfg.c_quad * np.square(pos(z)).sum(axis=1)
    empty = 1.0 if float(cargo) <= cfg.eps_cargo else 0.0
    rasp_term = cfg.c_rasp * pos(z[:, I_RASP]) * empty
    probe_term = cfg.c_probe * pos(z[:, I_PROBE]) * empty
    unused_st = (stolen < cfg.eps_stolen).astype(np.float64)
    digest_term = cfg.c_digest * pos(z[:, I_DIGEST]) * unused_st
    heme_term = cfg.c_heme * pos(z[:, I_HEME]) * unused_st
    return quad + rasp_term + probe_term + digest_term + heme_term


def iron_viability(heme_load: np.ndarray, heme_safe: np.ndarray, cfg: RunConfig) -> np.ndarray:
    return np.exp(-cfg.beta_heme * heme_load / (1.0 + pos(heme_safe)))


def phenotype(pop: Pop, cfg: RunConfig, cargo: float = 0.0) -> Phenotype:
    z = additive_z(pop)
    empty = np.empty(0, dtype=np.float64)
    if pop.n == 0:
        return Phenotype(
            z=z,
            energy_fruit=empty,
            energy_hemolymph=empty,
            energy_stolen=empty,
            usable_stolen=empty,
            energy_bite_mammal=empty,
            energy_host=empty,
            energy=empty,
            heme_load=empty,
            v_iron=empty,
            cost=empty,
            v_load=empty,
            survive=empty,
            fertility=empty,
            w=empty,
            thief=np.empty(0, dtype=bool),
            cargo=float(cargo),
            cargo_frac=0.0,
            demand=0.0,
            share_fruit=empty,
            share_hemolymph=empty,
            share_stolen=empty,
        )
    fruit_avail = fruit_available(pop.t, cfg)
    e = energy_channels(z, fruit_avail, cargo, cfg)
    v_iron = iron_viability(e.heme_load, z[:, I_HEME], cfg)
    cost = trait_cost(z, e.stolen, cargo if mosquitoes_present(pop.t, cfg) else 1.0, cfg)
    # standing rasp/probe cost only when cargo is empty on the host era
    v_load = load_weights(pop.load, cfg).prod(axis=1)
    steep, thresh = survive_params(pop.t, cfg)
    survive = logistic(e.total, thresh=thresh, steep=steep) * v_iron
    fertility = pos(cfg.fert_a + cfg.fert_b * e.total - cfg.fert_d * cost) * v_load
    w = survive * fertility * np.exp(-cost) * v_load
    sf, sh, ss = _shares(e.fruit, e.hemolymph, e.usable_stolen)
    return Phenotype(
        z=z,
        energy_fruit=e.fruit,
        energy_hemolymph=e.hemolymph,
        energy_stolen=e.stolen,
        usable_stolen=e.usable_stolen,
        energy_bite_mammal=e.bite_mammal,
        energy_host=e.host,
        energy=e.total,
        heme_load=e.heme_load,
        v_iron=v_iron,
        cost=cost,
        v_load=v_load,
        survive=survive,
        fertility=fertility,
        w=w,
        thief=e.stolen > cfg.thief_threshold,
        cargo=e.cargo,
        cargo_frac=e.frac,
        demand=float(e.demand.sum()) if pop.n else 0.0,
        share_fruit=sf,
        share_hemolymph=sh,
        share_stolen=ss,
    )


def clutch_sizes(fert_f: np.ndarray, fert_m: np.ndarray, cfg: RunConfig) -> np.ndarray:
    return np.maximum(0, np.rint(cfg.c0 * fert_f * fert_m)).astype(np.int32)
