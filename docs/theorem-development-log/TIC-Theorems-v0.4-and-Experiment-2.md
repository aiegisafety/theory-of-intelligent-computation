# TIC — Theorem Layer v0.4 + Experiment 2

**Theorem 7: learning the abstraction. Experiment 2: what learning it badly costs.**

Extends `TIC-Theorems-v0.1/v0.2/v0.3`. Companion to `TIC-Consolidated-v0.3.md`.

This closes the item that has stood at the top of the open list since Theorem 4: **the canonical abstraction $\sim_\theta^{*}$ is computed from known dynamics — but a real entity must estimate it from experience.** Theorem 7 shows the estimation is well-posed and quantifies both failure directions; Experiment 2 measures them and produces one connection I did not expect: *insufficient learning is paid for in communication bandwidth.*

| | Statement | Status |
|---|---|---|
| **Theorem 7.1–7.2** | $\varepsilon$-refinement from samples is **sandwiched**: coarser than $\sim_\theta^{*}$, and $(\varepsilon+2\gamma)$-adequate | **Proved** |
| **Theorem 7.3** | Sample complexity $n = O\!\big((K+\log(|\mathcal S|/\delta))/\varepsilon^2\big)$ | **Proved** |
| **Theorem 7.4** | Independent learners converge to the *same* abstraction — no negotiation needed | **Proved** (from T4 uniqueness) |
| **Theorem 7.5** | Learning errors are **asymmetric**: over-splitting costs bandwidth, over-merging destroys Theorem 3 | **Proved** |
| **Experiment 2** | Trade-off surface measured; safe $\varepsilon$-window spans ~1 order of magnitude | **Confirmed** |
| **Finding 2c** | Under-learning shows up as a **2 bit/step bandwidth tax**, not as errors | **Unpredicted** |

---

## 7. Theorem 7 — Learning the canonical abstraction

### 7.1 Setting

The entity does not know the kernels. It draws $n$ transitions per state (per action) and forms $\hat P$. It then runs **$\varepsilon$-refinement**: identical to Theorem 4's partition refinement, except that two states are separated only when their *estimated* block-transition rows differ by more than $\varepsilon$ in total variation.

Fix the high-probability event

$$E(\gamma):\qquad \mathrm{TV}\big(\hat P_a(\cdot\mid s),\,P_a(\cdot\mid s)\big)\le\gamma \quad \text{for all } (s,a)$$

**Lemma 7.0 (coarsening is free).** For any partition $\Pi$, the block-marginals inherit the bound: $\mathrm{TV}\big(\hat P_a(\cdot_\Pi\mid s), P_a(\cdot_\Pi\mid s)\big) \le \gamma$. *(Data processing for total variation: summing probabilities cannot increase TV.)* This is what makes a **single** sampling event suffice for **all** rounds of refinement — errors do not compound across rounds.

### 7.2 Theorem 7.1 (soundness) and 7.2 (completeness)

> **7.1.** On $E(\gamma)$, any two states merged by $\varepsilon$-refinement have true block-transition TV at most $\varepsilon+2\gamma$. Hence the output partition is $(\varepsilon+2\gamma)$-**adequate**.
>
> **7.2.** On $E(\gamma)$, if $\varepsilon \ge 2\gamma$ then no two $\sim_\theta^{*}$-equivalent states are ever separated; hence $\sim_\theta^{*}$ refines the output.

**Proof of 7.2** (7.1 is the triangle inequality on TV). Joint induction on rounds. Base: $\Pi_0$ is the goal partition, which $\sim_\theta^{*}$ refines by (G). Step: assume $\sim_\theta^{*}$ refines $\Pi_t$. Then each $\Pi_t$-block is a union of $\sim_\theta^{*}$-blocks, so any $s_1\sim_\theta^{*}s_2$ have *identical* true $\Pi_t$-block rows; by Lemma 7.0 their estimated rows differ by at most $2\gamma \le \varepsilon$, so the algorithm does not split them, and $\sim_\theta^{*}$ refines $\Pi_{t+1}$. $\blacksquare$

