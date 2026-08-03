"""
Two tests that the symmetric torus could not support.

TEST 1 — autocovariance.  Is sd(T_n/n) = sigma_theta/sqrt(n)?
   On the torus this held EXACTLY, but only because T was i.i.d. there.  Here
   the quotient kernel has 10-21 distinct row shapes, so the information
   sequence is genuinely dependent and the autocovariance terms in
       Var(T_n) = n*Var(T) + 2*sum_{k<n} (n-k) Cov(T_1, T_{1+k})
   are non-zero.  Reported as the ratio  sd(T_n/n) / (sigma_theta/sqrt(n)):
   1.000 would mean i.i.d., anything else measures the correction.

TEST 2 — width vs sigma_theta.  Corollary 14.2 says the transition band scales
   with sigma_theta.  On the torus this was untestable (staircase; 4 of 5
   configs landed on the same step).  Here the quotient has 16-36 blocks, and
   the terrain contrast gives an independent handle on sigma_theta.
"""
import json
import math
import numpy as np
from env_asym import AsymTerrain
from refine import refine
from theorem14 import block_chain, info_stats, eps_exact
from corollary14_3 import trajectory_distribution, eps_curve, cross, tn_stats


def build(m, p_lo, p_hi, p_noise=0.15, drag=0.0):
    env = AsymTerrain(Nx=12, Ny=4, m=m, K=1, p_lo=p_lo, p_hi=p_hi,
                      p_noise=p_noise, drag=drag)
    s2b, nb = refine(env.num_states, env.num_actions, env.labels,
                     env.transitions_for_action)
    P, mu = block_chain(env, s2b, nb)
    _, _, ht, sg = info_stats(P, mu)
    shapes = len({tuple(np.round(np.sort(P[i])[::-1], 9)) for i in range(nb)})
    return env, P, mu, nb, ht, sg, shapes


if __name__ == "__main__":
    print("=" * 96)
    print("TEST 1 — autocovariance: does sd(T_n/n) = sigma_theta/sqrt(n) survive")
    print("          once the quotient rows are no longer permutations?")
    print("=" * 96)
    env, P, mu, nb, ht, sg, shapes = build(4, 0.05, 0.45)
    print(f"  m=4  |S|={env.num_states}  blocks={nb}  distinct row shapes={shapes}/{nb}")
    print(f"  h_theta={ht:.4f}  sigma_theta={sg:.4f}\n")
    print(f"  {'n':>3s} {'E[T_n/n]':>9s} {'sd(T_n/n)':>10s} {'sigma/sqrt(n)':>13s} "
          f"{'RATIO':>7s} {'implied Cov contrib':>20s}")
    rows1 = []
    for n in (1, 2, 3, 4):
        tp = trajectory_distribution(P, mu, n)
        mean_n, sd_n = tn_stats(tp, mu, n)
        iid = sg / math.sqrt(n)
        ratio = sd_n / iid
        # Var(T_n) = n s^2 (1 + corr);  corr = ratio^2 - 1
        print(f"  {n:3d} {mean_n:9.4f} {sd_n:10.4f} {iid:13.4f} {ratio:7.4f} "
              f"{ratio**2 - 1:+20.4f}")
        rows1.append(dict(n=n, sd=sd_n, iid=iid, ratio=ratio))

    print("\n  (torus reference: this ratio was 1.0000 at every n)")

    print()
    print("=" * 96)
    print("TEST 2 — transition width vs sigma_theta, on a 16-36 block quotient")
    print("=" * 96)
    print("  NOTE: the exact-code curve is a staircase that need not span")
    print("  [0.2, 0.8], so the width is measured on the INFORMATION-TAIL curve")
    print("  Pr[T > C] -- which section 11 established is the object the")
    print("  Gaussian law actually describes.  Quantity reported: the 20-80")
    print("  quantile width of T, divided by sigma_theta.  Gaussian => 1.683.")
    print()
    print(f"  {'m':>2s} {'drag':>5s} {'p_hi':>5s} {'blocks':>7s} {'shapes':>7s} "
          f"{'h_theta':>8s} {'sigma':>7s} {'W_tail':>8s} {'W/sigma':>8s}")
    rows2 = []
    for (m, lo, hi, dg) in [(4, 0.05, 0.45, 0.0), (4, 0.05, 0.45, 0.2),
                            (4, 0.05, 0.45, 0.4), (4, 0.05, 0.45, 0.6),
                            (4, 0.02, 0.60, 0.5), (6, 0.05, 0.45, 0.0),
                            (6, 0.05, 0.45, 0.3), (6, 0.05, 0.45, 0.6)]:
        env, P, mu, nb, ht, sg, shapes = build(m, lo, hi, 0.15, dg)
        vals, wts = [], []
        for i in range(nb):
            for j in range(nb):
                if P[i, j] > 1e-14:
                    vals.append(-math.log2(P[i, j])); wts.append(mu[i] * P[i, j])
        v = np.array(vals); w = np.array(wts); w = w / w.sum()
        o = np.argsort(v); v, w = v[o], w[o]
        cw = np.cumsum(w)
        W = float(np.interp(0.8, cw, v) - np.interp(0.2, cw, v))
        print(f"  {m:2d} {dg:5.2f} {hi:5.2f} {nb:7d} {shapes:7d} {ht:8.4f} "
              f"{sg:7.4f} {W:8.4f} {W/sg:8.4f}")
        rows2.append(dict(m=m, drag=dg, p_hi=hi, n_blocks=nb, shapes=shapes,
                          h_theta=ht, sigma=sg, W=W, ratio=W / sg))

    r = np.array([x["ratio"] for x in rows2])
    s = np.array([x["sigma"] for x in rows2])
    w = np.array([x["W"] for x in rows2])
    print(f"\n  W/sigma across configs: mean={r.mean():.3f}  sd={r.std():.3f}  "
          f"relative spread={r.std()/r.mean():.1%}")
    if len(set(np.round(s, 4))) > 1:
        b, a = np.polyfit(np.log(s), np.log(w), 1)
        print(f"  fit  log W = a + b log sigma :  b = {b:.3f}  "
              f"(Corollary 14.2 predicts b = 1)")
        print(f"  sigma range across configs: {s.min():.4f} - {s.max():.4f} "
              f"({s.max()/s.min():.2f}x)")

    json.dump(dict(test1=rows1, test2=rows2), open("test_asym.json", "w"),
              indent=1)
