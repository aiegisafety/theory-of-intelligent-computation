# TIC — Theorem Layer v0.2

**Theorem 4: where $\sim_\theta$ comes from. Theorem 5: what entropy is not.**

Extends `TIC-Theorems-v0.1.md` (Theorems 1–3). Companion to `TIC-Consolidated-v0.3.md`.

This instalment does two different kinds of work. Theorem 4 **closes the open problem** listed last as the hardest in v0.1 §4: the task equivalence $\sim_\theta$, which every result in Part III assumes is given, turns out to be canonically determined — it exists, is unique, and is computable. Theorem 5 **refutes the theory's own centrepiece slogan**: the Deliberation Value Proposition $\Delta H_D \to \Delta H_S^{future}$, called "the sharpest statement TIC currently has" in v0.3 §1.8, is false, and the failure has a sharp characterization.

Both are what a working formalism is supposed to do. The first shows the definitions generating structure that was not put in by hand; the second shows them talking back.

| | Statement | Status |
|---|---|---|
| **Theorem 4** | Canonical Abstraction — $\sim_\theta^{*}$ exists, is unique, is computable | **Proved**; exhaustively verified (300/300 MDPs) |
| **Cor. 4.2** | Every task has an intrinsic bandwidth $h_\theta \le h$ | **Proved** |
| **Theorem 5** | Entropy is not the objective of intelligent computation | **Proved** (counterexample + exact threshold), verified |

---

## 4. Theorem 4 — Canonical Abstraction

### 4.1 The problem it closes

Theorem 3 and its corollaries — the cooperation criterion, the operational bandwidth law — all begin "let $\sim_\theta$ be a task equivalence satisfying (D) and (G)". This was the theory's largest remaining piece of hand-waving: an agent that must be *given* its abstraction is not doing the interesting part of the work, and a designer free to choose $\sim_\theta$ can make the bandwidth law say anything.

### 4.2 Setting

Finite state set $\mathcal{S}$, finite action set $\mathcal{A}$ with kernels $P_a$, and a goal/constraint labelling $g:\mathcal{S}\to L$ (which states satisfy the goal, which violate constraints). An equivalence $\sim$ on $\mathcal{S}$ is **$\theta$-adequate** iff

- **(G)** $S_1\sim S_2 \Rightarrow g(S_1)=g(S_2)$;
- **(D)** $S_1\sim S_2 \Rightarrow$ for every $a$ and every $\sim$-block $B$: $P_a(B\mid S_1) = P_a(B\mid S_2)$.

Write $\mathcal{Q}_\theta$ for the family of $\theta$-adequate equivalences, partially ordered by coarseness.

### 4.3 Lemma 4.1 (join closure)

If $\sim_1,\sim_2 \in \mathcal{Q}_\theta$ then their join $\sim \;=\; (\sim_1\cup\sim_2)^{*}$ is in $\mathcal{Q}_\theta$.

**Proof.** Let $S,T$ lie in the same join block; then there is a chain $S=X_0 \sim_{i_1} X_1 \sim_{i_2}\cdots\sim_{i_k} X_k = T$ with each $i_j\in\{1,2\}$.

*(G)* Each step preserves $g$, hence $g(S)=g(T)$.

*(D)* Let $B$ be a block of the join. Since $\sim_1$ refines the join, $B$ is a disjoint union of $\sim_1$-blocks $C_1,\dots,C_r$. For a step $X\sim_1 Y$:

$$P_a(B\mid X)=\sum_{j} P_a(C_j\mid X) = \sum_j P_a(C_j\mid Y) = P_a(B\mid Y)$$

using (D) for $\sim_1$ on each $C_j$. Identically for $\sim_2$. Chaining the steps gives $P_a(B\mid S)=P_a(B\mid T)$. $\blacksquare$

*The step that matters is the middle equality: coarsening only sums block-probabilities, and equalities survive summation. This is why adequacy is stable upward — the property is not fragile under merging.*

### 4.4 Theorem 4

