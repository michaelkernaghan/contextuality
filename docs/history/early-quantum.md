# Early Quantum Theory (1900–1930)

The foundations of quantum mechanics were laid in the first three decades of the twentieth century. Although the term "contextuality" would not appear until much later, the conceptual seeds were planted during this period—particularly in debates about the nature of measurement, the role of the observer, and whether quantum systems possess definite properties prior to observation.

---

## Historical Background

### The Old Quantum Theory (1900–1924)

The quantum revolution began not with philosophical puzzles about measurement but with practical problems in physics:

**1900 – Planck's quantum hypothesis**
: Max Planck introduced energy quantization ($E = h\nu$) to explain black-body radiation. This was initially a mathematical device, not a claim about the nature of reality.

**1905 – Einstein's light quanta**
: Einstein proposed that light itself comes in discrete packets (photons), explaining the photoelectric effect. This suggested quantization was more than a calculational trick.

**1913 – Bohr's atomic model**
: Niels Bohr introduced stationary states for electrons in atoms, with "quantum jumps" between them. The question of what happens *during* a quantum jump—and what causes it—was already troubling.

**1922–1924 – The Stern–Gerlach experiment**
: Spatial quantization of angular momentum was demonstrated. A silver atom's spin is found to be either "up" or "down" along any chosen axis—but the axis is chosen by the experimenter. This proto-contextual feature would become central.

### The New Quantum Mechanics (1925–1927)

The modern theory emerged rapidly:

**1925 – Heisenberg's matrix mechanics**
: Werner Heisenberg developed a formalism using matrices of observable quantities. Crucially, these matrices generally do not commute: $\hat{x}\hat{p} \neq \hat{p}\hat{x}$.

**1926 – Schrödinger's wave mechanics**
: Erwin Schrödinger introduced the wave function $\psi$ and his famous equation. The question immediately arose: what does $\psi$ represent?

**1926 – Born's probability interpretation**
: Max Born proposed that $|\psi|^2$ gives the probability density for finding a particle at a given location. Probability entered fundamental physics.

**1927 – Heisenberg's uncertainty principle**
: Heisenberg showed that position and momentum cannot both be precisely defined: $\Delta x \cdot \Delta p \geq \hbar/2$. This was often interpreted as measurement disturbance—measuring one quantity disturbs the other.

---

## Key Figures and Ideas

### Niels Bohr and Complementarity

Bohr developed the philosophical framework that would dominate quantum mechanics for decades. His key contribution was the principle of **complementarity**:

!!! quote "Bohr's Complementarity"
    Quantum systems exhibit mutually exclusive properties (e.g., wave-like and particle-like behavior) depending on the experimental arrangement. A complete description requires considering all complementary aspects, but they cannot be observed simultaneously.

**Proto-contextual elements:**

1. **Dependence on experimental arrangement**: For Bohr, the experimental setup is not merely a passive revealer of pre-existing properties—it actively participates in defining what properties can be meaningfully discussed.

2. **Wholeness of the phenomenon**: Bohr insisted that the quantum "phenomenon" includes both the system and the measuring apparatus. You cannot speak of the system in isolation.

3. **Classical language**: Measurement results must be described in classical terms, but which classical concepts apply depends on the measurement context.

Bohr never used the word "contextuality," but his insistence that the experimental context shapes what can be said about the system is recognizably contextual in spirit.

### Werner Heisenberg and Measurement Disturbance

Heisenberg initially interpreted the uncertainty principle in terms of **measurement disturbance**:

!!! quote "Heisenberg's Gamma-Ray Microscope"
    To measure an electron's position precisely, we must use short-wavelength (high-energy) photons. But these photons disturb the electron's momentum. Precise position measurement necessarily disturbs momentum.

**Implications for contextuality:**

- If measuring one observable disturbs others, then the outcome of measuring $A$ might depend on whether we also measure $B$.
- This suggests that measurement outcomes are not simply revealing pre-existing values.

However, the disturbance picture is incomplete. The uncertainty principle is not merely about practical disturbance—it's a fundamental feature of the quantum state. Later work (especially Kochen–Specker) would show that the problem runs deeper than disturbance.

### Erwin Schrödinger and the Measurement Problem

Schrödinger was troubled by the role of measurement in quantum mechanics. His famous **cat paradox** (1935) highlighted the measurement problem:

- Before measurement, the wave function describes superpositions of macroscopically distinct states.
- After measurement, we observe definite outcomes.
- What causes the "collapse"?

This problem is intimately related to contextuality: if the quantum state does not determine definite outcomes, and measurement produces definite outcomes, then the measurement context must play a role.

### John von Neumann's Mathematical Foundations

In 1932, von Neumann published *Mathematische Grundlagen der Quantenmechanik*, which:

1. Provided rigorous Hilbert space foundations for quantum mechanics
2. Distinguished "Type I" processes (unitary evolution) from "Type II" processes (measurement collapse)
3. Included an **impossibility proof** for hidden variables

**Von Neumann's no-hidden-variables theorem:**

