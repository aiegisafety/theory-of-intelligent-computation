"""Analysis: locate the collapse threshold and test the three predictions."""
import json
import numpy as np

R = json.load(open("results.json"))
LEVEL = 0.5   # threshold definition: first C at which success crosses 0.5


def curve(N, m, K, mode):
    rows = [r for r in R if r["N"] == N and r["m"] == m and r["K"] == K
            and r["mode"] == mode and not r["scramble"]]
    rows.sort(key=lambda r: r["C"])
    return np.array([r["C"] for r in rows]), np.array([r["success_mean"] for r in rows])


def threshold(C, y, level=LEVEL):
    """First crossing of `level`, linearly interpolated. None if never crossed."""
    for i in range(1, len(y)):
        if y[i - 1] < level <= y[i]:
            if y[i] == y[i - 1]:
                return float(C[i])
            t = (level - y[i - 1]) / (y[i] - y[i - 1])
            return float(C[i - 1] + t * (C[i] - C[i - 1]))
    return None if y.max() < level else float(C[0])


def meta(N, m, K):
    r = [x for x in R if x["N"] == N and x["m"] == m and x["K"] == K][0]
    return r["num_states"], r["n_blocks"], r["h"], r["h_theta"]


CFG = [(6, m, 1, "base") for m in (2, 3, 6)] + \
      [(6, m, 4, "highH") for m in (2, 3, 6)] + \
      [(12, m, 1, "bigS") for m in (2, 3, 6)]

print("=" * 100)
print("TABLE 1 — configurations and measured rates")
print("=" * 100)
print(f"{'tag':6s} {'N':>3s} {'m':>2s} {'K':>2s} {'|S|':>7s} {'blocks':>7s} "
      f"{'h':>7s} {'h_theta':>8s} {'C*_class':>9s} {'C*_state':>9s}")
rows_t1 = []
for (N, m, K, tag) in CFG:
    S, nb, h, ht = meta(N, m, K)
    tc = threshold(*curve(N, m, K, "class"))
    ts = threshold(*curve(N, m, K, "state"))
    rows_t1.append(dict(tag=tag, N=N, m=m, K=K, S=S, nb=nb, h=h, ht=ht,
                        tc=tc, ts=ts))
    f = lambda v: f"{v:9.2f}" if v is not None else "     none"
    print(f"{tag:6s} {N:3d} {m:2d} {K:2d} {S:7d} {nb:7d} {h:7.3f} {ht:8.3f}"
          f"{f(tc)}{f(ts)}")

print()
print("=" * 100)
print("PREDICTION 1 — the class-aware threshold tracks h_theta, not h")
print("=" * 100)
print(f"{'tag':6s} {'m':>2s} {'h':>7s} {'h_theta':>8s} {'C*_class':>9s} "
      f"{'C*-h_theta':>11s} {'C*-h':>8s}")
d_ht, d_h = [], []
for r in rows_t1:
    if r["tc"] is None:
        continue
    print(f"{r['tag']:6s} {r['m']:2d} {r['h']:7.3f} {r['ht']:8.3f} "
          f"{r['tc']:9.2f} {r['tc']-r['ht']:11.2f} {r['tc']-r['h']:8.2f}")
    d_ht.append(r["tc"] - r["ht"]); d_h.append(r["tc"] - r["h"])
print(f"\n  spread of (C* - h_theta): {np.std(d_ht):.3f} bits   "
      f"mean offset {np.mean(d_ht):+.3f}")
print(f"  spread of (C* - h)      : {np.std(d_h):.3f} bits   "
      f"mean offset {np.mean(d_h):+.3f}")
print("  -> the quantity with the SMALLER spread is the one the threshold "
      "actually tracks.")

print()
print("=" * 100)
print("PREDICTION 2 — raising h by +2.000 bits (K=1 -> K=4) at fixed h_theta")
print("                must NOT move the class-aware threshold")
print("=" * 100)
print(f"{'m':>2s} {'h(K=1)':>7s} {'h(K=4)':>7s} {'dh':>6s} "
      f"{'h_th(K=1)':>10s} {'h_th(K=4)':>10s} {'C*(K=1)':>8s} {'C*(K=4)':>8s} {'dC*':>6s}")
for m in (2, 3, 6):
    a = [r for r in rows_t1 if r["m"] == m and r["K"] == 1 and r["N"] == 6][0]
    b = [r for r in rows_t1 if r["m"] == m and r["K"] == 4][0]
    if a["tc"] is None or b["tc"] is None:
        print(f"{m:2d}   (difficulty-limited: no 0.5 crossing; excluded)")
        continue
    dc = b["tc"] - a["tc"]
    print(f"{m:2d} {a['h']:7.3f} {b['h']:7.3f} {b['h']-a['h']:6.3f} "
          f"{a['ht']:10.3f} {b['ht']:10.3f} {a['tc']:8.2f} {b['tc']:8.2f} {dc:6.2f}")

