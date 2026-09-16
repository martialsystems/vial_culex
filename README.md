# vial_culex

Can diploid sponging flies switch from fruit to stealing vertebrate blood already in an engorged mosquito, then find the next mosquito, without evolving a mammal-biting pierce kit?

No. 0 of 3 k-NN seeds. All six starve arms went extinct at t=5, the first generation without fruit. Cargo was still 200. Stolen share 0. Hemolymph share 0. Mammal bite energy 0. Fruit-forever stolen share 0 at t=400. They never found the mosquito. Science lock `fa819c7`.

The mosquito is the host. Stolen midgut blood and hemolymph are separate liquids. Finite cargo: M0=200 at t_starve, arrivals a0=8 per generation.

## Origin

n=1,000, t_starve=5, 2,500 generations, seeds 1 to 3. k-NN delayed-cap. Random control. Fruit-forever t=400. M0=200, a0=8. `z_max=3.0`.

Copied from `logs/knn_2500_s{1,2,3}.json`, `logs/random_2500_s{1,2,3}.json`, `logs/fruit_forever_400_s1.json`.

| seed | mate | last live t | last live n | last live F | t_end | cargo at t=5 | stolen share | hemolymph share | mammal bite | extinct |
|-----:|------|------------:|------------:|------------:|------:|-------------:|-------------:|----------------:|------------:|:-------:|
| 1 | knn | 4 | 1,200 | 0.008 | 5 | 200 | 0 | 0 | 0 | yes |
| 2 | knn | 4 | 1,200 | 0.004 | 5 | 200 | 0 | 0 | 0 | yes |
| 3 | knn | 4 | 1,200 | 0.007 | 5 | 200 | 0 | 0 | 0 | yes |
| 1 | random | 4 | 1,200 | 0.001 | 5 | 200 | 0 | 0 | 0 | yes |
| 2 | random | 4 | 1,200 | 0.001 | 5 | 200 | 0 | 0 | 0 | yes |
| 3 | random | 4 | 1,200 | 0.001 | 5 | 200 | 0 | 0 | 0 | yes |
| 1 | fruit-forever | 400 | 1,200 | 0.551 | 400 | 0 | 0 | 0 | 0 | no |

None lived on hemolymph. None drained cargo. None were fallback-dominated. PASS requires >=2 of 3 k-NN seeds at t=2,500. 0 of 3 is a fail. Do not average. Do not add mammal `bite_weight`.

Halt.

## How to run

```text
python3.12 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest
.venv/bin/python -m vial_culex run --arm knn --seed 1 --generations 2500 \
  --starve-at 5 --mosq 200 --arrivals 8 \
  --out logs/knn_2500_s1.json
```

## Files

| Path | Role |
|------|------|
| `src/vial_culex/` | config, genome, diet, cargo, fitness, mating, inheritance, population, metrics, cli |
| `AGENTS.md` | Five laws. VBD gate. No GraphForge. |
| `LONG_ARM.md` | origin fail; next legal node: none |
| `tests/` | five laws, hemolymph ≠ stolen, cargo, fruit-forever, origin locks |
| `logs/knn_2500_s{1,2,3}.json` | origin k-NN locks |
| `logs/random_2500_s{1,2,3}.json` | origin random locks |
| `logs/fruit_forever_400_s1.json` | fruit-forever lock |

Do not add mammal bite_weight. Do not pin GraphForge. Do not restamp vial_morsus or vial_sanguis2.

[Fly research index](https://gist.github.com/martialsystems/12835f747d6360781f3cc7f91f243178)
