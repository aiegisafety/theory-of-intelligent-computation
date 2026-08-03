"""
TIC Experiment 5 (v2) — environment.

DESIGN RATIONALE (read before changing anything):

v1 failed for two structural reasons: (a) at 2 of its 3 granularities the goal
labelling admitted NO non-trivial bisimulation quotient (|S/~| = |S|, so
h_theta = h and the "class-aware" encoder was literally the same function as the
"state-aware" one), and (b) its "10x scale" axis raised |S| but barely moved h
(4.37 -> 4.44 bits/step).  (b) happens because the entropy RATE of a random walk
does not grow with the number of states -- it is set by the move noise.  Both
are fixed here by construction.

  * GRANULARITY AXIS (m).  Two agents on an N x N torus.  Goal = RENDEZVOUS:
    both agents in the same zone, zone(x) = x mod m.  Because the torus is a
    cyclic group and moves are +/-1, x -> x mod m is dynamically closed when
    m | N.  So a non-trivial canonical abstraction is guaranteed to EXIST, and
    partition refinement will DISCOVER it: nothing in refine.py is told about
    "mod m", it sees only a raw label array and a raw transition kernel.
    Varying m moves h_theta without touching the physical dynamics.

  * SCALE AXES.  Two different ones, because they test different things:
      (A) grid size N.  Multiplies |S| by (N'/N)^4.  h stays ~constant
          (random-walk entropy rate is N-independent).  Tests: insensitivity to
          the raw STATE COUNT.
      (B) weather K.  A global variable w in {0..K-1} that jumps uniformly at
          random every step, is unaffected by the agents, and does not enter the
          goal labelling.  Multiplies |S| by K and adds EXACTLY log2(K)
          bits/step to h, while leaving the quotient chain -- hence h_theta --
          mathematically untouched.  Tests: insensitivity to physical ENTROPY
          RATE h.  This is the sharp version of the bandwidth-law prediction.

  * The y coordinate is task-irrelevant but dynamically coupled to the agent's
    own moves -- a second, different kind of irrelevant structure the refiner
    must also collapse.  Kept in deliberately so refinement does real work.

State encoding:  s = ((x1*N + y1) * n_pos + (x2*N + y2)) * K + w
Action encoding: a = a1*5 + a2,  each in {up, down, left, right, stay}
"""

import numpy as np

ACTIONS = np.array([(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)], dtype=np.int64)
N_ACT = len(ACTIONS)


