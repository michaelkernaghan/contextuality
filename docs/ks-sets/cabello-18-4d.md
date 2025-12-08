# Cabello 18-Vector Kochen–Specker Set (4D)

## Basic Metadata

| Property | Value |
|----------|-------|
| **Name** | Cabello 18-Vector KS Set |
| **Dimension** | 4 (two-qubit Hilbert space) |
| **Number of Rays** | 18 |
| **Type** | State-independent KS set |
| **Authors** | Adán Cabello, José M. Estebaranz, Guillermo García-Alcaine |
| **Year** | 1996 |
| **Original Reference** | A. Cabello, J. M. Estebaranz, and G. García-Alcaine, "Bell–Kochen–Specker theorem: A proof with 18 vectors," *Phys. Lett. A* **212**, 183 (1996) |

---

## Overview

The **Cabello 18-vector set** is the **minimal known Kochen–Specker set in 4 dimensions**. It was obtained by refining Kernaghan's earlier 20-vector construction, identifying and removing two redundant rays while preserving the KS property.

This set represents a significant achievement in the search for minimal KS configurations:

- **Minimal in 4D**: No KS set with fewer than 18 vectors is known in dimension 4
- **Computational benchmark**: Used as a reference point for computational searches and proofs
- **Elegant structure**: Maintains high symmetry despite the reduction from 20 vectors

Whether 18 is the absolute minimum for 4D remains an open question, but extensive computational searches have not found anything smaller.

---

## Structure

The 18 rays live in $\mathbb{C}^4$, the Hilbert space of a two-qubit system. The construction was derived from Kernaghan's 20-vector set by careful analysis of which rays were essential for the KS contradiction.

Cabello, Estebaranz, and García-Alcaine observed that two rays could be removed from Kernaghan's construction without destroying the KS property. The remaining 18 rays are arranged into **9 orthonormal bases** (complete sets of 4 mutually orthogonal rays), with each ray appearing in multiple bases—this overlap pattern prevents any consistent noncontextual value assignment.

!!! info "Hypergraph Representation"
    The hypergraph for this set has:

    - **18 vertices** (rays)
    - **9 hyperedges** of size 4 (bases)

    The KS property requires that no 0-1 coloring exists with exactly one "1" per hyperedge. This is a hypergraph coloring problem, and the Cabello 18 hypergraph is provably non-colorable.

!!! tip "Vector Coordinates"
    For explicit vector coordinates and the complete basis structure, see the original paper: A. Cabello, J. M. Estebaranz, and G. García-Alcaine, "Bell–Kochen–Specker theorem: A proof with 18 vectors," *Phys. Lett. A* **212**, 183 (1996).

---

## KS Contradiction

The proof that no noncontextual assignment exists follows the standard KS argument:

1. **Setup**: Attempt to assign $v(r) \in \{0, 1\}$ to each of the 18 rays such that each basis has exactly one ray assigned 1.

2. **Counting argument**: With 9 bases, we need exactly 9 ones total. With 18 rays each appearing in 2 bases (on average), a consistent assignment would require careful balancing.

3. **Case analysis**: Systematic case analysis (or exhaustive computer search) shows that no such assignment exists. Every attempt to satisfy some bases violates others due to the overlap pattern.

The proof is elementary but tedious by hand; it is often verified computationally.

---

## Minimality

### Is 18 Optimal?

The Cabello 18 set is the smallest **known** KS set in 4D, but whether it is truly minimal remains open:

- **Lower bounds**: Various arguments give lower bounds on KS set size, but none reach 18
- **Computational searches**: Extensive searches have not found 17-vector or smaller KS sets in 4D
- **Structural constraints**: The hypergraph constraints suggest 18 may be close to optimal

### Comparison with Other Dimensions

| Dimension | Smallest Known KS Set | Reference |
|-----------|----------------------|-----------|
| 3 | 31 vectors | Conway–Kochen |
| 4 | 18 vectors | Cabello et al. |
| 8 | 40 vectors | Kernaghan–Peres |

The 4D case is notable for having the smallest known KS set relative to a power-of-2 dimension, making it particularly relevant for qubit-based quantum information.

---

## Relation to Other KS Sets

### Kernaghan 20 (4D)

The Cabello 18 set is a direct refinement of Kernaghan's 20-vector construction. The relationship demonstrates that:

- Initial constructions may contain redundancy
- Careful analysis can identify essential vs. dispensable elements
- The path to minimality often goes through simplification of larger sets

### Peres–Mermin Square

The **Peres–Mermin magic square** provides a different approach to contextuality in 4D, using 9 observables arranged in a 3×3 array. While not directly a KS set (it uses observables rather than rays), it is related to the Cabello construction and provides an alternative proof of 4D contextuality.

### Yu–Oh Set

Yu and Oh found a 13-ray set in 3D that, while not a KS set, demonstrates state-dependent contextuality. This shows that the landscape of contextuality proofs extends beyond KS sets.

---

## Role in Contextuality Resource Theory

The Cabello 18 set is a workhorse for contextuality research:

### Experimental Tests

Due to its small size, the Cabello 18 set is often used in **experimental tests of contextuality**:

- Requires only 18 measurement settings
- Each setting corresponds to a projector onto one of the rays
- Violations of noncontextuality inequalities can be tested with current technology

### Noncontextuality Inequalities

The 9-basis structure gives rise to specific **noncontextuality inequalities**. For any noncontextual model:

$$\sum_{i=1}^{9} \sum_{j=1}^{4} p(1|r_{ij}) = 9$$

where $p(1|r_{ij})$ is the probability of outcome 1 for ray $j$ in basis $i$. Quantum mechanics can violate the constraints implicit in noncontextual models.

### Two-Qubit Systems

As a 4D construction, the Cabello 18 set is directly applicable to **two-qubit systems**:

- The rays can be realized as two-qubit states
- The bases correspond to complete measurements on the two-qubit system
- Contextuality witnesses derived from this set apply to any two-qubit state

### Contextuality Monotones

The small size makes the Cabello 18 set computationally tractable for:

- Computing contextuality measures
- Comparing contextual resources across different states
- Optimizing contextuality-based protocols

---

## References

- A. Cabello, J. M. Estebaranz, and G. García-Alcaine, "Bell–Kochen–Specker theorem: A proof with 18 vectors," *Phys. Lett. A* **212**, 183 (1996)
- M. Kernaghan, "Bell–Kochen–Specker theorem for 20 vectors," *J. Phys. A: Math. Gen.* **27**, L829 (1994)
- A. Peres, "Two simple proofs of the Kochen–Specker theorem," *J. Phys. A: Math. Gen.* **24**, L175 (1991)
- A. Cabello, "Experimentally testable state-independent quantum contextuality," *Phys. Rev. Lett.* **101**, 210401 (2008)
- S. Yu and C. H. Oh, "State-independent proof of Kochen–Specker theorem with 13 rays," *Phys. Rev. Lett.* **108**, 030402 (2012)
