"""Round 7: confirmation review of version 11.0 after the round-6 fixes.

Round 6 found no mathematical repair needed and listed wording objections.  They were fixed and
v11.0 was tagged without re-review.  This round asks the reviewer to check each fix and to look
for anything the fixes broke or that round 6 missed in the new text.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import oxford_review_v10 as O
import oxford_review_v11_round6 as R6

PROMPT = r"""You are conducting a SHORT, AGGRESSIVE confirmation review of version 11.0 (git tag v11.0) of "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three". In round 6 you reviewed the version 11 draft; your report is at paper/reviews/codex-review-algebraic-islands-v11-round6.txt in the repository C:\Users\Michael Kernaghan\contextuality. Read it first. The author says every issue in your table was fixed and then tagged v11.0 WITHOUT re-review. Your job now: (1) for EACH row of your round-6 issue tables, and each further remark in your prose (the "generic minimum" wording, "P(sqrt 2) = P(1/sqrt 2)", "no shorter fixed list", C5's list of surviving results, the supergolden "product of two letters" phrase, "two degenerate points", the distinctB comment in lean/Minimality.lean), quote the current text from paper/v11_*.tex or paper/algebraic_islands_v11.tex and say FIXED / PARTLY FIXED / NOT FIXED / FIX INTRODUCED A NEW ERROR. (2) The author added to the Methods paragraph "Proofs checked in Lean" an argument that statements about vectors are statements about rays ("a coloring of rays gives a coloring of any choice of representative vectors and conversely, and each listed pool has one vector per ray (the export script checks this)"). Is the argument correct as worded, and does ks_lean_minimality.py really check one vector per ray (see the assert on len(index) in intpool and field_pool, and what R.canon does in ks_recertify_v10.py / ks_verify_large_minima.py)? (3) Read the abstract, the three paragraphs "Results", "Standard of proof", "Relation to earlier versions" of the introduction, the Conclusion and the Open questions once more as a hostile referee: any remaining sentence that claims more than a theorem proves, or contradicts another sentence? (4) Anything else you now see that should block an arXiv replacement.

Do not re-review the mathematics of the theorems or the Lean proofs, which you have passed. Do not run lake build.

OUTPUT FORMAT.
1. One-line verdict: FIT TO REPLACE v10.4 ON ARXIV / FIT AFTER THE LISTED FIXES / NOT FIT.
2. Table: | Round-6 issue | Current text (quoted) | Status |.
3. Table of any NEW issues: | Priority | Where | Issue (quote) | Suggested fix |.
4. Two or three sentences of prose.

Do not flatter. Do not equivocate."""


def main():
    tex = R6.assemble()
    hits = [(i, ln) for i, ln in enumerate(tex.splitlines(), 1)
            for p in O.INJECTION if re.search(p, ln, re.IGNORECASE)]
    if hits:
        print("Injection pre-scan flagged %d line(s); aborting." % len(hits))
        return 1
    text = O.strip_latex(tex)
    print("Extracted %d words from the assembled v11.0 paper" % len(text.split()))
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "algebraic_islands_v11.txt"
        f.write_text(text, encoding="utf-8")
        cmd = [sys.executable, str(O.REVIEWER), str(f), "--prompt", PROMPT, "--model", O.MODEL,
               "--timeout", "3300"]
        return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
