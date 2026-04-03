---
title: "Kochen-Specker Vectors"
slug: pavicic-2005-ks-vectors
authors: ["Mladen Pavičić", "Jean-Pierre Merlet", "Brendan McKay", "Norman D. Megill"]
year: 2005
journal: "Journal of Physics A: Mathematical and General"
doi: "10.1088/0305-4470/38/7/013"
tags: [kochen-specker, MMP-hypergraph, exhaustive-generation, 4D, coloring]
status: read
---

# Kochen-Specker Vectors

## Summary

This paper establishes a constructive, exhaustive characterization of Kochen-Specker (KS) vectors in four-dimensional Hilbert space. The authors introduce a rigorous definition of KS vectors via the MMP (McKay-Megill-Pavičić) hypergraph language and deploy interval analysis together with a computer-assisted search to generate all 4D KS systems up to 24 vectors. The method is both constructive (producing explicit vector sets) and exhaustive (proving completeness within the bound).

## Core Contributions

- **Formal definition of KS vectors**: A set of unit vectors in ℝ⁴ (or ℂ⁴) is KS if it admits no consistent 0-1 coloring respecting orthogonality — i.e., no assignment {0,1} to each vector such that (i) exactly one vector in every orthogonal basis receives 1, and (ii) orthogonal vectors are not both assigned 1.
- **MMP hypergraph encoding**: Orthogonality relations among vectors are encoded as hyperedges; the coloring problem becomes a hypergraph coloring problem, enabling computer search.
- **Exhaustive generation up to 24 vectors in 4D**: All non-isomorphic KS systems with ≤24 vectors are enumerated. This encompasses Kernaghan's 20-vector system (noted as a key landmark) and pushes the boundary systematically.
- **Interval analysis for coordinatization**: After identifying combinatorial KS configurations, interval arithmetic verifies that real or complex coordinate assignments exist — separating combinatorially uncolorable hypergraphs that have no geometric realization from genuine KS sets.

## Key Results

| Dimension | Vector count | Status |
|-----------|-------------|--------|
| 4D        | 18 (minimum known at time) | KS set exists |
| 4D        | 20 | Kernaghan's set |
| 4D        | ≤24 | All enumerated |

The paper demonstrates that the search space, while large, is tractable through the MMP representation combined with efficient isomorphism rejection.

## Methods

1. **MMP language**: Vectors are labeled by integers; bases (maximal orthogonal sets) are listed as hyperedges. A KS proof is a hypergraph with no valid 0-1 coloring.
2. **Generation algorithm**: Start from small hypergraphs, extend by adding vectors/bases, check coloring via constraint propagation.
3. **Interval verification**: For each combinatorial KS candidate, construct real coordinates using interval arithmetic to certify geometric realizability.

## Connections to Existing Wiki Articles

- [[kochen-specker-theorem]] — foundational theorem this paper operationalizes
- [[ks-set]] — the combinatorial objects systematically classified here
- [[graph-contextuality]] — MMP hypergraphs are the precursor formalism to graph-theoretic approaches
- [[algebraic-islands-main]] — the algebraic approach to contextuality complements this combinatorial/geometric one

## Open Questions Raised

- What is the minimum number of vectors for a KS set in 4D? (18 was a candidate; later work pushed this.)
- Can the MMP method extend efficiently to higher dimensions?

## Citation

Pavičić, M., Merlet, J.-P., McKay, B., & Megill, N. D. (2005). Kochen-Specker vectors. *Journal of Physics A: Mathematical and General*, 38(7), 1577–1592. https://doi.org/10.1088/0305-4470/38/7/013
