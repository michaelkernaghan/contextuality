# Literature Review Notes — 2026-02-18

## Papers Read in Detail

### 1. Trandafir & Cabello (arXiv:2501.11640, PRA 2025)
**"Two fundamental solutions to the rigid KS set problem"**

**Key results:**
- CK-31 and CK-33 are **rigid** (unique up to unitary equivalence)
- Construction: start with 13-element minimal SI-C set (Yu-Oh), complete bases → 25 elements, add all vectors orthogonal to ≥2 existing → 97 elements. CK-37 sits inside this. CK-31 = CK-37 minus 6 vectors.
- **Theorem 3**: No KS set of ≤30 elements can be obtained from the SI-C set by their construction procedure
- **Conjecture 1**: No rigid KS set of ≤30 elements containing the minimal SI-C set exists
- **One assumption**: minimal KS set is rigid AND contains the minimal SI-C set
- KS-81: from super-symmetric SIC, uses ω=e^{2πi/3} coordinates (Eisenstein!)
- **Bootstrap percolation** (Proposition 1): if set A₀ 2-percolates the orthogonality graph, it determines the entire KS set

**Connection to our work:**
- Their rigidity proof means CK-31 is essentially unique — aligns with our finding of one integer island
- KS-81 coordinates use ω (Eisenstein) — falls into our Eisenstein island
- Their SI-C construction is top-down; our alphabet approach is bottom-up. Complementary.
- Their 97-element "closure" of the SI-C set: how does this compare to our 49-ray integer pool?
  - Their closure adds vectors orthogonal to ≥2 existing; our pool is ALL {0,±1,±2} rays
  - Are these the same set? Should check.

### 2. Cortez, Morales & Reyes (arXiv:2211.13216, 2022)
**"Minimal ring extensions of Z exhibiting KS contextuality"**

**Key results:**
- N(S) = lcm{q(v) : v ∈ S} where q(v) = ||v||² — invariant measuring which primes needed
- Projection matrices P_v = vv^T/q(v) live in M_d(Z[1/N(S)])
- **Theorem 1**: Z[1/N] admits no algebraic hidden states iff 6|N (for d=3)
- Minimal ring: **Z[1/6]** — must invert both 2 and 3
- Their 85-vector set Q has N(S)=462=2×3×7×11
- For d≥6: Z itself exhibits contextuality (no ring extension needed)

**Connection to our work:**
- Their N(S) invariant is about projector denominators; our norm-2 boundary is about generator norms. Different but related perspectives.
- 6=2×3: the prime 2 connects to our norm-2 identity (1+1=2). The prime 3 connects to Eisenstein (|ω|²+ω·1+1·ω̄=0, related to 1+ω+ω²=0).
- They work with subrings of Q (localizations Z[1/N]). We work with number field extensions (Z[√2], Z[ω], etc.). These are different algebraic structures answering different questions.
- Key insight: their work shows 2 and 3 are the essential primes for 3D contextuality. Our work shows the algebraic EXTENSIONS at these primes (√2 for norm-2, ω for phase) are what generate the KS structure.
- **Potential bridge**: Can we characterize our six islands in terms of their N(S) invariant? E.g., integer island has all q(v) ∈ {1,2,5,6,9} → N(S)=lcm=90? Should compute.

### 3. Li, Bright & Ganesh (arXiv:2306.13319, IJCAI 2024)
**"SAT solver + CAS attack on minimum KS problem"**

**Key results:**
- Lower bound: **24 vectors** (improved from 22)
- Method: SAT+CAS orderly generation → enumerate all KS candidate graphs → check embeddability
- Encoding: edge variables, triangle variables, squarefree constraint, non-010-colorability
- Embeddability: check against 17 known minimal unembeddable subgraphs (up to order 12), then Z3
- For n=23: 41 KS candidates, all unembeddable. Proof certificate: 40.3 TiB.
- Estimate ~125 CPU-years to push to n=24

**Connection to our work:**
- They work at abstract graph level, not algebraic. Our algebra explains WHY embeddability fails.
- Their unembeddable subgraphs: could these be characterized algebraically?
- Their Z3 embeddability check = our realizability check, but they check individual candidates while we work within fixed algebraic pools
- Gap: 24 (their bound) to 31 (CK-31). Neither approach has closed it.

### 4. Kirchweger, Peitl & Szeider (AAAI 2023)
**"Co-certificate learning with SAT modulo symmetries"**

**Key results:**
- Independent lower bound: **24 vectors** (same as LBG)
- Co-certificate learning: when a graph IS colorable, the coloring blocks all future graphs colorable by the same coloring. One coloring at n=14 covers ~50,000 canonical graphs.
- KS candidate counts: n=17→1, n=19→8, n=20→147, n=21→2497, n=22→88282, n=23→3,747,950
- Only 2 of 3.7M candidates at n=23 don't contain known unembeddable subgraphs

**Connection to our work:**
- Their CCL technique is conceptually related to our CEGAR blocking — learning structural blocking clauses
- The explosive growth in candidates (88K at n=22, 3.7M at n=23) shows why enumeration alone can't reach n=31
- Neither paper discusses merge operations or algebraic structure

### 5. The Pavicic Dispute (2512.10483, 2502.13787, 2503.02974)

**Summary:** Terminological, not mathematical. Pavicic distinguishes:
- "KS sets" = all hyperedges are complete bases (his strict definition)
- "Extended KS" = what others call KS sets (allows incomplete bases)
- "Non-KS contextual" = contextual sets with some incomplete bases

He claims Cabello's "simplest" 33-50 set was already known from his 2023 Quantum paper (the 69-50 set, which reduces to 33-50). Trandafir-Cabello reply that Pavicic's "extended KS" sets add unnecessary observables. The dispute is about definitions and priority, not mathematical substance.

**Relevance to our work:** Minimal. We should use standard KS definitions consistently but don't need to wade into this debate. Our results are independent of terminological choices.

## Key Gaps in the Literature (Our Contributions Fill)

1. **No algebraic number theory approach to KS sets** — Cortez-Morales-Reyes work with Z[1/N] localizations, not number fields. We are the first to study KS-uncolorability as a function of algebraic number field extensions.

2. **No merge/vertex identification analysis** — Neither SAT paper, nor Trandafir-Cabello, discusses what happens when you merge non-orthogonal vertices. Our merge-saturation result is entirely new.

3. **No exact optimization within algebraic pools** — LBG and KPS enumerate abstract graphs; Trandafir-Cabello construct from SI-C. Nobody has done OCUS within a fixed algebraic pool. Our OCUS proof (31 optimal in integer pool) fills this gap.

4. **No systematic survey of which number fields support KS** — Our six-island classification is novel.

## Questions to Investigate

1. Is the Trandafir-Cabello 97-element SI-C closure the same as (or a subset of) our 49-ray integer pool?
2. What is N(S) for each of our six islands?
3. Can merge saturation be proved rather than just observed?
4. Can the bootstrap percolation framework (Trandafir-Cabello) be connected to our norm-2 boundary?
5. Can our algebraic classification explain the unembeddability of the Kirchweger et al. "odd" graphs?
