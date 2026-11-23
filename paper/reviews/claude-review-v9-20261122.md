# Referee report on arXiv v9: "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three"

Reviewer: Claude (Fable 5.2), 2026-11-22. Source reviewed: `paper/algebraic_islands.tex` (1,227 lines, commit 3847542).
A separate Oxford-style review by GPT is in `paper/reviews/` beside this file (see `oxford_review_v9.py`).

## Verdict

**Reject as it stands; rebuild around what is provable.** The paper holds one sound theorem (6 | n), several new
configurations worth recording, and a central idea (the coordinate alphabet) that is better than the paper's own
account of it. Around these sit a tautological observation presented as a discovery, a headline claim (isolated
"islands") that is false inside the paper's own framework, a norm bound the paper contradicts in three places, a
refuted pool minimum, and a layer of internal contradictions left by eight rounds of revision by accretion.

The good news is in section 2: checking the "isolated islands" claim produced an exact result that states the
alphabet idea as a theorem.

## 1. What I checked, and how

| Check | Method | Result |
|---|---|---|
| Proof of Theorem 6 \| n | By hand, case by case | Correct in substance; three small gaps (4.1) |
| "Islands are isolated; no continuous path" | New script `ks_modulus2_circle.py`, exact integer arithmetic plus SAT | **False.** See section 2 |
| Controls for that script | Numeric pools at theta = 0, pi/2, atan(sqrt 7) | Reproduce the paper exactly: 49/120/16, 49/120/16, 145 rays/42 triads |
| Merge saturation (Obs. on 3,756 merges) | Read `ks_peres_merge.py`; short proof | Tautology. See 3.1 |
| BPQS "patterns" | Arithmetic on the paper's own table | First pattern fails on its own row (3.5) |
| Hoffman bound section | Hypotheses of the bound | Bound needs a regular graph; these are not (3.6) |
| CSW "quantum bound" for CK-31 | Eigenvalues of the sum of the 31 projectors | 9.667, 9.667, **11.667**; the rays attain 35/3, not theta = 11.71 (3.7) |
| Golden minimum 52, OCUS claims | Project notes of 2026-09-20; **not re-run today** | 51-ray witness exists; 52 is refuted (3.3) |
| Literature attributions | From memory of the sources and the September GPT check; **not re-opened today** | Listed in 3.10 as items to confirm |

Not checked: the CSW/SDP numbers, the rigidity ranks, the B-KS searches, the class-number survey, the cubic and
supergolden data beyond what the September certification already covered.

## 2. New result: the modulus-2 "islands" are one circle

**Statement (exact for the orthogonalities, SAT for the colouring).** Let x be any complex number with |x|^2 = 2 and
let x* be its conjugate. There is a fixed list of 45 words over {0, +-1, +-x, +-x*} (printed by
`ks_modulus2_circle.py`) whose rays are KS-uncolorable **for every such x**.

Why it is a proof and not a sample: an inner product of two words is a polynomial in x and x*; after reducing with
x x* = 2 it is a combination of 1, x, x*, x^2, x*^2, which are linearly independent on the circle, so it vanishes
for every x iff every integer coefficient vanishes. The script finds 98 such identically-orthogonal pairs and 22
triads among the 45 words, and a SAT solver shows that graph uncolorable. At a special phase extra orthogonalities
only add constraints, and words that coincide as rays must share a colour, which is a restriction of colourings
already shown not to exist.

What it shows:

- The full pool S({0, +-1, +-x, +-x*}) has 145 rays, 378 identically-orthogonal pairs and 34 triads at a generic
  phase and is uncolorable there. Moving the *modulus* to |x|^2 = 2.02 makes it colorable (numeric check).
  Moving the *phase* never does.
- At theta = 0 and theta = pi/2 the 45 words collapse to exactly **33** distinct rays: Peres-33 and its
  Z[sqrt(-2)] twin are the two degenerate points of this family.
