"""V3 §6.7: zero-delay converse D_theta(C), penalty Delta_theta (Def 6.12, Table 6.2), Prop 6.13 bound, Schur counterexample."""
import itertools, math, numpy as np
from chains import H, rate, stat, families, torus_m2, dirichlet, h_sigma_W
from fastpart import best_partition_entropy


def exact_best(p, M):
    p = [x for x in p if x > 0]; best = 0.0
    for lab in itertools.product(range(M), repeat=len(p)):
        c = [0.0] * M
        for x, l in zip(p, lab): c[l] += x
        best = max(best, H(c))
    return best


def D(T, C, mu):
    M = 2 ** C
    return sum(mu[b] * (H(T[b]) - best_partition_entropy(T[b], M)) for b in range(len(T)))


# each section has its own seed so that the sections are reproducible independently
rng = np.random.default_rng(1)
# 1. partition search vs exhaustive enumeration
err = 0.0; nbad = 0
for _ in range(400):
    n = int(rng.integers(3, 10)); a = float(rng.choice([0.2, 0.7, 2.0]))
    p = rng.dirichlet([a] * n); M = int(rng.choice([2, 3, 4]))
    d = exact_best(p, M) - best_partition_entropy(p, M); err = max(err, d); nbad += d > 1e-9
print("1. heuristic vs exhaustive, 400 rows with 3-9 successors: short in %d rows, max shortfall = %.1e bits" % (nbad, err), flush=True)

# 2. example chains
print("2. D_theta(C) on example chains", flush=True)
rng = np.random.default_rng(2)
ex = [("torus m=2", torus_m2()), ("dirichlet K=32 a=1", dirichlet(32, 1.0, rng)),
      ("dirichlet K=32 a=0.2", dirichlet(32, 0.2, rng))]
for name, T in ex:
    mu = stat(T); h = rate(T, mu)
    for C in (1, 2, 3):
        d = D(T, C, mu)
        print("   %-22s h=%.3f C=%d floor=%.3f D=%.3f Delta=%.3f" % (name, h, C, max(h - C, 0), d, d - max(h - C, 0)), flush=True)

# 3. penalty over 48 chains, C=1,2 ; regression on h, sigma
rows = []
for fam, K, par, T in families(np.random.default_rng(7)):
    mu = stat(T); h, s, W = h_sigma_W(T)
    rows.append((fam, h, s, [D(T, C, mu) - max(h - C, 0) for C in (1, 2)]))
for ci, C in enumerate((1, 2)):
    v = np.array([r[3][ci] for r in rows])
    print("3. C=%d penalty over %d chains: mean %.3f max %.3f min %.4f" % (C, len(v), v.mean(), v.max(), v.min()), flush=True)
    for fam in ("dirichlet", "zipf", "mixture"):
        print("     %-9s mean %.3f" % (fam, np.mean([r[3][ci] for r in rows if r[0] == fam])), flush=True)
    X = np.c_[np.ones(len(rows)), [r[1] for r in rows], [r[2] for r in rows]]
    beta, *_ = np.linalg.lstsq(X, v, rcond=None); res = v - X @ beta
    print("     R^2 on (h_theta, sigma_theta) = %.2f" % (1 - res.var() / v.var()), flush=True)


# 4. Prop 6.13 bound
def U(pbar, M):
    if pbar >= 1: return 0.0
    return -pbar * math.log2(pbar) - (1 - pbar) * math.log2((1 - pbar) / (M - 1))


rng = np.random.default_rng(4)
viol = 0; xs = []; ys = []
for _ in range(600):
    n = int(rng.integers(4, 16)); a = float(rng.choice([0.1, 0.3, 1.0])); p = rng.dirichlet([a] * n)
    M = int(rng.choice([2, 4, 8])); pbar = max(p.max(), 1 / M)
    exact = best_partition_entropy(p, M, restarts=12)
    if exact > U(pbar, M) + 1e-9: viol += 1
    if p.max() >= 1 / M:
        xs.append(math.log2(M) - U(pbar, M)); ys.append(math.log2(M) - exact)
xs = np.array(xs); ys = np.array(ys)
print("4. Prop 6.13: violations %d/600; binding rows %d; mean slack %.3f; corr^2 %.2f" %
      (viol, len(xs), (ys - xs).mean(), np.corrcoef(xs, ys)[0, 1] ** 2), flush=True)

# 5. Schur counterexample
p = (0.3153, 0.2661, 0.1642, 0.1517, 0.1027); q = (0.2190, 0.2135, 0.2126, 0.1979, 0.1570)
maj = all(np.cumsum(sorted(p, reverse=True)) >= np.cumsum(sorted(q, reverse=True)) - 1e-12)
print("5. delta(p)=%.4f delta(q)=%.4f (M=3, exhaustive); p majorizes q: %s" %
      (math.log2(3) - exact_best(p, 3), math.log2(3) - exact_best(q, 3), maj), flush=True)