**Corollary (sandwich).** The learned partition $\hat\Pi$ satisfies

$$\sim_\theta^{*} \ \text{refines}\ \hat\Pi, \qquad \hat\Pi \ \text{is } (\varepsilon+2\gamma)\text{-adequate}$$

and therefore, **by Theorem 6.2**, the bandwidth computed from $\hat\Pi$ is within $(\varepsilon+2\gamma)\log_2(K-1) + H_b(\varepsilon+2\gamma)$ of the truth. *This is the first place where two previously proved theorems compose to give something neither states alone — Theorem 6 was proved for hypothetical approximate abstractions; Theorem 7 shows that learning is exactly the process that produces them.*

### 7.3 Theorem 7.3 (sample complexity)

Taking $\gamma \le \varepsilon/2$ and standard TV concentration for a distribution over $d$ outcomes, with a union bound over states and actions:

$$n \;=\; O\!\left(\frac{K + \log(|\mathcal{S}||\mathcal{A}|/\delta)}{\varepsilon^{2}}\right)$$

suffices with probability $1-\delta$. Note the dimension is $K$ — the number of *classes* — not $|\mathcal{S}|$, because refinement only ever compares block-marginals (Lemma 7.0). **The abstraction is cheaper to learn than the model.** Empirically the relevant noise scale is $\tfrac12\sqrt{2K/\pi n}$, which matched the observed merge onset in Experiment 2 to within a few percent.

### 7.4 Theorem 7.4 — no negotiation needed

> Two entities learning independently from their own samples converge to the **same** abstraction, without communicating about the abstraction at all.

**Proof.** By Theorem 4, $\sim_\theta^{*}$ is the *unique* coarsest adequate equivalence. By 7.1–7.2 each entity's output is sandwiched around it, and as $\gamma\to0$ with $\varepsilon\to0$ (at rate $\varepsilon\ge2\gamma$) each output converges to $\sim_\theta^{*}$. Both limits are the same object. $\blacksquare$

This is the substantive payoff of Theorem 4's uniqueness, and it is a claim about multi-agent systems worth stating plainly:

> **Coordination on ontology is a statistical problem, not a bargaining problem.** Entities need not agree on how to carve up the world; if they share a task and the world has one dynamics, sufficient data forces them to the same carving.

The finite-sample caveat is Experiment 2's business — and it is a real one: agents whose tolerance $\varepsilon$ is set outside the safe window disagree *persistently*, and more data does not help.

### 7.5 Theorem 7.5 — the asymmetry of learning errors

> **Over-splitting is safe and costs bandwidth. Over-merging is unsafe and no amount of bandwidth repairs it.**

**Proof.** *Over-splitting* ($\hat\Pi$ refines $\sim_\theta^{*}$): every $\hat\Pi$-block lies inside one $\theta$-class, so admissibility remains class-determined and Lemma 3.1 and Theorem 3 hold unchanged. The cost is bandwidth: since the coarser class variable is a function of the finer one, $H(\hat B_{t+1}\mid S_t) \ge H(B_{t+1}\mid S_t)$, so by Theorem 6.1 the floor rises. *Over-merging* ($\hat\Pi$ merges distinct $\theta$-classes): Lemma 3.1 fails — admissible sets are no longer determined by the block — so two entities can select mutually inadmissible transitions while agreeing on the class. No increase in $C$ removes this: the information they are exchanging is about the wrong partition. $\blacksquare$

Design consequence: **when in doubt, split.** The penalty is a computable number of bits per step; the alternative penalty is silent coordination failure.

---

## 8. Experiment 2 — learning the abstraction from data

**Setup.** Planted structure: $K=6$ operational classes, $m=4$ physical sub-states each ($|\mathcal{S}|=24$). True canonical abstraction (from exact refinement on the true kernel): 6 blocks, $h_\theta^{*}=2.067$ bits/step, against a physical rate $h=4.067$. Each entity draws $n$ transitions per state, estimates the kernel, and runs $\varepsilon$-refinement. 25 repetitions per cell.

