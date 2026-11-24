# The Algebraic Landscape of Kochen-Specker Sets in Dimension Three

Code, data and machine-checked proofs for the paper of that name
([arXiv:2603.16988](https://arxiv.org/abs/2603.16988)). The current version of the paper is
**version 11** (release tag `v11.1`):

- PDF: [`paper/algebraic_islands_v11.pdf`](paper/algebraic_islands_v11.pdf)
- Source: [`paper/algebraic_islands_v11.tex`](paper/algebraic_islands_v11.tex) and `paper/v11_*.tex`
- Standard of proof for every statement: [`LEDGER.md`](LEDGER.md)

> **Versions 1-9 are withdrawn.** They proposed a classification of Kochen-Specker (KS) sets by
> "cancellation mechanisms" and described the uncolourable coordinate alphabets as isolated
> "algebraic islands". That classification did not survive checking. In particular the claimed
> minimum of 52 rays for the golden-ratio pool is wrong (a 51-ray set exists), the "norm bound"
> is false, and the alphabets are not isolated. Appendix A of the paper lists the withdrawn
> claims. Material in this repository written for those versions is kept as history and is
> marked as such; do not rely on it.

## What the paper proves

A *coordinate alphabet* is the set of numbers allowed as ray coordinates, such as
{0, ±1, ±√2} for the 33 rays of Peres and {0, ±1, ±2} for the 31 rays of Conway and Kochen. An
alphabet generates a finite pool of rays, and the pool either has a KS colouring or does not.

1. **Two-symbol alphabets {0, ±1, ±x}, x complex.** The pool is uncolourable only when x or
   1/x is ±2, ±√2, ±√−2, or x is a primitive third or sixth root of unity. No KS set with
   coordinates in such an alphabet has fewer than 31 rays.
2. **Real three-symbol alphabets {0, ±1, ±x, ±y}, 1 < x < y.** Uncolourable exactly when two
   letters have ratio 2 or √2, or at eight further points. Again no KS set has fewer than 31
   rays.
3. **Conjugate-closed alphabets {0, ±1, ±x, ±x\*}.** Uncolourable exactly when |x|² = 2, or
   |x|² = 1/2, or x\*/x is a primitive third or sixth root of unity, or x is ±2 or ±1/2. On the
   circle |x|² = 2 one fixed list of 45 words is uncolourable at every point; the circle
   |x|² = 1/2 carries the 33-ray family of Gould and Aravind.
4. **Roots of unity.** The pool of 0 and the n-th roots of unity is uncolourable if and only
   if 6 divides n.

Two minima in family 3 are not determined, and the gap between the known bounds 24 and 31 for
the smallest KS set in dimension three is not closed. See "Open questions" in the paper and
"Pending further resources" in the ledger.

## Proofs checked in Lean

The folder [`lean/`](lean) holds three Lean 4 files (Lean 4.30 with mathlib). They use no axioms
beyond `propext`, `Classical.choice` and `Quot.sound`.

| File | What it proves |
|---|---|
| `Cyclotomic6n.lean` | Result 4 for n ≥ 3 |
| `NamedSets.lean` | The 43-ray set over Q(√−7) and the 47-ray supergolden set are uncolourable; the 45 words are uncolourable for every x with \|x\|² = 2 |
| `Minimality.lean` | Minimum KS subsets of six pools: 31 (integer), 33 (√2), 33 (√−2), 33 (Eisenstein), 43 (Q(√−7)), 47 (supergolden) |

```bash
cd lean
lake build                 # about ten minutes after mathlib is fetched
lake env lean Audit.lean   # prints the axioms each theorem depends on
```

A transcript of the build and audit for this release is in
[`results/lean_audit_v11.txt`](results/lean_audit_v11.txt). Limits, stated in the paper: each
pool is an explicit list of vectors in the Lean file, and Lean does not prove that the list is
every ray of the alphabet; the minima are minima within a pool; the three continuous
classifications (results 1-3) are not formalised.

A second, smaller project, [`lean-ks/`](lean-ks), proves the uncolourability of the Conway-Kochen
31 rays and the Peres 33 rays in core Lean 4 with no mathlib.

## Reproducing the paper

Appendix B of the paper lists the script behind every table. The main ones:

| Script | Produces |
|---|---|
| `ks_two_symbol_theorem.py` | Two-symbol classification (about five seconds) |
| `ks_three_symbol_real.py` | Real three-symbol classification, in exact arithmetic (`scan`, `check`, `certify`, `witness`) |
| `ks_conjugate_closed_theorem.py` | Conjugate-closed classification (`scan`, `certify`, `one`, `one4`) |
| `ks_modulus2_circle.py` | The 45 words on the circle \|x\|² = 2 |
| `ks_half_circle_family.py` | The 33-ray family on \|x\|² = 1/2 and its identification with Gould and Aravind |
| `ks_verify_cyclotomic_theorem.py` | Roots-of-unity pools, n ≤ 30 |
| `ks_recertify_v10.py`, `ks_certify_fast3.py`, `ks_certify_fast4.py` | Certified minima of the named pools |
| `ks_lean_export.py`, `ks_lean_minimality.py` | The rays and certificates inside the Lean files |

Result files are under [`results/`](results). Reviews of the paper by a second language model
acting as a hostile examiner are under [`paper/reviews/`](paper/reviews).

Requirements: Python 3.13, [PySAT](https://pysathq.github.io/), NetworkX, NumPy, SciPy, SymPy.

```bash
pip install python-sat networkx numpy scipy sympy
```

## Older material

- **Scripts from versions 1-9** (for example `ks_islands.py`, `ks_new_islands.py`,
  `ks_ocus_all_pools.py`) remain in the repository. They should not be used to reproduce the
  current paper. The certification procedure in `ks_ocus_all_pools.py` is unsound.
- **Version 9 of the paper** is [`paper/algebraic_islands.tex`](paper/algebraic_islands.tex);
  version 10 is `paper/algebraic_islands_v10.tex`. Both are kept for the record.
- **Letters** (`paper/cyclotomic_letter.tex`, `paper/heegner7_letter.tex`,
  `paper/sub31_letter.tex`, `paper/universality_letter.tex`) were written alongside versions
  1-9 and have not been revised. Where they disagree with version 11, version 11 is intended.
- **The pages under [`docs/`](docs)** (the "Contextuality & KS Set Atlas") include pages on the
  withdrawn classification. Those pages carry a notice at the top.
- The complete development history is on the [`archive-full`](../../tree/archive-full) branch.

## How this was produced

Computations, proofs and text were produced with a large language model (Claude, Anthropic)
under the author's direction, and reviewed by a second model (GPT, OpenAI) instructed to act as a
hostile examiner. Agreement between language models is not a proof. The safeguards are exact
arithmetic, a certifier with a short soundness argument, kernel-checked proofs where they exist,
and an explicit list of what was not checked. Details are in Appendix C of the paper.

## References

- M. Kernaghan, "Bell-Kochen-Specker theorem for 20 vectors," *J. Phys. A* **27**, L829-L830 (1994).
- M. Kernaghan and A. Peres, "Kochen-Specker theorem for eight-dimensional space," *Phys. Lett. A* **198**, 1-5 (1995).

## License

This code is provided for academic reproducibility. See the paper for citation details.
