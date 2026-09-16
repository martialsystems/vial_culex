# Copyright (c) 2026 Martial Systems LLC
"""Generation loop. Fly census may fall. Mosquito arrivals are not flies."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from vial_culex.cargo import arm_cargo, consume_and_arrive
from vial_culex.config import RunConfig
from vial_culex.diet import mosquitoes_present
from vial_culex.fitness import phenotype
from vial_culex.genome import FEMALE, MALE, Pop, init_population
from vial_culex.inheritance import meiosis_mutate
from vial_culex.mating import freeze_sigma0, mating_traits, pair
from vial_culex.metrics import evaluate_pass, first_times, heterozygosity_qtl, record_generation


def cap_uniform(live: Pop, n_cap: int, rng: np.random.Generator) -> Pop:
    if live.n <= n_cap:
        return live
    idx = rng.choice(live.n, size=n_cap, replace=False)
    idx.sort()
    return live.take(idx)


def extinct_rule(pop: Pop, ph_mean_survive: float, cfg: RunConfig) -> bool:
    if pop.n == 0:
        return True
    n_f = int(np.sum(pop.sex == FEMALE))
    n_m = int(np.sum(pop.sex == MALE))
    if n_f == 0 or n_m == 0:
        return True
    if pop.n < cfg.fail_n_min and ph_mean_survive < cfg.fail_viability:
        return True
    return False


def run_generations(
    cfg: RunConfig,
    rng: np.random.Generator | None = None,
    jsonl_path: Path | None = None,
) -> dict:
    if cfg.mating_mode not in ("random", "assortative_knn"):
        raise ValueError(cfg.mating_mode)
    rng = rng or np.random.default_rng(cfg.seed)
    pop = init_population(cfg, rng)
    cargo = 0.0
    armed = False
    cargo, armed = arm_cargo(pop.t, cargo, armed, cfg)
    ph = phenotype(pop, cfg, cargo=cargo)
    h0 = heterozygosity_qtl(pop)
    jsonl_fp = None
    if jsonl_path is not None:
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        jsonl_fp = jsonl_path.open("w", encoding="utf-8")
    rec0 = record_generation(pop, ph, None, cfg, h0, pop.n, pop.n, cargo, 0.0, 0.0)
    records = [rec0]
    if jsonl_fp is not None:
        jsonl_fp.write(json.dumps(rec0) + "\n")
        jsonl_fp.flush()
    ceiling = cfg.ceiling()
    cap_armed = bool(cfg.kinship_cap) and cfg.kinship_cap_on != "recover"
    t_kinship_on = 0 if cap_armed else None
    n_fallback_gens = 0
    t_recover: int | None = None
    for _step in range(cfg.generations):
        if extinct_rule(pop, float(ph.survive.mean()) if pop.n else 0.0, cfg):
            records[-1]["extinct"] = True
            break
        if (
            not cfg.fruit_forever
            and t_recover is None
            and pop.t >= cfg.t_starve
            and pop.n >= int(cfg.kinship_recover_n)
        ):
            t_recover = int(pop.t)
        if (
            cfg.kinship_cap
            and cfg.kinship_cap_on == "recover"
            and not cap_armed
            and t_recover is not None
        ):
            cap_armed = True
            t_kinship_on = int(pop.t)
        sigma0 = freeze_sigma0(mating_traits(ph, pop.t, cfg), cfg)
        pairing = pair(pop, ph, cfg, rng, sigma0, cap_armed=cap_armed)
        n_fallback_gens += int(pairing.n_cap_fallback)
        taken = 0.0
        arrivals = 0.0
        if mosquitoes_present(pop.t, cfg):
            cargo, taken, arrivals = consume_and_arrive(cargo, ph.demand, cfg)
        eggs, _po, _cl = meiosis_mutate(pop, ph, pairing, cfg, rng)
        n_eggs = eggs.n
        if n_eggs == 0:
            pop = eggs
            cargo, armed = arm_cargo(pop.t, cargo, armed, cfg)
            ph = phenotype(pop, cfg, cargo=cargo)
            rec = record_generation(pop, ph, pairing, cfg, h0, 0, 0, cargo, arrivals, taken)
            rec["extinct"] = True
            records.append(rec)
            if jsonl_fp is not None:
                jsonl_fp.write(json.dumps(rec) + "\n")
            break
        egg_ph = phenotype(eggs, cfg, cargo=cargo)
        survive = (rng.random(eggs.n) < egg_ph.survive) & (egg_ph.v_load > 0.0)
        n_viable = int(survive.sum())
        live = eggs.take(np.flatnonzero(survive))
        pop = cap_uniform(live, ceiling, rng)
        cargo, armed = arm_cargo(pop.t, cargo, armed, cfg)
        ph = phenotype(pop, cfg, cargo=cargo)
        rec = record_generation(pop, ph, pairing, cfg, h0, n_eggs, n_viable, cargo, arrivals, taken)
        records.append(rec)
        if jsonl_fp is not None:
            jsonl_fp.write(json.dumps(rec) + "\n")
            jsonl_fp.flush()
        if rec["extinct"] or extinct_rule(pop, float(ph.survive.mean()) if pop.n else 0.0, cfg):
            records[-1]["extinct"] = True
            break
    if jsonl_fp is not None:
        jsonl_fp.close()
    last = records[-1]
    result = {
        "config": cfg.payload(),
        "seed": cfg.seed,
        "arm": cfg.arm,
        "mate": "random" if cfg.mating_mode == "random" else "knn",
        "k": cfg.k,
        "h0_qtl": h0,
        "generations": records,
        "final_t": last["t"],
        "extinct": bool(last["extinct"]),
        "t_kinship_on": t_kinship_on,
        "n_cap_fallback_gens": n_fallback_gens,
        **first_times(records, cfg),
    }
    if result.get("t_recover") is None:
        result["t_recover"] = t_recover
    result["pass_eval"] = evaluate_pass(result, cfg)
    return result


def write_run(result: dict, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result), encoding="utf-8")
