# Kernaghan–Peres 40-Vector Kochen–Specker Set (8D)

## Basic Metadata

| Property | Value |
|----------|-------|
| **Name** | Kernaghan–Peres 40-Vector KS Set |
| **Dimension** | 8 (three-qubit Hilbert space) |
| **Number of Rays** | 40 |
| **Type** | State-independent KS set |
| **Authors** | Michael Kernaghan & Asher Peres |
| **Year** | 1995 |
| **Original Reference** | M. Kernaghan and A. Peres, "Kochen–Specker theorem for eight-dimensional space," *Phys. Lett. A* **198**, 1 (1995) |

---

## Overview

The **Kernaghan–Peres 40-vector set** is a remarkably efficient KS construction in 8-dimensional Hilbert space—the state space of three qubits. With only 40 rays, it achieves an exceptional **vector-to-dimension ratio** of 5:1, making it one of the most compact KS sets known relative to its dimension.

This construction has deep connections to:

- **GHZ-type paradoxes**: The structure relates to Greenberger–Horne–Zeilinger correlations in three-qubit systems
- **Pauli group**: The rays can be constructed from eigenstates of Pauli operators
- **Mermin-style arguments**: The proof is connected to parity-based contextuality arguments

The set demonstrates that increasing dimension does not necessarily require proportionally more vectors for a KS proof.

---

## Construction

The 40 rays live in $\mathbb{C}^8$, the Hilbert space of a three-qubit system. The construction exploits the structure of the **Pauli group** on three qubits and the **Mermin square/star** type arguments.

The explicit vector coordinates are provided in: [`data/kernaghan-peres-40-8d-vectors.csv`](../data/kernaghan-peres-40-8d-vectors.csv)

### Construction Approach

The vectors can be understood as joint eigenstates of commuting sets of Pauli operators on three qubits. For example:

- Operators like $X \otimes X \otimes X$, $Z \otimes Z \otimes I$, $I \otimes Z \otimes Z$, etc.
- Each commuting set of operators defines an orthonormal basis of common eigenstates
- The 40 rays are selected from these eigenstates with specific overlap properties

### Sample Vectors

| Label | Vector (unnormalized, 8 components) |
|-------|-------------------------------------|
| v1 | (placeholder) |
| v2 | (placeholder) |
| v3 | (placeholder) |
| ... | ... |
| v40 | (placeholder) |

!!! note "Vector Data"
    Complete coordinates will be added to the CSV file. The vectors typically have entries from $\{0, \pm 1, \pm i\}/\sqrt{2}$ or similar simple forms due to their Pauli-eigenstate origin.

---

## Orthogonality Structure

The 40 rays are organized into orthonormal bases (complete sets of 8 mutually orthogonal rays). The number of bases and their overlap pattern creates the KS contradiction.

### Basis Structure

- **Number of bases**: The rays form a specific number of complete 8-ray bases
- **Ray reuse**: Each ray appears in multiple bases
- **Critical overlaps**: The pattern of shared rays between bases prevents consistent value assignment

Example bases (placeholders):

- **B1**: {v1, v2, v3, v4, v5, v6, v7, v8}
- **B2**: {v9, v10, v11, v12, v13, v14, v15, v16}
- **B3**: {v1, v9, v17, v18, v19, v20, v21, v22}
- ...

!!! info "Hypergraph Representation"
    The hypergraph for this set has:

    - **40 vertices** (one per ray)
    - **Hyperedges of size 8** (one per orthonormal basis)

    The KS property is equivalent to the impossibility of 0-1 coloring the vertices such that each hyperedge has exactly one vertex colored 1.

---

## KS Contradiction

The KS argument in 8D follows the same logic as in 4D:

1. **Assumption**: Assign $v(r) \in \{0, 1\}$ to each of the 40 rays, with exactly one ray per basis receiving the value 1.

