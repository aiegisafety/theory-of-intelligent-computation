"""
Experiment 7 environment — ontology drift.

Theorem 11 claims a TWO-LEVEL rate condition

        C  >=  h_theta + h_A

where h_A is the rate at which the correct abstraction itself changes.  It is
the last major theorem with no non-toy evidence, and after Theorem 14 it should
be restated in fault-tolerant form:

        C*(eps)  ~  h_theta + h_A + sigma * Q^{-1}(eps)

DESIGN.  The rendezvous torus, plus a drifting RENDEZVOUS TARGET g in Z_m: the
agents must meet at x-offset equal to g, not at offset 0.  g performs a slow
Markov chain of its own.  So the question "which states count as the goal" --
the ontology -- is itself moving, at a rate we control exactly.

  goal(s) = 1  iff  (x1-x2) mod m == g  and  (y1-y2) mod m == 0

Because g is part of the state and the goal depends on it, the canonical
quotient must retain g:  expected  ((x1-x2) mod m, (y1-y2) mod m, g), i.e. m^3
blocks.  The refiner is told none of this.

WHY THIS IS A CLEAN TEST.  h_theta and h_A are separately tunable and exactly
computable, and because the offset process and the g process are independent,
the joint operational entropy rate is exactly their sum.  So holding the task
fixed and varying ONLY the drift rate gives the sharpest possible prediction:

        d C*  =  d h_A       one for one.

That is a third dissociation, on top of Experiment 5's two.

State: s = ((x1*N + y1) * n_pos + (x2*N + y2)) * m + g
"""

import numpy as np

ACTIONS = np.array([(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)], dtype=np.int64)
N_ACT = len(ACTIONS)


class RendezvousDrift:
    def __init__(self, grid_size=6, m=2, p_drift=0.0, p_noise=0.15):
        assert grid_size % m == 0
        self.N = int(grid_size)
        self.m = int(m)
        self.p_drift = float(p_drift)
        self.p_noise = float(p_noise)

        self.n_pos = self.N * self.N
        self.num_states = self.n_pos * self.n_pos * self.m
        self.num_actions = N_ACT * N_ACT

        s = np.arange(self.num_states, dtype=np.int64)
        self.g_of = s % self.m
        rest = s // self.m
        p2 = rest % self.n_pos
        p1 = rest // self.n_pos
        self.x1_of, self.y1_of = p1 // self.N, p1 % self.N
        self.x2_of, self.y2_of = p2 // self.N, p2 % self.N

        self.labels = (
            (((self.x1_of - self.x2_of) % self.m) == self.g_of) &
            (((self.y1_of - self.y2_of) % self.m) == 0)
        ).astype(np.int64)

    # ------------------------------------------------------------------ rates
    def h_A(self):
        """Entropy rate of the ontology process g.

        g stays with prob 1-p, else jumps uniformly to one of the other m-1
        values.  This is an exact analytic quantity, not an estimate.
        """
        p, m = self.p_drift, self.m
        if p <= 0:
            return 0.0
        h = -(1 - p) * np.log2(1 - p)
        if p > 0 and m > 1:
            h -= p * np.log2(p / (m - 1))
        return float(h)

    def encode(self, x1, y1, x2, y2, g):
        return (((x1 * self.N + y1) * self.n_pos +
                 (x2 * self.N + y2)) * self.m + g)

    # ------------------------------------------------------------- transitions
    def transitions_for_action(self, a):
        a1, a2 = a // N_ACT, a % N_ACT
        src_all = np.arange(self.num_states, dtype=np.int64)
        pn, m, p = self.p_noise, self.m, self.p_drift
        srcs, dsts, probs = [], [], []
        for i1 in range(N_ACT):
            dx1, dy1 = int(ACTIONS[i1, 0]), int(ACTIONS[i1, 1])
            q1 = (1.0 - pn) if i1 == a1 else pn / (N_ACT - 1)
            nx1 = (self.x1_of + dx1) % self.N
            ny1 = (self.y1_of + dy1) % self.N
            for i2 in range(N_ACT):
                dx2, dy2 = int(ACTIONS[i2, 0]), int(ACTIONS[i2, 1])
                q2 = (1.0 - pn) if i2 == a2 else pn / (N_ACT - 1)
                nx2 = (self.x2_of + dx2) % self.N
                ny2 = (self.y2_of + dy2) % self.N
                base = (((nx1 * self.N + ny1) * self.n_pos +
                         (nx2 * self.N + ny2)) * m)
                for ng in range(m):
                    stay = (ng == self.g_of)
                    pg = np.where(stay, 1.0 - p,
                                  p / (m - 1) if m > 1 else 0.0)
                    srcs.append(src_all)
                    dsts.append(base + ng)
                    probs.append(q1 * q2 * pg)
        return (np.concatenate(srcs), np.concatenate(dsts),
                np.concatenate(probs))

    def uniform_policy_chain(self):
        S = self.num_states
        keys, prob = [], []
        for a in range(self.num_actions):
            src, dst, pr = self.transitions_for_action(a)
            keys.append(src * S + dst)
            prob.append(pr / self.num_actions)
        k = np.concatenate(keys); pv = np.concatenate(prob)
        uk, inv = np.unique(k, return_inverse=True)
        agg = np.bincount(inv, weights=pv, minlength=len(uk))
        return (uk // S).astype(np.int64), (uk % S).astype(np.int64), agg

    def sample_move(self, x, y, a_idx, rng):
        if rng.random() < self.p_noise:
            i = rng.integers(0, N_ACT - 1)
            if i >= a_idx:
                i += 1
        else:
            i = a_idx
        return ((x + int(ACTIONS[i, 0])) % self.N,
                (y + int(ACTIONS[i, 1])) % self.N)

    def sample_g(self, g, rng):
        if self.m > 1 and rng.random() < self.p_drift:
            j = rng.integers(0, self.m - 1)
            if j >= g:
                j += 1
            return int(j)
        return int(g)
