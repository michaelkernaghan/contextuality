# Cross-Reference Analysis: Papers vs References
## 2026-02-18

---

## CRITICAL: Missing Citations

These must be added across the papers:

| Reference | Missing From | Why Critical |
|-----------|-------------|--------------|
| **Gould & Aravind 2010** | universality_letter | Direct precursor to universality claim. Their |c|^2=2 constraint IS the norm-2 boundary analytically. Shows Peres/Penrose 33v sets are graph-isomorphic via continuous 3-parameter family |
| **Li, Bright, Ganesh 2024** | universality_letter, sub31_letter | Established the proven 24 lower bound. Our conjecture of 31 must reference this |
| **Kirchweger, Peitl, Szeider 2023** | universality_letter, sub31_letter | Independently proved same 24 lower bound. SMS+CCL methodology is complementary |
| **Cabello 2025 (simplest)** | sub31_letter | The 33v Eisenstein set our pool converges to. Validates computational minimum |
| **Budroni et al. 2022** | heegner7_letter | Standard modern KS review. Should be cited for general context |

---

## HIGH-VALUE Findings to Incorporate

### 1. Gould-Aravind's |c|^2=2 explains norm-2 boundary analytically
**Affects**: universality_letter, algebraic_islands (main paper)

Their 2010 paper shows the Peres/Penrose family forms a continuous 3-parameter family with constraint |c|^2=2. This IS the theoretical underpinning for our empirical norm-2 boundary. The orthogonality relations depend only on the *norms* of the parameters, not the specific algebraic values. This explains:
- Why different algebras produce the same graph (universality)
- Why norm-2 is the threshold (the constraint is |c|^2=2 exactly)
- Why the islands are discrete yet connected through a continuum of realizations

### 2. KCBS numerical coincidence
**Affects**: heegner7_letter

The Heegner-7 pool's theta/alpha = 1.118 numerically matches sqrt(5)/2 ~ 1.118 for the KCBS pentagon (the fundamental contextuality scenario). Need to check if this is exact or approximate. If exact, it's a striking observation worth mentioning.

### 3. Universality fails at 33 but holds at 31 -- why?
**Affects**: universality_letter

Both Gould-Aravind and Cabello note that the Schutte-33 set has a *different* graph from Peres-33/Penrose-33. So universality does NOT hold at 33 vectors (multiple non-isomorphic KS graphs exist at that size). The universality letter must explain why it holds at 31 -- possibly because CK-31 is the unique subgraph obtainable by deleting 2 vectors from any member of the continuous family.

### 4. Pavicic's 4D golden ratio coordinates
**Affects**: heegner7_letter

Pavicic (2019) uses phi-coordinates {0, +/-(sqrt(5)-1)/2, +/-1, +/-(sqrt(5)+1)/2, 2} in 4D KS constructions. The heegner7 letter should note golden ratio coordinates have appeared before (in 4D) but not in dim-3 via cross-product completion. Strengthens novelty claim while being honest about prior art.

### 5. Finite pool SAT encoding is undersold in sub31
**Affects**: sub31_letter

The finite pool SAT encoding (C4a-C4c) that bypasses Z3's limitations is the strongest methodological contribution. Both LBG and KPS are bottlenecked by Z3 embeddability checking. Our encoding reformulates realizability within a finite pool as pure SAT (much faster). LBG and KPS spend pages discussing Z3 difficulties -- our encoding directly addresses this. Deserves more emphasis.

### 6. BPQS |X|x|Y| values should be computed
**Affects**: heegner7_letter

Cabello's Table I has |X|x|Y| values for known KS sets. Computing these for Heegner-7 (23 bases) and Golden (25 bases) would strengthen the BPQS claim. Currently the letter just says "each new KS set defines new bipartite Bell scenarios" without the specific numbers.

### 7. "Simplest" vs "smallest" distinction
**Affects**: sub31_letter, algebraic_islands

Cabello argues his 33v Eisenstein set is "simpler" than CK-31 by bases (14 vs 17) and symmetry (order 144 vs 4). We focus on vector count. These are complementary criteria -- should be acknowledged explicitly.

---

## TENSIONS TO ADDRESS

