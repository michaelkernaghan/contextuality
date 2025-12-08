# EPR, Bohm, and Measurement (1930–1960)

The three decades following the establishment of quantum mechanics saw intense debate about what the theory actually means. The key developments during this period—the EPR argument, Bohm's hidden-variable theory, and the emerging understanding of measurement—set the stage for the Kochen–Specker theorem and the explicit formulation of contextuality.

---

## Historical Background

### The Completeness Question

By the early 1930s, the mathematical framework of quantum mechanics was well established. The interpretive questions remained:

- Is the quantum state $\psi$ a complete description of physical reality?
- Can the apparent randomness of quantum mechanics be explained by hidden variables?
- What happens during measurement?

The EPR paper of 1935 crystallized these questions into a sharp argument.

---

## The EPR Argument (1935)

### Einstein, Podolsky, and Rosen

In May 1935, Albert Einstein, Boris Podolsky, and Nathan Rosen published "Can Quantum-Mechanical Description of Physical Reality Be Considered Complete?" This paper remains one of the most influential in the foundations of physics.

**The EPR criterion of reality:**

!!! quote "EPR Reality Criterion"
    "If, without in any way disturbing a system, we can predict with certainty (i.e., with probability equal to unity) the value of a physical quantity, then there exists an element of physical reality corresponding to this physical quantity."

**The argument:**

1. Consider two particles (originally position-momentum entangled) that have interacted and then separated.

2. By measuring particle 1, we can predict with certainty properties of particle 2 without disturbing it (since they're spatially separated).

3. By EPR's reality criterion, particle 2 must have had those properties all along.

4. But we can choose to measure either position or momentum on particle 1, allowing us to predict either property of particle 2.

5. If both position and momentum of particle 2 are "elements of reality," then quantum mechanics (which cannot simultaneously assign definite values to both) is incomplete.

**The implicit contextuality:**

EPR assumed that the properties of particle 2 are independent of what we choose to measure on particle 1. This is a **noncontextuality assumption** (specifically, a locality assumption—if the particles are spacelike separated, measuring one should not affect the other).

Bohr's response to EPR emphasized that the experimental arrangement as a whole defines what can be meaningfully said—a contextual reply, though not using that term.

---

## David Bohm's Contributions

### The Spin Version of EPR (1951)

In his 1951 textbook *Quantum Theory*, David Bohm reformulated the EPR argument using spin-½ particles rather than continuous variables. This version is conceptually cleaner and became the standard form:

**The Bohm–EPR setup:**

1. Two spin-½ particles are prepared in the singlet state:
   $$|\psi\rangle = \frac{1}{\sqrt{2}}(|\uparrow\downarrow\rangle - |\downarrow\uparrow\rangle)$$

2. The particles separate. Measuring spin along any axis on particle 1 allows perfect prediction of spin along the same axis on particle 2.

3. But we can choose different measurement axes.

4. If the outcomes are predetermined, particle 2 must have definite spin values for all axes simultaneously—which contradicts quantum mechanics.

This formulation made the EPR puzzle more tractable and directly connected to later contextuality arguments.

### Bohm's Pilot-Wave Theory (1952)

In 1952, Bohm published two papers presenting an explicit hidden-variable interpretation of quantum mechanics. This was revolutionary: it showed that von Neumann's impossibility proof had loopholes.

**Key features of Bohmian mechanics:**

1. **Particles have definite positions at all times.** The "hidden variable" is the particle's actual position $\mathbf{q}(t)$.

2. **The wave function guides particle motion.** The velocity is determined by:
   $$\mathbf{v} = \frac{\hbar}{m} \text{Im}\left(\frac{\nabla\psi}{\psi}\right)$$

3. **Quantum statistics emerge from ignorance.** If initial positions are distributed according to $|\psi|^2$, this distribution is preserved and reproduces all quantum predictions.

**Contextuality in Bohm's theory:**

!!! important "Bohmian Contextuality"
    Bohm's theory is deterministic but **explicitly contextual**. The outcome of a measurement depends not just on the hidden variable (particle position) but also on the measurement apparatus and its wave function. The same particle position can yield different outcomes depending on what else is measured.

This was a crucial insight: hidden variables are possible, but they must be contextual. Bohm's theory achieves determinism at the cost of contextuality (and nonlocality).

### Bohm–Aharonov (1957)

In 1957, Bohm and Yakir Aharonov revisited the EPR argument, clarifying the relationship between quantum mechanics and hidden variables. They showed:

- The EPR correlations are real and measurable
- Any hidden-variable theory reproducing them must be nonlocal
- The measurement interaction plays an essential role

This work anticipated Bell's theorem by several years.

---

## Key Figures and Ideas

### John Bell's Critique of von Neumann (1966)

Although Bell's famous inequality paper is from 1964, his critique of von Neumann's impossibility proof (published 1966, written earlier) is crucial for understanding contextuality.

**Bell's observation:**

Von Neumann assumed that hidden-variable theories must assign expectation values linearly to all observables:
$$\langle A + B \rangle_\lambda = \langle A \rangle_\lambda + \langle B \rangle_\lambda$$

even for non-commuting $A$ and $B$.

Bell pointed out that this is unreasonable. For incompatible observables, there's no physical reason to expect additivity—they cannot be measured together, so their "sum" has no operational meaning.

!!! quote "Bell on von Neumann"
    "The additivity of expectation values... is a quite peculiar property of quantum mechanical states, not to be expected a priori... There is no reason to demand it individually of the hypothetical dispersion-free states."

**Implications:**

- Von Neumann's proof does not rule out hidden variables
- Bohm's theory (which violates von Neumann's additivity for incompatible observables) is a valid counterexample
- The real constraint on hidden variables is contextuality (Kochen–Specker) and nonlocality (Bell), not von Neumann's additivity

