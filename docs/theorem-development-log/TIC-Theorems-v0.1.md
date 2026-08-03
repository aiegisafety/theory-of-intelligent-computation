# TIC — Theorem Layer v0.1

**Three theorems for the Theory of Intelligent Computation**

Companion to `TIC-Consolidated-v0.3.md`. This document exists because v0.3's honest status report said: *definitions many, completed proofs zero.* It closes that gap for the three candidates identified in v0.3 §7.4.

All entropies in bits ($\log = \log_2$). Every claim below is either **proved**, **proved under stated assumptions**, or explicitly labelled **cited** / **conjecture**. Numerical verification scripts and their outputs are reproduced in Appendix N.

| | Statement | Status |
|---|---|---|
| **Theorem 1** | Constraint Collapse — exact entropy accounting for pruning | **Proved** (exact identity + corollaries), verified to $4\times10^{-15}$ |
| **Theorem 2** | Residual Indeterminacy — $H_S \ge h - C$ | **Proved** (converse bound), verified in simulation |
| **Theorem 3** | Cooperation by Class Agreement | **Proved** from Ch. 2 conditions; corollaries verified |

The three are not independent: Theorem 3 combined with Theorem 2 yields the **Operational Bandwidth Law** (§3.6), which is the most directly useful consequence in the theory so far.

---

## 1. Theorem 1 — Constraint Collapse

### 1.1 Setting

Let the candidate transition set be $\Omega_\tau$ with deliberative distribution $P$ (Ch. 3: $P(\tau)$ is the running estimate that $\tau$ will be the committed transition). A constraint $c$ partitions

$$\Omega_\tau = A \sqcup B, \qquad B = \{\tau : c(\tau) \text{ violated}\}, \qquad p := P(B) \in (0,1)$$

Pruning replaces $P$ by its conditional $P_A$ on the survivors. Write $P_B$ for the conditional on the eliminated set. Define the **collapse**

$$\Delta H_D := H(P) - H(P_A)$$

Note that no observation occurs: $H_S$ is untouched. This is the phenomenon v0.2 named *Constraint Collapse* — uncertainty removed by normative structure rather than by evidence.

### 1.2 Theorem 1 (exact accounting)

$$\boxed{\ \Delta H_D \;=\; H_b(p) \;+\; p\,\big[H(P_B) - H(P_A)\big]\ }$$

where $H_b(p) = -p\log p - (1-p)\log(1-p)$.

**Proof.** The grouping (recursivity) property of Shannon entropy applied to the partition $\{A,B\}$ gives

$$H(P) = H_b(p) + (1-p)\,H(P_A) + p\,H(P_B)$$

Subtracting $H(P_A)$ from both sides:

$$H(P) - H(P_A) = H_b(p) + p\,H(P_B) + \big[(1-p) - 1\big]H(P_A) = H_b(p) + p\big[H(P_B) - H(P_A)\big] \qquad \blacksquare$$

*Verified over $2\times10^5$ random instances; maximum deviation $4.0\times10^{-15}$ (floating point).*

### 1.3 Corollary 1.1 (uniform law)

If $P$ is uniform on $n$ candidates and the constraint eliminates $k$ of them, $p = k/n$:

$$\boxed{\ \Delta H_D \;=\; \log\frac{1}{1-p}\ }$$

independent of $n$. **Proof.** $H(P) = \log n$, $H(P_A) = \log(n-k)$, so $\Delta H_D = \log\frac{n}{n-k} = -\log(1-p)$. $\blacksquare$

Reading: eliminating half the candidates buys exactly **1 bit**; eliminating 90% buys **3.32 bits**; eliminating 99% buys **6.64 bits**. The price of decisiveness is logarithmic in the pruning ratio — which is why constraints are cheap and exhaustive search is expensive.

### 1.4 Corollary 1.2 (cascade additivity)

Constraints $c_1,\dots,c_m$ applied in sequence, each eliminating a fraction $p_i$ of the *then-surviving* candidates in the uniform regime, collapse

$$\Delta H_D^{total} = \sum_{i=1}^m \log\frac{1}{1-p_i}$$

**Proof.** Survival fractions multiply; logarithms add. $\blacksquare$ *Verified.*

Governance consequence: a normative stack composes **additively in bits**. A policy layer that removes 50% and an authorization layer that removes 60% together deliver $1 + 1.32 = 2.32$ bits of decisiveness, regardless of the size of the original space.

### 1.5 Corollary 1.3 (bounds)

$$H_b(p) - p\log|A| \;\le\; \Delta H_D \;\le\; H_b(p) + p\log|B|$$

