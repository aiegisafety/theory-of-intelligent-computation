"""Experiment 8 sweep: episode return vs channel capacity, three encoders."""
import json
import sys
import numpy as np
from exp8 import (simple_spread_v3, N_AGENTS, MAX_CYCLES, sender_block,
                  assignment_from_block, my_target, choose_action, collect,
                  learn_abstraction, Quantizer)

MS = [16, 32, 64]


def build(seed=0, n_ep=250):
    X, Y = collect(n_ep=n_ep, seed=seed)
    psi = learn_abstraction(X, Y, seed=seed + 1)
    reps = {
        "phys":    dict(fn=lambda o: sender_block(o),
                        dec=lambda v: assignment_from_block(v),
                        train=X),
        "learned": dict(fn=lambda o: np.asarray(psi(sender_block(o))).reshape(-1),
                        dec=lambda v: int(np.argmax(v)),
                        train=psi(X)),
        "oracle":  dict(fn=lambda o: np.eye(N_AGENTS)[my_target(o)],
                        dec=lambda v: int(np.argmax(v)),
                        train=np.eye(N_AGENTS)[Y].astype(float)),
    }
    return reps, X, Y, psi


def run(reps, quants, name, n_ep=150, seed=1234, scramble=False, full=False):
    env = simple_spread_v3.parallel_env(N=N_AGENTS, local_ratio=0.5,
                                        max_cycles=MAX_CYCLES,
                                        continuous_actions=False)
    rng = np.random.default_rng(seed)
    rec = reps[name] if name in reps else None
    q = quants[name] if quants else None
    tot = []
    for ep in range(n_ep):
        obs, _ = env.reset(seed=seed * 104729 + ep)
        R = 0.0
        for t in range(MAX_CYCLES):
            if not env.agents:
                break
            # each agent j encodes ITSELF into one symbol
            claim_of = {}
            for b in env.agents:
                if full:                       # upper bound: no channel at all
                    claim_of[b] = my_target(obs[b])
                    continue
                v = rec["fn"](obs[b])
                idx = int(q.encode(v)[0])
                if scramble:
                    idx = int(rng.integers(q.M))
                claim_of[b] = rec["dec"](q.decode(idx))
            acts = {}
            for a in env.agents:
                claimed = {claim_of[b] for b in env.agents if b != a}
                acts[a], _ = choose_action(obs[a], claimed, rng, 0.0)
            obs, r, term, trunc, info = env.step(acts)
            R += float(sum(r.values()))
        tot.append(R)
    env.close()
    return float(np.mean(tot)), float(np.std(tot) / np.sqrt(len(tot)))


if __name__ == "__main__":
    n_eval = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    reps, X, Y, psi = build()
    P = psi(X)
    acc = float((P.argmax(1) == Y).mean())
    print(f"data {len(X)} samples | phys dim {X.shape[1]} | psi dim {P.shape[1]} "
          f"| learned assignment accuracy {acc:.3f} (chance {1/N_AGENTS:.3f})",
          flush=True)

    hi, hse = run(reps, None, "oracle", n_ep=n_eval, full=True)
    print(f"UPPER BOUND (no channel limit): {hi:8.2f} ± {hse:.2f}", flush=True)

    results = [dict(kind="upper_bound", ret=hi, se=hse)]
    print(f"  {'M':>3s} {'C':>5s}   " +
          "  ".join(f"{k:>16s}" for k in ("phys", "learned", "oracle")),
          flush=True)
    for M in MS:
        quants = {k: Quantizer(M, seed=7).fit(reps[k]["train"]) for k in reps}
        row = {}
        for name in ("phys", "learned", "oracle"):
            mu, se = run(reps, quants, name, n_ep=n_eval)
            row[name] = (mu, se)
            results.append(dict(M=M, C=float(np.log2(M)), encoder=name,
                                ret=mu, se=se, scramble=False, n_ep=n_eval))
        print(f"  {M:3d} {np.log2(M):5.2f}   " +
              "  ".join(f"{row[k][0]:10.2f}±{row[k][1]:4.2f}" for k in row),
              flush=True)

    quants = {k: Quantizer(max(MS), seed=7).fit(reps[k]["train"]) for k in reps}
    abl = {}
    for name in ("phys", "learned", "oracle"):
        mu, se = run(reps, quants, name, n_ep=n_eval, scramble=True)
        abl[name] = mu
        results.append(dict(M=max(MS), C=float(np.log2(max(MS))), encoder=name,
                            ret=mu, se=se, scramble=True, n_ep=n_eval))
    print("  ABLATION: " + "  ".join(f"{k}={v:.2f}" for k, v in abl.items()),
          flush=True)
    json.dump(results, open("exp8_results.json", "w"), indent=1)
