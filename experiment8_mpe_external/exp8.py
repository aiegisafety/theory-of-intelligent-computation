"""
Experiment 8 — the bandwidth law on an environment we did not design.

Every previous experiment ran in an environment built by us.  That is the single
largest weakness of the whole programme (paper §17.2): a theory tested only
inside its author's own simulators has not been tested against anything.

This runs on **PettingZoo / mpe2 `simple_spread_v3`** (Lowe et al., NeurIPS 2017)
-- a standard, published, widely used multi-agent benchmark.  Its physics,
reward, observation layout and action semantics are fixed by the package and we
change none of them.  (The only local modification is a stub for `pygame`, which
mpe2 imports at construction time solely to build a drawing surface; the
integrator, reward and observation code are the unmodified package.)

THE TASK.  N agents must cover N landmarks; reward penalises each landmark's
distance to its nearest agent, plus collisions.  The coordination content is an
ASSIGNMENT -- agents should take DIFFERENT landmarks.  So what agent i needs to
know about agent j is not j's precise position but WHICH LANDMARK j IS TAKING.

    physical variable   j's own observation block     8 continuous dims
    task variable       j's landmark assignment       log2(3) = 1.58 bits

WHO ENCODES WHAT.  Agent j knows its own observation exactly, so it can compute
its own assignment.  Each step it sends C bits about itself; agent i decodes and
treats the result as "the landmark j is claiming", then takes the nearest
landmark not claimed by anyone else.

Three encoders at matched rate C = log2 M:

  phys     quantise j's own physical block (position + landmark offsets), and
           decode ANALYTICALLY -- the receiver recomputes the assignment in
           closed form from the decoded vector.  This deliberately gives the
           baseline the strongest possible decoder.
  learned  quantise psi(o_j), a LEARNED abstraction (ridge on random Fourier
           features, never told the observation layout or which landmark
           matters), decoded by argmax.  Every approximation error counts
           AGAINST the hypothesis under test.
  oracle   quantise the true assignment index.

PREDICTION.  `oracle` should saturate by C ~ 1.58 bits; `learned` should track
it closely; `phys` should need substantially more bits for the same return.

FALSIFICATION.  If `phys` matches `learned` at matched C, then coordination is
NOT priced by the task abstraction on an environment we did not design, and the
programme's central result does not generalise beyond our own simulators.

Anti-trap rule #7 (channel ablation) is enforced throughout.
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pygame_stub"))
from mpe2 import simple_spread_v3   # noqa: E402

N_AGENTS = 3
MAX_CYCLES = 25
ACT_NOOP, ACT_LEFT, ACT_RIGHT, ACT_DOWN, ACT_UP = 0, 1, 2, 3, 4


# observation layout of simple_spread (fixed by the package):
#   [self_vel(2), self_pos(2), landmark_rel(2N), other_agent_rel(2(N-1)),
#    comm(2(N-1))]
def parse_obs(o, n=N_AGENTS):
    return (o[0:2], o[2:4], o[4:4 + 2 * n].reshape(n, 2),
            o[4 + 2 * n:4 + 2 * n + 2 * (n - 1)].reshape(n - 1, 2))


def sender_block(o, n=N_AGENTS):
    """The physical description agent j would transmit about itself:
    its velocity, its position, and its offsets to the landmarks."""
    v, p, lm, _ = parse_obs(o, n)
    return np.concatenate([v, p, lm.reshape(-1)])


def assignment_from_block(vec, n=N_AGENTS):
    """Analytic decoder for `phys`: recompute the nearest landmark in closed
    form from a (possibly quantised) sender block."""
    lm = vec[4:4 + 2 * n].reshape(n, 2)
    return int(np.argmin((lm ** 2).sum(1)))


def my_target(o, n=N_AGENTS):
    _, _, lm, _ = parse_obs(o, n)
    return int(np.argmin((lm ** 2).sum(1)))


# ---------------------------------------------------------------- controller
def act_toward(vec, rng, eps=0.0):
    if eps and rng.random() < eps:
        return int(rng.integers(5))
    dx, dy = float(vec[0]), float(vec[1])
    if abs(dx) < 1e-9 and abs(dy) < 1e-9:
        return ACT_NOOP
    if abs(dx) >= abs(dy):
        return ACT_RIGHT if dx > 0 else ACT_LEFT
    return ACT_UP if dy > 0 else ACT_DOWN


def choose_action(o, claimed, rng, eps=0.0, n=N_AGENTS):
    """Take the nearest landmark not believed claimed by another agent.

    `claimed` is the ONLY channel-borne input; the agent's own observation is
    private and exact.  Nothing about the others' true state reaches this
    function except through `claimed`.
    """
    _, _, lm, _ = parse_obs(o, n)
    order = np.argsort((lm ** 2).sum(1))
    for k in order:
        if int(k) not in claimed:
            return act_toward(lm[k], rng, eps), int(k)
    k = int(order[0])
    return act_toward(lm[k], rng, eps), k


# -------------------------------------------------------------------- data
def collect(n_ep=250, seed=0, eps=0.25):
    env = simple_spread_v3.parallel_env(N=N_AGENTS, local_ratio=0.5,
                                        max_cycles=MAX_CYCLES,
                                        continuous_actions=False)
    rng = np.random.default_rng(seed)
    X, Y = [], []
    for ep in range(n_ep):
        obs, _ = env.reset(seed=seed * 7919 + ep)
        for t in range(MAX_CYCLES):
            if not env.agents:
                break
            tgt = {a: my_target(obs[a]) for a in env.agents}
            acts = {}
            for a in env.agents:
                claimed = {tgt[b] for b in env.agents if b != a}
                acts[a], _ = choose_action(obs[a], claimed, rng, eps)
                X.append(sender_block(obs[a]))
                Y.append(tgt[a])
            obs, r, term, trunc, info = env.step(acts)
    env.close()
    return np.array(X), np.array(Y)


# ------------------------------------------------------ learned abstraction
class RFF:
    def __init__(self, dim, n_feat=500, bw=1.0, seed=0):
        rng = np.random.default_rng(seed)
        self.W = rng.normal(0, 1.0 / bw, (dim, n_feat))
        self.b = rng.random(n_feat) * 2 * np.pi
        self.s = np.sqrt(2.0 / n_feat)

    def __call__(self, X):
        return self.s * np.cos(np.atleast_2d(X) @ self.W + self.b)


def ridge(P, Y, lam=1e-6):
    return np.linalg.solve(P.T @ P + lam * len(P) * np.eye(P.shape[1]), P.T @ Y)


def learn_abstraction(X, Y, seed=1, n_feat=500):
    """psi(o) = predicted one-hot assignment.  The learner sees only the raw
    block and a scalar label; it is not told the layout."""
    T = np.eye(N_AGENTS)[Y].astype(float)
    bw = max(float(X.std()), 1e-6) * 2.0
    rff = RFF(X.shape[1], n_feat=n_feat, bw=bw, seed=seed)
    W = ridge(rff(X), T)
    return lambda Z: rff(Z) @ W


class Quantizer:
    def __init__(self, M, seed=0):
        self.M, self.seed, self.C = int(M), seed, None

    def fit(self, X, iters=25):
        rng = np.random.default_rng(self.seed)
        idx = rng.choice(len(X), size=min(self.M, len(X)), replace=False)
        C = X[idx].copy()
        for _ in range(iters):
            a = self.assign(X, C)
            for j in range(len(C)):
                m = a == j
                if m.any():
                    C[j] = X[m].mean(0)
        self.C = C
        return self

    @staticmethod
    def assign(X, C):
        return (((X[:, None, :] - C[None, :, :]) ** 2).sum(-1)).argmin(1)

    def encode(self, X):
        return self.assign(np.atleast_2d(X), self.C)

    def decode(self, i):
        return self.C[i]
