"""
Theorem 14' — the bandwidth law with a WRONG model, stated in cross-entropy.

Theorem 14 assumed the agent's predictive code is built from the TRUE quotient
kernel P.  Real agents code with a learned model Q.  Claim:

  (a) eps_Q(C) <= Pr_{x~P}[ -log2 Q(x|b) > C ]
      -- the same list-covering proof, applied to Q.  The governing variable is
      the per-step CROSS-ENTROPY of the agent's own model, not the true entropy.
  (b) E[-log2 Q] = h_theta + KL(P_theta || Q_theta)
      -- so model error raises the required capacity by exactly KL bits/step.
  (c) Lemma (only task-relevant error is charged):
         KL(P_theta || Q_theta)  <=  KL(P || Q)
      where Q_theta(B'|b) = sum_{s in b} mu(s|b) Q(B'|s).
      Proof: coarse-graining successors (data processing) + averaging the
      conditioning states (joint convexity of KL).
      Sharp corollary: a model that is wrong ONLY about task-irrelevant
      structure pays ZERO extra bandwidth.

Tests:
  T1  quotient-level mismatch: violations of (a), and the identity (b).
  T2  physical model wrong only about the weather (task-irrelevant):
      KL_phys > 0 but KL_theta must be exactly 0.
  T3  physical model wrong about positions (task-relevant):
      0 < KL_theta <= KL_phys.
"""
import math
import numpy as np
from env import RendezvousTorus
from refine import refine
from theorem14 import block_chain


def per_row_topM_mass(P, Q, M):
    """For each row b: mass under P of the top-M successors ranked by Q."""
    order = np.argsort(-Q, axis=1)[:, :M]
    return np.take_along_axis(P, order, axis=1).sum(1)


def test1():
    env = RendezvousTorus(grid_size=6, m=3, K=1)
    s2b, nb = refine(env.num_states, env.num_actions, env.labels,
                     env.transitions_for_action)
    P, mu = block_chain(env, s2b, nb)
    rng = np.random.default_rng(0)
    R = rng.random((nb, nb)); R /= R.sum(1, keepdims=True)
    h = -np.sum(mu[:, None] * P * np.log2(np.where(P > 0, P, 1)))
    print("T1  quotient-level mismatch  (m=3, 9 blocks, h_theta=%.4f)" % h)
    print("   lambda   KL(P||Q)   E[-log Q]   h+KL      viol/9   C*(0.3)")
    viol_total = 0
    for lam in (0.0, 0.1, 0.3, 0.6, 0.9):
        Q = (1 - lam) * P + lam * R
        ce = -np.sum(mu[:, None] * P * np.log2(np.where(P > 0, Q, 1)))
        kl = ce - h
        v = 0; cs = None
        for M in range(1, nb + 1):
            C = math.log2(M)
            eps = 1 - np.sum(mu * per_row_topM_mass(P, Q, M))
            bound = np.sum(mu[:, None] * P * ((-np.log2(np.where(Q > 0, Q, 1e-300)) > C + 1e-12) & (P > 0)))
            if eps > bound + 1e-9:
                v += 1
            if cs is None and eps <= 0.3:
                cs = C
        viol_total += v
        print("   %4.1f    %8.4f   %9.4f   %8.4f   %d/9     %.3f" % (lam, kl, ce, h + kl, v, cs))
    print("   total violations of (a): %d" % viol_total)


def physical_kl(env, s2b, nb, Qfun):
    src, dst, prob = env.uniform_policy_chain()
    S = env.num_states
    # stationary distribution of P
    mu = np.full(S, 1.0 / S)
    for _ in range(300):
        m2 = np.bincount(dst, weights=mu[src] * prob, minlength=S)
        m2 /= m2.sum()
        if np.abs(m2 - mu).sum() < 1e-14:
            mu = m2; break
        mu = m2
    q = Qfun(src, dst, prob)
    # renormalise Q per source row
    rs = np.bincount(src, weights=q, minlength=S)
    q = q / rs[src]
    kl_phys = float(np.sum(mu[src] * prob * np.log2(prob / q)))
    # quotient kernels, aggregated with P's stationary weights
    key = s2b[src] * nb + s2b[dst]
    mub = np.bincount(s2b, weights=mu, minlength=nb)
    Pt = np.bincount(key, weights=mu[src] * prob, minlength=nb * nb).reshape(nb, nb) / mub[:, None]
    Qt = np.bincount(key, weights=mu[src] * q, minlength=nb * nb).reshape(nb, nb) / mub[:, None]
    nz = Pt > 1e-15
    kl_t = float(np.sum((mub[:, None] * Pt * np.log2(np.where(nz, Pt / Qt, 1)))[nz]))
    return kl_phys, kl_t


def test2_3():
    env = RendezvousTorus(grid_size=6, m=2, K=4)
    s2b, nb = refine(env.num_states, env.num_actions, env.labels,
                     env.transitions_for_action)
    K = env.K
    print("\nT2  model wrong ONLY about the weather (task-irrelevant), m=2 K=4")
    print("   q_weather                     KL_phys    KL_theta")
    for qw in ([0.4, 0.2, 0.2, 0.2], [0.7, 0.1, 0.1, 0.1], [0.97, 0.01, 0.01, 0.01]):
        qw = np.array(qw)
        kp, kt = physical_kl(env, s2b, nb,
                             lambda s, d, p, qw=qw: p * K * qw[d % K])
        print("   %-28s %8.4f   %10.2e" % (str(qw.tolist()), kp, kt))
    # NOTE: a first version mixed P with "uniform over P's support".  Under the
    # uniform reference policy P is ALREADY uniform over its support, so that
    # perturbation was the identity (KL = 0 everywhere) -- the same cancellation
    # trap recorded in paper §11.2.  Replaced by a directional bias on agent 1's
    # x-moves, which changes the relative-offset dynamics and is task-relevant.
    print("\nT3a model wrong about agent-1 x-drift (task-relevant)")
    print("   beta     KL_phys    KL_theta   ratio")
    N = env.N
    for beta in (0.3, 0.8, 1.5):
        def Qf(s, d, p, beta=beta):
            dx = (env.x1_of[d] - env.x1_of[s]) % N
            dx = np.where(dx == N - 1, -1, dx)
            return p * np.exp(beta * dx)
        kp, kt = physical_kl(env, s2b, nb, Qf)
        print("   %4.1f    %8.4f   %8.4f   %.3f" % (beta, kp, kt, kt / kp))
    print("\nT3b mixed error: wrong weather AND x-drift (beta=0.8, q_w=[.7,.1,.1,.1])")
    qw = np.array([0.7, 0.1, 0.1, 0.1])
    def Qm(s, d, p):
        dx = (env.x1_of[d] - env.x1_of[s]) % N
        dx = np.where(dx == N - 1, -1, dx)
        return p * np.exp(0.8 * dx) * K * qw[d % K]
    kp, kt = physical_kl(env, s2b, nb, Qm)
    print("   KL_phys=%.4f   KL_theta=%.4f   ratio=%.3f" % (kp, kt, kt / kp))


if __name__ == "__main__":
    test1()
    test2_3()