from $0 \le H(P_A) \le \log|A|$ and $0 \le H(P_B) \le \log|B|$.

### 1.6 Corollary 1.4 (sign — and when constraints make deliberation *harder*)

$$\Delta H_D > 0 \iff H(P_A) - H(P_B) < \frac{H_b(p)}{p}$$

In particular for elimination of a **single** candidate of mass $p$ (so $H(P_B)=0$):

$$\Delta H_D > 0 \iff H(P_A) < \frac{H_b(p)}{p}$$

*Verified: zero violations over $2\times10^5$ random instances.*

**Sufficient condition for guaranteed reduction.** If the eliminated set is at least as internally uncertain as the survivors, $H(P_B) \ge H(P_A)$, then $\Delta H_D \ge H_b(p) > 0$.

**And the interesting failure case.** $\Delta H_D$ can be **negative**: pruning can *raise* deliberation entropy. Take $P = (0.98,\ 0.01,\ 0.01)$ and let the constraint forbid the leading candidate:

$$H(P) = 0.161 \text{ bits} \quad\longrightarrow\quad H(P_A) = 1.000 \text{ bit}, \qquad \Delta H_D = -0.839 \text{ bits}$$

The agent was nearly decided; the constraint vetoed the obvious move and left it genuinely undecided. This is not a defect of the theory — it is the formal counterpart of a familiar experience, and it yields a sharp, testable claim:

> **Constraints that veto the modal candidate increase deliberation cost; constraints that prune the tail decrease it.**

Random pruning raises $H_D$ in only ≈0.1% of cases (verified), so the *typical* effect is collapse — but safety filters are not random: they are precisely the constraints most likely to target the action the system currently most wants to take. **A safety layer can therefore be a net consumer of deliberation compute, and this is measurable.** Designing constraint systems to fire early (before probability mass concentrates) rather than late is, on this account, not a performance tweak but an entropy-accounting requirement.

### 1.7 Corollary 1.5 (compute, under an explicit model)

*Assumptions, stated as a model rather than derived:* (i) deliberation terminates when $H_D \le \varepsilon$; (ii) each deliberative step reduces $H_D$ by at most $\kappa$ bits. Then the number of steps is at least $(H_D - \varepsilon)/\kappa$, and applying a constraint beforehand saves at least

$$\frac{\Delta H_D}{\kappa} \text{ steps, at zero observation cost.}$$

This is the quantitative form of v0.3 §3.5 ("constraints are the cheapest intelligence"), and it is the basis of falsifiable prediction 2.

### 1.8 What Theorem 1 does and does not establish

It establishes exactly how normative structure converts into decisiveness, in bits, with a clean law in the uniform case and an exact identity in general — and it identifies a regime where the effect reverses. It does **not** establish that entropy reduction equals decision quality; that is Theorem 3's domain and, more deeply, the still-unproved Deliberation Value Proposition.

---

## 2. Theorem 2 — Residual Indeterminacy

*v0.3 withdrew the unconditional claim that observation plus communication drives every entity's state estimate to the truth. This section supplies what replaces it: a floor that no protocol can beat.*

### 2.1 Setting

The objective state $S_t$ evolves as a time-homogeneous Markov process on a finite set, with **conditional entropy rate**

$$h := H(S_{t+1} \mid S_t)$$

An entity accumulates evidence $e_t$ (observations, messages, records). The **acquisition capacity** $C$ bounds how much it can learn per step:

$$I\big(S_{t+1};\, e_{t+1} \mid e_t\big) \;\le\; C$$

$C$ aggregates every channel through which the entity confirms reality — sensor bandwidth, query rate, access permissions, message throughput. Define $U_t := H(S_t \mid e_t)$; by §1.6 of v0.3 this is $H_S$ measured against the entity's evidence.

### 2.2 Theorem 2 (floor)

$$\boxed{\ U_t \;\ge\; h - C \quad \text{for all } t \ge 1, \text{ for every protocol}\ }$$

**Proof.** Two steps.

*Prediction.* Since $S$ is Markov, $S_{t+1} \perp e_t \mid S_t$, hence $H(S_{t+1}\mid e_t, S_t) = H(S_{t+1}\mid S_t) = h$. Conditioning cannot increase entropy, so

$$H(S_{t+1}\mid e_t) \;\ge\; H(S_{t+1}\mid e_t, S_t) \;=\; h$$

*Correction.* By definition of conditional mutual information,

