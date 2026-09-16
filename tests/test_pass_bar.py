# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from vial_culex.config import RunConfig
from vial_culex.metrics import evaluate_pass


def _row(t: int, **kw: object) -> dict:
    qtl = {"find_mosquito": 1.0, "cuticle_rasp": 1.0, "gut_probe": 1.0, "digest": 0.2, "heme_safe": 0.2}
    rec = {
        "t": t,
        "n": 200,
        "F": 0.3,
        "p_thief": 0.4,
        "share_stolen": 0.7,
        "share_hemolymph": 0.1,
        "mean_energy_stolen": 0.4,
        "mean_energy_bite_mammal": 0.0,
        "qtl_mean": qtl,
        "extinct": False,
    }
    rec.update(kw)
    return rec


def test_pass_requires_held_stolen_not_hemolymph() -> None:
    cfg = RunConfig(generations=20, held_stolen_w=3)
    recs = [_row(t) for t in range(0, 21)]
    recs[-1]["t"] = 20
    result = {
        "generations": recs,
        "extinct": False,
        "n_cap_fallback_gens": 0,
        "t_held_stolen": 5,
        "t_stolen_load": 2,
        "t_digest_rise": 4,
        "t_heme_safe_rise": 4,
    }
    assert evaluate_pass(result, cfg)["pass"] is True


def test_fail_if_lived_on_hemolymph() -> None:
    cfg = RunConfig(generations=20, held_stolen_w=3)
    recs = [_row(t, share_stolen=0.2, share_hemolymph=0.7) for t in range(0, 21)]
    result = {
        "generations": recs,
        "extinct": False,
        "n_cap_fallback_gens": 0,
        "t_held_stolen": 5,
        "t_stolen_load": 2,
        "t_digest_rise": 4,
        "t_heme_safe_rise": 4,
    }
    ev = evaluate_pass(result, cfg)
    assert ev["pass"] is False
    assert "hemolymph_ge_0.30" in ev["reasons"]
    assert "lived_on_hemolymph" in ev["reasons"]
