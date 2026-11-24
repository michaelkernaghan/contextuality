# Papers

<!-- v11-notice -->
!!! warning "This page was written for versions 1-9 of the paper and is partly withdrawn"
    The classification by "cancellation mechanisms" and "algebraic islands" described in
    versions 1-9 of *The Algebraic Landscape of Kochen-Specker Sets in Dimension Three* did not
    survive checking and has been withdrawn. Withdrawn claims include: the list of four, six or
    eight "islands"; the "norm bound" (generator norm at most 2); the golden-ratio minimum of 52
    (a 51-ray set exists); "merge saturation"; "graph universality"; the tables of BPQS and
    Cabello-Severini-Winter quantities; and every statement that a set is "new" or "not
    previously reported". This page has not been rewritten. For what is currently claimed, and
    with what standard of proof, see [version 11 of the paper](https://github.com/michaelkernaghan/contextuality/blob/main/paper/algebraic_islands_v11.pdf) (Appendix A lists the
    withdrawals) and the [status ledger](https://github.com/michaelkernaghan/contextuality/blob/main/LEDGER.md).

## Overview

The algebraic islands research programme produced one main paper. Five short letters written alongside versions 1-9 were never revised. They are kept as a record in [`archive/letters/`](https://github.com/michaelkernaghan/contextuality/tree/main/archive/letters), with a note on what stands and what does not.

**Author**: Michael Kernaghan, Pacific Quantum Systems, Vancouver, Canada

---

## Main Paper

### The Algebraic Landscape of Kochen-Specker Sets in Dimension Three

**Length**: ~39 pages
**Venue**: Physical Review A (target)
**Status**: Complete, pending arXiv submission
**[PDF of version 9 (archived, withdrawn)](https://github.com/michaelkernaghan/contextuality/blob/main/archive/paper/algebraic_islands.pdf)**

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

## Computational Reproducibility

All results are reproducible via Python scripts in the `contextuality/` repository. Key dependencies: Python 3.11, PySAT 1.8 (Glucose4), NumPy, SciPy. All scripts use `random.seed(42)` for reproducibility.

---

## Related Pages

- [The Six Algebraic Islands](algebraic-islands.md) — Central classification result
- [Research Overview](index.md) — Programme summary
- [Bibliography](../bibliography.md) — Full reference list