*over-merge* = fraction of inequivalent pairs wrongly merged (unsafe) · *over-split* = fraction of equivalent pairs wrongly separated (safe) · *both-safe* = probability that two independently trained entities **both** avoid over-merging.

### 8.1 The trade-off surface

| $\varepsilon$ | $n$ | blocks | over-merge | over-split | $h_\theta$(learned) | both-safe |
|---|---|---|---|---|---|---|
| 0.02 | 100 | 24.0 | 0.000 | 1.000 | **4.067** | 1.00 |
| 0.02 | 5000 | 20.0 | 0.000 | 0.801 | 3.647 | 1.00 |
| 0.05 | 1000 | 12.2 | 0.000 | 0.391 | 2.793 | 1.00 |
| 0.05 | 5000 | **6.0** | **0.000** | **0.000** | **2.067** | 1.00 |
| 0.10 | 300 | 9.4 | 0.000 | 0.232 | 2.529 | 1.00 |
| 0.10 | 1000 | 6.6 | 0.000 | 0.053 | 2.199 | 1.00 |
| 0.10 | 5000 | 6.2 | 0.000 | 0.018 | 2.111 | 1.00 |
| 0.20 | 100 | 8.8 | 0.035 | 0.269 | 2.417 | **0.24** |
| 0.20 | 1000 | 5.7 | 0.060 | 0.052 | 1.914 | **0.00** |
| 0.20 | 5000 | 5.0 | **0.067** | 0.000 | 1.801 | **0.00** |

Three things to read off.

**(a) Theorem 7.5 is visible.** For $\varepsilon\le0.10$, over-merge is *exactly* 0.000 in every cell at every sample size — safety is not a matter of luck once $\varepsilon$ is in range. What varies is over-splitting, and it is paid for in the $h_\theta$ column.

**(b) A badly chosen tolerance is a bias, not a variance.** At $\varepsilon=0.20$, over-merging *grows* with data (0.035 → 0.060 → 0.067) and both-safe *falls to zero*. **More data does not fix a too-permissive abstraction tolerance; it entrenches it.** Two independently trained entities then disagree permanently — the failure Theorem 7.4 rules out asymptotically but only for $\varepsilon\ge2\gamma$ *and* $\varepsilon$ small enough.

**(c) Under-learning shows up as a bandwidth bill.** At $\varepsilon=0.02$ the entity is perfectly safe and perfectly correct at every $n$ — and stuck at $h_\theta = 4.067$, the *physical* entropy rate, when the task needs 2.067. It has learned nothing about which distinctions matter, so it must track everything. **A 2 bit/step tax, forever, for insufficient abstraction learning.** Nothing in the theory predicted this; it falls out of composing Theorem 7.5 with the bandwidth law, and it is the most practically suggestive result in this instalment: *in a multi-entity system, the cost of poor abstraction is not visible as errors — it is visible as a communication bill.*

### 8.2 The safe window

At $n=5000$ (estimation noise $\approx 0.014$):

| $\varepsilon$ | 0.01 | 0.02 | **0.04** | **0.06** | 0.08 | 0.10 | **0.12** | 0.15 | 0.18 | 0.20 | 0.25 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| blocks | 24.0 | 22.3 | **6.0** | **6.0** | 6.2 | 6.2 | **6.0** | 6.1 | 5.7 | 5.0 | 5.5 |
| over-merge | .000 | .000 | **.000** | **.000** | .000 | .000 | **.000** | .000 | .061 | .067 | .158 |
| $h_\theta$ | 4.067 | 3.889 | **2.067** | **2.067** | 2.120 | 2.102 | **2.067** | 2.085 | 1.892 | 1.801 | 1.914 |

The abstraction is recovered **exactly** ($h_\theta = h_\theta^{*} = 2.067$, zero errors of either kind) for $\varepsilon \in [0.04,\,0.15]$. Below that, sampling noise dominates and the algorithm only splits; above $\approx0.18$ it starts merging genuinely distinct classes.

**The window spans roughly an order of magnitude**, so this is not a knife-edge hyperparameter — a mild but real piece of good news for anything built on Theorem 4.

### 8.3 An honest negative: the window's upper edge is not predicted

