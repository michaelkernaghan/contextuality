"""Round 6 of the challenge review: the version 11 draft.

Version 11 restates version 10.4 in a new order and adds claims that results are proved in
Lean.  The theorems, proofs and tables were moved from v10.4 without change; the abstract,
introduction, connecting text, the Lean paragraphs, one figure and the trimmed catalogue are new.
This round asks the reviewer to attack (1) every "proved in Lean" claim against the Lean
sources, (2) the restructure, and (3) the new text.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import oxford_review_v10 as O

MAIN = "algebraic_islands_v11.tex"

PROMPT = r"""You are conducting an AGGRESSIVE Oxford-style challenge review of the VERSION 11 DRAFT of "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three". You reviewed version 10 in five rounds. Version 11 claims to be a restatement of version 10.4 in a new order, with three kinds of new material: (1) claims that certain results are proved in the Lean 4 proof assistant; (2) a restructure (results-first abstract and introduction; the three-symbol theorem as its own section with a new figure; the conjugate-closed section reordered with the classification first, then the circle |x|^2=2, then a new subsection on |x|^2=1/2; rigidity cut to one paragraph without its table; the catalogue cut to one section "Other pools"; corrections, reproducibility and "how this version was produced" moved to appendices; the table of imaginary quadratic fields removed); (3) new connecting prose. All of it was produced with a large language model; treat every sentence as unverified until checked. The theorems, proofs and tables that were moved unchanged you have reviewed before: do not re-review their mathematics, but DO check that nothing was lost or contradicted by the move.

You have read access to the repository at C:\Users\Michael Kernaghan\contextuality. Version 11 sources: paper/algebraic_islands_v11.tex and paper/v11_*.tex. Version 10.4 sources for comparison: paper/algebraic_islands_v10.tex and paper/v10_s*.tex. Lean sources: lean/Cyclotomic6n.lean, lean/NamedSets.lean, lean/Minimality.lean (this last file is 2.4 MB, almost all generated certificate data between "BEGIN GENERATED" and "END GENERATED" markers: do NOT read the data; read the definitions, theorem statements and proofs outside the markers, e.g. by searching for "theorem", "def ", "inductive", "structure", "example"). Export scripts: ks_lean_export.py (mode named), ks_lean_minimality.py. Status ledger: LEDGER.md. Do not run lake build (ten minutes, and it needs mathlib); the author reports it succeeds and that "#print axioms" gives propext, Classical.choice, Quot.sound for every theorem named below. You may take that on trust but say that you did.

Be specific, quote the paper, and where reading the Lean or a short calculation settles a point, do it and show it.

