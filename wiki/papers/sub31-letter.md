---
source: paper/sub31_letter.tex
date_ingested: 2026-04-03
type: paper
---

# Computational Evidence for the Optimality of Conway-Kochen's 31-Vector Kochen-Specker Set (Kernaghan, 2026)

## Summary

This PRL-format letter reports a systematic computational search for [[ks-set|KS sets]] with fewer than 31 vectors in dimension 3, where the Conway-Kochen construction (CK-31) has stood as the smallest known for over three decades. No sub-31 KS set is found by any of seven complementary strategies. The paper provides the most comprehensive computational evidence to date that 31 is the optimal minimum for KS sets in dimension 3, while stopping short of a proof.

The search deploys seven strategies: (1) MUS-based exact minimization within six algebraic ray pools, (2) cross-pool mixing of rays from different algebraic islands, (3) expanded coordinate alphabets including Pisot-number fields, (4) non-algebraic numerical optimization, (5) exhaustive criticality testing of CK-31, (6) triad density analysis, and (7) graph perturbation search over 500,000 trials. The graph perturbation search is particularly notable: it generates 61,702 abstract sub-31 KS-uncolorable hypergraphs, but numerical realizability testing finds no R^3 embedding for any of them - the best optimization residual is 3.8e-2, far above the acceptance threshold. A vertex-merging analysis derives 394 combinatorially valid 30-vertex KS graphs from CK-31, all proved unrealizable within the integer pool by finite SAT encoding in under 1 second each.

A key empirical finding is the *modulus-2 boundary*: integer-like alphabets {0,+/-1,+/-x} lacking the coordinate +/-2 (such as {0,+/-1,+/-3}) are not KS-uncolorable at all, despite generating 49 rays with 10 triads each. The paper confirms CK-31 is deletion-minimal (removing any single ray yields a colorable 30-ray set) and exhaustively checks all subsets down to 24 rays (the Li-Bright-Ganesh lower bound), finding all colorable.

## Key Claims

- No sub-31 KS set found by any of seven strategies across all tested algebraic pools and numerical methods
- MUS extraction results (Table tab:results): integer pool minimum = 31, Eisenstein/Peres/Z[sqrt(-2)] = 33, Heegner-7 = 43, golden ratio = 52; all consistent across 1,000-5,000 independent MUS extractions per pool
- OCUS-certified: 31 is the exact minimum within the 49-ray integer pool {0,+/-1,+/-2}^3 (no <=30-ray KS subset exists)
- CK-31 deletion-minimality: removing any single ray produces a colorable 30-ray set (all 31 removals tested exhaustively)
- Extended criticality (Table tab:criticality): all C(31,k) subsets for k<=8 are colorable; all 10^6 random k=9..12 subsets are colorable; specifically, all 2,629,575 24-ray subsets of CK-31 are colorable
- The modulus-2 boundary: alphabets {0,+/-1,+/-3} and {0,+/-1,+/-4} are not KS-uncolorable at all; the identity 1+1=2 appears necessary for integer-like alphabets
- Cross-pool mixing: all 15 pairwise pool combinations and the full 477-ray union minimize to 31 (integer rays), or 33 (without integer pool); no cross-pool mixing beats the single-pool minimum
- The 394 vertex-merge 30-vertex KS graphs: all unrealizable within the integer pool by finite SAT encoding; Z3 returns "unknown" on all 394 realizability queries but the finite-pool Boolean encoding resolves all in <1s
- Graph perturbation search (500,000 trials, 12.7 hours): 79,850 perturbed graphs are uncolorable; 61,702 have n<31; none are realizable in R^3 (best residual 3.8e-2 at n=30, t=17, p=69)
- Integer pool has six distinct minimal 31-sets (found across 5,000 MUS extractions), sharing a 13-ray invariant core (rays with ||v||^2 <= 3) and excluding all highest-norm rays; minimum swap distance between any two is 5 ray replacements
- Density trend: simpler cancellation identities produce denser orthogonality structures (integer: 0.53 triads/ray, minimum 31; golden ratio: 0.20 triads/ray, minimum 52)
- The finite-pool SAT encoding resolves realizability queries that defeat Z3, in <1s; proposed as a "quick accept" screen for the Li-Bright-Ganesh lower-bound pipeline

## Methods

- SAT-based KS-uncolorability encoding: exactly-one constraints per triad plus at-most-one constraints per orthogonal pair not in a triad; Glucose4 via PySAT
- MUS (Minimal Unsatisfiable Subset) extraction: 1,000-5,000 independent randomized trials per pool
- OCUS (Optimal Constrained Unsatisfiable Subset) for exhaustive certification of the integer pool minimum
- Greedy deletion minimization: 2,000 trials plus deterministic orderings plus swap-based local search
- Cross-pool mixing: canonical deduplication of rays from different pools, SAT testing of merged pools
- Expanded alphabet testing: 30 alphabets including integer up to {0,+/-1,...,+/-5}, mixed-field alphabets, Pisot-number fields (plastic, tribonacci, silver ratios)
- Non-algebraic numerical optimization: simulated annealing (n=28-30 rays), CK-31 perturbation, random seed completion, soft-tolerance annealing
- Exhaustive criticality testing: all C(31,k) subsets for k<=8; 10^6 random samples for k=9..12
- Triad density threshold sampling: 500 uniform random samples per subset size
- Graph perturbation search: 500,000 trials applying 1-5 perturbations (vertex removal, triad swap, vertex merge, pair addition/removal) to CK-31 graph, SAT-testing uncolorability, numerical realizability testing via L-BFGS-B (10-15 restarts)
- Vertex merging: identify two non-orthogonal vertices, merge neighborhoods, prove KS-uncolorability preserved by monotonicity; finite SAT encoding for realizability
- Z3 SMT solver for R^3 realizability (returned "unknown" on all queries)

## Relevance to Our Work

- This letter is the concise companion to [[sub31-overview]], which presents the same search in extended format with full methodology and structural analysis
- Provides the primary computational evidence supporting the optimality conjecture stated in [[universality-letter]]
- The six algebraic pools are those identified in [[algebraic-islands-main]]
- The OCUS certification of the integer pool minimum directly extends the main paper's results
- The modulus-2 boundary finding aligns with the two-mechanism theory of [[algebraic-islands-main]]
- The realizability barrier concept connects to the key structural insight in [[sub31-overview]]
- The finite-pool SAT encoding proposed as a tool for the [[kochen-specker-theorem]] lower bound program of Li-Bright-Ganesh
- Cross-links to [[csw-inequality]] via the Cortez-Morales-Reyes invariant N(S) = lcm{||v||^2} discussion (CK-31 has N=30, Eisenstein has N=6)

## Open Questions

- Can the realizability barrier be converted into a proof? Abstract sub-31 KS-uncolorable hypergraphs are abundant (~12% of valid perturbations) but none embed in R^3 - what geometric property prevents embedding?
- Can the OCUS certification be extended from the integer pool to other algebraic pools (currently only best-known values, not exhaustively certified)?
- Do any of the 394 vertex-merge 30-vertex graphs embed in other pools (Eisenstein, Heegner-7, etc.) or in C^3 (not yet tested)?
- Is the 13-ray invariant core (rays with ||v||^2 <= 3, norm-stratified, present in all six minimal 31-sets) structurally necessary for any KS-31 set, or specific to this pool?
- Can the proposed finite-pool SAT encoding actually advance the Li-Bright-Ganesh lower bound pipeline past 24?
- Are there KS sets with exactly 25, 26, 27, 28, 29, or 30 rays from any currently untested number field?
