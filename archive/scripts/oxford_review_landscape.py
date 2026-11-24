"""Oxford-style challenge review of algebraic_landscape_letter.tex via Codex (GPT-6).

Mirrors oxford_review_cyclotomic.py, but routes through
claude-inbox/scripts/codex_peer_review.py instead of the OpenAI Responses API, so
the tested Windows codex plumbing (node.exe launcher, stdin prompt, read-only
sandbox, --output-last-message) is reused rather than reimplemented.

The prompt is passed as an argv element from Python, never through a shell, so
there is no quoting or 32k command-line limit to worry about.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TEX = Path(r"C:\Users\Michael Kernaghan\contextuality\paper\algebraic_landscape_letter.tex")
REVIEWER = Path(r"C:\Users\Michael Kernaghan\claude-inbox\scripts\codex_peer_review.py")
MODEL = "gpt-6-astra"

# --- injection pre-scan (peer-review skill) -------------------------------
# The document is our own authored LaTeX, so this is a formality, but the skill
# asks for it and a silent scan costs nothing.
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
    text = re.sub(r"\\label\{[^}]*\}", "", text)
    text = re.sub(r"\\url\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\\\", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text)


PROMPT = r"""You are conducting an AGGRESSIVE Oxford-style challenge review of a Physical Review Letters submission in quantum foundations and algebraic number theory.

WHAT THE LETTER CLAIMS. Kochen-Specker (KS) uncolorability in dimension three is controlled by the arithmetic of the ring supplying ray coordinates. Classic constructions are read as words over a coordinate alphabet {0, +-1, +-x}: CK-31 at x=2, Peres-33 at x=sqrt(2). Orthogonality requires a vanishing sum of products of alphabet letters (a "cancellation identity"); these are enumerated in Table I. Two low-norm mechanisms (|x|^2=2 and 1+w+w^2=0) account for the classical constructions; a third (the minimal polynomial of a cubic unit) is conceded late. Generators with |x|^2 >= 3 that are not roots of unity give triads but no uncolorability. One genuine theorem: the nth-root-of-unity family in C^3 is KS-uncolorable iff 6|n. Eight "algebraic islands" are tabulated with OCUS-certified pool minima 31 < 33 < 43 < 52 < 58.

Adopt the stance of an unsympathetic Oxford DPhil examiner who knows the contextuality literature and is hunting for grounds to reject. Do NOT be polite. Do NOT pad. Be specific to THIS letter, quoting its sentences verbatim when you attack them.

Complete ALL FOUR steps.

STEP 1 -- HOSTILE EXAMINER (claims vs evidence).
Rank the four weakest points by how hard they are to fix. Force yourself to examine at least these:

(a) EPISTEMIC STATUS OF "THE CRITERION". The letter slides between theorem, criterion, classification and survey finding. Exactly one result is proved (6|n). Everything else is "across every alphabet we tested". Is the title "The arithmetic of Kochen-Specker uncolorability in dimension three" licensed by that evidence, or is it a promissory note?

(b) COMPLETENESS OF TABLE I. The letter asserts the primitive vanishing sums "can be listed completely". Is that a proof or an enumeration by inspection? Note the letter's own admitted history: for eight revisions the list covered three-term sums ONLY, and the two-term row Tr(x)=0 was missing until an outside reader supplied it. What argument, if any, now closes the list? Only one row (Tr(x)=+1) is said to be SMT-certified. Attack the rest.

(c) THE NORM BOUND AS UNFALSIFIABLE. The load-bearing negative claim is "|x|^2 >= 3 and not a root of unity gives triads but no uncolorability". This is purely empirical. Worse, the supergolden counterexample has |psi|^2 ~ 2.148, and the letter observes that this "still lies below 3, so the norm bound survives". Is the bound doing predictive work, or has it been retrofitted to whatever survived? What observation would falsify it? Press hard here.

(d) THE CONJUGATION-DEPENDENCE COMPARISON. The letter reports that 60 of 120 orthogonal pairs in the Z[sqrt(-2)] pool "vanish only because conjugation acts nontrivially, against none over Z[sqrt(2)]". But Z[sqrt(2)] is a REAL field, where conjugation is the identity, so the count there is necessarily zero. Is this comparison informative, or is it vacuous by construction -- a statistic that could not have come out any other way? If it is vacuous, the conclusion "the two rings reach isomorphic graphs by disjoint arithmetic routes" is unsupported by it. Decide and say so.

