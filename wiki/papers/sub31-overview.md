---
source: paper/sub31_overview.tex
date_ingested: 2026-04-03
type: paper
---

# The 24-31 Gap: Computational Methods and Structural Barriers for Minimal Kochen-Specker Sets in Dimension Three (Kernaghan, 2026)

## Summary

This extended companion paper to [[sub31-letter]] provides a comprehensive survey of the [[kochen-specker-theorem|KS]] minimality problem in dimension 3, covering the history of the 24-31 gap, a detailed methodology description, eight complementary search strategies, and a structural analysis of why current methods cannot close the gap. The paper is explicitly framed as an exploration addressed to researchers in quantum foundations, combinatorics, and automated reasoning.

The paper establishes the same core negative result as [[sub31-letter]] - no KS set with fewer than 31 vectors is found by any of eight strategies - but develops the structural analysis much further. The central structural contribution is the *realizability barrier* concept: abstract sub-31 KS-uncolorable hypergraphs exist in abundance (about 12% of valid graph perturbations of CK-31 yield uncolorable sub-31 hypergraphs), but none can be embedded as rays in R^3. The paper argues that this realizability barrier is the core obstruction, not the combinatorial structure of the coloring problem itself.

The paper provides extensive historical background: the original Kochen-Specker 117-ray proof (1967), Peres's 33-ray reduction (1991), the Conway-Kochen 31-ray set (reported ~1990), the progression of lower bounds from 18 (Arends et al.) to 22 (Uijlen-Westerbaan) to 24 (Li-Bright-Ganesh and Kirchweger-Peitl-Szeider), and the Trandafir-Cabello rigidity result. It also introduces the *plane matching property* as a candidate geometric constraint for future proof attempts.

## Key Claims

- No sub-31 KS set found by any of eight strategies (same conclusion as [[sub31-letter]] but with extended strategy set and structural analysis)
- OCUS certification: 31 is the exact minimum within the 49-ray integer pool {0,+/-1,+/-2}^3
- The current gap: 24 <= n_min^(3) <= 31; lower bound established by Li-Bright-Ganesh and Kirchweger-Peitl-Szeider (2023)
- Realizability barrier: graph perturbation search finds 61,702 abstract sub-31 KS-uncolorable hypergraphs; numerical optimization finds no R^3 embedding (best residual 3.8e-2)
- Vertex-merging analysis: 394 distinct 30-vertex KS graphs derived from CK-31; all proved unrealizable within the integer pool by finite SAT encoding (<1s each)
- Modulus-2 boundary: among integer-like alphabets {0,+/-1,+/-x}, only those where |x|^2 = 2 (or x=2) produce KS-uncolorable pools
- The plane matching property: a candidate geometric constraint for future proof attempts (requirement that every ray participate in sufficiently many orthogonal triples from a geodesically constrained configuration)
- Historical progression of upper bounds: 117 (KS 1967) -> 33 (Peres 1991) -> 31 (Conway-Kochen ~1990); lower bounds: 18 (Arends et al.) -> 22 (Uijlen-Westerbaan 2016) -> 24 (Li-Bright-Ganesh / Kirchweger et al., 2023)
- Trandafir-Cabello rigidity: CK-31 is unique up to unitary equivalence in C^3; they conjecture n_min^(3) = 31 under two assumptions (minimum set is rigid; minimum set contains minimal SI-C set)
- Density arguments are insufficient for a proof: KS-uncolorability depends on precise topological interlocking of basis constraints, not just triad/pair counts
- Closing the gap may require realizability-based arguments (extending the Li-Bright-Ganesh framework) rather than combinatorial density bounds
- Observes that the gap could also be narrowed from below: improving the lower bound from 24 to, say, 28 or 29 via stronger SAT encodings would be equally significant
- Working in C^3 does not help: all complex pools minimize to >=33

## Methods

- All methods from [[sub31-letter]] (SAT minimization, OCUS, MUS extraction, cross-pool mixing, expanded alphabets, numerical optimization, exhaustive criticality, triad density, graph perturbation, vertex merging)
- Extended: 8 strategies vs. 7 in the letter (the overview explicitly lists 8; the letter lists 7)
- Historical literature survey: systematic organization of prior work around upper bounds, lower bounds, rigidity results, and algebraic framework
- Structural analysis: constraint budget analysis, plane matching property, density arguments and their limitations
- OCUS procedure: exact exhaustive certification (not just heuristic MUS) for the integer pool minimum

## Relevance to Our Work

- This is the reference document for the full methodology behind the sub-31 search; [[sub31-letter]] is the concise journal version
- Explicitly identifies itself as a companion to [[algebraic-islands-main]] ("This paper is a companion to Ref. [algebraic], which establishes the algebraic framework... We assume that framework here")
- The structural analysis of proof obstacles connects to the [[kochen-specker-theorem]] lower bound research program
- The plane matching property is a new structural concept introduced here, potentially useful for future proof attempts
- The historical survey of the 24-31 gap provides context for all other papers in the research program
- The realizability barrier concept is the key insight connecting the graph perturbation search to the vertex-merging analysis
- Cross-links to [[csw-inequality]] via discussion of how contextual advantage relates to structural properties
- The Trandafir-Cabello rigidity result discussed here connects to [[universality-letter]]'s uniqueness conjecture

## Open Questions

- What is the plane matching property more precisely, and can it be used to prove that no KS set with fewer than 31 rays exists?
- Can the Li-Bright-Ganesh framework be extended using the finite-pool SAT encoding proposed here?
- Is the realizability barrier provable, or does it require discovering a new geometric invariant that distinguishes realizable from unrealizable KS hypergraphs?
- Can the lower bound be improved from 24 to a higher value (e.g., 28-30) using stronger SAT encodings, potentially meeting the upper bound?
- Does the "gap might also be narrowed from below" approach have any concrete path forward, or is it at a similar impasse as the upper-bound approach?
- Is it possible to prove that no KS set of fewer than 31 rays exists over C^3 (not just R^3)?
- Does the Trandafir-Cabello assumption (minimum set is rigid) have independent evidence, or is it itself a conjecture?