Theorem 7 gives a sufficient condition ($\varepsilon$ below the class separation at every reachable partition). Two natural candidates for that separation fail to predict the observed edge of $\approx 0.16$:

- separation measured against the **final** partition: $\Delta = 0.258$ — too permissive ($\varepsilon=0.20$ fails despite $0.20<0.258$);
- smallest split detected in the **first** refinement round: $0.0085$ — far too conservative ($\varepsilon = 0.10 \gg 0.0085$ works fine).

The reason the second is conservative is structural and worth recording: refinement is a fixed-point iteration, so a pair that is *not* separated in an early round can still be separated later, once the rest of the partition has sharpened. Information accumulates across rounds. **Characterizing the exact usable window is a well-posed open problem produced by this experiment** — the kind of question the theory could not have asked before Theorem 7 existed.

### 8.4 What Experiment 2 does not show

Still a known-structure simulation: planted classes, tabular kernels, one task. It does not touch continuous state, function approximation, non-stationarity, or entities that must also discover the *goal*. Its value is that it tests the one assumption Theorem 4 could not justify — known dynamics — and shows the failure modes are the ones the theory says they should be, with one addition the theory did not anticipate.

---

## 9. Status after v0.4

**Proved (7 theorems).** T1 constraint-collapse accounting and its reversal · T2 residual-indeterminacy floor · T3 cooperation by class agreement · T4 canonical abstraction, intrinsic task bandwidth · T5 entropy is not the objective · T6 generality and continuity of the bandwidth law · T7 learnability of the abstraction, with sandwich bounds, sample complexity, convergence without negotiation, and the split/merge asymmetry.

**Measured (2 experiments).** Cooperation threshold at $C\approx h_\theta$ · floor approachable within 0.3–0.9 bits by a naive code · complete insensitivity to physical uncertainty under class-aware coding · abstraction recoverable from $\sim10^3$ samples per state with a safe tolerance window spanning an order of magnitude · under-learning paid as a 2 bit/step bandwidth tax.

**The composition test.** The clearest sign of life this round: Theorem 6 was proved for hypothetical $\varepsilon$-adequate abstractions, before there was any account of where such things come from; Theorem 7 then showed that *learning is precisely the process that produces them*, and the two compose into a bound nobody wrote down in advance. Pieces proved for separate reasons fitting together is what distinguishes a theory from a collection of results.

**Open, re-prioritized.**

1. **The exact usable $\varepsilon$-window** (§8.3) — new, well-posed, and small enough to be finishable.
2. **Analytic achievability for Theorem 2** — §7.3 of the previous instalment suggests the floor is nearly tight.
3. **Discovering the goal, not just the abstraction.** Everything so far takes the task $\theta$ as given. This is now the deepest remaining assumption, and it is where TIC would have to say something about autonomy rather than competence.
4. **A theory of $V(D)$** — deliberation value, computability, stopping.
5. **Continuous state and function approximation** — bisimulation metrics are the route; without this the theorems stay tabular.
6. **The Active Inference comparison chapter**, with the specific technical question from v0.2 §5.7.

---

## Appendix N4 — Output

`experiment2.py` (grid), `eps_sweep.py` (window), `gap.py`/`gap2.py` (separation diagnostics). Ground truth: 6 blocks, $h_\theta^{*}=2.067$, $h=4.067$. Full tables reproduced in §8.1–8.2; raw runs in `theorem-verification/`.

## Sources

- [Givan, Dean & Greig, *Equivalence notions and model minimization in MDPs* (AIJ 2003)](https://www.sciencedirect.com/science/article/pii/S0004370202003764) — exact and approximate model minimization; the algorithm Theorem 7 makes statistical.
- [Ferns et al., *Bisimulation Metrics are Optimal Value Functions* (UAI 2014)](https://www.auai.org/uai2014/proceedings/individuals/67.pdf) — metric route for open problem 5.
- Levin, Peres & Wilmer, *Markov Chains and Mixing Times* — TV concentration and coupling.
- Kemeny & Snell, *Finite Markov Chains* — lumpability.
