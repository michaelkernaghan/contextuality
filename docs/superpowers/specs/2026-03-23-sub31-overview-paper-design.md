# Design: The 24-31 Gap — Overview Paper on Sub-31 KS Set Search Methods

**Date**: 2026-03-23
**Author**: Michael Kernaghan, Pacific Quantum Systems
**Status**: Draft spec
**Companion paper**: algebraic_islands.tex (arXiv, "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three")

## Purpose

A comprehensive survey and roadmap paper addressing the central open problem in KS theory for dimension 3: is 31 the minimum number of vectors for a Kochen-Specker set? The paper presents all strategies undertaken to either find a sub-31 set or prove one cannot exist, surveys existing literature on this topic, identifies new advances that limit or guide future searches, and taxonomizes the methods of approach available for resolving the question.

## Venue and Format

- arXiv-first (quant-ph), journal-agnostic
- revtex4-2 format, estimated 20-25 pages
- Natural length — not constrained to PRL's 4-page limit
- Self-contained (readable without algebraic_islands) but not redundant with it

## Relationship to Companion Paper

**algebraic_islands.tex** asks: "What algebraic structure controls KS-uncolorability?"
**This paper** asks: "Is 31 optimal, and how would we prove it?"

Boundary rules:
- **Reference, don't re-derive**: Six-island classification, cancellation identities, cross-product completion, BPQS, CSW invariants — cite algebraic_islands
- **Share data, different framing**: OCUS result, MUS landscape, pool sizes appear in both, but algebraic_islands uses them as evidence for the classification thesis; this paper uses them as search results bearing on optimality
- **New material unique to this paper**: Phase 3 perturbation search (500K trials), proof-by-contradiction structural analysis, literature survey focused on minimality, taxonomy of approaches, roadmap for closing the gap, expanded treatment of all 7 strategies

## Working Title

"The 24-31 gap: Computational methods and structural barriers for minimal Kochen-Specker sets in dimension three"

## Structure

### Section 1: Introduction (~2 pages)

The 24-31 gap as the central open problem in KS theory for dimension 3. Brief KS theorem setup (3-4 sentences, not a full re-derivation). History of CK-31: Conway-Kochen 1990, reported by Peres 1991/1993, unchallenged for three decades. Lower bound history: Arends-Ouaknine-Wampler (18), Uijlen-Westerbaan (22), LBG/KPS (24). Trandafir-Cabello rigidity and their optimality conjecture. Cabello's Eisenstein-33 as independent upper bound for complex coordinates.

Frame contribution: "We report a systematic multi-strategy search across algebraic, combinatorial, numerical, and graph-theoretic methods. No sub-31 KS set is found. We identify the realizability barrier as the core obstruction, provide structural constraints for proof attempts, and map the landscape of approaches for resolving this gap."

Cite algebraic_islands as companion paper establishing the algebraic framework.

### Section 2: Prior Work on KS Minimality (~2-3 pages)

Literature survey focused specifically on the minimality question (not KS theory in general):

- **Upper bounds**: Conway-Kochen (31, 1990), Peres (33, 1991), Cabello Eisenstein (33, 2025). Why CK-31 has resisted improvement.
- **Lower bounds**: Arends-Ouaknine-Wampler (18), Uijlen-Westerbaan (22), LBG (24), KPS (24). Methods: SAT + abstract hypergraph enumeration + Z3 realizability. Where pipelines bottleneck (Z3 "unknown" above order ~20).
- **Rigidity**: Trandafir-Cabello proving CK-31 unique up to unitary equivalence. Implication: any sub-31 set must have a different orthogonality graph.
- **Our companion paper**: Established six algebraic islands, modulus-2/phase-cancellation framework, new KS sets at 43 and 52 vectors. Referenced for algebraic framework, not re-derived.

### Section 3: Framework and Methods (~2 pages)

Self-contained but referential — enough to read alone without duplicating algebraic_islands.

- **Algebraic pool construction**: One paragraph on coordinate alphabets, ray canonicalization, orthogonality graphs, triads. Compact reference table of six pools (name, ring, rays, triads). Cite algebraic_islands for full treatment.
- **SAT encoding**: KS-colorability formula — variables, triad constraints, pair exclusion. One paragraph + formula.
- **MUS and OCUS**: Brief definitions since they're central to multiple strategies.
- **Cross-product completion**: One paragraph noting this is needed for the golden-ratio pool (which is invisible to raw alphabet search). Cite algebraic_islands for full treatment; here it is context, not a search strategy.
- **Realizability testing**: Z3/SMT (exact, often intractable) vs numerical optimization (L-BFGS-B with analytical gradients). Where each succeeds and fails.

