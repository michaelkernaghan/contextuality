# Status ledger

Every statement of *The Algebraic Landscape of Kochen-Specker Sets in Dimension Three*
(version 11) with the standard of proof it currently meets.

Version 11 (2026-11-23) restates version 10.4 in a new order; theorems, proofs and tables are
unchanged. Review round 6 (`paper/reviews/codex-review-algebraic-islands-v11-round6.txt`)
compared the two versions block by block, read the Lean statements and the checker's soundness
proof, and found no mathematical repair needed; its wording objections (scope of "completely",
the 1 < x < y normalisation in the abstract, origin removed from the four lines, n >= 3,
vectors versus rays, a lost withdrawal of the cubic 58) were fixed the same day and released as
v11.0. Round 7 (`...-v11-round7.txt`) confirmed every round-6 fix and raised three further
wording points (the "standard of proof" sentence did not fit the roots-of-unity theorem; "a
statement about one says nothing about the other" for raw and completed pools; the opening of
the open questions), fixed in v11.1. The reviewer did not run `lake build`; a transcript of the
build and of the axiom audit (`lean/Audit.lean`) is in `results/lean_audit_v11.txt`.

**Rule.** Nothing here is called machine-checked unless a Lean file proving exactly the
recorded statement builds with no `sorry` and no axioms beyond `propext`, `Classical.choice`
and `Quot.sound`. A counterexample to any entry is recorded here with the same standing as a
proof.

## Status levels

| Level | Meaning |
|---|---|
| **Lean** | Proved in Lean 4; checked by the kernel; file named. |
| **Paper** | Proof written out in the paper; read by referees (human or model); not formalised. |
| **Certified** | Computed in exact arithmetic by a named script; for a minimum, the certifier terminated. Reproducible; not formalised. |
| **Bound** | An explicit witness exists; nothing smaller has been excluded. |
| **Pending (resources)** | A Bound that the existing certifier would decide given more time or a faster solver; no new idea needed. Listed under "Pending further resources" below. |
| **Numerical** | Floating-point computation. |
| **Open** | Not known. |

## Lean-checked

Build: `cd lean-ks && lake build` (core Lean 4.36, no mathlib). Audit: `lake env lean Audit.lean` prints the axioms used.

| Statement | Lean | Notes |
|---|---|---|
| A case-split certificate that passes `KS.check` proves the system has no KS colouring | `KS.uncolourable_of_check` in `lean-ks/KS/Basic.lean` | Depends on `propext` only. |
| The 31 rays of Conway and Kochen admit no KS colouring | `KS.CK31.uncolourable` | Orthogonality is recomputed in Lean from the integer coordinates. Certificate: 307 nodes. |
| The 33 rays of Peres admit no KS colouring | `KS.Peres33.uncolourable` | Coordinates in Z[sqrt 2] as integer pairs. Certificate: 911 nodes. |

What the checker does not decide: whether the Lean statement says what the English sentence
says. Two points a reader should confirm for themselves. (1) `Valid` asks that no two
orthogonal rays are both coloured 1 and that every mutually orthogonal triple contains a ray
coloured 1; together these give exactly one per triad. (2) A coordinate `(a, b)` means
`a + b*sqrt(d)`, and the orthogonality test is "both components of the dot product are zero",
which is orthogonality of real vectors because `sqrt 2` is irrational; that last fact is not
part of the Lean development.

Negative control: changing one coordinate of one ray in `CK31.lean` makes `decide` report
that the check is false.

Second project: `cd lean && lake build` (Lean 4.30 + mathlib). Audit: a file containing
`import Cyclotomic6n` and `#print axioms KSCyclotomic.six_divides_iff_ks_uncolorable`, run with
`lake env lean`, lists `propext`, `Classical.choice`, `Quot.sound` (checked 2026-11-23).

`lean/Minimality.lean` (2026-11-23): minimum sizes of six pools. `lake build` checks it (about 9 minutes).
Certificates come from `python ks_lean_minimality.py`: a family of colourable sets with their
colourings, and a branching tree proving that no set of fewer than u rays meets the complement
of every one of them (`KSMin.min_index` is the soundness theorem). The six `minimum_*`
theorems depend on `propext`, `Classical.choice`, `Quot.sound` only. Negative controls are
`example`s in the file, re-checked on every build: for each pool the checker rejects the bound
u + 1, rejects the whole pool offered as a colourable set, and rejects a pair list with one
pair removed. Limits: (1) each pool is the explicit list of vectors in the file; that this
list is every ray with coordinates in the alphabet is not proved in Lean; (2) "minimum of the
pool", not "minimum in dimension three"; (3) the circle's "no shorter list than 45 words" is
not formalised.

