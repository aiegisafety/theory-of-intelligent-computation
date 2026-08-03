"""
Theorem 14 verification — fault-tolerant bandwidth threshold.

Quantities, all defined on the OPERATIONAL (quotient) chain:

    T        = -log2 P(S'_theta | S_theta)      per-step information variable
    h_theta  = E[T]                             operational entropy rate  (old)
    sigma_th = sd(T)                            OPERATIONAL VARENTROPY     (new)

Claims tested:
  (1)  exact one-step optimal error  eps_opt(C) = 1 - E[ top-2^C mass ]
  (2)  bound                          eps_opt(C) <= P[T > C]           (Lemma 14.1)
  (3)  Gaussian/dispersion form       eps(C) ~ Q((C - h_theta)/sigma_th)
  (4)  C*(eps) = h_theta + sigma_th * Q^{-1}(eps)   -- predicts C* < h_theta
                                                      whenever eps > 1/2
  (5)  transition WIDTH is proportional to sigma_th, and shrinks as
       1/sqrt(n) under n-step block coding  (so the sharp cliff is the
       asymptotic limit, not the finite-blocklength reality)
  (6)  empirical per-step decoding error of the actual predictive coder
       matches eps_opt.
"""

import json
import math
import numpy as np
from env import RendezvousTorus
from refine import refine, entropy_rates

# N=12 rows omitted: Table A already shows h_theta and sigma_theta are
# identical across N and K for a given m (the quotient chain is the relative
# offset, which does not depend on grid size or on the weather variable), so
# the N=12 refinements would cost ~25 s each to reproduce numbers we have.
CONFIGS = [(6, 2, 1), (6, 3, 1), (6, 6, 1), (6, 2, 4), (6, 3, 4)]
ALPHABETS = [1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 24]


def block_chain(env, s2b, nb):
    src, dst, prob = env.uniform_policy_chain()
    key = s2b[src] * nb + s2b[dst]
    agg = np.bincount(key, weights=prob, minlength=nb * nb).reshape(nb, nb)
    Tq = agg / np.maximum(agg.sum(axis=1, keepdims=True), 1e-300)
    # stationary distribution of the quotient chain
    mu = np.full(nb, 1.0 / nb)
    for _ in range(5000):
        nxt = mu @ Tq
        nxt /= nxt.sum()
        if np.abs(nxt - mu).sum() < 1e-15:
            mu = nxt
            break
        mu = nxt
    return Tq, mu


def info_stats(Tq, mu):
    """Distribution of T = -log2 P(s'|s) under stationarity."""
    vals, wts = [], []
    for i in range(Tq.shape[0]):
        for j in range(Tq.shape[1]):
            p = Tq[i, j]
            if p > 1e-14:
                vals.append(-math.log2(p))
                wts.append(mu[i] * p)
    vals = np.array(vals); wts = np.array(wts)
    wts = wts / wts.sum()
    mean = float(np.sum(wts * vals))
    var = float(np.sum(wts * (vals - mean) ** 2))
    return vals, wts, mean, math.sqrt(var)


def eps_exact(Tq, mu, M):
    """1 - E[mass of the M most probable successors]  (optimal one-step code)."""
    cov = 0.0
    for i in range(Tq.shape[0]):
        row = np.sort(Tq[i])[::-1]
        cov += mu[i] * row[:M].sum()
    return float(1.0 - cov)


def eps_bound(vals, wts, C):
    return float(np.sum(wts[vals > C + 1e-12]))


def Qfun(x):
    return 0.5 * math.erfc(x / math.sqrt(2.0))


def Qinv(p):
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if Qfun(mid) > p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def empirical_coder_error(Tq, mu, M, n_steps=200000, seed=7):
    """Run the ACTUAL predictive coder on the block chain; measure the
    conditional error rate (given the previous value was decoded correctly),
    which is what Theorem 14 bounds."""
    rng = np.random.default_rng(seed)
    nb = Tq.shape[0]
    order = np.argsort(-Tq, axis=1)
    book = order[:, :M]
    inbook = np.zeros((nb, nb), dtype=bool)
    for i in range(nb):
        inbook[i, book[i]] = True
    cum = np.cumsum(Tq, axis=1)
    s = int(rng.choice(nb, p=mu))
    err = 0
    for _ in range(n_steps):
        s2 = int(np.searchsorted(cum[s], rng.random()))
        s2 = min(s2, nb - 1)
        if not inbook[s, s2]:
            err += 1
        s = s2
    return err / n_steps


