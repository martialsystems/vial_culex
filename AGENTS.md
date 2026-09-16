# Agent notes: vial_culex

MIT. Closed-form NumPy generation engine. Not a fork of vial_sanguis, vial_sanguis2, or vial_morsus.

Question: Can diploid sponging flies switch from fruit to stealing vertebrate blood already in an engorged mosquito, then find the next mosquito, without evolving a mammal-biting pierce kit?

The mosquito is the host. The fly drinks midgut cargo, leaves, repeats.

## Five laws

1. Closed fly vial. No fly immigration.
2. Load required. Hidden recessives exist. Load is excluded from mating similarity.
3. Fly census may fall. Never invent flies. Mosquito arrivals are not flies.
4. Two liquids stay separate: stolen midgut blood vs hemolymph.
5. Mouthparts open a mosquito. No vertebrate skin channel. No connectome stepper.

Do not pin GraphForge. Do not reuse vialforge. VBD is the finish gate.
Do not add mammal bite_weight.
Do not open human wounds as backup food.
Do not call p_thief a vampire meter. p_thief alone is not a pass.
Do not merge this PASS with vial_morsus.
1 of 3 is a fail. Do not average.
Do not load FlyWire or MaleCNS.

Claim ban: do not write that this is an origin of hematophagy.
Claim ban: do not write that we made vampire flies that bite people.
Allowed claim: flies can or cannot live on stolen mosquito blood meals under a finite cargo supply.

Origin locked: 0 of 3 k-NN seeds. Extinct at t=5 with cargo still 200.
Do not add mammal bite_weight. LONG_ARM.md state is halt. Next legal node is none.

Frozen origin: n=1000, generations=2500, t_starve=5, seeds 1 2 3,
M0=200, a0=8, k=3, delayed cap phi_max=0.25, min_accepted_pairs=8, z_max=3.0.

PASS (>=2 of 3 knn seeds at t_end=2500): stolen_blood share of host energy
>= 0.50 for 10 consecutive gens; hemolymph share < 0.30 at t_end;
digest and heme_safe rise only after stolen_blood load > 0;
fruit-forever stolen_blood share < 0.05 at t=400.
Fail the seed if they live on hemolymph and we still say blood.
fallback_gens > 0.2 * generations cannot PASS.

Autonomous continue is allowed only along LONG_ARM.md.
Curiosity is not a transition.
Unfreezing a diet knob is a halt.

This repo only (not the home VBD pack).

## Verify

`python3 ~/agent_laws_verify_before_done/vbd_gate.py check --app-root . --claim-done`
`.venv/bin/python -m pytest`
