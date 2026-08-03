"""
Experiment 7, exact part — does the RATE REQUIREMENT shift by exactly h_A?

Theorem 11 is a statement about rate, not about task success.  Measuring it
through task success turned out to be confounded: ontology drift also makes the
task intrinsically harder to SUSTAIN (the target moves while the agents are
trying to hold a rendezvous for HOLD steps), so the achievable ceiling falls
from 0.68 to 0.49 and the 0.5-crossing drifts right for a reason that has
nothing to do with bandwidth.  That is the same difficulty confound that voided
the m=6 row in Experiment 5.

So the rate requirement is measured directly and EXACTLY, with no simulation
and no seeds, using Theorem 14(a) on the quotient chain:

        eps_opt(C) = 1 - E_b[ mass of the top-2^C successors of b ]

and C*(eps) := the capacity at which eps_opt reaches a fixed tolerance eps.

Prediction:  d C*(eps) / d h_A = 1, at every fixed eps.
"""

import json
import math
import numpy as np
from env_drift import RendezvousDrift
from refine import refine
from theorem14 import block_chain, info_stats, eps_exact

P_LIST = [0.0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30]
LEVELS = [0.5, 0.3, 0.2, 0.1]


def curve(P, mu, nb):
    Cs, es = [], []
    for M in range(1, nb + 1):
        Cs.append(math.log2(M))
        es.append(eps_exact(P, mu, M))
    return np.array(Cs), np.array(es)


def cross(Cs, es, level):
    for i in range(1, len(es)):
        if es[i - 1] > level >= es[i]:
            d = es[i - 1] - es[i]
            t = (es[i - 1] - level) / d if d else 0.0
            return float(Cs[i - 1] + t * (Cs[i] - Cs[i - 1]))
    return float("nan")


if __name__ == "__main__":
    rows = []
    print("=" * 100)
    print("TABLE A — the quotient absorbs the ontology; h_theta splits additively")
    print("=" * 100)
    print(f"{'p_drift':>8s} {'blocks':>7s} {'h_A':>8s} {'h_theta':>9s} "
          f"{'h_theta - h_A':>14s} {'sigma':>8s}")
    for p in P_LIST:
        env = RendezvousDrift(grid_size=6, m=3, p_drift=p)
        s2b, nb = refine(env.num_states, env.num_actions, env.labels,
                         env.transitions_for_action)
        P, mu = block_chain(env, s2b, nb)
        _, _, ht, sg = info_stats(P, mu)
        hA = env.h_A()
        Cs, es = curve(P, mu, nb)
        rows.append(dict(p=p, nb=int(nb), hA=hA, h_theta=ht, sigma=sg,
                         Cs=Cs.tolist(), es=es.tolist(),
                         Cstar={str(L): cross(Cs, es, L) for L in LEVELS}))
        print(f"{p:8.2f} {nb:7d} {hA:8.4f} {ht:9.4f} {ht - hA:14.4f} {sg:8.4f}",
              flush=True)

    print()
    print("=" * 100)
    print("TABLE B — C*(eps) versus h_A.  Theorem 11 predicts slope 1.")
    print("   (p=0 excluded from the fits: with no drift the ontology variable")
    print("    is constant and leaves the quotient entirely, 27 blocks -> 9,")
    print("    so it is a different chain rather than the same chain at h_A=0.)")
    print("=" * 100)
    hdr = "  ".join(f"C*({L})" for L in LEVELS)
    print(f"{'p':>6s} {'h_A':>8s}   {hdr}")
    for r in rows:
        print(f"{r['p']:6.2f} {r['hA']:8.4f}   " +
              "  ".join(f"{r['Cstar'][str(L)]:7.3f}" for L in LEVELS))

    print()
    drift = [r for r in rows if r["p"] > 0]
    hA = np.array([r["hA"] for r in drift])
    print(f"{'level':>7s} {'slope dC*/dh_A':>15s} {'intercept':>10s} {'R^2':>7s}")
    for L in LEVELS:
        y = np.array([r["Cstar"][str(L)] for r in drift])
        ok = np.isfinite(y)
        b, a = np.polyfit(hA[ok], y[ok], 1)
        pred = a + b * hA[ok]
        r2 = 1 - ((y[ok] - pred) ** 2).sum() / ((y[ok] - y[ok].mean()) ** 2).sum()
        print(f"{L:7.2f} {b:15.4f} {a:10.4f} {r2:7.4f}")

    print()
    print("  (a slope of 1 means every bit of ontology drift costs exactly one")
    print("   bit of channel capacity, which is the content of C >= h_theta + h_A)")

    json.dump(rows, open("drift_exact.json", "w"), indent=1)
