"""V3 §9.5: is sigma_theta <~ h_theta sufficient for Corollary 9.6?  W(20-80)/sigma over 48 chains."""
import numpy as np
from chains import families, h_sigma_W

rows = []
for fam, K, par, T in families(np.random.default_rng(7)):
    h, s, W = h_sigma_W(T)
    rows.append((fam, K, par, h, s, W / s))
inn = [r for r in rows if r[4] <= r[3]]; out = [r for r in rows if r[4] > r[3]]
for name, g in (("sigma<=h", inn), ("sigma>h", out)):
    v = np.array([r[5] for r in g])
    print("%-9s n=%2d  W/sigma = %.3f +- %.3f  range [%.3f, %.3f]" % (name, len(g), v.mean(), v.std(), v.min(), v.max()))
for fam in ("dirichlet", "zipf", "mixture"):
    v = np.array([r[5] for r in inn if r[0] == fam])
    if len(v): print("  in-domain %-9s n=%2d  %.3f +- %.3f  range [%.3f, %.3f]" % (fam, len(v), v.mean(), v.std(), v.min(), v.max()))
print("in-domain chains with W/sigma < 0.5:")
for r in inn:
    if r[5] < 0.5: print("  ", r[0], r[1], r[2], "sigma/h=%.3f W/sigma=%.3f" % (r[4] / r[3], r[5]))
