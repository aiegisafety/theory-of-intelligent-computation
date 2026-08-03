"""
Rate-limited predictive channel + agent policies.

ANTI-TRAP RULE #7 (new; this is what v1 violated and what the original spec's
six rules did not catch).  In v1 the agents' policy table was indexed by the
TRUE joint state, so the channel was decorative: success was ~1.0 even at C = 1
bit/step.  Here the architecture makes that impossible:

    * `choose_action` receives ONLY (own coordinates, decoded offset).  The true
      state of the other agent is not a parameter.  It cannot leak in.
    * `channel_ablation_test` in audit.py randomises every transmitted symbol.
      If performance does NOT collapse, decisions are not flowing through the
      channel and the run is void.  This is an empirical test, not a code
      review, and it would have caught v1 immediately.

The coder is PREDICTIVE, which is the theoretically correct thing: the bandwidth
law is about the entropy RATE h_theta, not the log of the class count.  A
memoryless code would need log2(#classes) bits; a predictive code needs only
enough alphabet to cover the typical successors of the previously decoded
value, which is what makes h_theta -- rather than log2|S/~| -- the threshold.
"""

import numpy as np

ACT_XMINUS, ACT_XPLUS, ACT_YMINUS, ACT_YPLUS, ACT_STAY = 0, 1, 2, 3, 4


class PredictiveChannel:
    """Fixed-alphabet predictive coder over a known Markov chain.

    Sender and receiver share the chain model (both agents know the environment).
    At each step the codebook is the M most probable successors of the receiver's
    PREVIOUSLY DECODED value, ordered by probability with ties broken by this
    receiver's own RNG (anti-trap rule #1: each agent's codebook randomisation is
    an independent stream, so two agents can and do decode differently).

    If the true value is in the codebook the receiver decodes it exactly;
    otherwise it decodes the codebook's top entry -- a genuine error that then
    propagates, because the next codebook is built from the wrong value.
    """

    def __init__(self, succ_idx, succ_prob, alphabet, rng, n_values):
        self.succ_idx = succ_idx      # list: value -> np.array of successors
        self.succ_prob = succ_prob    # list: value -> np.array of probs
        self.M = int(alphabet)
        self.rng = rng
        self.n_values = n_values
        self.v_prev = None

    def reset(self, v_true):
        # first step is free (agents are told the initial value)
        self.v_prev = v_true
        return v_true

    def step(self, v_true):
        idx = self.succ_idx[self.v_prev]
        pr = self.succ_prob[self.v_prev]
        if len(idx) == 0:
            self.v_prev = v_true
            return v_true
        jitter = self.rng.random(len(pr)) * 1e-12      # independent tie-break
        order = np.argsort(-(pr + jitter))
        book = idx[order[:self.M]]
        decoded = v_true if v_true in book else int(book[0])
        self.v_prev = decoded
        return decoded


def build_successors(src, dst, prob, n_values):
    """Group a transition triplet list into per-value successor arrays."""
    order = np.argsort(src, kind="stable")
    s, d, p = src[order], dst[order], prob[order]
    bounds = np.searchsorted(s, np.arange(n_values + 1))
    succ_idx, succ_prob = [], []
    for v in range(n_values):
        a, b = bounds[v], bounds[v + 1]
        pv = p[a:b]
        tot = pv.sum()
        succ_idx.append(d[a:b])
        succ_prob.append(pv / tot if tot > 0 else pv)
    return succ_idx, succ_prob


def choose_action(role, own_x, own_y, off_x, off_y, m):
    """Policy.  Role 0 closes the x-offset, role 1 closes the y-offset.

    Parameters are deliberately minimal: own coordinates (private, exact) and
    the DECODED offset (everything that came through the channel).  The other
    agent's true position is not available here by construction.
    """
    d = off_x if role == 0 else off_y
    if d == 0:
        return ACT_STAY
    # move the short way round the cycle Z_m
    if role == 0:
        return ACT_XMINUS if d <= m // 2 else ACT_XPLUS
    else:
        return ACT_YMINUS if d <= m // 2 else ACT_YPLUS
