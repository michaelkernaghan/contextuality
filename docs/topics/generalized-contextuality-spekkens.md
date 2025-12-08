# Generalized Contextuality (Spekkens)

This page introduces Robert Spekkens' framework of **generalized noncontextuality**, which extends the notion of contextuality beyond projective measurements to arbitrary operational scenarios.

---

## Beyond Kochen–Specker

The traditional Kochen–Specker approach to contextuality focuses on **projective measurements** and the assignment of definite values to rays in Hilbert space. While powerful, this framework has limitations:

- It applies only to projective measurements (not POVMs or other generalized measurements)
- It deals with state-independent scenarios
- It does not naturally accommodate preparations and transformations

Spekkens' **generalized noncontextuality** framework addresses all these limitations by recasting contextuality in purely operational terms.

---

## The Operational Framework

### Operational Theories

An **operational theory** describes experiments in terms of:

- **Preparations** ($P$): Procedures that prepare a system in some state
- **Transformations** ($T$): Operations applied to the system
- **Measurements** ($M$): Procedures that yield outcomes

The theory specifies probabilities $p(k|P, T, M)$ for outcome $k$ given preparation $P$, transformation $T$, and measurement $M$.

### Ontological Models

An **ontological model** posits that:

1. The system has an underlying **ontic state** $\lambda$ from some space $\Lambda$
2. Preparations determine a probability distribution $\mu(\lambda|P)$ over ontic states
3. Measurements determine response functions $\xi(k|\lambda, M)$ giving outcome probabilities
4. The operational probabilities arise from averaging over $\lambda$:

$$p(k|P, M) = \int_\Lambda \xi(k|\lambda, M) \, \mu(\lambda|P) \, d\lambda$$

---

## Operational Equivalences

The key insight is that operationally **indistinguishable** procedures might be realized differently in the laboratory.

### Preparation Equivalence

Two preparations $P_1$ and $P_2$ are **operationally equivalent** if they yield the same outcome probabilities for all measurements:

$$p(k|P_1, M) = p(k|P_2, M) \quad \forall k, M$$

Even though $P_1$ and $P_2$ may differ in their physical implementation, they are indistinguishable from the operational perspective.

### Measurement Equivalence

Two measurements $M_1$ and $M_2$ (or specific effects within them) are **operationally equivalent** if they yield the same statistics for all preparations:

$$p(k|P, M_1) = p(k|P, M_2) \quad \forall k, P$$

### Transformation Equivalence

Similarly, transformations $T_1$ and $T_2$ are operationally equivalent if they produce indistinguishable input-output behavior.

---

## Generalized Noncontextuality

Spekkens' principle of **generalized noncontextuality** demands that operational equivalences be reflected in the ontological model:

!!! definition "Generalized Noncontextuality"
    An ontological model is **noncontextual** if:

    - **Preparation noncontextuality**: Operationally equivalent preparations are represented by the same distribution over ontic states.
    - **Measurement noncontextuality**: Operationally equivalent measurements are represented by the same response functions.
    - **Transformation noncontextuality**: Operationally equivalent transformations are represented by the same stochastic maps on ontic states.

In symbols:

- If $P_1 \sim P_2$ operationally, then $\mu(\lambda|P_1) = \mu(\lambda|P_2)$
- If $M_1 \sim M_2$ operationally, then $\xi(k|\lambda, M_1) = \xi(k|\lambda, M_2)$

---

## Types of Contextuality

The generalized framework identifies distinct **types** of contextuality:

### Preparation Contextuality

A theory exhibits **preparation contextuality** if operationally equivalent preparations must be represented by different distributions over ontic states.

Example: In quantum mechanics, the completely mixed state $\rho = I/d$ can be prepared by mixing any orthonormal basis with equal weights. These different decompositions are operationally equivalent but cannot all be represented by the same ontic distribution in a noncontextual model.

### Measurement Contextuality

A theory exhibits **measurement contextuality** if operationally equivalent measurements cannot be represented by identical response functions.

This generalizes the traditional KS notion: different contexts for the same projector are operationally equivalent ways to measure that projector.

### Transformation Contextuality

A theory exhibits **transformation contextuality** if operationally equivalent transformations cannot be represented by the same ontic evolution.

