# Eisenstein 33-Vector Kochen-Specker Set (3D)

## Basic Metadata

| Property | Value |
|----------|-------|
| **Name** | Eisenstein 33-Vector KS Set |
| **Dimension** | 3 (spin-1 Hilbert space) |
| **Number of Rays** | 33 |
| **Ring** | $\mathbb{Z}[\omega]$, where $\omega = e^{2\pi i/3}$ |
| **Type** | State-independent KS set |
| **Author** | Michael Kernaghan |
| **Year** | 2026 |
| **Cancellation Identity** | $1 + \omega + \omega^2 = 0$ |

---

## Overview

The **Eisenstein 33-vector KS set** is constructed over the ring of Eisenstein integers $\mathbb{Z}[\omega]$, where $\omega$ is a primitive cube root of unity. The key algebraic identity $1 + \omega + \omega^2 = 0$ provides a cancellation mechanism that enables exact orthogonalities among triples of vectors in $\mathbb{C}^3$.

This construction is significant for several reasons:

- **Rigid**: With 78 orthogonal pairs (6 more than the Peres-33 set), the Eisenstein set is infinitesimally rigid — the additional constraints kill the flex mode present in the Peres graph
- **Smallest BPQS**: Achieves the exact bipartite perfect quantum strategy (BPQS) count of $5 \times 9 = 45$, the smallest among all known 3D KS sets
- **Connected to Cabello 2025**: Independently discovered via the Wigner-Heisenberg construction by Cabello (arXiv:2508.07335), who identified it as the "simplest Kochen-Specker set"

Key features:

- **57-ray pool**: The full Eisenstein alphabet with $|c| \leq 2$ generates 57 rays
- **Norm-2 cancellation**: The identity $1 + \omega + \omega^2 = 0$ has norm 1, satisfying the norm-$\leq 2$ threshold for KS-uncolorability
- **Three distinct 33-sets**: The Eisenstein-33, Peres-33, and Conway-Kochen-33 (CK-33) are three structurally distinct KS sets, all with 33 vectors but different graphs

---

## Structure

The 33 rays live in $\mathbb{C}^3$, using coordinates from the Eisenstein integer alphabet $\{0, \pm 1, \pm \omega, \pm \omega^2\}$. They are arranged into orthogonal triads whose orthogonality relies on the vanishing sum $1 + \omega + \omega^2 = 0$.

### Orthogonality Structure

| Property | Value |
|----------|-------|
| **Orthogonal pairs** | 78 |
| **Orthogonal triads** | — |
| **Degree distribution** | Includes degree-5 vertices (12 of them) |

The 78 orthogonal pairs provide 12 more constraints than the Peres-33 set's 72 pairs. These additional constraints — arising from 12 degree-5 vertices — are what make the Eisenstein set rigid while Peres is flexible.

---

## Rigidity

The Eisenstein-33 set is **infinitesimally rigid**: the Jacobian null space of the orthogonality constraints has dimension equal to the symmetry dimension (41), leaving zero deformation degrees of freedom.

| Property | Eisenstein-33 | Peres-33 |
|----------|--------------|----------|
| Orthogonal pairs | 78 | 72 |
| Null space dim | 41 | 42 |
| Symmetry dim | 41 | 41 |
| Deformation modes | **0 (rigid)** | **1 (flex)** |

The rigidity is a consequence of the graph structure, not the algebraic field: the 6 additional orthogonal pairs provide enough constraints to eliminate the infinitesimal flex present in the Peres graph.

---

## BPQS (Bipartite Perfect Quantum Strategy)

The Eisenstein-33 set defines a bipartite perfect quantum strategy with:

$$|S_A| \times |S_B| = 5 \times 9 = 45$$

This is the **exact minimum** BPQS for this construction, verified computationally. It is the smallest BPQS among all known 3D KS sets, consistent with the high constraint density of the Eisenstein graph.

---

## Connection to Cabello 2025

Cabello's 2025 paper "Simplest Kochen-Specker Set" (arXiv:2508.07335, PRL) constructs a 33-vector, 14-basis KS set via the Wigner-Heisenberg (WH) group acting on $\mathbb{C}^3$. This construction naturally produces Eisenstein-integer coordinates because the WH group for dimension 3 involves cube roots of unity.

Our algebraic islands programme discovered the same set independently through systematic alphabet enumeration over $\mathbb{Z}[\omega]$, providing a complementary algebraic perspective on why this construction exists.

---

## Relation to Other KS Sets

| Construction | Dimension | Vectors | Pairs | Rigid? | Ring |
|-------------|-----------|---------|-------|--------|------|
| Conway-Kochen (CK-31) | 3 | 31 | 71 | Yes | $\mathbb{Z}$ |
| **Eisenstein** | **3** | **33** | **78** | **Yes** | $\mathbb{Z}[\omega]$ |
| Peres | 3 | 33 | 72 | No (flex) | $\mathbb{Z}[\sqrt{2}]$ |
| Z[$\sqrt{-2}$] | 3 | 33 | 72 | No (flex) | $\mathbb{Z}[\sqrt{-2}]$ |
| Conway-Kochen (CK-33) | 3 | 33 | 76 | Yes | $\mathbb{Z}$ |

---

## References

- M. Kernaghan, "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three" (2026)
- A. Cabello, "Simplest Kochen-Specker Set," *Phys. Rev. Lett.* (2025), arXiv:2508.07335
- A. Cabello, "Simplest Bipartite Perfect Quantum Strategies," *Phys. Rev. Lett.* **134**, 010201 (2024), arXiv:2311.17735

---

## Cross-Links

- [Peres 33-Vector KS Set (3D)](peres-33-3d.md) — The classic 33-vector set with different graph structure
- [Conway-Kochen 31-Vector KS Set (3D)](conway-kochen-31-3d.md) — The minimal integer KS set
- [The Six Algebraic Islands](../research/algebraic-islands.md) — Classification of all known 3D KS constructions
- [Research Papers](../research/papers.md) — Full paper listing
