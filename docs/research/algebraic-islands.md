# The Six Algebraic Islands

## Classification

Systematic enumeration of algebraic number rings reveals exactly six "islands" — families of rays in $\mathbb{C}^3$ that produce KS-uncolorable pools with distinct graph types. Each island is defined by a number ring whose generators satisfy a norm-$\leq 2$ cancellation identity.

Note: "six islands" refers to six distinct *graph families*, not six rings. Some rings produce isomorphic orthogonality graphs — for instance, $\mathbb{Z}[\sqrt{-2}]$, Gaussian integers $\mathbb{Z}[i]$, and Peres' $\mathbb{Z}[\sqrt{2}]$ all produce the same "Peres graph." These are counted as one island (the Peres island) with multiple algebraic realizations.

| # | Island | Ring | Min KS | Cancellation Identity | Pool Size |
|---|--------|------|--------|-----------------------|-----------|
| 1 | [Integer (CK-31)](../ks-sets/conway-kochen-31-3d.md) | $\mathbb{Z}$ | 31 | $1+1=2$ | 49 |
| 2 | [Peres](../ks-sets/peres-33-3d.md) | $\mathbb{Z}[\sqrt{2}]$ | 33 | $(\sqrt{2})^2 = 2$ | 49 |
| 3 | [Eisenstein](../ks-sets/eisenstein-33-3d.md) | $\mathbb{Z}[\omega]$ | 33 | $1+\omega+\omega^2 = 0$ | 57 |
| 4 | [$\mathbb{Z}[\sqrt{-2}]$](../ks-sets/zsqrt2-neg-33-3d.md) | $\mathbb{Z}[\sqrt{-2}]$ | 33 | $|\sqrt{-2}|^2 = 2$ | 49 |
| 5 | [Heegner-7](../ks-sets/heegner7-43-3d.md) | $\mathbb{Z}[(1+\sqrt{-7})/2]$ | 43 | $\alpha \cdot \bar{\alpha} = 2$ | 145 |
| 6 | [Golden](../ks-sets/golden-52-3d.md) | $\mathbb{Z}[\varphi]$ | 52 | $\varphi^2 = \varphi + 1$ | 205 |

Islands 2, 4, and Gaussian ($\mathbb{Z}[i]$) are **graph-isomorphic** — they share the same orthogonality graph (the "Peres graph") despite using different algebraic coordinates. This means there are five distinct graph types among the six algebraic islands.

---

## The Norm-2 Boundary

The central organizing principle is the **generator norm**: for a ring element $\alpha$ to participate in KS-producing orthogonalities, it must satisfy a cancellation identity with "norm" $\leq 2$ (where norm refers to $|\alpha|^2$ or the algebraic norm $\alpha \bar{\alpha}$).

**What works** (norm $\leq 2$):
- $1 + 1 = 2$ (integers)
- $(\sqrt{2})^2 = 2$ (Peres)
- $1 + \omega + \omega^2 = 0$ (Eisenstein, norm 1)
- $\alpha \bar{\alpha} = 2$ for $\alpha = (1+\sqrt{-7})/2$ (Heegner-7)
- $\varphi^2 = \varphi + 1$ (Golden)

**What doesn't work** (norm $\geq 3$):
- $\{0, \pm 1, \pm 3\}$ — no KS set (lacks $1+1=2$)
- $\{0, \pm 1, \pm 4\}$ — no KS set
- Plastic ratio, tribonacci, silver ratio, supersilver — all colorable
- Heegner numbers $d = 11, 19, 43, 67, 163$ — all colorable (norm too large)

---

## Sub-31 Optimality

Strong computational evidence that CK-31 is the minimum KS set in dimension 3:

### OCUS Proof (Integer Pool)

The OCUS (Optimal Constrained Unsatisfiable Subset) algorithm exhaustively proved that no $\leq 30$-vector KS subset exists in the 49-ray integer pool $\{0, \pm 1, \pm 2\}$. Completed in 272 iterations (0.1 seconds).

### Six Independent Strategies

| Strategy | Method | Result |
|----------|--------|--------|
| 1. SAT minimization | MUS + greedy + swap on all 6 pools | All pools: min = known minimum |
| 2. Cross-pool mixing | All 15 pairwise + full 477-ray union | Cross-pool rays never help |
| 3. Larger alphabets | 30 expanded alphabets tested | Every alphabet with $\{0,\pm 1,\pm 2\}$ → 31 |
| 4. Numerical optimization | SA, perturbation, completion | Zero triads from random rays |
| 5. CK-31 criticality | Exhaustive k=1..8, sampled k=9..12 | 8-critical (all subsets colorable) |
| 6. Triad density bounds | Random rays in $\mathbb{R}^3$ and $\mathbb{C}^3$ | Zero orthogonal pairs in random samples |

**Key finding**: Every alphabet containing $\{0, \pm 1, \pm 2\}$ converges to CK-31 as its minimum. Alphabets lacking $\pm 2$ are either not KS-uncolorable or stay at $\geq 33$.

---

## Graph Universality of CK-31

All 31-vertex KS sets found by any method — integer alphabet, rational coordinates, mixed-field constructions, $A_4$ and $S_4$ group orbits — share the **same orthogonality graph** (verified by VF2 isomorphism, both graph and hypergraph).

This universality means the CK-31 graph is the unique minimal graph supporting KS-uncolorability in 3D with integer-type coordinates. Negative controls confirm: rings like $\mathbb{Z}[\sqrt{3}]$, $\mathbb{Z}[\sqrt{-5}]$ produce pools with many bases but all are KS-colorable.

---

## MUS Landscape

