"""Round 4 of the v10 challenge review: the conjugate-closed theorem only.

Rounds 1-3 predate Theorem "Conjugate-closed alphabets" (thm:conj) and its scripts
ks_conjugate_closed_theorem.py and ks_conjugate_closed_identify.py.  This round asks the
reviewer to attack that theorem.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import oxford_review_v10 as O

PROMPT = r"""You are conducting an AGGRESSIVE Oxford-style challenge review of ONE new result added to version 10 of "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three" after your three earlier rounds: the theorem labelled thm:conj ("Conjugate-closed alphabets") in the subsection "Every conjugate-closed alphabet", its proof, its table (tab:conj), the five remarks after it, the redrawn figure of the x-plane, and every sentence elsewhere in the paper that relies on it (abstract item (D), the introduction, the open questions, the conclusion). The theorem and its computation were produced with a large language model; treat every step and number as unverified until you have checked it. The rest of the paper was covered in rounds 1 to 3; do not re-review it except where it now contradicts or depends on the new theorem.

You have read access to the repository at C:\Users\Michael Kernaghan\contextuality. The new scripts are ks_conjugate_closed_theorem.py (modes: scan, certify <budget>, one "<label>" <budget> [floor]) and ks_conjugate_closed_identify.py. Their outputs are results/conjugate_closed_scan.json, results/conjugate_closed_theorem.json, results/conjugate_closed_reruns.jsonl, results/conjugate_closed_witness_graphs.json, and the logs results/conjugate_closed_certify.log and results/cc_rerun_*.log. They use ks_recertify_v10.py and ks_certify_fast3.py, which you have already read. The scan mode takes seconds; run it. Do not run certify (hours).

Be specific, quote the paper, and where a short calculation or a reading of the code settles a point, do it and show it.

STEP 1 -- THE REDUCTION TO 68 CASES. (a) Is every inner product and every 2x2 minor of two words over {0,+-1,+-x,+-x*} an integer combination of 1, x, x*, |x|^2, x^2, x*^2 with sum of |c_k| at most 3, and are there 376 nonzero vectors? (b) Are the two real vanishing conditions printed in the proof correct? (c) Is the description of a vector's solution set right (finitely many points plus whole curves that are the real axis, a vertical line, or b^2 = g0 + g1 a + g2 a^2), and is "two different curves meet in at most two values of a" enough to make the stratification argument valid, including for the reducible curves (pairs of lines b^2 = a^2, b^2 = 3a^2, b^2 = a^2/3) and the two-branched hyperbolas? Could a vector vanish on only one line of a pair, or on only one branch, in a way the argument misses? (d) Are there exactly fourteen curves and are they the ones listed? Is the set of 53 special points complete: every isolated solution, every pairwise intersection including tangencies, every point where words coincide? Are the reduced counts (28 classes of points, 12 of curves under x -> -x and x -> x*) right? (e) Is it true that x -> 1/x is not a symmetry of this pool? (f) Is anything lost at x = 0, on the real axis (x* = x) or on the imaginary axis (x* = -x)?

STEP 2 -- THE SCRIPT. Read ks_conjugate_closed_theorem.py line by line. Are Q2 arithmetic and Q2.sign exact? Does Pt.vanishes implement the two conditions correctly, including the case b = 0? Does decompose() classify every vector correctly? Does arrangement() find all intersections, including graph/graph, graph/vertical line, and points on the real axis? Do sample_graph and sample_line return points at which exactly the vectors vanishing on that whole curve vanish? Does pool() identify rays and orthogonality correctly (conjugation convention in inner_vec; minors without conjugation)? Is the mirror shortcut in certify() (copying the record of -x) legitimate? Is the "floor" device in one() sound: does a run started from a dummy upper-bound set of size 31 that terminates with "optimal" really prove that no uncolourable subset of fewer than 31 rays exists? Read certify3 again with that use in mind. Recompute independently, by a method that does not reuse this script's pool(), at least: a generic point; a generic point of each of |x|^2 = 2, |x|^2 = 1/2, the 30 degree line and the 60 degree line; one colourable curve; and the special points (1+i)/2, 1+i, zeta = exp(i pi/3), 2 zeta, exp(i pi/6), (1+sqrt(-7))/4 and exp(i pi/4). Report rays/pairs/triads/colourability against tab:conj.

STEP 3 -- IS WHAT IS PROVED EXACTLY WHAT IS STATED? Check (i), (ii), (iii) against the table and the JSON files. In (i): is the "if and only if" right in both directions -- every point of the three curve families uncolourable including their special points, and every other x colourable except +-2, +-1/2? Is "x*/x is a primitive third or sixth root of unity" the same set as arg x in {+-30, +-60, +-120, +-150 degrees}? In (ii): are 45 and 33 certified at the generic points of the curves? In (iii): is the lower bound of 31 supported for every case other than +-1+-i, and is the paper honest about the four cases where the exact minimum is not certified (table entries "31--33" and "<= 45")? Check the claim in the proof that part (c) follows from the two-symbol theorem by restriction: is it true that P(x) contains every ray of S(x*/x)? Is the last column of the table (graph of the smallest set found) supported by results/conjugate_closed_witness_graphs.json, and does any row claim more than a VF2 test of one witness supports?

STEP 4 -- OVERCLAIMS AND CONSISTENCY. Do the abstract, introduction, conclusion, figure caption and the five remarks claim more than the theorem gives? In particular: the first remark's statement that the theorem "absorbs" parts (i) and (ii) of the modulus-2 circle theorem; the second remark's "one-parameter family of 33-ray sets with Peres's graph" on |x|^2 = 1/2 (is that supported, and is it plausibly the Gould-Aravind family -- say what you can establish); the third remark's reading of the Heegner table and of the Gaussian alphabet as the point (1+i)/2; the fourth remark about 31. Is the theorem consistent with thm:twosymbol on the real and imaginary axes, with thm:circle, with the Eisenstein computed fact, with the Q(sqrt -7) computed fact and with tab:heegner? Does anything elsewhere in the paper now contradict it (for example the Gould-Aravind subsection, the open questions, the rigidity discussion)?

STEP 5 -- VERDICT. Is this theorem correct as stated and adequately proved for a preprint? What must change before it is released?

OUTPUT FORMAT.
1. Up-front verdict on the new theorem: CORRECT AS STATED / CORRECT WITH WORDING FIXES / GAP IN PROOF / WRONG, one-line justification.
2. A table of actionable issues: | Priority (High/Med/Low) | Step | Issue (quote the paper) | Suggested fix |. Separate demonstrated errors from unsupported claims and from things you could not check.
3. A short list: claims you independently confirmed, with the method used.
4. The Step 5 answer as short prose.

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
