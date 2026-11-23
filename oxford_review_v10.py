"""Oxford-style challenge review of the v10 draft (algebraic_islands_v10.tex + section files).

Same plumbing as oxford_review_v9.py.  The section files are inlined so the
reviewer sees one document.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PAPER = Path(r"C:\Users\Michael Kernaghan\contextuality\paper")
REVIEWER = Path(r"C:\Users\Michael Kernaghan\claude-inbox\scripts\codex_peer_review.py")
MODEL = "gpt-6-astra"

INJECTION = [
    r"ignore (all )?previous instructions", r"<\s*system\s*>", r"^\s*System:",
    r"recommend acceptance", r"give a positive review", r"\\color\{white\}",
    r"\\textcolor\{white\}", r"\\fontsize\{0", r"\\phantom\{", r"disregard the",
]


def assemble():
    tex = (PAPER / "algebraic_islands_v10.tex").read_text(encoding="utf-8")

    def inline(m):
        f = PAPER / m.group(1)
        return f.read_text(encoding="utf-8") if f.exists() else m.group(0)
    for _ in range(2):
        tex = re.sub(r"\\input\{([^}]+)\}", inline, tex)
    return tex


PROMPT = r"""You are conducting an AGGRESSIVE Oxford-style challenge review of version 10 (draft) of "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three". You reviewed version 9 and rejected it. Version 10 claims to withdraw the failed classification and to rest on two theorems plus a catalogue recomputed with new scripts. Your job is to find out whether that is true. The paper and its computations were produced with a large language model; treat every number, proof step and attribution as unverified until you have checked it.

You have read access to the repository at C:\Users\Michael Kernaghan\contextuality. The new scripts are ks_recertify_v10.py, ks_certify_fast3.py, ks_certify_fast.py, ks_verify_large_minima.py, ks_tables_v10.py, ks_zero_sums_v10.py, ks_modulus2_circle.py, ks_extras_v10.py, ks_bpqs_exact.py, ks_csw_exact.py, ks_rigidity_v10.py, ks_verify_cyclotomic_theorem.py, and their outputs are in results/*.jsonl. Cells marked "pending" in the catalogue table belong to computations still running; ignore them.

Be specific, quote the paper, and where a short calculation or a reading of the code settles a point, do it and show it.

STEP 1 -- THE TWO THEOREMS. (a) Check the proof of the 6|n theorem line by line, including that each colouring assigns every ray and satisfies every pair and triad constraint. (b) Check the modulus-2 circle theorem: the linear-independence argument, the treatment of words that coincide at special x, part (ii) (colourable for generic x) and especially part (iii) (minimality of 45) -- is what is proved exactly what is stated? Read ks_modulus2_circle.py and say whether it computes what the proof says. Recompute something independently if you can. (c) Is the argument that this family differs from the Gould-Aravind family sound?

STEP 2 -- SOUNDNESS OF THE NEW COMPUTATIONS. Read ks_certify_fast3.py / ks_certify_fast.py: is the certifier sound as described in the Methods section (every hitting clause the complement of a SAT-verified colourable set; termination implies minimality)? Read ks_bpqs_exact.py: is the monotonicity argument right, is the model the one in Cabello's Definition 2, is "exact" justified? Read ks_csw_exact.py: are alpha, the attained value, theta and alpha* computed and labelled correctly? Read ks_extras_v10.py census(): does the enumeration really list ALL minimum sets? Check a sample of the numbers in the paper's tables against results/*.jsonl and report every mismatch.

STEP 3 -- RESIDUAL OVERCLAIMS AND NEW ERRORS. Does anything withdrawn in the Corrections section survive elsewhere in the text? Are there new overclaims (for example about novelty, about "the smallest such list", about what the circle theorem shows regarding the Q(sqrt(-7)) set, about pools being non-isomorphic)? Is every "Computed fact" stated with the right scope (raw vs completed pool, which alphabet)? Is the Corrections list accurate and complete relative to your version 9 review?

STEP 4 -- LITERATURE. Check the attributions that remain: Trandafir-Cabello (what is proved, under what assumption), Cabello (bipartite strategies; simplest KS set; the 5x9 and 7x9 values), Cabello-Severini-Winter (the three bounds and what theta means), Gould-Aravind and Flores Gordillo, Frembs, Cortez-Morales-Reyes, Li-Bright-Ganesh, Kirchweger-Peitl-Szeider, Kernaghan-Peres. Say plainly where you could not check.

STEP 5 -- VERDICT ON THE REVISION. Is this now a paper you would let through, and at what level (as a preprint; for a journal, which)? What are the three most important things still to do? Is the paper's account of how it was produced and what was withdrawn adequate and honest?

OUTPUT FORMAT.
1. Up-front verdict: ACCEPT / MINOR REVISION / MAJOR REVISION / REJECT, one-line justification.
2. A table of actionable issues: | Priority (High/Med/Low) | Step | Issue (quote the paper) | Suggested fix |. Separate demonstrated errors from unsupported claims and from things you could not check.
3. A short list: claims you independently confirmed.
4. The Step 5 answer as short prose.

Do not flatter. Do not equivocate. If a section is solid, say so once and move on."""


def strip_latex(tex):
    text = re.sub(r"\\documentclass.*?\\begin\{document\}", "", tex, flags=re.DOTALL)
    text = re.sub(r"\\end\{document\}", "", text)
    for cmd in ["textbf", "textit", "emph", "texttt", "mathrm", "mathbb", "mathcal"]:
        text = re.sub("\\\\" + cmd + r"\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\cite\{([^}]*)\}", r"[cite:\1]", text)
    text = re.sub(r"\\ref\{([^}]*)\}", r"[ref:\1]", text)
    text = re.sub(r"\\label\{([^}]*)\}", r"[label:\1]", text)
    return re.sub(r"\n{3,}", "\n\n", text)


def main():
    tex = assemble()
    hits = [(i, ln) for i, ln in enumerate(tex.splitlines(), 1)
            for p in INJECTION if re.search(p, ln, re.IGNORECASE)]
    if hits:
        print("Injection pre-scan flagged %d line(s); aborting." % len(hits))
        for i, ln in hits[:20]:
            print("  %5d  %s" % (i, ln.strip()[:100]))
        return 1
    text = strip_latex(tex)
    print("Extracted %d words from the assembled v10 draft" % len(text.split()))
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "algebraic_islands_v10.txt"
        f.write_text(text, encoding="utf-8")
        cmd = [sys.executable, str(REVIEWER), str(f), "--prompt", PROMPT, "--model", MODEL,
               "--timeout", "2700"]
        return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