$$U_{t+1} = H(S_{t+1}\mid e_{t+1}) = H(S_{t+1}\mid e_t) - I\big(S_{t+1}; e_{t+1}\mid e_t\big) \;\ge\; h - C \qquad \blacksquare$$

*Verified by exact belief filtering on random walks over $\mathbb{Z}_m$ with quantized observation channels; the floor held in every configuration tested (Appendix N).*

### 2.3 Corollary 2.1 (the synchronization inequality)

$$H_S \le \varepsilon \ \text{ is attainable only if } \ C \ \ge\ h - \varepsilon$$

> **The rate at which an entity confirms reality must exceed the rate at which reality changes.**

Every operational instance of this is the same inequality: standup frequency vs. project volatility, monitoring interval vs. system dynamics, cache TTL vs. write rate, agent polling vs. environment change. It also says what happens when the inequality fails — not degraded accuracy, but a hard entropy floor no amount of reasoning can penetrate. *A system whose state changes faster than it can be confirmed cannot be reasoned about, however capable the reasoner.*

### 2.4 Tightness, and honesty about it

Theorem 2 is a **converse** (impossibility) bound: it says no protocol beats $h-C$, not that $h-C$ is achieved. In simulation the measured steady state exceeded the floor substantially (e.g. floor 2.00 bits vs. measured 3.88 bits) because the observation channel used was a fixed quantizer, not an optimally designed code. Closing that gap — achievability — is open, and is where the continuous-state analogue is instructive: the **data-rate theorem** of networked control (Tatikonda & Mitter; Nair & Evans) gives matching necessary-and-sufficient rates for stabilizing a linear system over a limited channel, with the threshold set by the system's entropy production. TIC's Theorem 2 is the discrete, estimation-side counterpart; importing the achievability machinery is the natural next step.

### 2.5 Theorem 2b (agreement obstruction) — cited, not proved here

Capacity is not the only obstruction. Even with $C$ large, in an asynchronous system with unreliable delivery, **common knowledge is unattainable** (Halpern & Moses; the coordinated-attack result). Consequently no protocol can make several entities *mutually certain* that they share the same state.

The two obstructions are independent — **rate** (information-theoretic) and **reliability** (distributed-computing) — and together they establish the honest claim of the Shared State architecture:

> Shared State does not guarantee agreement. It guarantees that divergence is **bounded, attributable, and correctable**, because there is a single referent to be wrong about.

---

## 3. Theorem 3 — Cooperation by Class Agreement

*The theorem that makes Part III more than an architecture sketch — and the one that makes Theorem 2's floor survivable.*

### 3.1 Setting

From v0.3 Ch. 2: a task $\theta$ induces an equivalence $\sim_\theta$ on states satisfying

- **(D) Dynamic compatibility.** $S_1 \sim_\theta S_2 \Rightarrow P([\cdot]_\theta \mid S_1,\tau) = P([\cdot]_\theta \mid S_2,\tau)$ for every admissible $\tau$.
- **(G) Goal compatibility.** Equivalent states are indistinguishable with respect to goal satisfaction and constraint violation.

Let $\mathcal{A}_\theta(S)$ be the set of transitions that are constraint-valid and goal-admissible at $S$. Call a deliberation procedure **$\theta$-sound** if it selects from $\mathcal{A}_\theta$ of its own current state estimate.

### 3.2 Lemma 3.1 (admissibility is class-determined)

If $S_1 \sim_\theta S_2$ then $\mathcal{A}_\theta(S_1) = \mathcal{A}_\theta(S_2)$.

**Proof.** Validity of $\tau$ depends on constraint violation at the current state and at successors. By (G) the current-state test agrees on $S_1,S_2$. By (D) the successor class-distributions agree, and by (G) again goal-admissibility is a function of successor classes; hence the successor test agrees. $\blacksquare$

Thus $\mathcal{A}_\theta$ descends to the quotient: it is a function of $[S]_\theta$.

### 3.3 Theorem 3

Let entities $A,B$ hold representations $\hat S_A, \hat S_B$ and deliberate $\theta$-soundly. If

$$\boxed{\ [\hat S_A]_\theta = [\hat S_B]_\theta\ }$$

then:

1. **No admissibility conflict.** $\mathcal{A}_\theta(\hat S_A) = \mathcal{A}_\theta(\hat S_B)$ — every transition either entity considers admissible is admissible to the other. Neither can regard the other's choice as invalid.
2. **Diversity preserved.** They need not select the same $\tau$: any $\tau_A \ne \tau_B$ within the common admissible set is compatible. Deliberative diversity is not merely tolerated but structurally unconstrained.
3. **Compatible successors.** By (D) the resulting class-distributions are determined by the class and the chosen transition, so both entities can predict each other's effect at task resolution without modelling each other's reasoning.

