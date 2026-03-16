# Research

## The Algebraic Islands Programme

This section documents original research (2026) on the algebraic classification of Kochen-Specker sets in dimension three. The central discovery is that KS-uncolorable ray pools in $\mathbb{R}^3$ and $\mathbb{C}^3$ cluster into exactly **six algebraic islands** (six distinct graph families), each characterized by number rings whose generators satisfy norm-$\leq 2$ cancellation identities. Multiple rings can produce the same island when they yield isomorphic orthogonality graphs.

### Central Thesis

> **Generator norm $\leq 2$ is the controlling invariant for KS-uncolorability in dimension 3.**

The integer identity $1+1=2$, the Peres identity $(\sqrt{2})^2 = 2$, the Eisenstein identity $1+\omega+\omega^2 = 0$, and the Heegner-7 identity $\alpha \cdot \bar{\alpha} = 2$ are all manifestations of the same constraint: the alphabet must support cancellation identities that produce exact orthogonalities among triples of vectors. At generator norm $\geq 3$, such cancellations become impossible.

---

## Research Pages

### [The Six Algebraic Islands](algebraic-islands.md)

The central classification result. Documents all six islands with their rings, minimal KS sets, cancellation identities, rigidity properties, and BPQS numbers. Includes the sub-31 optimality evidence, graph universality of CK-31, and the MUS landscape.

### [Papers](papers.md)

Listing of all papers produced by this research programme: one main paper (~36 pages) and four PRL-style letters, each addressing a distinct aspect of the classification.

---

## New KS Set Constructions

The algebraic islands programme discovered four new KS sets:

| Construction | Vectors | Ring | Status |
|-------------|---------|------|--------|
| [Eisenstein-33](../ks-sets/eisenstein-33-3d.md) | 33 | $\mathbb{Z}[\omega]$ | Independently found by Cabello (2025) |
| [Heegner-7](../ks-sets/heegner7-43-3d.md) | 43 | $\mathbb{Z}[(1+\sqrt{-7})/2]$ | Genuinely new |
| [Golden-52](../ks-sets/golden-52-3d.md) | 52 | $\mathbb{Z}[\varphi]$ | Genuinely new |
| [$\mathbb{Z}[\sqrt{-2}]$-33](../ks-sets/zsqrt2-neg-33-3d.md) | 33 | $\mathbb{Z}[\sqrt{-2}]$ | New realization of Peres graph |

---

## Key Results Summary

1. **Six algebraic islands** — complete classification of norm-$\leq 2$ KS-producing rings
2. **Sub-31 optimality** — OCUS proof that no $\leq 30$-vector KS set exists in the integer pool; six independent strategies confirm CK-31 as minimal
3. **Graph universality** — all 31-vertex KS sets (integer, rational, mixed-field, group-orbit) share the same orthogonality graph
4. **6|n cyclotomic theorem** — KS-uncolorability in cyclotomic fields $\mathbb{Q}(\zeta_n)$ requires exactly $6 | n$ (complete algebraic proof)
5. **Rigidity classification** — CK-31, Eisenstein-33, Heegner-7, Golden-52 are rigid; Peres-33 and $\mathbb{Z}[\sqrt{-2}]$-33 are flex (the flex belongs to the graph)
6. **Merge saturation** — all six minimal KS sets are merge-saturated (100% preservation under non-orthogonal pair merges)
