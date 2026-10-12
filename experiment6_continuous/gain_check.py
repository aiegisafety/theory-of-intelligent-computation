"""V3 §12.5: sensitivity of the operational-variable encoder to the controller gain.
Each agent displaces by GAIN*0.5*e_hat (GAIN=0.9 is the book's controller: 0.45 e_hat per agent)."""
import numpy as np, exp6
from env_cont import ContinuousRendezvous
from learn import Quantizer
env = ContinuousRendezvous(n_irr=0)
S = env.sample_state(np.random.default_rng(0), 20000)
E = env.offset(S).reshape(-1, 1)
pack = dict(rep=lambda Z: env.offset(np.atleast_2d(Z)).reshape(-1, 1), dec=lambda R: R[:, 0],
            quant={M: Quantizer(M, seed=0).fit(E) for M in (2, 8)})
for g in (0.9, 0.45):
    exp6.GAIN = g
    print("GAIN=%.2f" % g, {M: exp6.evaluate(env, {"opvar": pack}, "opvar", M, 200) for M in (2, 8)})
