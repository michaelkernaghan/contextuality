---
date_ingested: 2026-04-03
type: concept
---

# Algebraic Islands

## Definition

The algebraic islands are a discrete set of algebraic number rings that support [[kochen-specker-theorem|KS-uncolorable]] ray sets in C^3. The central empirical finding of [[algebraic-islands-main]] is that KS-uncolorability in two-symbol coordinate alphabets {0, ±1, ±x} requires exactly one of two mechanisms:

- **Modulus-2 cancellation**: the generator satisfies |x|^2 = 2 (e.g., x = √2, x = i√2, x = (1+i))
- **Phase cancellation**: x is a root of unity with a vanishing sum 1 + ω + ω^2 = 0 (i.e., 3rd or 6th roots of unity)

Alphabets whose generators have |x|^2 ≥ 3 and are not roots of unity produce orthogonal triples but not KS-uncolorability. The islands are therefore not a continuous family but isolated discrete cases.

## The Six Islands

| Island | Ring | Minimum KS set |
|--------|------|---------------|
| Integer | Z (integers) | CK-31 (31 vectors) |
| Peres | Z[√2] | 33 vectors |
| Eisenstein | Z[ω], ω = e^{2πi/3} | 33 vectors |
| Z[√(−2)] | Z[i√2] | 33 vectors |
| Heegner-7 | Z[(1+√(−7))/2] | 43 vectors (new) |
| Golden ratio | Q(φ) | 52 vectors (new) |

A seventh cubic island (Q(∛2) extended) is confirmed at 60 vectors. The Heegner-7 and golden ratio islands were first reported in [[algebraic-islands-main]] and developed further in [[heegner7-letter]].

## Key Results

- All six islands are identified by systematic search over 40+ number fields using cross-product completion and SAT-based uncolorability testing
- The [[cyclotomic-letter]] proves the sharp result: S_n is KS-uncolorable if and only if 6|n — the cyclotomic classification is complete
- [[universality-letter]] finds that all 31-ray minimal sets across tested alphabets are graph-isomorphic (the CK-31 graph), raising the uniqueness conjecture
- Peres (Z[√2]) and Z[√(−2)] minimal sets are graph-isomorphic despite arising from different rings
- Different islands yield different CSW contextual advantages; no island dominates all operational measures

## Connections

- [[kochen-specker-theorem]] — each island provides a proof
- [[ks-set]] — the specific minimal configurations within each island
- [[cyclotomic-fields]] — the cyclotomic island and the 6|n theorem
- [[peres-33-3d]] — one of the six islands
- [[algebraic-islands-main]] — the source paper for this classification
- [[universality-letter]] — graph-isomorphism observations across islands

## In Our Work

The algebraic islands classification is the central organizing framework of our research program. The six-island table is reproduced in condensed form in [[universality-letter]] and expanded upon in the companion letters [[cyclotomic-letter]], [[heegner7-letter]], [[sub31-letter]], and [[sub31-overview]].

## Open Questions

- Does the two-mechanism pattern extend to all number fields, or is there a third mechanism in unexplored higher-degree extensions?
- Is cross-product completion termination provable, or only observed empirically?
- Are the Heegner-7 and golden ratio islands truly new, or do they appear under different coordinates in existing KS catalogs?
- What is the exact minimum KS subset size within the Heegner-7 and golden ratio pools?
