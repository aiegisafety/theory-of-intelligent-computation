"""
Corollary 14.3 verification — does n-step block coding narrow the transition
band as 1/sqrt(n)?

This is the one prediction of Theorem 14 that was still untested, and it is the
prediction that reconciles the falsified sharp threshold: the cliff at C = h_theta
is the n -> infinity limit, and a per-step agent (n = 1) necessarily sees a band
of width ~ sigma_theta.

What is computed EXACTLY (no sampling):

  * the joint distribution of n-step operational trajectories given the previous
    decoded value, by iterated outer product over the quotient kernel;
  * the optimal n-step code error
        eps_n(C) = 1 - E_b[ mass of the top-2^{nC} trajectories ],
    which is the n-step analogue of Theorem 14(a);
  * the transition width  W(n) := C(eps=0.2) - C(eps=0.8);
  * the ACTUAL sd of T_n / n, compared against the i.i.d. approximation
    sigma_theta / sqrt(n).  For a Markov chain the varentropy of T_n carries
    autocovariance terms, so this approximation is NOT guaranteed -- checking it
    is part of the test, not an assumption.

Note this also repairs the discretisation failure that defeated the width test
in theorem14.py: with n-step coding, M ranges over many integers and
C = log2(M)/n becomes finely spaced.
"""

import json
import math
import numpy as np
from env import RendezvousTorus
from refine import refine
from theorem14 import block_chain, info_stats


def trajectory_distribution(P, mu, n):
    """Exact distribution over n-step trajectories.

    Returns (probs, weights) where probs[b] is an array over nb^n trajectories
    of P(traj | start=b), and weights[b] = mu[b].
    """
    nb = P.shape[0]
    out = []
    for b in range(nb):
        probs = P[b].copy()                 # after 1 step, indexed by s_1
        last = np.arange(nb)
        for _ in range(n - 1):
            probs = (probs[:, None] * P[last, :]).ravel()
            last = np.tile(np.arange(nb), len(last))
        out.append(probs)
    return out


def eps_curve(traj_probs, mu, n, nb):
    """eps_n(C) for every attainable alphabet size M, returned as (C, eps)."""
    sorted_desc = [np.sort(p)[::-1] for p in traj_probs]
    cums = [np.cumsum(s) for s in sorted_desc]
    total = nb ** n
    # sample M on a log grid to keep the curve cheap but dense in C
    Ms = np.unique(np.round(np.logspace(0, math.log10(total), 400)).astype(int))
    Ms = Ms[(Ms >= 1) & (Ms <= total)]
    Cs, eps = [], []
    for M in Ms:
        cov = sum(mu[b] * cums[b][min(M, len(cums[b])) - 1] for b in range(nb))
        Cs.append(math.log2(M) / n)
        eps.append(1.0 - cov)
    return np.array(Cs), np.array(eps)


def cross(Cs, eps, level):
    """C at which eps crosses `level` (eps is decreasing in C)."""
    for i in range(1, len(eps)):
        if eps[i - 1] >= level > eps[i]:
            d = eps[i - 1] - eps[i]
            t = (eps[i - 1] - level) / d if d > 0 else 0.0
            return Cs[i - 1] + t * (Cs[i] - Cs[i - 1])
    return float("nan")


def tn_stats(traj_probs, mu, n):
    """Exact mean and sd of T_n / n, where T_n = -log2 P(trajectory)."""
    vals, wts = [], []
    for b, p in enumerate(traj_probs):
        nz = p > 1e-300
        vals.append(-np.log2(p[nz]) / n)
        wts.append(mu[b] * p[nz])
    v = np.concatenate(vals); w = np.concatenate(wts)
    w = w / w.sum()
    mean = float(np.sum(w * v))
    sd = float(math.sqrt(np.sum(w * (v - mean) ** 2)))
    return mean, sd