STEP 1 -- DO THE LEAN THEOREMS SAY WHAT THE PAPER SAYS? For each of the following, quote the Lean statement and the paper's sentence about it, and say whether they match exactly, match with a caveat the paper states, match with a caveat the paper does NOT state, or do not match.
(a) KSCyclotomic.six_divides_iff_ks_uncolorable (Theorem thm:6n for n >= 3).
(b) KSNamed.Heegner43.uncolorable, KSNamed.Supergolden47.uncolorable and exists_psi, KSNamed.Circle45.uncolorable ("for every complex x with x x* = 2 the 45 words admit no coloring"). For Circle45: is the hypothesis x * conj x = 2 the right one; are the 45 Lean rays the 45 words of the paper's Table tab:words (compare with results/modulus2_circle.json via ks_lean_export.circle45_coords); is the reduction lmul (x x* -> 2) correct; is the zero test only sufficient and is that enough; does vset allow two words to coincide at special x without breaking the conclusion?
(c) KSMin.IntPool.minimum_31, HeegnerPool.minimum_43, EisPool.minimum_33, PeresPool.minimum_33, Sqrtm2Pool.minimum_33, SupergoldenPool.minimum_47. The paper says: "some u of the pool's vectors form an uncolorable set, and every set of fewer than u of them has a coloring". Check the definitions this rests on: KSCyclotomic.IsColoring / IsTriad / KSUncolorable (is this the paper's definition of coloring, including that an orthogonal pair in no triad is still a constraint?), KSNamed.vset, KSMin.ValidOn, Pool.ok, colOK, checkLB, packOK, the constructor LB.dead, min_index, colorable_of_index, minimum_eq. Is the soundness argument of the lower-bound tree right (a leaf lists complements that miss the included rays and are pairwise disjoint after removing excluded rays)? Is there any way a wrong certificate could pass: for example Pool.ok not forcing the pair and triad lists to be complete, colOK checking pairs only inside the listed pairs, T not being required to lie inside the set, BT.get returning a default leaf for an out-of-range index, Nat.testBit on bits >= n, the hypothesis T.ncard < u being vacuous for infinite T, or the ring-injectivity lemmas (not_real, ι_eq_zero, indep, irrational_sqrt_two) being used in the wrong direction? Are the negative-control "example"s meaningful?
(d) The paper states two limits: each pool is an explicit list of vectors in Lean, not proved to be all rays of the alphabet; and these are minima within a pool. Are there further limits it should state? In particular: does the Lean pool for {0,+-1,+-2} have exactly the 49 rays of the paper's pool (check ks_lean_minimality.intpool and primitive()); for the Q(sqrt -7) pool is the scaling by 1 or 2 harmless; is the statement about vectors really a statement about rays (distinct list entries could be proportional vectors: does distinctB or anything else rule that out, and does it matter for either half of the theorem)?
(e) Every place the paper says "proved in Lean", "checked by the Lean kernel", "kernel-checked" or marks a table entry with the superscript L: list them and check each against (a)-(c). Is "six of the minima and Theorem thm:6n are checked by the Lean kernel" accurate? Is the abstract's sentence accurate?

STEP 2 -- THE RESTRUCTURE. Compare version 11 with version 10.4. (a) List every theorem, lemma, corollary, computed fact, table and figure of v10.4 and say whether it is present unchanged, present changed, or absent in v11. For each one absent or changed, is the change intended (see the list above) and is anything else in v11 still relying on what was removed (the rigidity table, the imaginary-quadratic table tab:heegner and the Gaussian-alphabet paragraph, the golden-ratio and cubic subsections, three rows of the profiles table)? (b) Are there forward references that now read wrongly because sections were reordered (e.g. "the previous subsection", "below", "above", "Section sec:circle" meaning the old section)? (c) Does the new order introduce any circularity: is anything used before it is proved in a way that matters logically? (d) Do the remarks after thm:conj and the new subsection on |x|^2 = 1/2 say exactly what the v10.4 text said, no more? Check the new sentence "cannot contain a 33-ray KS set there, since the minimum on that circle is 45" and the sentence "The two families meet in Peres's set: P(sqrt 2) = P(1/sqrt 2)". (e) The rigidity paragraph replaces a table: check every flex count in it against the v10.4 table and results (ks_rigidity_v10.py outputs), including "each of nine sampled members".

STEP 3 -- NEW TEXT. (a) Abstract and the "Results" paragraph of the introduction: is every clause a correct statement of a theorem as proved? Any overclaim, e.g. "we answer it completely for three families" given the two undetermined minima of thm:conj and the restriction of thm:threesymbol to real letters? (b) The new figure fig:threesymbol: are the six lines and eight points drawn where the theorem puts them (coordinates in the tikz source of paper/v11_s3_three.tex against tab:threesymbol), is the domain right, is the caption right ("31 where a light line meets a heavy one")? (c) "Other pools": the new paragraph on completion and the supergolden paragraph: any number changed or scope blurred (raw vs completed) relative to v10.4? (d) "Open questions" and "Conclusion": consistent with the rest? (e) Appendices: anything in the corrections list now stale?

STEP 4 -- VERDICT. Is version 11 fit to replace version 10.4 on arXiv? What must change first?

OUTPUT FORMAT.
1. Up-front verdict on each of: the Lean claims; the restructure; the new text. One of CORRECT AS STATED / CORRECT WITH WORDING FIXES / OVERCLAIMS / WRONG, with a one-line justification each.
2. A table of actionable issues: | Priority (High/Med/Low) | Step | Issue (quote the paper or the Lean) | Suggested fix |. Separate demonstrated errors from unsupported claims and from things you could not check.
3. A short list: claims you independently confirmed, with the method used.
4. The Step 4 answer as short prose.

Do not flatter. Do not equivocate. If a part is solid, say so once and move on."""


def assemble():
    tex = (O.PAPER / MAIN).read_text(encoding="utf-8")

    def inline(m):
        f = O.PAPER / m.group(1)
        return f.read_text(encoding="utf-8") if f.exists() else m.group(0)
    for _ in range(2):
        tex = re.sub(r"\\input\{([^}]+)\}", inline, tex)
    return tex


def main():
    tex = assemble()
    hits = [(i, ln) for i, ln in enumerate(tex.splitlines(), 1)
            for p in O.INJECTION if re.search(p, ln, re.IGNORECASE)]
    if hits:
        print("Injection pre-scan flagged %d line(s); aborting." % len(hits))
        return 1
    text = O.strip_latex(tex)
    print("Extracted %d words from the assembled v11 draft" % len(text.split()))
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "algebraic_islands_v11.txt"
        f.write_text(text, encoding="utf-8")
        cmd = [sys.executable, str(O.REVIEWER), str(f), "--prompt", PROMPT, "--model", O.MODEL,
               "--timeout", "3300"]
        return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
