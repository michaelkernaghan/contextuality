# Sub-31 Overview Paper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write a 20-25 page arXiv paper surveying all methods for finding or ruling out sub-31 KS sets in dimension 3.

**Architecture:** LaTeX paper in revtex4-2 format. 14 sections written incrementally, each producing a compilable document. Data and results drawn from existing scripts and the companion algebraic_islands.tex paper. No new computational work needed — this is a writing task.

**Tech Stack:** LaTeX (revtex4-2), pdflatex (MiKTeX), BibTeX-style inline bibliography

**Spec:** `docs/superpowers/specs/2026-03-23-sub31-overview-paper-design.md`
**Companion paper:** `paper/algebraic_islands.tex`
**Existing letter (being expanded):** `paper/sub31_letter.tex`
**Output file:** `paper/sub31_overview.tex`

---

### Task 1: Scaffold the document

**Files:**
- Create: `paper/sub31_overview.tex`

- [ ] **Step 1: Create the LaTeX file with preamble, all section headings, and bibliography skeleton**

Create `paper/sub31_overview.tex` with:
- revtex4-2 document class (twocolumn, pra, superscriptaddress, nofootinbib)
- Standard packages (amsmath, amssymb, amsthm, mathtools, booktabs, hyperref, array, enumitem, xcolor)
- Theorem environments (theorem, proposition, lemma, corollary, conjecture, definition, observation, remark)
- Command shortcuts (\R, \C, \Z, \Q, \KS, \CK)
- Title: "The 24--31 gap: Computational methods and structural barriers for minimal Kochen--Specker sets in dimension three"
- Author: Michael Kernaghan, Pacific Quantum Systems, Vancouver, Canada
- Date: March 2026
- Placeholder abstract (one paragraph summary)
- All 14 section headings as empty sections with labels
- Bibliography block with all expected references (copied from algebraic_islands.tex bibliography, plus Arends-Ouaknine-Wampler, plus self-reference to Kernaghan2026algebraic)
- Acknowledgments placeholder

- [ ] **Step 2: Compile to verify no errors**

Run: `cd "C:/Users/Michael Kernaghan/contextuality/paper" && pdflatex sub31_overview.tex`
Expected: Compiles with warnings about empty references but no errors.

- [ ] **Step 3: Commit**

```
git add paper/sub31_overview.tex
git commit -m "Scaffold sub31 overview paper with section structure and bibliography"
```

---

### Task 2: Write Section 1 — Introduction

**Files:**
- Modify: `paper/sub31_overview.tex` — Section 1

- [ ] **Step 1: Write the Introduction (~2 pages)**

Content per spec:
- Opening: The minimum KS set size in dimension 3 is the central open problem. CK-31 has stood for three decades. The gap between the lower bound (24) and upper bound (31) remains open.
- Brief KS setup (3-4 sentences — definition of KS-uncolorability, dimension 3, rays and triads). Do NOT re-derive from scratch; cite Budroni2022 for comprehensive review.
- History: Conway-Kochen 1990 (reported by Peres 1993), Peres 33-vector set 1991. The alphabet {0,±1,±2} and the cancellation identity 1+1=2.
- Lower bound history: Arends-Ouaknine-Wampler (18, 2011), Uijlen-Westerbaan (22, 2016), Li-Bright-Ganesh (24, 2024), Kirchweger-Peitl-Szeider (24, 2023). Note their methods: SAT + abstract hypergraph enumeration + Z3 realizability checking.
- Trandafir-Cabello rigidity: CK-31 unique up to unitary equivalence. Their conjecture that 31 is optimal.
- Cabello's Eisenstein 33-vector construction (2025) — independent upper bound at 33 for complex coordinates.
- Our contribution paragraph: "We report a systematic multi-strategy search... seven complementary strategies... no sub-31 KS set found... identify the realizability barrier as the core obstruction... provide structural constraints for proof attempts... map the landscape of approaches."
- Cite algebraic_islands (Kernaghan2026algebraic) as companion paper establishing the algebraic framework.
- Brief section outline (one sentence per major section group).

- [ ] **Step 2: Compile**

Run: `cd "C:/Users/Michael Kernaghan/contextuality/paper" && pdflatex sub31_overview.tex`
Expected: Clean compile.

- [ ] **Step 3: Commit**

