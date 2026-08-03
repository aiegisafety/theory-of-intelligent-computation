# TIC — Consistency Audit and Resolutions (v0.5)

Audited: `TIC-Consolidated-v0.3.md` + theorem layers v0.1–v0.4 (7 theorems, 2 experiments).
Date: 2026-07-31. Author: Claude, acting on Stein's instruction to resolve the theory's internal contradictions and to exercise judgment where a decision is needed.

---

## 0. What I did, and the one thing to read first

I stopped adding results and instead checked whether what exists is consistent. I found **six genuine contradictions or unresolved tensions**, one of which is serious enough that it undermined the theory's central claim of distinctiveness. All six are resolved below. Resolving them required three new small theorems (T8–T10), which are proved and verified, and one structural change to the theory's foundations.

**If you read one section, read A1.** The theory has been quietly running two incompatible definitions of entropy — a prior-free one in the definitions and a Bayesian one in the theorems. The resolution is not to choose between them but to recognize that TIC has **two layers**, and that its distinctive claims live in the prior-free layer while its neighbours (POMDP, Active Inference) live in the probabilistic one. That is a better position than the one we thought we had.

Section D lists every decision I made on your behalf. All are reversible.

---

# Part A — Contradictions found and resolved

## A1. The prior problem: State Entropy is defined one way and used another

### The contradiction

`v0.3 §1.6a` defines State Entropy over the **evidence-induced possibility set**:

$$\Omega(e)=\{S : S \text{ consistent with evidence } e\},\qquad H_S = H(\Omega(e))$$

with the explicit claim that this is *epistemic but not subjective*, requires no prior, and is therefore **not** a POMDP belief. That definition exists because you insisted — correctly — that the state is objective and that its entropy is usually zero.

But **Theorem 2 is proved about $H(S_t \mid e_t)$**, a conditional Shannon entropy, which presupposes a joint probability distribution over states and evidence — i.e. exactly a prior. And Experiment 1 implements literal Bayesian belief updating. So the definitional layer says "no priors" while the load-bearing theorem and the only experiment both use one.

This is not a wording problem. It means the claimed separation from POMDP was asserted in the definitions and abandoned in the proofs.

### The resolution: TIC has two entropy layers, and they are both legitimate

Rather than choose, name both. They correspond to two standard and long-established notions.

| | **Layer 0 — possibilistic** | **Layer 1 — probabilistic** |
|---|---|---|
| Object | possibility set $\Omega(e)$ | distribution over states |
| Entropy | $H_0 = \log_2|\Omega(e)|$ (Hartley) | $H = -\sum p\log p$ (Shannon) |
| Requires | evidence only | evidence **and a prior** |
| Equivalence | ordinary bisimulation | probabilistic bisimulation |
| Neighbours | nondeterministic systems, epistemic logic, classical model minimization | POMDP, Active Inference, RL abstraction |

with the standard relation $H \le H_0$, equality iff uniform.

**Layer 0 is TIC's definitional default** — it is what makes $H_S=0$ the normal case, keeps entropy attached to evidence rather than to opinion, and delivers the epistemic-not-subjective claim honestly. **Layer 1 is a refinement available when a probability model is warranted**, and is where comparison with the neighbours takes place.

### What this does to the existing theorems — three consequences, one of them striking

**(i) The "uniform law" was secretly the Layer-0 theorem.** Corollary 1.1 said: eliminating a fraction $p$ of *equiprobable* candidates buys $\log\frac{1}{1-p}$ bits. In Layer 0 there is no "equiprobable" — there is only counting — and the same statement is the general theorem:

$$\Delta H_0 = \log_2\frac{|\Omega_\tau|}{|\Omega_\tau^{A}|} = \log_2\frac{1}{1-p},\qquad p = \text{fraction of candidates removed}$$

What looked like a special case was the primitive law; the probabilistic identity of Theorem 1 is the refinement.

