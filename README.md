# Theory of Intelligent Computation (TIC)

A task-relative theory of state computation: intelligent computation is the selection of state
transitions on the coarsest abstraction determined by the goal. This repository contains the paper,
the numerical verification scripts for its theorems, the raw data behind every table and figure, and
the internal notes that trace how the theorems were derived and revised.

The paper itself is posted on arXiv (link to be added once live) and is not included in this
repository. Everything here exists to make its claims independently checkable: verification
scripts, raw experimental data, and the theorem-development notes.

If you are only here to check one thing, start with §15 of the paper ("Summary of validity
conditions") and §17 ("Epistemic status") — they index every claim against its evidence and its
known failure conditions.

## Repository layout

```
theorem-verification/         standalone numerical checks for individual theorems and counterexamples
experiment5_discrete/         discrete rendezvous experiments: bandwidth law, fault-tolerant
                               threshold, operational variance-entropy, ontological drift
experiment6_continuous/       continuous-torus experiment: the rate-distortion continuum limit
experiment8_mpe_external/     external confirmation on PettingZoo/mpe2 simple_spread_v3
docs/theorem-development-log/ internal working notes (Chinese) recording how the theorems were
                               derived, revised, and — in a few cases — falsified along the way
```

### Mapping to the paper

| Folder | Paper section(s) | What it produced |
|---|---|---|
| `theorem-verification/` | §4 (Theorem 4), §5 (Theorem 5, the rescue-robot counterexample), Appendix A.4 (reachable-set counterexample), and assorted sanity checks for Theorems 1, 9, 10, 12, 13 | Small, self-contained numerical checks. Each script is independent; the comment block at the top of each file states which claim it is checking |
| `experiment5_discrete/` | §8 (bidirectional dissociation), §9–§10 (Theorem 14, Corollaries 14.2–14.4, operational variance-entropy σθ), §11 (breaking the i.i.d. degeneracy), §12 (Theorem 11′, ontological drift experiments 7a/7b) | All raw results underlying the tables in §8–§12; the `data/` subfolder holds the `.json`/`.csv`/`.npy`/`.txt` outputs actually quoted in the paper |
| `experiment6_continuous/` | §13 (the continuum limit, rate-distortion, the successor-representation failure mode and its fix) | `exp6_results.json` holds the numbers behind the §13.5 results table |
| `experiment8_mpe_external/` | §17.2 (external confirmation on `simple_spread_v3`) | The only experiment in this repository run on an environment we did not design ourselves |
| `docs/theorem-development-log/` | background for all of the above | Chinese-language working notes, kept as-is rather than translated, tracing the theorem set from v0.1 through v0.7 — including the consistency audit that resolved six internal contradictions before v1.0 |

### Second version of the theory (V2)

The second version, *A Theory of Intelligent Computation: Task Abstraction and the Bandwidth of
Coordination* (monograph, October 2026), uses chapter-based numbering. Its Appendix C maps every
result of the first version to its new number, and its Appendix D points to this repository. The
scripts above remain valid for V2; the files below were added for results that are new or
corrected in V2.

| File | V2 location | What it checks |
|---|---|---|
| `experiment5_discrete/theorem14prime.py`, `data/t14prime_out.txt` | Chapter 10 (Theorem 10.2, Lemma 10.4) | Mismatched models: per-step cross-entropy bound, relative entropy of the projection onto the task abstraction, weather and drift perturbations |
| `experiment5_discrete/recheck_asym.py`, `data/recheck_asym_out.txt` | §9.5, §16.4 | Recomputation of the asymmetric-terrain configurations (Table 9.1) with the tolerance-based refiner; all unchanged |
| `experiment6_continuous/ablate_conditioning.py` | §12.3 (Proposition 12.1) | Controlled ablation: action-averaged vs action-conditioned representation, same features, data and readout |
| `experiment6_continuous/env_cont.py` (updated) | §12.2 | Reference rate now uses the sequential rate-distortion function ½·log₂(1 + σ²/D) |
| `experiment8_mpe_external/run8_persist.py`, `exp8_full.json` | Chapter 14 (Table 14.1, ablation table) | Same seeds as `run8.py`; every number in Chapter 14 is written to `exp8_full.json` |
| `theorem-verification/table8_2_common_refinement.py`, `table8_2_common_refinement_out.txt` | §8.6 (Theorem 8.8, Table 8.2) | Requirement of the common refinement of several tasks, computed with the true requirement H(B′∣S) |

## Reproducing the results

**Requirements:** Python 3.10+ and NumPy. `experiment8_mpe_external/` additionally expects
`pettingzoo[mpe]`; if that is not installed, the bundled `pygame_stub/` provides a minimal stand-in
sufficient to run the encoder/decoder logic without a display.

```bash
pip install numpy
# optional, for experiment8_mpe_external only:
pip install "pettingzoo[mpe]"
```

Every script in `theorem-verification/`, `experiment5_discrete/`, and `experiment6_continuous/` is
a standalone, dependency-free (beyond NumPy) Python file — run it directly:

```bash
python3 theorem-verification/verify5.py        # Theorem 5: the rescue-robot counterexample
python3 experiment5_discrete/run_sweep.py       # §8: bidirectional dissociation sweep
python3 experiment5_discrete/theorem14.py       # §10: Theorem 14 / fault-tolerant threshold
python3 experiment5_discrete/theorem14_closeloop.py   # §10.8: Corollary 14.4, closed-loop prediction
python3 experiment5_discrete/corollary14_3.py   # §10.9: block-length narrowing
python3 experiment5_discrete/drift_sweep.py     # §12: ontological drift, experiments 7a/7b
python3 experiment6_continuous/exp6.py          # §13: continuous-torus experiment
python3 experiment8_mpe_external/run8.py        # §17.2: external MPE confirmation
```

The `data/` subfolder under `experiment5_discrete/` and the `.json` files in `experiment6_continuous/`
are the actual outputs used to write the paper's tables — kept in the repository so a reader can check
the reported numbers without rerunning anything, and can diff a rerun against them.

## Honesty notes carried over from the paper

This repository matches the paper's own epistemic accounting rather than presenting a cleaned-up
success story:

- Every result comes with the validity conditions under which it holds, and the conditions under
  which it is known to fail — see §15 of the paper.
- Three claims in the paper were revised or discarded after these experiments contradicted them
  (a "sharp threshold" that turned out to be a smooth tail probability, a two-level rate condition
  that overcharged for absorbable drift, and one experimental condition retired as confounded by
  task difficulty rather than bandwidth) — see §9.1, §10.10, and §12 for the record.
- A numerical bug (unsafe floating-point equality in partition refinement) was found in the
  refinement code during this project and fixed; §17.4 of the paper documents the fix and audits
  its impact on every reported number.
- All work in this repository is simulation. Nothing here has been run on a physical system or
  reproduced by a third party — see §17.3 and §18 of the paper for the resulting open problems.

## License

- **Code** (`theorem-verification/`, `experiment5_discrete/`, `experiment6_continuous/`,
  `experiment8_mpe_external/`): MIT License — see [`LICENSE`](LICENSE).
- **Data and notes** (the `data/` subfolders, `docs/`): Creative Commons Attribution 4.0
  International (CC BY 4.0) — see [`LICENSE-DATA.md`](LICENSE-DATA.md).

## Citation

See the arXiv listing (link to be added once live) for the paper, full author details, and the
canonical citation.
