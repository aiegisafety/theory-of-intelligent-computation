"""
Learned task abstraction by function approximation — the continuum replacement
for partition refinement.

THE BRIDGE.  Theorem 4 builds ~_theta* from the goal partition, refined by the
dynamics.  Read as an iteration: distinguish states differing in the goal; then
states differing in where the goal will be next; then next-next.  In the
continuum this becomes a multi-horizon goal-prediction map -- the transition
operator iterated on the goal function (a Krylov subspace; the same object the
successor-representation literature reaches from another direction).

A CORRECTION THE FIRST ATTEMPT FORCED, worth recording because it is a theory
point and not an implementation detail.  The obvious feature

    psi(s) = ( E[goal_{t+h} | s] )_{h=1..H}          -- averaged over actions

FAILS, and fails for a principled reason.  The goal here is |e| < delta, which
is symmetric in the sign of the offset; under a random policy the dynamics are
symmetric too.  So +e and -e have identical goal-prediction profiles and the
feature merges them.  Measured: readout MAE 0.194 versus 0.000 for the oracle,
i.e. the learned feature carried essentially no usable offset information.

But a controller MUST distinguish +e from -e: they require opposite moves.  The
resolution is already in the tabular theory and I had simply dropped it in the
translation.  Condition (D) of Theorem 4 quantifies PER ACTION:

    S1 ~ S2  =>  for EVERY a and every block B:  P_a(B|S1) = P_a(B|S2).

Averaging over actions discards exactly that quantifier.  The continuum feature
must therefore be ACTION-CONDITIONED:

    psi(s) = ( E[goal_{t+h} | s, a_t = a] )_{a in A, h = 1..H}

which is what is implemented below.  Under a fixed action, +e and -e have
genuinely different goal-hitting profiles, and the symmetry is broken.

    => Goal-prediction sufficiency is NOT control sufficiency.  The per-action
       quantifier is what makes the difference, in the continuum exactly as in
       the finite case.

Everything is learned by ridge regression on random Fourier features from
rollouts alone.  The learner is never told that the task depends on x1 - x2,
never told which coordinates are irrelevant, and never sees a partition.
"""

import numpy as np

U0 = 0.06                      # discrete control magnitude
CONTROLS = np.array([-U0, 0.0, +U0])
N_A = len(CONTROLS)


class TorusRFF:
    """Random Fourier features with INTEGER frequencies.

    The state lives on a torus, so integer frequencies are exactly periodic --
    no boundary artefacts, and the modes that matter (differences like x1 - x2)
    are representable as single columns.
    """

    def __init__(self, dim, n_feat=800, fmax=1, seed=0, max_order=2):
        """Frequencies are SPARSE: at most `max_order` non-zero components.

        Dense random integer frequencies fail in high dimension -- for d = 10
        there are 3^10 = 59049 possible columns and the one that matters
        (+1 on x1, -1 on x2) is essentially never drawn.  Measured: readout MAE
        degraded from 0.016 at d=4 to 0.199 at d=10, which would have been
        misread as the theory failing when it was the approximator failing.

        Restricting to low-order interactions is the standard degree-2 kernel
        prior.  It does NOT tell the learner which pair of coordinates matters
        -- all C(d,2) pairs are equally available -- it only says the answer is
        a low-order interaction, which is the usual assumption behind every
        polynomial or Gaussian kernel method.
        """
        rng = np.random.default_rng(seed)
        W = np.zeros((dim, n_feat))
        for j in range(n_feat):
            order = rng.integers(0, max_order + 1)
            if order > 0:
                idx = rng.choice(dim, size=min(order, dim), replace=False)
                vals = rng.choice([-fmax, fmax], size=len(idx))
                W[idx, j] = vals
        self.W = W
        self.b = rng.random(n_feat) * 2 * np.pi
        self.scale = np.sqrt(2.0 / n_feat)

    def __call__(self, X):
        return self.scale * np.cos(2 * np.pi * (np.atleast_2d(X) @ self.W)
                                   + self.b)


