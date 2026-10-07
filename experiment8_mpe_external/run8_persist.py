"""Persisted version of the Experiment 8 sweep (Chapter 14).

Every number reported in Table 14.1 and in the ablation table is written to
exp8_full.json, so that each figure in the book can be checked against a file.
Seeds are identical to run8.py, so results reproduce the console output of the
original runs.

Usage:
    python run8_persist.py sweep 2 3 4      # evaluate these alphabet sizes
    python run8_persist.py ablate 16        # channel ablation at M=16
    python run8_persist.py upper            # no-channel upper bound
"""
import json
import os
import sys
import numpy as np
from run8 import build, run
from exp8 import Quantizer

N_EVAL = 90
OUT = "exp8_full.json"


def load():
    return json.load(open(OUT)) if os.path.exists(OUT) else []


def save(rows):
    json.dump(rows, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    mode = sys.argv[1]
    reps, X, Y, psi = build()
    rows = load()
    if mode == "upper":
        mu, se = run(reps, None, "oracle", n_ep=N_EVAL, full=True)
        acc = float((psi(X).argmax(1) == Y).mean())
        rows = [r for r in rows if r.get("kind") != "upper"]
        rows.append(dict(kind="upper", ret=mu, se=se, n_ep=N_EVAL,
                         n_train=int(len(X)), train_accuracy=acc))
        print("upper bound %.2f +- %.2f   train acc %.3f   n_train %d"
              % (mu, se, acc, len(X)), flush=True)
    elif mode == "sweep":
        for M in [int(m) for m in sys.argv[2:]]:
            quants = {k: Quantizer(M, seed=7).fit(reps[k]["train"]) for k in reps}
            for name in ("phys", "learned", "oracle"):
                mu, se = run(reps, quants, name, n_ep=N_EVAL)
                rows = [r for r in rows if not (r.get("kind") == "sweep" and
                                                r["M"] == M and r["encoder"] == name)]
                rows.append(dict(kind="sweep", M=M, C=float(np.log2(M)),
                                 encoder=name, ret=mu, se=se, n_ep=N_EVAL))
                print("M=%d %s %.2f +- %.2f" % (M, name, mu, se), flush=True)
            save(rows)
    elif mode == "ablate":
        M = int(sys.argv[2])
        quants = {k: Quantizer(M, seed=7).fit(reps[k]["train"]) for k in reps}
        for name in ("phys", "learned", "oracle"):
            a, _ = run(reps, quants, name, n_ep=N_EVAL)
            b, _ = run(reps, quants, name, n_ep=N_EVAL, scramble=True)
            rows = [r for r in rows if not (r.get("kind") == "ablate" and
                                            r["M"] == M and r["encoder"] == name)]
            rows.append(dict(kind="ablate", M=M, encoder=name, normal=a,
                             randomized=b, drop=a - b, n_ep=N_EVAL))
            print("ablate M=%d %s normal %.2f randomized %.2f drop %.2f"
                  % (M, name, a, b, a - b), flush=True)
    save(rows)