`lean/NamedSets.lean` (2026-11-23) is a `lake build` target. Data
between its GENERATED markers comes from `python ks_lean_export.py named`, which also checks
that the ring arithmetic gives the stored graphs (107, 110 and 98 pairs). Audit: the three
`uncolorable` theorems and `exists_psi` depend on `propext`, `Classical.choice`, `Quot.sound`
only. Negative control: moving ray 0 from (0,0,1) to (1,0,1) in any one of the three sets
makes `decide` report `check_ok` false.

| Statement | Lean | Notes |
|---|---|---|
| For n >= 3, the pool of 0 and the n-th roots of unity is KS-uncolourable iff 6 divides n | `KSCyclotomic.six_divides_iff_ks_uncolorable` in `lean/Cyclotomic6n.lean` | Complex vectors over mathlib's `ℂ`; colourings are on vectors, equivalent to rays. |
| The 43 rays over Q(sqrt -7) admit no KS colouring | `KSNamed.Heegner43.uncolorable` in `lean/NamedSets.lean` | Vectors in `ℂ³` with coordinates in Z[alpha], alpha = (1 + i sqrt 7)/2 a specific complex number; alpha^2 = alpha - 2 and conj alpha = 1 - alpha proved. Certificate 675 nodes. |
| The 47 rays over {0, +-1, +-psi, +-psi^2} admit no KS colouring, for every real psi with psi^3 = psi^2 + 1 | `KSNamed.Supergolden47.uncolorable`; `exists_psi` shows such psi exists (intermediate value theorem) | Certificate 499 nodes. |
| For every complex x with x conj(x) = 2, the 45 words of the circle theorem admit no KS colouring | `KSNamed.Circle45.uncolorable` | The uncolourability half of Theorem (modulus-2 circle), for the whole circle. Inner products are reduced with x conj(x) = 2 only, so every orthogonality used holds at every x on the circle. Certificate 1359 nodes. Minimality of 45 is not in Lean. |
| Integer pool {0, +-1, +-2} (49 rays): some 31 rays are uncolourable and every set of fewer than 31 is colourable | `KSMin.IntPool.minimum_31` in `lean/Minimality.lean` | 166 colourable sets, lower-bound tree 969 nodes. |
| Q(sqrt -7) pool {0, +-1, +-alpha, +-alpha*} (145 rays): minimum 43, in the same two-part sense | `KSMin.HeegnerPool.minimum_43` | 476 colourable sets, tree 13187 nodes. |
| Eisenstein pool {0, +-1, +-omega, +-omega^2} (57 rays): minimum 33 | `KSMin.EisPool.minimum_33` | 1082 colourable sets, tree 49307 nodes. |
| Peres pool {0, +-1, +-sqrt 2} (49 rays): minimum 33 | `KSMin.PeresPool.minimum_33` | 33 colourable sets, tree 1 node; uses `irrational_sqrt_two`. |
| sqrt -2 pool {0, +-1, +-sqrt -2} (49 rays): minimum 33 | `KSMin.Sqrtm2Pool.minimum_33` | 33 colourable sets, tree 1 node. |
| Supergolden pool {0, +-1, +-psi, +-psi^2} (109 rays): minimum 47, for every real psi with psi^3 = psi^2 + 1 | `KSMin.SupergoldenPool.minimum_47` | 534 colourable sets, tree 35699 nodes; `indep`: 1, psi, psi^2 independent over Z (no rational root, via `isInteger_of_is_root_of_monic`). |
| The pool for n = 6 is uncolourable | `KSCyclotomic.cabello_S6_uncolorable` | 33 rays over Z[omega] from `ks_lean_export.py eisenstein`; orthogonality recomputed in Z[omega] and carried to `ℂ` by a proved embedding; certificate 1035 nodes, `decide +kernel`. Negative control: moving ray 0 from (0,0,1) to (0,1,1) makes `decide` report the check false. (Moving it to (0,0,1+omega) does not: that is the same ray.) |

## Statements of the paper

