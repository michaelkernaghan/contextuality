# Contextuality in Interpretations of Quantum Mechanics

The Kochen–Specker theorem establishes that quantum mechanics is contextual—a fact that any interpretation must accommodate. But *how* different interpretations handle contextuality varies dramatically. Some embrace it, others explain it away through different mechanisms, and still others make it central to their worldview.

This page examines how contextuality manifests across the major interpretations of quantum mechanics.

---

## Historical Background

### The Interpretation Problem

Quantum mechanics provides an extraordinarily successful mathematical apparatus for predicting experimental outcomes. But what does it tell us about reality? Different interpretations answer this question differently:

- What is the quantum state?
- What happens during measurement?
- Are there hidden variables?
- Is the world deterministic?

The KS theorem constrains the space of possible interpretations: any interpretation must either deny hidden variables, accept contextual hidden variables, or modify the quantum formalism itself.

### Timeline of Major Interpretations

| Era | Interpretation | Key Figures |
|-----|----------------|-------------|
| 1920s–30s | Copenhagen | Bohr, Heisenberg |
| 1952 | Pilot-wave theory | Bohm |
| 1957 | Many-worlds | Everett |
| 1986 | GRW objective collapse | Ghirardi, Rimini, Weber |
| 1985–present | Modal interpretations | van Fraassen, Dieks |
| 2002 | QBism | Fuchs, Schack |
| 2005 | Spekkens' epistemic view | Spekkens |

---

## Key Figures and Ideas

### Copenhagen Interpretation

**Core claims:**

1. The quantum state $\psi$ is a complete description—there are no hidden variables
2. Observables do not have definite values until measured
3. Measurement causes "collapse" to an eigenstate
4. The experimental arrangement determines what can be meaningfully said about the system

**How it handles contextuality:**

!!! quote "Copenhagen and Context"
    For Copenhagen, contextuality is not a puzzle—it's a feature. Since observables don't have pre-existing values, the question of whether those values are context-dependent doesn't arise. The measurement *creates* the outcome; it doesn't reveal a pre-existing property.

**Bohr's view in particular:**

Bohr emphasized the "wholeness" of quantum phenomena: the system and measuring apparatus form an indivisible whole. Different experimental arrangements (contexts) define different phenomena. Asking about the value of an observable outside of any measurement context is, for Bohr, meaningless.

**Compatibility with KS:**

Copenhagen is compatible with the KS theorem because it denies the premise: there are no values to be contextual or noncontextual. The theorem simply confirms what Copenhagen already assumed—that we cannot assign definite pre-measurement values.

---

### Bohmian Mechanics (Pilot-Wave Theory)

**Core claims:**

1. Particles have definite positions at all times
2. The wave function $\psi$ guides particle motion via the guidance equation
3. Quantum statistics arise from initial uncertainty about positions
4. Measurement outcomes are determined but appear random due to ignorance

**How it handles contextuality:**

!!! important "Bohmian Contextuality"
    Bohm's theory is **explicitly contextual**. The outcome of a measurement depends not just on the particle's position (the hidden variable) but also on the wave function of the measuring apparatus. The same particle position can yield different outcomes depending on what else is measured.

**The mechanism:**

Consider measuring spin. In Bohmian mechanics:

- The particle has a definite position
- It does *not* have a definite spin value prior to measurement
- The spin measurement outcome depends on how the Stern-Gerlach apparatus interacts with the guiding wave
- Different measurement setups (contexts) channel the particle differently

**Compatibility with KS:**

Bohm's theory evades the KS theorem by being contextual. It has hidden variables (positions), but it does not assign noncontextual values to all observables. The KS theorem proves that any hidden-variable completion of quantum mechanics must be like this.

---

### Many-Worlds / Everett Interpretation

**Core claims:**

1. The quantum state never collapses—only unitary evolution occurs
2. "Measurement" is just entanglement between system and observer
3. All outcomes occur, in different "branches" of reality
4. Observers experience only one branch, creating the illusion of collapse

**How it handles contextuality:**

!!! info "Everettian Contextuality"
    In many-worlds, contextuality manifests as **basis dependence of branching**. The way the universe "splits" depends on what basis the measurement is performed in. Different measurement contexts lead to different branching structures.

**The mechanism:**

When you measure an observable $A$:
- The universe branches according to the eigenstates of $A$
- Each branch contains a version of you seeing one of $A$'s eigenvalues

When you measure a different observable $B$:
- The universe branches according to $B$'s eigenstates
- The resulting branches are different from the $A$-measurement branches

There is no fact about "what the system's value was before measurement"—the branching structure depends on the measurement choice.

**Compatibility with KS:**

Everett is compatible with KS because it doesn't assign definite values to observables prior to branching. The interpretation avoids hidden variables entirely, embracing the quantum state as complete.

**The preferred basis problem:**

A major challenge for many-worlds: what determines which basis defines the branches? Decoherence provides a partial answer (pointer states emerge dynamically), but the connection to contextuality remains subtle.