Principle: if algebraic_islands defines it, cite and use. If this paper needs a tool algebraic_islands doesn't foreground (OCUS, perturbation framework), define here.

### Section 4: Exact Minimization Within Algebraic Pools (~2 pages)

Strategy 1. MUS extraction across all six pools. Results per pool (table). The six distinct minimal 31-sets from the integer pool: norm stratification, 13-ray invariant core, Jaccard ~0.71, no swap connectivity. OCUS exhaustive proof that 31 is optimal in the integer pool.

*Rules out*: Any sub-31 set from known algebraic pools.

### Section 5: Cross-Pool Mixing (~1 page)

Strategy 2. All 15 pairwise combinations + full 477-ray union. Despite significant cross-pool orthogonalities, every minimized set draws from a single pool. Greedy bias caveat.

*Rules out*: Hybrid algebraic constructions from known fields (heuristic).

### Section 6: Expanded Alphabets (~1.5 pages)

Strategy 3. Thirty expanded alphabets including Pisot-number fields. The modulus-2 boundary: every alphabet containing {0,+/-1,+/-2} converges to 31; alphabets lacking +/-2 are not KS-uncolorable. Table of selected results.

*Rules out*: Larger coordinate sets from tested fields.
*New bound*: Alphabets lacking +/-2 are not KS-uncolorable (empirical).

### Section 7: Numerical Optimization (~1 page)

Strategy 4. Four methods: simulated annealing, CK-31 perturbation, orthogonal completion, soft-tolerance annealing. Categorical failure — at most 5-6 orthogonal pairs, zero triads. Soft-tolerance finds 227 near-orthogonal pairs that all evaporate at exact tolerance.

*Rules out*: Nothing new (negative control). Establishes that continuous methods categorically cannot find KS sets — algebraic structure is necessary, not merely convenient.

### Section 8: Criticality and Deletion-Minimality (~1 page)

Strategy 5. Exhaustive k=1-8 (11.5M SAT checks), sampled k=9-12. CK-31 is deletion-minimal. At k=7 (24 rays remaining = LBG lower bound), all 2,629,575 subsets colorable.

*Rules out*: Sub-configurations of CK-31.

### Section 9: Triad Density Analysis (~1 page)

Strategy 6. Threshold rarity within pools: integer pool not KS below n=42/49, Eisenstein n=48/57, Heegner-7 none up to n=75/145. CK-31 has highest pair density (15.3%). Triad count alone doesn't predict uncolorability — topological interlocking matters.

*Rules out*: Density-based proof strategies.

### Section 10: Graph Perturbation Search (~2 pages)

Strategy 7 — **flagship new result**. The first strategy searching outside algebraic pools entirely.

500,000 trials (12.73 hours). Start from CK-31 graph, apply 1-5 random perturbations (remove vertex, swap triad, merge vertices, add/remove pair). Results:
- 79,850 still uncolorable after perturbation
- 61,702 sub-31 uncolorable abstract hypergraphs
- 1,904 near-realizable (residual < 0.1)
- **Zero realizable** in R^3
- Best residual: 0.038 at n=30, t=17, p=69

Best residual 0.038 is far from tolerance (1e-10) — structural impossibility, not a near-miss.

*Rules out*: Nothing definitively (heuristic). Quantifies the realizability barrier: abstract candidates abundant, geometric realization is the bottleneck.

### Section 11: Vertex Merging and the Realizability Barrier (~2 pages)

Central structural insight — gets its own section.

- The 394 merged 30-vertex graphs (monotonicity argument for preservation).
- Z3 vs finite SAT: Z3 returns "unknown" on all 394; finite pool SAT resolves all in <1s. Methodological contribution for LBG pipeline.
- Convergence with Phase 3: two independent methods, same barrier.
- **The realizability gap as the paper's thesis**: The 24-31 gap is not combinatorial (abstract uncolorable hypergraphs exist below 31 in abundance). It's a realizability gap — R^3 geometry refuses to accommodate them. Reframes the open problem.
- Open question: 394 merged graphs untested in Eisenstein, Heegner-7, C^3.

