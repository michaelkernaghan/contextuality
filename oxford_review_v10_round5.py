"""Round 5 of the v10 challenge review: the real three-symbol theorem, the faster certifier,
and the comparison with Gould and Aravind.

Rounds 1-4 predate Theorem "Real three-symbol alphabets" (thm:threesymbol), the certifier
ks_certify_fast4.py (core reduction and orbit clauses) and the numerical study of the family on
|x|^2 = 1/2 (ks_half_circle_family.py).  This round asks the reviewer to attack those three.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import oxford_review_v10 as O

PROMPT = r"""You are conducting an AGGRESSIVE Oxford-style challenge review of THREE additions to version 10 of "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three" made after your four earlier rounds. (1) The theorem labelled thm:threesymbol ("Real three-symbol alphabets") in the subsection "Real three-symbol alphabets", its proof, table tab:threesymbol, the three remarks after it, and every sentence elsewhere that relies on it (abstract item (E), the introduction, the open questions, the catalogue paragraph on the supergolden alphabet). (2) The paragraph in the Methods section introducing two reductions of the certifier (the core, and adding images of colourable sets under graph symmetries). (3) The second remark after thm:conj, on the family of 33-ray sets on |x|^2 = 1/2 and its comparison with Gould and Aravind. All of this was produced with a large language model; treat every step and number as unverified until you have checked it. Do not re-review the rest of the paper except where it now contradicts or depends on these additions.

You have read access to the repository at C:\Users\Michael Kernaghan\contextuality. New scripts: ks_three_symbol_real.py (modes: scan, check, certify <budget> <workers>), ks_certify_fast4.py, ks_half_circle_family.py, and the new mode one4 of ks_conjugate_closed_theorem.py. Outputs: results/three_symbol_real_scan.json and .log, results/three_symbol_real_check.log, results/three_symbol_real_certify.jsonl and .log, results/half_circle_family.json, results/cc_v4_*.log, and the certify4 records appended to results/conjugate_closed_reruns.jsonl. ks_certify_fast4.py builds on ks_certify_fast3.py and ks_recertify_v10.py, which you have read before. The scan mode of ks_three_symbol_real.py takes some minutes; run it if you can. Do not run certify (hours).

Be specific, quote the paper, and where a short calculation or a reading of the code settles a point, do it and show it.

STEP 1 -- THE REDUCTION. (a) Is every real three-symbol alphabet with three distinct nonzero absolute values equivalent to {0,+-1,+-x,+-y} with 1<x<y, and are the degenerate cases (equal absolute values, a zero letter) really two-symbol alphabets covered by thm:twosymbol(iii)? (b) Is every inner product and every 2x2 minor of two words an integer combination of 1, x, y, x^2, xy, y^2 with sum |c_k| <= 3, and are there 376 nonzero vectors? (c) Is "the pool and its graph at P depend only on the set F(P) of irreducible factors vanishing at P" correct, including for proportionality of words? (d) Is the list of realised sets F(P) complete: the empty set, {f} for each curve meeting D, and the sets at points of D on two curves or singular on one? Could a set F(P) with |F(P)| >= 2 occur along a whole curve (two different irreducibles sharing a component is impossible, but check the script handles factors that are equal up to sign or a constant)? Could an isolated real point of one curve, or a point where a curve is tangent to y = x or x = 1, be missed? Is the cell decomposition in branch_in_D (cuts at discriminant, leading coefficient, f(x,x), x = 1) enough to decide whether a curve meets D? (e) Are there 31 curves meeting D, 130 special sets, and is the count 1 + 31 + 130 = 162 right?

STEP 2 -- THE SCRIPT. Read ks_three_symbol_real.py line by line. Check inner_vec and minor_vec, factorise and norm_poly, branch_in_D and in_D, components, points_of, special_sets (Groebner membership and the 55-digit cross-check), pool, colourable, check (an independent rebuild from floating-point coordinates: is it actually independent of pool?), and symmetries (are the 24 maps genuine automorphisms, and is each checked?). Recompute independently, with your own code, at least: a generic point; a generic point of x = 2, of y^2 = 2x^2 and of one colourable curve; and the points (sqrt(phi), phi), (psi, psi^2), (1+sqrt3, 2+sqrt3) and (sqrt(2+2 sqrt2), 1+sqrt2). Report rays/pairs/triads/colourability against the results files and tab:threesymbol.