class RendezvousTorus:
    def __init__(self, grid_size=6, m=2, K=1, p_noise=0.15):
        assert grid_size % m == 0, "m must divide grid_size (quotient closure)"
        self.N = int(grid_size)
        self.m = int(m)
        self.K = int(K)
        self.p_noise = float(p_noise)

        self.n_pos = self.N * self.N
        self.num_states = self.n_pos * self.n_pos * self.K
        self.num_actions = N_ACT * N_ACT

        # per-state decoded coordinates (vectorised)
        s = np.arange(self.num_states, dtype=np.int64)
        self.w_of = s % self.K
        rest = s // self.K
        self.p2_of = rest % self.n_pos
        self.p1_of = rest // self.n_pos
        self.x1_of = self.p1_of // self.N
        self.y1_of = self.p1_of % self.N
        self.x2_of = self.p2_of // self.N
        self.y2_of = self.p2_of % self.N

        self.labels = self._compute_labels()

    # ------------------------------------------------------------------ coding
    def encode(self, x1, y1, x2, y2, w):
        p1 = x1 * self.N + y1
        p2 = x2 * self.N + y2
        return (p1 * self.n_pos + p2) * self.K + w

    def decode(self, s):
        w = s % self.K
        rest = s // self.K
        p2 = rest % self.n_pos
        p1 = rest // self.n_pos
        return (p1 // self.N, p1 % self.N, p2 // self.N, p2 % self.N, w)

    # ------------------------------------------------------------------ labels
    def _compute_labels(self):
        """1 = rendezvous, 0 = not.  Refiner receives only this array.

        2-D rendezvous: the agents must occupy the same zone in BOTH axes,
        zone(x, y) = (x mod m, y mod m).

        NOTE ON A CORRECTED PREDICTION.  An earlier 1-D version of this task
        (same x-zone only) was expected to quotient to m^2 blocks; the refiner
        returned m.  The refiner was right and the prediction was wrong: the
        label depends only on (x1 - x2) mod m, and that difference is itself
        dynamically closed, so absolute position collapses entirely.  The same
        logic applies here, giving the corrected analytic prediction

            |S / ~_theta*|  =  m^2      via  ((x1-x2) mod m, (y1-y2) mod m)

        This is a genuinely large collapse (e.g. 1296 -> 4) and it is the
        refiner, not the designer, that finds it.
        """
        return (((self.x1_of % self.m) == (self.x2_of % self.m)) &
                ((self.y1_of % self.m) == (self.y2_of % self.m))).astype(np.int64)

    # ------------------------------------------------------- transition kernel
    def _move_outcomes(self, a_idx):
        """Outcome list for one agent intending action a_idx.

        Returns list of (dx, dy, prob) over the 5 realised moves.
        """
        out = []
        for i in range(N_ACT):
            p = (1.0 - self.p_noise) if i == a_idx else self.p_noise / (N_ACT - 1)
            out.append((int(ACTIONS[i, 0]), int(ACTIONS[i, 1]), p))
        return out

    def transitions_for_action(self, a):
        """Vectorised (src, dst, prob) triplets for joint action a.

        nnz = num_states * 25 * K.  Generated on demand so we never hold the
        whole kernel in memory at once.
        """
        a1, a2 = a // N_ACT, a % N_ACT
        src_all = np.arange(self.num_states, dtype=np.int64)
        srcs, dsts, probs = [], [], []
        pw = 1.0 / self.K
        for dx1, dy1, q1 in self._move_outcomes(a1):
            nx1 = (self.x1_of + dx1) % self.N
            ny1 = (self.y1_of + dy1) % self.N
            np1 = nx1 * self.N + ny1
            for dx2, dy2, q2 in self._move_outcomes(a2):
                nx2 = (self.x2_of + dx2) % self.N
                ny2 = (self.y2_of + dy2) % self.N
                np2 = nx2 * self.N + ny2
                base = (np1 * self.n_pos + np2) * self.K
                pr = q1 * q2 * pw
                for nw in range(self.K):
                    srcs.append(src_all)
                    dsts.append(base + nw)
                    probs.append(np.full(self.num_states, pr))
        return (np.concatenate(srcs), np.concatenate(dsts),
                np.concatenate(probs))

    def uniform_policy_chain(self):
        """Deduplicated (src, dst, prob) for the chain induced by the uniform
        joint policy.  Both h and h_theta are measured on this chain with the
        same estimator (anti-trap rule #4)."""
        S = self.num_states
        keys_all, prob_all = [], []
        for a in range(self.num_actions):
            src, dst, pr = self.transitions_for_action(a)
            keys_all.append(src * S + dst)
            prob_all.append(pr / self.num_actions)
        keys = np.concatenate(keys_all)
        prob = np.concatenate(prob_all)
        uk, inv = np.unique(keys, return_inverse=True)
        agg = np.bincount(inv, weights=prob, minlength=len(uk))
        return (uk // S).astype(np.int64), (uk % S).astype(np.int64), agg

    # -------------------------------------------------- fast factored sampling
    def sample_move(self, x, y, a_idx, rng):
        """Sample one agent's realised move (used by the simulator)."""
        if rng.random() < self.p_noise:
            i = rng.integers(0, N_ACT - 1)
            if i >= a_idx:
                i += 1
        else:
            i = a_idx
        dx, dy = int(ACTIONS[i, 0]), int(ACTIONS[i, 1])
        return (x + dx) % self.N, (y + dy) % self.N