### Gleason's Theorem (1957)

Andrew Gleason proved a remarkable mathematical theorem about measures on Hilbert space:

!!! theorem "Gleason's Theorem"
    In a Hilbert space of dimension ≥ 3, any measure on closed subspaces that is countably additive must be given by a density operator via the trace rule:
    $$\mu(P) = \text{tr}(\rho P)$$

**Implications for hidden variables:**

Gleason's theorem implies that if you want to assign probabilities to projectors in a way that respects quantum structure, you must use the standard quantum rule. This severely constrains hidden-variable theories and is closely related to the Kochen–Specker theorem (which can be seen as a constructive, finite version of Gleason's result).

---

## How This Relates to Contextuality

### The Road to Kochen–Specker

The period 1935–1960 established several key points:

1. **Hidden variables are not ruled out by von Neumann** (Bell's critique)

2. **Hidden variables are possible** (Bohm's theory exists)

3. **Hidden variables must be contextual** (Bohm's theory is)

4. **Hidden variables must be nonlocal** (EPR + Bohm)

5. **Probability assignments are constrained** (Gleason's theorem)

What remained was to formulate precisely what "contextuality" means and prove it is unavoidable. This was achieved by Kochen and Specker in 1967.

### The Contextual Structure Emerges

Several elements of contextuality were implicit in this period:

| Concept | Pre-1967 Form | Post-KS Form |
|---------|---------------|--------------|
| Measurement context | EPR: choice of what to measure on distant particle | KS: set of compatible observables |
| Value assignment | Bohm: particle position determines outcome | KS: assignment of 0/1 to rays |
| Constraint | Gleason: probability measure structure | KS: exactly one "1" per orthonormal basis |
| Impossibility | von Neumann (flawed), EPR (locality) | KS theorem: noncontextual assignment impossible |

---

## Influence on Later Developments

### Bell's Theorem (1964)

Bell derived inequalities that local hidden-variable theories must satisfy. Quantum mechanics violates these inequalities. This establishes that:

- Quantum correlations cannot be explained by local hidden variables
- Any hidden-variable theory must be nonlocal

Bell nonlocality is related to but distinct from KS contextuality:

| Bell Nonlocality | KS Contextuality |
|------------------|------------------|
| Spatially separated measurements | Measurements on single system |
| Requires entanglement | State-independent |
| Statistical (inequalities) | Logical (impossibility proof) |

Both can be seen as instances of the impossibility of noncontextual explanations.

### Kochen–Specker (1967)

Building on Gleason, Bell's critique, and Bohm's example, Kochen and Specker proved:

- No noncontextual value assignment exists in $d \geq 3$
- This holds even for a finite set of rays (their original set had 117 rays in 3D)

→ [See: The Kochen–Specker Theorem](kochen-specker.md)

---

## Recommended References

- A. Einstein, B. Podolsky, and N. Rosen, "Can Quantum-Mechanical Description of Physical Reality Be Considered Complete?" *Physical Review* **47**, 777–780 (1935)
- N. Bohr, "Can Quantum-Mechanical Description of Physical Reality Be Considered Complete?" *Physical Review* **48**, 696–702 (1935) — Bohr's reply to EPR
- D. Bohm, *Quantum Theory*, Prentice-Hall (1951) — Spin version of EPR
- D. Bohm, "A Suggested Interpretation of the Quantum Theory in Terms of 'Hidden' Variables, I and II," *Physical Review* **85**, 166–193 (1952)
- D. Bohm and Y. Aharonov, "Discussion of Experimental Proof for the Paradox of Einstein, Rosen, and Podolsky," *Physical Review* **108**, 1070–1076 (1957)
- J. S. Bell, "On the Problem of Hidden Variables in Quantum Mechanics," *Reviews of Modern Physics* **38**, 447–452 (1966)
- A. M. Gleason, "Measures on the Closed Subspaces of a Hilbert Space," *Journal of Mathematics and Mechanics* **6**, 885–893 (1957)

---

## Cross-Links

- [Early Quantum Theory (1900–1930)](early-quantum.md) — The previous chapter
- [The Kochen–Specker Theorem (1967)](kochen-specker.md) — The formalization of contextuality
- [Contextuality Basics](../topics/contextuality-basics.md) — Modern conceptual treatment
- [Asher Peres](../people/asher-peres.md) — Later work building on Bohm and Bell

---

## Glossary

**EPR paradox**
: The argument by Einstein, Podolsky, and Rosen that quantum mechanics is incomplete because it cannot assign simultaneous reality to incompatible observables of entangled particles.

**Singlet state**
: The maximally entangled spin state $\frac{1}{\sqrt{2}}(|\uparrow\downarrow\rangle - |\downarrow\uparrow\rangle)$, central to EPR-Bohm scenarios.

**Pilot-wave theory (Bohmian mechanics)**
: Bohm's deterministic interpretation of quantum mechanics, where particles have definite positions guided by the wave function.

**Gleason's theorem**
: The mathematical result that probability measures on Hilbert space projectors must be given by density operators.

**Nonlocality**
: The property that correlations between spatially separated measurements cannot be explained by local hidden variables.

---

!!! note "Why This Matters Today"
    The EPR-Bohm period established that hidden variables are possible but constrained. Bohm's theory showed that contextuality is the price of determinism. Bell's work disentangled the flawed von Neumann proof from the genuine constraints (contextuality and nonlocality). This conceptual clarification was essential for understanding what makes quantum mechanics truly non-classical. The KS sets in this atlas—including the [Kernaghan–Peres 40-vector set](../ks-sets/kernaghan-peres-40-8d.md), which connects to GHZ-EPR type scenarios—are direct descendants of this work.
