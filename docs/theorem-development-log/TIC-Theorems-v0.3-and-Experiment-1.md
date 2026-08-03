# TIC — Theorem Layer v0.3 + First Experiment

**Theorem 6: the bandwidth law without idealization. Experiment 1: the theory's first empirical test.**

Extends `TIC-Theorems-v0.1.md` (T1–T3) and `v0.2.md` (T4–T5). Companion to `TIC-Consolidated-v0.3.md`.

Two items from the open list are addressed here. Theorem 6 removes the exact-lumpability assumption that made Theorem 4 "a statement about idealized systems" — and in the process shows the floor never needed lumpability at all. Experiment 1 runs prediction 4′ in simulation: it confirms the cooperation threshold, produces the first evidence on the achievability question (open problem 1), and yields an engineering result that was not predicted in advance.

| | Statement | Status |
|---|---|---|
| **Theorem 6.1** | Bandwidth floor holds for **any** partition — no lumpability needed | **Proved** (strengthens Cor. 3.3) |
| **Theorem 6.2** | $\varepsilon$-adequate abstraction: proxy error $\le \varepsilon\log(K-1) + H_b(\varepsilon)$ | **Proved**, verified |
| **Theorem 6.3** | Cooperation faults occur at rate $\le\varepsilon$; mean fault-free time $\ge 1/\varepsilon$ | **Proved** (TV coupling) |
| **Experiment 1** | Cooperation collapses at $C \approx h_\theta$; insensitive to $H_S$ above it | **Confirmed** |
| **Experiment 1b** | Greedy balanced code lands within 0.0–0.87 bits of the Theorem 2 floor | **New evidence**, open problem 1 |
| **Experiment 1c** | Class-aware vs. state-aware encoding: 1.00 vs 0.45 at equal capacity | **Unpredicted finding** |

---

## 6. Theorem 6 — Approximate abstraction

### 6.1 The floor never needed lumpability

Corollary 3.3 derived the bandwidth law by applying Theorem 2 to the quotient chain, which required (D) exactly — the assumption criticized in v0.2 §6. It turns out the detour was unnecessary.

Let $\theta$ be **any** partition of the state space, $B_t := [S_t]_\theta$, and let $C$ bound the entity's information acquisition per step as in Theorem 2.

> **Theorem 6.1.** For every partition and every protocol,
> $$H(B_{t+1}\mid e_{t+1}) \;\ge\; \underbrace{H(B_{t+1}\mid S_t)}_{=:\ h_\theta^{\mathrm{gen}}} \;-\; C$$

**Proof.** $S$ is Markov, so $B_{t+1}$ is conditionally independent of $e_t$ given $S_t$; hence $H(B_{t+1}\mid e_t) \ge H(B_{t+1}\mid e_t,S_t) = H(B_{t+1}\mid S_t)$. Subtract the at most $C$ bits acquired in the step. $\blacksquare$

Under exact adequacy $h_\theta^{\mathrm{gen}} = H(B_{t+1}\mid B_t) = h_\theta$, recovering Corollary 3.3. So **the bandwidth law is general; lumpability was only ever needed to *interpret* $h_\theta$ as the entropy rate of a Markov quotient chain** — that is, to make it computable from the abstraction alone rather than from the full dynamics. That is a modelling convenience, not a load-bearing hypothesis, and Theorem 6.2 bounds what it costs.

### 6.2 Continuity of the proxy

Call $\theta$ **$\varepsilon$-adequate** if for every block $b$, every action, and every $S_1,S_2\in b$, the class-transition distributions satisfy $\mathrm{TV}\big(P(\cdot_\theta\mid S_1),\,P(\cdot_\theta\mid S_2)\big)\le\varepsilon$. Let $K$ be the number of classes.

> **Theorem 6.2.** $\qquad 0 \;\le\; \underbrace{H(B_{t+1}\mid B_t)}_{\text{quotient proxy } h_\theta} - \underbrace{H(B_{t+1}\mid S_t)}_{\text{true requirement } h_\theta^{\mathrm{gen}}} \;\le\; \varepsilon\log_2(K-1) + H_b(\varepsilon)$