2. **Parity constraints**: The construction incorporates parity constraints inherited from the Mermin-style argument. Products of certain operators must yield specific values, which translates to parity constraints on the 0-1 assignments.

3. **Contradiction**: The parity constraints are mutually inconsistent. The structure of the 40 vectors and their bases is designed so that satisfying the constraints on some bases necessarily violates others.

This contradiction can be understood as a "proof by parity"—similar to how the GHZ paradox yields a contradiction through incompatible parity requirements.

---

## Connection to GHZ Paradox

The Kernaghan–Peres construction is intimately related to the **Greenberger–Horne–Zeilinger (GHZ) paradox**:

- The **GHZ state** $|GHZ\rangle = \frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$ exhibits perfect correlations under certain Pauli measurements
- These correlations cannot be explained by local hidden variables (or noncontextual models)
- The 40-vector KS set "geometrizes" this algebraic paradox into a finite set of rays

The set can be viewed as revealing the **state-independent contextual structure** underlying the GHZ phenomenon.

---

## Relation to Other KS Sets

- **Mermin's Constructions**: Mermin developed elegant "magic square" and "magic star" proofs in 4D and 8D. The Kernaghan–Peres set is related to these but achieves a different optimization.

- **Kernaghan 20 (4D)**: The 4D construction by Kernaghan used a different approach. The 8D collaboration with Peres exploited the richer structure available in three-qubit space.

- **Larger Pauli-based Sets**: Other constructions use more vectors from the Pauli eigenstates. The Kernaghan–Peres set is optimized for minimality.

---

## Role in Contextuality Resource Theory

The 40-vector set has special significance for contextuality as a resource in quantum computation:

### Three-Qubit Contextuality Witness

The set provides a powerful **state-independent contextuality witness** for three-qubit systems. Any quantum state in $\mathbb{C}^8$ exhibits contextuality when probed with measurements derived from this construction.

### Stabilizer Formalism Connection

The rays are closely related to **stabilizer states**—states that are eigenstates of Pauli operators. The KS construction reveals the hidden contextual structure within the stabilizer formalism:

- Stabilizer operations alone are classically simulable (Gottesman–Knill)
- But the underlying measurement structure already contains contextuality
- Adding non-stabilizer ("magic") states activates this contextuality for computation

### MBQC and Computational Contextuality

In **measurement-based quantum computation (MBQC)**:

- Computation proceeds by adaptive measurements on entangled resource states
- The power of MBQC requires contextual measurement scenarios
- The Kernaghan–Peres 40-vector structure can be seen as part of the **contextuality backbone** underlying MBQC on three-qubit systems

The set demonstrates that even before adding magic states, the measurement scenarios on multi-qubit systems contain a rich contextual structure that can be harnessed for computation.

### Magic States and Contextuality

Following Howard et al. (2014), contextuality is a necessary resource for quantum speedup in qudit systems. The Kernaghan–Peres set:

- Defines measurement contexts in three-qubit space
- Provides the "background contextuality" against which magic states become computationally useful
- Can be used to formulate and test contextuality inequalities for three-qubit magic state distillation

---

## References

- M. Kernaghan and A. Peres, "Kochen–Specker theorem for eight-dimensional space," *Phys. Lett. A* **198**, 1 (1995)
- D. M. Greenberger, M. A. Horne, and A. Zeilinger, "Going beyond Bell's theorem," in *Bell's Theorem, Quantum Theory, and Conceptions of the Universe*, Kluwer (1989)
- N. D. Mermin, "Hidden variables and the two theorems of John Bell," *Rev. Mod. Phys.* **65**, 803 (1993)
- M. Howard, J. Wallman, V. Veitch, and J. Emerson, "Contextuality supplies the 'magic' for quantum computation," *Nature* **510**, 351 (2014)
- R. Raussendorf, "Contextuality in measurement-based quantum computation," *Phys. Rev. A* **88**, 022322 (2013)