(e) THE 6|n PROOF SKETCH. Sufficiency is "the sixth roots sit inside the nth roots, and they carry the Eisenstein 33-ray set with them". Does uncolorability actually pass to supersets of a RAY SET? New rays in S_n \ S_6 bring new orthogonality constraints, but also new rays to colour -- spell out whether the letter has established the direction it needs, or merely asserted monotonicity. In the necessity case 3|n with n odd, the argument turns on each all-nonzero ray lying in EXACTLY one triad. Is that uniqueness established in the sketch, or assumed?

(f) "ISLANDS ARE ISOLATED". Justified by sweeping 164 angles of a one-parameter family and finding five uncolorable ones. Does a finite sample of a continuum license "no continuous path joins one island to another"? What would?

(g) CERTIFICATION LANGUAGE. "OCUS-certified" minima are certified WITHIN a finite pool. Does the letter make that scope unmistakable, or could a reader take 31 as a proved global minimum, which it is not?

STEP 2 -- LITERATURE CHECK. Check each load-bearing citation against what the work actually establishes:
- Cabello, "Simplest Kochen-Specker set" (arXiv:2508.07335): is the identification of that 33-vector construction with the letter's "Eisenstein island" exact, in the sense of coordinate alphabet and projective equivalence, or is it an analogy?
- Trandafir and Cabello (Phys. Rev. A 111, 052204): the letter says they "proved CK-31 rigid and conjectured it optimal". Accurate? Under what assumption?
- Cortez, Morales and Reyes (arXiv:2211.13216): the letter says "the same number 6 appears independently" in their Z[1/6] minimality. Is that a substantive connection or numerology on a small integer?
- Frembs (arXiv:2609.16490): the letter attributes to him a trace-zero observation and a "43-ray arrangement carrying an obstruction modulo 3". Is that a fair characterisation of a paper whose subject is linear constraint systems, and is the letter borrowing authority it has not earned?
- Li/Bright/Ganesh and Kirchweger/Peitl/Szeider: is the lower bound 24 correctly attributed and correctly described?

STEP 3 -- FRAMING AND PHILOSOPHY OF SCIENCE.
- "Contextuality in dimension three looks less like a continuous geometric phenomenon than a discrete arithmetic one." Is this a discovery or a restatement of the fact that the author chose to search over algebraic alphabets? Every finite ray set has coordinates in SOME ring. Is the alphabet a structural object or an artifact of presentation? This is the deepest objection available; do not let the author off.
- Does the "island" metaphor earn its place, or is it decoration over "we found eight examples and no others"?
- The letter concedes mid-argument that its own two-mechanism reading survived eight revisions before being refuted. Does that candour strengthen the work or signal that the classification is not ready for a Letter?
- The acknowledgments disclose that computational work, proof construction and manuscript preparation were done with a large language model under the author's direction. Would a PRL referee treat that as acceptance-positive, neutral, or a concern? Answer honestly rather than diplomatically.

STEP 4 -- PRL FIT.
- Is this PRL, or is it Phys. Rev. A / J. Phys. A / Foundations of Physics? Name the single result that would justify a Letter, if any.
- Is the title an overclaim given one theorem?
- The abstract runs about 1040 characters against PRL's ~600-character guidance. Flag it.
- Four pages with two tables. Is anything present that a Letter should cut, and is anything absent that a referee would demand -- for instance a worked smallest case, or an explicit statement of what is proved versus surveyed?

OUTPUT FORMAT.
1. Up-front verdict: ACCEPT / MAJOR REVISION / MINOR REVISION / REJECT, one-line justification.
2. A table of actionable issues, columns: | Priority (High/Med/Low) | Step | Issue (quote the letter) | Suggested fix |.
3. A free-form "what I would tell the author over a glass of port" paragraph: blunt, constructive, and specific.

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
        stripped = Path(tmp) / "algebraic_landscape_letter.txt"
        stripped.write_text(text, encoding="utf-8")
        cmd = [sys.executable, str(REVIEWER), str(stripped),
               "--prompt", PROMPT, "--model", MODEL, "--timeout", "1800"]
        print("Routing through codex_peer_review.py (model=%s)..." % MODEL)
        return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