**Proof.** The gap is $I(B_{t+1};S_t\mid B_t) = \mathbb{E}_b\big[H(\bar P_b) - \mathbb{E}_{s\in b}H(P_s)\big]$ where $\bar P_b$ is the block-averaged class-transition distribution. By convexity of TV, $\mathrm{TV}(P_s,\bar P_b)\le\varepsilon$ for every $s\in b$, so the Fannes–Audenaert continuity bound gives $|H(P_s)-H(\bar P_b)| \le \varepsilon\log_2(K-1)+H_b(\varepsilon)$ termwise. Non-negativity is the data-processing direction: conditioning on $S_t$ (which determines $B_t$) cannot increase entropy. $\blacksquare$

*Verified* across $\varepsilon\in[0,0.35]$: the bound held in every trial and is loose in practice (measured gaps $\le 0.003$ bits against bounds up to 0.38) — perturbations tend to average out within blocks.

**Consequence.** The bandwidth law degrades continuously in the abstraction error:

$$C \;\ge\; h_\theta - \big[\varepsilon\log_2(K-1)+H_b(\varepsilon)\big] \ \text{ suffices to be within the true requirement}$$

Theorem 4's canonical abstraction is therefore not a knife-edge idealization. An abstraction that is *nearly* adequate carries a *nearly* correct bandwidth requirement, with an explicit modulus of continuity.

### 6.3 Cooperation degrades gracefully too

> **Theorem 6.3.** If two entities' class-successor distributions differ by at most $\varepsilon$ in total variation, there is a coupling under which they assign the same class with probability $\ge 1-\varepsilon$ per step. Hence the expected number of steps before a coordination fault is at least $1/\varepsilon$.

**Proof.** The coupling characterization of total variation: $\mathrm{TV}(P,Q)=\min_{\text{couplings}}\Pr[X\ne Y]$. Faults are then a process with per-step probability $\le\varepsilon$. $\blacksquare$

So Theorem 3's cooperation criterion, which is stated as an exact class identity, has a quantitative neighbourhood: **approximate class agreement buys $1/\varepsilon$ expected fault-free steps.** A team whose shared abstraction is 2% off can expect roughly 50 steps of coordinated action before a mismatch — which is a design number, not a metaphor.

### 6.4 What Theorem 6 settles

The v0.2 objection ("without approximate abstraction, Theorem 4 is about idealized systems") is answered on all three fronts: the floor is exact and general (6.1), the computable proxy is continuous in the error (6.2), and cooperation degrades at a bounded rate (6.3). What remains genuinely open is *learning* the abstraction from data rather than computing it from a known model.

---

## 7. Experiment 1 — the cooperation threshold

*TIC's first empirical claim. Everything above is derivation; this section is a measurement.*

### 7.1 Design

