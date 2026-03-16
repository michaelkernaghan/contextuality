# Golden Ratio 52-Vector Kochen-Specker Set (3D)

## Basic Metadata

| Property | Value |
|----------|-------|
| **Name** | Golden Ratio 52-Vector KS Set |
| **Dimension** | 3 (spin-1 Hilbert space) |
| **Number of Rays** | 52 |
| **Ring** | $\mathbb{Z}[\varphi]$, where $\varphi = (1+\sqrt{5})/2$ |
| **Type** | State-independent KS set |
| **Author** | Michael Kernaghan |
| **Year** | 2026 |
| **Cancellation Identity** | $\varphi^2 = \varphi + 1$ |

---

## Overview

The **Golden ratio 52-vector KS set** is constructed over the ring $\mathbb{Z}[\varphi]$ of integers in $\mathbb{Q}(\sqrt{5})$, where $\varphi = (1+\sqrt{5})/2$ is the golden ratio. The identity $\varphi^2 = \varphi + 1$ provides a norm-2 cancellation mechanism (since $\varphi \cdot \bar{\varphi} = -1$ and $\varphi^2 - \varphi - 1 = 0$ imply cancellations producing exact orthogonalities).

This construction is remarkable for several reasons:

- **Invisible to raw search**: The golden ratio set cannot be found by alphabet enumeration alone — it is revealed only by **cross-product completion**, where new rays are generated as cross products of existing alphabet rays
- **Genuinely new**: Not present in any prior KS catalogue
- **Rigid**: With 124 orthogonal pairs, the Jacobian analysis confirms zero deformation modes
- **Largest known minimal 3D KS set**: At 52 vectors, this is the largest minimal KS set among the six algebraic islands

Key features:

- **205-ray pool**: The full golden ratio alphabet with cross-product closure generates 205 rays
- **Cross-product discovery**: Raw alphabet search over $\{0, \pm 1, \pm \varphi\}$ produces only colorable pools; KS-uncolorability emerges only after closing under cross products
- **No integer absorption**: Unlike most other extended alphabets, the golden ratio pool does not collapse to the CK-31 integer set when integers are added

---

## Structure

The 52 rays live in $\mathbb{R}^3$, using coordinates from the golden ratio ring $\mathbb{Z}[\varphi] = \{a + b\varphi : a, b \in \mathbb{Z}\}$. Unlike the Eisenstein and Heegner-7 sets which use complex coordinates, the golden ratio set lives entirely in real 3-space.

### Orthogonality Structure

| Property | Value |
|----------|-------|
| **Orthogonal pairs** | 124 |
| **Ray pool size** | 205 |
| **Minimum KS subset** | 52 vectors |

---

## Rigidity

The Golden-52 set is **infinitesimally rigid**: the Jacobian null space has dimension exactly equal to the symmetry dimension.

| Property | Value |
|----------|-------|
| Null space dim | 60 |
| Symmetry dim | 60 |
| Deformation modes | **0 (rigid)** |

This rigidity is a new result not covered by any prior analysis.

---

## Cross-Product Completion

The golden ratio island illustrates a key methodological point: not all KS sets can be found by simple alphabet enumeration.

1. **Start**: Generate all rays with coordinates in $\{0, \pm 1, \pm \varphi\}$
2. **Problem**: The resulting pool is KS-colorable — no subset proves the KS theorem
3. **Solution**: Take cross products $v_i \times v_j$ for all pairs of rays, normalize, and add new rays whose coordinates remain in $\mathbb{Z}[\varphi]$
4. **Result**: The completed pool of 205 rays contains KS-uncolorable subsets, with minimum size 52

This "invisibility" to raw search makes the golden ratio island the most structurally subtle of the six islands.

---

## BPQS (Bipartite Perfect Quantum Strategy)

The Golden-52 set defines a bipartite perfect quantum strategy with:

$$|S_A| \times |S_B| \leq 12 \times 13 = 156$$

This is the best BPQS found (heuristic upper bound). The 25 bases define a new Bell scenario.

---

## Relation to Other KS Sets

| Construction | Dimension | Vectors | Pairs | Rigid? | Ring |
|-------------|-----------|---------|-------|--------|------|
| Conway-Kochen (CK-31) | 3 | 31 | 71 | Yes | $\mathbb{Z}$ |
| Peres | 3 | 33 | 72 | No (flex) | $\mathbb{Z}[\sqrt{2}]$ |
| Eisenstein | 3 | 33 | 78 | Yes | $\mathbb{Z}[\omega]$ |
| Heegner-7 | 3 | 43 | 107 | Yes | $\mathbb{Z}[(1+\sqrt{-7})/2]$ |
| **Golden** | **3** | **52** | **124** | **Yes** | $\mathbb{Z}[\varphi]$ |

---

## Why Can't Other Real Quadratic Fields Produce KS Sets?

Extensive testing of other real algebraic numbers — the silver ratio $1+\sqrt{2}$ (which IS the Peres set), the plastic ratio, tribonacci constant, and supersilver ratio — shows that only those with norm-2 cancellation identities support KS-uncolorable pools. The golden ratio satisfies $\varphi^2 = \varphi + 1$, which enables the necessary cancellations; fields without such identities produce colorable pools regardless of pool size.

---

## References

- M. Kernaghan, "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three" (2026)
- M. Kernaghan, "New KS Sets from Algebraic Number Fields with Enhanced Contextual Advantage" (2026, PRL letter)

---

## Cross-Links

- [Heegner-7 43-Vector KS Set (3D)](heegner7-43-3d.md) — The other genuinely new construction
- [Peres 33-Vector KS Set (3D)](peres-33-3d.md) — The classic real-coordinate 3D KS set
- [The Six Algebraic Islands](../research/algebraic-islands.md) — Classification of all known 3D KS constructions
- [Research Papers](../research/papers.md) — Full paper listing