**(ii) The pathology of Corollary 1.4 is prior-induced.** In Layer 0, $\Delta H_0 \ge 0$ always: removing candidates can never increase $\log|\Omega|$. The reversal — constraints that veto the modal candidate *raising* $H_D$ — **cannot occur without a prior**. This sharpens rather than weakens the finding: *the phenomenon by which a safety constraint increases deliberation cost is an artefact of the agent having concentrated its belief, not of the constraint itself.* An agent reasoning possibilistically never suffers it; an agent with confident predictions does. That is a much more interesting statement than the one we had, and it is testable.

**(iii) Theorem 2 has a prior-free form.** Let $b$ be the branching number of the dynamics (minimum number of possible successors). Observation carrying $C$ bits takes at most $2^C$ values, so the possibility sets it induces partition the pre-observation set; their sizes sum to it, hence the average part has size at least $|{\cdot}|/2^C$. Combining with growth by the dynamics:

$$\boxed{\ \mathbb{E}\,\big|\Omega(e_{t+1})\big| \;\ge\; b\,/\,2^{C}\ }\qquad\text{equivalently}\qquad H_0 \;\gtrsim\; \log_2 b - C$$

**Proof.** Dynamics: every $S\in\Omega(e_t)$ has at least $b$ successors consistent with the evidence so far, so the pre-observation possibility set has size $\ge b$. Observation: the $\le 2^C$ possible readings induce a partition of that set, so the sizes sum to it and the mean part size is at least $b/2^C$. $\blacksquare$

This is Theorem 2 with no prior anywhere — the version that actually matches the definition in §1.6a. The Shannon form remains valid in Layer 1 with $h$ in place of $\log b$.

### What must change in the documents

Every theorem must be labelled with its layer. Current assignment: **T1** (both, with the counting form primitive) · **T2** (both) · **T3** (Layer 0 — it is about class identity, no probabilities needed) · **T4, T6, T7** (Layer 1 as proved, via TV between distributions; each has a Layer-0 shadow in ordinary bisimulation, which is the *classical* and better-studied setting) · **T5** (Layer 1 — it is precisely a statement about what happens when you make a probabilistic functional the objective).

**Net effect on positioning.** The claim "TIC's $H_S$ is not a POMDP belief" is now true where it is asserted (Layer 0) instead of being contradicted three pages later. And the Layer-0 shadow of the abstraction theorems connects TIC to classical bisimulation and model minimization for nondeterministic systems — an older, cleaner literature than the probabilistic one, and one where the algorithms are simpler.

---

## A2. Is Deliberation primitive or derived?

### The contradiction

`v0.3 §0.3` lists $D$ among the primitives, on your explicit instruction (you overruled the proposal to make Deliberation an implementation of a "Transition Operator", and you were right). But `v0.3 Ch. 3` then defines deliberation as **state evolution over $\sigma=(\Omega_\tau, P(\tau), e)$** — built entirely from State, Transition and Observation. By the theory's own Rule 1 (*a primitive cannot be derived from the remaining primitives*), Chapter 3 derives away a primitive.

### The resolution: identify what is actually irreducible

Chapter 3's construction accounts for the *dynamics* of deliberation — expansion, pruning, evidence acquisition — and those genuinely are state evolution. What it does not and cannot construct from $\{S,\tau,O\}$ is the distinction it silently assumes throughout:

> Some transitions are **entertained** (internal, revocable, consequence-free); some are **committed** (external, irrevocable, consequential).

Nothing in State plus Transition marks which is which. A transition kernel does not know whether it is being simulated or executed. Call this marker the **commitment relation** $\kappa$.

With $\kappa$ in hand:

- **Deliberation** = state evolution restricted to entertained transitions, terminating in a commitment;
- **Action** = a committed transition whose effect is realized externally.

So Deliberation and Action are the two faces of one irreducible thing, which also explains why v0.2's derivation of Action from Transition felt slightly too easy: what was derived was Action's *form* (it is a transition), not its *status* (it is committed).