Von Neumann argued that no hidden-variable theory could reproduce quantum predictions while satisfying certain "natural" assumptions. His key assumption (later criticized) was that the expectation value of a sum of observables equals the sum of expectation values—even for incompatible observables.

!!! warning "Limitations of von Neumann's Proof"
    Von Neumann's proof assumed that the hidden-variable theory must assign expectation values linearly to *all* observables, including incompatible ones. This is an unreasonably strong assumption. Bell (1966) later pointed out that no physical theory should be expected to satisfy this for non-commuting observables.

Nevertheless, von Neumann's work established the framework within which contextuality would later be formulated: observables as operators, incompatibility as non-commutativity, and the question of value assignments.

---

## How This Relates to Contextuality

The period 1900–1932 established several features that contextuality would later formalize:

### 1. Incompatibility of Observables

Non-commuting observables cannot be simultaneously measured. This creates the structure of "contexts"—sets of compatible measurements. The mathematical apparatus of Hilbert spaces, commutators, and projection operators was in place by 1932.

### 2. The Role of Measurement

Measurement in quantum mechanics is not passive observation. The Copenhagen interpretation emphasized that measurement produces outcomes, not reveals them. This is a contextual stance, even if not yet called that.

### 3. The Question of Hidden Variables

Von Neumann's impossibility proof raised the question: can quantum indeterminacy be explained by hidden variables? His proof suggested no, but for the wrong reasons. The correct answer—that hidden variables must be contextual—would come later.

### 4. Complementarity as Proto-Contextuality

Bohr's complementarity contains the essential contextual insight: what can be said about a quantum system depends on the experimental arrangement. Different arrangements (contexts) reveal different aspects.

---

## Influence on Later Developments

The conceptual foundations laid in this period directly influenced:

**EPR (1935)**
: Einstein, Podolsky, and Rosen challenged the completeness of quantum mechanics, forcing a sharper formulation of what "elements of reality" meant. → [See: EPR, Bohm, and Measurement](epr-bohm.md)

**Bohm (1952)**
: David Bohm constructed an explicit hidden-variable theory, showing von Neumann's proof had loopholes. His theory is explicitly contextual.

**Bell (1964, 1966)**
: John Bell clarified what was wrong with von Neumann's proof and derived his famous inequalities. Bell's theorem establishes nonlocality; the Kochen–Specker theorem (1967) establishes contextuality.

**Kochen–Specker (1967)**
: Kochen and Specker gave the definitive no-go theorem for noncontextual hidden variables. → [See: The Kochen–Specker Theorem](kochen-specker.md)

---

## Recommended References

- N. Bohr, "The Quantum Postulate and the Recent Development of Atomic Theory," *Nature* **121**, 580–590 (1928)
- W. Heisenberg, "Über den anschaulichen Inhalt der quantentheoretischen Kinematik und Mechanik," *Zeitschrift für Physik* **43**, 172–198 (1927)
- J. von Neumann, *Mathematische Grundlagen der Quantenmechanik*, Springer (1932); English translation: *Mathematical Foundations of Quantum Mechanics*, Princeton University Press (1955)
- M. Jammer, *The Philosophy of Quantum Mechanics*, Wiley (1974) — Comprehensive historical survey
- J. S. Bell, "On the Problem of Hidden Variables in Quantum Mechanics," *Reviews of Modern Physics* **38**, 447–452 (1966) — Critique of von Neumann

---

## Cross-Links

- [Contextuality Basics](../topics/contextuality-basics.md) — Modern formulation of contextuality
- [EPR, Bohm, and Measurement](epr-bohm.md) — The next chapter in the history
- [The Kochen–Specker Theorem](kochen-specker.md) — Contextuality formalized
- [Asher Peres](../people/asher-peres.md) — Later contributor who built on these foundations

---

## Glossary

**Complementarity**
: Bohr's principle that mutually exclusive experimental arrangements reveal mutually exclusive properties of quantum systems.

**Uncertainty principle**
: Heisenberg's result that conjugate variables (like position and momentum) cannot both be precisely determined.

**Measurement disturbance**
: The idea that measuring one observable physically disturbs the values of incompatible observables.

**Hidden variables**
: Hypothetical additional parameters that would make quantum mechanics deterministic.

**Non-commutativity**
: The property that the order of operations matters: $\hat{A}\hat{B} \neq \hat{B}\hat{A}$ for incompatible observables.

---

!!! note "Why This Matters Today"
    The conceptual struggles of the 1920s are not merely historical curiosities. Bohr's emphasis on experimental context, Heisenberg's measurement disturbance, and von Neumann's mathematical framework remain directly relevant. When we construct KS sets like Kernaghan's 20-vector set, we are working within the Hilbert space formalism von Neumann established, addressing questions Bohr raised, using the mathematical tools Heisenberg and Schrödinger created. The modern understanding of contextuality as a computational resource (see [Contextuality & Quantum Computation](../topics/contextuality-and-quantum-computation.md)) is a direct descendant of these foundational debates.
