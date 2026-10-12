"""V3: all figures of the book, drawn only from the book's own data files.

Inputs (paths relative to the repository root, override with TIC_ROOT):
  experiment5_discrete/data/results.json        Table 6.1, Figure 6.1
  experiment5_discrete/data/corollary14_3.json  Table 9.2, Figure 9.1b
  experiment6_continuous/exp6_results.json      Table 12.1, Figure 12.1
  experiment8_mpe_external/exp8_full.json       Table 14.1, Figure 14.1
  v3/v3_zero_delay_data.json                    Table 6.2, Figures 6.2, 6.3b
  v3/v3_error_propagation_data.json             Table 6.3, Figure 6.3a
  v3/v3_cor96_data.json                         Figure 9.2
  v3/v3_tolerance_data.json                     Figure 8.1
Figure 9.1a and Figure 10.1 are computed here from the operational chains themselves.
"""
import json, os, itertools, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.environ.get("TIC_ROOT", os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.environ.get("FIG_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))
os.makedirs(OUT, exist_ok=True)
J = lambda *p: json.load(open(os.path.join(ROOT, *p)))

BLUE, ORANGE, PURPLE, GREY, GREEN = "#1f6fb2", "#c8702a", "#8e63b0", "#808080", "#3f7f2a"
FAM = {"dirichlet": (BLUE, "o", "Dirichlet rows"), "zipf": (PURPLE, "^", "Zipf rows"),
       "mixture": (ORANGE, "s", "dominant successor")}
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 9.5, "axes.titlelocation": "left", "legend.frameon": False,
                     "savefig.dpi": 300, "savefig.bbox": "tight", "font.family": "DejaVu Sans"})


def panel(ax, letter):
    ax.text(-0.13, 1.06, letter, transform=ax.transAxes, fontsize=11, fontweight="bold", va="bottom")


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".png")); plt.close(fig); print("wrote", name)


def threshold(rows):
    rows = sorted(rows, key=lambda x: x["C"])
    for a, b in zip(rows, rows[1:]):
        if a["success_mean"] < 0.5 <= b["success_mean"]:
            return a["C"] + (0.5 - a["success_mean"]) * (b["C"] - a["C"]) / (b["success_mean"] - a["success_mean"])
    return None


# ---------------------------------------------------------------- Figure 6.1
def fig6_1():
    r = J("experiment5_discrete", "data", "results.json")
    cfgs = [(6, 2, 1, "N=6, K=1"), (6, 2, 4, "N=6, K=4"), (12, 2, 1, "N=12, K=1"),
            (6, 3, 1, "N=6, K=1"), (6, 3, 4, "N=6, K=4"), (12, 3, 1, "N=12, K=1")]
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.7))
    ax = axs[0]; panel(ax, "a")
    styles = {(6, 1): "-", (6, 4): "--", (12, 1): ":"}
    pts = []
    for N, m, K, lab in cfgs:
        rows = [x for x in r if (x["N"], x["m"], x["K"]) == (N, m, K) and x["mode"] == "class" and not x["scramble"]]
        rows.sort(key=lambda x: x["C"])
        col = BLUE if m == 2 else ORANGE
        ax.plot([x["C"] for x in rows], [x["success_mean"] for x in rows], styles[(N, K)], color=col, lw=1.6,
                label="m=%d, %s" % (m, lab))
        pts.append((rows[0]["h"], rows[0]["h_theta"], threshold(rows), m, N, K))
    rows = [x for x in r if (x["N"], x["m"], x["K"]) == (6, 2, 1) and x["mode"] == "state" and not x["scramble"]]
    rows.sort(key=lambda x: x["C"])
    ax.plot([x["C"] for x in rows], [x["success_mean"] for x in rows], "-", color=GREY, lw=1.4, label="physical encoder, m=2")
    best_scr = max(x["success_mean"] for x in r if x["scramble"] and x["m"] in (2, 3))
    ax.axhline(best_scr, color=GREY, lw=0.8, ls="-.")
    ax.axhline(0.5, color="k", lw=0.5, alpha=0.4)
    ax.set_xlabel("capacity $C$ (bits per step)"); ax.set_ylabel("success rate")
    ax.set_title("Block encoder: curves move with $m$ only")
    ax.legend(fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3); ax.set_ylim(-0.02, 1.0)
    ax = axs[1]; panel(ax, "b")
    for h, ht, c, m, N, K in pts:
        col = BLUE if m == 2 else ORANGE
        ax.plot(ht, c, "o", color=col, ms=6, mfc=col)
        ax.plot(h, c, "o", color=col, ms=6, mfc="white")
    ax.plot([], [], "o", color="k", mfc="k", label="against $h_\\theta$")
    ax.plot([], [], "o", color="k", mfc="white", label="against $h$")
    ax.text(2.0, 1.45, "$m=2$", color=BLUE, fontsize=8); ax.text(3.2, 2.15, "$m=3$", color=ORANGE, fontsize=8)
    ax.set_xlabel("rate (bits per step)"); ax.set_ylabel("threshold $C^*$ (bits per step)")
    ax.set_title("Thresholds cluster by $h_\\theta$, spread across $h$")
    ax.legend(fontsize=7.5, loc="center right"); ax.set_xlim(1.5, 7); ax.set_ylim(1.0, 2.5)
    fig.tight_layout(); save(fig, "fig6_1_dissociation")
    return pts


