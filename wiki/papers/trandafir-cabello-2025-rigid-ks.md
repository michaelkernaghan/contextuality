---
source: references/corpus/TrandafirCabello2025-rigid-KS-2501.11640.pdf
date_ingested: 2026-04-03
type: paper
---

# Rigid Kochen-Specker Sets in Three Dimensions (Trandafir & Cabello, 2025)

## Summary

This paper establishes two new rigid Kochen-Specker sets in C^3, where *rigid* means the set is unique up to unitary transformations — a property critical for Bell self-testing and for certifying quantum observables without prior knowledge of the state. The constructions proceed from two distinct starting points: the super-symmetric SIC-POVM (Hesse SIC) and the minimal state-independent contextuality (SI-C) set.

Starting from the Hesse SIC (the SIC covariant under the full Clifford group in C^3), the authors apply the BBC-21 construction to obtain a KS set of 81 elements (KS-81). They prove this set is rigid.

Starting from the minimal SI-C set — the 13-element Yu-Oh set — the authors iteratively complete orthogonal bases to generate successively larger sets: CK-37, then CK-33, then the 31-element set CK-31. CK-31 and CK-33 are both proved rigid. Rigidity of CK-31 is established using 2-neighbor bootstrap percolation on the orthogonality graph. The paper also proves that no KS set of 30 or fewer elements can be obtained from the minimal SI-C set via this completion procedure, and conjectures that 31 is the minimum number of elements in any C^3 KS set.

## Key Claims

- KS-81 (derived from the Hesse super-SIC) is a rigid KS set in C^3
- CK-31 is a rigid KS set in C^3 with 31 elements; it is the smallest known rigid KS set in C^3
- CK-33 is a rigid KS set in C^3 with 33 elements
- No KS set of <=30 elements can be obtained from the minimal SI-C (Yu-Oh) set via basis completion
- Conjecture: 31 is the minimum number of elements in any C^3 KS set
- Rigidity of CK-31 is proved via 2-neighbor bootstrap percolation on the orthogonality hypergraph
- Rigid KS sets enable Bell self-testing: any full-rank state on the Hilbert space suffices to certify the observables

## Methods

- Construction 1 (KS-81): Hesse SIC-POVM embedded in C^3 via BBC-21 construction; coordinates lie in the cyclotomic field Q(omega) where omega = e^{2*pi*i/3}
- Construction 2 (CK-31): iterative basis completion starting from the 13-element Yu-Oh SI-C set; add any vector completing an orthogonal basis for each context, repeat until closed
- Rigidity proof: 2-neighbor bootstrap percolation — show that fixing any two orthogonal rays in the set forces all remaining rays by orthogonality propagation
- Comparison of CK-31 with Peres-33: CK-31 is smaller but both arise from the same minimal SI-C starting point via different completion orderings

## Relevance to Our Work

- CK-31 and CK-33 are KS sets in the integer ring Z[omega] (Eisenstein integers), the same algebraic island studied in [[algebraic-islands-main]]
- The conjecture that 31 is the minimum C^3 KS set size directly bears on the OCUS-certified lower bound of <=30 established in [[algebraic-islands-main]] for the integer pool
- Rigidity connects to our Jacobian-based rigidity analysis; the bootstrap percolation method is an alternative rigidity criterion worth comparing
- The BBC-21 construction from the Hesse SIC is a route to KS-81; our algebraic islands paper does not yet explore SIC-based constructions
- See also [[li-2024-sat-ks]] for the SAT-based lower bound proof that any C^3 KS set needs >=24 vectors
- See also [[trandafir-cabello-2025-optimal-bpqs]] for how CK-31 and related sets generate optimal bipartite perfect quantum strategies

## Open Questions

- Is 31 truly the minimum? The SAT lower bound gives >=24; closing the gap from 24 to 31 remains open
- Are there rigid KS sets with fewer than 31 elements not constructible from the Yu-Oh SI-C set?
- Does bootstrap percolation give a general rigidity criterion applicable to the other algebraic islands?
- Can the Hesse SIC route (KS-81) be pruned to a smaller rigid set?