> **The family $\mathcal{Q}_\theta$ has a unique maximum $\sim_\theta^{*}$ — the coarsest $\theta$-adequate equivalence. It is obtained by partition refinement starting from the $g$-partition, in polynomial time.**

**Proof.** $\mathcal{Q}_\theta$ is non-empty (the identity relation is adequate) and closed under joins (Lemma 4.1); on a finite set this makes it a complete join-semilattice, whose maximum is the join of all its members. A maximum in a partial order is unique, giving $\sim_\theta^{*}$.

*Computation.* Let $\Pi_0$ be the $g$-partition and let $\Pi_{n+1}$ split each block of $\Pi_n$ by the signature $s \mapsto \big(P_a(B\mid s)\big)_{a\in\mathcal{A},\,B\in\Pi_n}$. Two claims:

1. *The fixed point is adequate.* Refinement preserves (G) since it only splits, and stationarity means no state pair in a block has differing block-transition vectors — which is (D).
2. *$\sim_\theta^{*}$ refines every $\Pi_n$.* Induction. $\sim_\theta^{*}$ refines $\Pi_0$ by (G). If it refines $\Pi_n$, then each $\Pi_n$-block is a union of $\sim_\theta^{*}$-blocks, so by (D) any two $\sim_\theta^{*}$-equivalent states have identical $\Pi_n$-signatures and are not split; hence $\sim_\theta^{*}$ refines $\Pi_{n+1}$.

By (2) the fixed point is coarser than or equal to $\sim_\theta^{*}$; by (1) it is adequate, so being coarser than the coarsest adequate forces equality. Each round strictly refines or halts, so at most $|\mathcal{S}|$ rounds; the standard Paige–Tarjan style implementation runs in $O(|\mathcal{A}|\,|\mathcal{S}|\log|\mathcal{S}|)$. $\blacksquare$

**Verification.** Exhaustive enumeration of all partitions of a 6-state, 2-action MDP with planted structure, 300 random instances: in **300/300** the adequate family had a unique coarsest element, and it equalled the refinement output; a non-trivial abstraction existed in 300/300. Join closure separately: **0 violations in 1994** random pairs of adequate partitions.

### 4.5 What Theorem 4 means for the theory

**The abstraction is not chosen — it is computed from the goal.** Refinement begins at the goal partition (what the task cares about) and stops as soon as dynamics permit. This is the non-circular version of the exploration's intuition that "deliberation determines which states count as the same": the task determines it, deliberation merely operates in the quotient.

Three consequences:

1. **The hand-waving in Theorem 3 is removed.** $\sim_\theta$ was an assumption; it is now a construction.
2. **The designer's freedom is gone.** One cannot pick a convenient abstraction to make the bandwidth law flattering: given the goal and the dynamics, $\sim_\theta^{*}$ is forced.
3. **TIC inherits an algorithm, not just a theorem.** Bisimulation minimization / MDP model minimization is mature (Kanellakis–Smolka; Larsen–Skou; Givan, Dean & Greig). Chapter 2 of v0.3 should be rewritten to cite it as the computational content of State Equivalence rather than describing $\sim_\theta$ as an open modelling choice.

### 4.6 Corollary 4.1 (goal-relative reduction)

