"""V3 §9.5: in-domain failure of Cor 9.6 when one value of the per-step information carries >= 60% of its mass."""
import numpy as np
from chains import h_sigma_W
rng = np.random.default_rng(3); K = 32
for top, nrest in ((0.85, 4), (0.85, 8), (0.7, 4)):
    T = np.zeros((K, K))
    for i in range(K):
        idx = rng.choice(K, 2 + nrest, replace=False)
        T[i, idx[:2]] = top / 2; T[i, idx[2:]] = (1 - top) / nrest
    h, s, W = h_sigma_W(T)
    print("top mass %.2f on 2 successors, rest on %d: h=%.3f sigma=%.3f sigma/h=%.3f W/sigma=%.3f" % (top, nrest, h, s, s / h, W / s))
