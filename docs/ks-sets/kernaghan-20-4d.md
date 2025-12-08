# Kernaghan 20-Vector Kochen–Specker Set (4D)

## Basic Metadata

| Property | Value |
|----------|-------|
| **Name** | Kernaghan 20-Vector KS Set |
| **Dimension** | 4 (two-qubit Hilbert space) |
| **Number of Rays** | 20 |
| **Type** | State-independent KS set |
| **Author** | Michael Kernaghan |
| **Year** | 1994 |
| **Original Reference** | M. Kernaghan, "Bell–Kochen–Specker theorem for 20 vectors," *J. Phys. A: Math. Gen.* **27**, L829 (1994) |

---

## Overview

The **Kernaghan 20-vector set** was the first KS construction to achieve exactly 20 rays in 4-dimensional Hilbert space. Prior to this work, KS proofs in 4D required significantly more vectors. This construction demonstrated that compact, symmetric KS sets could be found in the two-qubit Hilbert space.

The set is historically significant as a precursor to Cabello's later 18-vector minimal KS set, which refined Kernaghan's construction. The 20-vector set remains important for its elegant structure and its role in developing contextuality witnesses for 2-qubit systems.

Key features:

- **Compact**: Only 20 rays needed for a complete KS contradiction
- **Symmetric**: The construction possesses a high degree of symmetry
- **Foundational**: Served as the basis for subsequent minimal constructions

---

## Construction

The 20 rays of this KS set live in $\mathbb{C}^4$, the Hilbert space of a two-qubit system. Each ray is specified by a 4-component vector (up to normalization and overall phase).

The explicit vector coordinates are provided in the data file: [`data/kernaghan-20-4d-vectors.csv`](../data/kernaghan-20-4d-vectors.csv)

### Sample Vectors

| Label | Vector (unnormalized) |
|-------|----------------------|
| v1 | (placeholder) |
| v2 | (placeholder) |
| v3 | (placeholder) |
| v4 | (placeholder) |
| ... | ... |
| v20 | (placeholder) |

!!! note "Vector Data"
    The complete vector coordinates will be added to the CSV file. Vectors are typically expressed with integer or simple algebraic entries for computational convenience.

---

## Orthogonality Structure

The 20 rays are arranged into **11 orthonormal bases** (complete sets of 4 mutually orthogonal rays). Each ray appears in multiple bases—this overlap structure is what makes a noncontextual value assignment impossible.

### Bases

The orthonormal bases can be written as:

- **B1**: {v1, v2, v3, v4}
- **B2**: {v5, v6, v7, v8}
- **B3**: {v1, v5, v9, v10}
- **B4**: (placeholder)
- **B5**: (placeholder)
- ...
- **B11**: (placeholder)

!!! info "Hypergraph Representation"
    This structure can be viewed as a **hypergraph**:

    - **Vertices** = the 20 rays
    - **Hyperedges** = the 11 orthonormal bases (each hyperedge connects 4 vertices)

    The KS property corresponds to the non-colorability of this hypergraph under the constraint that exactly one vertex per hyperedge is colored "1" and the rest "0".

---

## KS Contradiction

The Kochen–Specker argument proceeds as follows:

1. **Noncontextuality assumption**: Suppose we can assign a value $v(r) \in \{0, 1\}$ to each ray $r$, representing whether a measurement of the projector onto that ray would yield outcome "yes" (1) or "no" (0).

2. **Orthonormal basis constraint**: For any orthonormal basis $\{r_1, r_2, r_3, r_4\}$, exactly one ray must be assigned 1 (since the projectors onto the four rays sum to the identity, and a quantum state must be in exactly one of them).

3. **Contradiction**: Due to the pattern of overlaps between the 11 bases, there is no consistent way to assign 0s and 1s to all 20 rays. Any attempt to satisfy the constraint for some bases inevitably violates it for others.

This can be verified by systematic case analysis or by computational search. The impossibility of such an assignment proves that quantum mechanics cannot be explained by noncontextual hidden variables.

---

## Relation to Other KS Sets

The Kernaghan 20-vector set is closely related to several other important constructions:

- **Cabello 18 (4D)**: In 1996, Cabello, Estebaranz, and García-Alcaine refined Kernaghan's construction to obtain an 18-vector KS set—the current minimal known in 4D. They achieved this by identifying redundant rays that could be removed while preserving the KS property.

- **Peres 33 (3D)**: The earlier Peres construction in 3D used 33 rays. The move to 4D allowed for more efficient constructions.

- **Kernaghan–Peres 40 (8D)**: Kernaghan and Peres later collaborated on an 8-dimensional construction with remarkable efficiency (40 vectors for dimension 8).

---

## Role in Contextuality Resource Theory

The Kernaghan 20-vector set plays several roles in the modern theory of contextuality as a quantum resource:

### State-Independent Contextuality Witness

The set provides a **state-independent** proof of contextuality: the KS contradiction holds regardless of which quantum state the system is prepared in. This makes it a robust witness for contextuality in any two-qubit state.

### Noncontextuality Inequalities

From the orthogonality structure, one can derive **noncontextuality inequalities**—algebraic expressions involving measurement probabilities that are bounded in any noncontextual model but can be violated by quantum mechanics. The Kernaghan 20 set gives rise to such inequalities for 2-qubit systems.

### Contextuality Monotones

In small-dimensional systems, KS sets like this one can be used to define and compute **contextuality monotones**—quantitative measures of "how contextual" a quantum state or measurement scenario is. The compact structure of the 20-vector set makes it computationally tractable for such analyses.

---

## References

- M. Kernaghan, "Bell–Kochen–Specker theorem for 20 vectors," *J. Phys. A: Math. Gen.* **27**, L829 (1994)
- A. Cabello, J. M. Estebaranz, and G. García-Alcaine, "Bell–Kochen–Specker theorem: A proof with 18 vectors," *Phys. Lett. A* **212**, 183 (1996)
- A. Peres, *Quantum Theory: Concepts and Methods*, Kluwer (1993)
- S. Kochen and E. P. Specker, "The problem of hidden variables in quantum mechanics," *J. Math. Mech.* **17**, 59 (1967)