# ---------------------------------------------------------------- Figure 6.2
def fig6_2():
    d = J("v3", "v3_zero_delay_data.json")
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.1))
    ax = axs[0]; panel(ax, "a")
    names = {"torus m=2": ("torus rendezvous, $m=2$", ORANGE), "dirichlet K=32 a=1": ("Dirichlet rows, $\\alpha=1$", BLUE),
             "dirichlet K=32 a=0.2": ("Dirichlet rows, $\\alpha=0.2$", PURPLE)}
    for key, (lab, col) in names.items():
        e = [x for x in d["examples"] if x["name"] == key]
        C = [x["C"] for x in e]; h = e[0]["h"]
        ax.plot(C, [x["D"] for x in e], "o-", color=col, lw=1.6, label="%s, $h_\\theta$=%.2f" % (lab, h))
        ax.plot(C, [max(h - c, 0) for c in C], "--", color=col, lw=0.9)
    ax.plot([], [], "--", color=GREY, label="floor $\\max(h_\\theta-C,0)$")
    ax.set_xticks([1, 2, 3]); ax.set_xlabel("capacity $C$ (bits per step)"); ax.set_ylabel("$D_\\theta(C)$ (bits)")
    ax.set_title("Per-step floor $D_\\theta(C)$ and the floor of Cor. 6.7"); ax.legend(fontsize=7)
    ax = axs[1]; panel(ax, "b")
    for fam, (col, mk, lab) in FAM.items():
        f = [x for x in d["families"] if x["fam"] == fam]
        ax.plot([x["h"] for x in f], [x["pen2"] for x in f], mk, color=col, ms=5, alpha=0.85, label=lab, ls="none")
    ax.axhline(0, color=GREY, lw=0.6)
    ax.set_xlabel("intrinsic bandwidth $h_\\theta$ (bits per step)"); ax.set_ylabel("$\\Delta_\\theta(2)$ (bits)")
    ax.set_title("Zero-delay penalty at $C=2$, 48 chains"); ax.legend(fontsize=7.5)
    fig.tight_layout(); save(fig, "fig6_2_per_step_floor")


# ---------------------------------------------------------------- Figure 6.3
def fig6_3():
    e = [x for x in J("v3", "v3_error_propagation_data.json") if x["chain"].startswith("dirichlet")]
    d = J("v3", "v3_zero_delay_data.json")["bound"]
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.1))
    ax = axs[0]; panel(ax, "a")
    C = [x["C"] for x in e]
    ax.plot(C, [x["floor"] for x in e], "s--", color=GREY, label="floor $h_\\theta-C$")
    ax.plot(C, [x["D"] for x in e], "o-", color=BLUE, lw=1.8, label="$D_\\theta(C)$, previous state shared")
    ax.plot(C, [x["R"] for x in e], "^-", color=ORANGE, lw=1.8, label="myopic code, errors propagate")
    ax.fill_between(C, [x["D"] for x in e], [x["R"] for x in e], color=ORANGE, alpha=0.12)
    ax.set_xticks(C); ax.set_xlabel("capacity $C$ (bits per step)"); ax.set_ylabel("uncertainty about $B_{t+1}$ (bits)")
    ax.set_title("Propagating errors cost more than uneven rows"); ax.legend(fontsize=7.5)
    ax = axs[1]; panel(ax, "b")
    x = np.array(d["bound"]); y = np.array(d["deficit"])
    ax.plot(x, y, "o", color=BLUE, ms=3, alpha=0.6)
    lim = max(x.max(), y.max()) * 1.05; ax.plot([0, lim], [0, lim], "-", color=GREEN, lw=1.2)
    ax.text(0.55 * lim, 0.42 * lim, "bound = deficit", color=GREEN, fontsize=7.5, rotation=35)
    ax.set_xlabel("$\\log M-U(\\bar p,M)$, Proposition 6.13"); ax.set_ylabel("row deficit $\\log M-\\max_{\\mathcal{Q}} H(p_{\\mathcal{Q}})$")
    ax.set_title("The bound through the largest atom (%d rows)" % len(x))
    fig.tight_layout(); save(fig, "fig6_3_errors_and_bound")