- At theta = atan(sqrt 7) the family sits in Z[(1+sqrt(-7))/2]; the pool gains pairs (378 to 522) and triads
  (34 to 42) from the extra relation x + x* = 1. So **the Heegner-7 "island" is a special point of a continuous
  family, not an isolated arithmetic accident**, and what it needs from its ring is |x|^2 = 2, not class number 1.
- For complex x the two-symbol alphabet {0, +-1, +-x} is the wrong object: without x* it is colorable at every
  phase tested except 0 and pi/2. The paper already uses the conjugate-closed alphabet for Heegner-7 without
  saying why.

This is the paper's "modulus-2 mechanism" turned from a pattern into a theorem, and at the same time a refutation of
"no continuous path through parameter space connects one KS-supporting alphabet to another".

Limits, stated plainly. (a) 45 is the size every one of 200 greedy descents reached and the set is ray-critical in
the generic graph; it is **not** a certified minimum. (b) The family is not one set in disguise: the words (1, 1, x) and
(1, 0, x*) are both in the list and their overlap is |1 + x*^2|^2 / 12 = (5 + 4 cos 2 theta) / 12, a unitary
invariant that varies with the phase, so the family contains infinitely many unitarily inequivalent sets. I have
not worked out exactly which phases are equivalent to which. (c) I have **not** searched the literature for this family; Gould-Aravind and
Flores Gordillo treat a phase family through Peres-33 and must be compared before any novelty claim. (d) The
paper's own Observation on rigidity reports the Heegner-7 43-set as infinitesimally rigid; that is consistent only
if the 43-set uses the extra x + x* = 1 edges. Worth confirming, because "rigid at the special point, flexible
around it" would be a clean statement.

## 3. Errors and unsupported claims in v9

### 3.1 Merge saturation is a tautology (delete)
The code merges by *identifying* v2 with v1; the printed Definition says "removing v2 ... deleting all edges incident
to v2", which is deletion and would contradict minimality. With identification the observation is a one-line lemma:
a colouring of the merged graph pulls back to the original by giving v1 and v2 the same colour (every original pair
and triad maps to a pair or 3-clique of the merged graph; v1 and v2 are not orthogonal, so no constraint is lost).
So *every* uncolorable set is "merge-saturated". The 3,756 SAT calls verify the lemma, the conjecture is a trivial
theorem, and it cannot count as evidence for the optimality of CK-31.

### 3.2 "Islands are isolated" is false (section 2), and the paper cites a counterexample itself
Besides section 2, the paper's own rigidity Observation describes a circle of 33-ray KS sets through Peres-33.
The trigonometric sweep (164 sampled angles) cannot establish isolation in any case.

### 3.3 The Golden minimum of 52 is refuted; "OCUS-certified" is not safe as written
A 51-ray ray-critical KS set exists in the completed Q(phi) pool (`golden_51_rays.txt`, found on 54 of 5,033 greedy
descents, 2026-09-20). The paper says the Golden certification ran "at n = 51", which reads as the right experiment
with the wrong number carried forward. Independent re-certification so far: Heegner-7 = 43 and supergolden = 47
hold; Integer 31, Peres 33, Eisenstein 33, Z[sqrt(-2)] 33 and cubic 58 have not been independently re-run. Every
"OCUS-certified" phrase, and "Minimization is now certified", must go until they are. The pool each minimum refers
to (raw or completed) is also never stated.

### 3.4 The norm bound is contradicted three times inside the paper
- x = 2 has |x|^2 = 4, is not a root of unity, and gives CK-31. Calling it "degenerate" does not exempt it.
- Limitations item 6: d = 15 (|alpha|^2 = 4) and d = 5, 6 are uncolorable with enriched alphabets, and "fields with
  |alpha|^2 <= 6 can support KS sets". The abstract says |x|^2 >= 3 gives none.