class GaussRFF:
    """Random Fourier features for non-periodic inputs (used on psi)."""

    def __init__(self, dim, n_feat=500, bw=1.0, seed=0):
        rng = np.random.default_rng(seed)
        self.W = rng.normal(0.0, 1.0 / bw, size=(dim, n_feat))
        self.b = rng.random(n_feat) * 2 * np.pi
        self.scale = np.sqrt(2.0 / n_feat)

    def __call__(self, X):
        return self.scale * np.cos(np.atleast_2d(X) @ self.W + self.b)


def ridge_fit(Phi, Y, lam=1e-6):
    A = Phi.T @ Phi + lam * len(Phi) * np.eye(Phi.shape[1])
    return np.linalg.solve(A, Phi.T @ Y)


def collect_rollouts(env, n_traj=600, T=30, seed=1):
    """Random-DISCRETE-action rollouts.  Returns (S, A1) with A1 the action
    index taken at each step."""
    rng = np.random.default_rng(seed)
    S = np.empty((n_traj, T, env.dim))
    A1 = np.empty((n_traj, T), dtype=int)
    s = env.sample_state(rng, n_traj)
    for t in range(T):
        S[:, t] = s
        a1 = rng.integers(0, N_A, n_traj)
        a2 = rng.integers(0, N_A, n_traj)
        A1[:, t] = a1
        s = env.step(s, CONTROLS[a1], CONTROLS[a2], rng)
    return S, A1


def learn_abstraction(env, S, A1, H=5, n_feat=800, seed=2):
    """Action-conditioned multi-horizon goal prediction.

    Returns (rff, [W_a for a in actions]); psi(s) is the concatenation over
    actions of the H-horizon goal predictions, i.e. 3*H dimensions.
    """
    n_traj, T, d = S.shape
    goal = env.at_goal(S).astype(float)
    rff = TorusRFF(d, n_feat=n_feat, fmax=1, seed=seed)
    Ws = []
    for a in range(N_A):
        Xs, Ys = [], []
        for t in range(T - H):
            mask = A1[:, t] == a
            if mask.sum() == 0:
                continue
            Xs.append(S[mask, t])
            Ys.append(np.stack([goal[mask, t + h] for h in range(1, H + 1)],
                               axis=1))
        X = np.concatenate(Xs); Y = np.concatenate(Ys)
        Ws.append(ridge_fit(rff(X), Y))
    return rff, Ws


def psi(rff, Ws, s):
    F = rff(s)
    return np.concatenate([F @ W for W in Ws], axis=1)


def learn_readout(env, X, R, seed=3, n_feat=500):
    """Readout from a representation R to the circular offset, as (cos, sin).

    Trained offline on rollouts.  Every encoder gets the same class of readout,
    so the comparison isolates WHAT IS QUANTISED rather than who decodes better.
    """
    e = env.offset(X)
    Y = np.stack([np.cos(2 * np.pi * e), np.sin(2 * np.pi * e)], axis=1)
    bw = max(R.std(), 1e-6) * 2.0
    rff = GaussRFF(R.shape[1], n_feat=n_feat, bw=bw, seed=seed)
    W = ridge_fit(rff(R), Y)
    return rff, W


def readout_offset(rff, W, r):
    cs = rff(r) @ W
    return np.arctan2(cs[:, 1], cs[:, 0]) / (2 * np.pi)


class Quantizer:
    """k-means codebook.  Rate = log2(n_codes) bits per transmission."""

    def __init__(self, n_codes, seed=0):
        self.M = int(n_codes)
        self.seed = seed
        self.C = None

    def fit(self, X, iters=30):
        rng = np.random.default_rng(self.seed)
        idx = rng.choice(len(X), size=min(self.M, len(X)), replace=False)
        C = X[idx].copy()
        for _ in range(iters):
            a = self.assign(X, C)
            for j in range(len(C)):
                mask = a == j
                if mask.any():
                    C[j] = X[mask].mean(axis=0)
        self.C = C
        return self

    @staticmethod
    def assign(X, C):
        return (((X[:, None, :] - C[None, :, :]) ** 2).sum(-1)).argmin(1)

    def encode(self, X):
        return self.assign(np.atleast_2d(X), self.C)

    def decode(self, i):
        return self.C[i]