# ---------------------------------------------------------------- Figure 8.1
def fig8_1():
    d = J("v3", "v3_tolerance_data.json")
    D = np.array(d["Delta"]); Ds = np.array(d["DeltaStar"]); L = np.array(d["limit"])
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.1))
    ax = axs[0]; panel(ax, "a")
    ax.loglog(D, L, "o", color=BLUE, ms=4, label="against $\\Delta$")
    ax.loglog(Ds, L, "^", color=ORANGE, ms=4, alpha=0.8, label="against $\\Delta^*$")
    g = np.logspace(-3.3, 0, 10); ax.loglog(g, g, "-", color=GREEN, lw=1); ax.loglog(g, g / 2, ":", color=GREY, lw=1)
    ax.text(0.0016, 0.0024, "limit $=$ separation", color=GREEN, fontsize=7.5, rotation=33)
    ax.set_xlabel("separation $\\Delta$ or $\\Delta^*$"); ax.set_ylabel("tolerance at which over-merging begins")
    ax.set_title("Theorem 8.2 holds in all 40 environments"); ax.legend(fontsize=7.5, loc="lower right")
    ax = axs[1]; panel(ax, "b")
    for n, col, ls in ((200, PURPLE, "--"), (5000, BLUE, "-")):
        s = sorted([x for x in d["sampled"] if x["n"] == n], key=lambda x: x["f"])
        ax.plot([x["f"] for x in s], [x["overmerge"] for x in s], "o" + ls, color=col, lw=1.6, label="$n=%d$ samples per state" % n)
    ax.axvline(1.0, color=GREY, ls="--", lw=0.8); ax.text(1.02, 0.12, "$\\epsilon=\\Delta^*$", color=GREY, fontsize=7.5)
    ax.set_xlabel("tolerance $\\epsilon$, as a multiple of $\\Delta^*$"); ax.set_ylabel("over-merging rate")
    ax.set_title("Above $\\Delta^*$ more data does not help (16 environments)"); ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout(); save(fig, "fig8_1_tolerance")


# ---------------------------------------------------------------- Figure 9.1
def torus_chain(m):
    mv = [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]
    inc = {}
    for a, b in itertools.product(mv, mv):
        k = ((a[0] - b[0]) % m, (a[1] - b[1]) % m); inc[k] = inc.get(k, 0) + 1 / 25
    st = [(x, y) for x in range(m) for y in range(m)]
    T = np.zeros((len(st), len(st)))
    for i, (x, y) in enumerate(st):
        for (dx, dy), p in inc.items():
            T[i, st.index(((x + dx) % m, (y + dy) % m))] += p
    return T


def fig9_1():
    T = torus_chain(3); K = len(T); mu = np.ones(K) / K
    v, w = [], []
    for i in range(K):
        for j in range(K):
            if T[i, j] > 0: v.append(-np.log2(T[i, j])); w.append(mu[i] * T[i, j])
    v = np.array(v); w = np.array(w); h = (v * w).sum(); s = np.sqrt(((v - h) ** 2 * w).sum())
    Cs = np.linspace(0, math.log2(K), 400)
    eps = [1 - np.mean([np.sort(T[i])[::-1][:int(2 ** c + 1e-9)].sum() for i in range(K)]) for c in Cs]
    tail = [w[v > c + 1e-12].sum() for c in Cs]
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.1))
    ax = axs[0]; panel(ax, "a")
    ax.plot(Cs, eps, "-", color=BLUE, lw=1.8, label="exact error, Theorem 9.4(a)")
    ax.plot(Cs, tail, "--", color=PURPLE, lw=1.5, label="tail bound $\\Pr[\\imath_t>C]$, 9.4(b)")
    ax.plot(Cs, [0.5 * math.erfc((c - h) / s / math.sqrt(2)) for c in Cs], ":", color=GREY, lw=1.5, label="normal approximation")
    ax.axvline(h, color=GREY, lw=0.8); ax.text(h + 0.04, 0.9, "$h_\\theta$", color=GREY)
    ax.set_xlabel("capacity $C$ (bits per step)"); ax.set_ylabel("per-step error")
    ax.set_title("Rendezvous, $m=3$: error is a tail probability"); ax.legend(fontsize=7.5, loc="lower left")
    ax = axs[1]; panel(ax, "b")
    c = J("experiment5_discrete", "data", "corollary14_3.json")
    for m, col in ((2, BLUE), (3, ORANGE)):
        rows = sorted([x for x in c if x["m"] == m and x["C50"] == x["C50"]], key=lambda x: x["n"])
        ax.plot([x["n"] for x in rows], [x["C50"] for x in rows], "o-", color=col, lw=1.6, label="$m=%d$" % m)
        ax.axhline(rows[0]["h_theta"], color=col, ls=":", lw=1)
        ax.text(11.3, rows[0]["h_theta"], "$h_\\theta$", color=col, va="center", fontsize=8)
    ax.set_xlabel("block length $n$ (steps of deferred commitment)"); ax.set_ylabel("threshold $C^*_n(0.5)$ (bits per step)")
    ax.set_title("Deferring commitment moves the threshold toward $h_\\theta$"); ax.legend(fontsize=7.5, loc="lower right")
    fig.tight_layout(); save(fig, "fig9_1_tail_and_blocks")
    return h, s


