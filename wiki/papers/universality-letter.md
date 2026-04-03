---
source: paper/universality_letter.tex
date_ingested: 2026-04-03
type: paper
---

# Graph Isomorphism of 31-Vertex Kochen-Specker Sets Across Coordinate Alphabets in Dimension Three (Kernaghan, 2026)

## Summary

This PRL-format letter presents a computational survey of coordinate alphabets for [[kochen-specker-theorem|KS]] constructions in dimension 3 and reports a graph universality observation: in three alphabet-based search instances that yielded 31-ray [[ks-set|KS subsets]], the minimized subsets are mutually graph-isomorphic (verified by the VF2 algorithm). The letter identifies six discrete [[algebraic-islands|algebraic islands]] and their corresponding graph types, and states two formal conjectures - that 31 is optimal and that CK-31 is the unique 31-ray KS graph up to isomorphism.

The letter is careful to note an important caveat: the three 31-ray search instances (integer alphabet, rational Z[1/2] alphabet, and a mixed-alphabet) may not be genuinely independent, because the rational and mixed alphabets contain the integer alphabet as a subset (the rational alphabet is projectively equivalent to the integer alphabet after canonicalization, and the mixed alphabet contains the integer alphabet directly). The convergence to the same graph may simply reflect rediscovery of the embedded Conway-Kochen configuration rather than true algebraic universality. This caveat is stated explicitly and prominently.

The letter also surveys the modulus-2 cancellation boundary across 40+ number fields, providing the most condensed version of the algebraic classification developed in [[algebraic-islands-main]]. It notes that at 33 vectors, multiple non-isomorphic KS graphs coexist (the Schutte set has a different graph from the Peres/Penrose family, which Cabello's Eisenstein set also differs from), making the apparent uniqueness at 31 vectors at least noteworthy. The cubic field Q(cbrt(2)) extended alphabet is reported as producing a KS set at 60 vectors, suggesting the modulus-2 pattern extends but with rapidly increasing cost.

## Key Claims

- Conjectures (two independent): (1) Optimality: no KS set with 30 or fewer rays exists in dimension 3; (2) Uniqueness: CK-31 is the unique 31-ray KS graph up to isomorphism
- Graph universality observation: all three 31-ray search instances produce graph-isomorphic KS sets (VF2-verified), with identical invariants: 31 vertices, 71 edges, 17 bases, degree sequence (3^4, 4^14, 5^8, 6^3, 8^2), 17 triangles, tr(A^4)=1250, spectral radius 4.9443, WL-1 indistinguishable
- Important caveat: the three search instances may not be independent (rational alphabet projectively equivalent to integer alphabet; mixed alphabet contains integer alphabet); the observation is consistent with uniqueness but does not prove it
- At 33 vectors, multiple non-isomorphic KS graphs coexist (Schutte set, Peres/Penrose family, Eisenstein set); uniqueness at 31 is therefore a non-trivial observation if genuine
- Peres and Z[sqrt(-2)] minimal sets are graph-isomorphic (the two 33-vector sets from modulus-2 cancellation share the same orthogonality graph)
- Heegner-7 (43 vectors) and golden ratio (52 vectors) are new graph types not matching any of the four previously known algebraic KS families
- In C^3, every triangle in the orthogonality graph is already a basis triple (any two orthogonal rays determine a unique third), so graph isomorphism implies basis hypergraph isomorphism
- The modulus-2 cancellation boundary holds for all 40+ tested fields: KS-uncolorable sets found only when the effective coordinate set (after completion) supports |x|^2=2 or phase cancellation
- For two-element alphabets {0,+/-1,+/-x}, enumerating all three-term zero-sums from the product set yields exactly four non-trivial identities: x=2, |x|^2=2, |x|^2=x+1, x^2+x+1=0 - each corresponding to a known island; enumeration is complete for two-element alphabets
- Cubic field Q(cbrt(2)): basic alphabet colorable; extended alphabet {0,+/-1,+/-cbrt(2),+/-cbrt(4)} uncolorable via completion, minimum 60 vectors
- 30,000+ random KS-uncolorable 3-uniform hypergraphs on 31 vertices generated and tested for realizability in R^3 via SAT-encoded orthogonality constraints - none geometrically realizable
- The algebraic alphabet method is outside the two construction families (dimension-lifting and concatenation) analyzed in Trandafir-Cabello Appendix B as unable to produce rigid KS sets in C^3; the algebraic approach yields rigid sets (unique up to unitary equivalence) in four of six islands

## Methods

- Coordinate alphabet construction from 40+ algebraic number rings (quadratic fields Q(sqrt(d)) for d=2..30, all nine class-1 imaginary quadratic fields, cyclotomic fields n<=30, golden ratio, cubic extensions)
- Hermitian orthogonal completion (cofactor formula) until ray pool stabilizes
- SAT-based KS-uncolorability testing (Glucose4 via PySAT)
- Randomized greedy deletion minimization (500 trials, seed 42)
- VF2 isomorphism algorithm (via NetworkX) for pairwise graph isomorphism testing with explicit vertex mappings
- Graph invariant computation: degree sequence, tr(A^4), spectral radius, Weisfeiler-Leman 1-stable coloring
- SAT-encoded realizability testing: Boolean assignment of vertices to pool rays with orthogonality and injectivity constraints
- Cyclotomic field analysis: KS-uncolorability observed when 6|n (for n<=30 cyclotomic fields), consistent with the Eisenstein embedding

## Relevance to Our Work

- The uniqueness conjecture is the key claim directly motivated by all the computational evidence in [[sub31-letter]] and [[sub31-overview]]
- The graph universality observation provides the sharpest current evidence that CK-31 is the unique minimal KS configuration
- The six-island classification table (Table tab:islands) is the most concise version of the [[algebraic-islands]] framework from [[algebraic-islands-main]]
- The explicit statement that Peres and Z[sqrt(-2)] produce graph-isomorphic sets connects to [[algebraic-islands-main]]'s Proposition (prop:isomorphism)
- The modulus-2 cancellation boundary survey covers the same ground as [[algebraic-islands-main]] in condensed form
- The Trandafir-Cabello rigidity connection provides external support for the uniqueness conjecture
- Cross-links to [[peres-33-3d]], [[cyclotomic-fields]], [[ks-set]], [[kochen-specker-theorem]], [[graph-contextuality]]
- The cubic field result (60 vectors) extends the algebraic islands beyond the six main ones into higher-degree fields

## Open Questions

- Are the three search instances genuinely independent, or do they all simply rediscover the embedded CK configuration? Could a genuinely independent algebraic path to a 31-ray KS set be found?
- Is CK-31 actually the unique 31-ray KS graph up to isomorphism, or are there other 31-ray KS graphs not accessible by the current search strategies?
- Could there exist a KS set of 31 rays with a *different* graph that appears only in some as-yet-untested number field?
- How does the cubic field result (60 vectors from Q(cbrt(2)) extended) relate to the general pattern? Do higher-degree fields consistently require more vectors?
- Can the algebraic alphabet method's rigidity (producing rigid sets in four of six islands) be proved in general, or only verified computationally case by case?
- Does the absence of KS-uncolorability in Z[sqrt(-3)] (despite Z[omega] = Eisenstein integers being uncolorable) have a deeper algebraic explanation beyond the alphabet distinction?