---

## The Leibniz Principle

Spekkens' noncontextuality can be understood as an **ontological Leibniz principle**:

> If two things are operationally indistinguishable, they should be ontologically identical.

This is a principle of **parsimony**: the hidden-variable model should not contain structure that is invisible at the operational level.

Quantum mechanics violates this principle—it is contextual precisely because operational equivalences hide ontological distinctions.

---

## Quasiprobability Representations

A remarkable connection exists between contextuality and **negativity in quasiprobability representations**.

### Wigner Function

The Wigner function $W(q, p)$ is a quasiprobability distribution that can represent quantum states in phase space. For many states, $W$ takes negative values—a signature of non-classicality.

### Spekkens' Result

Spekkens showed that:

!!! theorem "Negativity-Contextuality Equivalence"
    A theory admits a noncontextual ontological model if and only if it admits a non-negative quasiprobability representation.

Equivalently:

- **Noncontextual** ⟺ Non-negative quasiprobabilities possible
- **Contextual** ⟺ Negativity in any quasiprobability representation

This connects an abstract property (contextuality) to a concrete, quantifiable feature (Wigner negativity).

---

## Contextuality Inequalities

The generalized framework enables the derivation of **noncontextuality inequalities**—constraints on operational statistics that must be satisfied by any noncontextual model.

### Structure of Inequalities

A noncontextuality inequality has the form:

$$\sum_i c_i \, p(k_i | P_i, M_i) \leq B_{NC}$$

where $B_{NC}$ is the noncontextual bound. Quantum mechanics can violate these inequalities, demonstrating contextuality.

### Advantages Over KS

- Apply to **any** operational scenario (not just projective measurements)
- Can witness **state-dependent** contextuality
- Enable **experimental tests** with realistic measurements

---

## Experimental Implications

The generalized framework has made contextuality **experimentally accessible**:

### Prepare-and-Measure Scenarios

Simple prepare-and-measure experiments (no entanglement required) can demonstrate contextuality:

1. Prepare states using operationally equivalent procedures
2. Perform measurements with operationally equivalent effects
3. Observe violation of noncontextuality inequalities

### Robustness to Noise

Unlike KS proofs (which require exact orthogonality), generalized contextuality inequalities:

- Are robust to experimental imperfections
- Have statistical significance testable with finite data
- Apply to noisy, realistic quantum systems

---

## Connection to KS Contextuality

The generalized framework **subsumes** traditional KS contextuality:

- KS contextuality arises from measurement noncontextuality applied to projective measurements
- The projector $|v\rangle\langle v|$ in different bases represents operationally equivalent measurements
- Assigning the same response function to all contexts would require consistent 0-1 assignments—impossible for KS sets

But generalized contextuality is **broader**: it captures scenarios beyond KS, including preparation contextuality, which has no traditional KS analog.

---

## Applications

Generalized contextuality has found applications in:

### Quantum Information

- **Parity-oblivious multiplexing**: Quantum advantage linked to contextuality
- **State discrimination**: Contextuality advantages for certain tasks
- **Cryptography**: Security proofs based on contextuality

### Foundations

- **Classifying quantum phenomena**: Contextuality as a unifying concept
- **Toy models**: Spekkens' toy model as a noncontextual reference
- **Quantum reconstruction**: Contextuality as a core feature

### Computation

- **Magic states**: Preparation contextuality relates to magic state resource theory
- **MBQC**: Measurement contextuality underlies computational power

---

## References

- R. W. Spekkens, "Contextuality for preparations, transformations, and unsharp measurements," *Phys. Rev. A* **71**, 052108 (2005)
- R. W. Spekkens, "Negativity and contextuality are equivalent notions of nonclassicality," *Phys. Rev. Lett.* **101**, 020401 (2008)
- M. D. Mazurek, M. F. Pusey, R. Kunjwal, K. J. Resch, and R. W. Spekkens, "An experimental test of noncontextuality without unphysical idealizations," *Nat. Commun.* **7**, 11780 (2016)
- R. Kunjwal and R. W. Spekkens, "From the Kochen-Specker theorem to noncontextuality inequalities without assuming determinism," *Phys. Rev. Lett.* **115**, 110403 (2015)
