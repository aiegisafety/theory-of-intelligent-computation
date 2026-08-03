"""Run one configuration of the sweep and append to results.json.

Usage:  python3 run_sweep.py <config_index>
"""
import json
import os
import sys
import time
import numpy as np

from env import RendezvousTorus
from refine import refine, entropy_rates
from simulate import Scenario, evaluate

CONFIGS = []
for N, K, tag in [(6, 1, "base"), (6, 4, "highH"), (12, 1, "bigS")]:
    for m in (2, 3, 6):
        CONFIGS.append(dict(N=N, m=m, K=K, tag=tag))

ALPHABETS = [1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 24]
N_SEEDS = 60
RESULTS = "results.json"


def main(i):
    cfg = CONFIGS[i]
    t0 = time.time()
    env = RendezvousTorus(grid_size=cfg["N"], m=cfg["m"], K=cfg["K"])
    s2b, nb = refine(env.num_states, env.num_actions, env.labels,
                     env.transitions_for_action)
    h, h_th, _, _ = entropy_rates(env.num_states, s2b, nb,
                                  env.uniform_policy_chain())
    sc = Scenario(env, s2b, nb)
    print(f"[{i}] {cfg} |S|={env.num_states} blocks={nb} "
          f"h={h:.4f} h_theta={h_th:.4f} setup={time.time()-t0:.1f}s", flush=True)

    rows = []
    for M in ALPHABETS:
        C = float(np.log2(M))
        for mode in ("class", "state"):
            mu, sd = evaluate(sc, mode, M, n_seeds=N_SEEDS)
            rows.append(dict(**cfg, num_states=int(env.num_states),
                             n_blocks=int(nb), h=h, h_theta=h_th,
                             alphabet=M, C=C, mode=mode,
                             success_mean=mu, success_std=sd,
                             n_seeds=N_SEEDS, scramble=False))
            print(f"   M={M:2d} C={C:.2f} {mode:5s} {mu:.3f}+-{sd:.3f}",
                  flush=True)
    # channel ablation control at the largest alphabet
    for mode in ("class", "state"):
        mu, sd = evaluate(sc, mode, 24, n_seeds=N_SEEDS, scramble=True)
        rows.append(dict(**cfg, num_states=int(env.num_states),
                         n_blocks=int(nb), h=h, h_theta=h_th,
                         alphabet=24, C=float(np.log2(24)), mode=mode,
                         success_mean=mu, success_std=sd,
                         n_seeds=N_SEEDS, scramble=True))
        print(f"   ABLATION {mode}: {mu:.3f}", flush=True)

    old = json.load(open(RESULTS)) if os.path.exists(RESULTS) else []
    old = [r for r in old if not (r["N"] == cfg["N"] and r["m"] == cfg["m"]
                                  and r["K"] == cfg["K"])]
    json.dump(old + rows, open(RESULTS, "w"), indent=1)
    print(f"[{i}] done in {time.time()-t0:.1f}s", flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]))
