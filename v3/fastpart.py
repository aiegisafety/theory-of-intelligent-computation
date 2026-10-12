"""Fast heuristic for max over partitions of p into <= M cells of H(cell masses).

LPT start from several orders, then local search with single moves and pairwise swaps,
each evaluated through the change in the two affected cells only. Returns a lower bound
on the maximum (exact on all small instances checked against enumeration)."""
import numpy as np


def _f(x):
    x = np.asarray(x, float)
    out = np.zeros_like(x)
    m = x > 0
    out[m] = -x[m] * np.log2(x[m])
    return out


def best_partition_entropy(p, M, restarts=4, seed=0):
    p = np.asarray(p, float); p = p[p > 0]; n = len(p)
    if M >= n:
        return float(_f(p).sum())
    if M <= 1:
        return 0.0
    rng = np.random.default_rng(seed)
    best = -1.0
    for r in range(restarts):
        order = np.argsort(-p) if r == 0 else rng.permutation(n)
        a = np.empty(n, int); mass = np.zeros(M)
        for i in order:
            j = int(np.argmin(mass)); a[i] = j; mass[j] += p[i]
        for _ in range(10000):
            improved = False
            # single moves: item i from a[i] to every j
            fm = _f(mass)
            src = a
            # gain[i, j] = f(m_src - p_i) + f(m_j + p_i) - f(m_src) - f(m_j)
            ms = mass[src]
            g = (_f(ms - p)[:, None] + _f(mass[None, :] + p[:, None])
                 - fm[src][:, None] - fm[None, :])
            g[np.arange(n), src] = -np.inf
            i, j = np.unravel_index(np.argmax(g), g.shape)
            if g[i, j] > 1e-13:
                mass[src[i]] -= p[i]; mass[j] += p[i]; a[i] = j; improved = True
                continue
            # pairwise swaps
            A = a[:, None]; B = a[None, :]
            d = p[None, :] - p[:, None]          # item i in A gets +p_k - p_i
            ma = mass[A]; mb = mass[B]
            g2 = (_f(ma + d) + _f(mb - d) - _f(ma) - _f(mb))
            g2[A == B] = -np.inf
            i, k = np.unravel_index(np.argmax(g2), g2.shape)
            if g2[i, k] > 1e-13:
                x, y = a[i], a[k]
                mass[x] += p[k] - p[i]; mass[y] += p[i] - p[k]; a[i], a[k] = y, x; improved = True
            if not improved:
                break
        best = max(best, float(_f(mass).sum()))
    return best
