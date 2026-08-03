"""
Episode simulator.

Task: 2-D rendezvous on the torus.  Success = the two agents occupy the same
zone (both axes) for HOLD consecutive steps within T steps.

Two channel conditions, differing ONLY in what the broadcaster encodes:
  * 'class'  -- encodes the canonical operational block  ~_theta*  (rate h_theta)
  * 'state'  -- encodes the raw physical state                     (rate h)
Both use the identical predictive coder and the identical alphabet size, so any
difference between them is attributable to WHAT is encoded, not to how well.
"""

import numpy as np
from env import RendezvousTorus, ACTIONS
from agents import (PredictiveChannel, build_successors, choose_action)

T_STEPS = 60
# HOLD was raised from 3 to 6 after calibration (anti-trap rule #3): at m=2 the
# quotient has only 4 blocks, so random co-location gave a ~0.6 chance floor and
# the m=2 row carried almost no information.  HOLD=6 pushes the floor down for
# every configuration uniformly; it is a property of the task, not of a
# condition, so it does not bias class-vs-state.
HOLD = 6


class Scenario:
    """Everything that can be precomputed once per (N, m, K) configuration."""

    def __init__(self, env, s2b, n_blocks):
        self.env = env
        self.s2b = s2b
        self.n_blocks = n_blocks
        chain = env.uniform_policy_chain()
        self.phys_succ = build_successors(*chain, env.num_states)
        # block chain under the same uniform policy, same estimator path
        src, dst, prob = chain
        key = s2b[src] * n_blocks + s2b[dst]
        agg = np.bincount(key, weights=prob, minlength=n_blocks * n_blocks)
        Tq = agg.reshape(n_blocks, n_blocks)
        Tq = Tq / np.maximum(Tq.sum(axis=1, keepdims=True), 1e-300)
        bsrc, bdst = np.nonzero(Tq > 1e-12)
        self.block_succ = build_successors(bsrc, bdst, Tq[bsrc, bdst], n_blocks)
        # block id -> (offset_x, offset_y)
        rep = np.full(n_blocks, -1, dtype=np.int64)
        for s in range(env.num_states):
            b = s2b[s]
            if rep[b] < 0:
                rep[b] = s
        self.block_off = np.empty((n_blocks, 2), dtype=np.int64)
        for b in range(n_blocks):
            s = rep[b]
            self.block_off[b] = (
                (env.x1_of[s] - env.x2_of[s]) % env.m,
                (env.y1_of[s] - env.y2_of[s]) % env.m,
            )


def run_episode(sc, mode, alphabet, seed, scramble=False):
    """One episode.  `scramble=True` randomises every decoded value: the
    channel-ablation control (anti-trap rule #7)."""
    env = sc.env
    rng1 = np.random.default_rng(seed * 100003 + 1)
    rng2 = np.random.default_rng(seed * 100003 + 2)
    rng_env = np.random.default_rng(seed * 100003 + 999)

    if mode == "class":
        succ_i, succ_p, nval = sc.block_succ[0], sc.block_succ[1], sc.n_blocks
        to_val = lambda s: int(sc.s2b[s])
    else:
        succ_i, succ_p, nval = sc.phys_succ[0], sc.phys_succ[1], env.num_states
        to_val = lambda s: int(s)

    ch1 = PredictiveChannel(succ_i, succ_p, alphabet, rng1, nval)
    ch2 = PredictiveChannel(succ_i, succ_p, alphabet, rng2, nval)

    # start in a non-goal state
    while True:
        x1 = int(rng_env.integers(env.N)); y1 = int(rng_env.integers(env.N))
        x2 = int(rng_env.integers(env.N)); y2 = int(rng_env.integers(env.N))
        if (x1 % env.m, y1 % env.m) != (x2 % env.m, y2 % env.m):
            break
    w = int(rng_env.integers(env.K))

    s = env.encode(x1, y1, x2, y2, w)
    v1 = ch1.reset(to_val(s)); v2 = ch2.reset(to_val(s))
    streak = 0

    for _ in range(T_STEPS):
        # ---- each agent's view of the operational offset -------------------
        def offset_from(v, agent_rng):
            if scramble:
                v = int(agent_rng.integers(nval))
            if mode == "class":
                return sc.block_off[v]
            b = sc.s2b[v]
            return sc.block_off[b]

        o1 = offset_from(v1, rng1)
        o2 = offset_from(v2, rng2)

        a1 = choose_action(0, x1, y1, int(o1[0]), int(o1[1]), env.m)
        a2 = choose_action(1, x2, y2, int(o2[0]), int(o2[1]), env.m)

        x1, y1 = env.sample_move(x1, y1, a1, rng_env)
        x2, y2 = env.sample_move(x2, y2, a2, rng_env)
        w = int(rng_env.integers(env.K))

        s = env.encode(x1, y1, x2, y2, w)
        if (x1 % env.m) == (x2 % env.m) and (y1 % env.m) == (y2 % env.m):
            streak += 1
            if streak >= HOLD:
                return 1
        else:
            streak = 0

        v1 = ch1.step(to_val(s))
        v2 = ch2.step(to_val(s))

    return 0


def evaluate(sc, mode, alphabet, n_seeds=60, scramble=False, seed0=1000):
    r = np.array([run_episode(sc, mode, alphabet, seed0 + i, scramble)
                  for i in range(n_seeds)], dtype=float)
    return float(r.mean()), float(r.std())
