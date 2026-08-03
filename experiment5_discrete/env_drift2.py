"""
Experiment 7b — NON-ABSORBABLE ontology drift.

Experiment 7a falsified Theorem 11's two-level rate condition C >= h_theta + h_A:
driving the ontology drift rate h_A from 0 to 1.18 bits/step moved the capacity
threshold by 0.024 bits (slope 0.02, not 1).  The reason is structural, not
numerical: there the drifting target g was a SHIFT acting on the same cyclic
group as the state offset, so the canonical quotient absorbed it --
((x1-x2) - g) mod m is closed, and an agent that tracks its offset RELATIVE TO
THE CURRENT TARGET never needs to know the target at all.

That suggests the corrected statement: h_A only costs capacity to the extent it
is NOT absorbable by the abstraction.  This file builds the non-absorbable case
to test the other side of that claim.

Here the drifting variable selects WHICH COORDINATE the task is about:

    g = 0  ->  goal is  (x1 - x2) mod m == 0
    g = 1  ->  goal is  (y1 - y2) mod m == 0

No shift of the state can absorb this: g changes the task's identity, not its
location.  The quotient must retain g, so 2*m^2 blocks are expected, and the
prediction is that here d C* / d h_A really is 1.

State: s = ((x1*N + y1) * n_pos + (x2*N + y2)) * 2 + g
"""

import numpy as np

ACTIONS = np.array([(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)], dtype=np.int64)
N_ACT = len(ACTIONS)


class ModeDrift:
    def __init__(self, grid_size=6, m=3, p_drift=0.0, p_noise=0.15):
        assert grid_size % m == 0
        self.N, self.m = int(grid_size), int(m)
        self.p_drift, self.p_noise = float(p_drift), float(p_noise)
        self.n_pos = self.N * self.N
        self.num_states = self.n_pos * self.n_pos * 2
        self.num_actions = N_ACT * N_ACT

        s = np.arange(self.num_states, dtype=np.int64)
        self.g_of = s % 2
        rest = s // 2
        p2 = rest % self.n_pos
        p1 = rest // self.n_pos
        self.x1_of, self.y1_of = p1 // self.N, p1 % self.N
        self.x2_of, self.y2_of = p2 // self.N, p2 % self.N

        dx = (self.x1_of - self.x2_of) % self.m
        dy = (self.y1_of - self.y2_of) % self.m
        self.labels = np.where(self.g_of == 0, dx == 0, dy == 0).astype(np.int64)

    def h_A(self):
        p = self.p_drift
        if p <= 0 or p >= 1:
            return 0.0
        return float(-(1 - p) * np.log2(1 - p) - p * np.log2(p))

    def encode(self, x1, y1, x2, y2, g):
        return (((x1 * self.N + y1) * self.n_pos +
                 (x2 * self.N + y2)) * 2 + g)

    def transitions_for_action(self, a):
        a1, a2 = a // N_ACT, a % N_ACT
        src_all = np.arange(self.num_states, dtype=np.int64)
        pn, p = self.p_noise, self.p_drift
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
                         (nx2 * self.N + ny2)) * 2)
                for ng in range(2):
                    pg = np.where(ng == self.g_of, 1.0 - p, p)
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