---

### GRW (Objective Collapse) Theories

**Core claims:**

1. The wave function undergoes spontaneous localization events
2. These collapses are random, with a specified rate (one per ~$10^8$ years per particle)
3. For macroscopic objects, frequent collapses ensure definite positions
4. This solves the measurement problem without invoking observers

**How it handles contextuality:**

!!! quote "GRW and Context"
    In GRW, collapse outcomes are **objectively random** and depend on the collapse mechanism—which is itself context-dependent. The collapse occurs in position basis, but what constitutes "position" in an interacting system depends on the physical setup.

**The mechanism:**

- GRW modifies the Schrödinger equation with stochastic collapse terms
- The collapse basis (position) is preferred
- But for interacting systems (e.g., during measurement), the effective "position" of pointer variables is determined by the apparatus setup
- Different measurement contexts couple the system to different pointer variables

**Compatibility with KS:**

GRW doesn't have hidden variables in the traditional sense—the randomness is fundamental. It is compatible with KS because it doesn't attempt noncontextual value assignments. The collapse outcomes are genuinely created, not revealed.

---

### Modal Interpretations

**Core claims:**

1. At any time, systems have definite values for some observables
2. Which observables have definite values is determined by the quantum state (via spectral decomposition)
3. The quantum state provides constraints on possible value assignments
4. Different versions (van Fraassen, Dieks, Vermaas-Dieks) differ in details

**How it handles contextuality:**

!!! info "Modal Interpretations and Context"
    Modal interpretations attempt to assign definite values to some observables while respecting quantum constraints. Contextuality appears in how the set of "definite" observables changes depending on the state and interactions.

**The mechanism:**

Consider the biorthogonal decomposition of an entangled state:
$$|\psi\rangle_{AB} = \sum_i c_i |a_i\rangle |b_i\rangle$$

Modal interpretations assign:
- System $A$ has a definite value from $\{|a_i\rangle\}$
- System $B$ has a definite value from $\{|b_i\rangle\}$
- Which observables are definite depends on the state

**Challenges:**

Modal interpretations have struggled with:
- The Kochen–Specker constraints (how to avoid contradictions)
- Dynamics of property ascription
- Treatment of degeneracies

**Compatibility with KS:**

Modal interpretations must be carefully constructed to avoid KS contradictions. They typically do this by:
- Not assigning values to all observables (only a "preferred" set)
- Allowing the preferred set to be context-dependent
- Accepting that not all observables have simultaneous values

---

### QBism (Quantum Bayesianism)

**Core claims:**

1. The quantum state represents an agent's beliefs, not objective reality
2. Probabilities are subjective (Bayesian), not physical propensities
3. Measurement outcomes are personal experiences of the agent
4. Quantum mechanics is a "user's manual" for navigating experience

**How it handles contextuality:**

!!! quote "QBist Contextuality"
    For QBism, contextuality is **radical and perspectival**. There are no hidden variables—not because the world lacks definite values, but because the quantum formalism is not about describing the world. It's about guiding an agent's expectations.

**The mechanism:**

In QBism:
- The quantum state is my state of belief
- A measurement is an action I take
- The outcome is a new experience that updates my beliefs
- Different measurement choices are different actions with different consequences

Contextuality is "built in" because the entire framework is agent-relative. There's no objective state that could be contextual or noncontextual—just the agent's evolving beliefs.

**Compatibility with KS:**

QBism is compatible with KS because it rejects the premise of hidden variables entirely. The KS theorem shows that if you try to assign agent-independent values to observables, you fail. QBism says: don't try. The values are not "out there" waiting to be found.

**Criticism:**

Critics argue QBism doesn't explain why agents' experiences are so tightly constrained by quantum mechanics, or how different agents come to agree on outcomes.

---

### Spekkens' Epistemic View

**Core claims:**

1. The quantum state represents incomplete knowledge of an underlying reality
2. Quantum phenomena arise from epistemic restrictions (what can be known)
3. A toy model demonstrates many "quantum" features arise this way
4. But quantum mechanics exhibits features (contextuality!) that go beyond the toy model

**How it handles contextuality:**

!!! important "Spekkens on Contextuality"
    Spekkens' approach makes contextuality the **central distinguishing feature** of quantum mechanics. His toy model (2007) shows that many "quantum" phenomena can be explained classically with epistemic restrictions. But the toy model is noncontextual. Contextuality is what makes quantum mechanics genuinely different.

**The mechanism:**

Spekkens' toy model:
- Has underlying "ontic states" (like hidden variables)
- Has "epistemic states" (what agents know)
- Reproduces superposition, entanglement, no-cloning, teleportation
- But it is explicitly noncontextual

Since quantum mechanics is contextual and the toy model is not, contextuality is precisely what the epistemic view cannot explain classically.

**Spekkens' generalized contextuality:**

