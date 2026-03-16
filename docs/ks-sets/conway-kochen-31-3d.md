# Conway-Kochen 31-Vector Construction (3D)

## Source

Scanned from: "Contextualism à la Conway et Kochen" (textbook excerpt).

---

## Overview

The Conway-Kochen 31-vector construction is a refinement of the original Kochen-Specker 117-vector proof and Peres's 33-vector proof, reducing the set to **31 vectors** in 3-dimensional real Hilbert space while still blocking any noncontextual value assignment.

The diagram below shows the cube construction with labeled vectors at vertices, edge midpoints, and face centers. The coloring (green circles = value 1, red circles = value 0) demonstrates the contradiction: the constraints from overlapping orthogonal triads make consistent assignment impossible.

---

## Diagram

![Conway-Kochen 31-vector construction](scans/conway-kochen-31.jpg)

**"Contextualism à la Conway et Kochen"**

Steps 1–3 as before (same as the Peres 33-vector setup).

Step 4: *Simmer, but stir vigorously* in a desperate attempt to verify that the following **31-vector** construction blocks value assignment.

The annotated cube shows vectors labeled with coordinates (e.g., **J**, **X**, **Y**, **A**, **B**, etc.) at lattice points, with subscripts indicating direction (N, S, E, W). Green and red circles mark the forced coloring that leads to contradiction.

> "A few less vectors, but the cook may by now be wondering whether it would have been better to stick to the 'Original' recipe!"

---

## Relation to Other KS Sets

| Construction | Dimension | Vectors | Year |
|-------------|-----------|---------|------|
| Kochen-Specker (original) | 3 | 117 | 1967 |
| Peres | 3 | 33 | 1991 |
| **Conway-Kochen** | **3** | **31** | — |
| Kernaghan | 4 | 20 | 1994 |
| Cabello et al. | 4 | 18 | 1996 |

---

## Recent Research (2026)

### Sub-31 Optimality

The Conway-Kochen 31-vector set is conjectured to be the **minimum KS set in dimension 3**. Six independent computational strategies have failed to find any sub-31 construction:

1. **OCUS proof**: Exhaustively proved no $\leq 30$-vector KS subset exists in the 49-ray integer pool (272 iterations, 0.1s)
2. **Cross-pool mixing**: All 15 pairwise combinations of algebraic pools tested — cross-pool rays never help
3. **Larger alphabets**: 30 expanded alphabets tested — every alphabet containing $\{0, \pm 1, \pm 2\}$ converges to 31
4. **Numerical optimization**: Simulated annealing, perturbation, and completion methods all fail
5. **CK-31 criticality**: 8-critical (exhaustive verification of all $\binom{31}{k}$ subsets for $k = 1..8$)
6. **Triad density bounds**: Random rays in $\mathbb{R}^3$ and $\mathbb{C}^3$ produce zero orthogonal pairs

### Rigidity

CK-31 is **infinitesimally rigid**: the Jacobian null space of the 71 orthogonality constraints has dimension 39, equal to the symmetry dimension (39), leaving zero deformation modes.

### MUS Landscape

From 5000 MUS trials on the 49-ray integer pool, exactly **6 distinct minimal 31-sets** exist:

- **13 core rays** ($\|v\|^2 \leq 3$) appear in all 6 sets
- **12 rays never used** — all with $\|v\|^2 = 9$ (highest norm)
- CK-31 is one of the 6 (rediscovered as set 5)
- No swap connectivity — minimum Hamming distance 5 between any two sets

### Graph Universality

All 31-vertex KS sets found by any method — integer alphabet, rational coordinates, mixed-field constructions, group orbits — share the **same orthogonality graph** (VF2-verified). The CK-31 graph is the unique minimal KS graph in 3D.

### BPQS

$$|S_A| \times |S_B| \leq 8 \times 9 = 72$$

Best found bipartite perfect quantum strategy.

---

## Cross-Links

- [Peres 33-Vector KS Set (3D)](peres-33-3d.md) — The 33-vector construction this refines
- [Kernaghan 20-Vector KS Set (4D)](kernaghan-20-4d.md) — Compact 4D construction
- [Kochen-Specker Theorem History](../history/kochen-specker.md) — Full historical context
- [The Six Algebraic Islands](../research/algebraic-islands.md) — Classification of all known 3D KS constructions
- [Sub-31 Optimality Evidence](../research/papers.md) — Computational evidence paper
