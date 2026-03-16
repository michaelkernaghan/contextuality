# Heegner-7 43-Vector Kochen-Specker Set (3D)

## Basic Metadata

| Property | Value |
|----------|-------|
| **Name** | Heegner-7 43-Vector KS Set |
| **Dimension** | 3 (spin-1 Hilbert space) |
| **Number of Rays** | 43 |
| **Ring** | $\mathbb{Z}[(1+\sqrt{-7})/2]$ |
| **Type** | State-independent KS set |
| **Author** | Michael Kernaghan |
| **Year** | 2026 |
| **Cancellation Identity** | $\alpha \cdot \bar{\alpha} = 2$ |

---

## Overview

The **Heegner-7 43-vector KS set** is constructed over the ring of integers of $\mathbb{Q}(\sqrt{-7})$, a quadratic imaginary number field associated with the Heegner number 7. The algebraic integer $\alpha = (1+\sqrt{-7})/2$ satisfies $\alpha \cdot \bar{\alpha} = 2$, providing a norm-2 cancellation identity that enables exact orthogonalities in $\mathbb{C}^3$.

This construction is significant for several reasons:

- **Genuinely new**: Not present in any prior KS catalogue — the first KS set discovered from a Heegner number field
- **Rigid**: With 107 orthogonal pairs, the Jacobian null space analysis shows zero deformation modes
- **Enhanced contextual advantage**: The CSW contextuality ratio $\theta/\alpha = 1.118$, the highest among all known 3D KS sets
- **Large ray pool**: The full alphabet generates 145 rays, from which the minimal 43-vector set is extracted

Key features:

- **145-ray pool**: The Heegner-7 alphabet with bounded coefficients generates 145 rays
- **Norm-2 cancellation**: $\alpha \cdot \bar{\alpha} = 2$ satisfies the controlling invariant for KS-uncolorability
- **Smooth degradation**: Ablation study shows the contextual advantage degrades smoothly from 1.118 to ~1.03 as rays are removed, with KS property preserved

---

## Structure

The 43 rays live in $\mathbb{C}^3$, using coordinates from the alphabet $\{0, \pm 1, \pm \alpha, \pm \bar{\alpha}\}$ where $\alpha = (1+\sqrt{-7})/2$. Orthogonality between vectors relies on the identity $\alpha \cdot \bar{\alpha} = 2$ together with standard integer arithmetic.

### Orthogonality Structure

| Property | Value |
|----------|-------|
| **Orthogonal pairs** | 107 |
| **Ray pool size** | 145 |
| **Minimum KS subset** | 43 vectors |

---

## Rigidity

The Heegner-7 set is **infinitesimally rigid**: the Jacobian null space has dimension exactly equal to the symmetry dimension, leaving zero deformation modes.

| Property | Value |
|----------|-------|
| Null space dim | 51 |
| Symmetry dim | 51 |
| Deformation modes | **0 (rigid)** |

This rigidity is a new result not covered by the Trandafir-Cabello analysis, which focused on previously known constructions.

---

## Contextual Advantage

The Heegner-7 set exhibits the highest contextual advantage among all known 3D KS sets, measured via the Cabello-Severini-Winter (CSW) graph invariants on the **full 145-ray pool** orthogonality graph (not just the 43-ray minimal set):

| Invariant | Graph | Value |
|-----------|-------|-------|
| Independence number $\alpha(G)$ | 145-ray pool | 50 |
| Lovász theta $\vartheta(G)$ | 145-ray pool | 55.89 |
| Contextuality ratio $\theta/\alpha$ | 145-ray pool | **1.118** |

The CSW invariants are computed on the full pool graph because the contextual advantage measures the maximum quantum-over-classical violation achievable using any rays from the algebraic pool. The ratio $\theta/\alpha > 1$ certifies quantum contextuality. The Heegner-7 value of 1.118 exceeds all other known 3D constructions, and the advantage degrades smoothly as rays are removed (ablation study).

---

## BPQS (Bipartite Perfect Quantum Strategy) — *Heuristic upper bound*

The Heegner-7 set defines a bipartite perfect quantum strategy with:

$$|S_A| \times |S_B| \leq 9 \times 12 = 108$$

This is the best BPQS found by heuristic search (not proved optimal). The 23 bases of the Heegner-7 set define a new Bell scenario not previously studied.

---

## Relation to Other KS Sets

| Construction | Dimension | Vectors | Pairs | Rigid? | Ring |
|-------------|-----------|---------|-------|--------|------|
| Conway-Kochen (CK-31) | 3 | 31 | 71 | Yes | $\mathbb{Z}$ |
| Eisenstein | 3 | 33 | 78 | Yes | $\mathbb{Z}[\omega]$ |
| Peres | 3 | 33 | 72 | No (flex) | $\mathbb{Z}[\sqrt{2}]$ |
| **Heegner-7** | **3** | **43** | **107** | **Yes** | $\mathbb{Z}[(1+\sqrt{-7})/2]$ |
| Golden | 3 | 52 | 124 | Yes | $\mathbb{Z}[\varphi]$ |

The Heegner-7 set occupies a middle position in the six-island hierarchy: larger than the 31-33 vector sets but smaller than the Golden-52, with the highest contextual advantage ratio.

---

## Why "Heegner-7"?

The number 7 is one of the nine **Heegner numbers** (1, 2, 3, 7, 11, 19, 43, 67, 163) — the values of $d$ for which $\mathbb{Q}(\sqrt{-d})$ has class number one (unique factorization). All nine Heegner number fields were tested; only $d=7$ produces a KS set. The key algebraic integer $\alpha = (1+\sqrt{-7})/2$ satisfies $\alpha \bar{\alpha} = 2$, providing the norm-2 cancellation needed for orthogonality. For larger Heegner numbers ($d = 11, 19, \ldots, 163$), the corresponding algebraic integers have norm too large to support the necessary cancellations.

---

## References

- M. Kernaghan, "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three" (2026)
- M. Kernaghan, "New KS Sets from Algebraic Number Fields with Enhanced Contextual Advantage" (2026, PRL letter)

---

## Cross-Links

- [Golden Ratio 52-Vector KS Set (3D)](golden-52-3d.md) — The other genuinely new construction
- [Eisenstein 33-Vector KS Set (3D)](eisenstein-33-3d.md) — Another complex-coordinate KS set
- [The Six Algebraic Islands](../research/algebraic-islands.md) — Classification of all known 3D KS constructions
- [Research Papers](../research/papers.md) — Full paper listing
