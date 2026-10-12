"""V3 §6.8: per-step coding when the receiver's state is not shared (errors propagate).

Sender knows B_{t+1} and tracks the receiver's belief pi_t. Myopic rule: partition the predictive
belief q_t = pi_t P into M = 2^C cells of masses as equal as possible; send the cell of B_{t+1};
receiver's new belief is q_t restricted to the cell. Residual uncertainty H(pi_{t+1}).
"""
import json, numpy as np
from chains import H, rate, stat, dirichlet, torus_m2
from fastpart import _f


def balanced_cells(q, M):
    """Assignment of symbols to M cells with masses as equal as possible (LPT + moves/swaps)."""
    idx = np.where(q > 0)[0]; p = q[idx]; n = len(p)
    a = np.empty(n, int); mass = np.zeros(M)
    for i in np.argsort(-p):
        j = int(np.argmin(mass)); a[i] = j; mass[j] += p[i]
    for _ in range(5000):
        fm = _f(mass); src = a
        g = (_f(mass[src] - p)[:, None] + _f(mass[None, :] + p[:, None]) - fm[src][:, None] - fm[None, :])
        g[np.arange(n), src] = -np.inf
        i, j = np.unravel_index(np.argmax(g), g.shape)
        if g[i, j] > 1e-13:
            mass[src[i]] -= p[i]; mass[j] += p[i]; a[i] = j; continue
        A = a[:, None]; B = a[None, :]; d = p[None, :] - p[:, None]
        g2 = _f(mass[A] + d) + _f(mass[B] - d) - _f(mass[A]) - _f(mass[B]); g2[A == B] = -np.inf
        i, k = np.unravel_index(np.argmax(g2), g2.shape)
        if g2[i, k] > 1e-13:
            x, y = a[i], a[k]; mass[x] += p[k] - p[i]; mass[y] += p[i] - p[k]; a[i], a[k] = y, x; continue
        break
    cell = -np.ones(len(q), int); cell[idx] = a
    return cell, mass


def D_shared(T, C):
    from fastpart import best_partition_entropy
    mu = stat(T); M = 2 ** C
    return sum(mu[b] * (H(T[b]) - best_partition_entropy(T[b], M)) for b in range(len(T)))


def run(T, C, steps=8000, seed=0, burn=500):
    rng = np.random.default_rng(seed); K = len(T); M = 2 ** C
    mu = stat(T); b = rng.choice(K, p=mu); pi = np.eye(K)[b]
    res = []; Hq = []; Hm = []
    for t in range(steps):
        q = pi @ T
        b = rng.choice(K, p=T[b])
        cell, mass = balanced_cells(q, M)
        g = cell[b]
        post = np.where(cell == g, q, 0.0); post /= post.sum()
        if t >= burn:
            res.append(H(post)); Hq.append(H(q)); Hm.append(float(_f(mass).sum()))
        pi = post
    return np.mean(res), np.mean(Hq), np.mean(Hm)


if __name__ == "__main__":
    OUT = []
    for name, T in [("dirichlet K=16 a=0.5", dirichlet(16, 0.5, np.random.default_rng(11))),
                    ("torus m=2", torus_m2())]:
        h = rate(T)
        print("%s  h_theta=%.4f" % (name, h))
        print("  C  floor   D_shared  R_myopic  E[H(q)]  E[H(msg)]")
        for C in (1, 2, 3):
            R, hq, hm = run(T, C)
            OUT.append(dict(chain=name, h=h, C=C, floor=max(h - C, 0), D=D_shared(T, C), R=R, Hq=hq, Hm=hm))
            print("  %d  %.4f  %.4f    %.4f    %.4f   %.4f" % (C, max(h - C, 0), D_shared(T, C), R, hq, hm), flush=True)
    json.dump(OUT, open("v3_error_propagation_data.json", "w"), indent=1)