```
git add paper/sub31_overview.tex
git commit -m "Write Introduction section for sub31 overview paper"
```

---

### Task 3: Write Section 2 — Prior Work on KS Minimality

**Files:**
- Modify: `paper/sub31_overview.tex` — Section 2

- [ ] **Step 1: Write the literature survey (~2-3 pages)**

Organize into four subsections:

**Upper bounds.** Conway-Kochen (31, reported by Peres ~1990/1993). The integer alphabet {0,±1,±2}. Peres 33-vector set (1991) using {0,±1,±√2}. CK-33 (different from CK-31 — also 33 vectors but integer alphabet, communicated to Peres ~1990). Cabello's Eisenstein 33 (2025) — Weyl-Heisenberg construction, fewest bases (14), simplest by that criterion. Note: all upper bounds ≥31 use algebraic coordinate structure.

**Lower bounds.** Chronological treatment:
- Arends-Ouaknine-Wampler (2011): 18 vectors. Method: enumeration + graph coloring.
- Uijlen-Westerbaan (2016): 22 vectors. Method: improved combinatorial constraints.
- Li-Bright-Ganesh (2024, IJCAI): 24 vectors. Method: SAT-based enumeration of abstract 3-uniform hypergraphs + Z3 realizability checking. Key bottleneck: Z3 returns "unknown" on realizability queries above order ~20. The pipeline works: enumerate candidate graphs → filter by SAT-verified uncolorability → test geometric embeddability. The embeddability step is the bottleneck.
- Kirchweger-Peitl-Szeider (2023, AAAI): Independent 24-vector lower bound via SAT modulo symmetries.
- Note: both groups use fundamentally the same approach (enumerate + realize). Neither claims 24 is tight.

**Rigidity and uniqueness.** Trandafir-Cabello (2025): CK-31 is rigid in C^3 — any set of rank-1 projectors satisfying the same orthogonality graph must be unitarily equivalent. Implication for the search: any sub-31 KS set must have a *different* orthogonality graph than CK-31. Combined with graph universality (all tested constructions achieving 31 produce the same graph), this means a sub-31 set cannot be a variant of CK-31 — it must be fundamentally different.

**Algebraic framework.** Brief summary of our companion paper (Kernaghan2026algebraic): systematic survey of coordinate alphabets from quadratic, cyclotomic, and golden-ratio number fields. Six discrete algebraic islands. Two cancellation mechanisms (modulus-2, phase). New KS sets at 43 (Heegner-7) and 52 (golden ratio) vectors. Reference for the pool framework used throughout this paper.

- [ ] **Step 2: Compile**

Run: `cd "C:/Users/Michael Kernaghan/contextuality/paper" && pdflatex sub31_overview.tex`
Expected: Clean compile.

- [ ] **Step 3: Commit**

```
git add paper/sub31_overview.tex
git commit -m "Write prior work section for sub31 overview paper"
```

---

### Task 4: Write Section 3 — Framework and Methods

**Files:**
- Modify: `paper/sub31_overview.tex` — Section 3

- [ ] **Step 1: Write the methods section (~2 pages)**

**Algebraic pool construction.** One paragraph: A coordinate alphabet A is a finite set of values from which ray coordinates are drawn. The induced ray pool S(A) consists of all projectively distinct nonzero vectors in A^3. Rays are canonicalized (first nonzero coordinate positive, gcd-reduced for integers, standard form for complex). The orthogonality graph has rays as vertices, edges between orthogonal pairs; triads are 3-cliques (mutually orthogonal triples forming a basis). See Kernaghan2026algebraic for full treatment.

Compact reference table (copy from sub31_letter Table I format):

| Pool | Ring | Rays | Triads |
|------|------|------|--------|
| Integer | Z | 49 | 26 |
| Eisenstein | Z[ω] | 57 | 22 |
| Peres | Z[√2] | 49 | 16 |
| Z[√-2] | Z[√-2] | 49 | 16 |
| Heegner-7 | Z[α] | 145 | 42 |
| Golden | Z[φ] | 205 | 166 |

**SAT encoding.** One paragraph + formula. Boolean variable b_v per ray (colored 1 = "green"). For each triad {a,b,c}: exactly-one clause (b_a ∨ b_b ∨ b_c) plus three pairwise exclusion clauses. For each orthogonal pair (u,v) not in any triad: exclusion clause (¬b_u ∨ ¬b_v). UNSAT = KS-uncolorable. Solver: Glucose4 via PySAT.