Coarser goals yield coarser abstractions: if $g'$ is a coarsening of $g$ then $\sim_{\theta'}^{*}$ is coarser than $\sim_\theta^{*}$. (Immediate: $\Pi_0' $ is coarser and refinement is monotone.) *Asking less of the world buys a smaller state space — and Corollary 4.2 says exactly how much bandwidth that saves.*

### 4.7 Corollary 4.2 (intrinsic task bandwidth)

Under $\sim_\theta^{*}$, condition (D) is precisely lumpability, so the class process $B_t := [S_t]_{\theta}$ is Markov with a well-defined entropy rate $h_\theta$, and

$$h_\theta \;\le\; h$$

**Proof.** Lumpability gives $P(B_{t+1}\mid S_t) = P(B_{t+1}\mid B_t)$, hence $H(B_{t+1}\mid B_t) = H(B_{t+1}\mid S_t)$. Since $B_{t+1}$ is a function of $S_{t+1}$, $H(B_{t+1}\mid S_t) \le H(S_{t+1}\mid S_t) = h$. $\blacksquare$

Combining with Theorem 2 and Corollary 3.3:

> **Every task has an intrinsic minimum synchronization bandwidth $h_\theta$, determined by the goal and the dynamics alone.** Below it, no protocol, architecture, or model capacity permits reliable cooperation; above it, cooperation is possible with residual physical uncertainty arbitrarily large.

*Verified:* blow-up chains with 4 states per class gave $h - h_\theta = 2.000$ bits in every trial — exactly the $\log_2 4$ of discarded within-class detail.

This is, I think, the most consequential statement the theory has produced. It converts an engineering intuition ("how often must we sync?") into a quantity computable from the task specification, and it says the answer does not depend on how clever the agents are.

---

## 5. Theorem 5 — Entropy is not the objective

### 5.1 The claim under examination

v0.3 §1.8 states, as the theory's candidate core theorem:

> $\Delta H_D \to \Delta H_S^{future}$: **good deliberation minimizes future State Entropy under Goal and Normative constraints.**

It has drifted through every draft since the exploration sessions, where it was greeted as "the most important formula in the paper". It is false. Worse, the way it fails is not a technicality: in an identifiable and common regime it inverts the preference order completely.

### 5.2 Disambiguation

"Future state entropy" has two readings, and they behave differently:

- **(i) predictive** — $H(S_{t+1}\mid e_t)$, uncertainty about the next state as seen *before* acting;
- **(ii) posterior** — $\mathbb{E}\,[\,H(S_{t+1}\mid e_{t+1})\,]$, expected uncertainty *after* acting and observing.

### 5.3 Reading (i) is false even for purely epistemic goals

Consider a binary unknown with a uniform prior, and two candidate transitions: **measure** (reveals the value) and **ignore**.

| | $H(S_{t+1}\mid e_t)$ (predictive) | $\mathbb{E}[H(S_{t+1}\mid e_{t+1})]$ (posterior) |
|---|---|---|
| measure | 1.000 bits | **0.000 bits** |
| ignore | 1.000 bits | 1.000 bits |

Predictive entropy cannot distinguish them, and in general *penalizes* informative actions: the outcome of a good measurement is precisely what you cannot predict. Any objective of form (i) rejects information gathering. Reading (i) is discarded.

### 5.4 Reading (ii) is correct exactly for epistemic goals

If the goal *is* to determine the state (diagnosis, inspection, audit, scientific measurement), then value is by definition negative posterior entropy and minimizing (ii) is right — this is standard information-maximizing exploration. Note what has happened: the principle holds where the goal is epistemic, i.e. where entropy reduction *is* the goal. It is a tautology in its domain of validity, not a discovery.

### 5.5 Theorem 5 — failure for achievement goals, with exact threshold

Let the goal be a region $G$ and let candidate transitions $\tau$ have success probabilities $q_\tau = P(S_{t+1}\in G\mid \tau)$. Value is $q_\tau$; goal-relevant outcome entropy is $H_b(q_\tau)$.

> **Theorem 5.** $\arg\min_\tau H_b(q_\tau) = \arg\max_\tau q_\tau$ **iff** $q_{\max} + q_{\min} \ge 1$. In particular, whenever every achievable success probability is below $\tfrac12$, entropy minimization selects the **strictly worst** available transition.

**Proof.** $H_b$ is strictly concave with maximum at $\tfrac12$ and is strictly decreasing in $|q-\tfrac12|$. Hence $\arg\min H_b = \arg\max |q - \tfrac12|$, which coincides with $\arg\max q$ iff $q_{\max}-\tfrac12 \ge \tfrac12 - q_{\min}$, i.e. iff $q_{\max}+q_{\min}\ge 1$. If $q_{\max} < \tfrac12$ then every $q$ lies below $\tfrac12$, so $|q-\tfrac12|$ is decreasing in $q$ and the minimizer of $H_b$ is the minimizer of $q$. $\blacksquare$

**Verification.** $3\times10^5$ random candidate sets: **0 violations** of the threshold condition. In the sub-$\tfrac12$ regime, entropy minimization selected the strictly worst candidate in **100,000 / 100,000** cases. Over random tasks the two criteria agree only ~50% of the time; mean regret when they disagree is 0.26 in success probability, exceeding 0.3 in 39% of cases.

**The instance to remember.** A rescue robot:

| candidate | $P(\text{victim reached})$ | outcome entropy |
|---|---|---|
| aggressive route | **0.40** | 0.971 bits |
| cautious route | 0.05 | 0.286 bits |
| do nothing | 0.00 | **0.000 bits** |

Entropy minimization prescribes *do nothing*. **Certain failure is the lowest-entropy outcome.** Any theory that makes future-state-entropy the objective recommends abandoning the victim, and does so most confidently exactly in the hard cases — those where success is unlikely.

This is the same degeneracy the drafts noticed informally ("an AI that always answers *I don't know* has zero entropy") and tried to patch by adding "under Goal and Normative constraints". Theorem 5 shows the patch fails: constraints restrict the *feasible set*, and the inversion happens *within* the feasible set.

### 5.6 What survives, and what replaces it

**Retired:** the Deliberation Value Proposition as an optimization principle. It is not the theory's core theorem; it is a valid special case for epistemic goals and an inversion for achievement goals below the threshold.

**Retained, and unaffected:** Theorems 1–4 use entropy as a *measured quantity*, never as an objective, and none depends on the retired claim. Theorem 1 accounts for what constraints do to $H_D$; Theorem 2 bounds what confirmation can do to $H_S$; Theorems 3–4 concern equivalence and bandwidth. The formalism is intact.

**Replacement thesis:**

$$\boxed{\ \text{Entropy is the currency and the diagnostic of intelligent computation, not its objective.}\ }$$

with each entropy keeping a precise, non-teleological role:

| | role | governed by |
|---|---|---|
| $H_S$ | how far reality is from being confirmed | Theorem 2 (floor), observation |
| $H_D$ | how far the decision is from being determined | Theorem 1 (constraints), deliberation |
| $H_T$ | dispersion of outcomes — a **risk term inside** the value, not a term to minimize | task's risk attitude |

and the objective remaining the value functional of v0.1 §1.7, $V(D) = \Delta\mathbb{E}[Q(\tau)] - \lambda\,\mathrm{Cost}(D)$.

### 5.7 Consequence for TIC's external positioning

v0.3 §7.1 claimed distinctiveness partly through "the objective is defined on transition space". After Theorem 5 that phrasing must go; the accurate and more defensible claim is:

> TIC does not propose a new objective. It identifies the state- and transition-space **quantities that any intelligent computation must regulate** — and proves what regulating them costs and buys.

This is narrower than the earlier claim and much harder to attack. It also sharpens the contrast with the neighbours rather than blurring it: Active Inference *does* make an entropy-like functional the objective (expected free energy), and Theorem 5 is exactly the kind of question one should ask of it — for achievement goals with low attainable success probability, what keeps expected free energy from preferring certain failure? TIC now has a specific, technical question to put to its nearest competitor instead of a claim of similarity. That is a better position to be in.

---

## 6. Status after v0.2

**Proved so far.** Constraint-collapse accounting and its reversal regime (T1); the residual-indeterminacy floor and synchronization inequality (T2); cooperation by class agreement, its tolerance characterization and survival under uncertainty (T3); existence, uniqueness and computability of the canonical task abstraction, and intrinsic task bandwidth (T4); the failure of entropy-as-objective with exact threshold (T5).

**Two of the five results are corrections to claims the theory previously made loosely** — Corollary 1.4 (constraints can raise $H_D$) and Theorem 5 (entropy is not the objective). That ratio is healthy at this stage and should be expected to fall as the formalism stabilizes.

**Required edits to v0.3.** §1.8 (rewrite the Deliberation Value Proposition box per §5.6); §7.1 (positioning per §5.7); Ch. 2 (cite bisimulation minimization as the computational content of $\sim_\theta$, per §4.5); §7.4/7.7 (retire open problems 3–4, which Theorem 4 closes).

**Open, re-prioritized.**

1. **Achievability for Theorem 2** — is the floor $h-C$ approached by an optimal confirmation protocol? Import from the data-rate-theorem literature. *Now the top item: it is the difference between an impossibility result and a design rule.*
2. **Approximate abstraction.** Theorem 4 requires exact (D). Real tasks are only approximately lumpable; bisimulation metrics supply the relaxation, and the bandwidth law should degrade continuously in the approximation error. **This is the highest-value technical extension** — without it, Theorem 4 is a statement about idealized systems.
3. **Learning $\sim_\theta^{*}$ from experience** rather than computing it from a known model. Theorem 4 assumes the dynamics are given; an agent must estimate them. This is the honest residue of "where does the abstraction come from".
4. **The value functional's own theory** — conditions under which $V(D)$ is computable or approximable, and its relation to the metareasoning literature's stopping rules.
5. **A minimal experiment.** Still outstanding, and now better specified: prediction 4′ (cooperation collapses when channel capacity falls below $h_\theta$, and is insensitive to physical-state uncertainty above it) is directly testable in simulation and would be the first empirical claim of the theory.

---

## Appendix N2 — Verification output

**Theorem 4.**
```
TEST 1  exhaustive (n=6 states, 2 actions), 300 random MDPs with planted symmetry
  unique coarsest adequate partition = refine() in 300/300 MDPs;
  non-trivial abstraction found in 300/300
TEST 2  join of two adequate partitions is adequate
  violations: 0/1994
TEST 3  entropy rate of quotient vs ground chain
  h(ground)=3.383  h_theta=1.383      h(ground)=3.415  h_theta=1.415
  h(ground)=3.307  h_theta=1.307      h(ground)=3.293  h_theta=1.293
  h(ground)=3.455  h_theta=1.455        (blow-up factor 4 = 2.000 bits, exactly)
```

**Theorem 5.**
```
A) rescue robot: argmax P(goal) = aggressive route (0.40)
                 argmin H       = do nothing (0.00)   <-- certain failure
B) threshold  argmin Hb == argmax q  iff  q_max+q_min >= 1
   violations: 0/300000;  criteria agree in 50.0% of random tasks
C) mean regret when they disagree: 0.262   P(regret>0.3)=0.393   max 0.999
D) sub-1/2 regime: entropy-min picks the strictly worst candidate 100000/100000 = 100.0%
E) predictive reading cannot distinguish measure from ignore (both 1.000 bits);
   posterior reading separates them (0.000 vs 1.000)
```

Scripts: `theorem-verification/verify4.py`, `verify5.py`.

---

## Sources

- Kanellakis & Smolka; Larsen & Skou (probabilistic bisimulation); Paige & Tarjan (partition refinement) — Theorem 4's algorithm.
- [Givan, Dean & Greig, *Equivalence notions and model minimization in Markov decision processes* (AIJ 2003)](https://www.sciencedirect.com/science/article/pii/S0004370202003764) — the MDP form of Theorem 4.
- Kemeny & Snell, *Finite Markov Chains* — lumpability, Corollary 4.2.
- [Ferns et al., *Bisimulation Metrics are Optimal Value Functions* (UAI 2014)](https://www.auai.org/uai2014/proceedings/individuals/67.pdf) — route for open problem 2.
- [Nair & Evans (Automatica 2003)](https://people.eng.unimelb.edu.au/gnair/NairAuto03.pdf); Tatikonda & Mitter — open problem 1.
- [Russell & Wefald, *Principles of Metareasoning* (AIJ 1991)](https://www.sciencedirect.com/science/article/abs/pii/000437029190015C) — the value functional retained in §5.6.
- [Parr, Pezzulo & Friston, *Active Inference* (MIT Press 2022)](https://direct.mit.edu/books/oa-monograph/5299/Active-InferenceThe-Free-Energy-Principle-in-Mind) — the comparison sharpened in §5.7.
