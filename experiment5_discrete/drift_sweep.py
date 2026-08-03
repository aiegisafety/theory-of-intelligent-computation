"""
Experiment 7 — does the collapse threshold move by exactly h_A?

Same channel architecture, policy structure and ablation control as Experiment
5.  The only new thing is that the rendezvous TARGET drifts, so the ontology
itself moves at a rate we set exactly.

Prediction (Theorem 11, in Theorem 14's fault-tolerant form):
        C*(eps)  ~  h_theta + h_A + sigma * Q^{-1}(eps)
so with the task held fixed and only the drift rate varied,
        d C*  =  d h_A      one for one.
"""

import json
import math
import sys
import numpy as np
from env_drift import RendezvousDrift
from refine import refine, entropy_rates
from agents import PredictiveChannel, build_successors

T_STEPS = 60
HOLD = 6
ALPHABETS = [2, 3, 4, 6, 8, 12, 16, 24, 32, 48]


class DriftScenario:
    def __init__(self, env):
        self.env = env
        s2b, nb = refine(env.num_states, env.num_actions, env.labels,
                         env.transitions_for_action)
        self.s2b, self.nb = s2b, nb
        chain = env.uniform_policy_chain()
        h, h_th, _, _ = entropy_rates(env.num_states, s2b, nb, chain)
        self.h, self.h_theta = h, h_th
        src, dst, prob = chain
        key = s2b[src] * nb + s2b[dst]
        agg = np.bincount(key, weights=prob, minlength=nb * nb).reshape(nb, nb)
        Tq = agg / np.maximum(agg.sum(axis=1, keepdims=True), 1e-300)
        bs, bd = np.nonzero(Tq > 1e-12)
        self.block_succ = build_successors(bs, bd, Tq[bs, bd], nb)
        # block -> (dx, dy, g)
        rep = np.full(nb, -1, dtype=np.int64)
        for s in range(env.num_states):
            if rep[s2b[s]] < 0:
                rep[s2b[s]] = s
        self.info = np.empty((nb, 3), dtype=np.int64)
        for b in range(nb):
            s = rep[b]
            self.info[b] = ((env.x1_of[s] - env.x2_of[s]) % env.m,
                            (env.y1_of[s] - env.y2_of[s]) % env.m,
                            env.g_of[s])


def choose(role, d, m):
    """Role 0 drives the x-offset to the (drifting) target; role 1 drives y to 0.

    Inputs are ONLY the decoded quantities -- no access to true state."""
    if d == 0:
        return 4                     # stay
    if role == 0:
        return 0 if d <= m // 2 else 1
    return 2 if d <= m // 2 else 3


def episode(sc, M, seed, scramble=False):
    env = sc.env
    rng1 = np.random.default_rng(seed * 100003 + 1)
    rng2 = np.random.default_rng(seed * 100003 + 2)
    rngE = np.random.default_rng(seed * 100003 + 999)
    si, sp = sc.block_succ
    ch1 = PredictiveChannel(si, sp, M, rng1, sc.nb)
    ch2 = PredictiveChannel(si, sp, M, rng2, sc.nb)

    while True:
        x1, y1 = int(rngE.integers(env.N)), int(rngE.integers(env.N))
        x2, y2 = int(rngE.integers(env.N)), int(rngE.integers(env.N))
        g = int(rngE.integers(env.m))
        if not (((x1 - x2) % env.m == g) and ((y1 - y2) % env.m == 0)):
            break

    s = env.encode(x1, y1, x2, y2, g)
    v1 = ch1.reset(int(sc.s2b[s])); v2 = ch2.reset(int(sc.s2b[s]))
    streak = 0
    for _ in range(T_STEPS):
        b1 = int(rng1.integers(sc.nb)) if scramble else v1
        b2 = int(rng2.integers(sc.nb)) if scramble else v2
        dx1, dy1, g1 = sc.info[b1]
        dx2, dy2, g2 = sc.info[b2]
        a1 = choose(0, int((dx1 - g1) % env.m), env.m)
        a2 = choose(1, int(dy2), env.m)

        x1, y1 = env.sample_move(x1, y1, a1, rngE)
        x2, y2 = env.sample_move(x2, y2, a2, rngE)
        g = env.sample_g(g, rngE)

        if ((x1 - x2) % env.m == g) and ((y1 - y2) % env.m == 0):
            streak += 1
            if streak >= HOLD:
                return 1
        else:
            streak = 0
        s = env.encode(x1, y1, x2, y2, g)
        v1 = ch1.step(int(sc.s2b[s])); v2 = ch2.step(int(sc.s2b[s]))
    return 0


def evaluate(sc, M, n=80, scramble=False):
    return float(np.mean([episode(sc, M, 3000 + i, scramble) for i in range(n)]))


def cross(Cs, ys, level=0.5):
    for i in range(1, len(ys)):
        if ys[i - 1] < level <= ys[i]:
            d = ys[i] - ys[i - 1]
            t = (level - ys[i - 1]) / d if d else 0.0
            return Cs[i - 1] + t * (Cs[i] - Cs[i - 1])
    return None


def run(m, p_drift, n_seeds=80):
    env = RendezvousDrift(grid_size=6, m=m, p_drift=p_drift)
    sc = DriftScenario(env)
    hA = env.h_A()
    print(f"m={m} p_drift={p_drift:.2f} |S|={env.num_states} blocks={sc.nb} "
          f"h_theta={sc.h_theta:.4f} h_A={hA:.4f} "
          f"h_theta-h_A={sc.h_theta - hA:.4f}", flush=True)
    Cs, ys = [], []
    for M in ALPHABETS:
        C = math.log2(M)
        y = evaluate(sc, M, n_seeds)
        Cs.append(C); ys.append(y)
    print("   C : " + " ".join(f"{c:5.2f}" for c in Cs), flush=True)
    print("   y : " + " ".join(f"{v:5.2f}" for v in ys), flush=True)
    ab = evaluate(sc, max(ALPHABETS), n_seeds, scramble=True)
    cstar = cross(Cs, ys)
    print(f"   C*={cstar}  ablation={ab:.3f}", flush=True)
    return dict(m=m, p_drift=p_drift, n_blocks=int(sc.nb),
                h_theta=sc.h_theta, h_A=hA, C=Cs, y=ys, C_star=cstar,
                ablation=ab, n_seeds=n_seeds)


if __name__ == "__main__":
    ps = [float(x) for x in sys.argv[1:]] or [0.0]
    out = []
    for p in ps:
        out.append(run(3, p))
    try:
        old = json.load(open("drift_results.json"))
    except Exception:
        old = []
    keep = [r for r in old if r["p_drift"] not in ps]
    json.dump(keep + out, open("drift_results.json", "w"), indent=1)
