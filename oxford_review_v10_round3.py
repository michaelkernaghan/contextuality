"""Round 3 of the v10 challenge review: the two-symbol theorem only.

Rounds 1 and 2 (oxford_review_v10.py) predate Theorem "Two-symbol alphabets" and its
script ks_two_symbol_theorem.py.  This round asks the reviewer to attack that theorem.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import oxford_review_v10 as O

PROMPT = r"""You are conducting an AGGRESSIVE Oxford-style challenge review of ONE new result added to version 10 of "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three" after your two earlier rounds: the theorem labelled thm:twosymbol ("Two-symbol alphabets"), its proof, its table (tab:twosymbol), the four remarks after it, and every sentence elsewhere in the paper that relies on it (abstract item (C), the introduction, the open questions, the conclusion). The theorem and its computation were produced with a large language model; treat every step and number as unverified until you have checked it. The rest of the paper was covered in rounds 1 and 2; do not re-review it except where it now contradicts or depends on the new theorem.

You have read access to the repository at C:\Users\Michael Kernaghan\contextuality. The new script is ks_two_symbol_theorem.py and its output is results/two_symbol_theorem.json. It uses ks_recertify_v10.py, ks_certify_fast3.py, ks_verify_large_minima.py and ks_extras_v10.py, which you have already read.

Be specific, quote the paper, and where a short calculation or a reading of the code settles a point, do it and show it.

STEP 1 -- THE REDUCTION TO FINITELY MANY CASES. (a) Is it true that the orthogonality graph of the pool of {0,+-1,+-x} depends on x only through which words are proportional and which of the 128 coefficient vectors vanish? (b) Is the proportionality claim right: are x in {+-1, +-i} the only nonzero x at which extra words coincide, and is the list of possible 2x2 minors complete? (c) Is the description of each vector's solution set right (empty, finitely many real points, the real axis, a vertical line, a circle centred on the real axis)? Are there exactly nine curves, and are they the ones listed? (d) Is the stratification argument valid: constant graph off all curves, constant on each curve away from special points? Is the set of special points complete -- every real root, every pairwise intersection including tangencies, and the coincidence points? Is the count 27 up to conjugation right? (e) Is it legitimate to ignore the sign of Im x? (f) Is anything lost by x = 0 being excluded, or by treating x = +-1?

STEP 2 -- THE SCRIPT. Read ks_two_symbol_theorem.py line by line. Does locus() classify all 128 vectors correctly? Does intersect() cover every pair of curve types, including tangent circle/line and circle/circle cases? Does sample() really return a point at which exactly the vectors with that locus vanish? Are Pt.vanishes and Pt.poly_vanishes exact and correct for points a + i sqrt(B) with a in Q(sqrt d)? Does pool() identify rays and orthogonality correctly from the formal coefficient vectors (check the conjugation convention in inner_vec and that orthogonality is well defined on rays)? Are the triads all triangles? Is the use of certify3 sound here and did every uncolourable case terminate? Recompute independently at least: the generic pool, one curve, x = 2, x = sqrt(2), x = sqrt(-2), a primitive sixth root of unity, x = 1+i and x = (1+sqrt(-7))/2, by a method that does not reuse this script's pool(), and report rays/pairs/triads/colourability/minimum against tab:twosymbol.

STEP 3 -- IS WHAT IS PROVED EXACTLY WHAT IS STATED? Check parts (i), (ii) and (iii) of the theorem against the table and the JSON. In (i), is the list of uncolourable x complete and correctly described ("x or 1/x is one of +-2, +-sqrt 2, +-sqrt(-2), or x is a primitive third or sixth root of unity")? In (ii), is "the minimum sets are the six copies of CK-31" justified for all four of x = +-2, +-1/2, and is "33 rays in every other uncolourable case" certified? In (iii), is the reduction from {0,+-a,+-b} to {0,+-1,+-x} complete, including degenerate a, b? Does (iii) quietly assume the rays are given by words over the alphabet, and is that the natural reading of "coordinates in"? Does the table's last column claim more than the VF2 test of one witness supports?

STEP 4 -- OVERCLAIMS AND CONSISTENCY. Do the abstract, introduction, conclusion and the four remarks claim more than the theorem gives -- in particular about the open gap between 24 and 31 rays, about completed pools, about novelty of the {0,+-1,+-omega} row, and about "the construction read off Peres's cubes cannot beat Conway and Kochen"? Is the new theorem consistent with the paper's other statements: the two-symbol table (tab:alphabets), the zero-sum table, the 6|n theorem (S_3 colourable, S_6 not), the Eisenstein computed fact (exactly three minimum 33-sets in the 57-ray pool), the modulus-2 circle theorem, and the Heegner table? Is the result already in the literature, or an easy corollary of something that is?

STEP 5 -- VERDICT. Is this theorem correct as stated and adequately proved for a preprint? What must change before it is released?

OUTPUT FORMAT.
1. Up-front verdict on the new theorem: CORRECT AS STATED / CORRECT WITH WORDING FIXES / GAP IN PROOF / WRONG, one-line justification.
2. A table of actionable issues: | Priority (High/Med/Low) | Step | Issue (quote the paper) | Suggested fix |. Separate demonstrated errors from unsupported claims and from things you could not check.
3. A short list: claims you independently confirmed, with the method used.
4. The Step 5 answer as short prose.

Do not flatter. Do not equivocate. If a part is solid, say so once and move on."""


def main():
    tex = O.assemble()
    import re
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
               "--timeout", "2700"]
        return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