**Proof.** (1) is Lemma 3.1. (2) is immediate since (1) constrains the set, not the choice. (3) is (D). $\blacksquare$

### 3.4 Corollary 3.1 (strictly weaker than agreement)

$\hat S_A = \hat S_B \Rightarrow [\hat S_A]_\theta = [\hat S_B]_\theta$, never the converse when classes are non-singleton. **Cooperation therefore requires strictly less than agreement**, and the slack is the diameter of the class under the state metric.

The slack is not a numerical tolerance. Verified demonstration (server-load task, classes *idle* $<50$, *normal* $[50,80)$, *loaded* $\ge 80$):

| $\hat S_A$ | $\hat S_B$ | numeric gap | same class | admissible sets equal |
|---|---|---|---|---|
| 78.0 | 79.0 | 1.0 | yes | **yes** |
| 20.0 | 45.0 | 25.0 | yes | **yes** |
| 78.0 | 81.0 | 3.0 | no | no |
| 49.9 | 50.1 | 0.2 | no | no |

Two entities differing by 25.0 cooperate; two differing by 0.2 do not. **Consistency is not numerical closeness — it is class agreement.** This retires the intuition that cooperation degrades smoothly with disagreement, and explains why "we're roughly aligned" is not a meaningful cooperation criterion while "we agree it's overloaded" is.

### 3.5 Corollary 3.2 (cooperation survives residual indeterminacy)

Cooperation does not require $H_S \to 0$. It requires only that residual indeterminacy be **class-internal**:

$$\boxed{\ \Omega(e_i) \subseteq [S^{*}]_\theta \quad \text{for every participating entity } i\ }$$

Then every entity's possibility set lies in one class, all class assignments coincide, and Theorem 3 applies — even where $H_S$ is large.

This is what makes Theorem 2 livable. The floor $h - C$ is unavoidable; it is also frequently irrelevant, because what must be confirmed is the class, not the state.

### 3.6 Corollary 3.3 (Operational Bandwidth Law)

Apply Theorem 2 to the **quotient** process $[S_t]_\theta$ rather than to $S_t$. Condition (D) is precisely (probabilistic) **lumpability** in the sense of Kemeny & Snell, which is what makes the class process a well-defined Markov chain with its own entropy rate $h_\theta \le h$. Then:

$$\boxed{\ \text{Required synchronization capacity } = h_\theta,\ \text{the entropy rate of the \emph{operational} state — not } h\ }$$

Verified. Random walk on $\mathbb{Z}_{64}$, step entropy $h = 3$ bits/step, observation capacity $C = 1$ bit/step:

| task classes $K$ | $H_S$ (physical) | $H_\theta$ (operational) | $\Pr[\Omega(e) \subseteq$ one class$]$ |
|---|---|---|---|
| 64 (full precision) | 3.86 bits | 3.86 bits | 0.00 |
| 8 | 3.86 bits | 1.04 bits | 0.11 |
| 2 | 3.86 bits | **0.00 bits** | **1.00** |

At $K=2$ the entity has essentially **no idea** where the physical state is (3.86 bits of indeterminacy, near-maximal) and yet knows the operational class with certainty and can cooperate 100% of the time, on a channel three times too slow to track the state.

This is the quantitative form of the football observation: eleven players share ball position, score and tactical intent — never coordinates — and cooperate on a channel of a few bits per second. It also inverts a standard engineering instinct: **the way to make a multi-agent system cooperate under bandwidth pressure is not to synchronize harder but to coarsen the task abstraction**, and Corollary 3.3 says exactly how much that buys.

---

## 4. What is now proved, and what remains

**Proved.** Constraint collapse accounting and its uniform law, cascade additivity, sign condition and the reversal case (Th. 1). The impossibility floor on state uncertainty and the synchronization inequality (Th. 2). Class-determined admissibility, cooperation under class agreement, its strict weakness relative to agreement, its survival under residual indeterminacy, and the operational bandwidth law (Th. 3).

**Consequences for v0.3.** §3.5 ("constraints are the cheapest intelligence") is now quantified — *and qualified*: Corollary 1.4 identifies the regime where it is false. §6.2's Theorem B is now proved in its rate form. §5.4's cooperation criterion is now a theorem with a tolerance characterization. Falsifiable predictions 2, 3 and 4 acquire quantitative forms; prediction 4 becomes prediction *4′*: cooperation degrades sharply when $C < h_\theta$ — the threshold is set by the operational, not physical, entropy rate.

