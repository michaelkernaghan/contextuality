# Status ledger

Every statement of *The Algebraic Landscape of Kochen-Specker Sets in Dimension Three*
(version 10) with the standard of proof it currently meets.

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

## Statements of the paper

| # | Statement | Status | Evidence |
|---|---|---|---|
| Lemma (Restriction) | A set containing an uncolourable set is uncolourable | Paper | One line. |
| Theorem (Two-symbol alphabets) | For every nonzero complex x: which pools of {0, +-1, +-x} are uncolourable; minimum 31 only at x = +-2, +-1/2, otherwise 33; no KS set over {0, +-a, +-b} has fewer than 31 rays | Paper + Certified | Reduction to 37 cases proved in the paper; cases by `ks_two_symbol_theorem.py`; all 37 graphs rebuilt independently in review round 3. |
| Lemma (vanishing sums of roots of unity) | Two n-th roots of unity sum to zero iff 2 divides n; three iff 3 divides n | Paper | |
| Theorem (6 divides n) | The pool of 0 and the n-th roots of unity is uncolourable iff 6 divides n | Paper; Lean except one finite fact | Explicit colourings in three cases; checked by SAT for n <= 30. `lean/Cyclotomic6n.lean` (Lean 4.30 + mathlib) states and proves `six_divides_iff_ks_uncolorable` with a single remaining `sorry`, `cabello_S6_uncolorable`: that the 57-ray pool for n = 6 is uncolourable. Not rebuilt on 2026-11-22; status taken from the file and its last commit. |
| Theorem (modulus-2 circle) | For every x with |x|^2 = 2 the pool of {0, +-1, +-x, +-x*} is uncolourable; a fixed list of 45 words suffices; no shorter list of words does; the generic pool is colourable | Paper + Certified | `ks_modulus2_circle.py`; certificate of 408 colourable sets archived in `results/modulus2_circle.json`, re-checked with a second solver in review round 2. |
| Theorem (Conjugate-closed alphabets) | The pool of {0, +-1, +-x, +-x*} is uncolourable exactly when |x|^2 = 2, or |x|^2 = 1/2, or x*/x is a primitive third or sixth root of unity, or x = +-2, +-1/2. Minimum 45 on |x|^2 = 2 and 33 on the other curves away from special points | Paper + Certified | Reviewed in round 4 (correct with wording fixes; 14 pools rebuilt independently). Reduction to 68 cases in the paper; cases by `ks_conjugate_closed_theorem.py`; smallest sets identified by `ks_conjugate_closed_identify.py`. The lines also follow from the two-symbol theorem by Restriction. |
| Same theorem, part (iii) | No uncolourable subset of fewer than 31 rays for any x other than +-1 +- i | Certified | Three of the cases by separate runs that only exclude sets below a given size (`results/conjugate_closed_reruns.jsonl`). |
| Same theorem, x = eta/sqrt 2 and x = 2 zeta (zeta = exp(i pi/3), eta = exp(i pi/6)) | Minimum 33 | Certified | 33-ray witness plus a run excluding every set below 33 (2026-11-23). |
| Same theorem, two special points | Minimum is 32 or 33 at x = zeta/sqrt 2; between 24 and 45 at x = 1 + i | Bound | Eight-hour runs on 2026-11-23 did not terminate. |
| Corollary (points of the circle) | Collapse to Peres's 33 rays at sqrt 2 and sqrt -2; contains the 43-ray set at (1 + sqrt -7)/2; the family is not one unitary class | Paper + Certified | |
| Computed fact (Integer pool) | Minimum 31; exactly six minimum sets, one symmetry class | Certified | `ks_recertify_v10.py`, `ks_extras_v10.py` |
| Computed fact (Peres pool) | Minimum 33, unique minimum set; same for sqrt -2 | Certified | |
| Computed fact (pools not isomorphic) | The sqrt 2 and sqrt -2 pools have isomorphic minimum sets and non-isomorphic pools | Certified | VF2 |
| Computed fact (Eisenstein pool) | 57 rays, minimum 33, exactly three minimum sets | Certified | |
| Computed fact (Q(sqrt -7) pool) | 145 rays, minimum 43 | Certified | |
| Catalogue: supergolden four-letter pool | Minimum 47 | Certified | |
| Catalogue: six completed pools (Gaussian, Q(sqrt -7), two supergolden, golden, cube root of two) | Minimum at most 33, 43, 47, 47, 51, 60 respectively | Bound | Certifier did not terminate within budget. |
| Rigidity table | Numbers of infinitesimal flexes | Numerical | `ks_rigidity_v10.py` |

## Open

| Question | Note |
|---|---|
| Does the pool at x = 1 + i contain a KS set of fewer than 31 rays? | The one case of the conjugate-closed theorem with no lower bound of its own; an eight-hour run did not decide it. |
| Is the family of 33-ray sets along |x|^2 = 1/2 the family of Gould and Aravind? | It has the graph of Peres's set. Not compared. |
| Is 31 the minimum size of a KS set in dimension three? | Known bounds: 24 and 31. Nothing here closes the gap. |
| Can a three-symbol alphabet {0, +-1, +-x, +-y} give a KS set of fewer than 31 rays? | Same method applies in principle; not attempted. |
| Is the second infinitesimal flex of the 45 words a genuine deformation? | |
| Why does completion make the golden-ratio and cube-root-of-two pools uncolourable but not those of sqrt 3 and sqrt 5? | |
| Do the 43-, 45- and 47-ray sets appear in the published catalogues? | Literature comparison not done. No novelty claimed. |

## Next for Lean

1. Discharge `cabello_S6_uncolorable`: export the Eisenstein 33 rays over Z[omega] with a certificate, and connect the finite check to the complex-number statement in `lean/Cyclotomic6n.lean`. That would make the 6-divides-n theorem fully machine-checked.
2. Uncolourability of the other named sets (the 43-, 45- and 47-ray sets).
3. Minimality: a checker for the certificates (a list of colourable sets with their colourings, plus a refutation of a small hitting set).
4. The classification theorems, where the finite cases are easy and the reduction over the complex numbers is the hard part.
