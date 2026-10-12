"""V3 §6.8: decomposition of the 0.3-0.9-bit gap of the greedy balanced-mass code of Experiment 1
(theorem-verification/experiment1.py, class-aware coder, 12 classes) into belief dispersion
E[H(q_t)] - h_theta and coding loss C - E[H(message)]. Run from the repository's v3/ folder; set TV_DIR to use another copy of theorem-verification/."""
import os, numpy as np
PATH = os.environ.get("TV_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "theorem-verification"))
exec(open(os.path.join(PATH, "experiment1.py")).read().split("P=lambda")[0])
for ht in (2.0, 3.0):
    Q, h = make_chain(ht)
    for C in (1, 2):
        if C >= h: continue
        G = 2 ** C; rng = np.random.default_rng(7); perm = rng.permutation(K); b = rng.integers(K); bel = np.ones(K) / K
        U = []; Hq = []; Hm = []
        for t in range(1500):
            b = rng.choice(K, p=Q[b]); pred = bel @ Q; g = groups(pred, G, perm)
            mass = np.array([pred[g == j].sum() for j in range(G)])
            post = np.where(g == g[b], pred, 0.0); post /= post.sum(); bel = post
            if t > 500: U.append(H(post)); Hq.append(H(pred)); Hm.append(H(mass))
        print("h=%.2f C=%d  U=%.3f  floor=%.3f  gap=%.3f | belief dispersion E[H(q)]-h=%.3f  coding loss C-E[H(msg)]=%.3f"
              % (h, C, np.mean(U), h - C, np.mean(U) - (h - C), np.mean(Hq) - h, C - np.mean(Hm)))