**Decision.** $D$ stays in the primitive list, with its irreducible content now identified as $\kappa$ rather than left unanalysed. Chapter 3 is relabelled: it models deliberative dynamics **given** the commitment boundary; it does not define deliberation. Your original instinct is preserved and now has a reason.

**Testable consequence.** A system with no commitment boundary — one that cannot entertain a transition without enacting it — is by this account incapable of deliberation regardless of its capacity. Pure next-token generation without rollback is exactly such a system, which is a sharper form of your original objection to Transformers than "it has no Deliberation Space".

---

## A3. Cooperation: Theorem 3 is satisfied by two entities that are identically wrong

### The contradiction

Theorem 3 makes cooperation conditional on $[\hat S_A]_\theta = [\hat S_B]_\theta$. Experiment 1 then found agreement rising while correctness fell (agreement by shared ignorance). Meanwhile the **Reality Principle** (v0.3 §1.7) demands that all intelligent computation be grounded in the objective state. So the theory's cooperation criterion does not meet the theory's own standard.

### The resolution: two conditions, not one

$$\textbf{Coherence:}\quad [\hat S_A]_\theta = [\hat S_B]_\theta \qquad\qquad \textbf{Grounding:}\quad [\hat S_i]_\theta = [S^{*}]_\theta$$

Grounding implies coherence; not conversely. Theorem 3 establishes exactly what coherence buys — **absence of admissibility conflict** — and nothing more. Correct joint action requires grounding, which is what the Shared State architecture (a single referent) exists to supply.

**Corollary A3.1 (coordinated error is cheap).** Coherence costs $h_\theta$ bits/step of mutual synchronization. Grounding costs whatever it costs to track reality, which by Theorem 2 has a floor no protocol beats. Since coherence can be achieved *without* grounding — two entities synchronizing with each other rather than with the world — **the cheapest stable configuration of a multi-agent system is perfect coordination on a false state.** Groups fall into it not from stupidity but because it is the low-energy state.

This is the theorem-level statement of why the Shared State architecture insists on a single objective referent rather than on consensus, and it is, I think, the most consequential thing in this audit after A1. It also predicts something checkable: multi-agent systems that synchronize agent-to-agent will drift into confident agreement faster than systems that synchronize agent-to-world, and the drift rate should scale with the ratio of the two costs.

---

## A4. "Entropy Reduction Principle" survives Theorem 5 only as description

`v0.3 §1.8` still calls entropy regulation "the essence of intelligent computation" while §1.8's revised box (after T5) says entropy is not the objective. Both cannot be foregrounded.

**Resolution (wording, but load-bearing).** Entropy regulation is a **description of the process**, not a statement of its purpose:

> Intelligent computation *proceeds by* regulating $H_S$, $H_D$ and $H_T$; it *aims at* transition quality. The entropies are what the process spends and what an observer can measure — not what it is for.

Delete "essence"; the sentence now reads as an empirical description, which is what T5 leaves standing.

---

## A5. Theorem 4 did not remove the free parameter — it relocated all of it into the goal

Theorem 4 is stated as "the abstraction is not chosen, it is computed", which is true — but it is computed *from the goal partition*. The designer's freedom did not vanish; it was concentrated. Since Memory (T9 below), bandwidth (Cor. 4.2), cooperation (T3) and the learnable abstraction (T7) are all now derived from $\sim_\theta^{*}$, and $\sim_\theta^{*}$ is derived from $g$:

$$\boxed{\ \text{TIC now has exactly one free parameter: the goal.}\ }$$

This is worth stating prominently rather than treating as a caveat. It sharpens the open problem list to a single item of real depth — *where do goals come from* — and it means any criticism of the theory's arbitrariness must attack the goal specification, not the machinery.

---

## A6. "Encode the class, not the state" appears to contradict general-purpose shared state