### Section 12: Toward a Proof of Optimality (~2-3 pages)

Partial results and open problems, not a claimed proof. Frame explicitly: "The following structural insights suggest where a proof might begin, identifying candidate constraints and research directions rather than partial proofs."

- **Setup**: Assume minimal 30-vector KS set S exists in R^3.
- **Constraint budget**: C = t + p. CK-31 profile. All 20 extra pairs essential.
- **Why counting arguments fail**: 18/31 CK-31 vectors in only 1 triad. Degree-1 vectors essential via pair constraints. High C/n doesn't imply uncolorability (best 30-subsets reach C/n=5.33, all colorable).
- **Plane matching property**: For each v in R^3, triads through v form a matching on N(v) in v-perp. R^3 geometric fact, not CK-31-specific. Candidate constraint for a proof.
- **What a proof needs**: Connect R^3 geometry (constraining which graphs are realizable) to combinatorial structure required for uncolorability. Not counting arguments.
- **Comparison with LBG**: They enumerate bottom-up, we constrain top-down. Complementary — a proof likely needs both.

### Section 13: Discussion — The Landscape of Approaches (~2 pages)

The roadmap. Taxonomy of all known methods:

1. **Algebraic search** (pool construction, alphabet expansion, cross-pool) — exhaustive within tested fields, can't cover all fields
2. **Combinatorial enumeration** (LBG/KPS abstract hypergraphs + realizability) — complete in principle, bottlenecked by Z3
3. **Numerical/heuristic** (SA, perturbation, graph perturbation) — fast exploration, no guarantees
4. **Structural/proof-theoretic** (constraint budget, plane matching, rigidity) — the path to a definitive answer

What our work contributes to each. Connections to Trandafir-Cabello, Cortez-Morales-Reyes N(S) invariant, SI-C closure convergence.

Assessment: improving the lower bound from 24 (via stronger SAT encodings + our finite pool SAT as accelerator) may be more tractable than proving 31 optimal.

### Section 14: Conclusion and Open Problems (~1 page)

Concrete open questions with difficulty/tractability assessment:

1. Is 31 optimal? (Hard)
2. Can the lower bound improve beyond 24? (Tractable — finite SAT encoding could help)
3. Does the modulus-2 boundary hold for all number fields? (Open)
4. Are the 394 merged graphs realizable in C^3? (Computable — untested)
5. Does the plane matching property constrain n=30 hypergraphs? (Research question)
6. Can merge saturation be proved for all minimal KS sets? (Conjecture)

## Key Scripts (computational reproducibility)

All scripts in the contextuality/ repository with `random.seed(42)`:

| Script | Strategies |
|--------|-----------|
| ks_sat.py | SAT encoding (shared) |
| ks_exact_minimize.py | Strategy 1 (MUS + greedy + swap) |
| ks_maxsat_optimal.py | Strategy 1 (OCUS proof) |
| ks_mus_landscape.py | Strategy 1 (6 distinct 31-sets) |
| ks_cross_pool.py | Strategy 2 |
| ks_larger_alphabets.py | Strategy 3 |
| ks_exotic.py | Strategy 3 (Pisot fields) |
| ks_numerical_search.py | Strategy 4 |
| ks_sub31_search.py | Strategy 5 (criticality) |
| ks_triad_density.py | Strategy 6 |
| ks_irregular_search.py --perturb | Strategy 7 |
| ks_merge_integer_csp.py | Section 11 (vertex merging) |
| ks_30_contradiction.py | Section 12 (constraint budget) |
| ks_30_budget.py | Section 12 (extra pair essentiality) |

## References (expected)

Core: KochenSpecker1967, ConwayKochen (via Peres1993), Peres1991, LiBrightGanesh2024, KirchwegarPeitlSzeider2023, TrandafirCabello2025, Cabello2025simplest, CortezMoralesReyes2022, Pavicic2019, UijlenWesterbaan2016, ArendsOuaknineWampler, AudemardSimon2018 (Glucose), Z3, Budroni2022 (review).

Our companion: Kernaghan2026algebraic (algebraic_islands).

## Estimated Length

~20-25 pages in revtex4-2 two-column format. No appendices anticipated (ray lists are in algebraic_islands).