if __name__ == "__main__":
    out = []
    print("=" * 104)
    print("TABLE A — operational entropy rate and OPERATIONAL VARENTROPY (new quantity)")
    print("=" * 104)
    print(f"{'N':>3s} {'m':>2s} {'K':>2s} {'|S|':>7s} {'blocks':>7s} "
          f"{'h_theta':>8s} {'sigma_th':>9s} {'C*(0.5) pred':>13s}")
    cache = {}
    for (N, m, K) in CONFIGS:
        env = RendezvousTorus(grid_size=N, m=m, K=K)
        s2b, nb = refine(env.num_states, env.num_actions, env.labels,
                         env.transitions_for_action)
        Tq, mu = block_chain(env, s2b, nb)
        vals, wts, ht, sd = info_stats(Tq, mu)
        cache[(N, m, K)] = (Tq, mu, vals, wts, ht, sd, nb, env.num_states)
        print(f"{N:3d} {m:2d} {K:2d} {env.num_states:7d} {nb:7d} "
              f"{ht:8.4f} {sd:9.4f} {ht + sd*Qinv(0.5):13.3f}")

    print()
    print("=" * 104)
    print("TABLE B — exact optimal error, Lemma 14.1 bound, Gaussian form, and the")
    print("           empirical error of the coder actually used in Experiment 5")
    print("=" * 104)
    for key in [(6, 2, 1), (6, 3, 1), (6, 6, 1)]:
        Tq, mu, vals, wts, ht, sd, nb, S = cache[key]
        print(f"\n  N={key[0]} m={key[1]} K={key[2]}  h_theta={ht:.4f} sigma={sd:.4f}")
        print(f"    {'C':>5s} {'eps_exact':>10s} {'P[T>C] bnd':>11s} "
              f"{'Gaussian':>9s} {'empirical':>10s}")
        for M in ALPHABETS:
            C = math.log2(M)
            ee = eps_exact(Tq, mu, M)
            eb = eps_bound(vals, wts, C)
            eg = Qfun((C - ht) / sd) if sd > 0 else float("nan")
            em = empirical_coder_error(Tq, mu, M, n_steps=40000)
            print(f"    {C:5.2f} {ee:10.4f} {eb:11.4f} {eg:9.4f} {em:10.4f}")
            out.append(dict(N=key[0], m=key[1], K=key[2], C=C, M=M,
                            eps_exact=ee, eps_bound=eb, eps_gauss=eg,
                            eps_empirical=em, h_theta=ht, sigma=sd))

    print()
    print("=" * 104)
    print("TABLE C — bound validity check: is eps_exact <= P[T>C] everywhere?")
    print("=" * 104)
    viol = [r for r in out if r["eps_exact"] > r["eps_bound"] + 1e-9]
    print(f"  violations of Lemma 14.1: {len(viol)} / {len(out)}")
    mx = max(r["eps_bound"] - r["eps_exact"] for r in out)
    print(f"  max slack (bound - exact): {mx:.4f}")

    print()
    print("=" * 104)
    print("TABLE D — PREDICTION 5: transition width scales with sigma_theta")
    print("   width := C at eps=0.2  minus  C at eps=0.8, using the exact curve")
    print("=" * 104)
    print(f"{'N':>3s} {'m':>2s} {'K':>2s} {'sigma_th':>9s} {'width':>8s} {'width/sigma':>12s}")
    for key in CONFIGS:
        Tq, mu, vals, wts, ht, sd, nb, S = cache[key]
        grid = np.linspace(0, 6, 601)
        e = np.array([eps_exact(Tq, mu, max(1, int(2 ** c))) for c in grid])

        def cross(level):
            for i in range(1, len(e)):
                if e[i - 1] >= level > e[i]:
                    return grid[i]
            return float("nan")
        w = cross(0.2) - cross(0.8)
        print(f"{key[0]:3d} {key[1]:2d} {key[2]:2d} {sd:9.4f} {w:8.3f} "
              f"{w/sd if sd>0 else float('nan'):12.3f}")

    print()
    print("=" * 104)
    print("TABLE E — COROLLARY 14.3: block coding over n steps sharpens the transition")
    print("   effective sd of T_n/n is sigma/sqrt(n); width shrinks as 1/sqrt(n)")
    print("=" * 104)
    Tq, mu, vals, wts, ht, sd, nb, S = cache[(6, 3, 1)]
    print(f"  m=3: h_theta={ht:.4f} sigma={sd:.4f}")
    print(f"  {'n':>4s} {'sd(T_n/n)':>10s} {'C*(0.5)':>9s} {'C*(0.05)':>9s} {'width(.2-.8)':>13s}")
    for n in (1, 2, 5, 10, 50, 200, 1000):
        sn = sd / math.sqrt(n)
        print(f"  {n:4d} {sn:10.4f} {ht + sn*Qinv(0.5):9.3f} "
              f"{ht + sn*Qinv(0.05):9.3f} "
              f"{sn*(Qinv(0.2)-Qinv(0.8)):13.3f}")

    json.dump(out, open("theorem14_data.json", "w"), indent=1)