Experiment 1 concluded that channels should carry operational classes. But classes are task-relative, and a shared state store serves many tasks. Taken naively the two recommendations conflict.

### Theorem 10 (multi-task synchronization cost)

An entity serving tasks $\theta_1,\dots,\theta_k$ must be able to answer each, so it must maintain the **common refinement** $\bigwedge_i \sim_{\theta_i}$ (blocks are intersections). Hence its synchronization requirement is $h_{\wedge}$, and

$$h_{\wedge} \;\ge\; \max_i h_{\theta_i}, \qquad h_{\wedge} \nearrow h \ \text{ as tasks proliferate}$$

**Verified** ($N=36$ physical states, $h=4.221$ bits/step; each task a 3-way partition):

| tasks | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| blocks of the refinement | 3 | 9 | 19 | 28 | 34 | 35 |
| $h_\wedge$ | 1.501 | 2.815 | 3.868 | 4.103 | 4.196 | **4.206** |
| $\max_i h_{\theta_i}$ | 1.501 | 1.501 | 1.550 | 1.564 | 1.564 | 1.564 |

Six tasks already cost 4.206 of the physical 4.221 bits.

### The resolution, and why existing practice is right

There is no contradiction once layers are respected: **the store holds state; the channel encodes classes.** And Theorem 10 explains the observed engineering trade-off rather than contradicting it:

> **General-purpose state sharing costs the physical entropy rate, by theorem.** A store that must serve arbitrary future tasks has no cheaper option than raw values — which is exactly what databases do, and why they are expensive to synchronize. Task-specific channels are cheap *because* they are task-specific, and their cheapness is forfeited the moment they must serve a second purpose.

The design rule from Experiment 1 therefore applies to **channels and protocols**, not to stores — and the corollary for the Part III architecture is that a shared-state runtime should expose *per-task class projections* over a common store, not one universal encoding.

---

# Part B — Theorem-filter audit

Rule 10 of the constitution: *nothing becomes part of TIC unless it eventually appears in a theorem.* Applying it honestly to the current concept set:

| Concept | Appears in a theorem? |
|---|---|
| State, Transition, Observation, Entropy | yes (T1–T7) |
| State Equivalence, task abstraction | yes (T3, T4, T6, T7) |
| Constraint | yes (T1) |
| Goal | only as the seed of $\sim_\theta^{*}$ (T4) |
| **Memory** | **no** |
| **Identity** | **no** |
| **Provenance / authority / evidence-bearing shared state** | **no** |
| Deliberation | partially — its dynamics, not its irreducible content |

Three concepts were carrying no mathematical weight. Two of them can be discharged immediately; the third cannot, and I mark it accordingly.

### Theorem 8 — Identity lowers the cost of being cooperated with

Identity constrains an entity's admissible transitions to a submanifold $\Omega_D$. Since conditioning cannot increase entropy, the entity's own state process has a lower rate; by Theorem 6.1, the capacity a partner needs to track it falls accordingly.

$$h\big(\text{constrained}\big) \;\le\; h\big(\text{unconstrained}\big) \;\Longrightarrow\; C_{\text{required}} \ \text{falls}$$