# ---------------------------------------------------------------- Figure 9.2
def fig9_2():
    d = J("v3", "v3_cor96_data.json")
    fig, ax = plt.subplots(figsize=(5.6, 3.2))
    for fam, (col, mk, lab) in FAM.items():
        f = [x for x in d if x["fam"] == fam]
        ax.plot([x["sigma"] / x["h"] for x in f], [x["ratio"] for x in f], mk, color=col, ms=5, alpha=0.85, ls="none", label=lab)
    ax.axhline(1.683, color=GREEN, lw=1.2); ax.axhspan(1.678 - 0.033, 1.678 + 0.033, color=GREEN, alpha=0.15)
    ax.text(1.62, 1.72, "normal value 1.683; Table 9.1: $1.678\\pm0.033$", color=GREEN, fontsize=7.5)
    ax.axvline(1.0, color=GREY, ls="--", lw=0.8); ax.text(1.02, 0.15, "$\\sigma_\\theta=h_\\theta$", color=GREY, fontsize=7.5)
    ax.plot([0.711], [0.0], "*", color="k", ms=10, label="dominant atom (§9.5)")
    ax.set_xlabel("$\\sigma_\\theta/h_\\theta$"); ax.set_ylabel("$W_{20\\text{-}80}/\\sigma_\\theta$")
    ax.legend(fontsize=7.5, loc="center right"); ax.set_ylim(-0.1, 2.4)
    fig.tight_layout(); save(fig, "fig9_2_normal_domain")


