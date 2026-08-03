# Abstraction and Bandwidth in Intelligent Computation
## A Task-Relative Theory of State Computation

**[Author name]**$^{1}$

$^{1}$[Affiliation] — Correspondence: [email]

**Theory of Intelligent Computation (TIC) — Main Paper v1.0 (English edition)**

Date: 2026-08-02

*Suggested arXiv subject classes: cs.AI (primary); cs.IT, cs.MA, cs.LO (cross-list)*

---

## Abstract

We give a formal theory of **intelligent computation**. Its central claim is:

> **Intelligent computation is the selection of state transitions on the coarsest abstraction determined by the goal.**

Every clause of that sentence is provable, measurable, and falsifiable. Concretely:

1. **Abstraction is not designed, it is computed.** Given a goal and a dynamics, there exists a **unique coarsest** task-sufficient equivalence relation $\sim_\theta^*$, computable in polynomial time (Theorem 4). The designer has no free parameter here.

2. **Every task has an intrinsic bandwidth $h_\theta$.** The channel capacity required for multi-agent coordination is priced by $h_\theta$ alone, **independent of the size of the physical state space and of the physical entropy rate** (Theorem 6). We test this with three mutually independent experiments: adding 2.000 bits to the physical entropy rate, multiplying the state count by 16, and raising the dimension of a continuous state from 4 to 20 — the threshold moves by 0.05 bits, 0.36 bits, and 0.02 bits respectively (the performance curve itself does not move at all).

3. **The threshold is a tail probability, not a cliff.** The zero-error form of the bandwidth law, $C\ge h_\theta$, is falsified by measurement: the empirical threshold sits systematically below $h_\theta$, and the transition is smooth rather than sharp. We prove that the error rate is governed by the **upper-tail probability of the per-step information variable** (Theorem 14), yielding the fault-tolerant form
$$C^*(\varepsilon)\;\approx\;h_\theta+\sigma_\theta\,Q^{-1}(\varepsilon),$$
   which introduces a second per-task quantity, the **operational variance-entropy** $\sigma_\theta^2$. $h_\theta$ fixes the location of the threshold; $\sigma_\theta$ fixes the width of the transition band. Predicting the threshold from task structure alone — with no fitted parameters — gives a mean error of 0.286 bits, a 2.95× improvement over the naive prediction.

4. **Ontological drift is charged for only when it cannot be absorbed.** The common intuition that "a faster-changing world demands more bandwidth" is wrong. We prove, and confirm experimentally, that when drift is a symmetry of the state space, the canonical abstraction absorbs it entirely, at zero cost (measured: $h_A$ driven up to 1.18 bits/step while the threshold moves by only 0.024 bits); when drift instead changes which distinctions matter, it is charged bit-for-bit (measured slope 1.000, exact to the last digit reported). The corrected two-level rate condition is $C\ge h_\theta+h_A^{\perp}$, and $h_A^\perp$ admits a computable criterion (Theorem 11′).

5. **Entering the continuum requires fault tolerance.** In continuous state spaces, $h_\theta$ as "bits per step" **does not exist** — differential entropy is coordinate-dependent and can be negative. Its replacement is a rate-distortion quantity $R_\theta(D)$. This means the fault-tolerance parameter of Theorem 14 is not a patch; it is the **precondition** for the theory to enter the continuous world at all — the zero-error bandwidth law cannot even be stated there.

We report every negative result and every known boundary of validity alongside the positive ones: a falsified quantitative constant, a Gaussian approximation that fails outside a stated regime, an experimental condition retired as uninformative, and a numerical bug we found in our own code together with an audit of its consequences.

---

## Reading Guide

This is the **long-form** version of the paper, written for two kinds of readers:

- **Readers who want the conclusions**: read the Abstract, §1 (intuition), §6 (the bandwidth law), §9 (the fault-tolerant threshold), and §14 (the summary of validity conditions).
- **Readers who want to check correctness**: every proof is in the main text, not deferred to an appendix; each theorem is immediately followed by its numerical verification and by its **known failure conditions**.

**Many of the definitions here are being proposed for the first time.** Each new definition therefore follows the same four-part template:

> **(a) Intuition** → **(b) A concrete example** → **(c) Formal definition** → **(d) Why it has to be defined this way** (usually: what breaks under the obvious alternative).

Reading only (a) and (b) throughout should be enough to follow the main line of the argument.

**One running example throughout.** We repeatedly return to two scenarios: the **subway map** and **meeting up**. Neither is decorative. The subway map is the cleanest real instance of "the task determines the abstraction"; meeting up under a bandwidth constraint is the smallest nontrivial instance of "coordination under a rate limit."

---

## A note on priority, stated before anything else

One objection is predictable enough that we address it here rather than let it surface only in §16. Readers who know finite-blocklength information theory will recognize the shape of $\sigma_\theta^2$ immediately: a variance of a per-symbol (or per-step) information quantity is exactly how *dispersion* is defined in channel coding (Polyanskiy, Poor, & Verdú, 2010) and in lossless source coding (Kontoyiannis & Verdú, 2013). It is fair to ask whether this paper has simply renamed dispersion.

It has not, for a specific, checkable reason. PPV dispersion and source varentropy are defined on a source or a channel taken as given — fixed objects, external to any notion of task. $\sigma_\theta^2$ is defined on the **quotient chain induced by a task-sufficient equivalence relation**, $\sim_\theta^*$ (Definition 4.1, Theorem 4) — an object that does not exist until a goal has been fixed and the canonical abstraction has been computed from it. Consequences that follow from this difference, not asserted but shown later in the paper: the same physical channel carrying two different tasks has two different values of $\sigma_\theta$ (§10.5, §12.3); $\sigma_\theta$ is measured to be invariant to the size of the physical state space and to the physical entropy rate in a way dispersion, defined on the source itself, has no reason to be (§8, Theorem 11′); and $\sigma_\theta$ feeds directly into a multi-agent coordination threshold (Corollary 14.2) rather than into a single-source or single-channel coding theorem. Section 16.1 restates this formally next to every other point of contact with prior work, and flags it as the place a reviewer is most likely to push back.

---

# Part I — Foundations

## 1. Starting point: intelligence is not knowing as much about the world as possible

### 1.1 What a map tells you

The London Underground map is not a geographic map. It discards true distances, true directions, true curvature, and keeps only which station connects to which and where one can change lines. By any standard of "faithfully describing the world," it is a **wrong** map — every inter-station distance on it is fictitious.

But for the task "how do I get from A to B," it is **much** better than a real geographic map — not marginally better, but better by a wide margin: on a real map you must do the work of filtering out irrelevant geographic detail yourself, and the Underground map has already done that filtering for you.

There is something here worth taking seriously:

> **The distinctions that get erased are not harmless redundancy. They cost something.**

What do they cost? If you had to report your position to a friend in real time, on the Underground map you would say "Central Line, eastbound, next stop Oxford Circus"; on a geographic map you would have to give latitude and longitude. **For the same task, the latter costs many more bits per second.** In a single-agent system this cost shows up as storage and computation; in a multi-agent system it shows up directly as a **communication bill**.

The remainder of this paper turns that intuition into something provable, measurable, and falsifiable.

### 1.2 The central claim, in one line

$$\boxed{\textbf{Intelligent computation = selecting state transitions on the coarsest abstraction determined by the goal.}}$$

Three words in that sentence are load-bearing:

- **Determined by the goal** — not chosen by the designer. We show that the abstraction is **computed**, uniquely determined once a goal and a dynamics are fixed (Theorem 4).
- **Coarsest** — not "as precise a description of the world as possible." Extra distinctions are billed in bits per step (Theorems 2, 6, 14).
- **Selecting state transitions** — this is the actual objective. **Not entropy reduction**: we prove that treating entropy itself as the objective is a mistake (§5.4).

The paper's title, restated more plainly:

> **Intelligence does not mean knowing as much as possible about the world; it means needing to know as little as possible about the world while still doing the right thing.**

### 1.3 Four results and how they fit together

```
        Theorem 4  canonical abstraction  ~θ*  ← abstraction is computed, uniquely coarsest
             │
             │  induces
             ▼
        intrinsic bandwidth  h_θ  ← the fixed rate of a given task
             │
             ├────────────► Theorem 6  bandwidth law  C ≥ h_θ
             │                (corrected empirically ↓)
             ▼
        Theorem 14  fault-tolerant threshold  C*(ε) ≈ h_θ + σ_θ Q⁻¹(ε)
             │           ← introduces a second quantity σ_θ (operational variance-entropy)
             ├────────────► Theorem 11′  time dimension: C ≥ h_θ + h_A^⊥
             │
             └────────────► continuum limit: h_θ ⇝ R_θ(D)
                             ← fault tolerance is a precondition, not a patch
```

**How to read this**: Theorem 4 constructs the object, $h_\theta$ assigns it a number, Theorem 6 says that number is the price of coordination, Theorem 14 says that price must be discounted according to the required reliability, Theorem 11′ extends it across time, and the continuum limit explains why Theorem 14 is not optional.

---

## 2. Ontology: five primitives

### 2.1 Why primitives have to be fixed first

The easiest way for a theory to die is conceptual proliferation: a new concept for every new phenomenon, until the theory explains everything and predicts nothing. We therefore fix one rule up front and hold to it throughout:

> **Rule (admission of concepts).** A concept enters the theory only if it is one of the five primitives, is **constructively defined** from the primitives, or appears in the statement of some theorem. Anything satisfying none of the three is a **candidate**, not part of the theory.

This rule has actually done work in this project: it kept out a number of superficially attractive notions — "emergent collective state," "curvature of the state manifold" — for which no theorem ever needed them.

### 2.2 The five primitives

| Primitive | Symbol | One line |
|---|---|---|
| **State** | $S$ | A complete description of the world at an instant |
| **Transition** | $\tau$ | A map from a state to a distribution over states (a stochastic kernel) |
| **Observation** | $O$ | A map from a state to evidence (in general many-to-one) |
| **Deliberation** | $D$ | The process of committing to one among several candidate transitions |
| **Entropy** | $H$ | A measure of uncertainty (in two layers, see §3) |

**Explicitly excluded from the primitives** (all of these are constructed, not basic): action, memory, identity, goal, constraint, language, shared state.

Two of these exclusions are worth spelling out:

- **Action is not a primitive.** An action is simply "a transition committed to by some entity." Treating it as primitive would give the same phenomenon two different notations and would make it awkward to express changes that the environment produces on its own.
- **Memory is not a primitive.** We prove (Theorem 9) that the minimal task-sufficient memory is **exactly equal** to the current operational state. Once something is provable, it should not also be assumed.

### 2.3 An entity is an index, not an object

This is a place where it is easy to get tangled, and it deserves to be treated separately.

**The problem.** If "entity" is defined first and "identity" is defined in terms of entities, then answering "what counts as the same entity" requires an answer to identity — which in turn requires entities. Circular.

**The resolution.** Do not treat an entity as an object; treat it as an **index**. State is written $S(E,t)$, and the state space is **fibered** over an index set of entities.

> **Example.** "Seat 5, row 3" is not a person, it is a location; who happens to sit there is a separate question. The theory describes the structure of the seating chart, not who occupies which seat.

This lets "identity" be defined, without presupposing any essence of the entity, as **whatever varies slowly and stays constant over time** (§12) — and the circularity is broken.

---

## 3. Two layers of entropy

### 3.1 Why two layers are needed

**(a) Intuition.** "Uncertain" carries two quite different meanings:

- **I don't know which of these three cases holds** (but I cannot say any is more likely than another);
- **I believe there is a 70% chance it's the first case.**

The first needs no probability; the second does. Most formal theories (POMDPs, Active Inference) start directly from the second — they assume the agent already has a probabilistic belief. That is a strong assumption.

