"""
Asymmetric-terrain environment.

WHY THIS EXISTS.  In the rendezvous torus every row of the quotient kernel was a
permutation of the same distribution (m=2: {.36,.32,.16,.16} in every row).  A
consequence nobody asked for: the per-step information variable
T = -log2 P(S'|S) is i.i.d., so Var(T_n) = n*sigma_theta^2 EXACTLY, with all
autocovariance terms identically zero.  Every measurement of sigma_theta so far
therefore lives in a degenerate special case, and the general claim
"sd(T_n/n) = sigma_theta/sqrt(n)" is untested.

This environment breaks that symmetry deliberately: the move noise depends on
the agent's own zone ("rough terrain in some zones, smooth in others"), so
different operational states have genuinely different-SHAPED successor
distributions, not merely relabelled ones.

Consequences designed in:
  * zone(x) = x mod m stays dynamically closed (the noise level is a function of
    the zone, so the zone still determines its own successor distribution) --
    a canonical quotient still exists and refinement can still find it;
  * the quotient can no longer collapse to the relative offset (x1-x2), because
    the dynamics now depend on ABSOLUTE zone.  Expect ~m^2 blocks rather than m,
    which also gives a finer staircase for the width-vs-sigma test that failed
    on discretisation last time.
  * y is retained on a short ring as task-irrelevant structure the refiner must
    still collapse.

State: s = ((x1*Ny + y1) * n_pos + (x2*Ny + y2)) * K + w
"""

import numpy as np

ACTIONS = np.array([(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)], dtype=np.int64)
N_ACT = len(ACTIONS)


class AsymTerrain:
    def __init__(self, Nx=12, Ny=4, m=4, K=1, p_lo=0.05, p_hi=0.45,
                 p_noise=0.15, drag=0.0):
        assert Nx % m == 0
        self.Nx, self.Ny, self.m, self.K = int(Nx), int(Ny), int(m), int(K)
        self.p_noise = float(p_noise)
        # `drag`: probability the agent is pinned in place regardless of action
        # or wind.  Like the wind, it survives the uniform-action average, so it
        # is a working lever on h_theta and sigma_theta.  p_noise is NOT such a
        # lever -- it cancels exactly (see transitions_for_action).
        self.drag = float(drag)
        self.n_pos = Nx * Ny
        self.num_states = self.n_pos * self.n_pos * self.K
        self.num_actions = N_ACT * N_ACT

        # terrain: noise level as a function of zone.  Deliberately uneven and
        # non-monotone so the resulting rows are not orderings of one another.
        z = np.arange(self.m)
        self.p_zone = p_lo + (p_hi - p_lo) * (
            0.5 * (1 - np.cos(2 * np.pi * z / self.m)) * 0.6
            + 0.4 * ((z * 7) % self.m) / max(self.m - 1, 1))

        s = np.arange(self.num_states, dtype=np.int64)
        self.w_of = s % self.K
        rest = s // self.K
        p2 = rest % self.n_pos
        p1 = rest // self.n_pos
        self.x1_of, self.y1_of = p1 // Ny, p1 % Ny
        self.x2_of, self.y2_of = p2 // Ny, p2 % Ny
        self.labels = ((self.x1_of % m) == (self.x2_of % m)).astype(np.int64)

    def encode(self, x1, y1, x2, y2, w):
        return (((x1 * self.Ny + y1) * self.n_pos +
                 (x2 * self.Ny + y2)) * self.K + w)

    def transitions_for_action(self, a):
        """FIRST ATTEMPT FAILED, RECORDED HERE.  The obvious design -- make the
        action-realisation noise p depend on the zone -- produces NO asymmetry
        at all, because averaging over intended actions uniformly gives every
        move probability (1-p)/5 + 4*(p/4)/5 = 1/5 regardless of p.  The terrain
        cancels exactly.  Measured: 1 distinct row shape out of 16, and h_theta
        identical for m=4 and m=6.

        The fix is a zone-dependent effect that is NOT a reweighting of the
        agent's own action set: a directional WIND that displaces the agent by
        +1 in x with probability p_zone(z), independently of what it intended.
        Convolving a zone-dependent asymmetric shift with the action average
        cannot cancel, so successor distributions genuinely differ in shape.
        """
        a1, a2 = a // N_ACT, a % N_ACT
        src_all = np.arange(self.num_states, dtype=np.int64)
        pz1 = self.p_zone[self.x1_of % self.m]
        pz2 = self.p_zone[self.x2_of % self.m]
        pw = 1.0 / self.K
        pn = self.p_noise
        srcs, dsts, probs = [], [], []
        for i1 in range(N_ACT):
            dx1, dy1 = int(ACTIONS[i1, 0]), int(ACTIONS[i1, 1])
            q1 = (1.0 - pn) if i1 == a1 else pn / (N_ACT - 1)
            for wnd1 in (0, 1, 2):     # 2 = pinned by drag
                if wnd1 == 2:
                    r1 = q1 * self.drag
                    nx1, ny1 = self.x1_of, self.y1_of
                else:
                    r1 = q1 * (1.0 - self.drag) * (pz1 if wnd1 else (1.0 - pz1))
                    nx1 = (self.x1_of + dx1 + wnd1) % self.Nx
                    ny1 = (self.y1_of + dy1) % self.Ny
                for i2 in range(N_ACT):
                    dx2, dy2 = int(ACTIONS[i2, 0]), int(ACTIONS[i2, 1])
                    q2 = (1.0 - pn) if i2 == a2 else pn / (N_ACT - 1)
                    for wnd2 in (0, 1, 2):
                        if wnd2 == 2:
                            r2 = q2 * self.drag
                            nx2, ny2 = self.x2_of, self.y2_of
                        else:
                            r2 = (q2 * (1.0 - self.drag) *
                                  (pz2 if wnd2 else (1.0 - pz2)))
                            nx2 = (self.x2_of + dx2 + wnd2) % self.Nx
                            ny2 = (self.y2_of + dy2) % self.Ny
                        base = (((nx1 * self.Ny + ny1) * self.n_pos +
                                 (nx2 * self.Ny + ny2)) * self.K)
                        pr = r1 * r2 * pw
                        pr = np.broadcast_to(np.asarray(pr, dtype=float),
                                             (self.num_states,))
                        base = np.broadcast_to(np.asarray(base),
                                               (self.num_states,))
                        for nw in range(self.K):
                            srcs.append(src_all)
                            dsts.append(base + nw)
                            probs.append(pr)
        return (np.concatenate(srcs), np.concatenate(dsts),
                np.concatenate(probs))

    def uniform_policy_chain(self):
        S = self.num_states
        keys, prob = [], []
        for a in range(self.num_actions):
            src, dst, pr = self.transitions_for_action(a)
            keys.append(src * S + dst)
            prob.append(pr / self.num_actions)
        k = np.concatenate(keys)
        p = np.concatenate(prob)
        uk, inv = np.unique(k, return_inverse=True)
        agg = np.bincount(inv, weights=p, minlength=len(uk))
        return (uk // S).astype(np.int64), (uk % S).astype(np.int64), agg