### Heuristic evidence vs formal proof
**Papers affected**: sub31_letter
**Issue**: LBG provide DRAT proof certificates (40.3 TiB) for the 24 lower bound. Our "strong evidence" for 31 rests on greedy deletion (2000 trials). These are fundamentally different epistemic statuses.
**Resolution**: Soften language. Clearly state: "We do not claim a proof; we provide computational evidence from six complementary strategies that all converge to 31."

### KS definition (original vs extended)
**Papers affected**: sub31_letter, universality_letter
**Issue**: LBG use both "original" and "extended" KS definitions. CK-31 = 31 vectors (original) but 51 vectors (extended). Our papers use original definition implicitly.
**Resolution**: Add a sentence explicitly stating which definition we use.

### Continuous family vs discrete islands
**Papers affected**: universality_letter, algebraic_islands
**Issue**: Gould-Aravind show a continuous family connecting Peres and Penrose. We frame islands as discrete.
**Resolution**: The islands ARE discrete at the level of number fields, but within each island there can be continuous families of realizations sharing the same graph. The discreteness is in the graph/hypergraph structure, not in the coordinatization.

### Complex coordinates dismissed too quickly
**Papers affected**: sub31_letter
**Issue**: We say "Working in C^3 does not help: all complex pools minimize to >=33." But Cabello values his 33v complex set for symmetry and physical properties.
**Resolution**: Acknowledge the complementary criterion. Complex coordinates don't help for vertex-count minimality but may be superior by other metrics.

---

## UNCITED CONNECTIONS (lower priority)

### For heegner7_letter
- Budroni et al.'s resource theory of contextuality -- auxiliary rays as a resource for contextual strength
- CSW's fractional packing number alpha*(G) -- report for Heegner-7 pool to complete the triple
- Check if Heegner-7 43v set contains the Yu-Oh 13v set as subgraph (Cabello shows his Eisenstein set does)
- Note that the BPQS-optimal KS set (Peres-33) has zero CSW advantage (theta-perfect), reinforcing the tension between BPQS optimality and CSW advantage

### For universality_letter
- Is CK-31 unique up to unitary transformations? (Cabello asks this for his set; Trandafir proved uniqueness for the Eisenstein set)
- Does CK-31 contain Yu-Oh 13v as substructure?
- KPS's co-certificate learning technique is relevant to cross-pool mixing strategy

### For sub31_letter
- LBG found 4 KS candidates at order 20 missed by prior enumeration -- tempers confidence in exhaustiveness
- LBG's 17 minimal unembeddable subgraphs up to order 12 -- do our 394 merged graphs contain these as subgraphs?
- Glucose's parallel version Syrup could help with larger instances
- BGK (2018) for quantum advantage motivation (currently absent from sub31)

### For algebraic_islands (main paper)
- CSW Result 3 (perfect graphs) -- check which islands produce perfect orthogonality graphs
- Budroni et al.'s experimental implementation discussion -- which islands are most experimentally accessible?
- Pavicic's automated generation as closest prior art for alphabet-based methodology (4D focus vs our 3D)
- The claim "algebraic substrate determines contextual advantage strength" is genuinely novel beyond CSW -- make prominent

---

## SUMMARY TABLE: Papers x References

| Reference | algebraic_islands | heegner7 | universality | sub31 |
|-----------|:---:|:---:|:---:|:---:|
| Cabello 2025 (simplest) | Cited, extend | Cited, validate | Should cite | **MUST ADD** |
| Cabello 2025 (BPQS) | Cited, extend | Cited, apply | -- | -- |
| Li, Bright, Ganesh 2024 | Should discuss gap | -- | **MUST ADD** | **MUST ADD** |
| Kirchweger et al. 2023 | Should cite | -- | **MUST ADD** | **MUST ADD** |
| Gould & Aravind 2010 | Should cite (norm-2) | -- | **MUST ADD** (precursor!) | -- |
| CSW 2014 | Cited, core framework | Cited, applied | -- | -- |
| Pavicic 2019 | Cited, compare 4D | Note 4D golden | Cite for catalogue | -- |
| Budroni et al. 2022 | Should cite | **Should cite** | -- | -- |
| Bravyi et al. 2018 | Cited (motivation) | -- | -- | Optional motivation |
| Audemard-Simon 2018 | -- | -- | -- | Cited (tool) |
| de Moura-Bjorner 2008 | -- | -- | -- | Cited (tool) |