**MUS and OCUS.** MUS (Minimal Unsatisfiable Subset): a subset of clauses that is unsatisfiable but becomes satisfiable upon removal of any single clause. Ray-level MUS extraction: introduce selector literals, extract unsatisfiable core, minimize by iterative deletion. Each ray-level MUS identifies a minimal KS-uncolorable subset. OCUS (Optimal Constrained Unsatisfiable Subset): iteratively proves no unsatisfiable subset of size ≤k exists, for increasing k, until the minimum is certified.

**Cross-product completion.** One paragraph: For some algebraic fields (notably the golden ratio), the raw alphabet produces too few triads. Cross-product completion adds rays computed as v_i × v_j for orthogonal pairs, expanding the pool. The golden-ratio island is invisible without this step. See Kernaghan2026algebraic for details.

**Realizability testing.** Two approaches:
1. Z3/SMT: Encode orthogonality constraints as polynomial equations over reals. Exact but often returns "unknown" for n > 20 due to nonlinear real arithmetic.
2. Numerical optimization: L-BFGS-B minimizing sum of squared dot products for all required-orthogonal pairs, with unit-norm penalty. Analytical gradients. Multiple random starts (10-20). Residual < 10^{-10} = realizable.
3. Finite pool SAT: For realizability within a specific pool, encode as Boolean: each vertex assigned to one of the pool rays, with orthogonality and injectivity constraints. Resolves instances in <1s that defeat Z3.

- [ ] **Step 2: Compile**

Run: `cd "C:/Users/Michael Kernaghan/contextuality/paper" && pdflatex sub31_overview.tex`
Expected: Clean compile.

- [ ] **Step 3: Commit**

```
git add paper/sub31_overview.tex
git commit -m "Write framework and methods section for sub31 overview paper"
```

---

### Task 5: Write Sections 4-6 — Algebraic Strategies

**Files:**
- Modify: `paper/sub31_overview.tex` — Sections 4, 5, 6

- [ ] **Step 1: Write Section 4 — Exact Minimization (~2 pages)**

Expand from sub31_letter Strategy 1. Include:
- MUS extraction across all six pools: 1000-5000 independent extractions per pool. All return the reported minimum (31 for integer, 33 for Peres/Eisenstein/Z[√-2], 43 for Heegner-7, 52 for golden). Results table (expand sub31_letter Table I with MUS trial counts).
- The six distinct minimal 31-sets from the integer pool: found across 5000 MUS extractions. Norm stratification table:
  - 13 rays with ||v||² ≤ 3 → in all 6 sets (invariant core = {0,±1} sub-alphabet)
  - 12 rays with ||v||² = 5 → in 5/6
  - 12 rays with ||v||² = 6 → in 4/6
  - 12 rays with ||v||² = 9 → in 0/6
- No swap connectivity: minimum Hamming distance 5 between any pair. Jaccard ~0.71 (25-26 shared rays).
- OCUS proof: exhaustively certified no ≤30-ray KS subset in the full 49-ray pool. 272 iterations, <0.2s. Also proved for n=21-30 in total 0.5s.
- "Rules out" summary: any sub-31 set from known algebraic pools.

- [ ] **Step 2: Write Section 5 — Cross-Pool Mixing (~1 page)**

Expand from sub31_letter Strategy 2. Include:
- All 15 pairwise pool combinations tested with 500 greedy trials each.
- Full 477-ray union of all six pools tested.
- Despite significant cross-pool orthogonalities (e.g., Integer+Golden shares 78 cross-triads), every minimized set draws rays from a single pool only.
- Any combination including Integer → 31 (all integer rays). Without Integer → 33.
- Greedy bias caveat: deletion is biased toward large basins of attraction. Mixed-pool solutions with small basins cannot be ruled out.
- "Rules out": hybrid algebraic constructions from known fields (heuristic).

- [ ] **Step 3: Write Section 6 — Expanded Alphabets (~1.5 pages)**

