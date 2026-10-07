"""Clean ablation for Proposition 12.1: identical features, identical data,
identical readout; ONLY the action-conditioning of the goal prediction differs."""
import numpy as np
from env_cont import ContinuousRendezvous
from learn import (collect_rollouts, TorusRFF, ridge_fit, learn_abstraction,
                   psi, learn_readout, readout_offset, N_A)

def learn_averaged(env, S, H=5, n_feat=2500, seed=2):
    n_traj, T, d = S.shape
    goal = env.at_goal(S).astype(float)
    rff = TorusRFF(d, n_feat=n_feat, fmax=1, seed=seed)
    X = np.concatenate([S[:, t] for t in range(T - H)])
    Y = np.concatenate([np.stack([goal[:, t + h] for h in range(1, H + 1)], 1)
                        for t in range(T - H)])
    W = ridge_fit(rff(X), Y)
    return lambda Z: rff(Z) @ W

for n_irr in (0, 3):
    env = ContinuousRendezvous(n_irr=n_irr, sigma=0.05, delta=0.06)
    S, A1 = collect_rollouts(env, n_traj=600, T=30, seed=1)
    X = S.reshape(-1, env.dim); e = env.offset(X)
    out = []
    for name, fn in [("averaged", learn_averaged(env, S, n_feat=2500)),
                     ("conditioned", (lambda r, W: (lambda Z: psi(r, W, Z)))(*learn_abstraction(env, S, A1, H=5, n_feat=2500, seed=2)))]:
        R = fn(X)
        rf, W = learn_readout(env, X, R, seed=3)
        mae = np.abs((readout_offset(rf, W, R) - e + 0.5) % 1.0 - 0.5).mean()
        out.append("%s=%.4f" % (name, mae))
    print("d=%2d  readout MAE  %s   (chance level for uniform offset: 0.25)" % (env.dim, "  ".join(out)), flush=True)