STEP 3 -- THE CERTIFIER. Read ks_certify_fast4.py. (a) Is the core reduction sound: does a minimum uncolourable subset always lie in the core, and does the code delete exactly the rays in no triad, iterated? Is it sound to delete a ray that lies in an orthogonal pair but in no triad? (b) Are orbit clauses sound: if M is colourable and g is a permutation of rays preserving the orthogonal pairs and the triads, is g(M) colourable? Does check_group verify both pairs and triads, on the core or on the full pool, and is that the right object? (c) Is the floor device (start from a dummy upper bound of size L; "optimal" proves no uncolourable subset below L) still sound with these two changes? (d) Check the validations recorded in the logs: 2 zeta floor 33 (paper says 33), Q(sqrt -7) floor 44 (paper says 43), and whatever the eta/sqrt2 validation shows. (e) In results/three_symbol_real_certify.jsonl, does every one of the 71 records have no_set_below_31 true and a certified minimum equal to its upper bound, with a witness that the script checked uncolourable?

STEP 4 -- IS WHAT IS PROVED EXACTLY WHAT IS STATED? Check (i), (ii), (iii) of thm:threesymbol against the JSON files: the six curves, the 57 uncolourable special sets on them, the eight others, and the minima (31 when two letters have ratio 2, 33 when ratio sqrt2 only, 42-57 at the eight points). Check each row of tab:threesymbol: the relations, that the point is the unique point of D satisfying them, the coordinates, the counts and the minimum. Check the remark that the supergolden point re-certifies 47 independently of the catalogue. Is the theorem consistent with the facts stated elsewhere: {0,+-1,+-2,+-3}, {0,+-1,+-sqrt2,+-2} and {0,+-1,+-phi,+-2} have minimum 31; {0,+-1,+-phi,+-phi^2} and {0,+-1,+-c,+-c^2} (c = cube root of 2) are colourable?

STEP 5 -- THE GOULD-ARAVIND REMARK. Read ks_half_circle_family.py and results/half_circle_family.json. Is the claim that the 33-ray family on |x|^2 = 1/2 has constant Peres graph, pairwise inequivalent members, exactly one non-trivial infinitesimal flex at each sampled member, and a velocity that is a non-trivial flex, supported? Is the trivial-motion space (u(3) plus one phase per ray) correctly computed? Does "coincides near Peres's set with the family of Gould and Aravind" follow (uniqueness of a one-dimensional deformation space), and is the paper honest that it is numerical and local?

STEP 6 -- VERDICT. Is thm:threesymbol correct as stated and adequately proved for a preprint? Are the certifier reductions sound? Is the Gould-Aravind remark supported? What must change before release?

OUTPUT FORMAT.
1. Up-front verdict on each of the three additions: CORRECT AS STATED / CORRECT WITH WORDING FIXES / GAP IN PROOF / WRONG, one-line justification each.
2. A table of actionable issues: | Priority (High/Med/Low) | Step | Issue (quote the paper) | Suggested fix |. Separate demonstrated errors from unsupported claims and from things you could not check.
3. A short list: claims you independently confirmed, with the method used.
4. The Step 6 answer as short prose.

Do not flatter. Do not equivocate. If a part is solid, say so once and move on."""


def main():
    tex = O.assemble()
    hits = [(i, ln) for i, ln in enumerate(tex.splitlines(), 1)
            for p in O.INJECTION if re.search(p, ln, re.IGNORECASE)]
    if hits:
        print("Injection pre-scan flagged %d line(s); aborting." % len(hits))
        return 1
    text = O.strip_latex(tex)
    print("Extracted %d words from the assembled v10 draft" % len(text.split()))
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "algebraic_islands_v10.txt"
        f.write_text(text, encoding="utf-8")
        cmd = [sys.executable, str(O.REVIEWER), str(f), "--prompt", PROMPT, "--model", O.MODEL,
               "--timeout", "3300"]
        return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