**Verified** ($\lambda$ = probability of leaving one's identity manifold):

| $\lambda$ | 1.00 | 0.70 | 0.50 | 0.30 | 0.20 | 0.10 | 0.05 |
|---|---|---|---|---|---|---|---|
| $h$ (bits/step) | 4.221 | 3.986 | 3.607 | 3.056 | 2.701 | 2.267 | **2.003** |

> **Identity is what makes an entity cheap for others to model.** Value drift is therefore not only an alignment concern but a *communication cost*: an entity whose constraints loosen forces every partner to spend more bandwidth on it, and by Theorem 2 there is a point past which no partner can track it at all.

This also gives the multi-timescale formulation of Identity (v0.3 §4.4) its first mathematical use: each slow variable $D_k$ contributes a reduction in rate proportional to how tightly it binds.

### Theorem 9 — the minimal task-adequate memory is the operational state

Under exact adequacy, the class $[S]_\theta$ is a sufficient statistic for everything $\theta$-deliberation requires: admissibility depends only on the class (Lemma 3.1) and the successor class distribution depends only on the class (condition D). By Theorem 4's maximality no coarser statistic suffices. Hence:

$$\boxed{\ \text{Minimal }\theta\text{-adequate memory} \;=\; [S]_\theta\ }$$

**Corollary 9.1 (why memory exists at all).** Under *exact* adequacy no history is needed — the current class suffices. History becomes valuable exactly when the abstraction is only $\varepsilon$-adequate, since then the class process is not Markov and past classes carry residual predictive information.

> **Memory is the price of imperfect abstraction.**

An entity with a perfect task abstraction needs no memory beyond its current operational state; every real entity has an imperfect one, and its memory is the compensation. This is the first statement that connects Memory (previously a free-floating Operator) to the proved core, and it agrees with the independently-motivated definition of memory as predictive compression — the minimal predictively-sufficient statistic is precisely the causal-state construction.

### Not discharged: provenance, authority, evidence-bearing state

Part III's five-element shared state (entity, value, identity, evidence, authority) appears in no theorem and does no mathematical work anywhere. It is well-motivated engineering and it is the natural TIC↔PEA interface, but by Rule 10 it is **not yet part of the theory**. I have marked it *Candidate — not load-bearing* rather than quietly leaving it as if it were established. The obvious route to discharging it: provenance is what makes grounding (A3) checkable, so a theorem of the form *"grounding is verifiable only if state carries provenance"* would earn it entry. I did not attempt it here.

---

# Part C — Revised concept register

| Concept | Layer | Load-bearing | Status |
|---|---|---|---|
| State | Primitive (object) | ✅ T1–T10 | Stable |
| Transition | Primitive (morphism) | ✅ | Stable |
| Observation | Primitive (operator) | ✅ T2 | Stable |
| Deliberation | Primitive (operator); irreducible content = commitment relation $\kappa$ | ◐ dynamics only | **Revised A2** |
| Entropy — Layer 0 (Hartley, possibility sets) | Primitive (measure) | ✅ T1, T2 | **New A1 — definitional default** |
| Entropy — Layer 1 (Shannon, priors) | Refinement | ✅ T1, T2, T5 | **New A1** |
| Entity | Index over states | ○ | Stable |
| Action | Derived: committed transition | ✅ via $\kappa$ | Revised A2 |
| Goal | Structure; **the sole free parameter** | ✅ seeds T4 | **Elevated A5** |
| Constraint | Structure | ✅ T1 | Stable |
| State Equivalence $\sim_\theta^{*}$ | Derived, canonical | ✅ T3,4,6,7,9,10 | Stable |
| Operational state / physical state | Derived (quotient / base) | ✅ | Stable |
| Bandwidth $h_\theta$ | Derived task invariant | ✅ T2,4,6,8,10 | Stable |
| Memory | Operator | ✅ **T9** | **Discharged B** |
| Identity | Constraint | ✅ **T8** | **Discharged B** |
| Shared State | Architecture | ✅ T3, T10 | Stable |
| Coherence vs Grounding | Derived conditions | ✅ **A3** | **New** |
| Provenance / authority / evidence | Architecture | ❌ none | **Candidate — not load-bearing** |
| Language | Derived (projection) | ❌ none | Candidate |
| Reading the room, Persistent Agent, Collective State, Shared Context, Transition Operator | — | — | Deleted (v0.3) |

---

# Part D — Decisions I made on your behalf

All reversible; each is where I judged rather than derived.

1. **Two entropy layers, with Layer 0 as the definitional default** (A1). The alternative — admitting $H_S$ is a Bayesian belief entropy — would have been simpler but would have collapsed your position into POMDP and made §1.6a false.
2. **Deliberation keeps primitive status, with $\kappa$ named as its irreducible content** (A2). I preserved your ruling and supplied the reason it survives Rule 1. The alternative was to demote Deliberation, which the formalism permitted and which I judged wrong.
3. **Theorem 3 restated as *coherence*, with *grounding* separated out** (A3). This weakens Theorem 3's advertised scope and I think that is correct — the earlier statement claimed more than it proved.
4. **"Essence of intelligent computation" removed from the entropy principle** (A4).
5. **The goal declared the theory's single free parameter** (A5) — a promotion of an open problem to a structural fact about the theory.
6. **Provenance marked as not-yet-part-of-the-theory** (B). It is your bridge to PEA and I expect you may want it in; by the theory's own rule it has not earned entry, and I judged consistency more valuable than reach.

---

# Part E — Where the theory now stands

**Ten theorems, two experiments, one free parameter.** Nothing in the corpus now contradicts anything else, so far as I can determine. Three earlier claims have been corrected by the formalism (constraints can raise $H_D$; entropy is not the objective; Theorem 3 proves coherence not cooperation), and one has been strengthened by being split (state entropy into two layers).

**The shape of what remains.** With A5 in place the open problems collapse into a short and unusually clean list:

1. **Where goals come from.** Now the only free parameter, hence the only place where TIC is arbitrary. Everything else is computed from it. This is no longer one open problem among six — it is *the* open problem.
2. **The exact usable $\varepsilon$-window** (from Experiment 2) — small, well-posed, finishable.
3. **Analytic achievability for Theorem 2** — the floor is empirically near-tight.
4. **Layer-0 versions of T4, T6, T7** — likely easier than the probabilistic ones, since ordinary bisimulation is better understood than probabilistic bisimulation, and they would put TIC's abstraction theory in its natural (prior-free) home.
5. **A theorem for provenance**, or an honest decision to leave it in the architecture layer permanently.
6. Continuous state; the Active Inference comparison chapter.

**My assessment of the criterion you set.** You asked for a theory with mathematical vitality. The test I would apply: does the formalism generate results nobody inserted, and does it refuse claims its author wanted? Both have now happened repeatedly — the bandwidth law, the split/merge asymmetry, the bandwidth tax, and the multi-task refinement cost were all produced rather than assumed; the entropy-objective, the unconditional convergence claim, and Theorem 3's scope were all refused. The audit this round found the deepest inconsistency yet and resolving it improved the theory's position rather than damaging it. That is the behaviour of a live formalism.

What it is not yet: a theory anyone else can pick up. The corpus is five documents written for one reader. If the goal is eventually to publish or to have others build on it, the next non-mathematical task is a single self-contained 20-page statement — definitions, ten theorems, two experiments, related work, open problems — with everything else demoted to appendices and research notes. I would do that before adding an eleventh theorem.

---

## Appendix — verification

`verify7.py` (Theorem 10, multi-task refinement cost), `verify8.py` (Theorem 8, identity and tracking cost). Both in `theorem-verification/`. Output reproduced inline in A6 and B.

## Sources

- Hartley (1928); Shannon (1948) — the two entropy notions of A1; see Cover & Thomas §2 for the $H\le\log|\Omega|$ relation.
- Kanellakis & Smolka; Paige & Tarjan — ordinary bisimulation and partition refinement, the Layer-0 home of T4/T7.
- Larsen & Skou — probabilistic bisimulation, the Layer-1 form.
- [Givan, Dean & Greig (AIJ 2003)](https://www.sciencedirect.com/science/article/pii/S0004370202003764) — model minimization, both layers.
- Shalizi & Crutchfield (2001) — causal states as minimal sufficient statistics, agreeing with Theorem 9.
- Halpern & Moses (JACM 1990) — epistemic logic and possibility sets, the natural formal home of Layer 0.