| # | Statement | Status | Evidence |
|---|---|---|---|
| Lemma (Restriction) | A set containing an uncolourable set is uncolourable | Paper | One line. |
| Theorem (Two-symbol alphabets) | For every nonzero complex x: which pools of {0, +-1, +-x} are uncolourable; minimum 31 only at x = +-2, +-1/2, otherwise 33; no KS set over {0, +-a, +-b} has fewer than 31 rays | Paper + Certified | Reduction to 37 cases proved in the paper; cases by `ks_two_symbol_theorem.py`; all 37 graphs rebuilt independently in review round 3. |
| Theorem (Real three-symbol alphabets) | For real 1 < x < y the pool of {0, +-1, +-x, +-y} is uncolourable iff two letters have ratio 2 or sqrt 2, or at eight further points; minimum 31 (ratio 2), 33 (ratio sqrt 2 only), 42 to 57 at the eight points; no KS set with real coordinates in {0, +-a, +-b, +-c} has fewer than 31 rays | Paper + Certified | `ks_three_symbol_real.py`: scan in exact arithmetic (rational isolating intervals, prime components via a separating form), 162 cases from 125 irreducible factors, identical to the earlier floating-point scan; check: all 162 graphs (ray partition and edge set) rebuilt from 60-digit coordinates, 0 failures, with positive and negative controls; certify: all 71 uncolourable cases certified with `ks_certify_fast4.py`, each with a separate run excluding sets below 31; witness: a checked minimum set for every case. Review round 5 (2026-11-23): classification confirmed by an independent exact enumeration; its objections (floating-point decisions, check skipped 19 curves and compared counts only, no witnesses archived) fixed the same day. |
| Lemma (vanishing sums of roots of unity) | Two n-th roots of unity sum to zero iff 2 divides n; three iff 3 divides n | Paper | |
| Theorem (6 divides n) | The pool of 0 and the n-th roots of unity is uncolourable iff 6 divides n | Paper + Lean (n >= 3) | Explicit colourings in three cases; checked by SAT for n <= 30. `lean/Cyclotomic6n.lean` proves `six_divides_iff_ks_uncolorable` with no `sorry` (built 2026-11-23); see Lean-checked above. n = 1, 2: the pools are subsets of the colourable pool over {0, +-1}. |
| Theorem (modulus-2 circle) | For every x with |x|^2 = 2 the pool of {0, +-1, +-x, +-x*} is uncolourable; a fixed list of 45 words suffices; no shorter list of words does; the generic pool is colourable | Paper + Certified; uncolourability of the 45 words also Lean | `ks_modulus2_circle.py`; certificate of 408 colourable sets archived in `results/modulus2_circle.json`, re-checked with a second solver in review round 2. Lean: `KSNamed.Circle45.uncolorable` (every x on the circle); "no shorter list" and "generic pool colourable" are not in Lean. |
| Theorem (Conjugate-closed alphabets) | The pool of {0, +-1, +-x, +-x*} is uncolourable exactly when |x|^2 = 2, or |x|^2 = 1/2, or x*/x is a primitive third or sixth root of unity, or x = +-2, +-1/2. Minimum 45 on |x|^2 = 2 and 33 on the other curves away from special points | Paper + Certified | Reviewed in round 4 (correct with wording fixes; 14 pools rebuilt independently). Reduction to 68 cases in the paper; cases by `ks_conjugate_closed_theorem.py`; smallest sets identified by `ks_conjugate_closed_identify.py`. The lines also follow from the two-symbol theorem by Restriction. |
| Same theorem, part (iii) | No uncolourable subset of fewer than 31 rays for any x other than +-1 +- i | Certified | Three of the cases by separate runs that only exclude sets below a given size (`results/conjugate_closed_reruns.jsonl`). |
| Same theorem, x = eta/sqrt 2 and x = 2 zeta (zeta = exp(i pi/3), eta = exp(i pi/6)) | Minimum 33 | Certified | 33-ray witness plus a run excluding every set below 33 (2026-11-23). |
| Same theorem, two special points | Minimum is 32 or 33 at x = zeta/sqrt 2; between 24 and 45 at x = 1 + i | Bound; Pending (resources) | Eight-hour runs on 2026-11-23 did not terminate. |
| Corollary (points of the circle) | Collapse to Peres's 33 rays at sqrt 2 and sqrt -2; contains the 43-ray set at (1 + sqrt -7)/2; the family is not one unitary class | Paper + Certified | |
| Computed fact (Integer pool) | Minimum 31; exactly six minimum sets, one symmetry class | Certified; minimum 31 also Lean | `ks_recertify_v10.py`, `ks_extras_v10.py` |
| Computed fact (Peres pool) | Minimum 33, unique minimum set; same for sqrt -2 | Certified | |
| Computed fact (pools not isomorphic) | The sqrt 2 and sqrt -2 pools have isomorphic minimum sets and non-isomorphic pools | Certified | VF2 |
| Computed fact (Eisenstein pool) | 57 rays, minimum 33, exactly three minimum sets | Certified | |
| Computed fact (Q(sqrt -7) pool) | 145 rays, minimum 43 | Certified | |
| Catalogue: supergolden three-symbol pool {0, +-1, +-psi, +-psi^2} | Minimum 47 | Certified | Re-certified independently as one of the eight points of the three-symbol theorem. |
| Catalogue: six completed pools (Gaussian, Q(sqrt -7), two supergolden, golden, cube root of two) | Minimum at most 33, 43, 47, 47, 51, 60 respectively | Bound; Pending (resources) | Certifier did not terminate within budget. |
| Rigidity table | Numbers of infinitesimal flexes | Numerical | `ks_rigidity_v10.py` |
| Remark (circle |x|^2 = 1/2 is Gould-Aravind's family) | Constant Peres graph on the whole circle; Gould-Aravind Table 3 at a = b = 1, c = 1/x* is our 33-word list ray for ray; diag(b, a, 1) reduces general (a, b, c) to (1, 1, a b* c); members inequivalent for 0 <= theta <= pi/2 via sum of quartic overlaps = 37493/432 + (17/2) cos 2 theta | Certified (exact symbolic) | `ks_half_circle_family.py exact` -> `results/half_circle_family_exact.json` (2026-11-23), after review round 5 found the earlier numerical "pairwise inequivalent on the whole circle" claim false (theta, -theta, theta + pi are equivalent). Penrose = sqrt -2 set rests on Gould-Aravind's parameters for Penrose, not re-derived. Flex counts: Numerical. |

## Pending further resources

Questions the existing method settles as it stands; the runs did not finish within budget. They
need time or faster solvers, not new ideas.

| Question | Note |
|---|---|
| Minimum at x = zeta/sqrt 2: 32 or 33? | Earlier eight-hour runs on 2026-11-23 did not terminate. A second run with `ks_certify_fast4.py` (started 09:17 PT, 8 h budget) was still running at the v10.4 release; its result goes into v11. |
| Does the pool at x = 1 + i contain a KS set of fewer than 31 rays? | The one case of the conjugate-closed theorem with no lower bound of its own. Same status as the row above. |
| Minima of the six completed catalogue pools | Bounds 33, 43, 47, 47, 51, 60 (catalogue row above). |
| All minimum sets on the circle |x|^2 = 2 | One 45-word set exhibited; enumeration not run. |
| Certifier time budget | `ks_certify_fast4.py` checks the budget only between solver calls; the eta/sqrt 2 validation ran 3 h 20 min past its 1 h budget (stopped 2026-11-23 12:45 PT, never counted). Fix before any long run. |
| Lean: minimality of the remaining certified pools (the completed pools with certified minima; the Gaussian raw pool) | Checker done 2026-11-23; these are further runs of `ks_lean_minimality.py` plus a ring model each. |

## Open

No method in hand.

| Question | Note |
|---|---|
| Is 31 the minimum size of a KS set in dimension three? | Known bounds: 24 and 31. Nothing here closes the gap. |
| Can a complex three-symbol alphabet {0, +-1, +-x, +-y} give a KS set of fewer than 31 rays? | Real case settled (no) by the three-symbol theorem; complex case not attempted. |
| Is the second infinitesimal flex of the 45 words a genuine deformation? | |
| Why does completion make the golden-ratio and cube-root-of-two pools uncolourable but not those of sqrt 3 and sqrt 5? | |
| Do the 43-, 45- and 47-ray sets appear in the published catalogues? | Literature comparison not done (reading, not computation). No novelty claimed. |
| Is there a proof by hand that the minimum on |x|^2 = 1/2 is 33, and why do the two circles differ? | |

## Next for Lean

1. Done 2026-11-23: `cabello_S6_uncolorable` discharged; the 6-divides-n theorem is kernel-checked for n >= 3.
2. Done 2026-11-23: uncolourability of the 43- and 47-ray sets, and of the 45 words for every x on the circle (`lean/NamedSets.lean`).
3. Done 2026-11-23: minimality checker (`lean/Minimality.lean`) and the minima 31, 43, 33, 33, 33, 47 of six pools. Still open here: the circle's "no shorter list than 45 words", and proving each pool list complete for its alphabet.
4. The classification theorems, where the finite cases are easy and the reduction over the complex numbers is the hard part.