# ---------------------------------------------------------------- Figure 10.1
def fig10_1():
    # values printed by experiment5_discrete/theorem14prime.py (data/t14prime_out.txt)
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.0))
    ax = axs[0]; panel(ax, "a")
    q = ["(0.4, 0.2, 0.2, 0.2)", "(0.7, 0.1, 0.1, 0.1)", "(0.97, 0.01, 0.01, 0.01)"]
    phys = [0.0719, 0.6201, 2.9939]; task = [0.0, 0.0, 0.0]
    x = np.arange(3)
    ax.bar(x - 0.18, phys, 0.36, color=GREY, label="relative entropy, physical kernel")
    ax.bar(x + 0.18, task, 0.36, color=BLUE, label="relative entropy, operational kernel")
    for i in x: ax.text(i + 0.18, 0.05, "0", ha="center", color=BLUE, fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(q, fontsize=7); ax.set_xlabel("model of the weather (truth uniform)")
    ax.set_ylabel("bits per step"); ax.set_title("Wrong only about what the task ignores: free"); ax.legend(fontsize=7.5)
    ax = axs[1]; panel(ax, "b")
    lab = ["$\\beta=0.8$", "$\\beta=1.5$"]; x = np.arange(2)
    ax.bar(x - 0.27, [0.1827, 0.6238], 0.27, color=GREY, label="physical")
    ax.bar(x, [0.0021, 0.0217], 0.27, color=BLUE, label="task $m=2$ (parity)")
    ax.bar(x + 0.27, [0.0399, 0.1573], 0.27, color=ORANGE, label="task $m=3$")
    ax.set_xticks(x); ax.set_xticklabels(lab); ax.set_xlabel("error in the modelled drift of one agent")
    ax.set_ylabel("bits per step"); ax.set_title("The same error is priced by the task"); ax.legend(fontsize=7.5)
    fig.tight_layout(); save(fig, "fig10_1_mismatch")


# ---------------------------------------------------------------- Figure 12.1
def fig12_1():
    e = J("experiment6_continuous", "exp6_results.json")
    fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.1))
    cols = {4: BLUE, 10: PURPLE, 20: ORANGE}
    ax = axs[0]; panel(ax, "a")
    for dim, col in cols.items():
        for enc, ls, mk in (("opvar", "-", "o"), ("phys", "--", "s")):
            rows = sorted([x for x in e if x["dim"] == dim and x["encoder"] == enc and not x["scramble"]], key=lambda x: x["C"])
            ax.plot([x["C"] for x in rows], [x["success"] for x in rows], ls, marker=mk, color=col, ms=4, lw=1.5,
                    label=("$d=%d$" % dim) if enc == "opvar" else None, alpha=1 if enc == "opvar" else 0.7)
    ax.plot([], [], "-", color="k", label="task variable"); ax.plot([], [], "--", color="k", label="physical state")
    ax.axvline(3.06, color=GREY, ls=":", lw=1)
    ax.set_xlabel("rate $C$ (bits per step)"); ax.set_ylabel("success rate")
    ax.set_title("Task variable invariant in $d$"); ax.legend(fontsize=7, ncol=2, loc="center right", bbox_to_anchor=(1.0, 0.6))
    ax = axs[1]; panel(ax, "b")
    x = np.arange(3); w = 0.26
    best = lambda d, enc: max(r["success"] for r in e if r["dim"] == d and r["encoder"] == enc and not r["scramble"])
    for k, (enc, col, lab) in enumerate((("opvar", BLUE, "task variable"), ("learned", PURPLE, "learned $\\psi$"), ("phys", ORANGE, "physical state"))):
        ax.bar(x + (k - 1) * w, [best(d, enc) for d in (4, 10, 20)], w, color=col, label=lab)
    ax.set_xticks(x); ax.set_xticklabels(["$d=4$", "$d=10$", "$d=20$"]); ax.set_ylabel("success rate")
    ax.set_title("Best success over rates (Table 12.1)"); ax.legend(fontsize=7.5, ncol=3, loc="upper center"); ax.set_ylim(0, 1.2); ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    fig.tight_layout(); save(fig, "fig12_1_continuum")


# ---------------------------------------------------------------- Figure 14.1
def fig14_1():
    d = J("experiment8_mpe_external", "exp8_full.json")
    up = [x for x in d if x["kind"] == "upper"][0]
    fig, ax = plt.subplots(figsize=(5.6, 3.2))
    for enc, col, mk, lab in (("oracle", BLUE, "o", "task variable"), ("learned", PURPLE, "^", "learned representation"),
                              ("phys", ORANGE, "s", "physical observation")):
        rows = sorted([x for x in d if x["kind"] == "sweep" and x["encoder"] == enc], key=lambda x: x["C"])
        ax.errorbar([x["C"] for x in rows], [x["ret"] for x in rows], yerr=[x["se"] for x in rows], fmt=mk + "-",
                    color=col, ms=4, lw=1.5, capsize=2, label=lab)
    ax.axhline(up["ret"], color=GREY, ls="--", lw=1); ax.text(4.2, up["ret"] + 0.6, "unlimited communication", color=GREY, fontsize=7.5)
    floor = np.mean([x["randomized"] for x in d if x["kind"] == "ablate"])
    ax.axhline(floor, color=GREY, ls=":", lw=1); ax.text(4.2, floor + 0.6, "randomized symbols", color=GREY, fontsize=7.5)
    ax.axvline(math.log2(3), color=BLUE, ls=":", lw=1); ax.text(1.64, -72.6, "$\\log 3$", color=BLUE, fontsize=8)
    ax.set_xlabel("bits per agent per step"); ax.set_ylabel("mean return (higher is better)")
    ax.legend(fontsize=7.5, loc="lower right")
    fig.tight_layout(); save(fig, "fig14_1_simple_spread")


if __name__ == "__main__":
    pts = fig6_1()
    for p in pts: print("Fig 6.1 threshold check: h=%.3f h_theta=%.3f C*=%.2f" % p[:3])
    fig6_2(); fig6_3(); fig8_1()
    h, s = fig9_1(); print("m=3: h_theta=%.4f sigma=%.4f" % (h, s))
    fig9_2(); fig10_1(); fig12_1(); fig14_1()
