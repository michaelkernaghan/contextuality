"""Round 10: short confirmation review of the version 12 draft after the round-9 fixes and
after the Prolegomena was shortened as rounds 8 and 9 advised."""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import oxford_review_v10 as O
import oxford_review_v12_round8 as R8

PROMPT = r"""You are conducting a SHORT, AGGRESSIVE confirmation review of the VERSION 12 DRAFT of "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three", after the author's response to your round-9 review. Your reports are paper/reviews/codex-review-algebraic-islands-v12-round8.txt and -round9.txt in the repository C:\Users\Michael Kernaghan\contextuality. Read round 9 first. Version 12 sources: paper/algebraic_islands_v12.tex and paper/v12_*.tex. Version 11.1 sources for comparison: paper/v11_*.tex and paper/algebraic_islands_v11.tex (git tag v11.1). The fixes were made with a large language model and have NOT been reviewed.

The author says: (a) every row of your round-9 "new issues" table was addressed: "lines" became "crossings" for the count 109; a coordinate triple with a parameter is now defined as an expression evaluated at each parameter value (Section 1.2 and the formal definition in Section 3), and the list W of the circle theorem is described as expressions in x and x*; x != 0 is stated; two table captions no longer say "two coordinate values" where one-value cases are included; "nonzero coordinate value" in Section 5; the caption of fig:circle says "At these three real values"; the reproducibility appendix names v11.1 as the computational baseline and lists ks_v12_prolegomena_checks.py; that script now tests entries of the displayed triples and its helper is renamed at_crossing. (b) The Prolegomena (paper/v12_s0_prolegomena.tex) was SHORTENED as you advised in rounds 8 and 9: it now has three subsections ("Rays on a cube, and the rule", "The grid", "The question"); the "machine with one dial" passage, the paragraphs on the hope and on what was found, and the closing paragraph on the circles are gone; the elimination statement survives as the last paragraph.

YOUR JOB.
(1) For each row of your round-9 NEW-issues table, quote the current text and say FIXED / PARTLY FIXED / NOT FIXED / FIX INTRODUCED A NEW ERROR. Also re-check the rows of your round-9 first table that you marked PARTLY FIXED or NOT FIXED (D3, D7, D8, D14, D15, D19, U1, U2, L2, the table-heading remark, the nonzero-parameter remark).
(2) Read the whole of the shortened Prolegomena as a hostile referee: is every factual sentence correct and consistent with Section 3 and the theorems? Did the shortening remove a definition, label or statement that the rest of the paper relies on (check every \ref to sec:prolegomena, sec:rule, sec:grid, sec:ladder, fig:generic, fig:triptych, fig:ladder, and any later sentence that refers back to the Prolegomena)? Is the expression/evaluation convention now adequate for every use of "coordinate triple", "the same triples", "fixed list", "145 coordinate triples" and "the 45 coordinate triples" in paper/v12_s2_two.tex and paper/v12_s4_conj.tex, or do particular sentences still need rewording? Quote any that do.
(3) Confirm once more that no theorem conclusion, proof step, table entry or number differs from v11.1 apart from vocabulary, the added convention sentences and the labels A, B, C on fig:circle, and that all cross-references resolve to the right objects.
(4) Anything else that should block an arXiv replacement of v11.1.

Do not re-review the mathematics of the theorems or the Lean proofs. Do not run lake build.

OUTPUT FORMAT.
1. One-line verdict: FIT TO REPLACE v11.1 ON ARXIV / FIT AFTER THE LISTED FIXES / NOT FIT.
2. Table: | Round-9 issue | Current text (quoted) | Status |.
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