**Still open, in priority order.**

1. **Achievability for Theorem 2** — is $h-C$ approached by an optimal confirmation protocol? Import from the data-rate-theorem literature.
2. **The Deliberation Value Proposition** $\Delta H_D \to \Delta H_S^{future}$ — still the deepest unproved claim, and the one that would connect Theorems 1 and 3 into a single optimization principle. Suggested first step: a finite-MDP instance where deliberation is explicit search and the value functional $V(D)$ is computable.
3. **Abstraction soundness** (v0.3 §2.3) — deliberation over $\mathcal{S}/\!\sim_\theta$ loses nothing. Special cases exist in the state-abstraction literature; the general statement does not.
4. **Where $\sim_\theta$ comes from.** Every result in §3 assumes the task equivalence is given. How an entity *discovers* an adequate abstraction is untouched — and is probably the hardest and most valuable open problem in TIC.
5. **Non-lumpable tasks.** When (D) fails, the class process is not Markov and $h_\theta$ is not well defined; approximate lumpability and bisimulation metrics are the route.

**A note on what these theorems are.** None is deep mathematics; Theorem 1 is an application of the grouping axiom and Theorem 2 a two-line data-processing argument. Their value is not difficulty but **placement**: they are the first statements in TIC that are simultaneously derived from its definitions, quantitative, and falsifiable. A theory earns the right to its vocabulary by proving things with it, and until now TIC had proved nothing. It has now proved three things, one of which (Corollary 1.4) contradicts a claim the theory previously made loosely — which is the better evidence that the machinery is doing work.

---

## Appendix N — Numerical verification

All scripts run under Python 3 / NumPy; outputs reproduced verbatim.

**N.1 Theorem 1.** $2\times10^5$ random distributions, random eliminated subsets.

```
identity max error:                    3.997e-15
uniform corollary max error:           6.217e-15
dominant-removal: H before=0.1614  after=1.0000  Delta=-0.8386
fraction of prunings that RAISE H_D:   0.0010
threshold test violations (Cor 1.4):   0
cascade: sum of steps=2.1520   -sum log2(1-p)=2.1520
```

**N.2 Theorem 2.** Exact Bayesian filtering, random walk on $\mathbb{Z}_m$ (step uniform over $q$, so $h=\log q$), observation = which of $2^C$ bins contains the state.

```
 m   q   C |   h=log2 q   h-C(floor)   measured U_inf   floor respected
 64   8   1 |    3.000        2.000          3.879        OK
 64   8   2 |    3.000        1.000          3.287        OK
 64   8   3 |    3.000        0.000          2.657        OK
 64   4   1 |    2.000        1.000          3.493        OK
 64  16   2 |    4.000        2.000          3.658        OK
128  16   1 |    4.000        3.000          4.861        OK
128   2   1 |    1.000        0.000          3.680        OK
 64   8   4 |    3.000       -1.000          1.846        OK
```

The gap between floor and measurement is the achievability gap of §2.4 (fixed quantizer, not an optimal code).

**N.3 Theorem 3.** Same chain, $C=1$ bit/step, task classes = contiguous blocks; table in §3.6. Admissibility demonstration table in §3.4.

Scripts: `verify1.py`, `verify2.py`, `verify3.py` (regenerable; ~40 lines each).

---

## Sources

- Grouping/recursivity axiom of entropy — Shannon 1948; see Cover & Thomas, *Elements of Information Theory*, §2.
- [Halpern & Moses, *Knowledge and Common Knowledge in a Distributed Environment*, JACM 1990](https://groups.csail.mit.edu/tds/papers/Halpern/JACM90.pdf) — Theorem 2b.
- [Nair & Evans, data-rate theorem for stabilization over limited-capacity channels (Automatica 2003)](https://people.eng.unimelb.edu.au/gnair/NairAuto03.pdf); Tatikonda & Mitter — achievability analogue for §2.4.
- Kemeny & Snell, *Finite Markov Chains* — lumpability, underlying Corollary 3.3.
- [Ferns et al., *Bisimulation Metrics are Optimal Value Functions* (UAI 2014)](https://www.auai.org/uai2014/proceedings/individuals/67.pdf) — approximate version of condition (D), route for open problem 5.
- [Russell & Wefald, *Principles of Metareasoning* (AIJ 1991)](https://www.sciencedirect.com/science/article/abs/pii/000437029190015C) — the value functional in Corollary 1.5.