print()
print("=" * 100)
print("PREDICTION 3 — multiplying |S| by 16 (N=6 -> N=12) at fixed h_theta")
print("                must NOT move the class-aware threshold")
print("=" * 100)
print(f"{'m':>2s} {'|S|(N=6)':>9s} {'|S|(N=12)':>10s} {'h_th(6)':>8s} "
      f"{'h_th(12)':>9s} {'C*(6)':>7s} {'C*(12)':>7s} {'dC*':>6s}")
for m in (2, 3, 6):
    a = [r for r in rows_t1 if r["m"] == m and r["K"] == 1 and r["N"] == 6][0]
    b = [r for r in rows_t1 if r["m"] == m and r["N"] == 12][0]
    if a["tc"] is None or b["tc"] is None:
        print(f"{m:2d}   (difficulty-limited: no 0.5 crossing; excluded)")
        continue
    dc = b["tc"] - a["tc"]
    print(f"{m:2d} {a['S']:9d} {b['S']:10d} {a['ht']:8.3f} {b['ht']:9.3f} "
          f"{a['tc']:7.2f} {b['tc']:7.2f} {dc:6.2f}")

print()
print("=" * 100)
print("PREDICTION 4 (DOUBLE DISSOCIATION) — the decisive test")
print("  A: hold |S| and h EXACTLY fixed, vary h_theta  -> threshold MUST move")
print("  B: hold h_theta EXACTLY fixed, vary h and |S|   -> threshold MUST NOT")
print("=" * 100)
print("A) within a fixed environment (|S|=1296, h=4.644 for all rows):")
for tag, N, K in [("base", 6, 1)]:
    for m in (2, 3):
        r = [x for x in rows_t1 if x["m"] == m and x["N"] == N and x["K"] == K][0]
        print(f"   m={m}: |S|={r['S']}  h={r['h']:.3f} (fixed)  "
              f"h_theta={r['ht']:.3f}  C*={r['tc']:.2f}")
a2 = [x for x in rows_t1 if x["m"] == 2 and x["N"] == 6 and x["K"] == 1][0]
a3 = [x for x in rows_t1 if x["m"] == 3 and x["N"] == 6 and x["K"] == 1][0]
print(f"   => d(h_theta)={a3['ht']-a2['ht']:+.3f} bits produced "
      f"d(C*)={a3['tc']-a2['tc']:+.3f} bits, with h and |S| held constant.")
print("\nB) holding h_theta fixed and moving everything else:")
for m in (2, 3):
    base = [x for x in rows_t1 if x["m"] == m and x["N"] == 6 and x["K"] == 1][0]
    hi = [x for x in rows_t1 if x["m"] == m and x["K"] == 4][0]
    bg = [x for x in rows_t1 if x["m"] == m and x["N"] == 12][0]
    print(f"   m={m} (h_theta={base['ht']:.3f} in all three):")
    print(f"      h  {base['h']:.3f} -> {hi['h']:.3f} (+{hi['h']-base['h']:.3f}) : "
          f"C* {base['tc']:.2f} -> {hi['tc']:.2f}  (d={hi['tc']-base['tc']:+.2f})")
    print(f"      |S| {base['S']} -> {bg['S']} (x{bg['S']//base['S']})        : "
          f"C* {base['tc']:.2f} -> {bg['tc']:.2f}  (d={bg['tc']-base['tc']:+.2f})")

print()
print("=" * 100)
print("CONTROL — channel ablation (all transmitted symbols randomised)")
print("   if these are NOT near zero, decisions are bypassing the channel")
print("=" * 100)
for (N, m, K, tag) in CFG:
    ab = [r for r in R if r["N"] == N and r["m"] == m and r["K"] == K
          and r["scramble"]]
    best = max([r["success_mean"] for r in R
                if r["N"] == N and r["m"] == m and r["K"] == K
                and r["mode"] == "class" and not r["scramble"]])
    s = "  ".join(f"{r['mode']}={r['success_mean']:.3f}" for r in ab)
    print(f"{tag:6s} N={N:2d} m={m}: best class success={best:.3f}   ablated: {s}")

print()
print("=" * 100)
print("FULL CURVES (success rate, 60 seeds each)")
print("=" * 100)
for (N, m, K, tag) in CFG:
    C, yc = curve(N, m, K, "class")
    _, ys = curve(N, m, K, "state")
    S, nb, h, ht = meta(N, m, K)
    print(f"\n{tag} N={N} m={m} K={K} |S|={S} blocks={nb} "
          f"h={h:.3f} h_theta={ht:.3f}")
    print("  C     : " + " ".join(f"{c:5.2f}" for c in C))
    print("  class : " + " ".join(f"{v:5.2f}" for v in yc))
    print("  state : " + " ".join(f"{v:5.2f}" for v in ys))