- |x|^2 is not an invariant of the ray set: S(A(x)) = S(A(1/x)). The paper's own Table 1 lists {0, +-1, +-1/2} as
  identical to the integer pool. "Modulus 2" is equally "modulus 1/2", and the golden explanation ("completion
  generates 1/phi with |1/phi|^2 < 1") explains nothing, because 1/phi is projectively present from the start.

### 3.5 BPQS pattern fails on its own table
"|S_A| + |S_B| >= |B| in every case examined" is followed by "Heegner-7 achieves 21/23". 21 < 23. The second
"pattern" (product about |B|^2/4) rests on six rows, three of them heuristic upper bounds. Limitations item 15
("every Bell scenario achievable by CK-31 is also achievable ... by the Eisenstein island") is a universal claim
drawn from 200 greedy trials.

### 3.6 The Hoffman-bound subsection is wrong
The ratio bound alpha <= n(-lambda_min)/(lambda_max - lambda_min) is a theorem for **regular** graphs. These
orthogonality graphs are irregular (the paper prints their degree sequences). "For connected graphs, this bound is
tight and well-established" is false, and the explanation of alpha/H > 1 by disconnectedness is the wrong
diagnosis. The alpha/H column has no theoretical standing. Delete the subsection.

### 3.7 CSW section: theta is not what the rays attain
theta(G) is a maximum over all orthonormal representations in any dimension. What an island's own rays attain is
the top eigenvalue of the sum of their projectors. For CK-31 that is 35/3 = 11.667 (computed today), against
alpha = 11 and the quoted theta = 11.71. The paper should report the attained value. "theta-perfect" is misused (it
is a statement about all induced subgraphs). The "auxiliary rays amplify the advantage" narrative compares
different graphs and reads a mechanism into five data points.

### 3.8 Internal contradictions (revision by accretion)
- "1,000 MUS extractions ... all returned subsets of exactly 31 rays" against (i) CK-33 being a critical 33-ray
  subset of the same pool, (ii) "CK-31 is rediscovered in 19% of trials", (iii) "six distinct 31-ray sets" against
  "162 distinct minimal KS sets (6 up to automorphism)" against "exactly six distinct minimal 31-sets".
- Section 4.3 opens "a complete proof over the full pool remains computationally infeasible"; the Remark below it
  says OCUS proves it in under 0.2 s.
- Which imaginary quadratic fields "support KS sets": the Heegner table caption says d = 1, 2, 3, 7; the Galois
  subsection says "precisely" d = 2, 3, 7 and that d = 1 fails; the d = 1 row uses a different, enriched alphabet;
  the sentence "d >= 11 gives |N(sqrt(-d))| = d" uses a different generator from the table (norms 3, 5, 11, ...);
  Limitations item 6 adds d = 5, 6, 15.
- Underneath all of these: every ring in the paper contains Z and therefore CK-31. "This field supports / does not
  support a KS set" is not a well-defined property of a field. Only a named finite pool can be colorable.
- Two-generator survey: "22 of 28 are uncolorable", then 17 + 3 = 20 are accounted for.
- "The remaining 76 auxiliary rays add 522 orthogonal pairs": 522 is the pool's total pair count.
- Conjecture support cites "30,000+ random hypergraphs", described nowhere; "density monotonicity" is never defined.
- The abstract announces the refutation of the paper's own earlier thesis; two islands exist only inside the
  Limitations list; three "Notes added" follow the conclusion.

### 3.9 Smaller mathematical errors
- Galois restatement: "(Z/nZ)* surjects onto Z/6Z iff 6 | n" is false (n = 6: the group has order 2; n = 7: it is
  cyclic of order 6). The true statement is mu_6 inside mu_n. Delete.
- "13 projective rays ... far too few for a KS set (the minimum known is 31)" uses an upper bound as a lower bound.
  Use the proved bound 24.
- Table of three-term zero-sums: the justification counts "binom(5+2, 3)" choices from four values (it is 20
  multisets, before signs); two-term sums are omitted although the Definition allows them (the Tr(x) = 0 row,
  Frembs); the row "|x|^2 = 2: sqrt 2, sqrt(-2), ..." has a whole circle of solutions, so "every solution
  corresponds to a known island" is false; sums such as x + x* + |x|^2 = 0 (x = -1 + i) are absent and reduce to a
  listed row only by an inversion argument that is not given. The Reproducibility section says Z3 certifies the
  enumeration complete; the text says Z3 certifies one obstruction for one row.
- Z[i] row of the complex-quadratic table (25/48/6): every nonzero letter is a unit, so the count is 124/4 = 31
  rays; reimplementation gives 31/69/7 (project note, 2026-09-19).
- Rigidity: infinitesimal rigidity is "necessary but not sufficient for global rigidity" is wrong; it implies local
  rigidity and is neither necessary nor sufficient for global. "Four of six islands are rigid" (Remark, Conclusion)
  should read "infinitesimally rigid".
- Division-algebra item: octonionic "rays" and orthogonality are not defined (non-associative scalars), and the
  result (31, CK graph) is forced by Z sitting inside everything. Delete.
- "Eisenstein-33 (this paper)" in the three-33 table: the set is Cabello's.

### 3.10 Literature items to confirm before v10 (not re-opened today)
- Kirchweger-Peitl-Szeider: the September GPT check gives IJCAI-23, pp. 1944-1953, author Tomas Peitl; the bib has
  AAAI-23, 4119-4126, "A. Peitl", and the key is misspelt.
- Cabello, bipartite strategies: project notes record the theorem as "every BPQS defines a **B-KS** set"; the paper
  says "defines a KS set". Check which is proved.
- Cortez-Morales-Reyes: their theorem concerns partial rings of symmetric matrices; the "same number 6" link is an
  analogy until a map between the two statements is given. "A preprint whose arguments we have verified" is a
  strong claim to make in print.
- Kernaghan-Peres 1995: 36 vectors (as printed) or 40. My recollection of the abstract is 36 vectors forming a
  subset of the 40 pentagram rays; the author can settle this faster than anyone.

### 3.11 The central thesis as worded is a tautology
"KS sets arise only when x supports a cancellation identity" is true by definition: orthogonality of two words *is*
a vanishing sum of letter products. The content would have to be in *which* identities suffice, and there the
taxonomy has been adjusted after each counterexample (a third mechanism for supergolden, "indirect modulus-2" for
golden and for the cubic). A classification that absorbs every counterexample by adding a class predicts nothing.

## 4. What is sound

### 4.1 Theorem 6 | n
I verified each case by hand. It holds. Gaps to close in print:
- Sufficiency: add the one-line restriction lemma (a colouring of a superset restricts to a colouring of a subset)
  and list the 33 rays.
- Case 2 (3 does not divide n, 2 divides n): the colouring never mentions the all-nonzero rays. They lie in no
  triad and can all be coloured 0; say so. Also state that the two chosen-green families (planes x = 0 and y = 0)
  are never mutually orthogonal, which the cross-plane computation already shows.
- Case 3: complete the colouring explicitly (one axis green, one ray per all-nonzero triad, everything else 0).
- "Proved algebraically for all four cases": there are three necessity cases plus sufficiency.

### 4.2 Worth keeping, as data with honest labels
- The Heegner-7 43-ray set (independently certified as the pool minimum), the supergolden 47 (Gonzalez), the golden
  set (now <= 51), the cubic set (<= 58, uncertified).
- The Peres / Z[sqrt(-2)] graph isomorphism and the v8 correction of the flex computation, which is a model of how
  to retract.
- The exact rows of the BPQS table.

## 5. Recommendation for v10

The September decision was to replace v9, not patch it, with a short paper on the cyclotomic theorem. I agree with
replacing, and today's result gives that paper a second leg and a better title:

1. **Theorem A (cyclotomic):** the n-th-roots-of-unity pool is uncolorable iff 6 | n.
2. **Theorem B (modulus-2 circle):** for every |x|^2 = 2 the conjugate-closed pool is uncolorable; Peres and
   Z[sqrt(-2)] are its degenerate points and Heegner-7 a special point. Needs the three checks in section 2 first.
3. **The alphabet cube figures** (below) as the way in: they are the origin of the idea and they make Theorem B
   visible, since the picture has exactly one free parameter.
4. A short, plainly labelled data section: named finite pools, their counts, certified minima where certified,
   upper bounds where not, with witnesses in the repository.
5. Dropped entirely: merge saturation, the Hoffman subsection, the Galois reformulation, the division-algebra item,
   the "island" isolation language, the norm >= 3 bound, the operational "Pareto" discussion, the Gleason and
   Cortez-Morales-Reyes parallels.

## 6. Figures

Generated by `make_alphabet_cube_figures.py` into `paper/figures/` (TikZ sources and PDFs).

- `alphabet_cube_generic`: the cube [-x, x]^3 with face lattice lines at 0, +-1, +-x, the 49 lattice rays as dots,
  and nine rays drawn from the centre out through the faces, each labelled with its word. It generalises Peres's
  Fig. 7.2 and Plate II: change x and only the two inner lines move (they sit at 1/x of the half-edge).
- `alphabet_cube_triptych`: the same cube at x = sqrt 2 (Peres-33 filled, as in Fig. 7.2), x = 2 (CK-31 filled,
  from the repository's coordinate list) and x = sqrt 3 (no filled dots; the pool is colorable).

Suggested caption for the first: "A ray whose coordinates form a word over {0, +-1, +-x} leaves the centre of the
cube [-x, x]^3 through a point of the 5 x 5 lattice on a face. The 49 lattice rays are the same for every x; which
pairs are orthogonal is not."

What the figures must not suggest: that the lattice picture covers the complex case (it is the real, two-symbol
family only; Theorem B's pool has 145 rays and needs x*), or that filled dots are the only KS subsets of a pool.
A third figure for Theorem B would be a circle |x|^2 = 2 in the complex plane with the four named points marked.

## 7. Addendum: the GPT Oxford review (same day)

File: `paper/reviews/codex-review-algebraic-islands-v9-20261122-131803.txt` (verdict REJECT, 72 rows). It had
read access to the repository and reached the main conclusions above independently (golden 52, merge tautology,
Galois surjection, norm bound, Hoffman regularity, the BPQS row, theta against the attained value, the tautology
of the central thesis). It also settles one item in 3.10: Kernaghan-Peres 1995 is 36 vectors; keep it.

Findings it made that I did not, with what I confirmed by hand afterwards:

| GPT finding | My check |
|---|---|
| The Eisenstein pool is not closed under completion: (1,1,0) and (1,-1,1) are in it and orthogonal, their complement (1,-1,-2) is not; exact completion gives 165 rays | First half confirmed by hand. The 165 count is GPT's |
| The printed Hermitian-complement formula has a sign error (cyclic indices plus an extra alternating sign) | Confirmed: it gives (1,1,-2) for the pair above, which is not orthogonal to (1,1,0) |
| Merge count "1,204 (Golden-52)" disagrees with 124 pairs: C(52,2) - 124 = 1,202 | Confirmed |
| For a sign- and permutation-symmetric pool the projectors sum to (n/3) I, so the Heegner pool attains 145/3 = 48.3, below alpha = 50: its advertised 11.8% advantage is not attained by its own rays | Confirmed (follows from symmetry and the paper's alpha) |
| The OCUS refinement clause in `ks_ocus_all_pools.py` is unsound, and the reporter can print CERTIFIED for a smaller counterexample | **Not verified by me.** If right, it explains the golden failure and voids every OCUS minimum |
| OCUS ran on raw pools while the closure table attaches the minima to completed pools; Heegner completion runs 145 to 685 rays | Not verified |
| "No floating-point approximation" is false for the cited scripts (`math.sqrt`, tolerance tests) | Not verified; consistent with what I saw in the repo's style |
| `ks_bpqs_sat.py` is not an exhaustive search although the table says "Exact" | Not verified |
| Cabello's theorem yields a B-KS object, not a literal KS subset; orbit counts for Eisenstein (3) and Peres (4) differ from the paper's | Not verified |

Its recommendation for v10 matches section 5 in shape: a short theorem paper plus a separate reproducible data
paper, opening with an explicit withdrawal of the false minimum certificates. Its advice on the cube figure:
restrict to real x > 1, say that antipodal points are one ray, distinguish the pool from the selected subset, show
at least one actual dot-product identity, and do not let the real cube stand for the complex case.