From 5000 MUS (Minimal Unsatisfiable Subset) trials on the 49-ray integer pool, exactly **6 distinct minimal 31-sets** exist:

- **13 core rays** ($\|v\|^2 \leq 3$) appear in all 6 sets — the $\{0, \pm 1\}$ skeleton
- **12 rays never used** — all with $\|v\|^2 = 9$ (highest norm)
- **Norm stratification**: $\|v\|^2 = 1,2,3 \to$ core (100%); $\|v\|^2 = 5 \to$ 83%; $\|v\|^2 = 6 \to$ 67%; $\|v\|^2 = 9 \to$ 0%
- **No swap connectivity** — minimum Hamming distance 5 between any two sets
- **CK-31 is one of the 6** (rediscovered as set 5)

---

## Merge Saturation

All six minimal KS sets exhibit 100% merge preservation: merging any pair of non-orthogonal vertices preserves KS-uncolorability.

| Island | Min | Non-orth pairs | Preserved | Rate |
|--------|-----|---------------|-----------|------|
| CK-31 | 31 | 394 | 394 | 100% |
| Peres-33 | 33 | 456 | 456 | 100% |
| Eisenstein-33 | 33 | 450 | 450 | 100% |
| $\mathbb{Z}[\sqrt{-2}]$-33 | 33 | 456 | 456 | 100% |
| Heegner-7 | 43 | 796 | 796 | 100% |
| Golden-52 | 52 | 1204 | 1204 | 100% |

**Total**: 3,756 merges, all preserving KS-uncolorability. This motivates the **merge-saturation conjecture**: every minimal KS set in $\mathbb{R}^3$/$\mathbb{C}^3$ is merge-saturated.

---

## Rigidity Classification

| Island | Vectors | Pairs | Null dim | Sym dim | Deformation | Status |
|--------|---------|-------|----------|---------|-------------|--------|
| CK-31 | 31 | 71 | 39 | 39 | 0 | **Rigid** |
| Eisenstein-33 | 33 | 78 | 41 | 41 | 0 | **Rigid** |
| Peres-33 | 33 | 72 | 42 | 41 | 1 | **Flex** |
| $\mathbb{Z}[\sqrt{-2}]$-33 | 33 | 72 | 42 | 41 | 1 | **Flex** |
| Heegner-7 | 43 | 107 | 51 | 51 | 0 | **Rigid** |
| Golden-52 | 52 | 124 | 60 | 60 | 0 | **Rigid** |

The Peres and $\mathbb{Z}[\sqrt{-2}]$ flex is **infinitesimal only** — blocked at second order. Both are finitely rigid. The flex belongs to their shared graph (72 pairs vs Eisenstein's 78), not to the choice of algebraic ring.

---

## BPQS / Bell Connections

Each KS set defines a bipartite perfect quantum strategy (BPQS), connecting the KS theorem to Bell nonlocality:

| Island | $|S_A| \times |S_B|$ | Product | Status |
|--------|---------------------|---------|--------|
| Eisenstein-33 | $5 \times 9$ | 45 | Exact |
| Peres-33 | $7 \times 9$ | 63 | Exact |
| CK-31 | $8 \times 9$ | $\leq 72$ | Best found |
| $\mathbb{Z}[\sqrt{-2}]$-33 | $7 \times 9$ | 63 | Exact (= Peres) |
| Heegner-7 | $9 \times 12$ | $\leq 108$ | Best found |
| Golden-52 | $12 \times 13$ | $\leq 156$ | Best found |

The Eisenstein-33 set achieves the smallest known BPQS (45) among all 3D KS sets.

---

## The 6|n Cyclotomic Theorem

**Theorem**: The cyclotomic ray pool $S_n$ (rays with coordinates in $\mathbb{Q}(\zeta_n)$) is KS-uncolorable if and only if $6 | n$.

This is proved by complete algebraic argument (no computational evidence needed):

- **Sufficiency**: When $6|n$, the Eisenstein 33-set embeds (since $\omega = \zeta_3 \in \mathbb{Q}(\zeta_n)$ when $3|n$)
- **Case 1** ($3 \nmid n$, $2 \nmid n$): Only the axis triad exists; trivially colorable
- **Case 2** ($3 \nmid n$, $2 | n$): Each non-axis ray has exactly one orthogonal partner; explicit coloring constructed
- **Case 3** ($3 | n$, $2 \nmid n$): Projective collapse reduces 6 permutations to 2 rays; each ray participates in exactly one triad; colorable by triad decomposition

---

## References

- M. Kernaghan, "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three" (2026)
- M. Kernaghan, "New KS Sets from Algebraic Number Fields with Enhanced Contextual Advantage" (2026)
- M. Kernaghan, "Graph Universality of CK-31 and the Norm-2 Boundary" (2026)
- M. Kernaghan, "Computational Evidence for the Optimality of CK-31" (2026)
- M. Kernaghan, "Kochen-Specker Uncolorability in Cyclotomic Fields Requires Exactly 6|n" (2026)
- A. Cabello, "Simplest Kochen-Specker Set," *Phys. Rev. Lett.* (2025), arXiv:2508.07335
- A. Cabello, "Simplest Bipartite Perfect Quantum Strategies," *Phys. Rev. Lett.* **134**, 010201 (2024)
- S. Trandafir and A. Cabello, rigidity of KS sets (2024)
- Liu et al., "Equivalence between FNS, FN, AVN, PT," *Phys. Rev. Research* **6**, L042035 (2024)
- F. Li, A. Bright, and V. Ganesh, SAT-based KS search, IJCAI 2024, arXiv:2306.13319
