---
source: ks_sat.py
date_ingested: 2026-04-03
type: computation
---

# KS SAT — SAT-Based KS Coloring Solver

## Purpose

Provides the primary computational engine for KS-uncolorability checking, using a SAT solver (Glucose4 via `python-sat`) rather than backtracking. Also implements realizability checking (can an abstract orthogonality graph be embedded in R^3?) and searches for novel KS configurations via random hypergraph generation and graph perturbation.

The script separates the combinatorial problem (is this graph KS-uncolorable?) from the geometric problem (can this graph be realized as actual R^3 vectors?). The key insight documented in the summary: most abstract KS-uncolorable graphs CANNOT be realized in R^3 — the geometric constraints are the bottleneck, not the combinatorial ones.

## Inputs

- Coordinate vectors (list of 3-tuples) via `build_graph()`, which constructs the orthogonality graph
- For realizability: abstract orthogonality graph (n_rays, pairs) — coordinates not required
- CK-31 vectors are hardcoded as `CK31_VECTORS` for the main demonstration

## Outputs

- Console output from the three-phase main demonstration
- Phase 1: essential ray/triad analysis of CK-31 (which rays/triads can be removed while preserving uncolorability)
- Phase 2: realizability check — recovers R^3 coordinates from CK-31's abstract graph via numerical optimization
- Phase 3: random search results — counts of uncolorable and realizable graphs found

## Key Results

**Phase 1 — CK-31 Analysis:**
- `is_uncolorable()` confirms CK-31 is uncolorable
- `find_essential_rays()` identifies which of the 31 rays are essential (removal makes set colorable)
- `get_essential_triads()` uses assumption-based SAT to find the UNSAT core (minimal set of triads generating the contradiction)
- Expected result: CK-31 is MINIMAL — every ray is essential

**Phase 2 — Realizability:**
- `check_realizability()` recovers R^3 coordinates from the abstract CK-31 graph using L-BFGS-B optimization over spherical coordinates
- `verify_realization()` checks for constraint violations and detects "extra" orthogonalities introduced by the embedding
- A clean realization (no extra orthogonalities) confirms the abstract and realized graphs match

**Phase 3 — Novel KS Search:**
- Strategy A: 200 random interlocked hypergraphs per (n_rays, n_triads) combination for n_rays in {26, 28, 30}. Uncolorable ones are checked for R^3 realizability.
- Strategy B: 200 perturbations of CK-31's graph (swap one ray in one triad). Counts how many perturbations preserve uncolorability.
- Expected finding: realizability is the hard constraint; random uncolorable hypergraphs are rarely realizable

## SAT Encoding

KS coloring is encoded as SAT: variable i = ray i is GREEN. For each triad (a,b,c): at-least-one-green clause + three pairwise-exclusion clauses. For non-triad orthogonal pairs: at-most-one-green clause. UNSAT = no valid coloring = KS set. Falls back to a propagation+backtracking solver if `python-sat` is unavailable.

## Key Functions (importable)

- `is_uncolorable(n, pairs, triads)` — primary coloring check, used by ks_islands.py and ks_geometry.py
- `build_graph(vectors)` — builds orthogonality graph from integer coordinate vectors
- `check_realizability(n_rays, pairs, n_restarts)` — numerical realizability check
- `find_essential_rays(n, pairs, triads)` — essential ray identification
- `get_essential_triads(n, pairs, triads)` — SAT-core triad identification

## Dependencies

- `python-sat` (Glucose4) — required for full SAT performance; backtracking fallback available
- `scipy` — L-BFGS-B optimization for realizability
- [[ks-complex]] — imported for fallback colorability when pysat unavailable
- [[kochen-specker-theorem]] — the combinatorial problem being solved
- [[algebraic-islands-main]] — CK-31 is the primary test case