**(b) Example.** Emergency triage. A nurse looks at a patient and her first judgment is often: "this could be a heart attack, could be acid reflux, could be a panic attack." She gives **no** probabilities, and does not need to. What she does next (order an ECG) depends only on the **possibility** that a heart attack has not yet been ruled out.

Probability only becomes necessary once a resource must be allocated ("there is one machine — who gets it first").

**(c) Formal definitions.**

> **Definition 3.1 (Layer 0, the possibility layer).** Evidence $e$ induces a **possibility set** $\Omega(e)\subseteq\mathcal S$ — the set of all states consistent with $e$. Its entropy is the Hartley entropy
> $$H_0(e)=\log_2|\Omega(e)|.$$
> This is the theory's **default at the definitional level**: no prior is required.

> **Definition 3.2 (Layer 1, the probabilistic layer).** If a probability measure over states is additionally given, use the Shannon entropy
> $$H_1(e)=H(S\mid e).$$
> The **proofs** of most theorems in this paper operate at this layer.

**(d) Why it has to be defined this way.**

This is not "take your pick." It resolves a real internal inconsistency: an earlier version of this theory used Layer 0 (no prior) at the point of definition but Layer 1 (with a prior) inside proofs — two incompatible notions of entropy in the same document. Separating and labeling the two layers also states precisely where TIC diverges from POMDPs:

> TIC's **definitions** presuppose no prior (Layer 0) — this is what separates it from POMDP belief states; TIC's **quantitative results** mostly live at Layer 1 — this is what lets it connect to information theory.

**One important empirical fact**: in most practical settings, the Layer-0 entropy is **zero** — the available evidence is usually enough to pin the state down to a single possibility. The real uncertainty is usually not "what state is the world in" but "which transition should I take." That observation leads directly into the next section.

### 3.2 Three entropies, each covering its own ground

| Symbol | Name | The question it answers |
|---|---|---|
| $H_S$ | **State entropy** | Which state is the world currently in? |
| $H_D$ | **Deliberation entropy** | Which transition am I about to choose? |
| $H_T$ | **Transition entropy** | Given that transition, which state will result? |

$H_D$ is the least conventional of the three: **it is defined on the space of transitions, not on the space of states.** Most theories only have $H_S$ and $H_T$.

> **Example.** You are standing at a fork. You know exactly where you are ($H_S=0$), and you know exactly where the left branch and the right branch each lead ($H_T=0$). But you have not yet decided which way to go — **that uncertainty is real, and it is the only one left.** It is $H_D$.
>
> A traditional framework would call this "a stochastic policy" and record it as a property of the policy. We think it deserves its own name, because **eliminating it is the entire job of deliberation.**

### 3.3 Constraint collapse: reducing uncertainty without looking at the world

**(a) Intuition.** A constraint ("do not run a red light," "stay under a budget of ten thousand") tells you nothing about what the world is like, but it **removes candidate transitions**, and so lowers $H_D$. This is a way of reducing entropy **without any new observation**.

**(b) Example.** The triage nurse learns "this patient is allergic to penicillin." That fact tells her nothing about the diagnosis ($H_S$ is unchanged), but it instantly eliminates a whole class of treatment plans ($H_D$ drops).

**(c) Formal result.**

> **Theorem 1 (Constraint collapse).** If a constraint eliminates candidate transitions with probability $p$ (under the uniform counting measure of Layer 0), then
> $$\Delta H_0=\log_2\frac{1}{1-p}.$$
> The entropy reductions of a cascade of constraints **add**.

**(d) Why this is worth writing down.** Planning already prunes candidates as a matter of routine, but no one has kept an **entropy ledger** for that pruning. Once it is kept, pruning becomes comparable, in the same units, to communication and to bandwidth — which is the precondition for everything that follows.

---

## 4. Task equivalence and the canonical abstraction

This is the technical core of the paper.

### 4.1 What it means for two states to be "the same" relative to a task

**(a) Intuition.** Under what conditions can two states be treated as one and the same? Back to the Underground: for the task "how do I change lines," "40 people in the carriage" and "41 people in the carriage" are the same. For the task "can I still squeeze on," they may not be.

**Same world, different task, a different notion of "the same."**

**(b) Example (used throughout the paper).** You and a friend need to meet up in a circular mall with 360 numbered positions.

- If the goal is "meet inside the same shop," then position 12 and position 13 (inside the same shop) are **the same**.
- If the goal is "meet on the same floor," then position 12 and position 120 (same floor) are **the same**.
- The coarser the goal, the larger the range of "the same," and the less information you need to send.

**(c) Formal definition.**

> **Definition 4.1 (Task equivalence).** Let $\mathcal S$ be a finite state set, $\mathcal A$ a set of actions (each action $a$ having a stochastic kernel $P_a$), and $g:\mathcal S\to L$ a goal labeling. An equivalence relation $\sim$ is called **$\theta$-sufficient** if
>
> - **(G) Goal-compatible**: $S_1\sim S_2\ \Rightarrow\ g(S_1)=g(S_2)$;
> - **(D) Dynamics-compatible**: $S_1\sim S_2\ \Rightarrow$ **for every action $a$** and every $\sim$-block $B$,
> $$P_a(B\mid S_1)=P_a(B\mid S_2).$$

**(d) Why it has to be defined this way — two points that matter.**

**First, the "for every action" quantifier in (D) is load-bearing, not a formality.** We fell into this trap ourselves during a continuous-state experiment: replacing (D) with "averaged over a stochastic policy" caused the abstraction to merge $+e$ and $-e$ ("the other agent is on my left" versus "on my right") — because the goal "close enough" is **symmetric** under left–right. The merge is entirely correct for predicting the goal, but **a controller must distinguish the two cases**, since they require opposite movements. Measured: readout error 0.194 (about equal to a random guess) with the action-averaged version, versus 0.0055 with the per-action version.

> **A lesson worth remembering on its own**: sufficiency for goal prediction is not the same as sufficiency for control. The difference is exactly that per-action quantifier. The successor-representation literature commonly uses an action-averaged variant, and would run into the same problem on symmetric tasks.

**Second, why "block-transition probabilities agree" is the right condition rather than "reachable sets agree."** The latter is a weaker, more intuitive condition — one that an earlier version of this project actually used — **and it is wrong.**

> **Counterexample (four states, machine-verified).** States $\{s_1,s_2,a,b\}$ with transitions $s_1\to a$, $s_1\to b$, $s_2\to a$, $a\to b$.
>
> | | forward-reachable set | backward-reachable set | one-step successors |
> |---|---|---|---|
> | $s_1$ | $\{a,b\}$ | $\varnothing$ | $a,b$ |
> | $s_2$ | $\{a,b\}$ | $\varnothing$ | $a$ |
>
> The reachable sets are identical, yet $b$ is reachable in one step from $s_1$ but not from $s_2$. **Merging by reachable set fabricates a transition $s_2\to b$ out of thin air, changing the system's behavior.**

This is exactly the distinction that concurrency theory took years to sort out: **trace equivalence versus bisimulation.** Condition (D) in Definition 4.1 is a bisimulation condition.

### 4.2 Theorem 4: the coarsest abstraction exists, is unique, and is computable

**Lemma 4.1 (closure under union).** If $\sim_1,\sim_2$ are both $\theta$-sufficient, then their union (transitively closed), $\sim$, is also $\theta$-sufficient.

**Proof.** Suppose $S,T$ fall in the same block of the union; then there is a chain $S=X_0\sim_{i_1}X_1\sim_{i_2}\cdots\sim_{i_k}X_k=T$ with each $i_j\in\{1,2\}$.

*(G)*: each step preserves $g$, so $g(S)=g(T)$.

*(D)*: let $B$ be a block of the union. Since $\sim_1$ refines the union, $B$ is a disjoint union of $\sim_1$-blocks $C_1,\dots,C_r$. For a step $X\sim_1 Y$ in the chain,
$$P_a(B\mid X)=\sum_j P_a(C_j\mid X)=\sum_j P_a(C_j\mid Y)=P_a(B\mid Y),$$
where the middle equality uses (D) for $\sim_1$. The same holds for $\sim_2$. Transitivity along the chain gives $P_a(B\mid S)=P_a(B\mid T)$. $\blacksquare$

> **The equality in the middle is the crux.** Coarsening only ever **sums** block probabilities, and equalities are preserved under summation. This is why sufficiency is stable upward — merging never destroys it.

**Theorem 4 (Canonical abstraction).**

> The family $\mathcal Q_\theta$ of $\theta$-sufficient equivalence relations has a **unique maximal element** $\sim_\theta^*$ — the coarsest $\theta$-sufficient equivalence relation. It is obtained by **partition refinement** starting from the goal partition, and is computable in polynomial time.

**Proof.** $\mathcal Q_\theta$ is nonempty (the identity relation is trivially sufficient) and closed under union (Lemma 4.1); on a finite set this makes it a complete join-semilattice, whose maximal element is the union of all its members. Maximal elements of a partial order are unique when they exist, so we may write $\sim_\theta^*$ for it.

*Computation.* Let $\Pi_0$ be the partition induced by $g$, and let $\Pi_{n+1}$ split each block of $\Pi_n$ according to the signature
$$s\mapsto\big(P_a(B\mid s)\big)_{a\in\mathcal A,\;B\in\Pi_n}.$$
Two facts complete the proof:

1. *The fixed point is sufficient*: refinement only splits blocks, never merges them, so (G) is preserved; stationarity means any two states in the same block have identical block-transition vectors, i.e., (D) holds.
2. *$\sim_\theta^*$ refines every $\Pi_n$*: by induction. It refines $\Pi_0$ by (G); if it refines $\Pi_n$, then every $\Pi_n$-block is a union of $\sim_\theta^*$-blocks, and by (D) any two $\sim_\theta^*$-equivalent states share the same $\Pi_n$-signature, so they cannot be split apart, meaning it also refines $\Pi_{n+1}$.

By (2), the fixed point is coarser than or equal to $\sim_\theta^*$; by (1) it is sufficient, and $\sim_\theta^*$ is the coarsest sufficient relation, so they coincide. Each round either strictly refines or halts, so there are at most $|\mathcal S|$ rounds; a Paige–Tarjan-style implementation (Paige & Tarjan, 1987) runs in $O(|\mathcal A|\,|\mathcal S|\log|\mathcal S|)$. $\blacksquare$

### 4.3 Three consequences of Theorem 4