def run(m, n_list):
    env = RendezvousTorus(grid_size=6, m=m, K=1)
    s2b, nb = refine(env.num_states, env.num_actions, env.labels,
                     env.transitions_for_action)
    P, mu = block_chain(env, s2b, nb)
    _, _, h_theta, sigma = info_stats(P, mu)

    print(f"\n{'='*100}")
    print(f"m={m}  blocks={nb}  h_theta={h_theta:.4f}  sigma_theta={sigma:.4f}")
    print(f"{'='*100}")
    print(f"{'n':>3s} {'E[T_n/n]':>9s} {'sd(T_n/n)':>10s} {'sigma/sqrt(n)':>13s} "
          f"{'ratio':>6s} {'C*(0.5)':>8s} {'width W(n)':>11s} "
          f"{'W*sqrt(n)':>10s} {'W/(1.683s/sqrt n)':>18s}")
    rows = []
    for n in n_list:
        tp = trajectory_distribution(P, mu, n)
        mean_n, sd_n = tn_stats(tp, mu, n)
        Cs, eps = eps_curve(tp, mu, n, nb)
        c50 = cross(Cs, eps, 0.5)
        W = cross(Cs, eps, 0.2) - cross(Cs, eps, 0.8)
        pred_W = 1.683 * sigma / math.sqrt(n)      # (Q^-1(.2)-Q^-1(.8)) = 1.683
        print(f"{n:3d} {mean_n:9.4f} {sd_n:10.4f} {sigma/math.sqrt(n):13.4f} "
              f"{sd_n/(sigma/math.sqrt(n)):6.3f} {c50:8.3f} {W:11.4f} "
              f"{W*math.sqrt(n):10.4f} {W/pred_W:18.3f}")
        rows.append(dict(m=m, n=n, mean=mean_n, sd=sd_n, sigma=sigma,
                         h_theta=h_theta, C50=c50, width=W))
    return rows


if __name__ == "__main__":
    allrows = []
    allrows += run(2, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    allrows += run(3, [1, 2, 3, 4, 5, 6])

    print(f"\n{'='*100}")
    print("SCALING TEST — fit log W(n) = a - b log n ;  Corollary 14.3 predicts b = 0.5")
    print("   GLOBAL fit is contaminated by the small-n transient, so LOCAL")
    print("   exponents between consecutive n are reported as well: the question")
    print("   is whether they are DRIFTING TOWARD 0.5, not whether the global fit is 0.5.")
    print(f"{'='*100}")
    for m in (2, 3):
        r = [x for x in allrows if x["m"] == m and np.isfinite(x["width"])
             and x["width"] > 0]
        ln = np.log([x["n"] for x in r]); lw = np.log([x["width"] for x in r])
        b, a = np.polyfit(ln, lw, 1)
        resid = lw - (a + b * ln)
        print(f"\n  m={m}: GLOBAL exponent b = {-b:.4f}  (predicted 0.5)  "
              f"R^2 = {1 - resid.var()/lw.var():.4f}")
        loc = []
        for i in range(1, len(r)):
            e = -(lw[i] - lw[i - 1]) / (ln[i] - ln[i - 1])
            loc.append((r[i - 1]["n"], r[i]["n"], e))
        print("       local: " + "  ".join(f"{a_}->{b_}:{e:.3f}" for a_, b_, e in loc))
        sig = r[0]["sigma"]
        print(f"       W*sqrt(n) should converge to 1.683*sigma = {1.683*sig:.4f}; "
              f"observed at largest n: {r[-1]['width']*math.sqrt(r[-1]['n']):.4f}")

    print(f"\n{'='*100}")
    print("THRESHOLD CONVERGENCE — C*(0.5) should approach h_theta as n grows")
    print(f"{'='*100}")
    for m in (2, 3):
        r = [x for x in allrows if x["m"] == m]
        ht = r[0]["h_theta"]
        print(f"  m={m} (h_theta={ht:.4f}): " +
              "  ".join(f"n={x['n']}:{x['C50']:.3f}" for x in r))

    json.dump(allrows, open("corollary14_3.json", "w"), indent=1)
