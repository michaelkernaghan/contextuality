---
date: 2026-04-03
type: query-output
question: What is the smallest known KS set in 3 dimensions?
---

# What is the smallest known KS set in 3 dimensions?

## Answer

**The smallest known KS set in 3 dimensions is CK-31 (Conway-Kochen), with 31 vectors and 17 orthogonal bases.** It has stood as the record since its discovery (communicated to Peres ~1990).

Key facts:

- **Lower bound**: Any KS set in C^3 must have at least **24 vectors**, proven by SAT+CAS computation with a 40.3 TiB DRAT certificate ([[li-2024-sat-ks]])
- **Upper bound**: CK-31 at **31 vectors** is the smallest known ([[trandafir-cabello-2025-rigid-ks]], [[sub31-letter]])
- **The 24-31 gap is open**: Seven complementary search strategies in [[sub31-letter]] found no sub-31 KS set. 61,702 abstract sub-31 KS-uncolorable hypergraphs exist but none embed in R^3.
- **CK-31 is rigid**: unique up to unitary transformations, proved via 2-neighbor bootstrap percolation ([[trandafir-cabello-2025-rigid-ks]])
- **CK-31 is deletion-minimal**: removing any single ray yields a colorable set
- **Uniqueness conjecture**: All tested algebraic alphabets converge to the same CK-31 graph ([[universality-letter]])

Note: if the question is about fewest *bases* rather than fewest *vectors*, the record is Cabello's 2025 construction — 33 vectors but only 14 bases, beating Peres's 33-vector/16-basis set ([[cabello-2025-simplest-ks]], [[peres-33-3d]])

## Sources Consulted

- [[ks-set]] — definition, bounds table, key examples
- [[peres-33-3d]] — historical record holder, relationship to CK-31
- [[sub31-letter]] — comprehensive sub-31 search, seven strategies, all negative
- [[li-2024-sat-ks]] — SAT proof of >=24 lower bound
- [[trandafir-cabello-2025-rigid-ks]] — rigidity of CK-31, the 31-minimum conjecture

## Gaps

- No wiki article yet on Conway-Kochen specifically (CK-31 documented across multiple articles but has no dedicated page)
- The original unpublished CK-31 communication is not in the corpus