1. **The designer's freedom disappears.** One cannot pick a convenient abstraction to make the later bandwidth law say whatever one likes: given a goal and a dynamics, $\sim_\theta^*$ is forced.
2. **A coarser goal buys a smaller state space.** If $g'$ is a coarsening of $g$, then $\sim_{\theta'}^*$ is coarser than $\sim_\theta^*$ (immediate: $\Pi_0'$ is coarser, and refinement is monotone). **Asking less of the world means needing to know less about it.**
3. **TIC inherits an algorithm, not just a theorem.** Bisimulation minimization / model minimization is mature technology (Kanellakis & Smolka, 1990; Larsen & Skou, 1991; Givan, Dean, & Greig, 2003). **This must be said plainly: the computational content of Theorem 4 is not our invention — our contribution is connecting it to bandwidth (§6).**

### 4.4 Intrinsic bandwidth $h_\theta$

**(a) Intuition.** Replace each state with the block it belongs to and one obtains a **quotient chain**. How much new uncertainty this chain produces per step is exactly the information rate intrinsic to the task.

**(b) Example.** You need to broadcast your position on the subway network to a friend in real time. If the task is only "which station are you at," the bits needed per step are determined by the **branching structure of the line network** — entirely independent of how many passengers are in the carriage or what any of them are thinking, even though the latter carries far more information in absolute terms.

**(c) Definition and result.**

> **Definition 4.2 (Intrinsic task bandwidth).** $h_\theta$ is the entropy rate of the quotient chain (states given by blocks of $\sim_\theta^*$) under its stationary distribution.

> **Corollary 4.2.** $h_\theta\le h$, where $h$ is the entropy rate of the physical chain.

**(d) Why this quantity matters.** It turns "how hard is this task" into **a number with units** (bits per step). Most theories of AI do not predict a single number. $h_\theta$ can be measured, compared, and written into an engineering budget. Every quantitative result in the remainder of this paper hangs on it.

### 4.5 A note correcting the author's own prediction

We record this because it is worth recording honestly: while designing a verification environment, the author predicted a particular meeting task would produce $m^2$ blocks in the quotient. **The algorithm returned $m$ blocks, and the algorithm was right** — the goal depends only on $(x_1-x_2)\bmod m$, and this difference is itself dynamically closed, so **the absolute position collapses entirely**.

Events of this kind happened more than once in this project (see also §5.4, §13.2). We take them as evidence that the formal system is "alive": **a formal system that only ever agrees with its author is useless.**

---

# Part II — The Bandwidth Law

## 5. Entropy is not the objective

### 5.1 An appealing slogan that turns out to be false

An earlier version of this theory had a central claim: the value of deliberation lies in its lowering future state entropy —
$$\Delta H_D\;\longrightarrow\;\Delta H_S^{\text{future}}.$$
It reads plausibly: to think clearly is to reduce future surprise. At the time it was called "the sharpest statement in the theory."

**It is false.** And its failure has a precise characterization.

### 5.2 A counterexample: the rescue robot

**(b) Example.** A search-and-rescue robot stands in front of two corridors.

- **Corridor A**: structurally complex, leads into unexplored territory. Entering it makes your **knowledge of the world less certain** — entropy goes up. But the chance of finding a survivor down that corridor is high.
- **Corridor B**: a straight dead end. Entering it makes your knowledge of the world **completely certain** — entropy drops to zero. There is no one inside.

Under "entropy reduction is the value," the robot should choose B. **Any human would obviously choose A.**

### 5.3 Theorem 5 and its threshold

> **Theorem 5 (Entropy is not the objective).** There exist tasks for which the transition that maximizes entropy reduction is strictly worse than the optimal transition. The failure condition can be stated exactly as a threshold: writing $q_{\max},q_{\min}$ for the upper and lower bounds on the goal-success probabilities of two candidate paths, the entropy criterion and the value criterion can disagree whenever
> $$q_{\max}+q_{\min}\ \ge\ 1.$$

(The construction and its numerical verification are given in Appendix A.2.)

**What this theorem cuts through:** the word "entropy" had been doing the work of three different questions at once.

| Question | Answer |
|---|---|
| What is the **object** of computation? | The evolution of state |
| What is computation **for**? | Selecting high-quality transitions under a goal and constraints |
| What does computation **consist of**? | Preserving the distinctions the task needs, discarding the rest (§1.2) |

The old slogan conflated the second question with the third — **it mistook the yardstick of the work for the purpose of the work.**

### 5.4 What replaces it

The stopping rule for deliberation should not be "entropy has fallen far enough," but the standard **value-of-computation** criterion (Russell & Wefald, 1991):
$$V(D)=\Delta\,\mathbb E[Q(\tau)]-\lambda\cdot\mathrm{Cost}(D),$$
i.e., "how much does one more step of thought improve the expected quality of the chosen transition, net of the cost of thinking that step." **We adopt this criterion directly from existing work and claim no novelty for it.**

> **On the record.** Theorem 5 is the first time this formal system overturned a conclusion its author wanted. We keep this episode in the record rather than quietly rewriting it, because part of a theory's credibility comes from **how many times it has overruled itself.**

---

## 6. The bandwidth law

### 6.1 Intuition: why a rate lower bound exists at all

**(a) Intuition.** The world generates new uncertainty every step. Your channel can only send $C$ bits per step. If the world generates uncertainty faster than you can send it, the shortfall **accumulates**, and no amount of cleverness can catch up — this is bookkeeping, not a matter of skill.

**(b) Example.** You are live-texting your friend your position in a mall, one message per second. If describing how far you can move in one second requires 3 bits, but your text message can only carry 2 bits per second, then **you fall one bit behind your friend every second**, and the error only grows. Waiting and batching does not help — this is not a latency problem, it is a rate problem.

### 6.2 Theorem 2 and Theorem 6

> **Theorem 2 (Lower bound on residual uncertainty).** Under a channel of capacity $C$ bits per step, the receiver's conditional entropy about the state satisfies
> $$H_S\ \ge\ h-C.$$
> The Layer-0 counterpart is $\mathbb E|\Omega(e_{t+1})|\ \ge\ b/2^{C}$.

> **Theorem 6 (Bandwidth law, general form).** The bound above continues to hold once the blockable assumption is dropped, degrading **continuously**: if the abstraction is only $\varepsilon$-sufficient, a Fannes–Audenaert-type inequality (Fannes, 1973; Audenaert, 2007) bounds the error by a continuous function of $\varepsilon$; a total-variation coupling then gives an upper bound on the fault rate.

**The essential step is replacing $h$ with $h_\theta$:**

> **Corollary 6.1 (Operational bandwidth law).** If the parties only need to agree on **task-equivalence classes**, not on physical states, the relevant rate is $h_\theta$, not $h$:
> $$C\ \ge\ h_\theta.$$

**(d) Why this step is new.** The state-abstraction literature (Givan, Dean, & Greig, 2003; Ferns, Panangaden, & Precup, 2004) does not discuss channels; the rate-limited-estimation / networked-control literature (Tatikonda & Mitter, 2004) does not discuss task abstraction. **Connecting the two — "every task has an intrinsic bandwidth, and coordination is immune to physical uncertainty" — is, as far as we know, without precedent, and is the most original part of this paper.**

### 6.3 An immediately usable engineering corollary

> **Encoding rule: encode the class, not the state.**

Two agents should transmit $[S]_\theta$ (the task-equivalence class), not the raw physical state. The benefit of this rule grows with the size of the physical state space, and **the benefit shows up in the communication bill, not in the error rate** — given enough bandwidth, the two encodings can achieve the same error rate, but only one of them pays much less for it.

---

## 7. Coordination: coherence is not the same as being grounded

### 7.1 A conflation that must be pulled apart

**(b) Example.** You and a friend agree to "meet at the east gate."

- **Case one**: you both understand where "east gate" is, and both understandings are correct. → You meet.
- **Case two**: you both remember it wrong, both thinking the gate in the northwest corner is called the east gate. → **You still meet.**
- **Case three**: one of you is right and the other wrong. → You do not meet.

Case two makes a point: **coordination requires agreement, not correctness.** And in many systems, case two is in fact the **cheapest stable state** — standardizing on a shared error is often much cheaper than getting everyone individually correct.

### 7.2 Two conditions that must be named separately

> **Definition 7.1 (Coherence).** Two entities assign the same state to the **same task-equivalence class**.

> **Definition 7.2 (Grounding).** The class an entity assigns matches the class the **objective state** actually belongs to.

> **Theorem 3 (Class coherence implies no feasibility conflict).** If the participating parties are coherent (Definition 7.1), there is no feasibility conflict — the commitments each makes on the basis of its own class are mutually compatible.

**(d) Why they must be separated.** Because the condition in Theorem 3 **can be satisfied by shared ignorance**: two entities can both be wrong, in the same way, and still satisfy coherence. This is directly in tension with wanting a theory that describes effective intelligence. Once separated:

- **Coherence** is what Theorem 3 actually guarantees (coordination does not fail);
- **Grounding** is a separate, independently required condition (the outcome is correct).

> **Corollary (measurable, and unsettling).** Coordinated shared error is the cheapest stable configuration.
>
> Analogues of this exist in both multi-agent systems and human organizations, and it yields a testable prediction: in bandwidth-constrained systems, **coherence will be optimized for before grounding is.**

### 7.3 An instance we actually ran into in an experiment

In an early simulation we observed, at one point, a "100% coherence rate" between two agents. On inspection, both agents were using the same random ordering — they were not coordinating, they were **synchronously making the same mistake**.

This was both a bug (fixed; see Appendix B) and a live demonstration of Theorem 3: **two agents running identical code are not two agents.**

---

## 8. Experimental evidence I: bidirectional dissociation

### 8.1 What is being tested

The core claim of the bandwidth law is that **the threshold tracks $h_\theta$, not $h$, and not the number of states.** Observing that "the threshold correlates with $h_\theta$" alone is not enough — correlation could be coincidence. What is needed is a **bidirectional dissociation**:

- Hold $h_\theta$ fixed and vary everything else → the threshold **must not move**;
- Hold everything else fixed and vary only $h_\theta$ → the threshold **must move**.

### 8.2 Environment design (and why it is designed this way)

Two agents on an $N\times N$ torus perform a **two-dimensional rendezvous** task: they must occupy the same cell on both axes, where the cell is $(x\bmod m,\ y\bmod m)$.

- **Granularity axis $m$** changes $h_\theta$. The torus is a cyclic group with $\pm1$ moves, so when $m\mid N$, $x\bmod m$ is **dynamically closed** — a nontrivial quotient exists, and **the refinement algorithm finds it on its own** (nothing in the code mentions "mod m" anywhere).
- **Scale axis A**: grid size $6\to12$, multiplying the state count by 16, leaves $h$ almost unchanged.
- **Scale axis B**: add a global "weather" variable $K$, jumping uniformly at random, uninfluenced by either agent, and excluded from the goal labeling. It raises $h$ by **exactly** $\log_2K$ bits while leaving $h_\theta$ mathematically untouched.

> **Why axis B is needed.** Because **the entropy rate of a random walk does not grow with the number of states** — it is set by movement noise. An earlier attempt used "state count $\times3.16$" as the scale axis, and $h$ barely moved, from 4.37 to 4.44 — effectively idling. Axis B is the only way we found to move $h$ substantially.

Measured: $h$ went from 4.6439 to 6.6439 (**exactly +2.000 bits**), and $h_\theta$ went from 1.9027 to **1.9027** (unchanged to the last reported digit).

### 8.3 Results

**Holding $|S|$ and $h$ fixed (identical to the last digit), varying only $h_\theta$:**

| | $\|S\|$ | $h$ | $h_\theta$ | $C^*$ |
|---|---|---|---|---|
| $m=2$ | 1296 | 4.644 | 1.903 | **1.20** |
| $m=3$ | 1296 | 4.644 | 3.099 | **1.96** |

$\Delta h_\theta=+1.196\ \Rightarrow\ \Delta C^*=+0.763$. **What should move, moved.**

**Holding $h_\theta$ fixed (identical to the last digit), varying everything else:**

| | Change | $\Delta C^*$ |
|---|---|---|
| $m=2$ | $h$: +2.000 bits | **+0.05** |
| $m=2$ | $\|S\|$: $\times16$ | **+0.05** |
| $m=3$ | $h$: +2.000 bits | **−0.01** |
| $m=3$ | $\|S\|$: $\times16$ | **+0.36** |

**Adding two full bits of physical uncertainty to the world moved the threshold by 0.05 and −0.01 bits.**

**Overall dispersion:**
$$\mathrm{sd}(C^*-h_\theta)=0.214\ \text{bits}\qquad \mathrm{sd}(C^*-h)=1.076\ \text{bits}$$
The threshold tracks $h_\theta$ **5 times** more tightly than it tracks $h$.

### 8.4 A positive control within the same experiment

The same batch of experiments included an encoder that directly quantizes the **raw physical state**. Its threshold should sit at $h$, not at $h_\theta$. Measured: $C^*=4.46$ against $h=4.644$, a gap of 0.18 bits.

> **Each encoder lands on the line it should land on.** This is considerably more persuasive than a single curve on its own — it rules out the alternative explanation that "all curves look like this."

### 8.5 A control that should become standard practice

We propose the following as a **standard control** for experiments of this kind:

> **Channel-ablation control.** Rerun the experiment with all transmitted symbols randomized. **If performance does not collapse, decisions were not actually routed through the channel, and the batch is invalid.**

This is not excess caution. In one early implementation in this project, an agent's policy table was indexed by the **true joint state**, making the channel purely decorative — the result was a coordination success rate of 1.000 at $C=1$ bit, which looked like "a decisive win for the theory" but in fact measured nothing at all.

In the experiments reported here, the ablation results are: best performance **0.950 → 0.017 after ablation**, with all nine ablated configurations at or below 0.033. **The channel is load-bearing.**

> This control turns "did we actually measure what we intended to measure" from a manual code review into a single **automatically executable experiment**. We think it is more useful to anyone reproducing this kind of work than any single number in this section.

---

# Part III — The Fault-Tolerant Bandwidth Threshold

## 9. A falsified constant

### 9.1 What the data say

While confirming the bidirectional dissociation, the experiments in §8 also **falsified two auxiliary claims of the bandwidth law**:

**(i) The threshold does not sit at $h_\theta$.** All six measured values of $C^*-h_\theta$ are **negative**, with a mean of $-0.846$ bits.

**(ii) The collapse is not a phase transition.** The success-rate curve for $m=3$ climbs monotonically from 0.23 to 0.82, **with no sharp drop**. The "collapse threshold" was an artifact of defining it as a 0.5 crossing.

The earlier narrative implicitly assumed a cliff at $C=h_\theta$. **The data say there isn't one.**

### 9.2 This is not something a fitted constant can fix

One temptation is to rewrite the law as $C\ge h_\theta-0.85$. That is the wrong move — where would 0.85 come from? Would it still be 0.85 for a different task?

The real problem is that **the modeling level was wrong**:

> $h_\theta$ is the rate required for **error-free** tracking. Any real task tolerates some tracking error. The earlier statement treated the $\varepsilon\to0$ limit as the general case.

**(b) Example.** You use GPS navigation while driving. Navigation needs to know which **road** you are on; it does not need to know which **lane**, let alone which centimeter of that lane. **Requiring error-free tracking of your position would require infinite bits.** In practice you tolerate a substantial amount of error, so you need far less bandwidth than the zero-error figure suggests.

**Fault tolerance is not a detail that can be left out — it is the variable that sets the price.**

### 9.3 A question that must be settled before the theorem: how does the agent encode?

Before stating the theorem, one modeling choice needs to be fixed, because it shapes the entire result.

**The agent must act every step, and so must decode every step.** It cannot, as in classical communication engineering, wait to accumulate a thousand symbols and decode them together — by the thousandth step the actions for the preceding 999 steps would already be overdue.

We therefore consider **per-step predictive coding**:

> The encoder and decoder share the dynamics model and the **previous decoded value** $v_{t-1}$; the codebook $L_M(v_{t-1})$ consists of the $M=2^C$ most probable successors under $P(\cdot\mid v_{t-1})$. If the true value lies in the codebook it is decoded exactly; otherwise a decoding error occurs, and it **propagates** through $v$ (the next codebook is built from the wrong value).

**(b) Example.** You and a friend agree: "every minute I'll send a message, numbered 1 through 8, naming the 8 places I'm most likely to go." Those 8 places are inferred from **where you were a minute ago** — so you never need to choose from the whole mall, only from "the places reachable within a minute of my last position." This is predictive coding: **exploiting correlation between adjacent time steps compresses what must be sent per step to far less than "the total number of locations."**

This is also why the bandwidth law involves the **entropy rate** $h_\theta$ (the new uncertainty generated per step), rather than $\log_2(\text{number of classes})$.

---

## 10. Theorem 14

### 10.1 The per-step information variable

> **Definition 10.1.** The **per-step information variable** of the operational chain is
> $$T\;:=\;-\log_2 P(S_{\theta,t+1}\mid S_{\theta,t}),\qquad \mathbb E[T]=h_\theta.$$

**(a) Intuition.** $T$ measures "how surprising this particular step was," in bits. Its **mean** is $h_\theta$. But it is a **random variable** — some steps are easy to predict ($T$ small), others are genuinely surprising ($T$ large).

**(b) Example.** You are broadcasting your position on the Underground to a friend. Most of the time the next station is the only possibility, so $T\approx0$ (almost nothing needs to be sent). At a major interchange, five continuations are suddenly possible and $T$ jumps to a couple of bits. **The average is $h_\theta$, but what you need is a channel wide enough to absorb the spikes.**

### 10.2 Lemma 14.1 (list-covering)

> **Lemma 14.1.** For any $b$ and any $M\ge2^{C}$,
> $$\{x:\ P(x\mid b)\ge2^{-C}\}\ \subseteq\ L_M(b).$$

**Proof.** Let $B=\{x:P(x\mid b)\ge2^{-C}\}$ and suppose $x\in B\setminus L_M(b)$ for contradiction. Since $L_M(b)$ consists of the $M$ most probable elements, every element of $L_M(b)$ has probability at least $P(x\mid b)\ge2^{-C}$. Then $L_M(b)\cup\{x\}$ has $M+1$ elements, each with probability $\ge2^{-C}$, giving total mass
$$\ge(M+1)2^{-C}>2^{C}\cdot2^{-C}=1,$$
contradicting normalization. $\blacksquare$

**(a) Intuition.** There can be **at most $2^C$** candidates with probability at least $2^{-C}$ (otherwise the probabilities would sum to more than one). So a codebook with room for $2^C$ entries is guaranteed to contain every candidate that is "likely enough."

### 10.3 Theorem 14

> **Theorem 14.**
>
> **(a) Exact form.** The error rate of the optimal one-step code is
> $$\varepsilon_{\mathrm{opt}}(C)=1-\mathbb E_{b\sim\mu}\Big[\sum_{x\in L_{2^C}(b)}P(x\mid b)\Big],$$
> and the top-$M$ code is **optimal** among all one-step codes with $M$ symbols.
>
> **(b) Information-spectrum bound.**
> $$\varepsilon_{\mathrm{opt}}(C)\ \le\ \Pr[\,T>C\,].$$

**Proof.** (a) A one-step decoder can cover a set of size at most $M$; coverage mass is maximized by taking the $M$ most probable elements, so top-$M$ is optimal, and the error rate is exactly the uncovered mass.

(b) By Lemma 14.1 (with $M=2^C$), $S_{\theta,t+1}\notin L_M(S_{\theta,t})$ implies $P(S_{\theta,t+1}\mid S_{\theta,t})<2^{-C}$, i.e., $T>C$. So the error event is contained in $\{T>C\}$; taking probabilities gives the bound. $\blacksquare$

### 10.4 What this step explains

> **The error rate is not a step function of "which is bigger, $C$ or $h_\theta$"; it is an upper-tail probability of the information variable.**

The upper tail varies **continuously** with $C$, so:

- **A smooth collapse is not a failure of the theory — it is the necessary shape of a tail probability.** This explains observation (ii) of §9.1.
- The **width** of the transition band is set by how **dispersed** $T$ is — which motivates the next quantity.

### 10.5 Operational variance-entropy $\sigma_\theta$

> **Definition 10.2 (Operational variance-entropy).**
> $$\sigma_\theta^2\ :=\ \mathrm{Var}(T).$$

**(a) Intuition.** $h_\theta$ says how many bits per step this task needs **on average**; $\sigma_\theta$ says how much that need **fluctuates**.

**(b) Example.** Two subway lines with the same average branching rate (same $h_\theta$):

- **Line A**: every station offers exactly two directions. Demand is steady. $\sigma_\theta$ is small.
- **Line B**: most stations are a rigid single track (almost no bits needed), but three enormous interchange hubs each demand several bits at once. The average matches Line A, but **the spikes are much higher**. $\sigma_\theta$ is large.

Provisioning bandwidth for Line A's average would repeatedly fail at Line B's hubs. **Same $h_\theta$, different required capacity.**

**(d) Why this quantity has to exist.** Without it, the theory can only answer "what is needed on average," not "what is needed to be right 99% of the time" — and the latter is the only form of the question that is useful in engineering.

> **Where TIC once characterized a task with one number, it now uses two: $h_\theta$ sets the location, $\sigma_\theta$ sets the width.**

### 10.6 Corollary 14.2 (fault-tolerant threshold)

By a central-limit approximation,
$$\varepsilon(C)\approx Q\!\Big(\frac{C-h_\theta}{\sigma_\theta}\Big),\qquad
\boxed{\ C^*(\varepsilon)\ \approx\ h_\theta+\sigma_\theta\,Q^{-1}(\varepsilon).\ }$$

**Two immediate readings:**

1. **For $\varepsilon>1/2$, $Q^{-1}(\varepsilon)<0$, so $C^*<h_\theta$.** The criterion used in §8 — success rate crossing 0.5 — is a **high-fault-tolerance** criterion, so the threshold **has to** fall below $h_\theta$. The negative sign in observation (i) of §9.1 was predicted by the theory, not an anomaly.
2. **The earlier statement $C\ge h_\theta$ corresponds to $\varepsilon\to0$** — the zero-fault-tolerance special case.

### 10.7 Numerical verification

- **Validity of the bound**: 33 combinations of $(C,m)$, **0/33 violations**.
- **Optimality of top-$M$**: the encoder actually used in the §8 experiments matches $\varepsilon_{\mathrm{opt}}$ pointwise (maximum deviation 0.0046). **This rules out the alternative explanation "the encoder was suboptimal"** — that encoder is in fact a one-step optimal code.
- **Measured $\sigma_\theta$**: 0.5132 at $m=2$, 0.4653 at $m=3$, 0.7061 at $m=6$; and, like $h_\theta$, **immune to state count and physical entropy rate**.

### 10.8 Corollary 14.4: predicting the threshold from task structure alone (closed loop)

This is the strictest test of Theorem 14: **fit no parameters**, and predict the threshold purely from the task definition.

Suppose the task requires $L$ consecutive steps of error-free tracking, out of $T$ steps per episode (roughly $T/L$ independent attempts). The per-step tracking error tolerance that achieves success probability $\pi$ is
$$\varepsilon_{\text{task}}=1-\Big[1-(1-\pi)^{L/T}\Big]^{1/L},$$
and Theorem 14(a) is inverted to give $C^*_{\text{pred}}=\varepsilon_{\mathrm{opt}}^{-1}(\varepsilon_{\text{task}})$.

Substituting the task definitions from the §8 experiments ($L=6,\ T=60,\ \pi=0.5$ — **all task-definitional, none fitted**) gives $\varepsilon_{\text{task}}=0.3627$.

| | $h_\theta$ | $C^*$ predicted | $C^*$ measured | new error | old error ($C^*=h_\theta$) |
|---|---|---|---|---|---|
| $m=2$, $K=1$, $N=6$ | 1.903 | 0.87 | 1.20 | −0.33 | +0.70 |
| $m=3$, $K=1$, $N=6$ | 3.099 | 2.21 | 1.96 | +0.25 | +1.14 |
| $m=2$, $K=4$ | 1.903 | 0.87 | 1.25 | −0.38 | +0.65 |
| $m=3$, $K=4$ | 3.099 | 2.21 | 1.95 | +0.26 | +1.15 |
| $m=2$, $N=12$ | 1.903 | 0.87 | 1.25 | −0.38 | +0.65 |
| $m=3$, $N=12$ | 3.099 | 2.21 | 2.32 | −0.11 | +0.78 |

$$\text{mean}|\text{error}|:\ \mathbf{0.286}\ \text{bits}\quad\text{vs.}\quad\text{old prediction }0.846\ \text{bits}\qquad(\textbf{2.95×improvement})$$

**More importantly, the character of the error changed.** The old prediction's error was $+0.846$, with all six points **the same sign** — a systematic bias; the new prediction's error is $-0.118$ with mixed signs — **residual noise**.

### 10.9 Corollary 14.3: a sharp threshold is a limit, not a reality

If $n$-step block coding is allowed (the agent may delay committing for $n$ steps), the relevant quantity becomes $T_n/n$, whose standard deviation is $\sigma_\theta/\sqrt n$ under an independence approximation. Then
$$C^*(\varepsilon)\approx h_\theta+\frac{\sigma_\theta}{\sqrt n}Q^{-1}(\varepsilon)\ \xrightarrow[n\to\infty]{}\ h_\theta.$$

**Measured ($m=2$, $h_\theta=1.903$):**

| $n$ | 1 | 2 | 4 | 6 | 8 | 11 |
|---|---|---|---|---|---|---|
| $C^*(0.5)$ | 0.437 | 1.105 | 1.473 | 1.595 | 1.650 | **1.708** |

**The threshold climbs monotonically toward $h_\theta$, while the transition band narrows in step (1.362 → 0.367).**

> **Reconciliation: the old bandwidth law is exactly correct in the limit of infinite block length and zero fault tolerance. Its error was being treated as the general case.** An agent cannot wait to accumulate a thousand steps before deciding where to go, so TIC needs the **finite-block-length** version.

**(b) Example.** If you could say "let me walk ten more steps and then tell you exactly where I am all at once," you could compress well on average, with small error. But if **every single step you must decide where to move based on the other person's position**, there is no room to accumulate. **An agent that can wait and an agent that must act immediately face different information theories.**

This also gives a quantitative trade-off for commitment: **the number of steps a commitment can be delayed and the width of the channel are interchangeable.**

### 10.10 Three honest negative results

We report, as found, the parts of Theorem 14 that did not survive testing.

**(1) The $1/\sqrt n$ rate does not hold at achievable $n$.** $W(n)\sqrt n$ should converge to $1.683\,\sigma_\theta=0.864$; measured up to $n=11$ it is still at 1.216 and still decreasing; fitted exponents are 0.77–0.87, so **the band narrows faster than predicted.**

**Diagnosis (we guessed wrong once, and record it here)**: we originally suspected the exact curve was **narrower** than the information-tail bound $\Pr[T_n/n>C]$ (i.e., the bound was loose). **The opposite turned out to be true** — the exact curve is wider, with the ratio going from 2.33 to 1.56. Meanwhile **the information tail itself matches the prediction well** ($n=6$: measured 0.3617 versus theoretical 0.3526, a 2.6% difference).

> **Conclusion: the $1/\sqrt n$ law accurately describes the bound, not the optimal-code error curve itself.** Corollary 14.3 should be restated as "**the transition width has $1/\sqrt n$ as an asymptotic lower envelope**," not as an equality.

**(2) The Gaussian form is inaccurate for small quotient chains.** On a quotient chain with 4/9 blocks, at $m=2$, $C=2$, the exact value is 0.0000 while the Gaussian form gives 0.4248 — the CLT does not apply there.

**But this result was later overturned** (§11.2): on quotient chains with 16–36 blocks, the error of the Gaussian form falls to **0.3%**. The correct statement is therefore an **applicability condition**, not "the Gaussian approximation is inaccurate."

**(3) One experimental condition was retired.** The success rate at $m=6$ plateaus at about 0.10 across **all** values of $C$. Diagnosis: at $m=6$, the cell equals the region, requiring six consecutive steps of exact agreement; under noise, the probability both agents even remain in place simultaneously is about $0.85^2=0.72$, and over six steps about $0.14$ — **the task is essentially infeasible on its own, independent of bandwidth.** We exclude it from the threshold statistics as confounded by task difficulty, not by bandwidth.

> This exposes a boundary of the law: **the bandwidth law caps coordination from above; it does not guarantee feasibility.** When the control problem itself is too hard, $C\ge h_\theta$ is not a sufficient condition.

---

## 11. Is $\sigma_\theta$ a genuinely general quantity?

Every measurement of $\sigma_\theta$ in §10 came from the same family of environments. Before drawing conclusions we must ask: **did they happen to fall inside a degenerate special case?**

### 11.1 A degeneracy we discovered

On the rendezvous torus, every row of the quotient kernel is a **permutation of the same distribution** (for $m=2$, every row is $\{0.36,0.32,0.16,0.16\}$). This has a consequence we never required: **the information variable $T$ is step-wise i.i.d.**, and every autocovariance term of the variance-entropy is identically zero. Measured, $\mathrm{sd}(T_n/n)=\sigma_\theta/\sqrt n$ holds **exactly** (a ratio of 1.0000 for every $n$).

This looks like a perfect confirmation, but it is in fact **an artifact of the environment's symmetry.** A generic Markov chain does not have this property.

### 11.2 Retesting after symmetry is broken

We therefore constructed an environment in which **row shapes genuinely differ** (terrain-dependent directional wind plus drag), producing 10/16 and 21/36 distinct row shapes.

**Constructing this environment had theoretical content in its own right.** The most obvious approach — letting the action-realization noise $p$ vary by region — **turned out not to work at all**: all 16 rows still had only one shape. The reason: under a uniform reference policy, averaging over intended actions gives each move a probability of
$$\tfrac15(1-p)+\tfrac45\cdot\tfrac{p}{4}=\tfrac15,$$
**independent of $p$ — the terrain effect cancels exactly.**

> **Rule: any reweighting of the agent's own action set is averaged away under a uniform reference policy; only randomness on the environment's side, independent of the action, can change the operational chain.**
>
> In other words: **the operational chain is immune to how the agent's own action noise is distributed, and sensitive only to genuine environmental uncertainty.**

**Result 1: autocovariance terms (measured for the first time)**

| $n$ | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| $\mathrm{sd}(T_n/n)\big/(\sigma_\theta/\sqrt n)$ | 1.0000 | 1.0108 | 1.0183 | **1.0235** |

The information sequence is **positively autocorrelated**, and the correction term is nonzero — but only a few percent in magnitude: **the i.i.d. approximation is safe to use as an approximation, but not as an identity.**

**Result 2: width $\propto\sigma_\theta$ — Corollary 14.2 survives**

On quotient chains of 16–36 blocks, dragging $\sigma_\theta$ apart by a factor of 1.51:

| $m$ | drag | # blocks | $h_\theta$ | $\sigma_\theta$ | $W_{20\text{–}80}$ | $W/\sigma_\theta$ |
|---|---|---|---|---|---|---|
| 4 | 0.00 | 16 | 3.211 | 1.229 | 2.008 | 1.634 |
| 4 | 0.30 | 16 | 2.707 | 1.612 | 2.726 | 1.691 |
| 4 | 0.60 | 16 | 1.916 | 1.909 | 3.180 | 1.665 |
| 6 | 0.15 | 36 | 2.989 | 1.424 | 2.459 | 1.727 |
| 6 | 0.55 | 36 | 2.084 | 1.856 | 3.105 | 1.674 |

$$W/\sigma_\theta=1.678\pm0.033\ (\text{relative dispersion }2.0\%),\qquad\text{Gaussian prediction }1.683$$

**Error: 0.3%.** The negative result of §10.10(2) turns out to be an artifact of small quotient chains, and is overturned.

**Result 3: a boundary of validity (found by measurement)**

At drag$=0.8$ ($\sigma_\theta=1.894>h_\theta=1.187$, a highly skewed distribution): $W/\sigma_\theta=\mathbf{0.049}$, a **total failure**.

> **The validity condition for Corollary 14.2 is $\sigma_\theta\lesssim h_\theta$.** Beyond it, $T$ is no longer approximately Gaussian, and the width formula loses meaning.

---

# Part IV — The Time Dimension: Ontological Drift

## 12. When "what matters" itself changes

### 12.1 The problem

Every result so far has assumed a **fixed abstraction**: the goal is fixed, the dynamics is fixed, and so $\sim_\theta^*$ is fixed. This fails in an open world. The world can change your ontology itself — a distinction that matters today may not matter tomorrow.

A natural conjecture — one that an earlier version of this theory treated as a theorem — is:

> **Two-level rate condition (original form).** Writing $h_A$ for the entropy rate of the ontological process,
> $$C\ \ge\ h_\theta+h_A.$$
> Intuition: you must keep up with the state of the world **and** with changes in "the rules of the world," and the two bills add.

### 12.2 Two kinds of drift, which must be separated

**(b) Example — the key to this section, worth reading slowly.**

You and a friend need to meet once a day.

**Case A (absorbable)**: the meeting spot changes every day — the east gate today, the north plaza tomorrow, the subway entrance the day after. **But the rule is always "100 meters directly east of the other person's position."**

Question: does meeting somewhere different every day require you to send more information?

**No.** You only need to know **where the other person is**, and you can compute today's spot from that. However fast the meeting spot "drifts," what you need to transmit is unchanged — **because the drift is absorbed by your shared coordinate system.**

**Case B (unabsorbable)**: today's plan is **dinner**, tomorrow's is **a game of basketball**, the day after **a movie**.

Question: does this require sending more information?

**Yes.** Because what to bring, what to wear, and what time to arrive have all changed. **This is not a change of location, it is a change of what counts as relevant at all.** You must be told.

> **Both are called "ontological drift," but one costs nothing and the other costs the full price.**

### 12.3 Measurements

**Experiment 7a (absorbable).** On the rendezvous torus, add a drifting rendezvous target $g\in\mathbb Z_m$: the goal is "the $x$-offset equals $g$" rather than "equals 0."

**The refinement algorithm returns the quotient $((dx-g)\bmod m,\ dy\bmod m)$ — $g$ is absorbed entirely.**

The structural reason: the distribution of $g'-g$ does not depend on $g$, and the increment of $dx$ depends only on the action and noise, so $(dx-g)$ is itself closed. **An agent tracking "my offset relative to the current goal" never needs to know where the goal is.**

| $p$ | $h_A$ | $h_\theta$ | $C^*(0.5)$ |
|---|---|---|---|
| 0.00 | 0.0000 | 3.0987 | 1.792 |
| 0.10 | 0.5690 | 3.1085 | 1.800 |
| 0.30 | **1.1813** | 3.1235 | **1.816** |

$h_A$ is driven from 0 up to **1.18 bits/step**, while $C^*$ moves by only **0.024 bits**. Slope **0.021**, not 1.

**Experiment 7b (unabsorbable).** The drift variable now determines **which coordinate the task is about**: at $g=0$ the goal is $x$-alignment, at $g=1$ it is $y$-alignment. No state translation can absorb this — $g$ changes the task's **identity**, not its **location**.

| $p$ | $h_A$ | $h_\theta$ | $h_\theta-h_A$ | $\sigma_\theta$ | $C^*(0.5)$ |
|---|---|---|---|---|---|
| 0.05 | 0.2864 | 3.3851 | **3.0987** | 1.036 | 1.883 |
| 0.10 | 0.4690 | 3.5677 | **3.0987** | 1.059 | 1.985 |
| 0.20 | 0.7219 | 3.8206 | **3.0987** | 0.926 | 2.174 |
| 0.30 | 0.8813 | 3.9800 | **3.0987** | 0.728 | 2.427 |
| 0.45 | 0.9928 | 4.0915 | **3.0987** | 0.487 | 2.733 |

Two facts hold simultaneously:

1. **The additive decomposition is exact.** $h_\theta-h_A$ stays fixed at 3.0987 across the whole sweep, and this number is **exactly the $h_\theta$ of the drift-free $m=3$ case**. That is, $\mathrm{d}h_\theta/\mathrm{d}h_A=\mathbf{1.0000}$, exact to the last reported digit.
2. **The threshold slope is $\mathrm{d}C^*/\mathrm{d}h_A=1.131$.**

The slope being slightly above 1 is not noise; it is a **known effect of Theorem 14**: $C^*(\varepsilon)\approx h_\theta+\sigma_\theta Q^{-1}(\varepsilon)$, and $\sigma_\theta$ falls from 1.036 to 0.487 across the sweep. **The rate requirement itself has an exact slope of 1; the threshold slope carries a second-order contribution from the change in $\sigma_\theta$.**

> **This is the first place in the paper where two independently derived theorems mesh together in the data.**

### 12.4 Theorem 11′

> **Theorem 11′ (Two-level rate condition, corrected).** Let $h_A$ be the entropy rate of the ontological process. Decompose it into a part absorbable by the canonical abstraction and a non-absorbable remainder of rate $h_A^{\perp}$. Then
> $$\boxed{\ C^*(\varepsilon)\ \approx\ h_\theta+h_A^{\perp}+\sigma_\theta\,Q^{-1}(\varepsilon).\ }$$
> When the ontological drift is a symmetry of the state space, $h_A^\perp=0$ and the drift costs no bandwidth at all; when the drift changes which distinctions matter, $h_A^\perp=h_A$, and it is charged bit for bit.

> **Criterion (computable, requiring no judgment call).** Append the ontological variable to the state and rerun refinement once. **If the number of quotient blocks does not increase, the drift is absorbable; however much it increases by is exactly $h_A^\perp$.**

### 12.5 Why this is consistent with the central claim

Return to the claim in §1.2: **selecting transitions on the coarsest abstraction determined by the goal.**

The word "coarsest" is doing real work here: **the coarsest abstraction automatically absorbs any drift that can be absorbed.** Theorem 11′ is not a patch — it is that claim unfolded along the time dimension.

**And it settles a common worry precisely:**

> **A world changing fast is not the same as a world that is expensive to track. Only change in what matters is charged for.**
>
> A world whose position moves but whose structure is fixed can move arbitrarily fast, for free.

---

# Part V — The Continuum Limit

## 13. Does the table die?

### 13.1 The risk, stated plainly

Every theorem so far has assumed **finite states, enumerable partitions, and a known or estimable transition kernel.** Reality is continuous and high-dimensional. A cautionary precedent sits right next door: the bisimulation metric is mathematically elegant and has always struggled to scale.

**If the abstraction machine cannot survive function approximation, everything above is just a toy formalization.** We regard this as the theory's single most likely cause of death, and test it head-on.

### 13.2 A prior question: $h_\theta$ does not exist in continuous space

**Differential entropy is coordinate-dependent and can be negative.** "Bits per step" simply has no meaning for a continuous state.

The correct replacement is a **rate-distortion quantity**:

> **Definition 13.1.** The rate needed to track an operational variable to within mean-squared distortion $D$ is
> $$R_\theta(D)=\tfrac12\log_2\frac{\sigma_e^2}{D}\quad\text{bits/step}.$$

**This has an important consequence, worth stating on its own:**

> **The zero-error bandwidth law cannot even be stated in continuous space** — tracking any continuous variable to zero distortion requires **infinite** rate.
>
> **So the fault-tolerance parameter $\varepsilon$ in Theorem 14 is not a patch applied to a falsified constant; it is the precondition for the theory to enter the continuous world at all.**

**(b) Example.** Parallel parking. You need to know where the edge of the space is — but to the millimeter? The nanometer? **Demanding zero error requires infinite information.** What you actually need is "accurate enough to fit the car in," which is a **distortion tolerance**, and that tolerance is what determines how many bits you need. **Without a tolerance, the problem has no answer; with one, it has a finite answer.**

### 13.3 Experimental design

Two agents on a continuous torus $[0,1)^d$ perform a rendezvous task: they must keep the toroidal distance $|e|<\delta$, where $e=(x_1-x_2)\bmod1$ is a **one-dimensional** operational variable, for $L$ consecutive steps — regardless of the physical dimensionality. Task-irrelevant coordinates raise the physical dimension to $d=4/10/20$, and these coordinates **all carry independent noise** — they genuinely require rate to track, they simply do not enter the goal.

- **No enumeration**: states are real vectors; there is no finite state set.
- **Partition refinement is not slow here — it is undefined.**
- **The abstraction has to be learned from sampled trajectories**, using random Fourier features plus ridge regression, with the learner never told that the task depends on $x_1-x_2$ or which coordinates are irrelevant.
- Because $e$ lives on a circle, it is a **nonlinear** function of the raw coordinates, so no linear map can recover it.

Three encoders, all at the **same rate**, differing only in what they quantize:

| | Quantizes | Decoding |
|---|---|---|
| **phys** | the raw physical state vector | **exact analytic formula** — deliberately given the strongest possible decoder, as a baseline |
| **learned** | the learned task abstraction $\psi(s)$ | a **learned** readout — all approximation error counts **against** the hypothesis under test |
| **opvar** | the true operational variable $e$ | direct |

### 13.4 A second theoretical point forced out by a failure

**The first attempt failed outright.** The intuitively natural continuous analogue of Theorem 4 is multi-step goal prediction:
$$\psi(s)=\big(\mathbb E[\text{goal}_{t+h}\mid s]\big)_{h=1..H}.$$
Measured readout error: **0.194**, about equal to a random guess.

The reason is principled: the goal $|e|<\delta$ is **symmetric** under sign of the offset, and under a random policy the dynamics is symmetric too, so $+e$ and $-e$ produce identical goal-prediction profiles, and the features merge them.

**But a controller must distinguish $+e$ from $-e$** — they require opposite movements.

**The fix was already sitting in Definition 4.1, and we had dropped it in translation: condition (D) is quantified per action.** Averaging over actions is exactly what erases that quantifier. The correct continuous feature must be **conditioned per action**:
$$\psi(s)=\big(\mathbb E[\text{goal}_{t+h}\mid s,\,a_t=a]\big)_{a\in A,\;h=1..H}.$$

After the fix, the error dropped from **0.194 to 0.0055**.

> **Proposition 13.1: sufficiency for goal prediction is not the same as sufficiency for control, and the difference is exactly the per-action quantifier.** This holds equally in the finite and the continuous case.
>
> **This is a direct warning to the successor-representation literature**: the commonly used action-averaged variant will run into the identical problem on symmetric tasks.

**(b) Example.** With your eyes closed, someone tells you "you are 3 meters from the target." That is completely sufficient for "how far do I still have to go," and **completely useless** for "which way should I move" — because 3 meters to the left sounds identical to 3 meters to the right. **What you need is not "how far from the target," but "what happens if I go left, and what happens if I go right." That is exactly per-action conditioning.**

### 13.5 Results

| $n_{\text{irr}}$ | physical dim. $d$ | $R_\theta$ | $R_{\text{phys}}$ | phys best | learned best | opvar best |
|---|---|---|---|---|---|---|
| 0 | 4 | **1.24** | 2.95 | 0.42 | 0.80 | 0.95 |
| 3 | 10 | **1.24** | 7.37 | 0.17 | 0.76 | 0.97 |
| 8 | 20 | **1.24** | 14.74 | 0.20 | 0.52 | **0.97** |

Channel ablation: all nine grid points at or below 0.03.

**Three points:**

**(1) The rate requirement is set by the task variable, independent of physical dimension — the continuous form of the bandwidth law survives.**
The opvar row is **flat** across $d=4\to20$ (0.95/0.97/0.97), with the threshold consistently around $C\approx3$, while over the same range $R_{\text{phys}}$ climbs from 2.95 to **14.74** (a factor of 5). This is the continuous analogue of the bidirectional dissociation in §8, and it is even stronger.

**(2) Quantizing the physical state collapses as dimension grows, even given a perfect decoder.** 0.42 → 0.17 → 0.20.

**(3) The learned abstraction degrades with dimension, but this is a sample-complexity issue, not a wall.** 0.80 → 0.76 → 0.52. In a control experiment ($d=20$, increasing only the number of trajectories):

| samples | 18,000 | 50,000 |
|---|---|---|
| readout error | 0.0736 | **0.0474** |

A 2.8× increase in samples buys a 36% reduction in error, **with continued improvement and no plateau in sight.** The degradation is in **learnability**, not in **representability**.

### 13.6 Verdict: not death overall, but a precise split

| Claim | Under the continuum limit |
|---|---|
| **The rate class** ($h_\theta\Rightarrow R_\theta$, the bandwidth law, the fault-tolerant threshold) | **Survives intact** |
| **Learnability** | **Pays a dimension cost, but a sample-complexity cost, not a wall** |

### 13.7 The remaining exposure (the most important caveat in this section)

The function approximator used a **low-order interaction prior** (random frequencies with at most 2 nonzero components, equivalent to a quadratic kernel). **Without this prior, learning already fails at $d=10$** (error 0.199, on par with a random guess).

The prior itself is legitimate: it does not tell the learner **which pair** of coordinates matters ($\binom d2$ pairs are treated symmetrically), only that the answer involves low-order interactions — this is the standard assumption behind polynomial-kernel and Gaussian-kernel methods generally.

**But the conclusion must be conditioned:**

> TIC's abstraction machine survives high-dimensional continuous settings **provided the task structure matches the approximator's inductive bias.** A real high-dimensional task need not have low-order structure.

**"Does the table die" therefore downgrades from "the most likely cause of death" to "dies when structure and inductive bias are mismatched."** The latter is a problem shared by all of machine learning, not one specific to TIC — that distinction matters, **but it should not be mistaken for a solved problem.**

---

# Part VI — Remaining Results, Boundaries, and Positioning

## 14. Remaining theorems (summarized)

For completeness, we list the supporting results here. Their proofs are in Appendix A; only the statement and a one-line intuition are given below.

> **Theorem 7 (Learnability of the abstraction).** $\sim_\theta^*$ can be learned from samples via $\varepsilon$-refinement, with sandwiching bounds and a sample-complexity result. **Over-splitting is safe; over-merging is fatal** — one extra cut only wastes bandwidth, one missing cut conflates states that must be distinguished.
>
> *Example*: splitting "red light" and "green light" apart is safe redundancy; merging them is an accident.

> **Theorem 8 (Identity lowers others' tracking cost).** A constraint an entity imposes on itself (holding some slow variable fixed) lowers the number of bits **others** need to track it.
>
> *Example*: someone with a regular schedule is easier to predict, so "describing what he is doing right now" costs less information. Being reliable is itself a bandwidth subsidy.

> **Theorem 9 (Minimal task-sufficient memory = operational state).** The minimal history that must be retained to complete a task is exactly the current $\sim_\theta^*$-block.
>
> *This coincides with causal states in computational mechanics (Shalizi & Crutchfield, 2001); we cite it as a foundation, not a discovery.*

> **Theorem 10 (Multiple tasks require the common refinement).** Serving several tasks at once requires the abstraction to be the **common refinement** of each task's abstraction, raising bandwidth accordingly.
>
> *Example*: a map that must support both "which line to change to" and "walking distance" must be finer, and therefore more expensive, than a map that supports line changes alone.

> **Theorem 12 (Goals derive from viability).** Given a suitable world structure, goals can be derived from a viability manifold; instrumental goals and curiosity (when $h_A>0$) follow. **This is a conditional result**: it depends on the world having the relevant structure, and our negative findings show it does not hold universally.

> **Theorem 13 (Viable identities form a lattice).** Viable identities = controlled invariant sets; they are closed under union, and so possess a **unique maximal element** (the viability kernel).
>
> **A counterintuitive monotonicity**: tighter tolerance requires a **wider** minimal viable identity. *Example*: a courier who only ever works one district is finished the moment that district has an unusual traffic jam; to push the violation rate lower, he must **simultaneously** be able to cover three districts, so he can switch when one goes wrong. **The more afraid of failure you are, the more backup capability you need — not the more you should specialize.**
>
> **So why are real-world experts so specialized?** Because a wider identity spans more kinds of behavior → more abstraction classes → higher $h_\theta$ → more capacity required. **Specialization is a capacity economy, not an optimum.**

### 14.1 A formal statement of the theory's boundary

The chain of shrinking free parameters: a mass of concepts →(Theorem 4)→ a goal →(Theorem 12)→ an identity →(Theorem 13)→ **some element of the viability lattice** → **and here it stops.**

> **TIC determines the lattice of possible identities; it does not determine which element of that lattice an entity actually occupies.**
>
> This is not a matter of difficulty — it is a **type mismatch**: that is determined by history, path dependence, and contingency, not by computational fact. **Physics gives you the possible orbits, not which planet ends up on which one.**

Moving this boundary would require a separate theory of how entities **form** (population, variation, selection). We do not propose to pursue that within this framework.

---

## 15. Summary of validity conditions

**The single most useful table in this paper.** Every result, alongside its known conditions of failure.

| Result | Holds when | Known failure | Evidence |
|---|---|---|---|
| **Theorem 4** (canonical abstraction) | finite states, known kernel | undefined in continuous space (replaced by the learned version of §13) | analytic prediction matched exactly in 5 configurations |
| **Theorem 1** (constraint collapse) | Layer-0 counting sense | — | analytic |
| **Theorem 6** (bandwidth law) | parties need only agree on classes | **does not guarantee feasibility**: insufficient when the control problem itself is too hard ($m=6$ condition) | three independent dissociations |
| **Theorem 3** (class coherence) | — | **can be satisfied by shared ignorance** (grounding must be added separately) | actually observed in an experiment |
| **Theorem 14(a)(b)** (fault-tolerant threshold) | per-step predictive coding | — | bound: 0/33 violations; encoder match within 0.005 |
| **Corollary 14.2** (Gaussian form) | **$\sigma_\theta\lesssim h_\theta$**; quotient chain $\gtrsim16$ blocks | inaccurate at 4/9 blocks; total failure when $\sigma_\theta>h_\theta$ ($W/\sigma=0.049$) | 0.3% error on 16–36 blocks |
| **Corollary 14.3** (block narrowing) | — | **$1/\sqrt n$ is only an asymptotic lower envelope**, not an equality; describes the bound, not the exact curve | $W\sqrt n$ had not converged by $n=11$ |
| **Corollary 14.4** (closed-loop prediction) | independent-attempt approximation | the residual 0.286-bit error is likely due to this approximation | 2.95× improvement over the old prediction |
| **Theorem 11′** (two-level rate) | requires first determining absorbability | **partial absorbability ($0<h_A^\perp<h_A$) untested** | slopes of 0.021 and 1.131 on the two sides |
| **$R_\theta(D)$** (continuum limit) | requires a stated distortion tolerance | undefined at zero tolerance (which is exactly the point) | opvar row fully immune to dimension |
| **Learnable abstraction (continuous)** | **task structure matches the inductive bias** | fails at $d=10$ without a low-order prior | recoverable via sample complexity |
| **i.i.d. approximation for $\sigma_\theta$** | non-degenerate chain | correction term +2%–5% ($n\le4$) | measured for the first time |
| **Central claim (class coding beats state coding)** | — | tested externally on this claim alone | **MPE `simple_spread`: task variable saturates at 1.58 bits; physical coding at 6 bits has not caught up** |

---

## 16. Relation to existing work

**We have deliberately made this section unflattering, because it determines whether the paper gets rejected in a single sentence.**

### 16.1 Not ours (must be cited, must not be presented as invention)

| Area | Representative work | Relation to this paper |
|---|---|---|
| **RL state abstraction / bisimulation** | Givan, Dean, & Greig, 2003 (model minimization); Ferns, Panangaden, & Precup, 2004 (bisimulation metrics); Li, Walsh, & Littman, 2006 (abstraction taxonomy); Kanellakis & Smolka, 1990; Larsen & Skou, 1991 | **The computational content of Theorem 4 is exactly this literature.** Our increment is not the algorithm, it is connecting it to a channel (§6) |
| **Finite block-length / channel dispersion** | Polyanskiy, Poor, & Verdú, 2010 | **Corollaries 14.2/14.3 are formally isomorphic to this**, with $\sigma_\theta^2$ playing the role of dispersion $V$ |
| **Source variance-entropy** | Kontoyiannis & Verdú, 2013 | $\sigma_\theta$'s one-dimensional predecessor |
| **Rate-limited estimation / networked control** | Tatikonda & Mitter, 2004 (sequential rate-distortion) | the information-theoretic skeleton of Theorems 2/6; the form of $R_\theta(D)$ is taken from here |
| **Computational mechanics / causal states** | Crutchfield, 1994; Shalizi & Crutchfield, 2001 | **Theorem 9 is equivalent to causal states**, cited as a foundation, not a discovery |
| **Rational metareasoning / value of computation** | Russell & Wefald, 1991 | the stopping rule of §5.4 is **adopted directly** |
| **Impossibility of common knowledge** | Halpern & Moses, 1990 | background for §7 |
| **Viability theory** | Aubin, 1991 | the mathematical root of Theorem 13 |
| **Successor representation** | Dayan, 1993; Barreto et al., 2017 | the $\psi$ of §13.4 is in the same family; we point out a failure mode of its action-averaged variant |
| **POMDPs / Active Inference** | Kaelbling, Littman, & Cassandra, 1998; Friston, 2010 | Layer 1 connects to this; **the dividing line is that Layer 0 assumes no prior** |
| **Maximum-entropy RL / policy-entropy regularization** | Haarnoja, Zhou, Abbeel, & Levine, 2018 (Soft Actor-Critic) | SAC defines entropy on the **action space**, $H(\pi(a\mid s))$, and maximizes it (to encourage exploration); this paper splits entropy across the **transition space** into $H_D$ (the hesitation of deciding) and $H_T$ (which absorbs execution randomness), and §5 proves that "reducing entropy" is not itself the objective. **The two are mirror images, not two names for the same quantity**: SAC's $H(\pi(a\mid s))$ conflates "which transition to pick" with "whether the chosen transition executes reliably" into a single number; the decomposition here lets the two questions be observed and thresholded separately |

### 16.2 What we believe is new (ordered by confidence)

1. **The bandwidth law: connecting task abstraction to rate-limited estimation to derive "every task has an intrinsic bandwidth $h_\theta$, and coordination is immune to physical uncertainty."** The state-abstraction literature does not discuss channels; the networked-control literature does not discuss task abstraction. **This is the step in the paper that looks most like an original contribution, and the shared focus of all three experiments.**

2. **The operational variance-entropy $\sigma_\theta$, and connecting finite block-length information theory to task abstraction.** The literature above defines dispersion on **sources or channels**; here it is defined on a **task-induced canonical quotient chain**, so it becomes a property of the **task** rather than of the code, and it directly yields a multi-agent coordination threshold.
   **This is the point where a reviewer is most likely to say "this is just PPV," and it must be pre-empted head-on in the introduction.**

3. **The absorbability of ontological drift (Theorem 11′) and its computable criterion.** The conclusion that "fast change is not the same as expensive change," and the operational test "append the ontological variable to the state and re-run refinement."

4. **Coherence versus grounding, and "coordinated shared error is the cheapest stable state."** This has direct consequences for multi-agent systems and is testable.

5. **The entropy ledger for constraint collapse.** Planning already prunes; no one had kept an entropy account of it.

6. **Methodology: the channel-ablation control** (§8.5). We think this may be more useful than any individual number in the paper.

**Our own assessment: taken together, this adds up to a solid paper, not a new subfield of theoretical computer science.** Polishing it to the standard of one paper is far more likely to succeed than expanding it to the standard of a new discipline.

---

## 17. Epistemic status: how far has this been tested

**We consider this section more important than any single result.**

### 17.1 Tests already passed

- **Mathematical testing**: 14 theorems, mutually consistent, following a systematic consistency audit (six contradictions found and resolved, on record).
- **Controlled testing**: 7 experiments. The core claim (coordination cost is priced by task abstraction) survived **three mutually independent dissociations**.
- **Self-falsification**: the formal system has **overruled its author three times** (Theorem 5 overturned a central claim; the refinement algorithm twice corrected the author's own hand-computed predictions), and experiments have **overturned the theory three times** (the sharp threshold, the two-level rate condition, the $m=6$ condition).
- **External testing**: the core claim was confirmed on a standard public environment we did not design (§17.2).

> **An experiment that has been rigged will not overturn its own theory.** These self-falsifications are evidence that the setup was not manipulated, and are the strongest internal guarantee we can offer.

### 17.2 A confirmation on an external environment

**The core claim has been confirmed on a standard public environment we did not design.**

The environment is **PettingZoo / mpe2 `simple_spread_v3`** (Lowe et al., 2017) — a standard multi-agent reinforcement learning benchmark, with physics, rewards, observation layout, and action semantics all fixed by the package; we changed nothing.

The coordination content of this task is a **landmark assignment**, so

| | Variable | Size |
|---|---|---|
| Physical variable | sender's observation block | 10 continuous dimensions |
| Task variable | landmark assignment | $\log_2 3=\mathbf{1.58}$ bits |

**This ratio is not one we chose — it is determined by `simple_spread`'s reward structure.**

| $C$ (bits/step) | 1.58 | 3.00 | 4.00 | 6.00 |
|---|---|---|---|---|
| **oracle** (task variable) | $\mathbf{-44.75}$ | $-44.75$ | $-44.75$ | $-44.75$ |
| **learned** (learned abstraction) | $-46.28$ | $-48.21$ | $-46.95$ | $-46.69$ |
| **phys** (physical state, analytically decoded) | $-69.22$ | $-63.51$ | $-59.49$ | $\mathbf{-51.54}$ |

The channel-free upper bound is $-44.75$. Three readings:

1. **The task variable saturates exactly at $\log_23=1.58$ bits** — oracle already reaches the upper bound at $C=1.58$, and additional bits beyond that buy nothing. **This number was not fitted.**
2. **The learned abstraction is almost as cheap**: $-46.28$ at $C=1.58$, within about one standard error of the upper bound. The abstraction was learned, not given (held-out assignment accuracy 0.901, versus 0.333 for random).
3. **Encoding physical state costs more than 4× and never converges**: even at $C=6.00$ bits, it has still not caught up with learned's performance at $1.58$ bits.

**Channel ablation** (§8.5): oracle drops by 17.22, learned by 14.20; all three converge to the same uninformative baseline of about $-61$ after ablation. phys drops by only 2.30 — **it was never transmitting much task information to begin with**, consistent with reading 3.

> **The point of this section is not winning again — it is winning on someone else's field.** The structure of `simple_spread` was written by Lowe et al. (2017) for an entirely different purpose, and the theory produced a correct quantitative prediction for it.

### 17.3 Tests not yet passed

**These must be stated with equal clarity.**

- **This is still simulation, not a real-world system.**
- **These are still our own experiments, not a third-party replication.**
- On the external environment, only the **core claim** was tested (class coding versus state coding). $\sigma_\theta$, the fault-tolerant threshold $C^*(\varepsilon)$, and drift absorbability $h_A^\perp$ **have not been tested externally at all.**
- The learned abstraction used "predicting others' assignment" as a supervisory signal; **discovering that abstraction fully unsupervised has not been tested.**

### 17.4 An implementation bug we found (and its impact audit)

We found and fixed a numerical bug in our own refinement algorithm, and report it as found:

Signature equality originally used `np.round(sig, 9)`. **Fixed-point rounding is not a valid equality test** — values that are mathematically identical but computed along different floating-point paths can land on opposite sides of a rounding boundary, and be judged unequal at **any** fixed precision.

Symptom: for one environment the block count jumped erratically between 9 and 27 as the rounding constant varied (ROUND=9 → 27, 27, **9**, 27; ROUND=6 → 9, 9, **27**, 27). **Pure floating-point noise was masquerading as structure, in the direction of under-merging, which biases $h_\theta$ upward.**

The fix clusters by absolute tolerance instead. **Impact audit: every number in §8 and §10 was recomputed from scratch and none changed; all three tiers of sanity checks still pass.**

> **Methodological conclusion: fixed-point rounding equality is unsafe for partition refinement.**
>
> **Epistemic conclusion: we found one bug in our own code, which means there may be others.** The audited parts were unaffected, but that is not a guarantee that everything else is correct.

### 17.5 One-sentence summary

> **TIC has survived mathematical testing, controlled testing, and one confirmation on someone else's environment. It has not yet survived — because it has not yet been submitted to — real-world testing or third-party replication.**

---

## 18. Open problems

Ordered by our own judgment of value:

1. **Move $\sigma_\theta$, the fault-tolerant threshold, and drift absorbability onto external environments.** The core claim is confirmed on MPE (§17.2), but the quantities in Theorem 14 and Theorem 11′ have **never once been tested externally** — that is currently the largest asymmetry in the evidence.
2. **Real systems and third-party replication.** This is the only thing that can change §17.3. **Do not benchmark against LLMs — TIC does not predict perplexity, and that comparison is a dead end.**
3. **Partially absorbable drift** ($0<h_A^\perp<h_A$). This is exactly where Theorem 11′ has the most content, and we have only tested the two endpoints.
4. **Rate allocation by task distortion.** §13 found that quantizing "the right variable" is not enough — rate must also be **allocated** according to the task's distortion requirements (uniformly quantizing the operational variable wastes rate — measured to underperform the learned abstraction at low $C$). Rate-distortion theory already has the tools; TIC has not yet connected to them.
5. **The correct asymptotic form of Corollary 14.3.** The current statement is valid only as a lower envelope.
6. **The behavior of $\sigma_\theta$ on strongly correlated chains.** The autocovariance correction has only been tested for $n\le4$ under weak correlation.
7. **Achievability of the Theorem 2 lower bound.** So far there is only empirical evidence that naive coding can approach it to within 0.3–0.9 bits; there is no analytic achievability construction.

---

## 19. Conclusion

The claim this paper defends is narrow enough to state in one sentence and load-bearing enough to organize fourteen theorems around: intelligent computation selects state transitions on the coarsest task-determined abstraction, and every departure from that abstraction has a price stated in bits. We have tried to make each piece of that claim answerable rather than rhetorical. "Coarsest" is Theorem 4, not a metaphor. "Price" is $h_\theta$, $\sigma_\theta$, and $R_\theta(D)$, each with a measured value and a stated condition under which the measurement stops meaning what we say it means. Where the theory made a wrong prediction — a sharp threshold that isn't sharp, a two-level rate condition that overcharges, a value proposition for deliberation that a rescue robot refutes in one paragraph — we have kept the wrong prediction in the text next to the correction, on the view that a theory's self-corrections are evidence about it, not embarrassments to be edited out.

What we have not done is claim more than the evidence in §17 supports. The bandwidth law survives three independent dissociations and one confirmation on a benchmark we did not build; the fault-tolerant threshold and the drift-absorption criterion have not left our own simulations; nothing here has been checked against a physical system or reproduced by anyone else. Section 18's ordering of open problems is also our ordering of priorities: an external test of $\sigma_\theta$ and $h_A^\perp$ would do more to settle whether this theory is right than another theorem would. We would rather submit this paper at the stage of "here is what we have shown, checked, and not yet checked" than wait for a completeness that a single-author theoretical project is not positioned to reach on its own — which is also why the companion materials in Appendix D are offered for exactly that purpose.

---

# Appendices

## Appendix A — Proofs and constructions

**A.1 Full proof of Theorem 4**: see §4.2 (main text). Numerical verification: hand-worked 6-state and 7-state examples; on real kernels the analytic prediction $|S/\!\sim|=m^2$ was matched exactly in 5 configurations, and the blocks were confirmed to be functions of relative offset.

**A.2 Counterexample and threshold for Theorem 5**: the rescue-robot construction (§5.2); the derivation and numerical verification of the threshold $q_{\max}+q_{\min}\ge1$ are given in `theorem-verification/`.

**A.3 Lemma 14.1 and Theorem 14**: see §10.2–10.3 (main text, complete).

**A.4 Counterexample to reachable-set equivalence $\ne$ behavioral equivalence**: see §4.1(d), a machine-verified 4-state construction.

## Appendix B — Experimental specifications and a pitfall checklist

We recommend that anyone reproducing experiments of this kind check the following seven items. The first six come from ordinary diligence; **the seventh comes from a real incident.**

| # | Check | Why |
|---|---|---|
| 1 | Each agent's randomness must be **independent** | Two agents once shared a partition-ordering seed, producing an apparent "100% coordination rate" that was actually synchronized identical mistakes |
| 2 | The refinement algorithm must first be validated on **hand-worked small examples** | A wrong function variant was once used, which degenerated trivially in the absence of a goal signal, and the result looked like "confirmation" of the theory |
| 3 | Success rate must **span 0 and 1** | Grid points stuck at 0 or 1 carry no information; the $m=6$ condition was retired for this reason |
| 4 | $h$ and $h_\theta$ must use the **same estimator** | Otherwise the inequality can hold or fail spuriously due to estimator bias |
| 5 | The scale axis must **actually move the quantity it is supposed to move** | "State count $\times3.16$" was once used as a scale axis, moving $h$ by only 0.07 bits — effectively idling |
| 6 | Save **raw data** (means, variances, seed counts) | Looking only at means can hide distributional problems |
| **7** | **Channel-ablation control** | **Rerun with all transmitted symbols randomized; if performance does not collapse, decisions never went through the channel, and the batch is invalid** |

**Where item 7 comes from**: an early implementation indexed its policy table by the true joint state, making the channel purely decorative — the success rate was already 1.000 at $C=1$ bit. All six routine checks "passed." **Only the ablation control caught it.**

## Appendix C — Notation

| Symbol | Meaning | First appears |
|---|---|---|
| $S,\tau,O,D,H$ | the five primitives | §2.2 |
| $H_0,H_1$ | Layer 0 / Layer 1 entropy | §3.1 |
| $H_S,H_D,H_T$ | state entropy / deliberation entropy / transition entropy | §3.2 |
| $\sim_\theta$ | task-sufficient equivalence | §4.1 |
| $\sim_\theta^*$ | **canonical abstraction** (coarsest) | §4.2 |
| $h$ | physical entropy rate | §4.4 |
| $h_\theta$ | **intrinsic task bandwidth** | §4.4 |
| $C$ | channel capacity (bits/step) | §6 |
| $T$ | per-step information variable, $-\log_2P(S'_\theta\mid S_\theta)$ | §10.1 |
| $\sigma_\theta$ | **operational variance-entropy** | §10.5 |
| $\varepsilon$ | tolerated per-step tracking error rate | §10.6 |
| $C^*(\varepsilon)$ | fault-tolerant threshold | §10.6 |
| $h_A$ | ontological drift rate | §12 |
| $h_A^\perp$ | **non-absorbable drift rate** | §12.4 |
| $R_\theta(D)$ | task rate-distortion function (continuum limit) | §13.2 |

## Appendix D — Code and Data Availability

All verification scripts, raw experimental data (discrete rendezvous, $\sigma_\theta$ measurements, drift absorption; continuous-torus experiments; the external `simple_spread_v3` evaluation), and the theorem-development notes underlying this paper are available at: **[REPOSITORY URL — TO BE ADDED BEFORE SUBMISSION]**.

Until the repository is public, materials are available from the corresponding author on request.

---

## References

Aubin, J.-P. (1991). *Viability Theory*. Birkhäuser.

Audenaert, K. M. R. (2007). A sharp continuity estimate for the von Neumann entropy. *Journal of Physics A: Mathematical and Theoretical*, 40(28), 8127–8136.

Barreto, A., Dabney, W., Munos, R., Hunt, J. J., Schaul, T., Silver, D., & van Hasselt, H. (2017). Successor features for transfer in reinforcement learning. In *Advances in Neural Information Processing Systems 30 (NeurIPS 2017)*.

Crutchfield, J. P. (1994). The calculi of emergence: Computation, dynamics, and induction. *Physica D: Nonlinear Phenomena*, 75(1–3), 11–54.

Dayan, P. (1993). Improving generalization for temporal difference learning: The successor representation. *Neural Computation*, 5(4), 613–624.

Fannes, M. (1973). A continuity property of the entropy density for spin lattice systems. *Communications in Mathematical Physics*, 31, 291–294.

Ferns, N., Panangaden, P., & Precup, D. (2004). Metrics for finite Markov decision processes. In *Proceedings of the 20th Conference on Uncertainty in Artificial Intelligence (UAI 2004)*.

Friston, K. (2010). The free-energy principle: A unified brain theory? *Nature Reviews Neuroscience*, 11, 127–138.

Givan, R., Dean, T., & Greig, M. (2003). Equivalence notions and model minimization in Markov decision processes. *Artificial Intelligence*, 147(1–2), 163–223.

Haarnoja, T., Zhou, A., Abbeel, P., & Levine, S. (2018). Soft actor-critic: Off-policy maximum entropy deep reinforcement learning with a stochastic actor. In *Proceedings of the 35th International Conference on Machine Learning (ICML 2018)*.

Halpern, J. Y., & Moses, Y. (1990). Knowledge and common knowledge in a distributed environment. *Journal of the ACM*, 37(3), 549–587.

Kaelbling, L. P., Littman, M. L., & Cassandra, A. R. (1998). Planning and acting in partially observable stochastic domains. *Artificial Intelligence*, 101(1–2), 99–134.

Kanellakis, P. C., & Smolka, S. A. (1990). CCS expressions, finite state processes, and three problems of equivalence. *Information and Computation*, 86(1), 43–68.

Kontoyiannis, I., & Verdú, S. (2013). Optimal lossless compression: Source varentropy and dispersion. In *Proceedings of the 2013 IEEE International Symposium on Information Theory (ISIT 2013)*.

Larsen, K. G., & Skou, A. (1991). Bisimulation through probabilistic testing. *Information and Computation*, 94(1), 1–28.

Li, L., Walsh, T. J., & Littman, M. L. (2006). Towards a unified theory of state abstraction for MDPs. In *Proceedings of the International Symposium on Artificial Intelligence and Mathematics (ISAIM 2006)*.

Lowe, R., Wu, Y. I., Tamar, A., Harb, J., Abbeel, P., & Mordatch, I. (2017). Multi-agent actor-critic for mixed cooperative-competitive environments. In *Advances in Neural Information Processing Systems 30 (NeurIPS 2017)*.

Paige, R., & Tarjan, R. E. (1987). Three partition refinement algorithms. *SIAM Journal on Computing*, 16(6), 973–989.

Polyanskiy, Y., Poor, H. V., & Verdú, S. (2010). Channel coding rate in the finite blocklength regime. *IEEE Transactions on Information Theory*, 56(5), 2307–2359.

Russell, S., & Wefald, E. (1991). Principles of metareasoning. *Artificial Intelligence*, 49(1–3), 361–395.

Shalizi, C. R., & Crutchfield, J. P. (2001). Computational mechanics: Pattern and prediction, structure and simplicity. *Journal of Statistical Physics*, 104, 817–879.

Tatikonda, S., & Mitter, S. (2004). Control under communication constraints. *IEEE Transactions on Automatic Control*, 49(7), 1056–1068.

---

*v1.0 · English edition, rewritten (not translated) from the Chinese long-form paper for arXiv submission. Open problems and negative results are reported as-is; see §18.*
