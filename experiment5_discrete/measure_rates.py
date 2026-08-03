"""Measure h and h_theta for every configuration in the sweep."""
import json
import numpy as np
from env import RendezvousTorus
from refine import refine, entropy_rates

CONFIGS = []
for m in (2, 3, 6):
    CONFIGS.append(dict(N=6, m=m, K=1))
for m in (2, 3, 6):
    CONFIGS.append(dict(N=6, m=m, K=4))     # scale axis B: +2 bits of h
for m in (2, 3, 6):
    CONFIGS.append(dict(N=12, m=m, K=1))    # scale axis A: 16x the states

if __name__ == "__main__":
    out = []
    for cfg in CONFIGS:
        env = RendezvousTorus(grid_size=cfg["N"], m=cfg["m"], K=cfg["K"])
        s2b, nb = refine(env.num_states, env.num_actions, env.labels,
                         env.transitions_for_action)
        chain = env.uniform_policy_chain()
        h, h_th, mu, mu_q = entropy_rates(env.num_states, s2b, nb, chain)
        rec = dict(**cfg, num_states=int(env.num_states), n_blocks=int(nb),
                   h=h, h_theta=h_th)
        out.append(rec)
        print(f"N={cfg['N']:2d} m={cfg['m']} K={cfg['K']}  "
              f"|S|={env.num_states:6d}  blocks={nb:3d}  "
              f"h={h:.4f}  h_theta={h_th:.4f}  ratio={h_th/h:.3f}", flush=True)
        np.save(f"s2b_N{cfg['N']}_m{cfg['m']}_K{cfg['K']}.npy", s2b)
    json.dump(out, open("rates.json", "w"), indent=2)
