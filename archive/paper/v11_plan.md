# Version 11 plan

Agreed 2026-11-23, after the v10.4 release. v10.4 finishes the job of withdrawing the claims of
versions 1-9. Version 11 is a tighter restatement organised around one picture: the parameter
space of the alphabet, with uncolourable curves and points marked.

Page figures below are from the v10.4 PDF (26 pages); the savings are estimates, not drafts.

## Keep together (the landscape, about 11 pages)

- Two-symbol theorem (all complex x).
- Real three-symbol theorem (six curves, eight points).
- The circle |x|^2 = 2 and its 45 words.
- Conjugate-closed classification (two circles, four lines, four points).

Each is one method stated once whose output is a list of named curves and points. Keep that form:
state the method, tabulate and name the outputs, no per-case prose.

## Trim or move

1. **Catalogue of pools (v10.4 pp. 18-20).** The golden-ratio, cube-root-of-two and completed
   supergolden pools come from completion with ad hoc letters, not from the landscape theorems,
   and most minima are bounds. Replace with one paragraph stating the construction and one table
   naming the pools. Keep in the structure table only the sets that lie in the landscape.
   About 1.5-2 pages.
2. **Roots of unity, 6 | n (pp. 10-11).** Not on the parameter-plane picture (parameter is n).
   Complete and kernel-checked in Lean. Option: a separate short note ("6 | n, with a Lean
   proof"), cited from a one-paragraph statement here. That is a new arXiv submission: Michael's
   decision, not yet made. About 1.5 pages.
3. **Rigidity (p. 18).** Numerical and off the main line. One sentence plus the open question.
4. **Corrections to versions 1-9.** Keep, shortened if possible. A replacement that withdraws
   claims should say so in the paper itself.

Target: about 20 pages.

## Results to fold in

- The faster-certifier runs at x = zeta/sqrt 2 (floor 33) and x = 1 + i (floor 31), started
  2026-11-23 09:17 PT, still running at the v10.4 release.
- Fix in `ks_certify_fast4.py` first: the time budget is checked only between hitting-set
  solves (line ~105), and one solve can block for hours (eta/sqrt 2 validation, stopped).
- Lean, done after v10.4 (`lean/NamedSets.lean`): uncolourability of the 43- and 47-ray
  sets, and of the 45 words for every x with |x|^2 = 2. Say so where the paper states the
  circle theorem and the catalogue minima, and add the file to the reproducibility list.
- Lean minimality, done after v10.4 (`lean/Minimality.lean`): minimum 31 (integer pool), 43
  (Q(sqrt -7)), 33 (Eisenstein), 33 (Peres), 47 (supergolden, every real root psi). The
  catalogue table can mark these minima "Lean" and the methods paragraph can say the
  certificate (colourable sets plus a lower-bound tree) is kernel-checked. State the limit:
  each pool is an explicit list in the Lean file.