Expand from sub31_letter Strategy 3. Include:
- 30 expanded alphabets tested (reproduce sub31_letter Table II, expanded with more entries).
- Key result: every alphabet containing {0,±1,±2} converges to 31 using integer rays. {0,±1,±2,±3} (145 rays) → 31. {0,±1,±2,±i} (127 rays, mixed field) → 31. Eisenstein c=3 (345 rays) → 31.
- The modulus-2 boundary: {0,±1,±3} and {0,±1,±4} are NOT KS-uncolorable despite generating 49 rays with 10 triads each. Lacking ±2 means lacking the 1+1=2 cancellation identity.
- Pisot-number fields: plastic ratio, tribonacci, silver ratio — all produce colorable pools. Extends the observation beyond quadratic fields.
- Golden+±2 (637 rays) → 33, not 31. No integer absorption (golden-ratio rays don't reduce to integers).
- "Rules out": larger coordinate sets from tested fields. "New bound": alphabets lacking ±2 empirically cannot produce KS sets.

- [ ] **Step 4: Compile**

Run: `cd "C:/Users/Michael Kernaghan/contextuality/paper" && pdflatex sub31_overview.tex`
Expected: Clean compile.

- [ ] **Step 5: Commit**

```
git add paper/sub31_overview.tex
git commit -m "Write algebraic strategy sections (4-6) for sub31 overview paper"
```

---

### Task 6: Write Sections 7-9 — Non-Algebraic Strategies

**Files:**
- Modify: `paper/sub31_overview.tex` — Sections 7, 8, 9

- [ ] **Step 1: Write Section 7 — Numerical Optimization (~1 page)**

Expand from sub31_letter Strategy 4. Include:
- Four methods tested:
  1. Simulated annealing from scratch (n=28,29,30 in R^3 and C^3, 2×10^5 steps): at most 5-6 exact orthogonal pairs, zero triads.
  2. CK-31 perturbation (remove 1-3 rays, replace with random): best = 16/17 triads preserved, never restores uncolorability.
  3. Random orthogonal completion from seeds: 60-ray sets achieve at most 1 triad.
  4. Soft-tolerance SA: finds 227 near-orthogonal pairs at tol=0.1, but ALL evaporate as tolerance tightens. Zero exact pairs survive.
- Key insight: exact orthogonality is measure-zero in continuous space. No gradient signal connects near-orthogonal to exact-orthogonal configurations. Continuous optimization categorically cannot find KS sets.
- Framing: negative control. Confirms algebraic structure is necessary, not merely convenient. Not independent evidence against sub-31.
- Total runtime: ~12 minutes for all four methods.

- [ ] **Step 2: Write Section 8 — Criticality and Deletion-Minimality (~1 page)**

Expand from sub31_letter Strategy 5. Include:
- CK-31 deletion-minimality: all 31 single-ray removals tested exhaustively, all produce colorable 30-ray sets. By hereditary property, every proper subset is colorable.
- Extended criticality table (reproduce sub31_letter Table III):
  - k=1-4: 36,456 subsets, exhaustive, all colorable
  - k=5: 169,911, exhaustive
  - k=6: 736,281, exhaustive
  - k=7: 2,629,575, exhaustive (24 rays = LBG lower bound)
  - k=8: 7,888,725, exhaustive
  - k=9-12: 4×10^6 sampled (10^6 per k)
- Total: 11,460,647 exhaustive + 4×10^6 sampled, all colorable.
- Connection to LBG: at k=7, the 24-ray subsets are exactly the configurations LBG's lower bound says are the minimum. None of CK-31's 24-ray subsets are KS. This is already implied by deletion-minimality but provides concrete confirmation.
- "Rules out": sub-configurations of CK-31.

- [ ] **Step 3: Write Section 9 — Triad Density Analysis (~1 page)**

Expand from sub31_letter Strategy 6. Include:
- Method: for each pool, sample 500 uniform random subsets at each size n, test KS-uncolorability via SAT.
- Results:
  - Integer pool: no KS below n=42 of 49 (upper bound p ≤ 0.006 at 95%)
  - Eisenstein: n=48 of 57
  - Heegner-7: none at any sampled size up to n=75 of 145
- CK-31 pair density: 15.3% of C(31,2) pairs are orthogonal — highest of any tested construction.
- Key insight: triad count alone doesn't determine uncolorability. KS sets are extraordinarily rare within pools — topological interlocking of constraints matters, not raw density.
- C^3 doesn't help: Eisenstein threshold (48) higher than integer (42) despite complex coordinates providing more orthogonality freedom.
- "Rules out": density-based proof strategies. A proof of optimality cannot rely on counting triads or pairs alone.

- [ ] **Step 4: Compile**

Run: `cd "C:/Users/Michael Kernaghan/contextuality/paper" && pdflatex sub31_overview.tex`
Expected: Clean compile.

- [ ] **Step 5: Commit**

```
git add paper/sub31_overview.tex
git commit -m "Write non-algebraic strategy sections (7-9) for sub31 overview paper"
```

---

### Task 7: Write Section 10 — Graph Perturbation Search

**Files:**
- Modify: `paper/sub31_overview.tex` — Section 10

- [ ] **Step 1: Write Section 10 (~2 pages)**

This is the paper's flagship new result. Include:

**Motivation.** Strategies 1-6 all search within or near algebraic pools. If a sub-31 KS set exists with an "irregular" orthogonality graph — one not arising from any known algebraic construction — those strategies would miss it. Strategy 7 searches the space of abstract hypergraphs directly.

**Method.** Start from CK-31's orthogonality graph (31 vertices, 71 edges, 17 triads). Apply 1-5 random perturbations per trial, drawn from five operations:
1. Remove vertex (reduce n by 1, remap remaining vertices)
2. Swap triad (remove one triad, add a random one)
3. Merge vertices (identify two non-adjacent vertices)
4. Add pair (add an orthogonality edge between non-adjacent vertices)
5. Remove pair (remove an extra pair not in any triad)

Operations weighted: vertex removal and triad swaps favored (weight 3 each), merges weight 2, pair operations weight 1.

After perturbation: test KS-uncolorability via SAT. If uncolorable and n < 31: test R^3 realizability via L-BFGS-B (10-15 random starts, analytical gradients, tolerance 10^{-10}).

**Results.** 500,000 trials, 12.73 hours. Summary table:

| Metric | Count |
|--------|-------|
| Valid perturbations | 500,000 |
| Still uncolorable | 79,850 (16.0%) |
| Sub-31 uncolorable | 61,702 (12.3%) |
| Near-realizable (residual < 0.1) | 1,904 |
| Realizable | 0 |
| Best residual | 3.8 × 10^{-2} |
| Best config | n=30, t=17, p=69 |

**Interpretation.**
- Abstract sub-31 KS-uncolorable hypergraphs are *abundant* — about 12% of valid perturbations produce one. The combinatorial requirement (uncolorability) is not the bottleneck.
- The geometric requirement (R^3 realizability) is the bottleneck. Of 61,702 abstract candidates, zero are realizable.
- The best residual (0.038) is far from the tolerance (10^{-10}). This is not a near-miss that more optimization restarts would fix — it's a structural gap.
- Best configuration (n=30, t=17, p=69) is tantalizingly close to CK-31's profile (n=31, t=17, p=71) — same number of triads, two fewer pairs, one fewer vertex — but the geometry refuses.

**Script reference.** `ks_irregular_search.py --perturb`, random seed 42.

- [ ] **Step 2: Compile**

Run: `cd "C:/Users/Michael Kernaghan/contextuality/paper" && pdflatex sub31_overview.tex`
Expected: Clean compile.

- [ ] **Step 3: Commit**

```
git add paper/sub31_overview.tex
git commit -m "Write graph perturbation search section (flagship result) for sub31 overview"
```

---

### Task 8: Write Section 11 — Vertex Merging and the Realizability Barrier

**Files:**
- Modify: `paper/sub31_overview.tex` — Section 11

- [ ] **Step 1: Write Section 11 (~2 pages)**

**Vertex merging construction.** Generate 30-vertex candidate KS graphs by merging non-orthogonal ray pairs in CK-31. Merge = identify two vertices into one that inherits both neighborhoods. Monotonicity argument: if the merged graph were colorable, assigning the merged vertex's color back to both originals yields a valid coloring of the original, contradicting uncolorability. Therefore all merges of CK-31 with non-orthogonal pairs preserve KS-uncolorability.

CK-31 has C(31,2) - 71 = 394 non-orthogonal pairs. All 394 merges produce abstract 30-vertex KS graphs with 17-21 triads, 70-71 pairs.

**Realizability testing.** Three approaches tried:
1. Z3/SMT (R^3 polynomial encoding): returns "unknown" on all 394. Intractable.
2. Finite pool SAT: Boolean assignment of 30 vertices to 49 pool rays, with orthogonality + injectivity constraints. All 394 UNSAT in <1s each. Definitive within the integer pool.
3. Numerical optimization (same L-BFGS-B as Strategy 7): provides residuals but cannot prove unrealizability.

**The realizability barrier — thesis statement.** Two independent lines of evidence converge:
- Vertex merging: 394 combinatorially valid 30-vertex KS graphs, all unrealizable in the integer pool.
- Graph perturbation (Section 10): 61,702 abstract sub-31 KS hypergraphs from a completely different construction method, all unrealizable in R^3.

The 24-31 gap is NOT a combinatorial gap. Abstract uncolorable hypergraphs with n < 31 exist in abundance (at least 62,096 found by our two methods). The gap is a *realizability* gap: R^3 geometry refuses to accommodate them. Closing the gap requires either:
- A realizability proof (showing no embedding exists for any sub-31 abstract KS hypergraph), or
- A surprise construction that evades all tested approaches.

**Methodological contribution.** The finite pool SAT encoding resolves realizability instances in <1s that defeat Z3. Directly applicable to the LBG pipeline as a "quick accept" screen: test candidate hypergraphs against finite algebraic pools before invoking expensive Z3 queries. Would not replace Z3 (it tests pool membership, not general R^3 realizability) but could accelerate the pipeline significantly.

**Open questions.** The 394 merged graphs have not been tested for realizability in:
- Other algebraic pools (Eisenstein, Heegner-7, etc.)
- C^3 (complex coordinates)
These remain computable but untested.

- [ ] **Step 2: Compile**

Run: `cd "C:/Users/Michael Kernaghan/contextuality/paper" && pdflatex sub31_overview.tex`
Expected: Clean compile.

- [ ] **Step 3: Commit**

```
git add paper/sub31_overview.tex
git commit -m "Write vertex merging and realizability barrier section for sub31 overview"
```

---

### Task 9: Write Section 12 — Toward a Proof of Optimality

**Files:**
- Modify: `paper/sub31_overview.tex` — Section 12

- [ ] **Step 1: Write Section 12 (~2-3 pages)**

Frame explicitly: "The following structural insights suggest where a proof might begin, identifying candidate constraints and research directions rather than partial proofs."

**Setup.** Suppose a minimal KS set S with |S| = 30 exists in R^3. What properties must it have? We derive necessary conditions by analyzing the structure of CK-31 (the closest known KS set) and identifying R^3 geometric constraints.

**Constraint budget.** Define C = t + p: total constraint count = number of triads + number of orthogonal pairs. For CK-31: n=31, t=17, p=71, C=88, C/n=2.839. The 71 pairs decompose into 51 triad-implied pairs (from 17 triads × 3 pairs each) and 20 "extra" pairs (orthogonal pairs not contained in any triad).

All 20 extra pairs are essential: removing any single extra pair makes the SAT formula satisfiable (colorable). Triads alone (51 pairs from 17 triads) are satisfiable. 19 of 20 extra pairs: satisfiable. Need all 20 for unsatisfiability. CK-31 is *maximally tight*.

**Why counting arguments fail.**
- Naive approach: "every vector must be in ≥2 triads for constraint propagation." FALSE for CK-31: 18 of 31 vectors are in only 1 triad. These degree-1 vectors are essential not because of triads but because of extra pair constraints.
- Degree distribution of CK-31: 18 at triad-degree 1, 8 at degree 2, 3 at degree 3, 2 at degree 4.
- High constraint density doesn't imply uncolorability: the densest 30-vector subsets of the integer pool achieve C/n = 5.33, far exceeding CK-31's 2.84, yet all are colorable. Structure matters, not raw count.
- This kills the most natural proof strategy (derive a minimum constraint density, show 30 vectors can't achieve it).

**The plane matching property.** For each vector v in R^3, the perpendicular plane v⊥ is 2-dimensional. Any triad containing v consists of v plus two vectors in v⊥ that are orthogonal to each other. If v is in k triads, those k pairs of vectors in v⊥ must be mutually compatible: they form a matching on the neighbors of v in v⊥. This is an R^3 geometric constraint (in higher dimensions, orthogonal pairs in v⊥ need not form a matching). Verified on all 31 CK-31 vectors.

**What a proof would need.** Not counting arguments. Something that connects:
- R^3 geometry (which constrains which orthogonality graphs are realizable — the plane matching property, dimensional constraints on the number of orthogonal pairs per vertex), with
- The combinatorial structure required for uncolorability (enough interlocking triads and pairs to make SAT unsatisfiable).

**Comparison with LBG.** Their approach: enumerate abstract hypergraphs bottom-up, test realizability. Our approach: identify geometric constraints top-down. The approaches are complementary. A proof likely needs both directions to meet in the middle: LBG-style enumeration (possibly accelerated by our finite SAT encoding) to cover the combinatorial side, plus geometric constraints (plane matching, rigidity) to cover the realizability side.

- [ ] **Step 2: Compile**

Run: `cd "C:/Users/Michael Kernaghan/contextuality/paper" && pdflatex sub31_overview.tex`
Expected: Clean compile.

- [ ] **Step 3: Commit**

```
git add paper/sub31_overview.tex
git commit -m "Write proof-of-optimality section for sub31 overview paper"
```

---

### Task 10: Write Sections 13-14 — Discussion and Conclusion

**Files:**
- Modify: `paper/sub31_overview.tex` — Sections 13, 14

- [ ] **Step 1: Write Section 13 — Discussion (~2 pages)**

**Taxonomy of approaches.** Organize all known methods into four categories:

1. *Algebraic search* — Pool construction, alphabet expansion, cross-pool mixing (our Strategies 1-3, 6). Strengths: exhaustive within tested fields, SAT-certifiable. Limitations: cannot cover all number fields. Our contribution: six pools fully characterized, modulus-2 boundary identified, 30 expanded alphabets tested.

2. *Combinatorial enumeration* — Abstract hypergraph generation + realizability (LBG, KPS). Strengths: complete in principle. Limitations: bottlenecked by Z3 above order ~20. Our contribution: finite pool SAT encoding resolves instances in <1s that defeat Z3; directly applicable as quick-accept screen.

3. *Numerical/heuristic* — SA, perturbation, graph perturbation (our Strategies 4, 7). Strengths: fast exploration of large search spaces, can probe outside algebraic pools. Limitations: no completeness guarantees, can only find (not rule out). Our contribution: 500K-trial perturbation search quantifying the realizability barrier.

4. *Structural/proof-theoretic* — Constraint budget, plane matching, rigidity (our Section 12, Trandafir-Cabello). Strengths: the only path to a definitive answer. Limitations: incomplete — no proof yet. Our contribution: identified why counting arguments fail, plane matching as candidate constraint.

**Connections to published work.**
- Trandafir-Cabello rigidity → any sub-31 set has a different graph. Combined with our graph universality (Kernaghan2026algebraic), no tested construction produces an alternative 31-vertex graph.
- Cortez-Morales-Reyes N(S) invariant: CK-31 has N=30, Eisenstein has N=6 (= minimal ring Z[1/6] of their theorem). Provides independent structural classification.
- SI-C closure (Trandafir-Cabello): their 97-ray closure and our 49-ray integer pool overlap in 37 rays; after second-round closure (1741 rays), our pool is contained. Top-down (closure) and bottom-up (alphabet) approaches converge.

**Assessment.** Improving the lower bound from 24 may be more tractable than proving 31 optimal. Our finite pool SAT encoding could accelerate the LBG pipeline. Even modest improvements (to 28 or 29) would be significant and may be achievable with current SAT technology plus our algebraic constraints.

- [ ] **Step 2: Write Section 14 — Conclusion and Open Problems (~1 page)**

Summary paragraph: seven complementary strategies, no sub-31 KS set found, realizability barrier identified as core obstruction.

Open problems with assessment:

1. *Is 31 optimal?* (Hard — the central open problem. Requires combining geometric realizability constraints with combinatorial uncolorability requirements.)
2. *Can the lower bound be improved beyond 24?* (Tractable — finite pool SAT encoding as LBG accelerator. Geometric constraints may further prune the search space.)
3. *Does the modulus-2 boundary hold for all number fields?* (Open — tested for quadratic, cyclotomic, Pisot. Untested: higher-degree algebraic extensions, transcendental coordinates.)
4. *Are the 394 merged 30-vertex graphs realizable in C^3?* (Computable — straightforward extension of our methods, not yet tested.)
5. *Does the plane matching property yield combinatorial constraints at n=30?* (Research question — would require proving that no uncolorable 3-uniform hypergraph with the matching property exists at that size.)
6. *Can merge saturation be proved for all minimal KS sets?* (Conjecture — verified for all six known islands, 3,756 total merges.)

Final sentence: the 24-31 gap remains one of the central open problems in Kochen-Specker theory, but the landscape of approaches is now well-mapped.

- [ ] **Step 3: Write Acknowledgments**

"The author thanks Adán Cabello for valuable correspondence on KS set rigidity and for offering to sponsor the arXiv submission. The author acknowledges the use of Claude (Anthropic) for computational assistance. SAT solving used PySAT with the Glucose4 solver. Code, ray/triad lists, and SAT instances are available at [GitHub URL]."

- [ ] **Step 4: Compile**

Run: `cd "C:/Users/Michael Kernaghan/contextuality/paper" && pdflatex sub31_overview.tex`
Expected: Clean compile.

- [ ] **Step 5: Commit**

```
git add paper/sub31_overview.tex
git commit -m "Write discussion and conclusion sections for sub31 overview paper"
```

---

### Task 11: Write the Abstract

**Files:**
- Modify: `paper/sub31_overview.tex` — Abstract

- [ ] **Step 1: Write the final abstract (~200 words)**

Write after all sections are complete so it accurately reflects content. Should cover:
- The problem (24-31 gap, minimum KS set in dim 3)
- Our approach (seven complementary strategies across algebraic, combinatorial, numerical, and graph-theoretic methods)
- Key results (no sub-31 found; OCUS proof of 31 optimal within integer pool; 61,702 abstract sub-31 KS hypergraphs none realizable; modulus-2 boundary; 394 merged graphs unrealizable)
- The thesis (realizability barrier, not combinatorial gap)
- Contribution framing (roadmap for closing the gap)

Replace the placeholder abstract.

- [ ] **Step 2: Compile final version**

Run: `cd "C:/Users/Michael Kernaghan/contextuality/paper" && pdflatex sub31_overview.tex && pdflatex sub31_overview.tex`
Expected: Clean compile, all references resolved on second pass.

- [ ] **Step 3: Commit**

```
git add paper/sub31_overview.tex
git commit -m "Write abstract and finalize sub31 overview paper draft"
```

---

### Task 12: Final review pass

**Files:**
- Modify: `paper/sub31_overview.tex` — full document

- [ ] **Step 1: Cross-reference check**

Verify all \ref{} and \cite{} resolve. Check that every reference in the bibliography is cited at least once. Check that no section references content from algebraic_islands without citing it.

- [ ] **Step 2: Redundancy check against algebraic_islands.tex**

Read both papers side by side. Flag any paragraph that appears in both with similar wording. For shared data (OCUS result, MUS landscape, pool table), verify the framing is different: algebraic_islands frames as evidence for algebraic classification; this paper frames as evidence for optimality/realizability barrier.

- [ ] **Step 3: Consistency check**

Verify all numbers match between this paper and sub31_letter.tex / algebraic_islands.tex:
- Pool sizes: 49, 57, 49, 49, 145, 205
- Minimum KS sizes: 31, 33, 33, 33, 43, 52
- CK-31 stats: 31 vectors, 71 pairs, 17 triads, 20 extra pairs
- Phase 3 stats: 500K trials, 79850 uncolorable, 61702 sub-31, 1904 near-realizable, 0 realizable, best residual 0.038
- OCUS: 272 iterations, <0.2s
- Criticality: 11,460,647 exhaustive checks

- [ ] **Step 4: Final compile**

Run: `cd "C:/Users/Michael Kernaghan/contextuality/paper" && pdflatex sub31_overview.tex && pdflatex sub31_overview.tex`
Expected: Clean compile, no unresolved references.

- [ ] **Step 5: Commit**

```
git add paper/sub31_overview.tex
git commit -m "Final review pass: cross-references, redundancy, consistency verified"
```
