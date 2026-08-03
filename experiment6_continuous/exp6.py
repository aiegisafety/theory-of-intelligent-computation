"""
Experiment 6 — does the bandwidth law survive the continuum?

Three encoders, quantised at the SAME rate C = log2(M) bits/step, differing
only in WHAT is quantised:

  phys     the raw physical state vector, decoded with an EXACT ANALYTIC
           readout (the offset is computed from the decoded vector in closed
           form).  This deliberately gives the baseline the strongest possible
           decoder, so it cannot be said to lose because its readout was hard
           to learn.
  learned  psi(s), the LEARNED action-conditioned task abstraction, decoded
           with a LEARNED readout -- i.e. every approximation error counts
           AGAINST the hypothesis under test.
  oracle   the true offset e (upper bound).

PREDICTIONS
  P1  learned ~ oracle >> phys at matched C.
  P2  irrelevant dimensions must not move the learned/oracle threshold but
      must degrade phys (continuum form of Experiment 5's double dissociation).
  P3  the learned/oracle threshold sits near the ONE-dimensional rate
      R_theta(D) = 0.5 log2(sigma_e^2 / D), independent of physical dimension.

FALSIFICATION: if learned fails to separate from phys, or if its threshold
grows with the irrelevant dimension count, the abstraction machine does not
survive function approximation -- "tabular death" -- and it is reported as such.

Anti-trap rule #7 (channel ablation) is enforced for every configuration.
"""

import json
import sys
import numpy as np
from env_cont import ContinuousRendezvous
from learn import (collect_rollouts, learn_abstraction, psi, learn_readout,
                   readout_offset, Quantizer, CONTROLS, N_A)

HOLD = 4
T_STEPS = 40
GAIN = 0.9        # fraction of the estimated offset each agent closes per step


def build(env, seed=1):
    S, A1 = collect_rollouts(env, n_traj=600, T=30, seed=seed)
    nf = max(2500, 60 * env.dim)
    rff_a, Ws = learn_abstraction(env, S, A1, H=5, n_feat=nf, seed=seed + 1)
    X = S.reshape(-1, env.dim)

    packs = {}
    # --- physical: quantise the state vector, decode the offset ANALYTICALLY
    packs["phys"] = dict(rep=lambda Z: np.atleast_2d(Z),
                         dec=lambda R: env.offset(R),
                         train=X)
    # --- learned: quantise psi, decode with a learned readout
    P = psi(rff_a, Ws, X)
    rff_r, W_r = learn_readout(env, X, P, seed=seed + 2)
    packs["learned"] = dict(rep=lambda Z: psi(rff_a, Ws, np.atleast_2d(Z)),
                            dec=lambda R: readout_offset(rff_r, W_r, R),
                            train=P)
    # --- oracle: quantise the true offset
    E = env.offset(X).reshape(-1, 1)
    packs["opvar"] = dict(rep=lambda Z: env.offset(np.atleast_2d(Z)).reshape(-1, 1),
                           dec=lambda R: R[:, 0],
                           train=E)
    return packs


def evaluate(env, packs, name, M, n_seeds, scramble=False, seed=5000):
    """All episodes are run as one batch -- identical semantics to a per-seed
    loop, but vectorised so the sweep fits in the time budget."""
    rng = np.random.default_rng(seed)
    p = packs[name]
    q = p["quant"][M]

    s = env.sample_state(rng, n_seeds)
    bad = env.at_goal(s)
    while bad.any():                       # start every episode off-goal
        s[bad] = env.sample_state(rng, int(bad.sum()))
        bad = env.at_goal(s)

    streak = np.zeros(n_seeds, dtype=int)
    done = np.zeros(n_seeds, dtype=bool)
    for _ in range(T_STEPS):
        idx = q.encode(p["rep"](s))
        if scramble:
            idx = rng.integers(0, q.M, n_seeds)
        e_hat = p["dec"](q.decode(idx))
        # both agents close half the estimated offset from opposite sides;
        # e_hat is the ONLY channel-borne quantity entering the decision
        u = GAIN * 0.5 * np.asarray(e_hat)
        s = env.step(s, -u, +u, rng)
        at = env.at_goal(s)
        streak = np.where(at, streak + 1, 0)
        done |= streak >= HOLD
    return float(done.mean())


def main(n_irr, Ms, n_seeds=100, sigma=0.05, delta=0.06):
    env = ContinuousRendezvous(n_irr=n_irr, sigma=sigma, delta=delta)
    packs = build(env)
    for name in packs:
        packs[name]["quant"] = {M: Quantizer(M, seed=7).fit(packs[name]["train"])
                                for M in Ms}
    D = (delta / 2) ** 2
    print(f"=== n_irr={n_irr}  physical dim={env.dim}  "
          f"R_theta={env.R_theta(D):.2f}  R_phys={env.R_phys(D):.2f} bits/step ===",
          flush=True)
    print(f"  {'M':>4s} {'C':>5s} " + " ".join(f"{n:>9s}" for n in packs),
          flush=True)
    results = []
    for M in Ms:
        C = float(np.log2(M))
        row = {n: evaluate(env, packs, n, M, n_seeds) for n in packs}
        print(f"  {M:4d} {C:5.2f} " + " ".join(f"{row[n]:9.3f}" for n in packs),
              flush=True)
        for n in packs:
            results.append(dict(n_irr=n_irr, dim=env.dim, M=M, C=C, encoder=n,
                                success=row[n], scramble=False,
                                R_theta=env.R_theta(D), R_phys=env.R_phys(D)))
    abl = {n: evaluate(env, packs, n, max(Ms), n_seeds, scramble=True)
           for n in packs}
    print("  ABLATION: " + "  ".join(f"{n}={abl[n]:.3f}" for n in abl),
          flush=True)
    for n in packs:
        results.append(dict(n_irr=n_irr, dim=env.dim, M=max(Ms),
                            C=float(np.log2(max(Ms))), encoder=n,
                            success=abl[n], scramble=True,
                            R_theta=env.R_theta(D), R_phys=env.R_phys(D)))
    return results


if __name__ == "__main__":
    n_irr = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    res = main(n_irr, [2, 4, 8, 16, 32, 64])
    try:
        old = json.load(open("exp6_results.json"))
    except Exception:
        old = []
    old = [r for r in old if r["n_irr"] != n_irr]
    json.dump(old + res, open("exp6_results.json", "w"), indent=1)