Two entities track a common operational state and must agree on its class (Theorem 3's cooperation condition). Deliberately minimal, so that the only thing being tested is the theory's prediction:

- **World.** A Markov chain over $K=12$ operational classes; the entropy rate $h_\theta$ is tuned continuously by temperature (bisection to a target).
- **Channels.** Each entity has its own $C$-bit-per-step channel, *different from the other's*: the encoder greedily splits the entity's current belief mass into $2^C$ groups in a per-entity random order and reports which group contains the true class. Both channels are truthful; they simply carry different partitions. (An earlier version of this experiment used belief-ordered greedy splitting for both entities, which silently produced *identical* partitions and hence a spurious 100% agreement everywhere. The bug is worth recording: two agents with the same code are not two agents.)
- **Entities.** Each maintains a belief over classes, predicts through the kernel, applies its observation, and reports its MAP class.
- **Measures.** *agree* — both MAP estimates coincide (Theorem 3's condition); *correct* — both coincide **and** match the truth; $H_\theta$ — steady-state belief entropy, compared against Theorem 2's floor $\max(0,h_\theta-C)$.

### 7.2 Result 1 — the threshold is where the theory puts it

| $h_\theta$ | $C=1$ agree | $C=2$ agree | $C=3$ agree |
|---|---|---|---|
| 0.25 | 1.000 | 1.000 | 1.000 |
| 0.50 | 1.000 | 1.000 | 1.000 |
| 1.00 | **0.982** | 1.000 | 1.000 |
| 1.50 | 0.704 | **0.965** | 1.000 |
| 2.00 | 0.543 | 0.856 | **0.993** |
| 2.50 | 0.391 | 0.657 | 0.960 |
| 3.00 | 0.283 | 0.417 | 0.880 |

Cooperation is essentially perfect while $h_\theta \le C$ and degrades once $h_\theta$ exceeds it; the knee tracks $C$ across all three capacities. **Prediction 4′ is confirmed.** Note also that the collapse is graceful rather than a cliff — consistent with Theorem 6.3, since finite-capacity tracking makes the entities' effective class distributions differ by a small but growing amount.

### 7.3 Result 2 — how close is the floor? (open problem 1)

| $h_\theta$ | $C$ | Theorem 2 floor | measured $H_\theta$ | gap |
|---|---|---|---|---|
| 1.50 | 1 | 0.500 | 1.315 | 0.815 |
| 2.00 | 1 | 1.000 | 1.870 | 0.870 |
| 3.00 | 1 | 2.000 | 2.447 | 0.447 |
| 2.50 | 2 | 0.500 | 0.913 | 0.413 |
| 3.00 | 2 | 1.000 | 1.324 | 0.324 |
| 3.00 | 3 | 0.000 | 0.311 | 0.311 |

The floor was proved as a converse; v0.1 §2.4 flagged that a fixed quantizer left a 1.9-bit gap and that achievability was unknown. A **greedy balanced-mass code — five lines, no optimization** — closes the gap to **0.3–0.9 bits**, and the gap shrinks as $h_\theta$ grows relative to $C$.

This is not a proof of achievability, but it is the first evidence that the floor is the right quantity rather than a loose bound: a naive code already operates within a bit of it. The residual gap is the natural target for the analytical work.

### 7.4 Result 3 — insensitivity to physical uncertainty, and an unpredicted finding

Fix $h_\theta = 1.0$, $C = 2$. Now blow each class up into $m$ physical sub-states, so the physical state entropy is $H_S = H_\theta + \log_2 m$ while the *task* is unchanged. Two encoders at identical capacity: **class-aware** (codes the operational class) and **naive** (codes the physical state, then marginalizes).

| $m$ | $\log_2 m$ added to $H_S$ | class-aware agree / correct | naive agree / correct |
|---|---|---|---|
| 1 | 0.00 | 1.000 / 1.000 | 1.000 / 1.000 |
| 2 | 1.00 | 1.000 / 0.999 | 0.942 / 0.936 |
| 4 | 2.00 | 1.000 / 0.999 | 0.691 / 0.571 |
| 8 | 3.00 | 1.000 / 0.999 | 0.623 / 0.450 |
| 16 | 4.00 | 1.000 / 0.999 | 0.694 / 0.412 |
| 32 | 5.00 | **1.000 / 0.999** | 0.799 / **0.486** |

Two things happen here.

**The predicted one.** With class-aware coding, a 32-fold increase in physical state space — five extra bits of physical uncertainty — costs *nothing*: agreement 1.000, correctness 0.999 throughout. Cooperation is governed by the operational entropy rate, exactly as Corollary 3.3 and Theorem 6.1 say, and is indifferent to how uncertain the entities are about the physical world.

**The unpredicted one.** The same task, same capacity, same dynamics, different *encoder*: correctness falls to 0.41–0.49. The channel is spent on distinctions the task cannot use. The engineering moral is sharp and was not stated anywhere in the theory before this run:

> **Encode the operational class, not the state.** Bandwidth spent on within-class detail is not merely wasted — it is subtracted from the capacity available for the distinctions that determine cooperation.

This bears directly on the shared-state architecture of v0.3 Part III: a shared-state service that synchronizes raw values is doing the naive thing. It should synchronize **task-relevant classes with provenance**, and Theorem 4 says which classes those are.

**An honesty note on the metric.** In the naive rows, agreement *rises* at $m=16,32$ (0.694, 0.799) while correctness keeps falling (0.412, 0.486). This is agreement by shared ignorance: two entities that have learned nothing both sit on the prior mode and coincide. Agreement alone is therefore not a sufficient measure of cooperation — a caution that applies to Theorem 3 as stated, whose condition $[\hat S_A]_\theta = [\hat S_B]_\theta$ is satisfied by two entities that are identically wrong. **Theorem 3 guarantees the absence of admissibility conflict, not the correctness of the joint action**; grounding in the objective state (v0.3's Reality Principle) is what supplies the latter, and this experiment shows the two conditions are genuinely independent.

### 7.5 What this experiment does not show

It is a simulation with a known model, hand-constructed classes, and MAP decoding. It tests whether the theory's internal predictions hold in a system built to satisfy its assumptions — necessary, but the weakest form of evidence. It says nothing yet about learned abstractions, real agents, or language-mediated communication. The next experiment should relax exactly one assumption: entities that must *estimate* the class structure rather than being given it.

---

## 8. Status after v0.3

**Proved.** T1 constraint-collapse accounting and its reversal regime · T2 residual-indeterminacy floor · T3 cooperation by class agreement · T4 canonical abstraction and intrinsic task bandwidth · T5 entropy is not the objective · T6 generality, continuity and graceful degradation of the bandwidth law.

**Measured.** Cooperation threshold at $C\approx h_\theta$; floor approachable to within 0.3–0.9 bits by a naive code; complete insensitivity to physical-state uncertainty under class-aware coding; a 2× correctness penalty for state-aware coding at equal capacity.

**The theory now has the shape it needs.** A small set of primitives; five theorems that are consequences of them rather than restatements; two results that corrected the theory's own claims; one canonical construction that removed a free parameter; and one experiment whose main quantitative prediction held and which produced a design rule nobody wrote down in advance. That last item is the useful test of whether a formalism is alive: it should occasionally tell you something you did not put into it.

**Open, re-prioritized.**

1. **Learning $\sim_\theta^{*}$ from experience.** Theorem 4 assumes the dynamics are known. This is now the largest gap between the theory and any real system, and it is where the state-abstraction literature has the most to offer.
2. **Analytic achievability for Theorem 2.** §7.3 suggests the floor is nearly tight; prove it, or exhibit the optimal confirmation code.
3. **A theory of $V(D)$** — computability and approximation of the deliberation value functional, and its relation to metareasoning stopping rules.
4. **Experiment 2**: entities that estimate the abstraction rather than receiving it.
5. **The Active Inference comparison chapter**, now with a specific technical question to ask (v0.2 §5.7).

---

## Appendix N3 — Verification and experiment output

**Theorem 6.2** (`verify6.py`) — bound holds at every $\varepsilon$; loose in practice.
```
  eps    measured TV   H(B'|B)   H(B'|S)     gap    bound   holds
  0.00      0.000     2.293    2.293    0.000   0.000    OK
  0.02      0.003     2.344    2.344    0.000   0.033    OK
  0.05      0.007     2.344    2.344    0.000   0.074    OK
  0.10      0.013     2.350    2.349    0.000   0.130    OK
  0.20      0.025     2.412    2.411    0.001   0.230    OK
  0.35      0.046     2.481    2.478    0.003   0.376    OK
```

**Experiment 1** (`experiment1.py`, `exp2b.py`) — full tables in §7.2–7.4. Parameters: $K=12$ classes, 1500 steps per run, first third discarded as burn-in, independent per-entity codes.

Scripts: `theorem-verification/verify6.py`, `experiment1.py`, `exp2b.py`.

---

## Sources

- Fannes; Audenaert, *A sharp continuity estimate for the von Neumann entropy* (2007) — the continuity bound in Theorem 6.2; classical (Shannon) form in Csiszár–Körner.
- Levin, Peres & Wilmer, *Markov Chains and Mixing Times* — the TV coupling characterization used in Theorem 6.3.
- Kemeny & Snell, *Finite Markov Chains* — lumpability, now shown inessential to the floor.
- [Givan, Dean & Greig, *Equivalence notions and model minimization in MDPs* (AIJ 2003)](https://www.sciencedirect.com/science/article/pii/S0004370202003764) — Theorem 4's algorithm; route for open problem 1.
- [Ferns et al., *Bisimulation Metrics are Optimal Value Functions* (UAI 2014)](https://www.auai.org/uai2014/proceedings/individuals/67.pdf) — the metric form of $\varepsilon$-adequacy.
- [Nair & Evans (Automatica 2003)](https://people.eng.unimelb.edu.au/gnair/NairAuto03.pdf); Tatikonda & Mitter — achievability machinery for open problem 2.
