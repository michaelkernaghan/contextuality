# Papers

## Overview

The algebraic islands research programme has produced one main paper and four PRL-style letters, each addressing a distinct aspect of the classification of Kochen-Specker sets in dimension three.

**Author**: Michael Kernaghan, Pacific Quantum Systems, Vancouver, Canada

---

## Main Paper

### The Algebraic Landscape of Kochen-Specker Sets in Dimension Three

**Length**: ~36 pages
**Venue**: Physical Review A (target)
**Status**: Complete, pending arXiv submission

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

**Key result**: Generator norm $\leq 2$ is the controlling invariant for KS-uncolorability in dimension 3.

---

## PRL Letters

### 1. New KS Sets from Algebraic Number Fields with Enhanced Contextual Advantage

**Length**: 3 pages
**Venue**: Physical Review Letters (target)
**Status**: Complete, all peer review items addressed

Introduces the Heegner-7 (43 vectors) and Golden ratio (52 vectors) KS sets — the first genuinely new 3D KS constructions in decades. Reports the enhanced contextual advantage of Heegner-7 ($\theta/\alpha = 1.118$) and the cross-product discovery mechanism for the Golden set.

**Key result**: Two genuinely new KS sets, neither in any prior catalogue, with the highest known contextual advantage in 3D.

---

### 2. Graph Universality of CK-31 and the Norm-2 Boundary

**Length**: 3 pages
**Venue**: Physical Review Letters (target)
**Status**: Complete, all peer review items addressed

Proves that all 31-vertex KS sets share the same orthogonality graph (VF2-verified graph and hypergraph isomorphism). Establishes the norm-2 boundary: rings with generator norm $> 2$ produce colorable pools regardless of size.

**Key result**: The CK-31 graph is the unique minimal KS graph in 3D integer-type constructions.

---

### 3. Computational Evidence for the Optimality of CK-31

**Length**: 5 pages
**Venue**: Physical Review Letters (target)
**Status**: Complete, OCUS proof and merge saturation added

Presents six independent computational strategies that all fail to find a sub-31 KS set. Includes the OCUS exhaustive proof for the integer pool, 8-criticality of CK-31, cross-pool mixing results, and the merge saturation universal property.

**Key result**: No sub-31 KS set exists by any known method; CK-31 is 8-critical and merge-saturated.

---

### 4. Kochen-Specker Uncolorability in Cyclotomic Fields Requires Exactly 6|n

**Length**: 4 pages
**Venue**: Physical Review Letters (target)
**Status**: Complete, all peer review items resolved (6 rounds)

The only letter with a complete algebraic proof (no computational evidence needed). Proves that the cyclotomic ray pool $S_n$ is KS-uncolorable if and only if $6|n$, via seven lemmas covering sufficiency and three necessity cases.

**Key result**: Complete characterization of KS-uncolorability across all cyclotomic fields, connecting to $\mathbb{Z}[1/6]$ minimality.

---

## Peer Review

All papers have undergone multiple rounds of GPT-based peer review (GPT-5.2 Pro via OpenAI API), with all issues resolved. Review transcripts are archived in `claude-inbox/peer-reviews/`.

| Paper | Rounds | Final verdict |
|-------|--------|---------------|
| Main paper | 1 (Major Revision → addressed) | Ready |
| Heegner-7 letter | 2 | Ready |
| Universality letter | 2 | Ready |
| Sub-31 letter | 5 | Ready |
| Cyclotomic letter | 6 | Ready |

---

## Computational Reproducibility

All results are reproducible via Python scripts in the `contextuality/` repository. Key dependencies: Python 3.11, PySAT 1.8 (Glucose4), NumPy, SciPy. All scripts use `random.seed(42)` for reproducibility.

---

## Related Pages

- [The Six Algebraic Islands](algebraic-islands.md) — Central classification result
- [Research Overview](index.md) — Programme summary
- [Bibliography](../bibliography.md) — Full reference list
