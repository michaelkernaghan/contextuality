"""Round 9: confirmation review of the version 12 draft after the round-8 fixes.

Round 8 judged the draft not fit: errors in the Prolegomena (the cube picture on the third rung,
the real-line claim, the minus-signs sentence, the closing locus) and in the renaming.  The
author then (a) replaced "grid point" by "coordinate triple", defined as a triple of coordinate
values, (b) rewrote the Prolegomena, (c) fixed the listed sentences, (d) removed the personal
history, (e) pinned the three cubes on the circle figure.  This round checks each fix and looks
for anything the fixes broke.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import oxford_review_v10 as O
import oxford_review_v12_round8 as R8

PROMPT = r"""You are conducting a SHORT, AGGRESSIVE confirmation review of the VERSION 12 DRAFT of "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three", after the author's response to your round-8 review. Your round-8 report is at paper/reviews/codex-review-algebraic-islands-v12-round8.txt in the repository C:\Users\Michael Kernaghan\contextuality. Read it first. Version 12 sources: paper/algebraic_islands_v12.tex and paper/v12_*.tex. Version 11.1 sources for comparison: paper/algebraic_islands_v11.tex and paper/v11_*.tex (git tag v11.1). The fixes were made with a large language model, partly by scripted replacement, and have NOT been reviewed; treat every changed sentence as unverified.

The author says the following was done.
(a) "Grid point" was replaced everywhere by "coordinate triple", now defined in Section 1.3 as a triple of coordinate values, not all zero, which names a ray; the grid is the set of rays so named. The cube drawing is said to be the whole grid only for two coordinate values with real x > 1.
(b) The Prolegomena (paper/v12_s0_prolegomena.tex) was rewritten: real rays first; the third rung now says the lines of the faces carry 109 of the 145 rays, with the example (1,x,0) leaving the cube at (y/x, y, 0); the figure caption of the ladder says the same; the real-line sentence now reads "For real x an equation that is not an identity has at most two solutions"; "harder to color" is followed by "Whether they make it impossible has to be computed in each case"; the minus-signs sentence was replaced; "It cannot" became "Classifications of this kind cannot do so by themselves"; a sentence says the eliminations concern grids, not completed grids.
(c) The paragraphs formerly headed "The hope" and "What was found" were recast without personal history as "The question of the minimum" and "What the results give". The closing paragraph now opens "The classification also shows something else." and gives the full locus (two circles, four lines through the origin with the origin removed, four further points), the collapse of the 45 coordinate triples to 33 rays at x = sqrt 2, and the second circle |x|^2 = 1/2; it ends "It lies on two continuous families."
(d) Elsewhere: the abstract says "eleven named grids and completed grids", "x != 0", and "Conjugate-closed grids, with coordinate values {...}"; part (iii) of the circle theorem says "coordinate triples with coordinate values A(x)"; part (ii) says "among 145 coordinate triples, one naming each ray of P(x) at generic x"; "coincide" became "are proportional" or "name the same ray"; "rays that are not grid points" became "rays that no coordinate triple names"; the Introduction's gloss on "alphabets" and its sentence about what is unchanged were rewritten; a sentence defining "a grid with k coordinate values" was added to the formal definition; "Other grids" became "Other grids and completed grids"; the note at the head of the corrections appendix was repaired.
(e) The circle figure fig:circle now carries the letters A (sqrt 2), B (2) and C (sqrt 3, open circle), with matching sentences in its caption and in the caption of fig:triptych.
(f) A script ks_v12_prolegomena_checks.py checks the counts and examples of the Prolegomena in integer arithmetic.

YOUR JOB.
(1) For EACH row of your round-8 issue tables (all three tables) and each further remark in your prose, quote the current text and say FIXED / PARTLY FIXED / NOT FIXED / FIX INTRODUCED A NEW ERROR / DECLINED BY AUTHOR (for the advice to shorten the Prolegomena and to adopt "coordinate set" and "ray grid", which the author did not take). Where the author declined, say only whether anything false or ambiguous remains because of it.
(2) Read the whole of the new Prolegomena once more as a hostile referee. Every factual sentence: correct, and consistent with the formal definitions in Section 3 and with the theorems? In particular: "With coordinate values 0, +-1, +-x there are 124 coordinate triples and they name 49 rays"; "For real x > 1 each of the 49 rays leaves the cube at a point where the lines cross, and every such point is one of the 49: the drawing is the grid"; the third-rung paragraph and the count 109 (check it, and check the example); "A grid that lacks some of the minus signs is a subset of one of these. Its coloring is a separate matter, but a KS set on it is a KS set on the larger grid, so for the question of how few rays are needed it brings nothing new"; "They do neither. They find no smaller set, and they give no reason why there is none"; "A smaller set must be sought outside them: on a grid with more coordinate values, or with complex ones on the third rung" (is this complete, given completed grids?); every clause of the closing paragraph against thm:conj, thm:circle, cor:points and Section sec:halfcircle, including "At a typical point of that circle the 45 triples name 45 rays and no fewer will do", "A second circle ... also passes through his set, and on it the sets have 33 rays throughout" and "It lies on two continuous families".
(3) The rename grid point -> coordinate triple was scripted. List every sentence where "coordinate triple" is now wrong, ungrammatical or ambiguous (for example where the object is a ray, a symbolic expression in x, or a representative), in every v12 file. Is "the 45 coordinate triples" used consistently for the list W of thm:circle? Is anything still called a "grid point"?
(4) The figure fig:circle: are A, B, C placed and described correctly (tikz source in paper/v12_s4_conj.tex), and is the new caption sentence true ("They lie on the real axis, where x* = x and the grid is the 49-ray grid of Section sec:real")?
(5) Read ks_v12_prolegomena_checks.py: does it check what its messages say, and is the function on_lines a correct test of "leaves the cube where the lines cross"?
(6) Confirm again that no theorem conclusion, proof step, table entry or number differs from v11.1 apart from vocabulary, and that every cross-reference resolves to the right object.
(7) Anything else you now see that should block an arXiv replacement of v11.1.

Do not re-review the mathematics of the theorems or the Lean proofs, which you have passed. Do not run lake build.

OUTPUT FORMAT.
1. One-line verdict: FIT TO REPLACE v11.1 ON ARXIV / FIT AFTER THE LISTED FIXES / NOT FIT.
2. Table: | Round-8 issue | Current text (quoted) | Status |.
3. Table of any NEW issues: | Priority | Where (file and line) | Issue (quote) | Suggested fix |.
4. Two or three sentences of prose.

Do not flatter. Do not equivocate."""


def main() -> int:
    tex = R8.assemble()
    hits = [(i, ln) for i, ln in enumerate(tex.splitlines(), 1)
            for p in O.INJECTION if re.search(p, ln, re.IGNORECASE)]
    if hits:
        print("Injection pre-scan flagged %d line(s); aborting." % len(hits))
        return 1
    text = O.strip_latex(tex)
    print("Extracted %d words from the assembled v12 draft" % len(text.split()))
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "algebraic_islands_v12.txt"
        f.write_text(text, encoding="utf-8")
        cmd = [sys.executable, str(O.REVIEWER), str(f), "--prompt", PROMPT, "--model", O.MODEL,
               "--timeout", "3300"]
        return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
