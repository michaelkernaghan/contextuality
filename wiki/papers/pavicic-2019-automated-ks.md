---
title: "Automated Generation of Kochen-Specker Sets"
slug: pavicic-2019-automated-ks
authors: ["Mladen Pavičić"]
year: 2019
journal: "Scientific Reports"
doi: "10.1038/s41598-019-41576-3"
tags: [kochen-specker, MMP-hypergraph, automated-generation, master-sets, 4D, 6D, omega-coordinatization]
status: read
---

# Automated Generation of Kochen-Specker Sets

## Summary

This paper introduces an automated, downward-generation algorithm for exhaustively producing Kochen-Specker (KS) sets by working from large "master sets" — complete sets of vectors with integer coordinates from {−1, 0, 1} — and pruning down to minimal KS subsets. Applied to 4D, it reproduces all 1233 known KS sets (as of 2019) in seconds. The method extends to 6D via an ω-coordinatization using complex components, dramatically expanding the frontier of known KS sets.

## Core Contributions

- **Master set approach**: Rather than building KS sets bottom-up (adding vectors), the algorithm starts from the maximal set of vectors with components in {−1, 0, 1} (or ω-based for 6D) and removes vectors/bases while checking that the remaining hypergraph retains uncolorability.
- **Downward generation**: Produces all non-isomorphic KS sets as sub-hypergraphs of the master set; completeness follows from the exhaustiveness of the master set.
- **4D completeness**: Reproduces all 1233 known 4D KS sets in a few seconds of computation — a dramatic speedup over prior bottom-up methods.
- **6D extension via ω-coordinatization**: Introduces vectors whose components involve the cube root of unity ω = e^{2πi/3}, enabling systematic exploration of 6D KS sets unreachable by real-integer coordinates.

## Key Results

| Dimension | Coordinate set | Output |
|-----------|---------------|--------|
| 4D | {−1, 0, 1} | All 1233 known KS sets reproduced |
| 6D | {0, ±1, ω, ω², ω̄, ω̄²} | New KS sets generated |

The ω-coordinatization connects to number-theoretic structure: the vectors live in a module over Z[ω], the ring of Eisenstein integers, which has natural links to [[cyclotomic-fields]].

## Algorithm Outline

1. **Construct master hypergraph**: Enumerate all unit vectors with components in the chosen set; record all maximal orthogonal bases as hyperedges.
2. **Check colorability of master**: The master set itself is typically uncolorable (a KS set).
3. **Downward search**: Systematically remove one vector or basis at a time; retain sub-hypergraphs that remain uncolorable; record minimal ones.
4. **Isomorphism rejection**: Use graph isomorphism tools (nauty/traces) to eliminate duplicates.

## Methods

- MMP hypergraph language (see [[pavicic-2005-ks-vectors]]) for encoding orthogonality
- Constraint propagation for rapid colorability checking
- Nauty/Traces for isomorphism filtering
- C implementation for speed

## Connections to Existing Wiki Articles

- [[kochen-specker-theorem]] — theorem the generated sets witness
- [[ks-set]] — the combinatorial objects produced
- [[pavicic-2005-ks-vectors]] — predecessor paper establishing the MMP approach
- [[algebraic-islands-main]] — algebraic hidden-state approach contrasts with this combinatorial approach
- [[cyclotomic-fields]] — ω-coordinatization situates KS vectors in cyclotomic/Eisenstein number fields

## Significance

The master-set / downward-generation paradigm shifts KS search from needle-in-haystack enumeration to principled pruning. The 6D ω-case shows that KS structure is sensitive to the arithmetic of the coordinate ring — a bridge to the algebraic contextuality program in [[cortez-2022-minimal-ring]].

## Citation

Pavičić, M. (2019). Automated generation of Kochen-Specker sets. *Scientific Reports*, 9, 6765. https://doi.org/10.1038/s41598-019-41576-3
