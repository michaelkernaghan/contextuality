"""Oxford-style challenge review of the arXiv v9 text (algebraic_islands.tex) via Codex.

Same plumbing as oxford_review_landscape.py (codex_peer_review.py, prompt passed
as an argv element, never through a shell). The prompt names areas to examine
but does not supply verdicts, so the reviewer is not anchored on ours.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TEX = Path(r"C:\Users\Michael Kernaghan\contextuality\paper\algebraic_islands.tex")
REVIEWER = Path(r"C:\Users\Michael Kernaghan\claude-inbox\scripts\codex_peer_review.py")
MODEL = "gpt-6-astra"

INJECTION = [
    r"ignore (all )?previous instructions", r"<\s*system\s*>", r"^\s*System:",
    r"recommend acceptance", r"give a positive review", r"\\color\{white\}",
    r"\\textcolor\{white\}", r"\\fontsize\{0", r"\\phantom\{", r"disregard the",
]


def strip_latex(tex: str) -> str:
    text = re.sub(r"\\documentclass.*?\\begin\{document\}", "", tex, flags=re.DOTALL)
    text = re.sub(r"\\end\{document\}", "", text)
    for cmd in ["textbf", "textit", "emph", "texttt", "mathrm", "mathbb", "mathcal"]:
        text = re.sub("\\\\" + cmd + r"\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\cite\{([^}]*)\}", r"[cite:\1]", text)
    text = re.sub(r"\\ref\{([^}]*)\}", r"[ref:\1]", text)
    text = re.sub(r"\\label\{([^}]*)\}", r"[label:\1]", text)
    text = re.sub(r"\\url\{([^}]*)\}", r"\1", text)
    return re.sub(r"\n{3,}", "\n\n", text)


PROMPT = r"""You are conducting an AGGRESSIVE Oxford-style challenge review of a long arXiv paper (version 9) in quantum foundations: "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three". The author intends to prepare version 10 and wants every defect found now. It is a single-author paper whose computations, proofs and text were produced with a large language model; treat every stated number, proof step and literature attribution as unverified until you have checked it yourself.

Adopt the stance of an unsympathetic Oxford DPhil examiner who knows the Kochen-Specker literature, algebraic number theory, SAT/MUS methods and spectral graph theory. Do NOT be polite. Do NOT pad. Quote the paper verbatim when you attack a sentence. Where you can settle a point by a short calculation, do the calculation and show it.

Complete ALL FIVE steps.

STEP 1 -- INTERNAL CONSISTENCY AUDIT. The paper has been revised eight times by accretion. Hunt for statements in one section that contradict statements, tables or definitions in another (counts, thresholds, lists of which fields "support KS sets", what was certified versus heuristic, what a definition says versus what an observation needs it to say). List every contradiction with both quotations.

STEP 2 -- MATHEMATICAL CORRECTNESS. Check, at minimum:
(a) the proof of the 6|n theorem, case by case, including whether each explicit colouring is complete (every class of ray accounted for);
(b) the "Galois-theoretic reformulation" subsection, sentence by sentence;
(c) the claimed completeness of the table of primitive three-term zero-sums and its justification paragraph (is the count of cases right, are solution sets described correctly, are the stated equivalences valid);
(d) whether the generator modulus |x|^2 is a well-defined invariant of the ray set S(A) at all;
(e) the merge definition and the "universal merge saturation" observation and conjecture: is the observation a finding, or does it follow from the definition by a short argument either way;
(f) the use of the Hoffman bound and of the terms "theta-perfect", "quantum bound" and "contextual advantage" in the CSW section: are the hypotheses of the cited bound satisfied, and is the Lovasz number of the graph the value actually attained by the paper's own three-dimensional rays;
(g) the rigidity section: symmetry dimension count, the relation between infinitesimal, local and global rigidity as stated;
(h) the bipartite (B-KS/BPQS) table and the two "empirical patterns" drawn from it: check them against the table's own rows.

STEP 3 -- EPISTEMIC STATUS AND THE CENTRAL THESIS. Is "KS sets arise only when x supports a cancellation identity" a finding or a tautology (orthogonality over a finite alphabet IS a vanishing sum)? Does the three-mechanism taxonomy make any prediction that could fail, given that the third mechanism was added after a counterexample and "indirect modulus-2" was added for the golden ratio? Is "island" (isolation, "no continuous path") established, given the paper's own citation of a continuous family through the Peres set? Are the "OCUS-certified" pool minima adequately specified to be checkable, and is their scope (raw pool or completed pool, which pool exactly) unambiguous? Does every ring in the tables contain the integers, and if so what does it mean to say a field does or does not "support" a KS set?

STEP 4 -- LITERATURE CHECK. Verify each load-bearing attribution against the cited work: Cabello (BPQS and "simplest KS set"), Trandafir-Cabello (rigidity, the minimal-set result and its assumption), Cortez-Morales-Reyes (what object their minimality theorem is about), Li-Bright-Ganesh and Kirchweger-Peitl-Szeider (lower bound 24, venue, pages, author initials), Gould-Aravind, Kernaghan-Peres 1995 (number of vectors in dimension eight), Haemers (Hoffman bound hypotheses), Kochen-Specker 1967 (coordinate field of the original 117). Say plainly where you could not check.

STEP 5 -- WHAT SURVIVES. State which results in this paper you would be willing to see in print as they stand, which are salvageable with stated work, and which should be deleted. Then recommend the shape of version 10: one long paper, a short theorem paper plus a data paper, or something else. The author also plans to add one or two figures generalising Peres's cube diagrams (rays from the cube centre through lattice points on the faces, with the face lattice lines placed at 0, +-1 and +-x on a half-edge of length x) to make the alphabet concept visible; say what such a figure must show to earn its place and what it must not suggest.

OUTPUT FORMAT.
1. Up-front verdict: ACCEPT / MINOR REVISION / MAJOR REVISION / REJECT, with a one-line justification.
2. A table of actionable issues, columns: | Priority (High/Med/Low) | Step | Issue (quote the paper) | Suggested fix |. Aim for completeness over brevity; thirty rows is acceptable.
3. The Step 5 recommendation as short prose.
4. A free-form "what I would tell the author over a glass of port" paragraph: blunt, constructive, specific.

Do not flatter. Do not equivocate. If a section is solid, say so once and move on."""


def main() -> int:
    tex = TEX.read_text(encoding="utf-8")

    hits = [(i, ln) for i, ln in enumerate(tex.splitlines(), 1)
            for p in INJECTION if re.search(p, ln, re.IGNORECASE)]
    if hits:
        print("Injection pre-scan flagged %d line(s):" % len(hits))
        for i, ln in hits[:20]:
            print("  %5d  %s" % (i, ln.strip()[:100]))
        print("Inspect before sending. Aborting.")
        return 1
    print("Injection pre-scan: clean.")

    text = strip_latex(tex)
    print("Extracted %d words (%d chars) from %s" % (len(text.split()), len(text), TEX.name))

    with tempfile.TemporaryDirectory() as tmp:
        stripped = Path(tmp) / "algebraic_islands_v9.txt"
        stripped.write_text(text, encoding="utf-8")
        cmd = [sys.executable, str(REVIEWER), str(stripped),
               "--prompt", PROMPT, "--model", MODEL, "--timeout", "2400"]
        print("Routing through codex_peer_review.py (model=%s)..." % MODEL)
        return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