Building on this, Spekkens developed the framework of generalized noncontextuality (see [Generalized Contextuality](../topics/generalized-contextuality-spekkens.md)), which extends contextuality beyond KS to:

- Preparation contextuality
- Transformation contextuality
- General measurement contextuality

**Compatibility with KS:**

Spekkens' framework *explains* KS contextuality as an instance of measurement contextuality. The framework also shows that quantum mechanics is contextual in ways that go beyond KS (preparation and transformation contextuality).

---

## Comparative Summary

| Interpretation | Hidden Variables? | How Contextuality Appears |
|----------------|-------------------|---------------------------|
| **Copenhagen** | No | Not applicable—no pre-existing values |
| **Bohmian mechanics** | Yes (positions) | Explicitly contextual |
| **Many-Worlds** | No | Basis-dependent branching |
| **GRW** | No | Collapse outcomes context-dependent |
| **Modal** | Partial | Which observables are definite is context-dependent |
| **QBism** | No | Radical agent-relative perspective |
| **Spekkens epistemic** | Possibly | Contextuality is the key non-classical feature |

---

## Influence on Later Developments

### Interpretation-Independent Contextuality

One important insight: **contextuality is interpretation-independent**. All interpretations must accommodate it, one way or another. This makes contextuality a robust, objective feature of quantum mechanics—not a matter of philosophical taste.

### Resource Theory

Understanding that contextuality is universal across interpretations helped motivate the view of contextuality as a **resource**. If every interpretation must deal with it, perhaps it's useful:

- Contextuality powers quantum computation
- Contextuality enables quantum advantages in communication
- Contextuality provides security in cryptography

### Experimental Tests

Interpretation debates sometimes seem untestable. But contextuality is testable:

- Contextuality inequalities can be violated in the lab
- These violations confirm quantum predictions
- They rule out certain interpretations (strict noncontextual hidden variables)

---

## Recommended References

- D. Bohm, "A Suggested Interpretation of the Quantum Theory in Terms of 'Hidden' Variables," *Physical Review* **85**, 166–193 (1952)
- H. Everett III, "'Relative State' Formulation of Quantum Mechanics," *Reviews of Modern Physics* **29**, 454–462 (1957)
- G. C. Ghirardi, A. Rimini, and T. Weber, "Unified dynamics for microscopic and macroscopic systems," *Physical Review D* **34**, 470–491 (1986)
- B. van Fraassen, *Quantum Mechanics: An Empiricist View*, Oxford University Press (1991)
- C. A. Fuchs, "QBism, the Perimeter of Quantum Bayesianism," arXiv:1003.5209 (2010)
- R. W. Spekkens, "Evidence for the epistemic view of quantum states: A toy theory," *Physical Review A* **75**, 032110 (2007)
- T. Norsen, *Foundations of Quantum Mechanics*, Springer (2017) — Comprehensive textbook on interpretations

---

## Cross-Links

- [Contextuality Basics](../topics/contextuality-basics.md) — Foundational concepts
- [Generalized Contextuality (Spekkens)](../topics/generalized-contextuality-spekkens.md) — Modern framework
- [The Kochen–Specker Theorem](kochen-specker.md) — The mathematical result interpretations must accommodate
- [Rob Spekkens](../people/rob-spekkens.md) — Developer of the epistemic view and generalized contextuality

---

## Glossary

**Copenhagen interpretation**
: The orthodox interpretation emphasizing measurement, complementarity, and the completeness of the quantum state.

**Pilot-wave theory (Bohmian mechanics)**
: Hidden-variable interpretation where particles have definite positions guided by the wave function.

**Many-worlds interpretation**
: Interpretation where all measurement outcomes occur in different branches of a universal wave function.

**Objective collapse theories**
: Theories (like GRW) where wave function collapse is a real physical process, not observer-induced.

**Modal interpretations**
: Family of interpretations assigning definite values to some observables based on the quantum state.

**QBism**
: Interpretation treating quantum states as subjective beliefs and probabilities as Bayesian.

**Epistemic interpretation**
: View that the quantum state represents knowledge about reality rather than reality itself.

---

!!! note "Why This Matters Today"
    The interpretation of quantum mechanics might seem like abstract philosophy, but it has practical implications. Understanding how contextuality fits into different interpretations helps clarify:

    - **What quantum computers are doing**: Are they exploring many branches? Exploiting contextual resources? Navigating belief updates?
    - **How to think about quantum foundations**: Contextuality as a robust feature, not an interpretation-dependent claim
    - **Where to look for new physics**: If contextuality is fundamental, perhaps violations would signal new physics

    The KS sets in this atlas ([Kernaghan 20](../ks-sets/kernaghan-20-4d.md), [Kernaghan–Peres 40](../ks-sets/kernaghan-peres-40-8d.md), [Cabello 18](../ks-sets/cabello-18-4d.md)) are interpretation-independent witnesses of contextuality. They demonstrate a feature that any interpretation—Copenhagen, Bohmian, Everettian, or otherwise—must account for.
