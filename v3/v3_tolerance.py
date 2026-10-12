"""V3 §8.1: soundness and conservatism of Theorem 8.2, order dependence of Definition 8.1,
and the separation Delta* measured against the final abstraction (same goal label only)."""
import numpy as np

K, COPIES = 6, 4
N = K * COPIES


def make_env(rng):
    Q = rng.dirichlet([0.6] * K, size=K)                 # quotient kernel
    cls = np.repeat(np.arange(K), COPIES)
    P = np.zeros((N, N))
    for s in range(N):
        for d in range(K):
            P[s, cls == d] = Q[cls[s], d] * rng.dirichlet([1.0] * COPIES)
    goal = (cls >= K // 2).astype(int)                  # coarse two-valued goal
    return P, goal, cls


def block_rows(P, part):
    B = sorted(set(part)); return np.stack([P[:, part == b].sum(1) for b in B], 1)


def tv(x, y): return 0.5 * np.abs(x - y).sum()


def exact_refine(P, goal):
    part = goal.copy(); hist = [part.copy()]
    while True:
        R = block_rows(P, part); new = -np.ones(N, int); keys = {}
        for s in range(N):
            k = (part[s],) + tuple(np.round(R[s], 9))
            new[s] = keys.setdefault(k, len(keys))
        if len(set(new)) == len(set(part)): return part, hist
        part = new; hist.append(part.copy())


def margins(P, goal, final, hist):
    D = np.inf                                              # Delta of Theorem 8.2
    for n in range(len(hist) - 1):
        R = block_rows(P, hist[n])
        for s in range(N):
            for t in range(s + 1, N):
                if hist[n][s] == hist[n][t] and hist[n + 1][s] != hist[n + 1][t]:
                    D = min(D, tv(R[s], R[t]))
    R = block_rows(P, final); Ds = np.inf                   # Delta*: same goal label, different final block
    for s in range(N):
        for t in range(s + 1, N):
            if goal[s] == goal[t] and final[s] != final[t]:
                Ds = min(Ds, tv(R[s], R[t]))
    return D, Ds


def eps_refine(Phat, goal, eps, order):
    part = goal.copy()
    for _ in range(N):
        R = block_rows(Phat, part); new = -np.ones(N, int); nb = 0
        for b in sorted(set(part)):
            reps = []
            for s in [x for x in order if part[x] == b]:
                for r, lab in reps:
                    if tv(R[s], R[r]) <= eps: new[s] = lab; break
                else:
                    reps.append((s, nb)); new[s] = nb; nb += 1
        if nb == len(set(part)): return new
        part = new
    return part


def overmerge(learned, final):
    bad = tot = 0
    for s in range(N):
        for t in range(s + 1, N):
            if final[s] != final[t]:
                tot += 1; bad += learned[s] == learned[t]
    return bad / tot


def limit(P, goal, final, order, grid):
    for e in grid:
        if overmerge(eps_refine(P, goal, e, order), final) > 0: return e
    return np.inf


def sample(P, n, rng):
    return np.stack([rng.multinomial(n, P[s]) / n for s in range(N)])


if __name__ == "__main__":
    rng = np.random.default_rng(42); grid = np.round(np.arange(0.005, 1.0, 0.005), 3)
    rows = []
    for e in range(40):
        P, goal, cls = make_env(rng)
        final, hist = exact_refine(P, goal)
        assert len(set(final)) == K
        D, Ds = margins(P, goal, final, hist)
        lim = limit(P, goal, final, np.arange(N), grid)
        rows.append((D, Ds, lim))
    D = np.array([r[0] for r in rows]); Ds = np.array([r[1] for r in rows]); L = np.array([r[2] for r in rows])
    print("40 envs, exact kernels, natural order:")
    print("  limit >= Delta/2 in %d/40;  limit/(Delta/2): median %.1f range %.1f-%.1f" %
          ((L >= D / 2).sum(), np.median(L / (D / 2)), (L / (D / 2)).min(), (L / (D / 2)).max()))
    print("  Delta <= Delta* in %d/40;  Delta*/Delta median %.2f" % ((D <= Ds + 1e-12).sum(), np.median(Ds / D)))
    print("  limit >= Delta*/2 in %d/40;  corr(limit,Delta)=%.2f corr(limit,Delta*)=%.2f" %
          ((L >= Ds / 2).sum(), np.corrcoef(L, D)[0, 1], np.corrcoef(L, Ds)[0, 1]))
    # order dependence in one environment, exact kernels
    P, goal, cls = make_env(np.random.default_rng(5)); final, hist = exact_refine(P, goal)
    lims = [limit(P, goal, final, np.random.default_rng(o).permutation(N), grid) for o in range(25)]
    print("order dependence (one env, exact kernels, 25 orders): limit %.3f-%.3f, ratio %.2f" %
          (min(lims), max(lims), max(lims) / min(lims)))
    # Delta* rule with sampling noise, 16 envs
    srng = np.random.default_rng(9); res = {}
    envs = []
    for e in range(16):
        P, goal, cls = make_env(srng); final, hist = exact_refine(P, goal); envs.append((P, goal, final, margins(P, goal, final, hist)[1]))
    for f in (0.5, 0.8, 1.2, 1.6):
        for n in (200, 5000):
            om = [overmerge(eps_refine(sample(P, n, srng), goal, f * Ds, np.arange(N)), final) for P, goal, final, Ds in envs]
            res[(f, n)] = (np.mean(om), sum(o == 0 for o in om))
        print("eps=%.1f Delta*: over-merge n=200 %.3f, n=5000 %.3f, clean at n=5000 %d/16, clean at n=200 %d/16" %
              (f, res[(f, 200)][0], res[(f, 5000)][0], res[(f, 5000)][1], res[(f, 200)][1]))
