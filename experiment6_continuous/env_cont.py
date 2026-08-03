"""
Experiment 6 — continuous-state environment.  The frontal test of "tabular death".

WHAT IS BEING RISKED.  All 14 theorems assume finite states, enumerable
partitions, and a known or estimable transition kernel.  The named most-likely
death mode for TIC is that none of this survives continuous, high-dimensional
state with function approximation -- the precedent being that bisimulation
metrics are mathematically clean and have always scaled badly.  Nothing in
Experiments 1-5 tested this: 20,736 states is still a table.

Here there is NO table anywhere:
  * state is a real vector in [0,1)^d, d up to ~20; no enumeration exists;
  * partition refinement is not merely slow but undefined;
  * the task abstraction must be LEARNED from sampled rollouts by function
    approximation, never given;
  * h_theta itself is not directly definable -- differential entropy is
    coordinate-dependent and can be negative.  The continuum replacement is a
    RATE-DISTORTION quantity R_theta(D), which is why Theorem 14's tolerance
    parameter is not a patch here but a precondition: the zero-error bandwidth
    law literally cannot be stated in the continuum (it would demand infinite
    rate for any continuous variable).

STRUCTURE.  Two agents on the circle [0,1).  Task: rendezvous, |x1 - x2|_circ
< delta, held L consecutive steps.  The operational variable is the circular
offset e = (x1 - x2) mod 1 -- ONE dimension, regardless of how many dimensions
the physical state has.  Task-irrelevant coordinates (each agent's y, plus
n_irr extra random-walk coordinates) inflate the physical state without
touching the task.

Because the offset lives on a circle, it is a genuinely NONLINEAR function of
the raw coordinates: no linear map recovers it.  Any encoder must do real
function approximation.
"""

import numpy as np


class ContinuousRendezvous:
    def __init__(self, n_irr=0, sigma=0.05, delta=0.06, seed=0):
        """n_irr: number of task-irrelevant coordinates PER AGENT (beyond y)."""
        self.n_irr = int(n_irr)
        self.sigma = float(sigma)
        self.delta = float(delta)
        # observation layout: [x1, y1, irr1..., x2, y2, irr2...]
        self.per_agent = 2 + self.n_irr
        self.dim = 2 * self.per_agent
        self.rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------ state
    def sample_state(self, rng, n=1):
        return rng.random((n, self.dim))

    def offset(self, s):
        """Signed circular offset e in (-0.5, 0.5]:  the operational variable."""
        x1 = s[..., 0]
        x2 = s[..., self.per_agent]
        e = (x1 - x2) % 1.0
        return np.where(e > 0.5, e - 1.0, e)

    def at_goal(self, s):
        return np.abs(self.offset(s)) < self.delta

    # -------------------------------------------------------------- dynamics
    def step(self, s, u1, u2, rng):
        """u1, u2 are the agents' control displacements applied to x only.

        Every coordinate also receives independent Gaussian innovation, so the
        irrelevant coordinates are genuinely stochastic (they cost rate to
        track) but never enter the goal.
        """
        s = s.copy()
        noise = rng.normal(0.0, self.sigma, s.shape)
        s += noise
        s[..., 0] += u1
        s[..., self.per_agent] += u2
        return s % 1.0

    def random_control(self, rng, n):
        return (rng.normal(0.0, self.sigma, n),
                rng.normal(0.0, self.sigma, n))

    # ------------------------------------------------- analytic rate reference
    def offset_innovation_sd(self):
        """Per-step innovation sd of the offset process e.

        e_{t+1} = e_t + (u1 - u2) + (eta1 - eta2); the two agent noises are
        independent, so the uncontrolled innovation sd is sigma*sqrt(2).
        """
        return self.sigma * np.sqrt(2.0)

    def R_theta(self, D):
        """Sequential (causal) rate-distortion reference for tracking a
        Gauss-Markov offset within mean-squared distortion D:

            R(D) ~ max(0, 0.5 * log2(sigma_e^2 / D))    bits/step

        This is the continuum stand-in for h_theta.  It is 1-DIMENSIONAL no
        matter how many physical dimensions exist -- which is precisely the
        prediction under test.
        """
        se2 = self.offset_innovation_sd() ** 2
        return max(0.0, 0.5 * np.log2(se2 / D))

    def R_phys(self, D):
        """Same quantity for tracking the WHOLE physical state to distortion D
        per coordinate: d times the per-coordinate rate.  This is what a
        state-aware encoder must pay."""
        return self.dim * max(0.0, 0.5 * np.log2(self.sigma ** 2 / D))
