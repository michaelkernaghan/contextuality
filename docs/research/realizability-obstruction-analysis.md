# Realizability Obstruction Analysis (2026-03-25)

## Motivation
Applied techniques from "Accelerating Scientific Research with Gemini" (arXiv:2602.03837v3):
- Context de-identification: presented n=30 problem as abstract math without KS context
- Cross-pollination: searched oriented matroid theory, rigidity theory, Gram dimension, etc.
- Neuro-symbolic verification: wrote scripts, ran them, fed results back into reasoning
- Negative prompting: "DO NOT use counting arguments, find structural obstruction"

## Cross-Pollination Results (from web search)

### Most Relevant Frameworks
1. **Gram dimension / forbidden minors** (Laurent & Varvitsiotis, 2012): gd(G) <= 3 iff no K4 minor. PSD matrix completion to rank 3 is NP-hard.
2. **Belk-Connelly d-realizability** (2007): 3-realizability forbidden minors are K5 and K_{2,2,2}.
3. **Orthogonality dimension** (Haviv, 2019): Minimum dimension for orthogonal representation. NP-hard to determine.
4. **ETR-completeness**: Matroid realizability over R is complete for existential theory of reals (2023).
5. **Delta Theorem** (Hall, Jan 2026): UPPER bound on faithful orth. rep. dimension (not useful as lower bound).

### Key Insight
The realizability question is ETR-complete. There is unlikely to be a clean combinatorial certificate for non-realizability. The obstruction lives in the real algebraic geometry of the configuration space.

## Computational Results

### CK-31 Calibration
- omega = 3 (max clique = triad, consistent with R^3)
- alpha = 11 (max independent set)
- free_dof = -12 (overconstrained: 71 constraints vs 59 effective DOF)
- treewidth ~ 12
- All 31 vertices in triads, 13 in 2+ triads
- Triad overlap graph: connected, diameter 4, **zero weight-2 edges**

### Abstract Sub-31 Uncolorable Hypergraphs
Generated 8,684 (526 unique) abstract uncolorable hypergraphs with n < 31.

**Three-layer filtering:**

| Filter | Blocks | % |
|--------|--------|---|
| omega > 3 (clique test) | 178/200 | 89% |
| Overconstrained (2n-m-3 < 0) | 196/200 | 98% |
| Passes both tests | 8/200 | 4% |

The 8 hardest cases (omega <= 3 AND underconstrained) have:
- omega = 3, free_dof = 0 to 5
- alpha = 14-16 (larger than CK-31's 11)

### Structural Differences (Triad Topology)

| Property | CK-31 | Hard cases (avg) |
|----------|-------|-----------------|
| Vertices in triads | 31/31 (100%) | 22/29 (76%) |
| Weight-2 triad overlaps | 0 | 2.6 |
| Vertices NOT in triads | 0 | 7 |
| Max triad degree per vertex | 4 | 5-7 |

**Key structural differences:**
1. CK-31 has ALL vertices in triads; hard cases have 5-12 "free" vertices
2. CK-31 has NO triads sharing an edge; hard cases do
3. Hard cases have vertices in up to 7 triads (tight plane constraints in v-perp)

## Emerging Obstruction Hypothesis

The obstruction likely operates at two levels:

**Level 1 (easy, blocks 89%)**: Clique size > 3. R^3 cannot have 4+ mutually orthogonal lines.

**Level 2 (hard, blocks remaining 11%)**: The triad overlap structure creates algebraic dependencies that are inconsistent in rank 3. Specifically:
- Weight-2 triad overlaps force rigid algebraic relationships
- Vertices in many triads create overdetermined systems in their perpendicular planes
- "Free" vertices (not in triads) must still satisfy orthogonality constraints that are inconsistent with the triad-determined vectors

## Next Steps
1. For the hard cases, attempt actual R^3 realization via numerical optimization (SciPy) to measure how close they get
2. Check if the triad overlap cycles create algebraic contradictions (cycle consistency)
3. Look at oriented matroid realizability certificates for specific hard cases
4. Consider whether the obstruction can be stated as a theorem about triad-overlap graphs

## Scripts
- `ks_realizability_obstruction.py` — Main analysis (DOF, clique, forbidden minors)
- `ks_triad_topology.py` — Triad overlap structural analysis
