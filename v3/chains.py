"""Families of operational chains used in the V3 checks (our own generators)."""
import numpy as np

def stat(T):
    ev, V = np.linalg.eig(T.T); i = np.argmin(abs(ev - 1))
    v = np.abs(np.real(V[:, i])); return v / v.sum()

def H(p):
    p = np.asarray(p, float); p = p[p > 0]; return float(-(p * np.log2(p)).sum())

def rate(T, mu=None):
    mu = stat(T) if mu is None else mu
    return float(sum(mu[i] * H(T[i]) for i in range(len(T))))

def info_dist(T, mu=None):
    mu = stat(T) if mu is None else mu
    v, w = [], []
    for i in range(len(T)):
        for j in range(len(T)):
            if T[i, j] > 1e-15:
                v.append(-np.log2(T[i, j])); w.append(mu[i] * T[i, j])
    v = np.array(v); w = np.array(w); w /= w.sum()
    return v, w

def h_sigma_W(T):
    v, w = info_dist(T)
    h = float((v * w).sum()); s = float(np.sqrt(((v - h) ** 2 * w).sum()))
    o = np.argsort(v); v, w = v[o], w[o]; cw = np.cumsum(w)
    W = float(np.interp(0.8, cw, v) - np.interp(0.2, cw, v))
    return h, s, W

def dirichlet(K, a, rng):
    return rng.dirichlet([a] * K, size=K)

def zipf(K, s, rng):
    base = 1.0 / np.arange(1, K + 1) ** s; base /= base.sum()
    return np.array([base[rng.permutation(K)] for _ in range(K)])

def mixture(K, eps, rng):
    T = eps * rng.dirichlet([1.0] * K, size=K)
    T[np.arange(K), rng.integers(0, K, K)] += 1 - eps
    return T

def families(rng):
    """48 chains: 16 per family, K in {32, 64}, two parameter settings each."""
    out = []
    for K in (32, 64):
        for a in (0.2, 0.5, 1.0, 3.0):
            for _ in range(2): out.append(("dirichlet", K, a, dirichlet(K, a, rng)))
        for s in (0.8, 1.2, 1.6, 2.0):
            for _ in range(2): out.append(("zipf", K, s, zipf(K, s, rng)))
        for e in (0.05, 0.2, 0.4, 0.7):
            for _ in range(2): out.append(("mixture", K, e, mixture(K, e, rng)))
    return out

def torus_m2():
    """Operational chain of the rendezvous task, m=2: offsets (dx,dy) mod 2, each agent's
    realized move uniform over 5 options under the uniform reference policy."""
    import itertools
    mv = [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]
    inc = {}
    for a, b in itertools.product(mv, mv):
        d = ((a[0] - b[0]) % 2, (a[1] - b[1]) % 2); inc[d] = inc.get(d, 0) + 1 / 25
    st = [(x, y) for x in range(2) for y in range(2)]
    T = np.zeros((4, 4))
    for i, (x, y) in enumerate(st):
        for (dx, dy), p in inc.items():
            T[i, st.index(((x + dx) % 2, (y + dy) % 2))] += p
    return T
