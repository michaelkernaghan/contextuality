---
date_ingested: 2026-04-03
type: concept
---

# KS Set

## Definition

A Kochen-Specker (KS) set is a finite set of unit vectors in a Hilbert space H (dim ≥ 3) for which no valid KS coloring exists. A **KS coloring** is a function assigning values in {0, 1} to every vector in the set such that:

1. **Completeness**: exactly one vector in every orthogonal basis (maximal context) receives the value 1
2. **Exclusivity**: orthogonal vectors receive different values (at most one 1 per orthogonal pair)

A KS set therefore provides a finite combinatorial proof of the [[kochen-specker-theorem]]: the impossibility of a noncontextual hidden-variable model.

## Key Examples and Bounds

| Set | Dimension | Vectors | Bases | Notes |
|-----|-----------|---------|-------|-------|
| Original Kochen-Specker | R^3 | 117 | — | First proof (1967) |
| Peres 1991 | C^3 | 33 | 16 | Long-standing record in d=3 |
| Cabello-Kleinmann-Portillo 2025 | C^3 | 33 | 14 | Current record: fewest bases ([[cabello-2025-simplest-ks]]) |
| CK-31 | C^3 | 31 | 17 | Smallest known in d=3; rigid ([[trandafir-cabello-2025-rigid-ks]]) |
| Cabello-Estebaranz-Garcia-Alcaine | R^4 | 18 | — | Smallest known in d=4 |

**Lower bound (d=3)**: any KS set in C^3 must contain at least 24 vectors, proven by SAT+CAS computation with a 40.3 TiB DRAT certificate ([[li-2024-sat-ks]]). The gap from 24 to 31 remains open.

## Structural Properties

- In C^3, every two orthogonal vectors determine a unique third completing an orthogonal basis, so the basis hypergraph is fully determined by the orthogonality graph
- **Rigidity**: a KS set is rigid if it is unique up to unitary transformations; CK-31 and CK-33 are both rigid ([[trandafir-cabello-2025-rigid-ks]]), enabling Bell self-testing
- The [[universality-letter]] observes that all tested 31-ray minimizations across different algebraic alphabets converge to the same CK-31 graph (degree sequence 3^4, 4^14, 5^8, 6^3, 8^2; 17 bases; tr(A^4) = 1250)

## Connections

- [[kochen-specker-theorem]] — the impossibility result that KS sets witness
- [[algebraic-islands]] — the algebraic classification of which number rings support KS sets
- [[peres-33-3d]] — the long-standing record holder in d=3
- [[li-2024-sat-ks]] — SAT-based proof of the ≥ 24 lower bound
- [[cabello-2025-simplest-ks]] — current record by basis count
- [[trandafir-cabello-2025-rigid-ks]] — rigidity and the 31-vector CK-31 set
- [[graph-contextuality]] — KS sets define exclusivity/orthogonality graphs used in the CSW framework

## In Our Work

The [[algebraic-islands-main]] paper classifies KS sets by algebraic origin, finding six discrete [[algebraic-islands]] each yielding minimal KS sets of different sizes (31–52 vectors). The OCUS-certified result establishes that the 49-ray integer pool contains no KS-uncolorable subset of ≤ 30 rays. Cross-product completion is the generation method; Glucose4 SAT solver tests uncolorability.

## Open Questions

- Does any KS set with fewer than 31 vectors exist in C^3? The bounds are [24, 31]
- Is CK-31 the unique 31-ray KS graph up to isomorphism (the uniqueness conjecture of [[universality-letter]])?
- Can the ≥ 24 lower bound be pushed closer to 31 without a TiB-scale certificate?
