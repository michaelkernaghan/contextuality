---
date_ingested: 2026-04-03
type: concept
---

# Peres 33-Vector KS Set (d=3)

## Definition

The Peres 33-vector KS set is a set of 33 unit vectors in C^3 forming 16 orthogonal bases (triples) that admit no valid KS coloring. Constructed by Asher Peres in 1991, it held the record as the smallest known KS set in dimension 3 for over 30 years. It belongs to the **Peres algebraic island**: its vector entries are drawn from the ring Z[√2], exploiting the modulus-2 cancellation identity |√2|^2 = 2.

## Key Results

- **Record status**: The Peres set was the smallest known KS set in d=3 by basis count until 2025, when [[cabello-2025-simplest-ks]] produced a 33-vector set with only 14 bases (beating the Peres 16-basis count), making Peres no longer the "simplest" by that measure
- **Graph isomorphism**: [[algebraic-islands-main]] and [[universality-letter]] establish that the Peres minimal 33-vector set is graph-isomorphic to the minimal 33-vector KS set from Z[√(−2)] — two different algebraic islands producing the same orthogonality graph
- **Rigidity**: [[trandafir-cabello-2025-rigid-ks]] compares CK-31 with the Peres-33 set; both arise from the minimal SI-C (Yu-Oh) starting point via different basis completion orderings, though Peres-33 is not itself proved rigid in that paper
- The Peres set is distinct as a graph from the Eisenstein 33-vector set (Z[ω]) and from the Schutte family, confirming that at 33 vectors multiple non-isomorphic KS graphs coexist ([[universality-letter]])
- **Connection to CK-31**: the Peres construction uses the same Yu-Oh SI-C starting material as CK-31; different completion orderings yield 31- vs. 33-element sets
- From the Peres-24 construction (a related 24-element set from Peres's work), the smallest known bipartite perfect quantum strategy for a 3×3 input scenario can be derived ([[trandafir-cabello-2025-optimal-bpqs]])

## Connections

- [[ks-set]] — the Peres set is a canonical example; its replacement as the simplest-by-bases is documented in [[cabello-2025-simplest-ks]]
- [[algebraic-islands]] — the Peres field Z[√2] is one of the six algebraic islands
- [[kochen-specker-theorem]] — the Peres set is a proof of the theorem
- [[cabello-2025-simplest-ks]] — the paper that beat the Peres 16-basis record with 14 bases
- [[trandafir-cabello-2025-rigid-ks]] — context on how Peres-33 and CK-31 relate structurally
- [[universality-letter]] — establishes graph isomorphism between Peres and Z[√(−2)] minimal sets

## In Our Work

The Peres 33-vector set is the canonical representative of the Z[√2] algebraic island in [[algebraic-islands-main]]. Its graph isomorphism with the Z[√(−2)] minimal set (despite different coordinate rings) is one of the structural surprises of the algebraic islands program — it suggests the graph structure of a KS set is not a faithful invariant of its algebraic origin, at least at 33 vectors. At 31 vectors, the apparent uniqueness of the CK-31 graph makes the analogy more interesting.

## Open Questions

- Is the Peres-33 set rigid (unique up to unitary equivalence)?
- Why do Z[√2] and Z[√(−2)] produce graph-isomorphic minimal sets, despite being different rings? Is there a ring-theoretic explanation?
- Does the Peres-33 graph appear as the orthogonality graph of any KS set from a non-modulus-2 island?
