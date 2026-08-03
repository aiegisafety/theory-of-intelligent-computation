"""
Canonical abstraction ~_theta* by partition refinement, plus entropy rates.

The refiner is deliberately GENERIC: its only inputs are a label array and a
transition-triplet callback.  It knows nothing about tori, zones, or `mod m`.
Whatever structure it finds, it found from the kernel.

Algorithm (Theorem 4 of TIC, standard Kanellakis-Smolka / Paige-Tarjan form):

    Pi_0  = partition by goal label
    Pi_n+1 = split each block of Pi_n by the signature
             s |-> ( P_a(B | s) )_{a in A, B in Pi_n}
    stop at the fixed point.

Signatures are computed with bincount aggregation over (state, target-block)
rather than dense |S| x |S| matrices, which is what makes |S| ~ 2*10^4 feasible.
"""

import numpy as np

TOL = 1e-9   # absolute tolerance for signature equality

# A BUG THIS FILE USED TO HAVE, AND WHY IT MATTERS.
#
# Signatures were compared by np.round(sig, 9).  Fixed-decimal rounding is not a
# valid equality test: two values that are mathematically identical but computed
# along different floating-point paths can straddle a rounding boundary
# (0.1499999... vs 0.1500000...) and be declared different at ANY precision.
#
# Symptom: in the ontology-drift environment the returned block count flipped
# between the analytically correct 9 and a spurious 27 depending only on the
# rounding constant --
#     ROUND=9 -> 27, 27,  9, 27
#     ROUND=7 ->  9, 27, 27,  9
#     ROUND=6 ->  9,  9, 27, 27
# i.e. pure floating-point noise masquerading as structure, in the direction of
# UNDER-merging (too many blocks, so h_theta over-estimated).
#
# Fixed by clustering each signature column with an absolute tolerance instead.


def _canonicalise(sig, tol=TOL):
    """Replace near-equal values in each column by a common representative."""
    out = np.empty_like(sig)
    for c in range(sig.shape[1]):
        col = sig[:, c]
        u = np.unique(col)
        reps = np.empty_like(u)
        start = 0
        for i in range(1, len(u) + 1):
            if i == len(u) or u[i] - u[start] > tol:
                reps[start:i] = u[start]
                start = i
        out[:, c] = reps[np.searchsorted(u, col)]
    return out


def refine(num_states, num_actions, labels, trans_fn, verbose=False,
           max_iter=100):
    """Return (state_to_block, n_blocks).

    trans_fn(a) -> (src, dst, prob) arrays for joint action a.
    """
    # Pi_0 : goal partition
    _, s2b = np.unique(labels, return_inverse=True)
    s2b = s2b.astype(np.int64)
    n_blocks = s2b.max() + 1

    for it in range(max_iter):
        # signature matrix: rows = states, cols = (action, target block)
        sig = np.empty((num_states, num_actions * n_blocks), dtype=np.float64)
        for a in range(num_actions):
            src, dst, prob = trans_fn(a)
            key = src * n_blocks + s2b[dst]
            agg = np.bincount(key, weights=prob,
                              minlength=num_states * n_blocks)
            sig[:, a * n_blocks:(a + 1) * n_blocks] = \
                agg.reshape(num_states, n_blocks)
        sig = _canonicalise(sig)

        # split within existing blocks: key on (current block, signature)
        combo = np.concatenate([s2b.reshape(-1, 1).astype(np.float64), sig],
                               axis=1)
        _, new_s2b = np.unique(combo, axis=0, return_inverse=True)
        new_s2b = new_s2b.astype(np.int64)
        new_n = new_s2b.max() + 1

        if verbose:
            print(f"  refine iter {it}: {n_blocks} -> {new_n} blocks", flush=True)

        if new_n == n_blocks:
            return s2b, int(n_blocks)
        s2b, n_blocks = new_s2b, new_n

    raise RuntimeError("refinement did not converge")


def entropy_rates(num_states, s2b, n_blocks, chain, power_iters=400):
    """h and h_theta measured with the SAME estimator (anti-trap rule #4).

    estimator:  h = - sum_s mu(s) sum_s' T(s'|s) log2 T(s'|s)
    applied to the physical chain and to the quotient chain respectively.
    """
    src, dst, prob = chain

    # stationary distribution by power iteration
    mu = np.full(num_states, 1.0 / num_states)
    for _ in range(power_iters):
        contrib = mu[src] * prob
        mu_next = np.bincount(dst, weights=contrib, minlength=num_states)
        tot = mu_next.sum()
        if tot <= 0:
            break
        mu_next /= tot
        if np.abs(mu_next - mu).sum() < 1e-14:
            mu = mu_next
            break
        mu = mu_next

    # physical entropy rate
    nz = prob > 1e-15
    h = float(-np.sum(mu[src[nz]] * prob[nz] * np.log2(prob[nz])))

    # quotient chain: aggregate by block.  Bisimulation guarantees the block
    # transition distribution is identical for every state in a block, so we
    # take the mu-weighted average (equals any representative's row).
    bsrc = s2b[src]
    bdst = s2b[dst]
    key = bsrc * n_blocks + bdst
    # weight each physical row by its stationary mass, then renormalise per block
    w = mu[src] * prob
    Tq_flat = np.bincount(key, weights=w, minlength=n_blocks * n_blocks)
    Tq = Tq_flat.reshape(n_blocks, n_blocks)
    mu_q = np.bincount(s2b, weights=mu, minlength=n_blocks)
    rowsum = Tq.sum(axis=1, keepdims=True)
    rowsum[rowsum <= 0] = 1.0
    Tq = Tq / rowsum

    nzq = Tq > 1e-15
    h_theta = float(-np.sum((mu_q[:, None] * Tq * np.log2(np.where(nzq, Tq, 1.0)))[nzq]))

    return h, h_theta, mu, mu_q
