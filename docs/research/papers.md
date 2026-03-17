# Papers

## Overview

The algebraic islands research programme has produced one main paper and four PRL-style letters, each addressing a distinct aspect of the classification of Kochen-Specker sets in dimension three.

**Author**: Michael Kernaghan, Pacific Quantum Systems, Vancouver, Canada

---

## Main Paper

### The Algebraic Landscape of Kochen-Specker Sets in Dimension Three

**Length**: ~39 pages
**Venue**: Physical Review A (target)
**Status**: Complete, pending arXiv submission
**[Download PDF](../papers/algebraic_islands.pdf)**

The comprehensive paper presenting the full algebraic classification. Covers:

- Systematic alphabet survey across number rings
- The six algebraic islands and their cancellation identities
- Cross-product closure methodology (revealing the Golden island)
- Realizability gap analysis
- Connection to bipartite perfect quantum strategies (BPQS)
- CSW graph invariants and Bell inequalities
- Rigidity classification (Jacobian null space analysis)
- Three distinct 33-vector KS sets (Peres, Eisenstein, CK-33)
- Merge saturation as a universal property
- OCUS optimality proof for CK-31
- Appendix with representative minimal KS sets for new islands

**Key result**: Low-complexity cancellation identities (modulus-2 or phase cancellation) are the controlling invariant for KS-uncolorability in dimension 3.

**Revision notes (March 16, 2026)**: Fixed CSW α* numerical error in integer pool table (17.00 → 19.00); clarified ray-level MUS extraction methodology; added classification scope limitation; added falsifiability paragraph; strengthened novelty claim qualifications; added Cabello finite-dimensional qualifier. Reviewed by GPT-5.4-pro Oxford challenge method (32 issues assessed, 6 substantive fixes applied).

---

## PRL Letters

### 1. New KS Sets from Algebraic Number Fields with Enhanced Contextual Advantage

**Length**: 4 pages
**Venue**: Physical Review Letters (target)
**Status**: Submitted to arXiv (March 2026), revision pending processing
**[Download PDF](../papers/heegner7_letter.pdf)**

Introduces the Heegner-7 (43 vectors) and Golden ratio (52 vectors) KS sets — the first genuinely new 3D KS constructions in decades. Reports the enhanced contextual advantage of Heegner-7 ($\vartheta/\alpha = 1.118$) and the cross-product discovery mechanism for the Golden set.

**Key result**: Two genuinely new KS sets, neither in any prior catalogue, with the highest known contextual advantage in 3D.

**Revision notes (March 16, 2026)**: Removed dependency on unpublished main paper ("in preparation" references); fixed Bell-scenario claim (necessity → candidates); added closure termination caveat; softened convention and Pavičić claims. Paper is now fully self-contained. GPT-5.4-pro Oxford review: 24 issues assessed, 5 substantive fixes applied.

---

### 2. Graph Isomorphism of 31-Vertex Kochen-Specker Sets Across Coordinate Alphabets

**Length**: 4 pages
**Venue**: Physical Review Letters (target)
**Status**: Submitted to arXiv (March 2026), revision pending processing
**[Download PDF](../papers/universality_letter.pdf)**

Shows that all 31-vertex KS sets found across three alphabet-based searches share the same orthogonality graph (VF2-verified). Establishes the modulus-2 cancellation boundary as an empirical regularity. Honestly notes that the three searches may not be independent (rational and mixed alphabets contain the integer alphabet).

**Key result**: The CK-31 graph is recovered by every tested alphabet-based search that achieves 31 rays.

**Revision notes (March 16, 2026)**: Removed dependency on unpublished papers ("in preparation" references); strengthened 109-ray projective equivalence verification; clarified Table 1 column header; added Schütte bibliography entry; anchored random hypergraph claim; defined rigidity parenthetically. Paper is now fully self-contained. GPT-5.4-pro Oxford review: 24 issues assessed, 6 substantive fixes applied.

---

### 3. Computational Evidence for the Optimality of CK-31

**Length**: 5 pages
**Venue**: Physical Review Letters (target)
**Status**: Complete, not submitted
**[Download PDF](../papers/sub31_letter.pdf)**

Presents six independent computational strategies that all fail to find a sub-31 KS set. Includes the OCUS exhaustive proof for the integer pool, 8-criticality of CK-31, cross-pool mixing results, and the merge saturation universal property.

**Key result**: No sub-31 KS set exists by any known method; CK-31 is 8-critical and merge-saturated.

---

### 4. Kochen-Specker Uncolorability in Cyclotomic Fields Requires Exactly 6|n

**Length**: 4 pages
**Venue**: Physical Review Letters (target)
**Status**: Submitted to arXiv (March 2026), revision pending processing
**[Download PDF](../papers/cyclotomic_letter.pdf)**

The only letter with a complete algebraic proof (no computational evidence needed). Proves that the cyclotomic ray pool $S_n$ is KS-uncolorable if and only if $6|n$, via seven lemmas covering sufficiency and three necessity cases.

**Key result**: Complete characterization of KS-uncolorability across all cyclotomic fields, connecting to $\mathbb{Z}[1/6]$ minimality.

**Revision notes (March 16, 2026)**: Added footnote clarifying orthogonality table shows necessary divisibility conditions; marked Cabello 2025 as preprint. GPT-5.4-pro Oxford review: 15 issues assessed, 2 substantive fixes applied (proofs confirmed correct).

---

## Computational Reproducibility

All results are reproducible via Python scripts in the `contextuality/` repository. Key dependencies: Python 3.11, PySAT 1.8 (Glucose4), NumPy, SciPy. All scripts use `random.seed(42)` for reproducibility.

---

## Related Pages

- [The Six Algebraic Islands](algebraic-islands.md) — Central classification result
- [Research Overview](index.md) — Programme summary
- [Bibliography](../bibliography.md) — Full reference list
