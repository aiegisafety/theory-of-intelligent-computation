"""
Theorem 14, closed loop: predict C* from task structure ALONE, then compare to
the C* measured in Experiment 5.

Chain of reasoning being tested end to end:

  task structure (needs L error-free consecutive operational steps,
                  ~T/L independent attempts per episode)
        -> tolerated per-step tracking error   eps_task
        -> Theorem 14 exact curve  eps_opt(C)
        -> predicted capacity threshold        C*_pred
        -> compare against measured C* from the sweep.

Nothing here is fitted to the sweep: L=6 and T=60 are the task definition, and
eps_opt comes from the quotient kernel.
"""
import json
import math
import numpy as np
from env import RendezvousTorus
from refine import refine
from theorem14 import block_chain, info_stats, eps_exact

L = 6      # HOLD, from simulate.py
T = 60     # T_STEPS, from simulate.py
TARGET = 0.5

MEASURED = {   # C* from analysis_output.txt (class-aware, 0.5 crossing)
    (6, 2, 1): 1.20, (6, 3, 1): 1.96,
    (6, 2, 4): 1.25, (6, 3, 4): 1.95,
    (12, 2, 1): 1.25, (12, 3, 1): 2.32,
}


def eps_task(L, T, target):
    """Per-step tracking-error rate the task can absorb and still succeed at
    `target`.  Model: an episode offers ~T/L independent chances at a run of L
    error-free steps."""
    tries = T / L
    #  target = 1 - (1 - (1-eps)^L)^tries
    inner = 1.0 - (1.0 - target) ** (1.0 / tries)   # = (1-eps)^L
    return 1.0 - inner ** (1.0 / L)


def invert_eps(Tq, mu, target_eps):
    """Smallest C with eps_opt(C) <= target_eps, linearly interpolated across
    the staircase in M."""
    prev_C, prev_e = None, None
    for M in range(1, Tq.shape[0] + 2):
        C = math.log2(M)
        e = eps_exact(Tq, mu, M)
        if prev_e is not None and prev_e > target_eps >= e:
            if prev_e == e:
                return C
            t = (prev_e - target_eps) / (prev_e - e)
            return prev_C + t * (C - prev_C)
        prev_C, prev_e = C, e
    return float("nan")


if __name__ == "__main__":
    et = eps_task(L, T, TARGET)
    print("=" * 92)
    print("TABLE F — closed loop: task structure -> eps_task -> C*_pred -> vs measured")
    print("=" * 92)
    print(f"  task: needs L={L} consecutive error-free operational steps, "
          f"T={T} steps/episode")
    print(f"  => tolerated per-step tracking error  eps_task = {et:.4f}")
    print(f"  (nothing below is fitted to the sweep)\n")
    print(f"{'N':>3s} {'m':>2s} {'K':>2s} {'h_theta':>8s} {'C*_pred':>8s} "
          f"{'C*_meas':>8s} {'err':>7s} {'old pred (=h_th) err':>21s}")

    rows = []
    for (N, m, K), meas in MEASURED.items():
        base = (6, m, 1)   # quotient chain is invariant in N and K
        env = RendezvousTorus(grid_size=base[0], m=base[1], K=base[2])
        s2b, nb = refine(env.num_states, env.num_actions, env.labels,
                         env.transitions_for_action)
        Tq, mu = block_chain(env, s2b, nb)
        _, _, ht, sd = info_stats(Tq, mu)
        cp = invert_eps(Tq, mu, et)
        rows.append((N, m, K, ht, cp, meas))
        print(f"{N:3d} {m:2d} {K:2d} {ht:8.3f} {cp:8.2f} {meas:8.2f} "
              f"{cp-meas:+7.2f} {ht-meas:+21.2f}")

    e_new = np.array([abs(r[4] - r[5]) for r in rows])
    e_old = np.array([abs(r[3] - r[5]) for r in rows])
    print(f"\n  mean |error|, Theorem 14 prediction : {e_new.mean():.3f} bits")
    print(f"  mean |error|, old prediction C* = h_theta : {e_old.mean():.3f} bits")
    print(f"  improvement factor: {e_old.mean()/e_new.mean():.2f}x")
    print(f"\n  signed bias, Theorem 14 : {np.mean([r[4]-r[5] for r in rows]):+.3f}")
    print(f"  signed bias, old        : {np.mean([r[3]-r[5] for r in rows]):+.3f}")
    json.dump([dict(N=r[0], m=r[1], K=r[2], h_theta=r[3], C_pred=r[4],
                    C_meas=r[5]) for r in rows],
              open("theorem14_closeloop.json", "w"), indent=1)
